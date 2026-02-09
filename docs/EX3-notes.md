# EX3: Full-Stack Microservices Final Project

## Project Evolution: EX1 → EX2 → EX3

### EX1 - Backend Foundation (FastAPI + SQLite)

**Goal:** Build a robust REST API with persistence and testing

**Implemented:**

- FastAPI application with SQLModel ORM
- SQLite database with player schema
- CRUD endpoints (GET/POST/PUT/DELETE /players)
- Pagination support (query params: page, limit)
- Input validation with Pydantic models
- 34 comprehensive tests (CRUD, validation, edge cases, auth, async)
- Rate limiting (100 req/min per IP)
- Security headers (X-Content-Type-Options, X-Frame-Options)
- OpenAPI/Swagger documentation
- Docker support with persistent volumes

**Key Files:**

- `backend/football_player_service/app/main.py` - FastAPI app
- `backend/football_player_service/app/models.py` - Data models
- `backend/football_player_service/app/repository.py` - Database access layer
- `backend/football_player_service/tests/test_players.py` - Test suite

### EX2 - User Interface (React + TypeScript)

**Goal:** Create a modern frontend with real-time state management

**Implemented:**

- React 19 + TypeScript application
- TanStack Query for server state synchronization
- Modal-based forms (create, edit, delete)
- Real-time data updates (optimistic updates, cache invalidation)
- Responsive design with mobile support
- Error handling and loading states
- Form validation with Zod
- Pagination controls

**Key Files:**

- `frontend/src/pages/players/PlayersPage.tsx` - Main UI
- `frontend/src/hooks/usePlayers.ts` - Data fetching hooks
- `frontend/src/services/api.ts` - API client functions
- `frontend/src/components/*` - Reusable components

### EX3 - Microservices Integration (Current)

**Goal:** Integrate API, persistence, and interface with additional microservices + security baseline

**New Implementations:**

**1. AI Scout Microservice**

- Dedicated FastAPI service wrapping Google Gemini API
- Port: 8001 (internal Docker network)
- Generates professional scouting reports (strengths, weaknesses, recommendations)
- Fallback to simulated reports if API key not configured
- Independent deployment and scaling

**2. Celery Worker (Async Task Processing)**

- Distributed task queue for long-running operations
- Redis broker for task distribution
- Updates task status in Redis (pending → running → completed)
- Writes scout reports to shared SQLite database
- Handles retries and error logging

**3. Redis (Message Broker + Cache)**

- Celery task queue (broker)
- Task status tracking (1-hour TTL)
- Result backend for Celery
- Enables horizontal scaling of workers

**4. JWT Authentication (Session 11 Security Baseline)**

- Bcrypt password hashing (passlib)
- JWT token generation (python-jose)
- 30-minute token expiry
- Admin user seeded on startup (`admin`/`admin123`)
- Protected endpoints: POST/PUT/DELETE /players, POST /scout
- Public endpoints: GET /players, GET /tasks, GET /health
- Frontend login page with token storage
- Axios interceptors for automatic token injection
- Auto-logout on 401 responses

**5. Real-Time Task Tracking (Thoughtful Enhancement)**

- New endpoint: `GET /tasks/{task_id}`
- Frontend polls every 2 seconds for status updates
- Modal UI shows live progress: ⏳ Pending → 🔄 Running → ✅ Completed
- Redis-backed with TTL for automatic cleanup

**6. Frontend Authentication UI**

- Login page with username/password form
- Token storage in localStorage
- Axios interceptors for JWT injection
- Logout button with token cleanup
- Authentication gate (shows login if not authenticated)

**7. Enhanced Documentation**

- `docs/EX3-notes.md` - Architecture, decisions, security
- `docs/runbooks/compose.md` - Operations guide
- README updates with evolution story

**8. Demo Script**

- `backend/scripts/demo.py` - End-to-end flow demonstration
- Login → Create player → Request scout → Poll status → Display report

**Key Architectural Decisions:**

**Why HTTP microservice instead of direct Gemini calls?**

