from __future__ import annotations

from pathlib import Path

from langchain_core.messages import SystemMessage
from langchain_core.tools import tool
from langchain_openai import AzureChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition

from support_chatbot.settings import AppSettings


class ChatService:
    def __init__(self, settings: AppSettings, vector_store) -> None:
        self._vector_store = vector_store
        self._prompt = self._load_prompt()
        self._llm = AzureChatOpenAI(
            azure_endpoint=settings.azure_openai_endpoint,
            azure_deployment=settings.model_chat,
            openai_api_version=settings.azure_openai_api_version,
            api_key=settings.azure_openai_api_key.get_secret_value(),
            temperature=0.2,
        )
        self._graph = self._build_graph()

    def _load_prompt(self) -> str:
        prompt_path = (
            Path(__file__).resolve().parents[1] / "prompts" / "support_chatbot_prompt.txt"
        )
        return prompt_path.read_text(encoding="utf-8")

    def _build_graph(self):
        @tool(response_format="content_and_artifact")
        def retrieve(query: str):
            """Retrieve information related to a query."""
            retrieved_docs = self._vector_store.similarity_search(query, k=10)
            serialized = "\n\n".join(
                f"Document: {doc.page_content}" for doc in retrieved_docs
            )
            return serialized, retrieved_docs

        def query_or_respond(state: MessagesState):
            llm_with_tools = self._llm.bind_tools([retrieve])
            prompt = [SystemMessage(self._prompt)] + state["messages"]
            response = llm_with_tools.invoke(prompt)
            return {"messages": [response]}

        tools = ToolNode([retrieve])

        def generate(state: MessagesState):
            recent_tool_messages = []
            for message in reversed(state["messages"]):
                if message.type == "tool":
                    recent_tool_messages.append(message)
                else:
                    break

            docs_content = "\n\n".join(
                message.content for message in reversed(recent_tool_messages)
            )
            system_message_content = f"{self._prompt}.\n\n{docs_content}"
            conversation_messages = [
                message
                for message in state["messages"]
                if message.type in ("human", "system")
                or (message.type == "ai" and not message.tool_calls)
            ]

            prompt = [SystemMessage(system_message_content)] + conversation_messages
            response = self._llm.invoke(prompt)
            return {"messages": [response]}

        graph_builder = StateGraph(MessagesState)
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

    def ask(self, question: str, thread_id: str) -> str:
        config = {"configurable": {"thread_id": thread_id}}
        response = self._graph.invoke(
            {"messages": [{"role": "user", "content": question}]},
            config=config,
        )
        return response["messages"][-1].content
