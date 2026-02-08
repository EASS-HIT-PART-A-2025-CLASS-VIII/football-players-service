# filepath: football_player_service/app/models.py
from enum import Enum
from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field
from pydantic import field_validator, EmailStr

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


class PlayerBase(SQLModel):
    """Shared fields for players."""

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


class Player(PlayerBase, table=True):
    """Database model with auto-generated ID."""

    __tablename__ = "players"

    id: Optional[int] = Field(default=None, primary_key=True)


class PlayerCreate(PlayerBase):
    """Incoming payload with normalization."""

    @field_validator("full_name", "country", "league", "current_team", mode="before")
    @classmethod
    def normalize_fields(cls, v):
        """Normalize strings to title case."""
        if isinstance(v, str):
            return v.title()
        return v


class PlayerResponse(PlayerBase):
    """Response model matching Player but without table config."""

    id: int


class PaginatedPlayers(SQLModel):
    """Paginated response for players list."""

    data: list[Player] = Field(description="List of players on current page")
    total: int = Field(description="Total number of players")
    page: int = Field(description="Current page number (1-indexed)")
    limit: int = Field(description="Items per page")
    pages: int = Field(description="Total number of pages")


# Auth-related models
class UserRole(str, Enum):
    """User roles for access control."""
    ADMIN = "admin"
    USER = "user"


class User(SQLModel, table=True):
    """User database model."""
    
    __tablename__ = "users"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True)
    username: str = Field(unique=True, index=True)
    hashed_password: str
    role: UserRole = Field(default=UserRole.USER)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)

