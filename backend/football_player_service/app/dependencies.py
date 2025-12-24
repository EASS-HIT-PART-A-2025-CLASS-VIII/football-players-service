from typing import Annotated

from fastapi import Depends
from sqlmodel import Session

from .config import Settings
from .database import get_session as get_db_session
from .repository import PlayerRepository


def get_settings() -> Settings:
    """Provide settings to endpoints."""
    return Settings()


def get_repository(session: Session = Depends(get_db_session)) -> PlayerRepository:
    """Provide repository to endpoints."""
    return PlayerRepository(session)


SettingsDep = Annotated[Settings, Depends(get_settings)]
RepositoryDep = Annotated[PlayerRepository, Depends(get_repository)]
