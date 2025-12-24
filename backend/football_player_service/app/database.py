# filepath: football_player_service/app/database.py
import os
from sqlalchemy import create_engine
from sqlmodel import SQLModel, Session

# Get database URL from environment or use local SQLite
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./football_players.db",  # Local development
)

# For Render PostgreSQL, the URL starts with "postgresql://"
# Render provides it as DATABASE_URL env var
if DATABASE_URL.startswith("postgresql://"):
    # PostgreSQL requires psycopg2
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+psycopg2://")

engine = create_engine(
    DATABASE_URL,
    echo=False,  # Set to True for SQL logging
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {},
)


def init_db():
    """Create all tables."""
    SQLModel.metadata.create_all(engine)


def get_session():
    """Get database session for dependency injection."""
    with Session(engine) as session:
        yield session
