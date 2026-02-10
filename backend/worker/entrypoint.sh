#!/usr/bin/env sh
set -e

: "${PORT:=10000}"

# Start a minimal HTTP server so Render detects an open port.
python -m http.server "$PORT" --bind 0.0.0.0 >/dev/null 2>&1 &

exec uv run celery -A worker.main.celery_app worker --loglevel=info
