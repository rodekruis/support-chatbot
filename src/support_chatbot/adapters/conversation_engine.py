"""LangGraph + LangChain conversation engine adapter.

Implements the :class:`ConversationEngine` port using Azure OpenAI for
generation and a LangGraph retrieval graph for tool-augmented answering. All
LangChain / LangGraph specifics are confined to this adapter so the services
layer stays framework-agnostic.
"""

from __future__ import annotations

from langchain_core.messages import SystemMessage
from langchain_core.runnables import RunnableConfig
from langchain_core.tools import tool
from langchain_openai import AzureChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition

from support_chatbot.domain.models import AskResponse
from support_chatbot.domain.ports import ConversationEngine, VectorStoreProvider
from support_chatbot.settings import AppSettings


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
            retrieved_docs = vector_store.similarity_search(query, k=5)
            serialized = "\n\n".join(
                f"Document: {doc.page_content}" for doc in retrieved_docs
            )
            return serialized, retrieved_docs

        def query_or_respond(state: ChatState):
            llm_with_tools = self._llm.bind_tools([retrieve])
            prompt = [SystemMessage(state["system_prompt"])] + state["messages"]
            response = llm_with_tools.invoke(prompt)
            return {"messages": [response]}

        tools = ToolNode([retrieve])

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

        graph_builder = StateGraph(ChatState)
        graph_builder.add_node(query_or_respond)
        graph_builder.add_node(tools)
        graph_builder.add_node(generate)
        graph_builder.set_entry_point("query_or_respond")
        graph_builder.add_conditional_edges(
            "query_or_respond",
            tools_condition,
            {END: END, "tools": "tools"},
        )
        graph_builder.add_edge("tools", "generate")
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
        response = self._graph.invoke(
            {
                "messages": [{"role": "user", "content": question}],
                "system_prompt": system_prompt,
            },
            config=config,
        )
        return AskResponse(answer=response["messages"][-1].content, trace_id=trace_id)

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
