"""
Data loading script to populate the database with players from CSV files.

This script:
1. Reads players.csv (sampling 200 random players)
2. Reads competitions.csv to map league names
3. Inserts players into the database (SQLite or PostgreSQL)

Usage:
    python load_data.py [--reset] [--limit 200]

Options:
    --reset: Clear existing players before loading (optional)
    --limit: Number of random players to load (default: 200)
"""

import csv
import os
import sys
from datetime import datetime
from pathlib import Path
import random
from typing import Optional

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlmodel import Session, select
from sqlalchemy import create_engine

# Import models
from football_player_service.app.models import Player, PlayingStatus
from football_player_service.app.database import DATABASE_URL


def get_competition_map() -> dict[str, str]:
    """Load competition codes to league names from competitions.csv."""
    competition_map = {}
    csv_path = Path(__file__).parent / "rawData" / "competitions.csv"
    
    if not csv_path.exists():
        print(f"⚠️  competitions.csv not found at {csv_path}")
        return competition_map
    
    try:
        with open(csv_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                comp_id = row.get("competition_id")
                name = row.get("name")
                if comp_id and name:
                    competition_map[comp_id] = name.title()
    except Exception as e:
        print(f"❌ Error reading competitions.csv: {e}")
    
    return competition_map


def calculate_age(date_of_birth_str: str) -> int:
    """Calculate age from date of birth string (YYYY-MM-DD format)."""
    try:
        if not date_of_birth_str:
            return 25  # Default age if missing
        
        dob = datetime.strptime(date_of_birth_str.split()[0], "%Y-%m-%d")
        today = datetime.now()
        age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
        return max(0, min(age, 120))  # Clamp between 0-120
    except Exception:
        return 25


def determine_status(last_season: str) -> PlayingStatus:
    """Determine player status based on last_season."""
    try:
        if not last_season:
            return PlayingStatus.ACTIVE
        
        last_season_year = int(last_season)
        current_year = datetime.now().year
        
        # If last season is more than 5 years ago, consider retired
        if current_year - last_season_year > 5:
            return PlayingStatus.RETIRED
        
        return PlayingStatus.ACTIVE
    except Exception:
        return PlayingStatus.ACTIVE


def parse_market_value(market_value_str: str) -> Optional[int]:
    """Parse market value string (e.g., '1000000' or '30000000') to integer."""
    try:
        if not market_value_str or market_value_str.strip() == "":
            return None
        
        # Handle currency symbols and abbreviations if present
        value_str = market_value_str.strip().replace("€", "").replace("$", "").replace("m", "000000").strip()
        
        # Try to convert to int
        value = int(float(value_str))
        
        # Validate within bounds
        if 0 <= value <= 10_000_000_000:
            return value
        return None
    except Exception:
        return None


def load_players(limit: int = 200, reset: bool = False) -> None:
    """Load players from CSV into database."""
    
    csv_path = Path(__file__).parent / "rawData" / "players.csv"
    
    if not csv_path.exists():
        print(f"❌ players.csv not found at {csv_path}")
        return
    
    # Load competition map for league names
    print("📚 Loading competition mappings...")
    competition_map = get_competition_map()
    print(f"   ✓ Loaded {len(competition_map)} competitions")
    
    # Set up database connection
    db_url = os.getenv("DATABASE_URL", "sqlite:///./football_players.db")
    
    # Handle PostgreSQL URL format
    if db_url.startswith("postgresql://"):
        db_url = db_url.replace("postgresql://", "postgresql+psycopg2://")
    
    print(f"\n🗄️  Database: {db_url.split('@')[-1] if '@' in db_url else db_url[:50]}...")
    
    try:
        engine = create_engine(
            db_url,
            connect_args={"check_same_thread": False} if "sqlite" in db_url else {},
        )
        
        # Create tables
        from football_player_service.app.models import SQLModel
        SQLModel.metadata.create_all(engine)
        
        with Session(engine) as session:
            # Reset if requested
            if reset:
                print("🗑️  Clearing existing players...")
                session.exec(select(Player).limit(None))  # Execute the delete
                from sqlalchemy import delete
                session.execute(delete(Player))
                session.commit()
            
            # Read all players from CSV
            print(f"\n📖 Reading players.csv...")
            all_players = []
            
            with open(csv_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    all_players.append(row)
            
            print(f"   Total players in CSV: {len(all_players)}")
            
            # Sample random players
            if len(all_players) > limit:
                players_to_load = random.sample(all_players, limit)
                print(f"   📊 Sampling {limit} random players")
            else:
                players_to_load = all_players
                print(f"   Using all {len(all_players)} players")
            
            # Insert players
            print(f"\n💾 Inserting players into database...")
            inserted = 0
            skipped = 0
            
            for row in players_to_load:
                try:
                    # Extract and clean data
                    first_name = (row.get("first_name") or "").strip().title()
                    last_name = (row.get("last_name") or "").strip().title()
                    full_name = f"{first_name} {last_name}".strip()
                    
                    # Use 'name' field if first/last name is empty
                    if not full_name or len(full_name) < 2:
                        full_name = (row.get("name") or "Unknown").strip().title()
                    
                    # Validate full_name length
                    if not full_name or len(full_name) < 2 or len(full_name) > 100:
                        skipped += 1
                        continue
                    
                    country = (row.get("country_of_citizenship") or "").strip().title()
                    if not country or len(country) < 2 or len(country) > 50:
                        country = "Unknown"
                    
                    current_team = (row.get("current_club_name") or "").strip().title()
                    if len(current_team) > 100:
                        current_team = current_team[:100]
                    
                    # Get league from competition map
                    league_id = row.get("current_club_domestic_competition_id", "").strip()
                    league = competition_map.get(league_id, "").title()
                    if league and len(league) > 100:
                        league = league[:100]
                    
                    # Calculate age from date of birth
                    dob = row.get("date_of_birth", "").strip()
                    age = calculate_age(dob)
                    
                    # Parse market value
                    market_value = parse_market_value(row.get("market_value_in_eur", ""))
                    
                    # Determine status
                    last_season = row.get("last_season", "").strip()
                    status = determine_status(last_season)
                    
                    # Create player instance
                    player = Player(
                        full_name=full_name,
                        country=country,
                        status=status,
                        current_team=current_team if current_team else None,
                        league=league if league else None,
                        market_value=market_value,
                        age=age,
                    )
                    
                    session.add(player)
                    inserted += 1
                    
                    # Progress indicator
                    if inserted % 50 == 0:
                        print(f"   {inserted} players processed...")
                
                except Exception as e:
                    print(f"   ⚠️  Error processing player {row.get('name', 'Unknown')}: {e}")
                    skipped += 1
                    continue
            
            # Commit all changes
            session.commit()
            
            print(f"\n✅ Data loading complete!")
            print(f"   ✓ Inserted: {inserted} players")
            print(f"   ⚠️  Skipped: {skipped} players")
            
            # Verify count
            from sqlalchemy import func
            total = session.exec(select(func.count(Player.id))).one()
            print(f"   📊 Total players in database: {total}")
    
    except Exception as e:
        print(f"❌ Database error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Load player data from CSV into database")
    parser.add_argument("--reset", action="store_true", help="Clear existing players before loading")
    parser.add_argument("--limit", type=int, default=200, help="Number of random players to load (default: 200)")
    
    args = parser.parse_args()
    
    print("🚀 Football Player Data Loader")
    print("=" * 50)
    
    load_players(limit=args.limit, reset=args.reset)
