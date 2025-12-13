# filepath: football_player_service/app/models.py
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field, model_validator

# Validation constants
MIN_FULL_NAME_LENGTH = 2
MAX_FULL_NAME_LENGTH = 100
MIN_COUNTRY_LENGTH = 2
MAX_COUNTRY_LENGTH = 50
MIN_AGE = 0
MAX_AGE = 120
MIN_MARKET_VALUE = 0
MAX_MARKET_VALUE = 10_000_000_000  # 10 billion USD


class PlayingStatus(str, Enum):
    ACTIVE = "active"
    RETIRED = "retired"
    FREE_AGENT = "free_agent"


class PlayerBase(BaseModel):
    """Shared fields for both creating and returning players.

    This model stays stable even when the persistence layer changes.
    """

    full_name: str = Field(
        min_length=MIN_FULL_NAME_LENGTH,
        max_length=MAX_FULL_NAME_LENGTH,
        description="Player's full name (2-100 characters)",
    )
    country: str = Field(
        min_length=MIN_COUNTRY_LENGTH,
        max_length=MAX_COUNTRY_LENGTH,
        description="Player's country of origin (2-50 characters)",
    )
    status: PlayingStatus = Field(
        description="Player's current playing status (active, retired, free_agent)"
    )
    current_team: Optional[str] = Field(
        None,
        max_length=100,
        description="Current team name (optional)",
    )
    league: Optional[str] = Field(
        None,
        max_length=100,
        description="Current league name (optional)",
    )
    market_value: Optional[int] = Field(
        None,
        ge=MIN_MARKET_VALUE,
        le=MAX_MARKET_VALUE,
        description="Market value in USD (optional, non-negative)",
    )
    age: int = Field(
        ...,
        ge=MIN_AGE,
        le=MAX_AGE,
        description="Player's age in years (0-120)",
    )


class Player(PlayerBase):
    """Response model including server-generated ID.

    When migrating to SQLModel, we will add `table=True`
    while keeping the HTTP contract unchanged.
    """

    id: int = Field(description="Unique player identifier (auto-generated)")


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
