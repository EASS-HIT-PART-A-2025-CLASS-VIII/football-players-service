# Docker Compose Runbook

## Prerequisites

- Docker Desktop installed and running
- Git repository cloned locally
- Gemini API key (get one from https://ai.google.dev/)

## Setup

### 1. Configure Environment Variables

Create a `.env` file in the project root:

```bash
cp .env.example .env
```

Edit `.env` and add your Gemini API key:

```env
GEMINI_API_KEY=your_actual_api_key_here
```

**Note:** If you don't have a Gemini API key, the AI service will return simulated reports for demo purposes.

### 2. Start All Services

From the project root directory:

```bash
docker compose up --build
```

**What this does:**

- Builds all Docker images (backend, frontend, worker, ai-service)
- Starts 5 services: backend API, frontend UI, Redis, Celery worker, AI service
- Creates a shared network for service communication
- Mounts volumes for database persistence
- **Automatically seeds database with ~20 sample football players** ⚽

**First-time build:** Takes 3-5 minutes to download dependencies and build images.

**Database Setup:**

- Empty SQLite database is created automatically
- Sample players (Messi, Ronaldo, Mbappé, etc.) are seeded on first startup
- Includes mix of active, retired, and free-agent players for testing
- Admin user (admin/admin123) is created for JWT authentication
- Seeding only happens if database is empty (idempotent)

**Services:**

- **Backend API:** http://localhost:8000
- **Frontend UI:** http://localhost:3000
- **AI Service:** http://localhost:8001 (internal use)
- **Redis:** localhost:6379

### 3. Verify Services Are Running

**Check health endpoints:**

```bash
# Backend health
curl http://localhost:8000/health
# Expected: {"status":"ok","app":"Football Player Service"}

# AI service health
curl http://localhost:8001/health
# Expected: {"status":"ok"}

# Frontend (in browser)
# Visit: http://localhost:3000
```

**Check rate-limit headers:**

```bash
curl -i -X POST http://localhost:8000/players \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"full_name":"Rate Check","country":"Test","status":"active","age":25}'

# Expected headers include X-RateLimit-Limit / X-RateLimit-Remaining
```

**Check Docker logs:**

```bash
# All services
docker compose logs

# Specific service
docker compose logs backend
docker compose logs worker
docker compose logs ai-service

# Follow logs in real-time
docker compose logs -f worker
```

## Testing (Pytest)

Run tests inside the backend container:

```bash
docker compose exec backend uv run pytest football_player_service/tests -v
```

Optional local runs (from `backend/`):

```bash
uv run pytest football_player_service/tests -v
uv run pytest tests/test_refresh.py -v
uv run pytest ai_service/test_main.py -v
```

## Usage

### Database & Sample Data

The system provides multiple levels of sample data:

**Level 1: Automatic Sample Data (Default)**

- **~20 famous players** are automatically loaded on first startup
- Includes Messi, Ronaldo, Mbappé, Haaland, etc.
- Mix of active/injured/retired statuses
- **No manual action required** - works immediately after `docker compose up --build`

**Level 2: Load Additional CSV Data (Optional)**
If you want more players for testing:

```bash
# Load 100 additional random players from CSV files
docker compose exec backend python scripts/load_csv_data.py

# Load 500 players
docker compose exec backend python scripts/load_csv_data.py --limit 500

# Load ALL available players from CSV (~thousands)
docker compose exec backend python scripts/load_csv_data.py --limit 0
```

**Level 3: Reset and Reload (Development)**
To start fresh with different data:

```bash
# Clear all players and load fresh CSV data
docker compose exec backend python scripts/load_csv_data.py --reset --limit 200
```

### Login

**Default Credentials:**

- Username: `admin`
- Password: `admin123`

The admin user is automatically created on first startup. All write operations (create, update, delete, scout) require JWT authentication per EX3 requirements.

### Test the Complete AI Scout Flow

**1. Open the frontend:**

```
http://localhost:3000
```

**2. Login with default credentials:**

- The login page appears automatically
- Enter username: `admin`
- Enter password: `admin123`
- Click "Login"

**3. Create a test player** (or use existing player):

- Click "Add Player" button
- Login to get JWT token:\*\*

```bash
# Get token
TOKEN=$(curl -X POST http://localhost:8000/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123" \
  | jq -r '.access_token')

echo "Token: $TOKEN"
```

**Create a player (requires auth):**

```bash
curl -X POST http://localhost:8000/players \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "full_name": "Lionel Messi",
    "country": "Argentina",
    "status": "active",
    "current_team": "Inter Miami",
    "league": "MLS",
    "age": 37,
    "market_value": 15000000
  }'
```

**Scout a player (requires auth):**

```bash
# Scout player ID 1
curl -X POST http://localhost:8000/players/1/scout \
  -H "Authorization: Bearer $TOKEN"
    "country": "Argentina",
    "status": "active",
    "current_team": "Inter Miami",
    "league": "MLS",
    "age": 37,
    "market_value": 15000000
  }'
```

**Scout a player:**

```bash
# Scout player ID 1
curl -X POST http://localhost:8000/players/1/scout
# Returns: {"task_id":"abc-123-def","status":"accepted"}
```

**Check task status:**

```bash
# Poll until status is "completed"
curl http://localhost:8000/tasks/abc-123-def
# Returns: {"task_id":"abc-123-def","status":"completed","result":"Report generated for Lionel Messi"}
```

**Get player with report:**

```bash
curl http://localhost:8000/players/1
# Player JSON now includes "scouting_report" field
```

## Monitoring

### Check Service Status

```bash
docker compose ps
```

Expected output:

```
NAME                   STATUS    PORTS
ex1-backend-1          Up        0.0.0.0:8000->8000/tcp
ex1-frontend-1         Up        0.0.0.0:3000->3000/tcp
ex1-redis-1            Up        0.0.0.0:6379->6379/tcp
ex1-worker-1           Up
ex1-ai-service-1       Up        0.0.0.0:8001->8000/tcp
```

### Monitor Worker Task Processing

```bash
docker compose logs -f worker
```

Look for:

```
Processing report for player 1 (task: abc-123-def)
Report generated for Lionel Messi
```

### Check Redis Queue

**Install redis-cli** (optional):

```bash
# Access Redis from worker container
docker compose exec worker sh
# Inside container:
redis-cli -h redis
> KEYS *
> GET task:abc-123-def
```

## Rate Limits

**Backend API:**

- POST/PUT requests: **100 requests/minute** per IP
- GET requests: Unlimited

**Gemini API:**

- Free tier: 15 requests/minute
- Check your quota: https://ai.google.dev/

If you hit Gemini rate limits, wait 1 minute and retry the scout request.

## Troubleshooting

### Worker Not Processing Tasks

**Symptoms:** Scout requests return 202 Accepted, but status stays "pending"

**Check:**

```bash
# Worker logs
docker compose logs worker

# Look for connection errors
docker compose logs worker | grep -i error

# Verify Redis connectivity
docker compose exec worker ping redis
```

**Fix:**

```bash
# Restart worker
docker compose restart worker
```

### AI Service Returns Simulated Reports

**Cause:** `GEMINI_API_KEY` not set or invalid

**Check:**

```bash
docker compose exec ai-service env | grep GEMINI
```

**Fix:** Update `.env` file and restart:

```bash
docker compose down
docker compose up --build ai-service
```

### Database Not Persisting

**Symptoms:** Players disappear after stopping Docker

**Check volume mount:**

```bash
ls -la backend/data/
# Should see: football_players.db
```

**Fix:** Ensure `backend/data/` directory exists:

```bash
mkdir -p backend/data
docker compose down
docker compose up
```

**Note:** Sample data will be automatically re-seeded if database is empty.

### No Sample Players After Startup

**Symptoms:** Database is empty except for admin user

**Cause:** Seeding script failed during container startup

**Check logs:**

```bash
docker compose logs backend | grep -i seed
# Look for seeding messages
```

**Manual fix:**

```bash
# Seed sample data manually
docker compose exec backend python scripts/seed_data.py

# Or load CSV data
docker compose exec backend python scripts/load_csv_data.py --limit 50
```

### Port Already In Use

**Symptoms:** `Error: bind: address already in use`

**Check:**

```bash
# Windows
netstat -ano | findstr :8000

# macOS/Linux
lsof -i :8000
```

**Fix:** Stop the conflicting process or change the port in `docker-compose.yml`:

```yaml
backend:
  ports:
    - "8001:8000" # Use 8001 instead
```

### Frontend Can't Connect to Backend

**Symptoms:** Frontend shows connection errors in browser console

**Check:**

```bash
# Backend is running
curl http://localhost:8000/health

# CORS headers (should allow localhost:3000)
curl -H "Origin: http://localhost:3000" -I http://localhost:8000/health
```

**Fix:** Update `ALLOWED_ORIGINS` in `docker-compose.yml` and restart:

```bash
docker compose restart backend
```

## Stopping Services

### Graceful Shutdown

```bash
docker compose down
```

**What this does:**

- Stops all containers
- Removes containers
- Keeps volumes (database persists)
- Keeps images (faster next startup)

### Complete Cleanup

```bash
# Stop + remove volumes (deletes database)
docker compose down -v

# Rebuild from scratch
docker compose build --no-cache
docker compose up
```

## Development Workflow

### Quick Restart After Code Changes

**Backend changes:**

```bash
docker compose restart backend
# or for full rebuild:
docker compose up --build backend
```

**Frontend changes:**

```bash
docker compose restart frontend
```

**Worker changes:**

```bash
docker compose restart worker
```

### View Build Logs

```bash
docker compose build --progress=plain
```

### Run Tests Inside Container

```bash
# Backend tests
docker compose exec backend pytest football_player_service/tests -v

# With coverage
docker compose exec backend pytest --cov=football_player_service
```

## Performance Tips

1. **Pre-pull base images:**

   ```bash
   docker pull python:3.11-slim
   docker pull node:20-alpine
   docker pull redis:alpine
   ```

2. **Use BuildKit for faster builds:**

   ```bash
   DOCKER_BUILDKIT=1 docker compose build
   ```

3. **Limit logs:**
   ```bash
   docker compose logs --tail=100
   ```

## Security Notes

🔒 **This is a local development setup. Before deploying to production:**

- [ ] Use strong SECRET_KEY (not the default)
- [ ] Restrict CORS origins to your frontend domain
- [ ] Enable HTTPS
- [ ] Add authentication if needed
- [ ] Rate limit AI service requests
- [ ] Set Gemini API quota limits
- [ ] Use PostgreSQL instead of SQLite
- [ ] Monitor logs for errors

## Next Steps

✅ All services running → Test the scout feature in the frontend
✅ Ready to develop → Make code changes and restart relevant services
✅ Need help → Check logs with `docker compose logs -f`