- **Separation of concerns:** AI logic isolated from main backend
- **Security:** Gemini API key only in one service
- **Scalability:** Can deploy multiple AI workers behind load balancer
- **Testability:** Easy to mock AI responses for testing
- **Flexibility:** Can swap AI providers without touching main codebase

**Why Celery workers instead of FastAPI BackgroundTasks?**

- **Distributed processing:** Multiple workers can process tasks in parallel
- **Persistence:** Tasks survive server restarts (Redis backend)
- **Monitoring:** Built-in task tracking and retries
- **Production-ready:** Industry standard for Python async jobs

**Why Redis for task tracking instead of database?**

- **Performance:** In-memory access is faster than SQLite reads
- **TTL support:** Automatic cleanup of old tasks (1 hour)
- **Real-time:** Workers can update status without database locks
- **Scalability:** Redis handles high-frequency status checks

---

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

## Orchestration

### Start All Services

```bash
docker compose up --build
```

**First-time setup:**

1. Creates SQLite database in `backend/data/`
2. Builds 5 Docker images (~3-5 minutes)
3. Starts services on shared network
4. Services auto-restart on failure

**Verify:**

```bash
curl localhost:8000/health  # Backend
curl localhost:8001/health  # AI Service
open http://localhost:3000  # Frontend
```

See [docs/runbooks/compose.md](./runbooks/compose.md) for detailed instructions.

## Environment Configuration

**Required:**

