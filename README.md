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

**Вариант 1 (uv):**
```bash
cd MCP-hr
uv run --with mcp python server.py
```

**Вариант 2 (venv + pip):**
```bash
cd MCP-hr
python3 -m venv venv
source venv/bin/activate   # Linux/macOS
pip install -r requirements.txt
python server.py
```

RAG использует семантический поиск по ключевым словам (без внешних ML-моделей).

## Запуск

```bash
MCP_TRANSPORT=http uv run --with mcp python server.py
# или с venv: MCP_TRANSPORT=http python server.py
```

**Общение через curl (HTTP):** запустите с `MCP_TRANSPORT=http`, затем используйте примеры из [CURL.md](CURL.md).
