# Football Player Service (Backend API)

A FastAPI backend for managing football player data with validation, JWT auth, rate limiting, and async AI scouting.

## Quick Start (Backend Only)

```bash
cd backend

# Setup
uv sync --no-dev

# Run
uv run python -m uvicorn football_player_service.app.main:app --reload --port 8000
```

API docs: http://localhost:8000/docs

## AI Scout (Async)

The scout feature uses Redis + Celery and calls the AI service. If you only run the backend process, the scout endpoints will not complete without the worker and AI service.

For the full stack (backend, frontend, worker, Redis, AI service), see docs/runbooks/compose.md.

## Overview

Football Player Service with AI-powered scouting reports - a complete microservices demonstration showcasing async job processing, task tracking, and service-to-service communication.

## Microservices Architecture

The solution consists of **5 cooperating services** managed via Docker Compose:

### 1. Backend (FastAPI) - Main API Gateway

- **Port:** 8000
- **Role:** Core REST API for player CRUD operations and task orchestration
- **Tech:** FastAPI, SQLModel, SQLite, Redis, Celery
- **Key Endpoints:**
  - `GET/POST /players` - Player management
  - `POST /players/{id}/scout` - Enqueue AI scouting task (returns task_id)
  - `GET /tasks/{task_id}` - Check async task status (NEW)
  - `GET /health` - Health check
  - `POST /token` - JWT authentication (preserved for future use)

### 2. Frontend (React + TypeScript)

- **Port:** 3000
- **Role:** User interface for managing players and viewing scout reports
- **Tech:** React, TypeScript, TanStack Query, Axios
- **Features:**
  - Player CRUD with pagination
  - Scout button with real-time progress tracking
  - Modal UI for viewing reports
  - Automatic refresh after report generation

### 3. Worker (Celery)

- **Role:** Background task processor for AI scouting
- **Tech:** Celery, Redis, SQLModel
- **Behavior:**
  - Picks tasks from Redis queue
  - Fetches player data from database
  - Calls AI Service via HTTP
  - Updates player record with report
  - Stores task status in Redis for tracking

### 4. AI Service (FastAPI)

- **Port:** 8001 (internal: 8000)
- **Role:** Dedicated microservice wrapping Google Gemini API
- **Tech:** FastAPI, google-generativeai Python library
- **Endpoints:**
  - `POST /generate` - Generate scouting report
  - `GET /health` - Health check
- **Fallback:** Returns simulated report if GEMINI_API_KEY not set

### 5. Redis

- **Port:** 6379
- **Role:** Message broker for Celery + task status cache
- **Uses:**
  - Celery broker (task queue)
  - Celery backend (task results)
  - Custom task status tracking (1-hour TTL)

```
┌─────────────┐
│   Frontend  │ (React - Port 3000)
└──────┬──────┘
       │ HTTP
       ▼
┌─────────────┐     Celery Task      ┌─────────────┐
│   Backend   │◄────────────────────►│    Redis    │
│  (FastAPI)  │                      │             │
└──────┬──────┘                      └──────┬──────┘
       │                                     │
       │                                     │ Poll Tasks
       │                                     ▼
       │                              ┌─────────────┐     HTTP      ┌─────────────┐
       │                              │   Worker    │──────────────►│ AI Service  │
       │                              │  (Celery)   │               │  (Gemini)   │
       │                              └──────┬──────┘               └─────────────┘
       │                                     │
       │                                     │
       ▼                                     ▼
┌─────────────────────────────────────────────┐
│           SQLite Database                   │
│        (Shared via Docker Volume)           │
└─────────────────────────────────────────────┘
```

## API Endpoints

```
GET    /health              # Health check
GET    /players             # List all
POST   /players             # Create (auth)
GET    /players/{id}        # Get one
PUT    /players/{id}        # Update (auth)
DELETE /players/{id}        # Delete (auth)
POST   /players/{id}/scout  # Enqueue AI scout (auth)
GET    /tasks/{task_id}     # Task status
```

Example:

```bash
# Create (auth required)
curl -X POST http://localhost:8000/players \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <TOKEN>" \
  -d '{
    "full_name": "Lionel Messi",
    "country": "Argentina",
    "status": "active",
    "current_team": "Inter Miami",
    "league": "MLS",
    "market_value": 15000000,
    "age": 37
  }'

# Get
curl http://localhost:8000/players/1
```

## Authentication

- Login: `POST /token` (form data: `username`, `password`)
- Default admin credentials: `admin` / `admin123`
- Protected endpoints: Create, Update, Delete, Scout
- Public endpoints: Health, List players, Get player, Task status

## Tech Stack

- FastAPI (Python 3.13+)
- SQLModel
- SQLite (local) or PostgreSQL (production)
- Pydantic v2
- Redis + Celery (async tasks)

## Testing

```bash
# Install dev deps
uv sync

# Run tests
uv run pytest football_player_service/tests -v

# With coverage
uv run pytest football_player_service/tests --cov=football_player_service --cov-report=term-missing
```

## Docker (Backend Only)

```bash
# Build
docker build -t football-service -f backend/football_player_service/Dockerfile backend

# Run
docker run --rm -p 8000:8000 football-service
```

## Configuration

Create `.env` (optional):

```bash
PLAYER_APP_NAME=Football Player Service
# Local development (default)
DATABASE_URL=sqlite:///./football_players.db

# Or for PostgreSQL
# DATABASE_URL=postgresql://user:pass@localhost:5432/football_players
```

Database behavior:

- Local: SQLite file at `football_players.db` (auto-created)
- Production: set `DATABASE_URL` to a PostgreSQL connection string

## Validation Rules

| Field        | Type | Constraints             |
| ------------ | ---- | ----------------------- |
| full_name    | str  | Required, 2-100 chars   |
| country      | str  | Required, 50 chars max  |
| status       | str  | active or inactive      |
| current_team | str  | Required, 100 chars max |
| league       | str  | Required, 50 chars max  |
| age          | int  | Required, 0-120         |
| market_value | int  | Optional, 10B USD max   |

## Error Responses

| Status | Code             | Meaning             |
| ------ | ---------------- | ------------------- |
| 422    | VALIDATION_ERROR | Invalid input       |
| 404    | PLAYER_NOT_FOUND | Player not found    |
| 429    | RATE_LIMIT       | Rate limit exceeded |
| 500    | INTERNAL_ERROR   | Server error        |

## What is uv?

`uv` is a fast Python package manager (replaces pip + venv):

```bash
uv sync       # Create .venv + install deps
uv run CMD    # Run command (auto-activates venv)
```

## AI Assistance

Prompts and focus areas:

- Review the worker + AI service integration points and the async scout flow
- Validate JWT auth and task tracking behavior in the backend
- Confirm test coverage for core CRUD and refresh logic

Verification:

- Manual API checks for login, create/update/delete, and scout
- Pytest runs for `football_player_service/tests` and `tests/test_refresh.py`

## License

MIT
