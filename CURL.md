# Общение с MCP HR Server через curl

Сервер по умолчанию работает через **stdio** (для Cursor). Чтобы обращаться к нему по HTTP и использовать curl, запустите с транспортом **http**:

```bash
cd mcp
MCP_TRANSPORT=http uv run --with mcp python server.py
```

Сервер будет доступен по адресу: **http://127.0.0.1:8000/mcp**

---

## Быстрый старт (всё в одном блоке)

Скопируйте и выполните целиком в одном терминале — так переменная `SESSION_ID` точно сохранится:

```bash
MCP_URL="http://127.0.0.1:8000/mcp"
response=$(curl -s -D - -X POST -H "Content-Type: application/json" -H "Accept: application/json" \
  -d '{"jsonrpc":"2.0","method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"curl","version":"1.0"}},"id":1}' "$MCP_URL")
SESSION_ID=$(echo "$response" | grep -i "mcp-session-id" | sed 's/^[^:]*:[[:space:]]*//' | tr -d '\r\n')
echo "Session ID: $SESSION_ID"
curl -s -X POST -H "Content-Type: application/json" -H "Accept: application/json" -H "Mcp-Session-Id: $SESSION_ID" \
  -d '{"jsonrpc":"2.0","method":"notifications/initialized"}' "$MCP_URL"
curl -s -X POST -H "Content-Type: application/json" -H "Accept: application/json" -H "Mcp-Session-Id: $SESSION_ID" \
  -d '{"jsonrpc":"2.0","method":"tools/list","id":2}' "$MCP_URL" | jq .
```

После этого можно вызывать другие инструменты с тем же `$SESSION_ID`.

---

## Протокол: сессия + JSON-RPC

MCP over HTTP использует **сессии**. Нужно:

1. **Инициализировать сессию** (`initialize`) — в ответе приходит заголовок `Mcp-Session-Id`
2. **Подтвердить инициализацию** (`notifications/initialized`)
3. Дальше все запросы отправлять с заголовком `Mcp-Session-Id`
4. В конце можно **закрыть сессию** (DELETE)

Локально авторизация не обязательна. **Важно:** в каждом запросе должен быть заголовок `Accept: application/json`, иначе сервер вернёт «Not Acceptable».

---

## 1. Инициализация сессии

```bash
# Ответ приходит в теле; Session ID — в заголовках
response=$(curl -s -D - -X POST \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "initialize",
    "params": {
      "protocolVersion": "2024-11-05",
      "capabilities": {},
      "clientInfo": {
        "name": "curl-client",
        "version": "1.0.0"
      }
    },
    "id": 1
  }' \
  http://127.0.0.1:8000/mcp)

# Достаём Session ID из заголовков (всё после двоеточия, без пробелов и переводов строк)
SESSION_ID=$(echo "$response" | grep -i "mcp-session-id" | sed 's/^[^:]*:[[:space:]]*//' | tr -d '\r\n')
echo "Session ID: $SESSION_ID"
# Проверка: если пусто — смотрите вывод выше
[ -z "$SESSION_ID" ] && echo "ОШИБКА: Session ID не найден. Проверьте, что сервер запущен и вернул заголовок Mcp-Session-Id." && exit 1
```

Сохраните `SESSION_ID` — он нужен для всех следующих запросов. **Выполняйте все команды в одном и том же терминале**, иначе переменная будет пустой.

---

## 2. Подтверждение инициализации

```bash
curl -s -X POST \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -H "Mcp-Session-Id: $SESSION_ID" \
  -d '{"jsonrpc": "2.0", "method": "notifications/initialized"}' \
  http://127.0.0.1:8000/mcp
```

---

## 3. Список инструментов (tools/list)

```bash
curl -s -X POST \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -H "Mcp-Session-Id: $SESSION_ID" \
  -d '{"jsonrpc": "2.0", "method": "tools/list", "id": 2}' \
  http://127.0.0.1:8000/mcp | jq .
```

---

## 4. Вызов инструментов (tools/call)

### RAG-поиск по HR-документам

