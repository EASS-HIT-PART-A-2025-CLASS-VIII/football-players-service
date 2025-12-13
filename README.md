# ⚽ Football Player Management System

A modern full-stack web application for managing football player data with **FastAPI** backend and **React 19** frontend.

## 🚀 Quick Start

### Backend

```bash
cd backend
uv sync --no-dev
uv run python -m uvicorn football_player_service.app.main:app --reload --port 8000
```

**API:** `http://localhost:8000/docs` (Swagger UI)

### Frontend

```bash
cd frontend
npm install
npm run dev
```

**App:** `http://localhost:5173`

---

## 🎨 Frontend Stack

- **React 19** + TypeScript
- **TanStack Query** — Data fetching & caching
- **React Router** — Navigation
- **Zod** — Form validation
- **Vite** — Build tool
- **Custom Hooks** — `usePlayers` (data), `usePlayersView` (state)

**Key Features:**

- CRUD operations with modal forms
- Delete confirmation dialog
- Loading & error states
- Component-based CSS
- Type-safe with Zod schemas

---

## 🔧 Backend Stack

- **FastAPI** (Python 3.13+)
- **Pydantic v2** — Validation
- **pytest** — 21 tests
- **Docker** — Containerization

**Endpoints:**

```
GET    /health              # Health check
GET    /players             # List all
POST   /players             # Create
GET    /players/{id}        # Get one
PUT    /players/{id}        # Update
DELETE /players/{id}        # Delete
```

---

## 📚 Development

### Both services together:

```bash
# Terminal 1 - Backend
cd backend && uv run python -m uvicorn football_player_service.app.main:app --reload --port 8000

# Terminal 2 - Frontend
cd frontend && npm run dev
```

### Testing

```bash
cd backend
uv run pytest football_player_service/tests -v
```

### Build for production

```bash
cd frontend
npm run build
```

---

## 📖 Architecture

**Data Flow:**

```
PlayersPage
  ↓ usePlayersView (view state, handlers)
    ↓ usePlayers (TanStack Query: queries + mutations)
      ↓ FastAPI Backend (CRUD operations)
        ↓ In-memory storage
```

**State Management:**

- **TanStack Query** — Server state (caching, auto-refetch)
- **usePlayersView** — UI state (modal, editing)
- **useState** — Local component state (forms, confirmations)

---

## 🐳 Docker

```bash
# Build & run backend
docker build -t football-service -f backend/football_player_service/Dockerfile backend
docker run --rm -p 8000:8000 football-service
```

---

## 📄 License

MIT
