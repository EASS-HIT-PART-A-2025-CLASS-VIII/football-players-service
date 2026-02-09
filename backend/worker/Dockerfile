FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
	PYTHONUNBUFFERED=1 \
	PATH="/app/.venv/bin:$PATH"

WORKDIR /app

# Install curl for health checks (optional for worker)
RUN apt-get update && apt-get install -y --no-install-recommends curl && \
    rm -rf /var/lib/apt/lists/*

# Create non-root user for security
RUN useradd -m -u 1000 appuser

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

COPY pyproject.toml ./

RUN uv sync --no-dev

COPY football_player_service ./football_player_service
COPY worker ./worker

# Ensure data directory exists if it needs to access DB file
RUN mkdir -p /app/data && chown -R appuser:appuser /app

USER appuser

# Worker command
# Make sure to run from /app so python allows imports
CMD ["uv", "run", "celery", "-A", "worker.main.celery_app", "worker", "--loglevel=info"]
