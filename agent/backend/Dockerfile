FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8001

ENV MCP_HR_URL=http://mcp:8000/mcp

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]
