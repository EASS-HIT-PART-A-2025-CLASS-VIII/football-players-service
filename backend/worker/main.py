import os
import requests
import sys
from celery import Celery
from sqlmodel import Session, select

# Adjust path to allow importing from sibling directory
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from football_player_service.app.models import Player
from football_player_service.app.database import engine

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
AI_SERVICE_URL = os.getenv("AI_SERVICE_URL", "http://ai-service:8000")

celery_app = Celery("ai_scout", broker=REDIS_URL, backend=REDIS_URL)

@celery_app.task(name="ai_scout.generate_report")
def generate_report(player_id: int):
    print(f"Processing report for player {player_id}")
    with Session(engine) as session:
        player = session.get(Player, player_id)
        if not player:
            print(f"Player {player_id} not found")
            return

        payload = {
            "player_name": player.full_name,
            "position": "Football Player", # Default since model lacks position
            "age": player.age,
            "stats": {
                "market_value": player.market_value,
                "country": player.country,
                "league": player.league,
                "team": player.current_team,
                "status": player.status.value
            }
        }
        
        try:
            resp = requests.post(f"{AI_SERVICE_URL}/generate", json=payload)
            resp.raise_for_status()
            data = resp.json()
            report = data.get("report")
            
            player.scouting_report = report
            session.add(player)
            session.commit()
            print(f"Report generated for {player.full_name}")
        except Exception as e:
            print(f"Error generating report: {e}")
            # Could implement retry logic here using self.retry()
