# EX3: Full-Stack Microservices Final Project

## Microservices Architecture
The solution consists of 4 main services managed via Docker Compose:

1.  **Backend (FastAPI)**: Core REST API, manages Players and Users (Security).
2.  **Frontend (React)**: User interface for managing players and requesting reports.
3.  **Worker (Celery)**: Background worker for processing potentially long-running AI tasks.
4.  **AI Service (FastAPI)**: Dedicated microservice wrapping the Google Gemini API.

Plus **Redis** as the message broker and cache.

## Orchestration
To start the entire stack:
```bash
docker-compose up -d --build
```
This launches all services and sets up the network. The database is persisted in a volume.

## Async Refresher (Session 09)
The `scripts/refresh.py` script demonstrates:
- **Bounded Concurrency**: Uses `asyncio.Semaphore` (or limited worker tasks) to process updates.
- **Idempotency**: Uses Redis (SETEX) to prevent re-processing the same player within a window.
- **Retries**: (Simulated in script logic).

Run it via:
```bash
docker-compose exec backend uv run python scripts/refresh.py
```

## Security Baseline (Session 11)
- **Hashed Credentials**: Passwords are hashed using Bcrypt (`passlib`).
- **JWT Protection**: `create_player`, `update_player`, `delete_player` and `scout_player` require a valid JWT token.
- **Role Checks**: Admin role seeded (`admin`/`admin123`).

### Key Rotation Plan
1.  Generate a new `SECRET_KEY`.
2.  Update `.env` file with `SECRET_KEY=<new_key>`.
3.  Restart services: `docker-compose restart backend`.
4.  *Note: Existing tokens will become invalid immediately.*

## Enhancement: AI Scouting Report
- **Goal**: Generate a text summary of a player's potential.
- **Flow**: User -> Backend (Enqueues Task) -> Redis -> Worker -> AI Service (Gemini) -> DB Update.
- **Trace**:
    ```
    [INFO] Received scouting request for Player 10
    [INFO] Worker fetched Player 10 (Lionel Messi)
    [INFO] Calling AI Service at http://ai-service:8000/generate
    [INFO] AI Service: Generating content via Gemini...
    [INFO] AI Service: Success.
    [INFO] Worker updated Player 10 with report.
    ```
