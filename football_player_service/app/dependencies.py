from collections.abc import Generator
from typing import Annotated

from fastapi import Depends

from .config import Settings
from .repository import PlayerRepository

_settings = Settings()
_repository = PlayerRepository()

def get_settings() -> Settings:
    """Provide settings to endpoints."""
    return _settings


def get_repository() -> Generator[PlayerRepository, None, None]:
    """Provide repository to endpoints."""
    yield _repository

SettingsDep = Annotated[Settings, Depends(get_settings)]
RepositoryDep = Annotated[PlayerRepository, Depends(get_repository)]