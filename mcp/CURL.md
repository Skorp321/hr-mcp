# Общение с MCP HR Server через curl

Сервер по умолчанию работает через **stdio** (для Cursor). Чтобы обращаться к нему по HTTP и использовать curl, запустите с транспортом **http**:

```bash
cd mcp
MCP_TRANSPORT=http uv run --with mcp python server.py
```

Сервер будет доступен по адресу: **http://127.0.0.1:8000/mcp**

---

## Быстрый старт

```bash
MCP_URL="http://127.0.0.1:8000/mcp"
response=$(curl -s -D - -X POST -H "Content-Type: application/json" -H "Accept: application/json" \
  -d '{"jsonrpc":"2.0","method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"curl","version":"1.0"}},"id":1}' "$MCP_URL")
SESSION_ID=$(echo "$response" | grep -i "mcp-session-id" | sed 's/^[^:]*:[[:space:]]*//' | tr -d '\r\n')
curl -s -X POST -H "Content-Type: application/json" -H "Accept: application/json" -H "Mcp-Session-Id: $SESSION_ID" \
  -d '{"jsonrpc":"2.0","method":"notifications/initialized"}' "$MCP_URL"
curl -s -X POST -H "Content-Type: application/json" -H "Accept: application/json" -H "Mcp-Session-Id: $SESSION_ID" \
  -d '{"jsonrpc":"2.0","method":"tools/list","id":2}' "$MCP_URL" | jq .
```

См. полную документацию в [CURL.md](../CURL.md) в корне проекта.
