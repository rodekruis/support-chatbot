"""LangGraph + LangChain conversation engine adapter.

Implements the :class:`ConversationEngine` port using Azure OpenAI for
generation and a LangGraph retrieval graph for tool-augmented answering. All
LangChain / LangGraph specifics are confined to this adapter so the services
layer stays framework-agnostic.
"""

from __future__ import annotations

import logging
import re
from importlib import resources

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_core.runnables import RunnableConfig
from langchain_core.tools import tool
from langchain_openai import AzureChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode
from openai import OpenAIError

from support_chatbot.domain.errors import ExternalServiceError
from support_chatbot.domain.models import AskResponse, Source
from support_chatbot.domain.ports import ConversationEngine, VectorStoreProvider
from support_chatbot.settings import AppSettings

logger = logging.getLogger(__name__)

_CITATION_PROMPT_FILE = "prompts/citation_prompt.md"
_CITATION_MARKER = re.compile(r"\s*\[(\d{1,2})\]")


class ChatState(MessagesState):
    """State stored in the LangGraph conversation graph."""

    system_prompt: str


class LangGraphConversationEngine(ConversationEngine):
    """Answer questions with a LangGraph retrieval graph over Azure OpenAI."""

    def __init__(
        self,
        settings: AppSettings,
        provider: VectorStoreProvider,
    ) -> None:
        """Initialize the language model, retrieval graph, and tracing."""
        self._provider = provider
        self._llm = AzureChatOpenAI(
            azure_endpoint=settings.azure_openai_endpoint,
            azure_deployment=settings.model_chat,
            openai_api_version=settings.azure_openai_api_version,
            api_key=settings.azure_openai_api_key.get_secret_value(),
            temperature=0.2,
        )
        self._citations_enabled = settings.citations_enabled
        self._citation_prompt = (
            resources.files("support_chatbot")
            .joinpath(_CITATION_PROMPT_FILE)
            .read_text(encoding="utf-8")
            if settings.citations_enabled
            else ""
        )
        self._langfuse = self._init_langfuse(settings)
        self._graph = self._build_graph()

    @staticmethod
    def _init_langfuse(settings: AppSettings):
        """Initialize the global Langfuse client when keys are configured.

        Returns the client (so callers can flush on shutdown) or ``None`` when
        tracing is disabled, in which case the engine behaves exactly as before.
        """
        if not (settings.langfuse_public_key and settings.langfuse_secret_key):
            return None
        from langfuse import Langfuse

        return Langfuse(
            public_key=settings.langfuse_public_key.get_secret_value(),
            secret_key=settings.langfuse_secret_key.get_secret_value(),
            host=settings.langfuse_host,
        )

    def _build_graph(self):
        @tool(response_format="content_and_artifact")
        def retrieve(query: str, config: RunnableConfig):
            """Retrieve information related to a query."""
            manual_id = config["configurable"]["manual_id"]
            vector_store = self._provider.get_store(manual_id)
            retrieved = vector_store.similarity_search_with_score(query, k=8)
            retrieved_docs = []
            for doc, score in retrieved:
                doc.metadata["score"] = score
                retrieved_docs.append(doc)
            serialized = "\n\n".join(
                f"Document: {doc.page_content}" for doc in retrieved_docs
            )
            return serialized, retrieved_docs

        def generate_query(state: ChatState):
            llm_with_tools = self._llm.bind_tools(
                [retrieve], tool_choice="retrieve"
            )
            prompt = [SystemMessage(state["system_prompt"])] + state["messages"]
            response = llm_with_tools.invoke(prompt)
            return {"messages": [response]}

        # Disable LangGraph's default tool-error swallowing so retrieval failures
        # (e.g. Azure Search / embeddings outages) propagate as ExternalServiceError
        # and surface as a 502 instead of being fed back to the LLM as text.
        tools = ToolNode([retrieve], handle_tool_errors=False)

        def generate(state: ChatState):
            recent_tool_messages = []
            for message in reversed(state["messages"]):
                if message.type == "tool":
                    recent_tool_messages.append(message)
                else:
                    break

            docs_content = "\n\n".join(
                message.content for message in reversed(recent_tool_messages)
            )
            system_message_content = f"{state['system_prompt']}.\n\n{docs_content}"
            conversation_messages = [
                message
                for message in state["messages"]
                if message.type in ("human", "system")
                or (message.type == "ai" and not message.tool_calls)
            ]

            prompt = [SystemMessage(system_message_content)] + conversation_messages
            response = self._llm.invoke(prompt)
            return {"messages": [response]}

        def cite(state: ChatState):
            """Annotate the latest answer with inline [n] source citations.

            Runs as a separate, fail-open step: any failure (LLM error, reworded
            output, hallucinated markers) leaves the original answer untouched,
            so citation problems never degrade a correct answer.
            """
            answer_message = state["messages"][-1]
            docs = self._current_turn_artifacts(state["messages"])
            if not docs or not answer_message.content:
                return {"messages": []}
            annotated = self._add_citations(answer_message.content, docs)
            if annotated is None or annotated == answer_message.content:
                return {"messages": []}
            return {"messages": [AIMessage(content=annotated, id=answer_message.id)]}

        graph_builder = StateGraph(ChatState)
        graph_builder.add_node(generate_query)
        graph_builder.add_node(tools)
        graph_builder.add_node(generate)
        graph_builder.set_entry_point("generate_query")
        graph_builder.add_edge("generate_query", "tools")
        graph_builder.add_edge("tools", "generate")
        if self._citations_enabled:
            graph_builder.add_node(cite)
            graph_builder.add_edge("generate", "cite")
            graph_builder.add_edge("cite", END)
        else:
            graph_builder.add_edge("generate", END)

        return graph_builder.compile(checkpointer=MemorySaver())

    def answer(
        self,
        *,
        question: str,
        thread_id: str,
        manual_id: str,
        system_prompt: str,
    ) -> AskResponse:
        """Return the assistant's reply (with an optional trace id) for a question."""
        config: dict = {
            "configurable": {"thread_id": thread_id, "manual_id": manual_id}
        }
        trace_id: str | None = None
        if self._langfuse is not None:
            from langfuse.langchain import CallbackHandler

            trace_id = self._langfuse.create_trace_id()
            config["callbacks"] = [
                CallbackHandler(trace_context={"trace_id": trace_id})
            ]
            config["metadata"] = {
                "langfuse_session_id": thread_id,
                "langfuse_user_id": thread_id,
                "langfuse_tags": [f"manual:{manual_id}"],
            }
        try:
            response = self._graph.invoke(
                {
                    "messages": [{"role": "user", "content": question}],
                    "system_prompt": system_prompt,
                },
                config=config,
            )
        except OpenAIError as exc:
            raise ExternalServiceError(
                f"Chat completion failed for manual {manual_id!r}: {exc}"
            ) from exc
        return AskResponse(
            answer=response["messages"][-1].content,
            trace_id=trace_id,
            sources=self._extract_sources(response["messages"]),
        )

    @staticmethod
    def _current_turn_artifacts(messages: list) -> list:
        """Return the retrieved documents backing the latest answer, in rank order.

        Only the final contiguous block of tool messages is considered, so the
        result reflects the current turn rather than the whole conversation.
        Documents are deduplicated by source URL while preserving retrieval rank.
        """
        tool_messages = []
        seen_tool = False
        for message in reversed(messages):
            if getattr(message, "type", None) == "tool":
                seen_tool = True
                tool_messages.append(message)
            elif seen_tool:
                break
        tool_messages.reverse()

        docs: list = []
        seen_urls: set[str] = set()
        for message in tool_messages:
            for doc in getattr(message, "artifact", None) or []:
                metadata = getattr(doc, "metadata", None) or {}
                url = metadata.get("source")
                if not url or url in seen_urls:
                    continue
                seen_urls.add(url)
                docs.append(doc)
        return docs

    @classmethod
    def _extract_sources(cls, messages: list) -> tuple[Source, ...]:
        """Collect the retrieved manual pages backing the latest answer."""
        sources: list[Source] = []
        for doc in cls._current_turn_artifacts(messages):
            metadata = getattr(doc, "metadata", None) or {}
            sources.append(
                Source(
                    url=metadata["source"],
                    title=metadata.get("title"),
                    score=metadata.get("score"),
                )
            )
        return tuple(sources)

    def _add_citations(self, answer: str, docs: list) -> str | None:
        """Return the answer with inline ``[n]`` markers, or ``None`` to fall back.

        Numbering matches the order of ``docs`` (and therefore the order of the
        sources returned to the client). Returns ``None`` when the citation step
        fails or alters the answer's wording, so the caller keeps the original.
        """
        sources_block = "\n\n".join(
            f"[{index}] {doc.page_content}" for index, doc in enumerate(docs, start=1)
        )
        user_content = f"ANSWER:\n{answer}\n\nSOURCES:\n{sources_block}"
        try:
            response = self._llm.invoke(
                [
                    SystemMessage(self._citation_prompt),
                    HumanMessage(user_content),
                ]
            )
        except OpenAIError as exc:
            logger.warning("Citation step failed; returning plain answer: %s", exc)
            return None

        annotated = self._validate_citation_markers(response.content, len(docs))
        # Reject any rewriting: stripping markers must reproduce the original
        # answer, otherwise the model added preamble or changed the wording.
        if self._strip_markers(annotated) != self._strip_markers(answer):
            logger.warning("Citation step altered answer wording; falling back.")
            return None
        return annotated

    @staticmethod
    def _validate_citation_markers(text: str, num_sources: int) -> str:
        """Drop ``[n]`` markers that fall outside the valid source range."""

        def _keep(match: re.Match[str]) -> str:
            index = int(match.group(1))
            return match.group(0) if 1 <= index <= num_sources else ""

        return _CITATION_MARKER.sub(_keep, text)

    @staticmethod
    def _strip_markers(text: str) -> str:
        """Remove all citation markers and collapse whitespace for comparison."""
        return " ".join(_CITATION_MARKER.sub("", text).split())

    def score(
        self,
        *,
        trace_id: str,
        value: float,
        comment: str | None = None,
    ) -> None:
        """Record a user-feedback score against a Langfuse trace."""
        if self._langfuse is not None:
            self._langfuse.create_score(
                trace_id=trace_id,
                name="user-feedback",
                value=value,
                data_type="NUMERIC",
                comment=comment,
            )
            self._langfuse.flush()

    def flush(self) -> None:
        """Flush pending Langfuse traces. No-op when tracing is disabled."""
        if self._langfuse is not None:
            self._langfuse.flush()