```bash
curl -s -X POST \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -H "Mcp-Session-Id: $SESSION_ID" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/call",
    "params": {
      "name": "hr_rag_search",
      "arguments": {
        "query": "сколько дней отпуска",
        "n_results": 3
      }
    },
    "id": 3
  }' \
  http://127.0.0.1:8000/mcp | jq .
```

### Персональные дни (все сотрудники)

```bash
curl -s -X POST \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -H "Mcp-Session-Id: $SESSION_ID" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/call",
    "params": {
      "name": "get_personal_days_tool",
      "arguments": {}
    },
    "id": 4
  }' \
  http://127.0.0.1:8000/mcp | jq .
```

### Персональные дни одного сотрудника

```bash
curl -s -X POST \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -H "Mcp-Session-Id: $SESSION_ID" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/call",
    "params": {
      "name": "get_personal_days_tool",
      "arguments": {"login": "ivanov"}
    },
    "id": 5
  }' \
  http://127.0.0.1:8000/mcp | jq .
```

### Оставшиеся дни отпуска

```bash
curl -s -X POST \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -H "Mcp-Session-Id: $SESSION_ID" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/call",
    "params": {
      "name": "get_remaining_vacation_days_tool",
      "arguments": {"login": "petrova"}
    },
    "id": 6
  }' \
  http://127.0.0.1:8000/mcp | jq .
```

---

## 5. Завершение сессии

```bash
curl -s -X DELETE \
  -H "Mcp-Session-Id: $SESSION_ID" \
  http://127.0.0.1:8000/mcp
```

---

## Полный пример в одном скрипте

Сохраните как `test_curl.sh` и выполните после запуска сервера (`MCP_TRANSPORT=http python server.py`):

```bash
#!/bin/bash
set -e
MCP_URL="http://127.0.0.1:8000/mcp"

echo "1. Initialize..."
response=$(curl -s -D - -X POST -H "Content-Type: application/json" -H "Accept: application/json" \
  -d '{"jsonrpc":"2.0","method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"curl","version":"1.0"}},"id":1}' "$MCP_URL")
SESSION_ID=$(echo "$response" | grep -i "mcp-session-id" | sed 's/^[^:]*:[[:space:]]*//' | tr -d '\r\n')
[ -z "$SESSION_ID" ] && echo "No session ID. Response:" && echo "$response" && exit 1
echo "Session: $SESSION_ID"

echo "2. Initialized notification..."
curl -s -X POST -H "Content-Type: application/json" -H "Accept: application/json" -H "Mcp-Session-Id: $SESSION_ID" \
  -d '{"jsonrpc":"2.0","method":"notifications/initialized"}' "$MCP_URL" > /dev/null

echo "3. List tools..."
curl -s -X POST -H "Content-Type: application/json" -H "Accept: application/json" -H "Mcp-Session-Id: $SESSION_ID" \
  -d '{"jsonrpc":"2.0","method":"tools/list","id":2}' "$MCP_URL" | jq .

echo "4. Call hr_rag_search..."
curl -s -X POST -H "Content-Type: application/json" -H "Accept: application/json" -H "Mcp-Session-Id: $SESSION_ID" \
  -d '{"jsonrpc":"2.0","method":"tools/call","params":{"name":"hr_rag_search","arguments":{"query":"отпуск"}},"id":3}' "$MCP_URL" | jq .

echo "5. Call get_remaining_vacation_days_tool..."
curl -s -X POST -H "Content-Type: application/json" -H "Accept: application/json" -H "Mcp-Session-Id: $SESSION_ID" \
  -d '{"jsonrpc":"2.0","method":"tools/call","params":{"name":"get_remaining_vacation_days_tool","arguments":{"login":"ivanov"}},"id":4}' "$MCP_URL" | jq .

echo "6. Terminate session..."
curl -s -X DELETE -H "Mcp-Session-Id: $SESSION_ID" "$MCP_URL"
echo "Done."
```

Запуск: `chmod +x test_curl.sh && ./test_curl.sh`
