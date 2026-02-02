# MCP HR Server + Agent

MCP-сервер на Python с RAG и инструментами для HR-данных. React-агент на LangGraph.

## Структура

| Папка | Описание |
|-------|----------|
| `mcp/` | MCP HR сервер (RAG, персональные дни, отпуска) |
| `agent/` | LangGraph агент + React UI |

## MCP сервер (mcp/)

### Инструменты

| Инструмент | Описание |
|------------|----------|
| `hr_rag_search` | RAG-поиск по HR-документам |
| `get_personal_days_tool` | Персональные дни сотрудников |
| `get_remaining_vacation_days_tool` | Оставшиеся дни отпуска |

Логины: ivanov, petrova, sidorov.

### Запуск MCP

```bash
MCP_TRANSPORT=http uv run --with mcp python server.py
# или с venv: MCP_TRANSPORT=http python server.py
```

**Общение через curl (HTTP):** запустите с `MCP_TRANSPORT=http`, затем используйте примеры из [CURL.md](CURL.md).
