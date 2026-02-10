# filepath: football_player_service/app/repository.py
from typing import List, Optional
from sqlmodel import Session, select, func, col
from .models import Player, PlayerCreate, PlayingStatus


class PlayerRepository:
    """Database repository using SQLModel."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def list(
        self,
        name: Optional[str] = None,
        min_price: Optional[int] = None,
        max_price: Optional[int] = None,
        country: Optional[str] = None,
        club: Optional[str] = None,
        league: Optional[str] = None,
        status: Optional[PlayingStatus] = None,
    ) -> List[Player]:
        """Get all players with optional filtering."""
        query = select(Player)
        
        # Apply filters
        if name:
            query = query.where(col(Player.full_name).ilike(f"%{name}%"))
        if country:
            query = query.where(func.lower(Player.country) == country.lower())
        if club:
            query = query.where(func.lower(Player.current_team) == club.lower())
        if league:
            query = query.where(func.lower(Player.league) == league.lower())
        if status:
            query = query.where(Player.status == status)
        if min_price is not None:
            query = query.where(Player.market_value >= min_price)
        if max_price is not None:
            query = query.where(Player.market_value <= max_price)
        
        query = query.order_by(Player.id)
        return self.session.exec(query).all()

    def count(
        self,
        name: Optional[str] = None,
        min_price: Optional[int] = None,
        max_price: Optional[int] = None,
        country: Optional[str] = None,
        club: Optional[str] = None,
        league: Optional[str] = None,
        status: Optional[PlayingStatus] = None,
    ) -> int:
        """Get total count of players with optional filtering."""
        query = select(func.count(Player.id))
        
        # Apply same filters as list()
        if name:
            query = query.where(col(Player.full_name).ilike(f"%{name}%"))
        if country:
            query = query.where(func.lower(Player.country) == country.lower())
        if club:
            query = query.where(func.lower(Player.current_team) == club.lower())
        if league:
            query = query.where(func.lower(Player.league) == league.lower())
        if status:
            query = query.where(Player.status == status)
        if min_price is not None:
            query = query.where(Player.market_value >= min_price)
        if max_price is not None:
            query = query.where(Player.market_value <= max_price)
        
        return self.session.exec(query).one()
    
    def get_filter_options(self) -> dict:
        """Get distinct values for filter dropdowns."""
        countries = self.session.exec(
            select(Player.country).distinct().where(Player.country.is_not(None))
        ).all()
        
        clubs = self.session.exec(
            select(Player.current_team).distinct().where(Player.current_team.is_not(None))
        ).all()
        
        leagues = self.session.exec(
            select(Player.league).distinct().where(Player.league.is_not(None))
        ).all()
        
        statuses = [status.value for status in PlayingStatus]
        
        return {
            "countries": sorted(countries),
            "clubs": sorted(clubs),
            "leagues": sorted(leagues),
            "statuses": statuses,
        }

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