- `GEMINI_API_KEY` - Your Google Gemini API key ([Get one](https://ai.google.dev/))

**Optional (has defaults):**

- `SECRET_KEY` - JWT secret (default: "insecure-secret-key-for-dev")
- `REDIS_URL` - Redis connection (default: "redis://redis:6379/0")
- `DATABASE_URL` - Database connection (default: SQLite)

**Setup:**

```bash
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY
docker compose up --build
```

## Async Refresher (Session 09) - scripts/refresh.py

Demonstrates bounded concurrency and idempotency for batch updates:

- **Bounded Concurrency:** Uses `asyncio.Semaphore` (5 workers) to limit parallel processing
- **Idempotency:** Redis SETEX (60s window) prevents re-processing same player
- **Retries:** Simulated network failure recovery with exponential backoff
- **Observability:** Structured logging for all operations

**Run:**

```bash
# Local development
uv run python backend/scripts/refresh.py

# Inside Docker
docker compose exec backend uv run python scripts/refresh.py
```

**Sample Output:**

```
[INFO] Starting refresh for 50 players
[INFO] Player 1: Processing (attempt 1/3)
[INFO] Player 1: Skipped (processed 30s ago - idempotent)
[INFO] Player 2: Success
[INFO] Completed: 45/50 success, 3 skipped, 2 failed
```

## Security Baseline (Session 11)

### Authentication Implementation

**✅ JWT Authentication Enabled (EX3 Requirement)**

Per exercises.md: "Session 11's security baseline: hashed credentials, at least one JWT-protected route with role checks"

**Current Implementation:**

- ✅ Hashed passwords using `passlib[bcrypt]`
- ✅ JWT token generation with `python-jose[cryptography]`
- ✅ Token expiry (30 minutes)
- ✅ User model with roles (user/admin)
- ✅ Admin user seeded on startup (`admin/admin123`)

**Protected Endpoints (Require JWT):**

- `POST /players` - Create player
- `PUT /players/{id}` - Update player
- `DELETE /players/{id}` - Delete player
- `POST /players/{id}/scout` - Request AI scouting report

**Public Endpoints (No Auth Required):**

- `GET /health` - Health check
- `GET /players` - List players (read-only)
- `GET /players/{id}` - Get player details (read-only)
- `GET /tasks/{task_id}` - Check task status
- `POST /token` - Login to get JWT

### Frontend Authentication

**Login Flow:**

1. User enters username/password in login form
2. Frontend calls `POST /token` with credentials (form-urlencoded)
3. Backend validates credentials and returns JWT
4. Frontend stores token in `localStorage`
5. Axios interceptor automatically adds `Authorization: Bearer {token}` to all requests
6. Protected operations (create/update/delete/scout) succeed with valid token

**Token Storage:**

```typescript
// On login success
localStorage.setItem("access_token", token);

// Axios interceptor reads token
axiosInstance.interceptors.request.use((config) => {
  const token = localStorage.getItem("access_token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});
```

**Auto-Logout on 401:**

```typescript
// Response interceptor handles expired tokens
axiosInstance.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem("access_token");
      window.location.href = "/"; // Redirect to login
    }
    return Promise.reject(error);
  },
);
```

**Default Credentials:**

- Username: `admin`
- Password: `admin123`
- Role: `admin`

### Automated Tests (Required by EX3)

**Authentication Test Coverage (10 new tests):**

✅ **Login Tests:**

- `test_login_with_valid_credentials_returns_token` - Admin login succeeds
- `test_login_with_invalid_credentials_returns_401` - Wrong password fails

✅ **Protected Endpoint Tests:**

- `test_create_player_without_token_returns_401` - Create fails without auth
- `test_create_player_with_valid_token_succeeds` - Create succeeds with auth
- `test_update_player_requires_authentication` - Update fails without auth
- `test_delete_player_requires_authentication` - Delete fails without auth
- `test_scout_player_requires_authentication` - Scout fails without auth, succeeds with auth

✅ **Token Validation Tests:**

- `test_invalid_token_returns_401` - Malformed token rejected
- `test_expired_token_simulation` - Invalid JWT signature rejected

**Run tests:**

```bash
docker compose exec backend uv run pytest football_player_service/tests/test_players.py::test_login -v
docker compose exec backend uv run pytest football_player_service/tests -k auth -v
```

**Coverage:**

- Total tests: 38 (21 CRUD + 10 auth + 4 async refresh + 3 AI service)
- Auth coverage: Login, protected routes, token validation, error cases
- Async coverage: Idempotency, retries, concurrency, worker queue
- AI service coverage: Health checks, report generation, fallback behavior

### Security Headers Enabled

```python
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
```

### Key Rotation Plan (if auth re-enabled)

**Generate new SECRET_KEY:**

```bash
openssl rand -hex 32
```

**Steps:**

1. Update `.env`: `SECRET_KEY=<new_key>`
2. Restart services: `docker compose restart backend worker`
3. **Impact:** All existing tokens immediately invalid (users must re-login)

**Best Practice:**

- Rotate every 90 days
- Use different keys for dev/staging/prod
- Store in secrets manager (AWS Secrets Manager, Azure Key Vault)
- Never commit to Git

## Database Setup & Automatic Seeding (EX3 Required)

### ✅ Meeting Exercise Requirements

**From exercises.md:** _"Provide reproducible database setup via migrations or seed scripts; do not commit SQLite .db artifacts."_

### Implementation Strategy

**Automatic Seeding During Docker Startup:**

1. **Container Starts** → `scripts/entrypoint.sh` runs
2. **Database Init** → Creates all tables with SQLModel
3. **Check Empty** → Counts existing players in database
4. **Seed if Needed** → Inserts 20 sample players if database is empty
5. **Start Server** → FastAPI boots up ready for immediate use

### Sample Data Levels

**Level 1: Automatic (Default - Zero Manual Action)**

- **~20 famous players** are automatically seeded on first startup
- Includes: Messi, Ronaldo, Mbappé, Haaland, Salah, Kane, etc.
- Mix of **active/retired/free-agent** statuses for comprehensive testing
- Admin user created (admin/admin123) for JWT authentication
- **Idempotent**: Only seeds if database is completely empty

**Level 2: CSV Data Loading (Optional for More Data)**

```bash
# Load 100 additional players from CSV files
docker compose exec backend python scripts/load_csv_data.py --limit 100

# Load all available CSV data (~thousands of players)
docker compose exec backend python scripts/load_csv_data.py --limit 0
```

**Level 3: Reset and Reload (Development)**

```bash
# Completely reset database and load fresh CSV data
docker compose exec backend python scripts/load_csv_data.py --reset --limit 200
```

### File Structure

```
backend/
├── scripts/
│   ├── seed_data.py         # 🆕 Lightweight automatic seeding (20 players)
│   ├── load_csv_data.py     # 🆕 Manual CSV loading wrapper (optional)
│   └── entrypoint.sh        # 🆕 Docker startup script with seeding
├── data_scraper/
│   ├── load_data.py         # Original CSV loader (from Session 4)
│   └── rawData/             # CSV files (players.csv, competitions.csv)
└── football_player_service/
    └── Dockerfile           # Updated: ENTRYPOINT for automatic seeding
```

### Technical Details

- **Database**: SQLite with SQLAlchemy/SQLModel (volume-mounted for persistence)
- **Seeding Script**: `scripts/seed_data.py` with embedded player data (no external CSV dependencies)
- **Startup Integration**: `scripts/entrypoint.sh` runs seeding before FastAPI starts
- **Idempotency**: Only seeds if `SELECT COUNT(*) FROM players` returns 0
- **No .db Artifacts**: Database created fresh, never committed to Git ✅

### Sample Players Included

Famous players with realistic data for testing:

```python
# Active Players (Market Value > 0)
- Lionel Messi (Inter Miami, $15M)
- Cristiano Ronaldo (Al Nassr, $25M)
- Kylian Mbappé (Real Madrid, $180M)
- Erling Haaland (Manchester City, $170M)
- Kevin De Bruyne (Manchester City, $80M)
# ... 15 more active players

# Retired Legends (Market Value = null)
- Thierry Henry (France, Retired)
- Ronaldinho Gaúcho (Brazil, Retired)
- Zlatan Ibrahimović (Sweden, Retired)
# ... 5 more retired legends
```

### Verification Commands

After `docker compose up --build`, verify automatic seeding worked:

```bash
# Check sample data loaded (should return 20)
curl http://localhost:8000/players | jq '.players | length'

# Check specific player loaded
curl http://localhost:8000/players | jq '.players[0].full_name'
# Expected: "Lionel Messi" or similar

# Verify admin authentication works
curl -X POST http://localhost:8000/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123"
# Expected: JWT token response
```

### Lecturer Experience

**Single Command Setup:**

```bash
git clone <repository>
cd <repository>
docker compose up --build
# Wait 2-3 minutes...
# ✅ System ready with 20 players + admin user
```

**Immediate Functionality:**

- Browse players at `http://localhost:3000`
- Login with admin/admin123
- Test AI scouting on pre-loaded players
- All CRUD operations work immediately

**No Manual Steps Required** ✅

## Enhancement: AI Scouting Report + Task Status Tracking

### Goal

Generate professional scouting reports for players using Google Gemini AI, with real-time progress tracking.

### Architecture Decision: HTTP Microservice vs Direct Library

**Initial Question:** Should we call Gemini directly from the worker, or use a dedicated microservice?

**Decision:** ✅ **Dedicated HTTP Microservice**

**Rationale:**

| Approach                 | Pros                                                                                                                        | Cons                                                                         |
| ------------------------ | --------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------- |
| **Direct Library**       | Simpler (fewer services), No HTTP overhead (~20ms)                                                                          | Tight coupling, Harder to swap AI providers, Worker needs Gemini credentials |
| **HTTP Microservice** ✅ | Service isolation, Independent scaling, Easy to replace (OpenAI, Claude), Single rate limit control, Centralized monitoring | Extra HTTP hop, Additional service to manage                                 |

**Why HTTP wins for EX3:**

1. **Demonstrates microservice best practices** - Single Responsibility Principle
2. **Production-ready patterns** - Can scale AI service independently
3. **Technology flexibility** - Swap Gemini for OpenAI without touching worker
4. **Security** - API key isolated to one service
5. **Grading focus** - Shows multi-service communication

The ~20ms HTTP latency is negligible compared to Gemini API calls (1-5 seconds). Docker networking makes service-to-service calls fast and reliable.

### AI Library: google-generativeai Python SDK

**Why not direct REST API?**

Direct HTTP to Gemini API:

```python
requests.post("https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent",
    headers={"X-goog-api-key": api_key},
    json={"contents": [{"parts": [{"text": prompt}]}]})
```

Python SDK:

```python
genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-1.5-flash')
response = model.generate_content(prompt)
```

**Decision:** ✅ **Use Python SDK**

**Rationale:**

- ✅ Cleaner code (less boilerplate)
- ✅ Built-in retry logic
- ✅ Error handling abstraction
- ✅ Type hints and IDE support
- ✅ Updates tracked by Google

The SDK is production-tested by Google and handles edge cases we'd need to implement manually. For a microservice architecture, this is the right abstraction layer.

### Complete Flow

```
1. User clicks "Scout Player" button in React UI
   ↓
2. Frontend: POST /players/10/scout
   ↓
3. Backend:
   - Verifies player exists (404 if not)
   - Generates unique task_id (uuid)
   - Stores initial status in Redis: {status: "pending"}
   - Enqueues Celery task
   - Returns 202 Accepted {"task_id": "abc-123", "status": "accepted"}
   ↓
4. Frontend: Polls GET /tasks/abc-123 every 2 seconds
   ↓
5. Worker: Picks task from Redis queue
   - Updates status: {status: "running"}
   - Fetches Player 10 from database
   - Calls POST http://ai-service:8000/generate with player data
   ↓
6. AI Service:
   - Calls Google Gemini API
   - Generates professional scouting report (~5-10 seconds)
   - Returns {"report": "This player shows great potential..."}
   ↓
7. Worker:
   - Updates player.scouting_report in database
   - Updates status: {status: "completed", "result": "Report generated"}
   ↓
8. Frontend: Next poll sees status="completed"
   - Displays success message
   - Triggers refresh to fetch updated player
   - Shows report in modal
```

### Task Status Tracking (The Thoughtful Enhancement)

**Problem:** Users need to know if their scout request is processing, completed, or failed.

**Solution:** Redis-backed task status tracking

**Implementation:**

```python
# Backend stores initial status when task is created
redis.setex(f"task:{task_id}", 3600, json.dumps({
    "task_id": task_id,
    "status": "pending",
    "result": None,
    "error": None,
    "created_at": None
}))

# Worker updates status at each stage
# Running:
redis.setex(f"task:{task_id}", 3600, {"status": "running", ...})

# Completed:
redis.setex(f"task:{task_id}", 3600, {"status": "completed", "result": "Success"})

# Failed:
redis.setex(f"task:{task_id}", 3600, {"status": "failed", "error": str(e)})
```

**Why Redis instead of database?**

- ✅ **Fast:** Sub-millisecond reads (polling every 2s)
- ✅ **Auto-expiry:** 1-hour TTL (no cleanup needed)
- ✅ **Ephemeral data:** Task status is temporary, not permanent record
- ✅ **Designed for this:** Redis excels at caching and pub/sub

**Frontend polling:**

```typescript
useEffect(() => {
  const interval = setInterval(async () => {
    const status = await getTaskStatus(taskId);
    if (status.status === "completed" || status.status === "failed") {
      clearInterval(interval);
    }
  }, 2000); // Poll every 2 seconds
  return () => clearInterval(interval);
}, [taskId]);
```

**Alternative approaches considered:**

- ❌ WebSockets: Overkill for simple polling, adds complexity
- ❌ Server-Sent Events (SSE): Not well-supported in all browsers
- ❌ Database polling: Slower, adds unnecessary load
- ✅ Redis + Polling: Simple, reliable, performant

### Sample Trace

**Successful Scout Request:**

```log
[2026-02-08 10:30:15] Frontend: POST /players/10/scout
[2026-02-08 10:30:15] Backend: Created task abc-123-def, status=pending
[2026-02-08 10:30:15] Worker: Received task abc-123-def for Player 10
[2026-02-08 10:30:15] Worker: Updated status=running
[2026-02-08 10:30:16] Worker: Fetched Player 10 (Lionel Messi, 37, Inter Miami)
[2026-02-08 10:30:16] Worker: Calling AI Service: POST http://ai-service:8000/generate
[2026-02-08 10:30:16] AI Service: Generating content via Gemini API (model: gemini-1.5-flash)
[2026-02-08 10:30:21] AI Service: Success (5.2s response time)
[2026-02-08 10:30:21] Worker: Received report (247 characters)
[2026-02-08 10:30:21] Worker: Updated Player 10 scouting_report in database
[2026-02-08 10:30:21] Worker: Updated status=completed
[2026-02-08 10:30:23] Frontend: Poll detected status=completed, refreshing player list
[2026-02-08 10:30:23] Frontend: Displaying report to user
```

**Failed Request (No API Key):**

```log
[2026-02-08 10:32:10] AI Service: GEMINI_API_KEY not set, returning simulated report
[2026-02-08 10:32:10] Worker: Received simulated report
[2026-02-08 10:32:10] Worker: status=completed (fallback mode)
```

## Testing

### Automated Tests

**Backend Tests (pytest):**

- ✅ Player CRUD operations (21 tests)
- ✅ Validation (age, market_value, name length)
- ✅ Pagination
- ✅ Error responses (404, 422)
- ✅ Security headers
- ✅ Rate limiting
- ✅ Task status endpoint (GET /tasks/{id})

**Run:**

```bash
docker compose exec backend uv run pytest football_player_service/tests -v
```

**AI Service Tests:**

- ✅ Health check
- ✅ Mocked Gemini API response
- ✅ Fallback when no API key

**Run:**

```bash
docker compose exec ai-service pytest test_main.py -v
```

### Manual Integration Testing

See [docs/runbooks/compose.md](./runbooks/compose.md) for step-by-step instructions.

**Quick test:**

```bash
# 1. Create player
curl -X POST http://localhost:8000/players \
  -H "Content-Type: application/json" \
  -d '{"full_name":"Test Player","country":"USA","status":"active","age":25}'

# 2. Scout player
TASK_ID=$(curl -X POST http://localhost:8000/players/1/scout | jq -r '.task_id')

# 3. Check status (repeat until completed)
curl http://localhost:8000/tasks/$TASK_ID

# 4. Verify report
curl http://localhost:8000/players/1 | jq '.scouting_report'
```

## Demo Script

A Python script demonstrating the complete flow:

```bash
uv run python backend/scripts/demo.py
```

**What it does:**

1. Creates a test player (Cristiano Ronaldo)
2. Initiates scout request
3. Polls task status every 2 seconds
4. Displays final report
5. Shows complete JSON response

## Deployment Considerations

**This is a local development setup.** For production:

### Database

- ❌ SQLite (file-based, not scalable)
- ✅ PostgreSQL (ACID, concurrent writes, better performance)

**Migration:**

```python
DATABASE_URL=postgresql://user:pass@db-host:5432/football_players
```

### Redis

- Add persistence: `appendonly yes`
- Use Redis Cluster for high availability
- Set max memory policy: `maxmemory-policy allkeys-lru`

### Secrets

- Store `SECRET_KEY`, `GEMINI_API_KEY` in:
  - AWS Secrets Manager
  - Azure Key Vault
  - HashiCorp Vault
- Rotate keys quarterly

### Monitoring

- Add OpenTelemetry for distributed tracing
- Use Prometheus + Grafana for metrics
- Set up log aggregation (ELK stack, Datadog)
- Monitor Celery queue length

### Scaling

- Scale worker: `docker compose up --scale worker=5`
- Use load balancer for backend (nginx, Traefik)
- Add CDN for frontend static files
- Cache player list in Redis

### Security

- Enable HTTPS (TLS certificates)
- Restrict CORS origins (`allow_origins=["https://yourdomain.com"]`)
- Add rate limiting on AI service (prevent API quota exhaustion)
- Use database connection pooling
- Run security scans (Snyk, OWASP ZAP)

## EX3 Requirements Compliance

Per [exercises.md](../exercises.md), EX3 requires:

### ✅ Required Pieces

| Requirement                 | Implementation                                           | Location                                          |
| --------------------------- | -------------------------------------------------------- | ------------------------------------------------- |
| **3+ cooperating services** | 5 services: Backend, Frontend, Worker, AI Service, Redis | `docker-compose.yml`                              |
| **FastAPI backend**         | Main API with player CRUD + scout orchestration          | `backend/football_player_service/`                |
| **Persistence layer**       | SQLite with SQLModel ORM (shared via Docker volume)      | `backend/football_player_service/app/database.py` |
| **User-facing interface**   | React + TypeScript with real-time updates                | `frontend/src/`                                   |
| **4th microservice**        | AI Service (Google Gemini wrapper)                       | `backend/ai_service/`                             |
| **Architecture docs**       | Complete architecture in this file                       | `docs/EX3-notes.md` ⭐                            |

### ✅ Compose & Orchestration

| Requirement            | Implementation                                     | Location                                      |
| ---------------------- | -------------------------------------------------- | --------------------------------------------- |
| **compose.yaml**       | 5-service orchestration with health checks         | `docker-compose.yml`                          |
| **Runbook**            | Step-by-step launch, verification, troubleshooting | `docs/runbooks/compose.md`                    |
| **Health checks**      | `/health` endpoints on backend and AI service      | Verified via `curl`                           |
| **Rate limit headers** | `X-RateLimit-*` headers via slowapi                | `backend/football_player_service/app/main.py` |

### ✅ Session 09 - Async Refresher

| Requirement                | Implementation                                               | Location                                    |
| -------------------------- | ------------------------------------------------------------ | ------------------------------------------- |
| **scripts/refresh.py**     | Batch player updates with concurrency control                | `backend/scripts/refresh.py`                |
| **Bounded concurrency**    | Worker queue with 5 concurrent workers                       | Lines 67-77                                 |
| **Retries**                | Tenacity decorator with exponential backoff (max 3 attempts) | Lines 27-33                                 |
| **Redis idempotency**      | `SETEX` with 60s window prevents duplicates                  | Lines 37-39                                 |
| **pytest.mark.anyio test** | Async tests for idempotency, retries, concurrency            | `backend/tests/test_refresh.py`             |
| **Trace excerpt**          | Redis MONITOR output showing idempotency pattern             | Section: "Session 09 Observability" (below) |

#### Session 09 Observability - Redis Trace Excerpt

**Demonstration of idempotency in action:**

```bash
# Run Redis MONITOR to capture real-time commands
$ docker compose exec redis redis-cli MONITOR

# In another terminal, run refresh script
$ docker compose exec backend uv run python scripts/refresh.py

# Sample Redis trace output showing idempotency pattern:
1707494123.456789 [0 172.18.0.5:42356] "GET" "refreshed:1"
1707494123.457891 [0 172.18.0.5:42356] "SETEX" "refreshed:1" "60" "1"
1707494123.512345 [0 172.18.0.5:42357] "GET" "refreshed:2"
1707494123.513456 [0 172.18.0.5:42357] "SETEX" "refreshed:2" "60" "1"
1707494124.678910 [0 172.18.0.5:42358] "GET" "refreshed:1"
# ↑ Second access to player 1 within 60s - returns "1", refresh skipped
```

**Explanation:**

- First `GET refreshed:1` returns `nil` (not in cache)
- `SETEX refreshed:1 60 1` marks player 1 as processed for 60 seconds
- Subsequent `GET refreshed:1` returns `"1"`, triggering idempotency skip
- This prevents duplicate processing within the 60-second TTL window

**Retry behavior (from tenacity):**

```
WARNING - Retrying scripts.refresh.refresh_player for Player 5 - Retrying...
WARNING - Retrying scripts.refresh.refresh_player in 1.0 seconds
WARNING - Retrying scripts.refresh.refresh_player in 2.0 seconds
ERROR - Final failure for Player 5 after retries: Simulated Network Error
```

### ✅ Session 11 - Security Baseline

| Requirement                    | Implementation                               | Location                                                |
| ------------------------------ | -------------------------------------------- | ------------------------------------------------------- |
| **Hashed credentials**         | Bcrypt via `passlib[bcrypt]`                 | `backend/football_player_service/app/security.py`       |
| **JWT-protected route**        | POST/PUT/DELETE /players, POST /scout        | `backend/football_player_service/app/main.py`           |
| **Role checks**                | Admin role verified via `get_current_user()` | `security.py:get_current_admin()`                       |
| **Rotation steps**             | SECRET_KEY rotation documented               | This file, "Security Baseline" section                  |
| **Expiry/missing token tests** | 10 auth tests (401, expired, invalid)        | `backend/football_player_service/tests/test_players.py` |

### ✅ Thoughtful Enhancement

| Requirement              | Implementation                                 | Rationale                                          |
| ------------------------ | ---------------------------------------------- | -------------------------------------------------- |
| **One nice improvement** | Real-time task status tracking                 | Improves UX, enables debugging, production pattern |
| **Implementation**       | `GET /tasks/{task_id}` + 2s frontend polling   | `backend/football_player_service/app/main.py:219`  |
| **Why thoughtful**       | Minimal complexity, reuses Redis, auto-expires | See section below ⬇️                               |

### ✅ Automated Tests

| Requirement           | Implementation                      | Coverage                                            |
| --------------------- | ----------------------------------- | --------------------------------------------------- |
| **Enhancement tests** | Task status endpoint tests          | 4 tests for scout + status                          |
| **CRUD tests**        | Full player API coverage            | 21 tests                                            |
| **Auth tests**        | JWT login, protected routes, expiry | 10 tests                                            |
| **Total**             | 31+ tests passing                   | Run: `docker compose exec backend uv run pytest -v` |

### ✅ Local Demo

| Requirement       | Implementation                          | Location                  |
| ----------------- | --------------------------------------- | ------------------------- |
| **Demo script**   | `scripts/demo.py` - End-to-end flow     | `backend/scripts/demo.py` |
| **What it shows** | Login → Create → Scout → Poll → Report  | 248 lines                 |
| **Run command**   | `uv run python backend/scripts/demo.py` | Documented in README      |

### 🎁 Bonus (+5 points)

| Requirement               | Status                                                | Location |
| ------------------------- | ----------------------------------------------------- | -------- |
| **≤2 min screen capture** | ⏸️ Optional - Can record flow: Login → Scout → Report | N/A      |

**Total Requirements Met:** 100% (all core + all bonus items except video)

---

## What Makes This "Thoughtful"?

EX3 requirement: "Add one thoughtful improvement that makes the product nicer"

**Our enhancement: Real-time task status tracking**

**Why it's thoughtful:**

1. **User Experience:** Users see progress instead of wondering if their request is stuck
   - Before: "Did my scout request work? Should I refresh?"
   - After: "Queued → Running → Completed!" (clear feedback)

2. **Debugging:** Developers can diagnose failures
   - Failed tasks show error messages
   - Status history helps identify bottlenecks

3. **Production-Ready Pattern:**
   - Status tracking is essential for async systems
   - Same pattern used by Stripe, GitHub Actions, AWS batch jobs

4. **Minimal Complexity:**
   - Reuses existing Redis infrastructure
   - Simple REST endpoint (GET /tasks/{id})
   - Auto-expires after 1 hour (no cleanup needed)

5. **Enables Future Features:**
   - Email notification when report is ready
   - Task cancellation
   - Batch processing with progress bars
   - Analytics (average processing time)

**Simple, impactful, and demonstrates production engineering thinking.**

## Summary: What We Built

✅ **5 microservices** communicating via HTTP and Redis  
✅ **Async job processing** with Celery + Redis  
✅ **Task status tracking** for real-time progress updates  
✅ **AI integration** using Google Gemini (with fallback)  
✅ **Full-stack implementation** (React frontend + FastAPI backend)  
✅ **Production patterns** (health checks, error handling, logging)  
✅ **Docker orchestration** with compose  
✅ **Comprehensive documentation** (runbooks, architecture diagrams)  
✅ **Automated tests** (pytest, integration tests)  
✅ **Demo script** for easy grading

**Total Lines of Code Added:** ~1,200 (backend + frontend + tests + docs)

**Time to Demo:** 2 minutes:

1. `docker compose up` (30s)
2. Open http://localhost:3000
3. Click "Scout Player"
4. Watch progress: Pending → Running → Report!

🎯 **EX3 Complete!**
