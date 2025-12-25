# ⚽ Football Player Management System

**Live:** <a href="https://football-players-service-1.onrender.com" target="_blank">https://football-players-service-1.onrender.com</a>

A modern full-stack web application for managing football player data with **FastAPI** backend and **React 19** frontend.

---

## 🚀 Quick Start

### Prerequisites

- **Backend:** Python 3.13+ with `uv` package manager
- **Frontend:** Node.js 18+ with npm
- **Docker:** (Optional) Docker & Docker Compose for containerized deployment

### Option 1: Local Development (Recommended)

Run both services in parallel terminals:

**Terminal 1 - Backend:**

```bash
cd backend
uv sync --no-dev
uv run python -m uvicorn football_player_service.app.main:app --reload --port 8000
```

**Terminal 2 - Frontend:**

```bash
cd frontend
npm install
npm run dev
```

- **API Docs:** http://localhost:8000/docs
- **App:** http://localhost:5173
- **Database:** SQLite (persistent in `backend/football_players.db`)

### Option 2: Docker Compose (One Command)

**Recommended for running both services together with persistent database.**

```bash
docker-compose up
```

- **API Docs:** http://localhost:8000/docs
- **App:** http://localhost:3000
- **Database:** SQLite (persists in `backend-data` volume)

**Stop:**

```bash
docker-compose down
```

