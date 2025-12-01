# ⚽ Football Player Service ⚽

Live demo & docs: <a href="https://football-players-service.onrender.com/docs" target="_blank" rel="noopener noreferrer">Football Player Service — interactive docs</a>

## Intro

Small FastAPI app providing a simple in-memory CRUD for football players (list, create, get, update, delete). Built with `FastAPI`, `Pydantic` for validation, `uvicorn` as the server, and light `pytest` tests using `httpx`/TestClient. The code separates models, repository and app logic so persistence can be swapped easily.

## How to run it yourself

- **Docs (hosted):** <a href="https://football-players-service.onrender.com/docs" target="_blank" rel="noopener noreferrer">Interactive API docs (Render) ⚽</a>

**1) Run locally (after clone)**

```bash
# Clone
git clone https://github.com/EASS-HIT-PART-A-2025-CLASS-VIII/football-players-service.git
cd football-players-service

# Install dependencies (preferred: use uv + pyproject.toml)
uv sync --no-dev

# Run the app
uv run uvicorn football_player_service.app.main:app --reload --port 8000
```

**2) OR Run with Docker (after clone)**

```bash
docker build -t football-service -f football_player_service/Dockerfile .
docker run --rm -p 8000:8000 --name football-service football-service
```

**3) Run tests**

Preferred command used in CI/local checks:

```bash
uv run pytest football_player_service/tests -v
```

Notes:

- Tests rely on an in-memory repository and `conftest.py` clears repository state between tests.
- The app reads `PLAYER_APP_NAME` from `.env` (tests expect `PLAYER_APP_NAME="Football Player Service"`).
  Notes:
- Tests rely on an in-memory repository and `conftest.py` clears repository state between tests.
- The app reads `PLAYER_APP_NAME` from `.env` (tests expect `PLAYER_APP_NAME="Football Player Service"`).
- Dependencies: this project uses `pyproject.toml` as the dependency manifest and the examples/CI use the `uv` tool to install them. `requirements.txt` may be empty — prefer `uv sync --no-dev` (or `pip install -r requirements.txt` if you populate it).
