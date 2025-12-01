# filepath: football_player_service/app/models.py
from __future__ import annotations
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field, model_validator

class PlayingStatus(str, Enum):
    ACTIVE = "active"
    RETIRED = "retired"
    FREE_AGENT = "free_agent"

class PlayerBase(BaseModel):
    """Shared fields for both creating and returning players.

    This model stays stable even when the persistence layer changes.
    """
    full_name: str = Field(min_length=2)
    country: str = Field(min_length=2)
    status: PlayingStatus
    current_team: Optional[str] = None
    league: Optional[str] = None

class Player(PlayerBase):
    """Response model including server-generated ID.

    When migrating to SQLModel, we will add `table=True`
    while keeping the HTTP contract unchanged.
    """
    id: int

class PlayerCreate(PlayerBase):
    """Incoming payload with validation + normalization rules."""

    @model_validator(mode="after")
    def normalize_fields(self) -> "PlayerCreate":
        """Normalize strings for consistency.

        Examples:
            - full_name: "lionel messi" → "Lionel Messi"
            - country: "argentina" → "Argentina"
            - league: "premier league" → "Premier League"
            - current_team: "manchester city" → "Manchester City"
        """

        if self.full_name:
            self.full_name = self.full_name.title()

        if self.country:
            self.country = self.country.title()

        if self.league:
            self.league = self.league.title()

        if self.current_team:
            self.current_team = self.current_team.title()

        return self