See [Docker & Deployment](#-docker--deployment) section for advanced usage.

---

## 📁 Project Structure

```
.
├── README.md                    # Main project overview (this file)
├── docker-compose.yml           # Local development with both services
├── backend/
│   ├── README.md                # Backend-specific setup & API docs
│   ├── pyproject.toml           # Python dependencies (uv)
│   ├── requirements.txt          # For Docker deployment
│   └── football_player_service/
│       ├── app/                 # FastAPI application
│       │   ├── main.py          # FastAPI setup, routes, middleware
│       │   ├── models.py        # SQLModel definitions
│       │   ├── database.py      # SQLAlchemy setup (SQLite/PostgreSQL)
│       │   ├── repository.py    # CRUD operations
│       │   └── dependencies.py  # DI setup
│       ├── contracts/           # OpenAPI schema
│       ├── scripts/             # Utilities (e.g., export OpenAPI)
│       ├── tests/               # pytest tests (21 total)
│       └── Dockerfile           # Container image
└── frontend/
    ├── README.md                # Frontend-specific setup & architecture
    ├── package.json             # npm dependencies
    ├── vite.config.ts           # Vite build config
    ├── .env                     # Local dev API URL
    ├── .env.production          # Production API URL
    ├── src/
    │   ├── main.tsx             # React entry point
    │   ├── services/api.ts      # Axios HTTP client
    │   ├── hooks/               # Custom hooks (usePlayers, usePlayersView)
    │   ├── components/          # React components
    │   ├── pages/               # Page components
    │   └── types/               # TypeScript types
    ├── Dockerfile               # Container image
    └── public/                  # Static files
```

### 📖 Documentation Structure

**Best Practice:** Multi-level READMEs for clarity

- **[README.md](README.md)** (Root) — Project overview, quick start, architecture overview
- **[backend/README.md](backend/README.md)** — Backend-specific: setup, API docs, testing, deployment
- **[frontend/README.md](frontend/README.md)** — Frontend-specific: components, hooks, styling, env vars

---

## 🔌 Communication Layer

**Frontend → Backend HTTP Communication:**

```
Frontend (.env)
  VITE_API_LOCATION = http://127.0.0.1:8000
    ↓
Axios Instance (src/services/api.ts)
  baseURL = http://127.0.0.1:8000
    ↓
Custom Hook (src/hooks/usePlayers.ts)
  ├ useQuery() — GET /players, GET /players/{id}
  └ useMutation() — POST /players, PUT /players/{id}, DELETE /players/{id}
    ↓
FastAPI Backend
  GET/POST/PUT/DELETE /players
    ↓
SQLite Database (backend/football_players.db)
```

---

## 📊 Tech Stack

### 🎨 Frontend

- **React 19** + TypeScript
- **Vite** — Build tool
- **TanStack Query** — Server state & caching
- **React Router** — Navigation
- **Zod** — Form validation
- **Axios** — HTTP client

### 🔧 Backend

- **FastAPI** (Python 3.13+)
- **SQLModel** — ORM
- **SQLite** (local) / PostgreSQL (production)
- **Pydantic v2** — Validation
- **pytest** — 21 tests
- **Rate Limiting** — slowapi (100 req/min per IP)

---

## 🎯 Features

- ✅ Full CRUD operations (Create, Read, Update, Delete players)
- ✅ Real-time data synchronization (TanStack Query)
- ✅ Modal forms with validation
- ✅ Delete confirmation dialogs
- ✅ Loading & error states
- ✅ Type-safe frontend & backend
- ✅ Rate limiting & security headers
- ✅ Comprehensive test coverage (21 tests)
- ✅ Docker containerization
- ✅ OpenAPI/Swagger documentation

---

## 📖 Full Documentation

- **[Backend Setup & API](backend/README.md)** — Database, endpoints, testing, deployment
- **[Frontend Setup & Architecture](frontend/README.md)** — Build, components, hooks, styling

---

## 📚 Development Workflow

### Running Tests

```bash
cd backend
uv run pytest football_player_service/tests -v
```

### Building for Production

```bash
cd frontend
npm run build    # Creates dist/ folder
```

### API Documentation

Open http://localhost:8000/docs while backend is running

---

## 🐳 Docker & Deployment

### Local Development with Docker Compose

**One command to start everything:**

```bash
docker-compose up
```

**What happens:**

1. **Backend** builds from [backend/football_player_service/Dockerfile](backend/football_player_service/Dockerfile)

   - Runs on `http://localhost:8000`
   - Uses SQLite database in `backend-data` volume (persisted between restarts)
   - Automatically initializes database on startup
   - Health check: `http://localhost:8000/health`

2. **Frontend** builds from [frontend/Dockerfile](frontend/Dockerfile)
   - Runs on `http://localhost:3000`
   - Configured to reach backend via `http://backend:8000` (Docker network)
   - Waits for backend to be healthy before starting
   - Health check: HTTP status on port 3000

**Logs & Management:**

```bash
# View logs from all services
docker-compose logs -f

# View backend logs only
docker-compose logs -f backend

# Stop services (keeps data)
docker-compose down

# Remove everything (clears data)
docker-compose down -v
```

### Database Persistence

The SQLite database is stored in a Docker volume (`backend-data`) so data persists between restarts:

```bash
# Check volumes
docker volume ls

# Inspect the volume
docker volume inspect ex1_backend-data
```

To reset the database:

```bash
docker-compose down -v   # Remove volume
docker-compose up         # New empty database
```

### Build Images Manually

```bash
# Backend
docker build -t football-service -f backend/football_player_service/Dockerfile backend

# Frontend
docker build -t football-frontend frontend
```

### Run Individual Containers

```bash
# Backend only (port 8000)
docker run --rm -p 8000:8000 football-service

# Frontend only (port 3000)
docker run --rm -p 3000:3000 football-frontend
```

### Customizing Docker Compose

Edit [docker-compose.yml](docker-compose.yml) to:

**Change ports:**

```yaml
ports:
  - "9000:8000" # Backend on 9000 instead of 8000
```

**Use PostgreSQL instead of SQLite (production-like):**

```yaml
backend:
  environment:
    - DATABASE_URL=postgresql://user:pass@db:5432/football
```

**Add database service:**

```yaml
services:
  db:
    image: postgres:16
    environment:
      POSTGRES_PASSWORD: password
      POSTGRES_DB: football
    volumes:
      - postgres-data:/var/lib/postgresql/data

volumes:
  postgres-data:
```

See [backend/README.md](backend/README.md) for database configuration details.

---

## 📄 License

MIT
