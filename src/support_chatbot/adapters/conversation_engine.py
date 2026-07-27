"""LangGraph + LangChain conversation engine adapter.

Implements the :class:`ConversationEngine` port using Azure OpenAI for
generation and a LangGraph retrieval graph for retrieval-augmented answering. All
LangChain / LangGraph specifics are confined to this adapter so the services
layer stays framework-agnostic.
"""

from __future__ import annotations

import logging
import re
from collections.abc import Generator, Iterator

from langchain_core.messages import AIMessage, SystemMessage
from langchain_core.runnables import RunnableConfig
from langchain_openai import AzureChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, MessagesState, StateGraph
from openai import OpenAIError

from support_chatbot.domain.errors import ExternalServiceError
from support_chatbot.domain.models import (
    AnswerComplete,
    AnswerToken,
    AskResponse,
    Source,
)
from support_chatbot.domain.ports import (
    ConversationEngine,
    PromptProvider,
    VectorStoreProvider,
)
from support_chatbot.settings import AppSettings

logger = logging.getLogger(__name__)

_CITATION_MARKER = re.compile(r"\s*\[(\d{1,2})\]")


class ChatState(MessagesState):
    """State stored in the LangGraph conversation graph."""

    system_prompt: str
    retrieved_docs: list


class LangGraphConversationEngine(ConversationEngine):
    """Answer questions with a LangGraph retrieval graph over Azure OpenAI."""

    def __init__(
        self,
        settings: AppSettings,
        provider: VectorStoreProvider,
        prompt_provider: PromptProvider,
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
        self._retrieval_k = settings.retrieval_k
        self._citation_prompt = (
            prompt_provider.get_citation_prompt()
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
            environment=settings.environment,
        )

    def _build_graph(self):
        def retrieve(state: ChatState, config: RunnableConfig):
            """Fetch and de-duplicate the manual pages backing the question.
            """
            question = state["messages"][-1].content
            manual_id = config["configurable"]["manual_id"]
            vector_store = self._provider.get_store(manual_id)
            retrieved = vector_store.similarity_search_with_score(
                question, k=self._retrieval_k
            )
            docs: list = []
            seen_urls: set[str] = set()
            for doc, score in retrieved:
                metadata = doc.metadata or {}
                url = metadata.get("source")
                if url and url in seen_urls:
                    continue
                if url:
                    seen_urls.add(url)
                doc.metadata["score"] = score
                docs.append(doc)
            return {"retrieved_docs": docs}

        def generate(state: ChatState):
            """Answer from the retrieved docs, adding inline [n] citations.
            Any out-of-range ``[n]`` markers are stripped afterwards;
            numbering matches the retrieved-doc order and therefore the
            sources returned to the client.
            """
            docs = state.get("retrieved_docs") or []
            numbered_docs = self._format_context(docs)
            system_parts = [
                state["system_prompt"],
                f"Context documents:\n{numbered_docs}",
            ]
            if self._citations_enabled and docs:
                system_parts.append(self._citation_prompt)
            conversation_messages = [
                message
                for message in state["messages"]
                if message.type in ("human", "ai")
            ]
            prompt = [SystemMessage("\n\n".join(system_parts))] + conversation_messages
            response = self._llm.invoke(prompt)
            if self._citations_enabled and docs and response.content:
                cleaned = self._validate_citation_markers(
                    response.content, len(docs)
                )
                if cleaned != response.content:
                    response = AIMessage(content=cleaned, id=response.id)
            return {"messages": [response]}

        graph_builder = StateGraph(ChatState)
        graph_builder.add_node(retrieve)
        graph_builder.add_node(generate)
        graph_builder.set_entry_point("retrieve")
        graph_builder.add_edge("retrieve", "generate")
        graph_builder.add_edge("generate", END)

        return graph_builder.compile(checkpointer=MemorySaver())

    def answer(
        self,
        *,
        question: str,
        session_id: str,
        manual_id: str,
        system_prompt: str,
        user_id: str | None = None,
    ) -> AskResponse:
        """Return the assistant's reply (with an optional trace id) for a question."""
        if self._langfuse is None:
            response = self._invoke_graph(
                question, system_prompt, session_id, manual_id
            )
            docs = response.get("retrieved_docs") or []
            return AskResponse(
                answer=response["messages"][-1].content,
                trace_id=None,
                sources=self._extract_sources(docs),
            )

        # Wrap the run in a Langfuse root span that records the question, the
        # final answer, and the retrieved context as separate, cleanly mappable
        # fields. An LLM-as-a-judge evaluator (e.g. faithfulness) can then target
        # this observation and map {{context}} -> metadata.retrieved_context and
        # {{answer}} -> output without parsing them out of the generation prompt.
        with self._langfuse.start_as_current_observation(
            as_type="span", name="rag-answer", input={"question": question}
        ) as root:
            root.update_trace(
                session_id=session_id,
                user_id=user_id or session_id,
                tags=[f"manual:{manual_id}"],
            )
            response = self._invoke_graph(
                question, system_prompt, session_id, manual_id
            )
            docs = response.get("retrieved_docs") or []
            answer_text = response["messages"][-1].content
            root.update(
                output=answer_text,
                metadata={"retrieved_context": self._format_context(docs)},
            )
            trace_id = root.trace_id
        return AskResponse(
            answer=answer_text,
            trace_id=trace_id,
            sources=self._extract_sources(docs),
        )

    def stream(
        self,
        *,
        question: str,
        session_id: str,
        manual_id: str,
        system_prompt: str,
        user_id: str | None = None,
    ) -> Iterator[AnswerToken | AnswerComplete]:
        """Stream the answer token-by-token, then a final AnswerComplete event.

        Only tokens from the ``generate`` node are surfaced. Sources are read
        from the final graph state once generation finishes, so the terminal
        event carries the same trace id and sources as :meth:`answer`.
        """
        if self._langfuse is None:
            docs, _ = yield from self._iter_answer_tokens(
                question, system_prompt, session_id, manual_id
            )
            yield AnswerComplete(
                trace_id=None, sources=self._extract_sources(docs)
            )
            return

        with self._langfuse.start_as_current_observation(
            as_type="span", name="rag-answer", input={"question": question}
        ) as root:
            root.update_trace(
                session_id=session_id,
                user_id=user_id or session_id,
                tags=[f"manual:{manual_id}"],
            )
            docs, answer_text = yield from self._iter_answer_tokens(
                question, system_prompt, session_id, manual_id
            )
            root.update(
                output=answer_text,
                metadata={"retrieved_context": self._format_context(docs)},
            )
            trace_id = root.trace_id
            sources = self._extract_sources(docs)
        yield AnswerComplete(trace_id=trace_id, sources=sources)

    def _iter_answer_tokens(
        self,
        question: str,
        system_prompt: str,
        session_id: str,
        manual_id: str,
    ) -> Generator[AnswerToken, None, tuple[list, str]]:
        """Stream answer tokens, returning ``(docs, answer_text)`` when done.

        Any Langfuse callback spans created while the graph streams nest under
        the currently active observation (the ``rag-answer`` root span when
        tracing is enabled).
        """
        config = self._graph_config(session_id, manual_id)
        inputs = {
            "messages": [{"role": "user", "content": question}],
            "system_prompt": system_prompt,
        }
        parts: list[str] = []
        try:
            for chunk, metadata in self._graph.stream(
                inputs, config=config, stream_mode="messages"
            ):
                if metadata.get("langgraph_node") != "generate":
                    continue
                content = getattr(chunk, "content", "")
                if isinstance(content, str) and content:
                    parts.append(content)
                    yield AnswerToken(text=content)
        except OpenAIError as exc:
            raise ExternalServiceError(
                f"Chat completion failed for manual {manual_id!r}: {exc}"
            ) from exc
        state = self._graph.get_state(config)
        docs = state.values.get("retrieved_docs") or []
        return docs, "".join(parts)

    def _invoke_graph(
        self,
        question: str,
        system_prompt: str,
        session_id: str,
        manual_id: str,
    ) -> dict:
        """Invoke the retrieval graph, translating LLM errors to domain errors."""
        config = self._graph_config(session_id, manual_id)
        try:
            return self._graph.invoke(
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

    def _graph_config(self, session_id: str, manual_id: str) -> dict:
        """Build the LangGraph run config, nesting tracing under the active span."""
        config: dict = {
            "configurable": {"thread_id": session_id, "manual_id": manual_id}
        }
        if self._langfuse is not None:
            from langfuse.langchain import CallbackHandler

            config["callbacks"] = [CallbackHandler()]
        return config

    @staticmethod
    def _format_context(docs: list) -> str:
        """Render retrieved docs as the numbered ``[n] page_content`` block.

        Matches exactly what the ``generate`` node feeds the model, so an
        evaluator scoring faithfulness sees the same context the answer was
        grounded on.
        """
        return "\n\n".join(
            f"[{index}] {getattr(doc, 'page_content', '')}"
            for index, doc in enumerate(docs, start=1)
        )

    @staticmethod
    def _extract_sources(docs: list) -> tuple[Source, ...]:
        """Map retrieved documents to API sources, preserving rank order."""
        sources: list[Source] = []
        for doc in docs:
            metadata = getattr(doc, "metadata", None) or {}
            url = metadata.get("source")
            if not url:
                continue
            sources.append(
                Source(
                    url=url,
                    title=metadata.get("title"),
                    score=metadata.get("score"),
                )
            )
        return tuple(sources)

    @staticmethod
    def _validate_citation_markers(text: str, num_sources: int) -> str:
        """Drop ``[n]`` markers that fall outside the valid source range."""

        def _keep(match: re.Match[str]) -> str:
            index = int(match.group(1))
            return match.group(0) if 1 <= index <= num_sources else ""

        return _CITATION_MARKER.sub(_keep, text)

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
