"""
Authentication Utilities
JWT-based auth with password hashing
"""

from datetime import datetime, timedelta
from typing import Optional
import os

from pydantic import BaseModel, EmailStr, Field
from passlib.context import CryptContext
from jose import JWTError, jwt

from .models import UserRole

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


class UserCreate(BaseModel):
    """User registration payload."""
    email: EmailStr
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=8)
    role: Optional[UserRole] = UserRole.USER


class UserResponse(BaseModel):
    """User response (without password)."""
    id: int
    email: str
    username: str
    role: UserRole
    is_active: bool
    created_at: datetime


class Token(BaseModel):
    """JWT token response."""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """JWT token payload data."""
    username: Optional[str] = None
    role: Optional[UserRole] = None


class LoginRequest(BaseModel):
    """Login credentials."""
    username: str
    password: str


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password."""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create JWT access token.
    
    Args:
        data: Payload data (should include 'sub' for username)
        expires_delta: Custom expiration time
    
    Returns:
        str: Encoded JWT token
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    return encoded_jwt


def decode_access_token(token: str) -> Optional[TokenData]:
    """
    Decode and validate JWT token.
    
    Args:
        token: JWT token string
    
    Returns:
        TokenData if valid, None otherwise
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        role: str = payload.get("role")
        
        if username is None:
            return None
        
        return TokenData(username=username, role=UserRole(role) if role else None)
    except JWTError:
        return None
