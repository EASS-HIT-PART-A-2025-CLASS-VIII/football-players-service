import logging
import uuid
import os
from typing import List, Annotated
from contextlib import asynccontextmanager
from datetime import timedelta

from fastapi import FastAPI, HTTPException, Request, status, Query, Depends
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from sqlmodel import Session, select
from celery import Celery

from .dependencies import RepositoryDep, SettingsDep
from .models import Player, PlayerCreate, PaginatedPlayers, User, Token
from .database import init_db, get_session, engine
from .security import (
    verify_password,
    get_password_hash,
    create_access_token,
    get_current_user,
    ACCESS_TOKEN_EXPIRE_MINUTES
)

logger = logging.getLogger("football-player-service")
logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)

# Celery config
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
celery_app = Celery("ai_scout", broker=REDIS_URL, backend=REDIS_URL)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event handler for startup and shutdown."""
    init_db()
    
    # Seed admin user
    with Session(engine) as session:
        statement = select(User).where(User.username == "admin")
        results = session.exec(statement)
        admin = results.first()
        if not admin:
            hashed_pwd = get_password_hash("admin123")
            admin_user = User(username="admin", hashed_password=hashed_pwd, role="admin")
            session.add(admin_user)
            session.commit()
            logger.info("Created default admin user (admin/admin123)")

    logger.info("=" * 60)
    logger.info("⚽ Football Player Service v0.3.0 (EX3)")
    yield
    logger.info("Shutting down Football Player Service")

async def rate_limit_exception_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        content={"error": {"code": "RATE_LIMIT_EXCEEDED", "message": "Rate limit exceeded."}},
    )

async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"error": {"code": "INTERNAL_SERVER_ERROR", "message": str(exc)}},
    )

app = FastAPI(
    title="Football Player Service",
    version="0.3.0",
    description="CRUD API + AI Scout + Security.",
    lifespan=lifespan,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, rate_limit_exception_handler)
app.add_exception_handler(Exception, global_exception_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production restricting this is better
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    return response

# === Auth Endpoints ===

@app.post("/token", response_model=Token, tags=["auth"])
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: Session = Depends(get_session)
):
    user = session.get(User, form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "role": user.role}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# === Service Endpoints ===

@app.get("/health", tags=["diagnostics"])
def health(settings: SettingsDep) -> dict:
    return {"status": "ok", "app": settings.app_name}

@app.get("/players", response_model=PaginatedPlayers, tags=["players"])
def list_players(
    repository: RepositoryDep,
    page: int = Query(1, ge=1),
    limit: int = Query(12, ge=1, le=100),
):
    all_players = list(repository.list())
    total = len(all_players)
    pages = (total + limit - 1) // limit
    if page > pages and total > 0:
        page = pages
    start = (page - 1) * limit
    end = start + limit
    paginated_data = all_players[start:end]
    return PaginatedPlayers(data=paginated_data, total=total, page=page, limit=limit, pages=pages)

@app.post("/players", response_model=Player, status_code=status.HTTP_201_CREATED, tags=["players"])
@limiter.limit("100/minute")
def create_player(
    request: Request,
    payload: PlayerCreate,
    repository: RepositoryDep,
    current_user: User = Depends(get_current_user), # Protected
):
    return repository.create(payload)

@app.get("/players/{player_id}", response_model=Player, tags=["players"])
def read_player(player_id: int, repository: RepositoryDep):
    player = repository.get(player_id)
    if player is None:
        raise HTTPException(status_code=404, detail="Player not found")
    return player

@app.put("/players/{player_id}", response_model=Player, tags=["players"])
@limiter.limit("100/minute")
def update_player(
    request: Request,
    player_id: int,
    payload: PlayerCreate,
    repository: RepositoryDep,
    current_user: User = Depends(get_current_user), # Protected
):
    updated = repository.update(player_id, payload)
    if updated is None:
        raise HTTPException(status_code=404, detail="Player not found")
    return updated

@app.delete("/players/{player_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["players"])
def delete_player(
    player_id: int,
    repository: RepositoryDep,
    current_user: User = Depends(get_current_user), # Protected
):
    if repository.get(player_id) is None:
        raise HTTPException(status_code=404, detail="Player not found")
    repository.delete(player_id)

# === AI Scout ===

@app.post("/players/{player_id}/scout", status_code=202, tags=["ai-scout"])
def scout_player(player_id: int, current_user: User = Depends(get_current_user)): # Protected
    """Enqueue AI scouting report generation."""
    task_id = str(uuid.uuid4())
    celery_app.send_task("ai_scout.generate_report", args=[player_id], task_id=task_id)
    return {"task_id": task_id, "status": "accepted"}
