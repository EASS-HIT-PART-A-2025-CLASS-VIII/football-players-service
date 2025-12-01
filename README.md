**Football Player Service**

Cloning and getting started

```bash
# Clone this repository
git clone https://github.com/EASS-HIT-PART-A-2025-CLASS-VIII/football-players-service.git
cd football-players-service
```

Prerequisites

If you want to follow the repository's exact workflow (matches the Dockerfile), install the `uv` package manager and Python 3.12 using the commands below. These steps are optional if you prefer to use a virtual environment + `pip` (see the alternate instructions later).

```bash
# Install uv package manager
curl -LsSf https://astral.sh/uv/install.sh | sh

# Restart your shell to load uv into PATH
exec "$SHELL" -l

# Verify uv installed correctly
uv --version

# (optional) Install Python 3.12 via uv-managed runtimes
uv python install 3.12
```

Once `uv` and Python are available, install project dependencies deterministically from `pyproject.toml`:

```bash
# If you have an existing lockfile and want exact versions:
uv sync --frozen --no-dev

# If you don't have a lockfile or want uv to resolve versions:
uv sync --no-dev
```

**Description**: FastAPI backend that manages an in-memory collection of football players (list/create/get/update/delete). The codebase is organized to separate models, repository, and application logic so persistence can be swapped without changing the HTTP contract.

**Quick Start (using `uv`)**

This repository uses the `uv` tool in examples and the Dockerfile. If you use `uv`, you can run the app and tests via `uv run` so the same environment is used locally and in CI.

- Install dependencies (example — already performed in this workspace):

  ```bash
  uv add fastapi uvicorn pydantic pydantic-settings httpx
  ```

- Start the app (the command you used):

  ```bash
  uv run uvicorn football_player_service.app.main:app --reload --port 8000
  ```

- Run tests:
  ```bash
  uv run pytest -q
  ```

**Local Setup (virtualenv + pip alternative)**

Use this if you don't use `uv`:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn football_player_service.app.main:app --reload --port 8000
```

**Docker — build & run**

Build (from repository root):

```bash
docker build -t football-service -f football_player_service/Dockerfile .
```

Run:

```bash
docker run --rm -p 8000:8000 --name football-service football-service
```

Health check:

```bash
curl http://127.0.0.1:8000/health
```

**Tests & API contract**

- Tests are in `football_player_service/tests`. `conftest.py` provides an autouse fixture that clears the in-memory repository between tests and a `client` fixture (TestClient) for making HTTP requests.
- Run tests (preferred — exact command used for CI and local checks):
  ```bash
  uv run pytest football_player_service/tests -v
  ```
- Export the OpenAPI schema (used for client generation and contract testing):
  ```bash
  python -m football_player_service.scripts.export_openapi
  # Writes: football_player_service/contracts/openapi.json
  ```

**Project layout (key files)**

- `football_player_service/app/main.py` — FastAPI application and routes
- `football_player_service/app/models.py` — Pydantic models and validators
- `football_player_service/app/repository.py` — In-memory `PlayerRepository` (has `clear()` for tests)
- `football_player_service/app/dependencies.py` — dependency providers for settings and repository
- `football_player_service/tests/` — pytest test suite + `conftest.py`
- `football_player_service/scripts/export_openapi.py` — exports OpenAPI JSON
- `football_player_service/Dockerfile` — image definition used in examples

**Notes & recommendations**

- The app reads `PLAYER_APP_NAME` from `.env` via `pydantic-settings`. Tests expect `PLAYER_APP_NAME="Football Player Service"`.
- The Dockerfile uses `uv` to install exact dependency versions from `uv.lock`. If `uv.lock` is not present, install dependencies locally or switch to `pip`-based Docker steps.
- For production, inject environment variables at runtime rather than embedding `.env` in images.

If you'd like, I can:

- Run the test suite and paste the output.
- Add a `Makefile` or `tasks.json` with common commands (`run`, `test`, `docker-build`).
- Generate the OpenAPI JSON now and show the top of the file.

---

This README is intended to be the project's front page: clear, actionable, and matching the exact commands you used.
