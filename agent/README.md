# HR Agent (LangGraph + React)

Агент на LangGraph, использующий MCP HR сервер. React-интерфейс для чата.

## Запуск локально

### 1. MCP сервер (в отдельном терминале)

```bash
cd mcp
MCP_TRANSPORT=http uv run --with mcp python server.py
```

### 2. Backend агента

```bash
cd agent/backend
pip install -r requirements.txt
export OPENAI_API_KEY=sk-...
uvicorn main:app --host 127.0.0.1 --port 8001
```

### 3. React frontend

```bash
cd agent/frontend
npm install
npm run dev
```

Откройте http://localhost:5173

## Docker Compose

```bash
export OPENAI_API_KEY=sk-...
docker-compose up -d
```

Затем запустите frontend локально (`npm run dev`) — он проксирует запросы на agent-api:8001.

Или добавьте frontend в docker-compose при необходимости.
