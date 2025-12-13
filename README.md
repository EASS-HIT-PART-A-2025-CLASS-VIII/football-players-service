# ⚽ Football Player Management System

> A modern full-stack web application for managing football player data. Built with **FastAPI** (backend) and **React + TypeScript** (frontend) with production-ready features including testing, validation, and containerization.

**Features:**
- ⚡ **Fast & Modern** — React 19, TypeScript, Vite, TanStack Query (React Query)
- 🔒 **Secure Backend** — Rate limiting, security headers, CORS support
- 🏗️ **Clean Architecture** — Separation of concerns across frontend and backend
- ✅ **Fully Tested** — 21 comprehensive pytest tests with edge case coverage
- 🐳 **Containerized** — Docker support for both services
- 📚 **Auto-Documented** — OpenAPI/Swagger docs auto-generated from code
- 🎯 **Responsive UI** — Modern frontend with React Router, Form validation (Zod), and FontAwesome icons

---

## 📋 Quick Start

### Prerequisites

- **Python:** 3.13+ (or 3.12+)
- **Node.js:** 18+ with npm
- **Package Manager:** `uv` (recommended, for Python) or `pip`
- **Optional:** Docker for containerized deployment

### Installation & Run

#### Backend Setup

```bash
# Navigate to backend directory
cd backend

# Install dependencies (creates .venv and installs packages)
uv sync --no-dev

# Start development server
# On Windows/MINGW64:
uv run python -m uvicorn football_player_service.app.main:app --reload --port 8000

# On macOS/Linux:
# uv run uvicorn football_player_service.app.main:app --reload --port 8000
```

**Backend runs at:** `http://localhost:8000`  
**API Docs:** `http://localhost:8000/docs` (Swagger UI)  
**Health Check:** `http://localhost:8000/health`

#### Frontend Setup

```bash
# Navigate to frontend directory (from project root)
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

**Frontend runs at:** `http://localhost:5173` (or next available port)

---

## 🎨 Frontend

### Tech Stack
- **Framework:** React 19
- **Language:** TypeScript
- **Bundler:** Vite
- **Routing:** React Router v7
- **Data Fetching:** TanStack Query (React Query) v5
- **Form Validation:** Zod
- **Icons:** FontAwesome
- **DevTools:** React Query DevTools (dev only)

### Project Structure

```
frontend/
├── src/
│   ├── components/          # Reusable UI components
│   │   ├── Navbar.tsx
│   │   └── Navbar.css
│   ├── layouts/             # Layout components
│   │   ├── RootLayout.tsx
│   │   └── RootLayout.css
│   ├── pages/               # Page components
│   │   ├── HomePage.tsx
│   │   ├── PlayersPage.tsx
│   │   └── *.css
│   ├── routes/              # Route definitions
│   │   └── routes.tsx
│   ├── services/            # API service calls
│   ├── types/               # TypeScript type definitions
│   ├── utils/               # Utility functions
│   ├── main.tsx             # Entry point
│   └── index.css
├── public/                  # Static assets
├── package.json
├── vite.config.ts           # Vite configuration
├── tsconfig.json            # TypeScript configuration
└── README.md
```

### Available Scripts

```bash
# Development server (watches for changes)
npm run dev

# Type-check and build for production
npm run build

# Preview production build locally
npm run preview

# Run ESLint linter
npm run lint
```

### Features

- **Players Page** — View, create, update, and delete football players
- **Responsive Design** — Mobile-friendly UI with modern CSS
- **Data Fetching** — TanStack Query with caching, refetching, and DevTools
- **Type Safety** — Full TypeScript support with Zod validation
- **Navigation** — React Router for seamless page transitions

---

## 🔧 Backend

### Tech Stack
- **Framework:** FastAPI
- **Language:** Python 3.13+
- **Validation:** Pydantic v2
- **Testing:** pytest with comprehensive coverage
- **Deployment:** Docker, Uvicorn

### Project Structure

```
backend/
├── football_player_service/
│   ├── app/
│   │   ├── main.py              # FastAPI app, routes, middleware
│   │   ├── models.py            # Pydantic models (validation)
│   │   ├── repository.py        # Data layer (in-memory storage)
│   │   ├── config.py            # Settings & environment
│   │   ├── dependencies.py      # Dependency injection
│   │   └── __init__.py
│   ├── tests/
│   │   ├── test_players.py      # API endpoint tests
│   │   ├── conftest.py          # pytest fixtures
│   │   └── __init__.py
│   ├── contracts/
│   │   └── openapi.json         # OpenAPI schema
│   ├── scripts/
│   │   └── export_openapi.py    # Export OpenAPI docs
│   ├── Dockerfile               # Container image
│   └── __init__.py
├── pyproject.toml               # Dependencies & project config
├── requirements.txt             # Frozen dependencies
└── README.md
```

### API Endpoints

