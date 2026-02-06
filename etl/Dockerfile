# ETL API Docker Image
# Build from repo root with context ./etl:  docker build -f etl/Dockerfile ./etl
# Or with compose (see docker-compose.yml: etl build context must be ./etl)
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Build context is ./etl: copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy ETL package into /app/etl so "from etl.xxx" resolves with PYTHONPATH=/app
COPY . /app/etl

RUN mkdir -p /app/etl/data /app/logs

ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

EXPOSE 8000

CMD ["uvicorn", "etl.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
