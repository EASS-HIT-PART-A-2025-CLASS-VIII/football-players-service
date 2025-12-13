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

---

## 🐳 Docker

```bash
# Build
docker build -t football-service -f backend/football_player_service/Dockerfile backend

# Run
docker run --rm -p 8000:8000 football-service
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

Create `.env`:

```bash
PLAYER_APP_NAME=Football Player Service
```

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
