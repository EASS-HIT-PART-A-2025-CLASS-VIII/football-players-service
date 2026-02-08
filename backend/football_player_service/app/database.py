# filepath: football_player_service/app/database.py
import os
import logging
from sqlalchemy import create_engine
from sqlmodel import SQLModel, Session, select

logger = logging.getLogger("football-player-service")

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
    """Create all tables and seed initial data."""
    from .models import User, UserRole
    from .auth import get_password_hash
    
    # Create tables
    SQLModel.metadata.create_all(engine)
    
    # Seed admin user if not exists
    with Session(engine) as session:
        admin_username = "admin"
        existing_admin = session.exec(
            select(User).where(User.username == admin_username)
        ).first()
        
        if not existing_admin:
            admin_user = User(
                email="admin@football.com",
                username=admin_username,
                hashed_password=get_password_hash("admin123"),  # Change in production!
                role=UserRole.ADMIN,
                is_active=True
            )
            session.add(admin_user)
            session.commit()
            logger.info("✓ Seeded admin user: username='admin', password='admin123'")
        else:
            logger.info("✓ Admin user already exists")


def get_session():
    """Get database session for dependency injection."""
    with Session(engine) as session:
        yield session

