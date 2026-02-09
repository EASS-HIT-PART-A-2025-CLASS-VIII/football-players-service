#!/usr/bin/env python3
"""
Lightweight database seeding script for Football Player Service

This script provides minimal sample data that gets loaded automatically during
Docker container startup, ensuring the lecturer sees a working system immediately
after 'docker compose up --build'.

Key features:
- Runs automatically during container startup (via entrypoint.sh)
- Creates ~20 sample players (lightweight, fast)
- Only seeds if database is empty (idempotent)
- No external CSV dependencies (data is embedded)
- Fallback for when CSV files are not available

Usage:
    python backend/scripts/seed_data.py
"""

import os
import sys
from pathlib import Path
from typing import List, Dict

# Add backend to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlmodel import Session, select
from sqlalchemy import create_engine, func

from football_player_service.app.models import Player, PlayingStatus, SQLModel


# Embedded sample data (lightweight, no external dependencies)
SAMPLE_PLAYERS = [
    {
        "full_name": "Lionel Messi",
        "country": "Argentina",
        "status": PlayingStatus.ACTIVE,
        "current_team": "Inter Miami CF",
        "league": "Major League Soccer",
        "age": 37,
        "market_value": 15000000,
    },
    {
        "full_name": "Cristiano Ronaldo",
        "country": "Portugal", 
        "status": PlayingStatus.ACTIVE,
        "current_team": "Al Nassr FC",
        "league": "Saudi Pro League",
        "age": 39,
        "market_value": 25000000,
    },
    {
        "full_name": "Kylian Mbappé",
        "country": "France",
        "status": PlayingStatus.ACTIVE,
        "current_team": "Real Madrid CF",
        "league": "La Liga",
        "age": 25,
        "market_value": 180000000,
    },
    {
        "full_name": "Erling Haaland",
        "country": "Norway",
        "status": PlayingStatus.ACTIVE,
        "current_team": "Manchester City FC",
        "league": "Premier League",
        "age": 24,
        "market_value": 170000000,
    },
    {
        "full_name": "Kevin De Bruyne",
        "country": "Belgium",
        "status": PlayingStatus.ACTIVE,
        "current_team": "Manchester City FC", 
        "league": "Premier League",
        "age": 33,
        "market_value": 80000000,
    },
    {
        "full_name": "Pedri González",
        "country": "Spain",
        "status": PlayingStatus.ACTIVE,
        "current_team": "FC Barcelona",
        "league": "La Liga",
        "age": 22,
        "market_value": 80000000,
    },
    {
        "full_name": "Vinicius Junior",
        "country": "Brazil", 
        "status": PlayingStatus.ACTIVE,
        "current_team": "Real Madrid CF",
        "league": "La Liga",
        "age": 24,
        "market_value": 120000000,
    },
    {
        "full_name": "Robert Lewandowski",
        "country": "Poland",
        "status": PlayingStatus.ACTIVE,
        "current_team": "FC Barcelona",
        "league": "La Liga", 
        "age": 36,
        "market_value": 25000000,
    },
    {
        "full_name": "Mohamed Salah",
        "country": "Egypt",
        "status": PlayingStatus.ACTIVE,
        "current_team": "Liverpool FC",
        "league": "Premier League",
        "age": 32,
        "market_value": 65000000,
    },
    {
        "full_name": "Sadio Mané",
        "country": "Senegal",
        "status": PlayingStatus.ACTIVE,
        "current_team": "Al Nassr FC",
        "league": "Saudi Pro League",
        "age": 32,
        "market_value": 25000000,
    },
    {
        "full_name": "Luka Modrić",
        "country": "Croatia",
        "status": PlayingStatus.ACTIVE,
        "current_team": "Real Madrid CF",
        "league": "La Liga",
        "age": 39,
        "market_value": 10000000,
    },
    {
        "full_name": "Neymar Jr",
        "country": "Brazil",
        "status": PlayingStatus.FREE_AGENT,
        "current_team": "Al Hilal SFC",
        "league": "Saudi Pro League", 
        "age": 32,
        "market_value": 60000000,
    },
    {
        "full_name": "Harry Kane",
        "country": "England",
        "status": PlayingStatus.ACTIVE,
        "current_team": "FC Bayern Munich",
        "league": "Bundesliga",
        "age": 31,
        "market_value": 90000000,
    },
    {
        "full_name": "Jamal Musiala",
        "country": "Germany",
        "status": PlayingStatus.ACTIVE,
        "current_team": "FC Bayern Munich",
        "league": "Bundesliga",
        "age": 21,
        "market_value": 110000000,
    },
    {
        "full_name": "Jude Bellingham", 
        "country": "England",
        "status": PlayingStatus.ACTIVE,
        "current_team": "Real Madrid CF",
        "league": "La Liga",
        "age": 21,
        "market_value": 150000000,
    },
    {
        "full_name": "Gianluigi Donnarumma",
        "country": "Italy",
        "status": PlayingStatus.ACTIVE,
        "current_team": "Paris Saint-Germain FC",
        "league": "Ligue 1",
        "age": 25,
        "market_value": 60000000,
    },
    {
        "full_name": "Thierry Henry",
        "country": "France",
        "status": PlayingStatus.RETIRED,
        "current_team": None,
        "league": None,
        "age": 47,
        "market_value": None,
    },
    {
        "full_name": "Ronaldinho Gaúcho",
        "country": "Brazil", 
        "status": PlayingStatus.RETIRED,
        "current_team": None,
        "league": None,
        "age": 44,
        "market_value": None,
    },
    {
        "full_name": "Zlatan Ibrahimović",
        "country": "Sweden",
        "status": PlayingStatus.RETIRED,
        "current_team": None,
        "league": None,
        "age": 43,
        "market_value": None,
    },
    {
        "full_name": "Andrea Pirlo",
        "country": "Italy",
        "status": PlayingStatus.RETIRED,
        "current_team": None,
        "league": None,
        "age": 45,
        "market_value": None,
    }
]


