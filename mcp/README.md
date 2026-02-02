# MCP HR Server

MCP-сервер на Python с RAG и инструментами для HR-данных.

## Инструменты

| Инструмент | Описание |
|------------|----------|
| `hr_rag_search` | RAG-поиск по HR-документам (политики отпусков, больничные, командировки и т.д.) |
| `get_personal_days_tool` | Персональные дни сотрудников (дни рождения, годовщины) |
| `get_remaining_vacation_days_tool` | Оставшиеся дни отпуска |

Данные по персональным дням и отпускам — моковые. Логины: ivanov, petrova, sidorov.

## Установка

```bash
cd mcp
uv run --with mcp python server.py
# или: pip install -r requirements.txt && python server.py
```

## HTTP режим (для агента)

```bash
MCP_TRANSPORT=http uv run --with mcp python server.py
```

Сервер будет доступен по адресу: **http://127.0.0.1:8000/mcp**
