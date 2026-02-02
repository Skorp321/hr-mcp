"""LangGraph ReAct агент с MCP HR инструментами."""

import os
from dotenv import load_dotenv
from typing import Annotated, Sequence, TypedDict

from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage, ToolMessage
from langchain_core.runnables import RunnableConfig
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_openai import ChatOpenAI
from langgraph.graph import END, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode

load_dotenv()

# Конфигурация MCP
MCP_HR_URL = os.environ.get("MCP_HR_URL", "http://127.0.0.1:8000/mcp")


class AgentState(TypedDict):
    """Состояние агента."""
    messages: Annotated[Sequence[BaseMessage], add_messages]


async def get_mcp_tools():
    """Загружает инструменты из MCP HR сервера."""
    import asyncio
    last_err = None
    for attempt in range(3):
        try:
            client = MultiServerMCPClient(
                connections={
                    "hr": {
                        "url": MCP_HR_URL,
                        "transport": "streamable-http",
                        "timeout": 30,
                    }
                }
            )
            tools = await client.get_tools()
            return tools
        except Exception as e:
            last_err = e
            if attempt < 2:
                await asyncio.sleep(2)
    raise last_err


def create_agent(tools):
    """Создаёт скомпилированный LangGraph ReAct агент."""
    api_key = os.environ.get("API_KEY") or os.environ.get("OPENAI_API_KEY")
    base_url = os.environ.get("OPENAI_BASE_URL", "https://foundation-models.api.cloud.ru/v1")
    model_name = os.environ.get("OPENAI_MODEL", "openai/gpt-oss-120b")

    model = ChatOpenAI(
        model=model_name,
        temperature=0,
        api_key=api_key,
        base_url=base_url,
    ).bind_tools(tools)

    tool_node = ToolNode(tools)

    def call_model(state: AgentState, config: RunnableConfig):
        messages = state["messages"]
        system = SystemMessage(
            content="""Ты — HR-ассистент. Отвечай на вопросы сотрудников о политиках компании:
отпуска, персональные дни, больничные, удалённая работа, командировки, льготы.
Используй доступные инструменты для поиска информации и получения данных.
Отвечай на русском языке кратко и по делу.
Логины сотрудников: ivanov, petrova, sidorov."""
        )
        response = model.invoke([system] + list(messages), config)
        return {"messages": [response]}

    def should_continue(state: AgentState):
        last = state["messages"][-1]
        if hasattr(last, "tool_calls") and last.tool_calls:
            return "tools"
        return "end"

    workflow = StateGraph(AgentState)

    workflow.add_node("agent", call_model)
    workflow.add_node("tools", tool_node)

    workflow.set_entry_point("agent")
    workflow.add_conditional_edges("agent", should_continue, {"tools": "tools", "end": END})
    workflow.add_edge("tools", "agent")

    return workflow.compile()


# Глобальный граф (инициализируется при первом запросе)
_agent_graph = None


async def get_agent():
    """Возвращает скомпилированный агент (с ленивой инициализацией)."""
    global _agent_graph
    if _agent_graph is None:
        tools = await get_mcp_tools()
        _agent_graph = create_agent(tools)
    return _agent_graph
