# filepath: football_player_service/app/repository.py
from typing import List, Optional
from sqlmodel import Session, select, func
from .models import Player, PlayerCreate, User, UserRole


class PlayerRepository:
    """Database repository using SQLModel."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def list(self) -> List[Player]:
        """Get all players."""
        return self.session.exec(select(Player)).all()

    def count(self) -> int:
        """Get total count of players."""
        return self.session.exec(select(func.count(Player.id))).one()

    def create(self, payload: PlayerCreate) -> Player:
        """Add a new player."""
        player = Player(**payload.model_dump())
        self.session.add(player)
        self.session.commit()
        self.session.refresh(player)
        return player

    def get(self, player_id: int) -> Optional[Player]:
        """Get a player by ID."""
        return self.session.get(Player, player_id)

    def update(self, player_id: int, payload: PlayerCreate) -> Optional[Player]:
        """Update a player."""
        player = self.session.get(Player, player_id)
        if not player:
            return None

        player_data = payload.model_dump(exclude_unset=True)
        for key, value in player_data.items():
            setattr(player, key, value)

        self.session.add(player)
        self.session.commit()
        self.session.refresh(player)
        return player

    def delete(self, player_id: int) -> None:
        """Delete a player."""
        player = self.session.get(Player, player_id)
        if player:
            self.session.delete(player)
            self.session.commit()


class UserRepository:
    """User repository for authentication."""
    
    def __init__(self, session: Session) -> None:
        self.session = session
    
    def create(self, email: str, username: str, hashed_password: str, role: UserRole = UserRole.USER) -> User:
        """Create a new user."""
        user = User(
            email=email,
            username=username,
            hashed_password=hashed_password,
            role=role
        )
        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)
        return user
    
    def get_by_username(self, username: str) -> Optional[User]:
        """Get user by username."""
        statement = select(User).where(User.username == username)
        return self.session.exec(statement).first()
    
    def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        statement = select(User).where(User.email == email)
        return self.session.exec(statement).first()
    
    def get(self, user_id: int) -> Optional[User]:
        """Get user by ID."""
        return self.session.get(User, user_id)

