# ⚽ Football Player Service ⚽

> A lightweight, production-ready FastAPI CRUD service for managing football player data. Built with security, testing, and clean architecture in mind.

**Live Demo:** <a href="https://football-players-service.onrender.com/docs" target="_blank" rel="noopener noreferrer">Interactive API Docs ⚽</a> | **Status:** ✅ Active

## Features

- ⚡ **Fast & Modern** — Built with FastAPI & Pydantic for validation
- 🔒 **Secure** — Rate limiting (100 req/min), security headers, CORS support
- 🏗️ **Clean Architecture** — Separation of concerns (models → repository → handlers)
- ✅ **Fully Tested** — 21 comprehensive pytest tests with edge case coverage
- 🐳 **Containerized** — Docker support with health checks & non-root user
- 📚 **Auto-Documented** — OpenAPI/Swagger docs auto-generated from code

## Quick Start

### Prerequisites

- **Python:** 3.13+ (or 3.12+)
- **Package Manager:** `uv` (recommended) or `pip`
- **Optional:** Docker for containerized deployment

### Installation & Run

```bash
# Clone repository
git clone https://github.com/EASS-HIT-PART-A-2025-CLASS-VIII/football-players-service.git
cd football-players-service/backend

# Install dependencies (creates .venv and installs packages)
uv sync --no-dev

# Start development server
# On Windows/MINGW64, use:
uv run python -m uvicorn football_player_service.app.main:app --reload --port 8000

# On macOS/Linux, you can also use:
# uv run uvicorn football_player_service.app.main:app --reload --port 8000
```

**What `uv sync` does:**

- Creates a `.venv` virtual environment in the `backend` directory
- Installs all dependencies from `pyproject.toml`
- No need to manually activate venv — `uv run` handles it automatically

**Starting the server:**

- The `uv run` command automatically uses the project's virtual environment
- App runs at `http://localhost:8000`
- Visit <a href="http://localhost:8000/docs" target="_blank">http://localhost:8000/docs</a> for interactive API docs
- `--reload` enables hot-reload during development (restart on file changes)

## API Endpoints

| Method   | Endpoint        | Description         |
| -------- | --------------- | ------------------- |
| `GET`    | `/health`       | Health check        |
| `GET`    | `/players`      | List all players    |
| `POST`   | `/players`      | Create a new player |
| `GET`    | `/players/{id}` | Get player by ID    |
| `PUT`    | `/players/{id}` | Update player by ID |
| `DELETE` | `/players/{id}` | Delete player by ID |

### Example Requests

**Create a player:**

```bash
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
```

**Response (201 Created):**

```json
{
  "id": 1,
  "full_name": "Lionel Messi",
  "country": "Argentina",
  "status": "active",
  "current_team": "Inter Miami",
  "league": "MLS",
  "market_value": 15000000,
  "age": 37
}
```

**Get player:**

```bash
curl http://localhost:8000/players/1
```

**Update player:**

```bash
curl -X PUT http://localhost:8000/players/1 \
  -H "Content-Type: application/json" \
  -d '{"age": 38}'
```

**Delete player:**

```bash
curl -X DELETE http://localhost:8000/players/1
```

## Error Handling

| Status | Error Code              | Meaning                                                                   |
| ------ | ----------------------- | ------------------------------------------------------------------------- |
| `422`  | `VALIDATION_ERROR`      | Invalid input (e.g., missing required field `age`, `full_name` < 2 chars) |
| `404`  | `PLAYER_NOT_FOUND`      | Player ID doesn't exist                                                   |
| `429`  | `RATE_LIMIT_EXCEEDED`   | Rate limit hit (100 requests/minute per IP)                               |
| `500`  | `INTERNAL_SERVER_ERROR` | Unexpected server error                                                   |

**Example error response:**

```json
{
  "error": {
    "code": "PLAYER_NOT_FOUND",
    "message": "Player with ID 999 not found",
    "player_id": 999
  }
}
```

