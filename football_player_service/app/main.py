import logging
from typing import List
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from .dependencies import RepositoryDep, SettingsDep
from .models import Player, PlayerCreate

logger = logging.getLogger("football-player-service")
logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

# Initialize rate limiter (100 requests per minute per IP)
limiter = Limiter(key_func=get_remote_address)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event handler for startup and shutdown."""
    # Startup
    logger.info("=" * 60)
    logger.info("⚽ Football Player Service v0.2.0")
    logger.info("=" * 60)
    logger.info("Features:")
    logger.info("  ✓ Rate limiting: 100 req/min per IP")
    logger.info("  ✓ Security headers: X-Frame-Options, HSTS, etc.")
    logger.info("  ✓ CORS: Enabled (configure for production)")
    logger.info("  ✓ Health check: /health endpoint")
    logger.info("  ✓ API Documentation: /docs (Swagger UI)")
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
    version="0.2.0",
    description="CRUD API for managing football players with validation, rate limiting, and security.",
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


@app.get("/players", response_model=List[Player], tags=["players"])
def list_players(repository: RepositoryDep) -> List[Player]:
    """Get all players."""
    return list(repository.list())


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