| Method   | Endpoint        | Description         |
| -------- | --------------- | ------------------- |
| `GET`    | `/health`       | Health check        |
| `GET`    | `/players`      | List all players    |
| `POST`   | `/players`      | Create a new player |
| `GET`    | `/players/{id}` | Get player by ID    |
| `PUT`    | `/players/{id}` | Update player by ID |
| `DELETE` | `/players/{id}` | Delete player by ID |

### Example Request

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

### Validation Rules

| Field          | Type  | Constraints                          |
| -------------- | ----- | ------------------------------------ |
| `id`           | `int` | Auto-generated                       |
| `full_name`    | `str` | Required, 2-100 chars                |
| `country`      | `str` | Required, ≤50 chars                  |
| `status`       | `str` | Required, "active" or "inactive"     |
| `current_team` | `str` | Required, ≤100 chars                 |
| `league`       | `str` | Required, ≤50 chars                  |
| `age`          | `int` | Required, 0-120                      |
| `market_value` | `int` | Optional, ≤10B USD                   |

### Error Handling

| Status | Error Code              | Meaning                    |
| ------ | ----------------------- | -------------------------- |
| `422`  | `VALIDATION_ERROR`      | Invalid input              |
| `404`  | `PLAYER_NOT_FOUND`      | Player ID doesn't exist    |
| `429`  | `RATE_LIMIT_EXCEEDED`   | Rate limit hit             |
| `500`  | `INTERNAL_SERVER_ERROR` | Unexpected server error    |

### Testing

```bash
# From backend directory
# Install dev dependencies (includes pytest, pre-commit, etc.)
uv sync

# Run all tests
uv run pytest football_player_service/tests -v

# Run with coverage report
uv run pytest football_player_service/tests --cov=football_player_service --cov-report=term-missing
```

**Test Coverage:** 21 tests covering:
- ✅ Happy path (create, read, update, delete)
- ✅ Validation (age bounds, string lengths, required fields)
- ✅ Error handling (404, 422, 429 responses)
- ✅ Security (rate limiting, headers)

---

## 🐳 Docker Deployment

### Backend

```bash
# Build image (run from repo root)
docker build -t football-service -f backend/football_player_service/Dockerfile backend

# Run container
docker run --rm -p 8000:8000 --name football-service football-service
```

Access API at `http://localhost:8000/docs`

---

## 🧪 Running Tests

```bash
# From backend directory
# Full test suite with verbose output
uv run pytest football_player_service/tests -v

# With coverage
uv run pytest football_player_service/tests --cov=football_player_service --cov-report=term-missing
```

---

## 📖 Development Workflow

### Backend Development

```bash
cd backend

# First time setup
uv sync

# Start dev server (with hot reload)
uv run python -m uvicorn football_player_service.app.main:app --reload --port 8000

# Format code
uv run ruff format .

# Lint
uv run ruff check .

# Run tests
uv run pytest football_player_service/tests -v
```

### Frontend Development

```bash
cd frontend

# First time setup
npm install

# Start dev server (with hot reload)
npm run dev

# Build for production
npm run build

# Lint
npm run lint
```

### Running Both Services Simultaneously

**Terminal 1 (Backend):**
```bash
cd backend
uv run python -m uvicorn football_player_service.app.main:app --reload --port 8000
```

**Terminal 2 (Frontend):**
```bash
cd frontend
npm run dev
```

Then open:
- Frontend: `http://localhost:5173`
- Backend API: `http://localhost:8000/docs`

---

## 🛠 Configuration

### Backend

Create `.env` in the `backend` directory:

```bash
# Optional: customize app name
PLAYER_APP_NAME=Football Player Service
```

### Frontend

Frontend configuration is in `vite.config.ts`. By default, it proxies API requests to `http://localhost:8000`.

---

## 📦 What `uv` Does

**`uv`** is a fast Python package installer and runner:

| Command            | What it does                                    |
| ------------------ | ----------------------------------------------- |
| `uv sync`          | Creates `.venv` and installs dependencies       |
| `uv sync --no-dev` | Install only production dependencies             |
| `uv run <command>` | Automatically activates `.venv` and runs command|

**Key benefit:** No manual venv activation needed!

---

## 🚀 Deployment Checklist

- [ ] Backend: `uv sync && uv run pytest` (all tests pass)
- [ ] Frontend: `npm install && npm run build` (no build errors)
- [ ] Backend: Docker image builds successfully
- [ ] Environment variables set correctly
- [ ] Frontend points to correct API endpoint

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Make your changes
4. Test thoroughly (backend: `pytest`, frontend: `npm run lint`)
5. Commit: `git commit -am 'Add my feature'`
6. Push: `git push origin feature/my-feature`
7. Open a Pull Request

---

## 📞 Support & Documentation

- **Backend API Docs:** `http://localhost:8000/docs` (when running locally)
- **Backend README:** [backend/README.md](backend/README.md)
- **Frontend README:** [frontend/README.md](frontend/README.md)

---

## 📄 License

MIT License — see LICENSE file for details.