FROM python:3.11-slim

WORKDIR /app

# Устанавливаем компилятор и зависимости для сборки
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем Phoenix (последняя версия)
RUN pip install --no-cache-dir \
    arize-phoenix

EXPOSE 6006 4317 4318

ENV PHOENIX_WORKING_DIR=/phoenix
ENV PHOENIX_SQL_DATABASE_URL=sqlite:////phoenix/phoenix.db

CMD ["phoenix", "serve"]
