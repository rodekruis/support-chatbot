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

_ROUTER_INSTRUCTION = (
    "You route messages for a product support assistant. Decide whether "
    "answering the user's latest message requires the product manual.\n"
    "Reply with exactly one word:\n"
    "- retrieve: a substantive product question (how-to, features, permissions, "
    "troubleshooting, configuration).\n"
    "- direct: a greeting, small talk, thanks, or an off-topic / general-"
    "knowledge request the manual would not help with.\n"
    "When in doubt, reply retrieve."
)

_CONTEXTUALIZE_INSTRUCTION = (
    "Given the conversation so far and the user's latest message, rewrite the "
    "latest message into a standalone question that can be understood without "
    "the chat history. Resolve references and pronouns (e.g. 'are you sure?', "
    "'and then?', 'what about export?') into an explicit question. If the latest "
    "message is already self-contained, return it unchanged. Do NOT answer it, "
    "output only the reformulated question."
)


class ChatState(MessagesState):
    """State stored in the LangGraph conversation graph."""

    system_prompt: str
    retrieved_docs: list
    route: str
    search_query: str


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
        self._direct_answer_prompt = prompt_provider.get_direct_answer_prompt()
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
        def router(state: ChatState):
            """Decide whether the turn needs manual retrieval."""
            return {"route": self._classify_route(state["messages"])}

        def contextualize(state: ChatState):
            """Rewrite a follow-up into a standalone retrieval query using history.

            History-aware retrieval: turns like "are you sure?" become an
            explicit question so both retrieval and the evaluator's
            ``{{question}}`` see a self-contained query. First turns (no prior
            history) skip the LLM call and use the message as-is.
            """
            conversation = [
                message
                for message in state["messages"]
                if message.type in ("human", "ai")
            ]
            latest = conversation[-1].content if conversation else ""
            if len(conversation) <= 1:
                return {"search_query": latest}
            prompt = [SystemMessage(_CONTEXTUALIZE_INSTRUCTION), *conversation]
            try:
                result = self._llm.invoke(prompt)
            except OpenAIError as exc:
                raise ExternalServiceError(
                    f"Query contextualization failed: {exc}"
                ) from exc
            rewritten = (getattr(result, "content", "") or "").strip()
            return {"search_query": rewritten or latest}

        def retrieve(state: ChatState, config: RunnableConfig):
            """Fetch and de-duplicate the manual pages backing the question.
            """
            question = state.get("search_query") or state["messages"][-1].content
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

        def direct_answer(state: ChatState):
            """Answer conversational/off-topic turns without retrieval."""
            conversation_messages = [
                message
                for message in state["messages"]
                if message.type in ("human", "ai")
            ]
            system_prompt = "\n\n".join(
                [state["system_prompt"], self._direct_answer_prompt]
            )
            prompt = [SystemMessage(system_prompt)] + conversation_messages
            response = self._llm.invoke(prompt)
            return {"messages": [response]}

        graph_builder = StateGraph(ChatState)
        graph_builder.add_node(router)
        graph_builder.add_node(contextualize)
        graph_builder.add_node(retrieve)
        graph_builder.add_node(generate)
        graph_builder.add_node(direct_answer)
        graph_builder.set_entry_point("router")
        graph_builder.add_conditional_edges(
            "router",
            lambda state: state["route"],
            {"retrieve": "contextualize", "direct": "direct_answer"},
        )
        graph_builder.add_edge("contextualize", "retrieve")
        graph_builder.add_edge("retrieve", "generate")
        graph_builder.add_edge("generate", END)
        graph_builder.add_edge("direct_answer", END)

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
        # final answer, and (when retrieval ran) the retrieved context as
        # separate, cleanly mappable fields. Evaluators (faithfulness, context
        # relevance) target this observation and filter on ``retrieval_used`` so
        # they never run on chitchat / off-topic turns.
        with self._trace_attributes(
            session_id, user_id, manual_id
        ), self._langfuse.start_as_current_observation(
            as_type="span", name="chat-turn", input=question
        ) as root:
            response = self._invoke_graph(
                question, system_prompt, session_id, manual_id
            )
            docs = response.get("retrieved_docs") or []
            answer_text = response["messages"][-1].content
            root.update(
                output=answer_text,
                metadata=self._answer_metadata(
                    response.get("route"),
                    docs,
                    response.get("search_query"),
                    response.get("messages"),
                ),
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

        Tokens from the ``generate`` and ``direct_answer`` nodes are surfaced
        (the ``router`` and ``contextualize`` steps stay silent). Sources are
        read from the final graph state once answering finishes, so the terminal
        event carries the same trace id and sources as :meth:`answer`.
        """
        if self._langfuse is None:
            _, _, docs, _, _ = yield from self._iter_answer_tokens(
                question, system_prompt, session_id, manual_id
            )
            yield AnswerComplete(
                trace_id=None, sources=self._extract_sources(docs)
            )
            return

        with self._trace_attributes(
            session_id, user_id, manual_id
        ), self._langfuse.start_as_current_observation(
            as_type="span", name="chat-turn", input=question
        ) as root:
            route, search_query, docs, messages, answer_text = yield from (
                self._iter_answer_tokens(
                    question, system_prompt, session_id, manual_id
                )
            )
            root.update(
                output=answer_text,
                metadata=self._answer_metadata(
                    route, docs, search_query, messages
                ),
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
    ) -> Generator[
        AnswerToken, None, tuple[str | None, str | None, list, list, str]
    ]:
        """Stream tokens; return ``(route, search_query, docs, messages, answer_text)``.

        Tokens from both the ``generate`` and ``direct_answer`` nodes are
        surfaced; router and contextualize tokens are filtered out. Any Langfuse
        callback spans created while the graph streams nest under the currently
        active observation (the ``chat-turn`` root span when tracing is enabled).
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
                if metadata.get("langgraph_node") not in ("generate", "direct_answer"):
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
        route = state.values.get("route")
        search_query = state.values.get("search_query")
        messages = state.values.get("messages") or []
        return route, search_query, docs, messages, "".join(parts)

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

    def _classify_route(self, messages: list) -> str:
        """Classify whether the latest turn needs retrieval ('retrieve'/'direct').

        Considers recent history so short follow-ups (e.g. "and then?") still
        route to retrieval. Biased toward 'retrieve' on any ambiguity \u2014 a
        missed retrieval hurts more than a wasted one.
        """
        recent = [m for m in messages if m.type in ("human", "ai")][-6:]
        prompt = [SystemMessage(_ROUTER_INSTRUCTION), *recent]
        try:
            result = self._llm.invoke(prompt)
        except OpenAIError as exc:
            raise ExternalServiceError(f"Routing failed: {exc}") from exc
        return self._parse_route(getattr(result, "content", ""))

    @staticmethod
    def _parse_route(text: str) -> str:
        """Map a router reply to 'direct', defaulting to 'retrieve'."""
        return (
            "direct"
            if str(text).strip().lower().startswith("direct")
            else "retrieve"
        )

    def _answer_metadata(
        self,
        route: str | None,
        docs: list,
        search_query: str | None = None,
        messages: list | None = None,
    ) -> dict:
        """Build span metadata; expose retrieved context only when retrieval ran.

        ``retrieval_used`` gates the RAG evaluators (context-relevance,
        faithfulness) so they never run on chitchat / off-topic turns.
        ``search_query`` is the history-aware standalone question used for
        retrieval; evaluators map ``{{question}}`` to it so follow-ups are scored
        against a self-contained question rather than the bare latest message.
        ``conversation_history`` (prior question/answer turns only, no retrieved
        context) is recorded on every turn for user-facing judges such as a
        distress evaluator.
        """
        retrieval_used = route == "retrieve"
        metadata: dict = {"retrieval_used": retrieval_used}
        if messages is not None:
            metadata["conversation_history"] = self._format_history(messages)
        if retrieval_used:
            metadata["retrieved_context"] = self._format_context(docs)
            if search_query:
                metadata["search_query"] = search_query
        return metadata

    @staticmethod
    def _format_history(messages: list) -> str:
        """Render prior question/answer turns as a plain transcript.

        Excludes the current turn (its user message is the span input and its
        answer the span output) and never includes retrieved context, only
        the human/assistant exchange.
        """
        turns = [
            message
            for message in messages
            if getattr(message, "type", None) in ("human", "ai")
        ]
        role = {"human": "user", "ai": "assistant"}
        prior = turns[:-2]
        return "\n".join(
            f"{role.get(message.type, message.type)}: {message.content}"
            for message in prior
        )

    @staticmethod
    def _trace_attributes(session_id: str, user_id: str | None, manual_id: str):
        """Propagate session/user/tags onto the trace and its child observations."""
        from langfuse import propagate_attributes

        return propagate_attributes(
            session_id=session_id,
            user_id=user_id or session_id,
            tags=[f"manual:{manual_id}"],
        )

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
