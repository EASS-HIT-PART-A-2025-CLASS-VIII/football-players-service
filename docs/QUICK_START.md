# EX3 Quick Start Guide

## 🚀 Launch Everything with Docker Compose

### Prerequisites

- Docker Desktop installed and running
- Ports available: 3000, 5432, 6379, 8000, 8001

### Start All Services

```bash
# From project root
docker compose -f docker-compose.ex3.yml up --build
```

**Wait for all services to start (2-3 minutes)**

You'll see:

```
✅ football-db (PostgreSQL)
✅ football-redis (Redis)
✅ football-backend (Main API)
✅ football-analytics (AI Service)
✅ football-worker (Background Tasks)
✅ football-frontend (React)
```

### Access Points

| Service        | URL                        | Description    |
| -------------- | -------------------------- | -------------- |
| **Frontend**   | http://localhost:3000      | React UI       |
| **Main API**   | http://localhost:8000/docs | Swagger UI     |
| **Analytics**  | http://localhost:8001/docs | AI Service API |
| **PostgreSQL** | localhost:5432             | Database       |
| **Redis**      | localhost:6379             | Task Queue     |

---

## 🔐 Login Credentials

### Default Admin User

- **Username:** `admin`
- **Password:** `admin123`

> ⚠️ **Change in production!**

---

## 🎯 Quick Demo Workflow

### 1. Login via API

```bash
# Get JWT token
curl -X POST http://localhost:8000/auth/login \
  -d "username=admin&password=admin123"
```

**Copy the `access_token` from response**

### 2. Create a Player

```bash
curl -X POST http://localhost:8000/players \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "Kylian Mbappe",
    "country": "France",
    "status": "active",
    "current_team": "Real Madrid",
    "league": "La Liga",
    "age": 25,
    "market_value": 180000000
  }'
```

### 3. Get AI Insights

```bash
# Replace {player_id} with the ID from step 2
curl http://localhost:8001/insights/1
```

**Response includes:**

- Performance score (0-100)
- Career trajectory prediction
- Injury risk assessment
- Personalized insights

### 4. Trigger Background Market Refresh (Admin Only)

```bash
curl -X POST http://localhost:8000/admin/refresh-market-values \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```

**Response:**

```json
{
  "status": "queued",
  "job_id": "abc123...",
  "message": "Market refresh task queued successfully"
}
```

### 5. Check Job Status

```bash
curl http://localhost:8000/admin/job-status/JOB_ID_HERE \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```

---

## 📊 Frontend Usage

1. **Open:** http://localhost:3000
2. **Browse Players:** View list of all players
3. **Create Player:** Click "Add Player" button
4. **View Details:** Click on a player card
5. **AI Insights:** (TODO) See analytics tab

---

## 🧪 Test the System

### Health Checks

```bash
# Main API
curl http://localhost:8000/health

# Analytics Service
curl http://localhost:8001/health
```

### List All Players

```bash
curl http://localhost:8000/players
```

### Get Specific Player

```bash
curl http://localhost:8000/players/1
```

---

## 🛑 Stop Services

```bash
# Stop and keep data
docker compose -f docker-compose.ex3.yml down

# Stop and remove data (fresh start)
docker compose -f docker-compose.ex3.yml down -v
```

---

## 🔄 Rebuild After Code Changes

```bash
# Rebuild specific service
docker compose -f docker-compose.ex3.yml up --build backend

# Rebuild all
docker compose -f docker-compose.ex3.yml up --build
```

---

## 📝 View Logs

```bash
# All services
docker compose -f docker-compose.ex3.yml logs -f

# Specific service
docker compose -f docker-compose.ex3.yml logs -f backend
docker compose -f docker-compose.ex3.yml logs -f analytics
docker compose -f docker-compose.ex3.yml logs -f worker
```

---

## ⚡ Run Async Refresh Script (Local)

### Prerequisites

```bash
cd backend
uv sync
```

### Run Refresh

```bash
# Refresh all players
uv run python ../scripts/refresh.py --all --api-url http://localhost:8000

# Refresh specific players
uv run python ../scripts/refresh.py --player-ids 1 2 3
```

**Output:**

```
Refreshing 3 players with max 5 concurrent requests
Player 1: $180,000,000 → $175,500,000 (attempt 1)
Player 2: $50,000,000 → $52,000,000 (attempt 1)
Player 3: $10,000,000 → $9,500,000 (attempt 1)
==================================================
Refresh Summary:
  Total: 3
  Successful: 3
  Failed: 0
  Skipped: 0
  Duration: 1.23s
==================================================
```

---

## 🐛 Troubleshooting

### Port Already in Use

```bash
# Find process using port
netstat -ano | findstr :8000  # Windows
lsof -i :8000                 # Mac/Linux

# Stop existing containers
docker compose -f docker-compose.ex3.yml down
```

### Services Not Starting

```bash
# Check Docker daemon
docker ps

# View service logs
docker compose -f docker-compose.ex3.yml logs backend

# Restart specific service
docker compose -f docker-compose.ex3.yml restart backend
```

### Database Issues

```bash
# Reset database (removes all data)
docker compose -f docker-compose.ex3.yml down -v
docker compose -f docker-compose.ex3.yml up --build
```

### Worker Not Processing Tasks

```bash
# Check Redis connection
docker exec -it football-redis redis-cli ping
# Should return: PONG

# Check worker logs
docker compose -f docker-compose.ex3.yml logs worker
```

---

## 📦 Service Dependencies

```
PostgreSQL (db)
  ↓
Backend (8000) ←───┐
  ↓                │
Analytics (8001)   │
  ↓                │
Worker ────────────┘
  ↓
Redis (6379)
```

**Startup Order:**

1. PostgreSQL & Redis (parallel)
2. Backend (waits for db + redis)
3. Analytics (waits for backend)
4. Worker (waits for backend + redis)
5. Frontend (waits for backend + analytics)

---

## 🎬 Demo Script

See full walkthrough: [scripts/demo.sh](../scripts/demo.sh) (TODO)

---

## 📚 API Documentation

- **Main API Docs:** http://localhost:8000/docs
- **Analytics Docs:** http://localhost:8001/docs
- **OpenAPI JSON:** http://localhost:8000/openapi.json

---

## 🔐 Security Notes

### Default Credentials

- Admin: `admin` / `admin123`
- **Must be changed in production**

### JWT Secret

- Default: `your-secret-key-change-in-production-2026`
- **Set via environment variable:** `JWT_SECRET_KEY`

### Token Expiration

- 30 minutes by default
- Refresh by logging in again

---

## 💡 Tips

1. **Use Postman/Insomnia** for easier API testing
2. **Import OpenAPI spec** from http://localhost:8000/openapi.json
3. **Monitor Redis** with RedisInsight: http://localhost:8001
4. **Database GUI:** Use pgAdmin or DBeaver for PostgreSQL

---

## 📖 Next Steps

1. ✅ Start services
2. ✅ Create some players
3. ✅ Generate AI insights
4. ✅ Trigger background refresh
5. 🚧 Build frontend analytics UI
6. 🚧 Add comprehensive tests
7. 🚧 Complete documentation

---

**Need Help?** Check [EX3_IMPLEMENTATION.md](EX3_IMPLEMENTATION.md) for detailed architecture
