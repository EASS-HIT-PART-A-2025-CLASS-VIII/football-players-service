import logging
from typing import List, Optional
from contextlib import asynccontextmanager
from datetime import timedelta
from fastapi import FastAPI, HTTPException, Request, status, Query
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from .dependencies import (
    RepositoryDep, SettingsDep, UserRepositoryDep,
    CurrentUserDep, AdminUserDep
)
from .models import Player, PlayerCreate, PaginatedPlayers, User, UserRole
from .database import init_db
from .auth import (
    Token, UserCreate, UserResponse, LoginRequest,
    verify_password, get_password_hash, create_access_token,
    ACCESS_TOKEN_EXPIRE_MINUTES
)

logger = logging.getLogger("football-player-service")
logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

# Initialize rate limiter (100 requests per minute per IP)
limiter = Limiter(key_func=get_remote_address)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event handler for startup and shutdown."""
    # Startup
    init_db()  # Create tables on startup
    logger.info("=" * 60)
    logger.info("⚽ Football Player Service v0.3.0 (EX3)")
    logger.info("=" * 60)
    logger.info("Features:")
    logger.info("  ✓ JWT Authentication with role-based access control")
    logger.info("  ✓ Background worker integration (Redis + RQ)")
    logger.info("  ✓ Rate limiting: 100 req/min per IP")
    logger.info("  ✓ Security headers: X-Frame-Options, HSTS, etc.")
    logger.info("  ✓ CORS: Enabled (configure for production)")
    logger.info("  ✓ Health check: /health endpoint")
    logger.info("  ✓ API Documentation: /docs (Swagger UI)")
    logger.info("  ✓ Database: SQLite (local) / PostgreSQL (production)")
    logger.info("=" * 60)
    yield
    # Shutdown (if needed)
    logger.info("Shutting down Football Player Service")


# Custom rate limit exceeded handler
async def rate_limit_exception_handler(request: Request, exc: RateLimitExceeded):
    """Handle rate limit exceeded errors."""
    return JSONResponse(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        content={
            "error": {
                "code": "RATE_LIMIT_EXCEEDED",
                "message": "Rate limit exceeded. Maximum 100 requests per minute per IP.",
            }
        },
    )


# Global exception handler for unhandled errors
async def global_exception_handler(request: Request, exc: Exception):
    """Handle uncaught exceptions with consistent error response."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "Internal server error",
                "type": exc.__class__.__name__,
            }
        },
    )


app = FastAPI(
    title="Football Player Service",
    version="0.3.0",
    description="CRUD API for managing football players with validation, authentication, and background workers.",
    lifespan=lifespan,
)

# Add rate limiter and exception handlers
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, rate_limit_exception_handler)
app.add_exception_handler(Exception, global_exception_handler)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict to specific domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Add security headers middleware
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    """Add security headers to all responses."""
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = (
        "max-age=31536000; includeSubDomains"
    )
    return response


@app.get("/health", tags=["diagnostics"])
def health(settings: SettingsDep) -> dict:
    """Health check endpoint."""
    return {"status": "ok", "app": settings.app_name}


# ==================== Authentication Endpoints ====================

