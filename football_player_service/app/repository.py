# filepath: football_player_service/app/repository.py
from __future__ import annotations

from typing import Dict, List

from .models import Player, PlayerCreate


class PlayerRepository:
    """In-memory storage for football players.

    You can swap in SQLModel + SQLite later without changing the
    interface (list/create/get/update/delete), so routes stay the same.
    """

    def __init__(self) -> None:
        self._items: Dict[int, Player] = {}
        self._next_id = 1

    def list(self) -> List[Player]:
        """Get all players."""
        return list(self._items.values())

    def create(self, payload: PlayerCreate) -> Player:
        """Add a new player and return it with assigned ID."""
        player = Player(id=self._next_id, **payload.model_dump())
        self._items[player.id] = player
        self._next_id += 1
        return player

    def get(self, player_id: int) -> Player | None:
        """Get a player by ID, or None if not found."""
        return self._items.get(player_id)

    def update(self, player_id: int, payload: PlayerCreate) -> Player | None:
        """Replace an existing player. Returns updated player or None if not found."""
        existing = self._items.get(player_id)
        if existing is None:
            return None

        updated = Player(id=player_id, **payload.model_dump())
        self._items[player_id] = updated
        return updated

    def delete(self, player_id: int) -> None:
        """Remove a player by ID (no-op if it doesn't exist)."""
        self._items.pop(player_id, None)

    def clear(self) -> None:
        """Remove all players (useful for tests)."""
        self._items.clear()
        self._next_id = 1