def is_database_empty() -> bool:
    """Check if database has any players (excluding admin user)."""
    try:
        db_url = os.getenv("DATABASE_URL", "sqlite:///./football_players.db")
        
        # Handle PostgreSQL URL format
        if db_url.startswith("postgresql://"):
            db_url = db_url.replace("postgresql://", "postgresql+psycopg2://")
        
        engine = create_engine(
            db_url,
            connect_args={"check_same_thread": False} if "sqlite" in db_url else {},
        )
        
        with Session(engine) as session:
            count = session.exec(select(func.count(Player.id))).one()
            return count == 0
            
    except Exception as e:
        print(f"⚠️  Error checking database: {e}")
        return True  # Assume empty if error


def seed_database() -> None:
    """Seed database with sample players if empty."""
    
    if not is_database_empty():
        print("✅ Database already contains players - skipping seed")
        return
    
    print("🌱 Seeding database with sample players...")
    
    try:
        db_url = os.getenv("DATABASE_URL", "sqlite:///./football_players.db")
        
        # Handle PostgreSQL URL format
        if db_url.startswith("postgresql://"):
            db_url = db_url.replace("postgresql://", "postgresql+psycopg2://")
            
        engine = create_engine(
            db_url,
            connect_args={"check_same_thread": False} if "sqlite" in db_url else {},
        )
        
        # Ensure tables exist
        SQLModel.metadata.create_all(engine)
        
        with Session(engine) as session:
            inserted = 0
            
            for player_data in SAMPLE_PLAYERS:
                try:
                    player = Player(**player_data)
                    session.add(player)
                    inserted += 1
                except Exception as e:
                    print(f"   ⚠️  Error creating {player_data['full_name']}: {e}")
                    continue
            
            session.commit()
            
            print(f"✅ Seeded {inserted} players successfully!")
            print("   Notable players include: Messi, Ronaldo, Mbappé, Haaland...")
            print("   Mix of active/retired/free-agent statuses for testing")
            
    except Exception as e:
        print(f"❌ Seeding failed: {e}")
        sys.exit(1)


def main():
    """Main entry point."""
    print("🚀 Football Player Service - Database Seeder")
    print("=" * 50)
    
    seed_database()
    
    print("\n📊 Database is ready!")
    print("   • Admin user: admin/admin123 (for authentication)")  
    print("   • Sample players available for testing")
    print("   • Ready for AI scout demos and frontend browsing")


if __name__ == "__main__":
    main()