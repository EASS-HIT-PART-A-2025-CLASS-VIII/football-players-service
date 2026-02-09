# Football Player Management System

A full-stack microservices app for managing football player data with AI-powered scouting reports, JWT authentication, and async task tracking.

## Features

- CRUD for players with validation and pagination
- JWT authentication for write operations
- AI scouting reports generated via Gemini
- Async task tracking with status polling
- Docker Compose orchestration for local development

## Architecture (Short)

- Frontend calls the backend API with Axios and a JWT interceptor.
- Backend enqueues AI scout jobs to Redis and returns a task id.
- Worker consumes the task, calls the AI service, and saves the report.
- Frontend polls task status and renders the report when completed.

## Quick Start (Docker Compose)

1. Create a local environment file:

```bash
cp .env.example .env
```

On Windows, you can use `copy .env.example .env`.

2. Add your `GEMINI_API_KEY` to the .env file.

3. Start all services:

```bash
docker compose up --build
```

4. Open the app and log in:

- Frontend: http://localhost:3000
- Default credentials: admin / admin123

For full operational details, see [docs/runbooks/compose.md](docs/runbooks/compose.md).

## Local Development (Optional)

Backend:

```bash
cd backend
uv sync
uv run python -m uvicorn football_player_service.app.main:app --reload --port 8000
```

Frontend:

```bash
cd frontend
npm install
npm run dev
```

Redis:

```bash
docker run -d -p 6379:6379 redis:alpine
```

Worker:

```bash
cd backend
uv run celery -A worker.main.celery_app worker --loglevel=info
```

AI service:

```bash
cd backend/ai_service
pip install -r requirements.txt
uvicorn main:app --port 8001
```

## Usage

- List players: GET /players
- Create player: POST /players (JWT required)
- Scout player: POST /players/{id}/scout (JWT required)
- Task status: GET /tasks/{task_id}

The scout flow is async: request -> task id -> poll status -> report saved.

## Hand-Off Notes (Short + Focused)

This is the documentation you wish every teammate handed you:

- Use [docs/runbooks/compose.md](docs/runbooks/compose.md) as the single source of truth for Docker Compose commands and troubleshooting.
- JWT is required for writes and scouting. Use admin/admin123 after first boot.
- The frontend polls task status every 2 seconds to show progress.
- The demo script in [backend/scripts/demo.py](backend/scripts/demo.py) shows the full flow end-to-end.

## Repository Structure (Short Map)

```
.|-- backend/
|   |-- ai_service/
|   |-- analytics_service/
|   |-- data/
|   |-- data_scraper/
|   |-- football_player_service/
|   |-- scripts/
|   |-- tests/
|   |-- worker/
|   |-- worker_service/
.|-- docs/
.|-- frontend/
.|-- docker-compose.yml
```

Explanation:

- [backend/](backend/) - Python services, scripts, and tests.
- [backend/ai_service/](backend/ai_service/) - FastAPI microservice that calls Gemini.
- [backend/analytics_service/](backend/analytics_service/) - Empty stub; not used.
- [backend/data/](backend/data/) - SQLite data and persisted volume.
- [backend/data_scraper/](backend/data_scraper/) - CSV loader and helper scripts.
- [backend/football_player_service/](backend/football_player_service/) - Main FastAPI app (models, routes, auth, DB, tests).
- [backend/scripts/](backend/scripts/) - Demo, seeding, CSV loading, refresh job, entrypoint.
- [backend/tests/](backend/tests/) - Extra tests outside the app package.
- [backend/worker/](backend/worker/) - Celery worker for scout tasks.
- [backend/worker_service/](backend/worker_service/) - Empty stub; not used.
- [frontend/](frontend/) - React UI (components, hooks, services, styles).
- [docs/](docs/) - Architecture notes and runbooks.
- [docker-compose.yml](docker-compose.yml) - Service orchestration.

## Documentation

- [docs/EX3-notes.md](docs/EX3-notes.md) - Architecture, security, and task tracking notes.
- [docs/runbooks/compose.md](docs/runbooks/compose.md) - Docker Compose operations and troubleshooting.
- [backend/README.md](backend/README.md) - Backend setup and tests.
- [frontend/README.md](frontend/README.md) - Frontend setup and build.

## Testing

```bash
docker compose exec backend uv run pytest football_player_service/tests -v
```

Local (from `backend/`):

```bash
uv run pytest football_player_service/tests -v
uv run pytest tests/test_refresh.py -v
uv run pytest ai_service/test_main.py -v
```

## AI Assistance

This project was built with help from:

- GitHub Copilot - Code completion and refactoring
- Claude (Anthropic) - Documentation review and debugging

Prompts and focus areas:

- Review architecture and repository file structure for a clear handoff
- Validate Docker Compose service layout and startup flow
- Identify and document all test commands

Verification:

- Manual testing of login, CRUD, and scout flows
- Automated pytest suite

## License

MIT
