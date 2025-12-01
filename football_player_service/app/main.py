from __future__ import annotations
import logging
from fastapi import FastAPI, HTTPException, status
from .dependencies import RepositoryDep, SettingsDep
from .models import Player, PlayerCreate

logger = logging.getLogger("football-player-service")
logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

app = FastAPI(
    title="Football Player Service",
    version="0.1.0",
)

@app.get("/health", tags=["diagnostics"])
def health(settings: SettingsDep) -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "ok", "app": settings.app_name}


@app.get("/players", response_model=list[Player], tags=["players"])
def list_players(repository: RepositoryDep) -> list[Player]:
    """Get all players."""
    return list(repository.list())

@app.post(
    "/players",
    response_model=Player,
    status_code=status.HTTP_201_CREATED,
    tags=["players"],
)
def create_player(
    payload: PlayerCreate,
    repository: RepositoryDep,
) -> Player:
    """Create a new player."""
    player = repository.create(payload)
    logger.info(
        "player.created id=%s name=%s status=%s",
        player.id,
        player.full_name,
        player.status,
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
            detail="Player not found",
        )
    return player


@app.put(
    "/players/{player_id}",
    response_model=Player,
    tags=["players"],
)
def update_player(
    player_id: int,
    payload: PlayerCreate,
    repository: RepositoryDep,
) -> Player:
    """Update a player by ID (full replace)."""
    updated = repository.update(player_id, payload)
    if updated is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Player not found",
        )
    logger.info(
        "player.updated id=%s name=%s status=%s",
        updated.id,
        updated.full_name,
        updated.status,
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
            detail="Player not found",
        )
    repository.delete(player_id)
    logger.info("player.deleted id=%s", player_id)
    # 204 → no body