## Running with Docker

```bash
# Build image (run from repo root, context is backend folder)
docker build -t football-service -f backend/football_player_service/Dockerfile backend

# Run container
docker run --rm -p 8000:8000 --name football-service football-service
```

Access the API at `http://localhost:8000/docs`

**Note:** If building from within the `backend` directory:

```bash
docker build -t football-service -f football_player_service/Dockerfile .
```

**Optional: Run with custom environment variables**

```bash
docker run --rm -p 8000:8000 \
  -e PLAYER_APP_NAME="Custom Name" \
  --name football-service football-service
```

**Docker Features:**

- ✅ Python 3.13-slim base (small image size)
- ✅ Non-root user (security)
- ✅ Health check endpoint (every 30s)
- ✅ Startup banner with feature list

## Testing

```bash
# From backend directory
# Install dev dependencies (includes pytest, pre-commit, etc.)
uv sync

# Run all tests (uv run automatically uses the project venv)
uv run pytest football_player_service/tests -v

# Run with coverage report
uv run pytest football_player_service/tests --cov=football_player_service --cov-report=term-missing
```

**Note:**

- `uv sync` without `--no-dev` installs both production + dev dependencies
- `uv run` automatically activates the `.venv` — no manual activation needed

**Test Coverage:** 21 tests covering:

- ✅ Happy path (create, read, update, delete)
- ✅ Validation (age bounds, string lengths, required fields)
- ✅ Error handling (404, 422, 429 responses)
- ✅ Security (rate limiting, headers)

## Project Structure

```
football-players-service/
├── backend/                          # Main backend service
│   ├── football_player_service/
│   │   ├── app/
│   │   │   ├── main.py               # FastAPI app, routes, middleware
│   │   │   ├── models.py             # Pydantic models (validation)
│   │   │   ├── repository.py         # Data layer (in-memory storage)
│   │   │   ├── config.py             # Settings & environment
│   │   │   └── dependencies.py       # Dependency injection
│   │   ├── tests/
│   │   │   ├── test_players.py       # API endpoint tests
│   │   │   └── conftest.py           # pytest fixtures
│   │   ├── Dockerfile                # Container image
│   │   └── contracts/
│   │       └── openapi.json          # OpenAPI schema
│   ├── pyproject.toml                # Dependencies & project config
│   ├── README.md                     # This file
│   └── .github/workflows/
│       └── ci.yml                    # GitHub Actions CI/CD
├── .git/                             # Git repository root
└── [other root config files]
```

## Configuration

Create `.env` in the `backend` directory:

```bash
# Optional: customize app name (default: "Football Player Service")
PLAYER_APP_NAME=Football Player Service
```

## Development

### Understanding `uv`

**What is `uv`?**
`uv` is a fast Python package installer and runner. It replaces `pip` + `venv` with a single tool:

| Command            | What it does                                                    |
| ------------------ | --------------------------------------------------------------- |
| `uv sync`          | Creates `.venv` and installs dependencies from `pyproject.toml` |
| `uv sync --no-dev` | Install only production dependencies (smaller, faster)          |
| `uv run <command>` | Automatically activates `.venv` and runs a command              |
| `uv pip install`   | Install packages (rarely needed; use `pyproject.toml` instead)  |

**Example workflow:**

```bash
# Step 1: One-time setup (create venv + install deps)
uv sync

# Step 2: Run commands (no need to activate venv manually)
uv run python script.py          # Run Python script
uv run pytest tests/             # Run tests
uv run ruff check .              # Run linter
```

**Key benefit:** `uv run` automatically uses the project's virtual environment — you never need to manually `source .venv/Scripts/activate` or `source venv/bin/activate`.

### Pre-commit Hooks

```bash
# From backend directory
# Install hooks (runs ruff format/check before each commit)
pre-commit install

# Run manually
pre-commit run --all-files
```

