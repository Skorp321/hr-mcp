# MCP HR Server + Agent

MCP-сервер на Python с RAG и инструментами для HR-данных. React-агент на LangGraph с трейсингом в Arize Phoenix.

## Быстрый старт

```bash
# Запуск всех сервисов через Docker Compose
docker-compose up --build
```

**Доступные сервисы:**
- **Frontend**: http://localhost:3000 - веб-интерфейс HR-ассистента
- **Agent API**: http://localhost:8001 - backend API агента
- **MCP Server**: http://localhost:8000 - MCP сервер с HR инструментами
- **Phoenix UI**: http://localhost:6006 - мониторинг и трейсинг LLM запросов

## Структура

| Папка | Описание |
|-------|----------|
| `mcp/` | MCP HR сервер (RAG, персональные дни, отпуска) |
| `agent/` | LangGraph агент + React UI |

## Phoenix Tracing

Все запросы к LLM автоматически трассируются в Arize Phoenix:
- Промпты и ответы модели
- Время выполнения и токены
- Вызовы инструментов (MCP tools)
- Цепочки выполнения (traces)

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
