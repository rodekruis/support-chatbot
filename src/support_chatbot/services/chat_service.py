"""Chat orchestration service for manual question answering."""

from __future__ import annotations

from langchain_core.messages import SystemMessage
from langchain_core.runnables import RunnableConfig
from langchain_core.tools import tool
from langchain_openai import AzureChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition

from support_chatbot.adapters.vector_store import VectorStoreProvider
from support_chatbot.config.manuals import DEFAULT_MANUAL_ID, get_manual_prompt
from support_chatbot.settings import AppSettings


class ChatState(MessagesState):
    """State stored in the LangGraph conversation graph."""

    system_prompt: str


class ChatService:
    """Coordinate prompt loading, retrieval, and answer generation."""

    def __init__(
        self,
        settings: AppSettings,
        provider: VectorStoreProvider,
        default_manual_id: str = DEFAULT_MANUAL_ID,
    ) -> None:
        """Initialize the language model and retrieval graph."""
        self._provider = provider
        self._default_manual_id = default_manual_id
        self._prompt_cache: dict[str, str] = {}
        self._llm = AzureChatOpenAI(
            azure_endpoint=settings.azure_openai_endpoint,
            azure_deployment=settings.model_chat,
            openai_api_version=settings.azure_openai_api_version,
            api_key=settings.azure_openai_api_key.get_secret_value(),
            temperature=0.2,
        )
        self._graph = self._build_graph()

    def _get_prompt(self, manual_id: str) -> str:
        if manual_id not in self._prompt_cache:
            self._prompt_cache[manual_id] = get_manual_prompt(manual_id)
        return self._prompt_cache[manual_id]

    def _build_graph(self):
        @tool(response_format="content_and_artifact")
        def retrieve(query: str, config: RunnableConfig):
            """Retrieve information related to a query."""
            manual_id = config["configurable"].get("manual_id", self._default_manual_id)
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

    def ask(
        self,
        question: str,
        thread_id: str,
        manual_id: str | None = None,
    ) -> str:
        """Ask the chatbot a question and return the final assistant reply."""
        manual_id = manual_id or self._default_manual_id
        system_prompt = self._get_prompt(manual_id)
        config = {"configurable": {"thread_id": thread_id, "manual_id": manual_id}}
        response = self._graph.invoke(
            {
                "messages": [{"role": "user", "content": question}],
                "system_prompt": system_prompt,
            },
            config=config,
        )
        return response["messages"][-1].content
