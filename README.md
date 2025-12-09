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
cd football-players-service

# Install dependencies
uv sync --no-dev

# Start development server
uv run uvicorn football_player_service.app.main:app --reload --port 8000
```

Server runs at `http://localhost:8000` — visit <a href="http://localhost:8000/docs" target="_blank">http://localhost:8000/docs</a> for interactive docs.

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
    "age": 37,
    "market_value": 15000000
  }'
```

**Response (201 Created):**

```json
{
  "id": 1,
  "full_name": "Lionel Messi",
  "country": "Argentina",
  "age": 37,
  "market_value": 15000000
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
# Build image
docker build -t football-service -f football_player_service/Dockerfile .

# Run container
docker run --rm -p 8000:8000 --name football-service football-service
```

Access the API at `http://localhost:8000/docs`

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
# Install dev dependencies
uv sync

# Run all tests
uv run pytest football_player_service/tests -v

# Run with coverage
uv run pytest football_player_service/tests --cov=football_player_service --cov-report=term-missing
```

**Test Coverage:** 21 tests covering:

- ✅ Happy path (create, read, update, delete)
- ✅ Validation (age bounds, string lengths, required fields)
- ✅ Error handling (404, 422, 429 responses)
- ✅ Security (rate limiting, headers)

## Project Structure

```
football-players-service/
├── football_player_service/
│   ├── app/
│   │   ├── main.py           # FastAPI app, routes, middleware
│   │   ├── models.py         # Pydantic models (validation)
│   │   ├── repository.py     # Data layer (in-memory storage)
│   │   ├── config.py         # Settings & environment
│   │   └── dependencies.py   # Dependency injection
│   ├── tests/
│   │   ├── test_players.py   # API endpoint tests
│   │   └── conftest.py       # pytest fixtures
│   ├── Dockerfile            # Container image
│   └── contracts/
│       └── openapi.json      # OpenAPI schema
├── pyproject.toml            # Dependencies & project config
├── README.md                 # This file
└── .github/workflows/
    └── ci.yml                # GitHub Actions CI/CD
```

## Configuration

Create `.env` in project root:

```bash
# Optional: customize app name (default: "Football Player Service")
PLAYER_APP_NAME=Football Player Service
```

## Development

### Pre-commit Hooks

```bash
# Install hooks (runs ruff format/check before each commit)
pre-commit install

# Run manually
pre-commit run --all-files
```

### Linting & Formatting

```bash
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

| Field          | Type  | Constraints           | Example               |
| -------------- | ----- | --------------------- | --------------------- |
| `id`           | `int` | Auto-generated        | `1`                   |
| `full_name`    | `str` | Required, 2-100 chars | `"Cristiano Ronaldo"` |
| `country`      | `str` | Required, ≤50 chars   | `"Portugal"`          |
| `age`          | `int` | Required, 0-120       | `39`                  |
| `market_value` | `int` | Optional, ≤10B USD    | `25000000` or `null`  |

## Troubleshooting

| Issue                                                      | Solution                                                      |
| ---------------------------------------------------------- | ------------------------------------------------------------- |
| **Port 8000 already in use**                               | `uv run uvicorn ... --port 8001`                              |
| **ImportError: No module named 'football_player_service'** | Run `uv sync` to install package in editable mode             |
| **Tests fail with "PLAYER_APP_NAME not found"**            | Add `PLAYER_APP_NAME=Football Player Service` to `.env`       |
| **Rate limit exceeded (429)**                              | Limit to 100 requests/minute per IP; wait or use different IP |
| **Docker build fails**                                     | Ensure Python 3.13+ available; check `Dockerfile`             |

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

**Before submitting:**

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
