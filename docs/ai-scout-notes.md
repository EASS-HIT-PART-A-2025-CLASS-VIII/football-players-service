# AI Scouting Pipeline Notes

This document focuses on the AI scouting workflow, task queue, and related infrastructure.

## Overview

A user can request a scouting report for a player. The request is accepted immediately, a background task is queued, and the frontend polls for status updates until the report is ready.

Key goals:

- Keep the UI responsive with async processing.
- Provide task status tracking with Redis TTLs.
- Isolate AI calls in a dedicated microservice.

## Services and Roles

### Backend (FastAPI)

- Accepts scout requests and validates player existence.
- Writes initial task status in Redis.
- Enqueues Celery task to generate the report.
- Exposes `GET /tasks/{task_id}` for polling.

### Worker (Celery)

- Consumes tasks from Redis broker.
- Fetches player data from SQLite.
- Calls the AI service via HTTP.
- Updates player record with scouting report.
- Updates task status in Redis.

### AI Service (FastAPI)

- Wraps Google Gemini API.
- Exposes `POST /generate`.
- Returns a simulated report if `GEMINI_API_KEY` is not set.

### Redis

- Celery broker (task queue).
- Task status storage with TTL (1 hour).
- Celery result backend (if enabled).

### Frontend (React)

- Calls `POST /players/{id}/scout`.
- Polls `GET /tasks/{task_id}` every 2 seconds.
- Refreshes player data when task completes.

## Scout Request Flow (End-to-End)

1. User clicks "Scout" in the UI.
2. Frontend calls `POST /players/1/scout`.
3. Backend:
   - Validates player exists.
   - Creates a `task_id` (UUID).
   - Writes status to Redis as `pending`.
   - Enqueues Celery task with player id and task id.
   - Returns `202 Accepted` with `task_id`.
4. Frontend starts polling `GET /tasks/{task_id}`.
5. Worker picks the task:
   - Updates status to `running`.
   - Loads player from SQLite.
   - Calls AI Service `POST /generate`.
6. AI Service:
   - Calls Gemini API (or returns fallback report).
   - Responds with report text.
7. Worker:
   - Saves `scouting_report` to the player record.
   - Updates status to `completed`.
8. Frontend:
   - Detects `completed` status.
   - Refreshes player list.
   - Displays the report.

## Task Status Model

Stored in Redis under a `task:{task_id}` key with 1 hour TTL:

```json
{
  "task_id": "<uuid>",
  "status": "pending|running|completed|failed",
  "result": "<summary or message>",
  "error": "<error message or null>",
  "created_at": "<timestamp>"
}
```

Status transitions:

- `pending` -> `running` -> `completed`
- `pending` -> `failed`
- `running` -> `failed`

## Why a Dedicated AI Service

- Isolates the API key from the main backend and worker.
- Makes it easy to swap providers later.
- Allows independent scaling and monitoring.
- Avoids coupling the worker to the Gemini SDK.

## Redis Usage Details

- Task status: `SETEX task:{task_id} 3600 <json>`
- Idempotency is not required for scout tasks, but TTL ensures cleanup.
- Polling every 2 seconds is safe since Redis reads are cheap.

## Auth Notes (Only What Affects Scouting)

- `POST /players/{id}/scout` is protected by JWT.
- Token is stored in localStorage and injected via Axios interceptor.
- On `401`, the frontend clears the token and redirects to login.

## Error Handling

- If the player does not exist, backend returns `404` and no task is queued.
- If AI service fails, the worker marks the task as `failed` with error text.
- If `GEMINI_API_KEY` is missing, AI service returns a simulated report and the task still completes.

## Configuration

Required:

- `GEMINI_API_KEY`

Common defaults:

- `REDIS_URL=redis://redis:6379/0`
- `DATABASE_URL=sqlite:///data/players.db`

## Useful Endpoints

- `POST /players/{id}/scout` - enqueue scout job
- `GET /tasks/{task_id}` - read status
- `GET /players/{id}` - verify report is saved
- `POST /generate` - AI service endpoint
- `GET /health` - health checks

## Quick Manual Test (Local)

```bash
# Request a scout report (JWT required)
curl -X POST http://localhost:8000/players/1/scout \
  -H "Authorization: Bearer <token>"

# Poll task status
curl http://localhost:8000/tasks/<task_id>

# Verify report stored on player
curl http://localhost:8000/players/1
```

## Where to Look in Code

- Backend scout route: `backend/football_player_service/app/main.py`
- Task status helpers: `backend/football_player_service/app/main.py`
- Worker task logic: `backend/worker/main.py`
- AI service: `backend/ai_service/main.py`
- Frontend polling: `frontend/src/components/scoutReportModal/ScoutReportModal.tsx`