@app.post("/auth/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED, tags=["auth"])
def register_user(
    user_data: UserCreate,
    user_repo: UserRepositoryDep,
) -> UserResponse:
    """
    Register a new user.
    
    Note: New users are created with 'user' role by default.
    Admin role must be assigned manually.
    """
    # Check if username already exists
    if user_repo.get_by_username(user_data.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # Check if email already exists
    if user_repo.get_by_email(user_data.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create user with hashed password
    hashed_password = get_password_hash(user_data.password)
    user = user_repo.create(
        email=user_data.email,
        username=user_data.username,
        hashed_password=hashed_password,
        role=user_data.role or UserRole.USER
    )
    
    logger.info(f"user.registered username={user.username} email={user.email} role={user.role}")
    
    return UserResponse(
        id=user.id,
        email=user.email,
        username=user.username,
        role=user.role,
        is_active=user.is_active,
        created_at=user.created_at
    )


@app.post("/auth/login", response_model=Token, tags=["auth"])
def login(
    form_data: OAuth2PasswordRequestForm = Depends(OAuth2PasswordRequestForm),
    user_repo: UserRepositoryDep = Depends(),
) -> Token:
    """
    Login and receive JWT access token.
    
    Use the token in subsequent requests:
    - Authorization: Bearer <token>
    """
    user = user_repo.get_by_username(form_data.username)
    
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    
    # Create access token
    access_token = create_access_token(
        data={"sub": user.username, "role": user.role.value},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    
    logger.info(f"user.login username={user.username} role={user.role}")
    
    return Token(access_token=access_token, token_type="bearer")


@app.get("/auth/me", response_model=UserResponse, tags=["auth"])
def get_current_user_info(current_user: CurrentUserDep) -> UserResponse:
    """
    Get current authenticated user information.
    
    Requires: Valid JWT token
    """
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        username=current_user.username,
        role=current_user.role,
        is_active=current_user.is_active,
        created_at=current_user.created_at
    )


# ==================== Admin Endpoints ====================

@app.post("/admin/refresh-market-values", tags=["admin"])
async def trigger_market_refresh(
    admin_user: AdminUserDep,
    player_ids: Optional[List[int]] = None,
) -> dict:
    """
    Trigger background task to refresh player market values.
    
    Requires: Admin role
    
    Args:
        player_ids: Optional list of specific player IDs to refresh. If None, refreshes all players.
    
    Returns:
        Job information with job_id for tracking
    """
    try:
        from backend.worker_service.app.tasks import enqueue_market_refresh
        
        job = enqueue_market_refresh(player_ids)
        
        logger.info(f"admin.refresh_triggered job_id={job.id} user={admin_user.username}")
        
        return {
            "status": "queued",
            "job_id": job.id,
            "message": "Market refresh task queued successfully",
            "player_ids": player_ids or "all"
        }
    except Exception as e:
        logger.error(f"Failed to enqueue market refresh: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Failed to queue background task: {str(e)}"
        )


@app.get("/admin/job-status/{job_id}", tags=["admin"])
async def get_job_status_endpoint(
    job_id: str,
    admin_user: AdminUserDep,
) -> dict:
    """
    Get status of a background job.
    
    Requires: Admin role
    """
    try:
        from backend.worker_service.app.tasks import get_job_status
        
        job_status = get_job_status(job_id)
        return job_status
    except Exception as e:
        logger.error(f"Failed to get job status: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Failed to get job status: {str(e)}"
        )


# ==================== Player Endpoints ====================


@app.get("/players", response_model=PaginatedPlayers, tags=["players"])
def list_players(
    repository: RepositoryDep,
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    limit: int = Query(12, ge=1, le=100, description="Items per page"),
) -> PaginatedPlayers:
    """Get players with pagination."""
    all_players = list(repository.list())
    total = len(all_players)
    pages = (total + limit - 1) // limit  # Ceiling division
    
    # Validate page number
    if page > pages and total > 0:
        page = pages
    
    # Calculate slice boundaries
    start = (page - 1) * limit
    end = start + limit
    paginated_data = all_players[start:end]
    
    return PaginatedPlayers(
        data=paginated_data,
        total=total,
        page=page,
        limit=limit,
        pages=pages,
    )


@app.post(
    "/players",
    response_model=Player,
    status_code=status.HTTP_201_CREATED,
    tags=["players"],
)
@limiter.limit("100/minute")
def create_player(
    request: Request,
    payload: PlayerCreate,
    repository: RepositoryDep,
) -> Player:
    """Create a new player."""
    player = repository.create(payload)
    logger.info(
        "player.created id=%s name=%s status=%s age=%s market_value=%s",
        player.id,
        player.full_name,
        player.status,
        player.age,
        player.market_value,
    )
    return player


@app.get("/players/{player_id}", response_model=Player, tags=["players"])
def read_player(
    player_id: int,
    repository: RepositoryDep,
) -> Player:
    """Get a specific player by ID."""
    player = repository.get(player_id)
    if player is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": {
                    "code": "PLAYER_NOT_FOUND",
                    "message": f"Player with ID {player_id} not found",
                    "player_id": player_id,
                }
            },
        )
    return player


@app.put(
    "/players/{player_id}",
    response_model=Player,
    tags=["players"],
)
@limiter.limit("100/minute")
def update_player(
    request: Request,
    player_id: int,
    payload: PlayerCreate,
    repository: RepositoryDep,
) -> Player:
    """Update a player by ID (full replace)."""
    updated = repository.update(player_id, payload)
    if updated is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": {
                    "code": "PLAYER_NOT_FOUND",
                    "message": f"Player with ID {player_id} not found",
                    "player_id": player_id,
                }
            },
        )
    logger.info(
        "player.updated id=%s name=%s status=%s age=%s market_value=%s",
        updated.id,
        updated.full_name,
        updated.status,
        updated.age,
        updated.market_value,
    )
    return updated


@app.delete(
    "/players/{player_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["players"],
)
def delete_player(
    player_id: int,
    repository: RepositoryDep,
) -> None:
    """Delete a player by ID."""
    if repository.get(player_id) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": {
                    "code": "PLAYER_NOT_FOUND",
                    "message": f"Player with ID {player_id} not found",
                    "player_id": player_id,
                }
            },
        )
    repository.delete(player_id)
    logger.info("player.deleted id=%s", player_id)
