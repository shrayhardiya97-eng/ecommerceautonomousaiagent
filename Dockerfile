# Production Dockerfile for FastAPI AI Shopping Agent Backend
FROM python:3.11-slim AS builder

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir --prefix=/install -r requirements.txt

# Final minimal runtime container
FROM python:3.11-slim AS runner

WORKDIR /app

COPY --from=builder /install /usr/local

# Copy application source code
COPY app/ ./app/
COPY main.py .
COPY cli.py .

# Create non-root system user for production security
RUN useradd -m -u 1001 appuser && \
    chown -R appuser:appuser /app
USER appuser

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8000 \
    ENVIRONMENT=production

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "app.api.server:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2", "--proxy-headers", "--forwarded-allow-ips", "*"]
