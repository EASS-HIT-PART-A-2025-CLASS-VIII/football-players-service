from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import Session

from .config import Settings
from .database import get_session as get_db_session
from .repository import PlayerRepository, UserRepository
from .auth import decode_access_token, TokenData
from .models import User, UserRole


def get_settings() -> Settings:
    """Provide settings to endpoints."""
    return Settings()


def get_repository(session: Session = Depends(get_db_session)) -> PlayerRepository:
    """Provide repository to endpoints."""
    return PlayerRepository(session)


def get_user_repository(session: Session = Depends(get_db_session)) -> UserRepository:
    """Provide user repository to endpoints."""
    return UserRepository(session)


# OAuth2 scheme for JWT token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login", auto_error=False)


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    user_repo: UserRepository = Depends(get_user_repository)
) -> User:
    """
    Get current authenticated user from JWT token.
    
    Raises:
        HTTPException: If token is invalid or user not found
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    if not token:
        raise credentials_exception
    
    token_data: TokenData = decode_access_token(token)
    if token_data is None or token_data.username is None:
        raise credentials_exception
    
    user = user_repo.get_by_username(username=token_data.username)
    if user is None:
        raise credentials_exception
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is inactive"
        )
    
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Get current active user (convenience dependency)."""
    return current_user


async def require_admin(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Require admin role.
    
    Raises:
        HTTPException: If user is not admin
    """
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    return current_user


# Type annotations for dependency injection
SettingsDep = Annotated[Settings, Depends(get_settings)]
RepositoryDep = Annotated[PlayerRepository, Depends(get_repository)]
UserRepositoryDep = Annotated[UserRepository, Depends(get_user_repository)]
CurrentUserDep = Annotated[User, Depends(get_current_active_user)]
AdminUserDep = Annotated[User, Depends(require_admin)]

