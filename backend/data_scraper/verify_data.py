import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlmodel import Session, select
from sqlalchemy import create_engine, func
from football_player_service.app.models import Player

engine = create_engine('sqlite:///football_players.db')
with Session(engine) as session:
    # Get stats
    total = session.exec(select(func.count(Player.id))).one()
    print(f"\n✅ Total Players: {total}\n")
    
    # Show samples
    players = session.exec(select(Player).limit(3)).all()
    print("Sample Players:")
    print("-" * 80)
    for p in players:
        print(f"ID: {p.id} | Name: {p.full_name}")
        print(f"  Country: {p.country} | Age: {p.age} | Status: {p.status}")
        print(f"  Team: {p.current_team} | League: {p.league}")
        print(f"  Market Value: ${p.market_value:,}" if p.market_value else "  Market Value: N/A")
        print()