### Linting & Formatting

```bash
# From backend directory
# Format code
uv run ruff format .

# Check code quality
uv run ruff check .
```

### CI/CD

Automated checks on every push/PR (GitHub Actions):

- ✅ `ruff format --check` (code formatting)
- ✅ `ruff check` (linting)
- ✅ `pytest` (full test suite)

See `.github/workflows/ci.yml` for details.

## Validation Rules

| Field          | Type  | Constraints                          | Example               |
| -------------- | ----- | ------------------------------------ | --------------------- |
| `id`           | `int` | Auto-generated                       | `1`                   |
| `full_name`    | `str` | Required, 2-100 chars                | `"Cristiano Ronaldo"` |
| `country`      | `str` | Required, ≤50 chars                  | `"Portugal"`          |
| `status`       | `str` | Required, must be "active" or "inactive" | `"active"`        |
| `current_team` | `str` | Required, ≤100 chars                 | `"Manchester United"` |
| `league`       | `str` | Required, ≤50 chars                  | `"Premier League"`    |
| `age`          | `int` | Required, 0-120                      | `39`                  |
| `market_value` | `int` | Optional, ≤10B USD                   | `25000000` or `null`  |

## Troubleshooting

| Issue                                                      | Solution                                                                                                            |
| ---------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------- |
| **Port 8000 already in use**                               | `uv run python -m uvicorn ... --port 8001`                                                                          |
| **`Failed to canonicalize script path` on Windows**        | Use: `uv run python -m uvicorn ...` instead of `uv run uvicorn ...`                                                 |
| **ImportError: No module named 'football_player_service'** | Run `uv sync` to install package in editable mode                                                                   |
| **Tests fail with "PLAYER_APP_NAME not found"**            | Add `PLAYER_APP_NAME=Football Player Service` to `.env`                                                             |
| **Rate limit exceeded (429)**                              | Limit to 100 requests/minute per IP; wait or use different IP                                                       |
| **Docker build fails**                                     | Ensure Python 3.13+ available; check `Dockerfile`                                                                   |
| **`uv: command not found`**                                | Install uv: `pip install uv` or see [uv installation docs](https://docs.astral.sh/uv/getting-started/installation/) |

## Architecture & Design

This project demonstrates **clean architecture** with separation of concerns:

- **Models Layer** (`models.py`) — Pydantic validators, type safety
- **Repository Layer** (`repository.py`) — Data persistence abstraction (swappable with DB)
- **Handler Layer** (`main.py`) — FastAPI routes, middleware, security
- **Dependency Injection** — Loose coupling, testable components

**Security Features:**

- Rate limiting (100 req/min per IP)
- Security headers (X-Content-Type-Options, X-Frame-Options, HSTS)
- CORS middleware (configurable)
- Global exception handler (standardized error format)
- Non-root Docker user

**Why This Matters:**

- Easy to test (repository can be mocked)
- Easy to migrate to real database (swap repository)
- Easy to scale (middleware & deps configure globally)

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Commit changes: `git commit -am 'Add my feature'`
4. Push to branch: `git push origin feature/my-feature`
5. Open a Pull Request

**Before submitting (from backend directory):**

```bash
uv sync
pre-commit run --all-files
uv run pytest football_player_service/tests -v
```

## License

MIT License — see LICENSE file for details.

## Support

- 📖 **API Docs:** <a href="https://football-players-service.onrender.com/docs" target="_blank" rel="noopener noreferrer">Swagger UI</a>
- 🐛 **Report Issues:** <a href="https://github.com/EASS-HIT-PART-A-2025-CLASS-VIII/football-players-service/issues" target="_blank" rel="noopener noreferrer">GitHub Issues</a>
- 💬 **Discussions:** <a href="https://github.com/EASS-HIT-PART-A-2025-CLASS-VIII/football-players-service/discussions" target="_blank" rel="noopener noreferrer">GitHub Discussions</a>
