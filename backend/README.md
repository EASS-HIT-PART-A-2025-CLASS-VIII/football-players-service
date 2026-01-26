## AI Scout Microservice (Exercise 3)

### Backend Changes

- Added `scouting_report` field to Player model.
- New endpoint: `POST /players/{id}/scout` (enqueues async AI scouting report task).
- New worker: `backend/scripts/worker.py` (Celery worker for AI Scout logic).

### Database Migration

- If using Alembic, generate and apply a migration to add the `scouting_report` column to the `players` table:
  ```bash
  alembic revision --autogenerate -m "add scouting_report to player"
  alembic upgrade head
  ```
- If not using Alembic, delete the database file and restart to auto-create tables (for dev only).

# ⚽ Football Player Service

A production-ready FastAPI CRUD service for managing football player data.

## 🚀 Quick Start

```bash
cd backend

# Setup
uv sync --no-dev

# Run
uv run python -m uvicorn football_player_service.app.main:app --reload --port 8000
```

**API Docs:** `http://localhost:8000/docs` (Swagger UI)

---

## 🔧 Tech Stack

- **FastAPI** (Python 3.13+)
- **SQLModel** — Database ORM
- **SQLite** (local) / **PostgreSQL** (production) — Flexible database backend
- **Pydantic v2** — Validation
- **pytest** — 21 comprehensive tests
- **Docker** — Containerization
- **Rate Limiting** — 100 req/min per IP
- **Security Headers** — CORS, HSTS, Content-Type protection

---

## 📚 API Endpoints

```
GET    /health              # Health check
GET    /players             # List all
POST   /players             # Create
GET    /players/{id}        # Get one
PUT    /players/{id}        # Update
DELETE /players/{id}        # Delete
```

**Example:**

```bash
# Create
curl -X POST http://localhost:8000/players \
  -H "Content-Type: application/json" \
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

# Delete
curl -X DELETE http://localhost:8000/players/1
```

---

## ✅ Testing

```bash
# Install dev deps
uv sync

# Run tests
uv run pytest football_player_service/tests -v

# With coverage
uv run pytest football_player_service/tests --cov=football_player_service --cov-report=term-missing
```

**Coverage:** 21 tests — Happy path, validation, error handling, security

### Test Architecture

- **In-memory SQLite** — Tests use `cache=shared` in-memory database for speed & isolation
- **Fixtures** (`conftest.py`) — Session-scoped test database, auto-cleanup between tests
- **Full integration** — Tests cover HTTP → FastAPI → Repository → SQLite → Response
- **No mocks** — Real database operations ensure behavior correctness

---

## 🐳 Docker

### Local Development (In-Memory SQLite)

```bash
# Build
docker build -t football-service -f backend/football_player_service/Dockerfile backend

# Run
docker run --rm -p 8000:8000 football-service
```

Visit http://localhost:8000/docs

**Note:** Uses in-memory SQLite — data is lost when container stops (fine for testing)

### Production Deployment on Render

Set `DATABASE_URL` environment variable to your PostgreSQL connection string:

```bash
docker run --rm -p 8000:8000 \
  -e DATABASE_URL="postgresql://user:pass@host:5432/db" \
  football-service
```

---

## 🛠 Development

### Setup

```bash
uv sync          # Install dev deps
pre-commit install    # Enable git hooks
```

### Commands

```bash
uv run ruff format .           # Format
uv run ruff check .            # Lint
uv run pytest ... -v           # Test
uv run pytest ... --cov        # Test with coverage
```

### Configuration

Create `.env` (optional):

```bash
PLAYER_APP_NAME=Football Player Service
# Local development (default)
DATABASE_URL=sqlite:///./football_players.db

# Or for PostgreSQL
# DATABASE_URL=postgresql://user:pass@localhost:5432/football_players
```

**Database Behavior:**

- **Local:** SQLite file at `football_players.db` (auto-created)
- **Render/Production:** Set `DATABASE_URL` env var to PostgreSQL connection string
- Code automatically switches between SQLite and PostgreSQL

---

## 📋 Validation Rules

| Field          | Type  | Constraints            |
| -------------- | ----- | ---------------------- |
| `full_name`    | `str` | Required, 2-100 chars  |
| `country`      | `str` | Required, ≤50 chars    |
| `status`       | `str` | "active" or "inactive" |
| `current_team` | `str` | Required, ≤100 chars   |
| `league`       | `str` | Required, ≤50 chars    |
| `age`          | `int` | Required, 0-120        |
| `market_value` | `int` | Optional, ≤10B USD     |

---

## ❌ Error Responses

| Status | Code               | Meaning             |
| ------ | ------------------ | ------------------- |
| `422`  | `VALIDATION_ERROR` | Invalid input       |
| `404`  | `PLAYER_NOT_FOUND` | Player not found    |
| `429`  | `RATE_LIMIT`       | Rate limit exceeded |
| `500`  | `INTERNAL_ERROR`   | Server error        |

---

## 📦 What is `uv`?

`uv` is a fast Python package manager (replaces pip + venv):

```bash
uv sync       # Create .venv + install deps
uv run CMD    # Run command (auto-activates venv)
```

No manual `activate` needed!

---

## 📄 License

MIT
