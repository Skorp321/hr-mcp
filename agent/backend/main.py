"""FastAPI backend для HR-агента."""

import os
from typing import List

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from agent_graph import get_agent, get_mcp_tools

app = FastAPI(title="HR Agent API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    message: str
    history: List[dict] = []


class ChatResponse(BaseModel):
    response: str


@app.get("/health")
def health():
    """Проверка работоспособности."""
    return {"status": "ok"}


@app.get("/mcp/status")
async def mcp_status():
    """Статус MCP-сервера и список инструментов."""
    try:
        tools = await get_mcp_tools()
        return {
            "connected": True,
            "url": os.environ.get("MCP_HR_URL", "http://127.0.0.1:8000/mcp"),
            "tools": [
                {"name": t.name, "description": (t.description or "")[:200]}
                for t in tools
            ],
        }
    except Exception as e:
        return {
            "connected": False,
            "url": os.environ.get("MCP_HR_URL", "http://127.0.0.1:8000/mcp"),
            "error": str(e),
            "tools": [],
        }


@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    """Отправка сообщения агенту."""
    if not req.message.strip():
        raise HTTPException(status_code=400, detail="Сообщение не может быть пустым")

    if not os.environ.get("OPENAI_API_KEY"):
        return ChatResponse(
            response="Ошибка: OPENAI_API_KEY не задан. Установите переменную окружения."
        )

    try:
        agent = await get_agent()

        # Преобразуем историю в сообщения
        from langchain_core.messages import AIMessage, HumanMessage

        messages = []
        for h in req.history:
            if h.get("role") == "user":
                messages.append(HumanMessage(content=h.get("content", "")))
            elif h.get("role") == "assistant":
                messages.append(AIMessage(content=h.get("content", "")))

        messages.append(HumanMessage(content=req.message))

        result = await agent.ainvoke(
            {"messages": messages},
            config={"configurable": {}},
        )

        last_message = result["messages"][-1]
        response_text = last_message.content if hasattr(last_message, "content") else str(last_message)

        return ChatResponse(response=response_text or "Нет ответа.")

    except Exception as e:
        msg = str(e)
        if hasattr(e, "exceptions") and e.exceptions:
            msg = "; ".join(str(x) for x in e.exceptions)
        return ChatResponse(response=f"Ошибка: {msg}")
