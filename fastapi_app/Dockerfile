FROM node:20-slim AS frontend-build
WORKDIR /build
COPY frontend/package*.json ./
RUN npm ci || npm install
COPY frontend/ ./
RUN npm run build

FROM python:3.12-slim AS base

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        gcc \
        g++ \
        default-jdk-headless \
        curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY fastapi_app/requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY fastapi_app/ .

COPY --from=frontend-build /build/dist /app/frontend/dist

ENV PYTHONPATH=/app \
    DATABASE_URL=sqlite+aiosqlite:////tmp/devstudio.db \
    FRONTEND_DIST=/app/frontend/dist

RUN useradd --create-home --shell /bin/bash appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=12s --retries=3 \
    CMD curl -fsS http://localhost:8000/health || exit 1

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
