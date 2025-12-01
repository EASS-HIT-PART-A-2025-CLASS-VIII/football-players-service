FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
	PYTHONUNBUFFERED=1 \
	PATH="/app/.venv/bin:$PATH"

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

COPY pyproject.toml uv.lock ./

RUN uv sync --frozen --no-dev

COPY football_player_service ./football_player_service

COPY .env ./.env

EXPOSE 8000

CMD ["uv", "run", "uvicorn", "football_player_service.app.main:app", "--host", "0.0.0.0", "--port", "8000"]

