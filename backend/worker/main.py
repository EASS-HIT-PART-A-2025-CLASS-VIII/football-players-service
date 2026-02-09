import os
import requests
import sys
import json
from celery import Celery
from sqlmodel import Session, select
import redis

# Adjust path to allow importing from sibling directory
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from football_player_service.app.models import Player
from football_player_service.app.database import engine

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
AI_SERVICE_URL = os.getenv("AI_SERVICE_URL", "http://ai-service:8000")

celery_app = Celery("ai_scout", broker=REDIS_URL, backend=REDIS_URL)
redis_client = redis.from_url(REDIS_URL, decode_responses=True)

@celery_app.task(name="ai_scout.generate_report", bind=True)
def generate_report(self, player_id: int):
    task_id = self.request.id
    print(f"Processing report for player {player_id} (task: {task_id})")
    
    # Update status to running
    task_data = {
        "task_id": task_id,
        "status": "running",
        "result": None,
        "error": None,
        "created_at": None
    }
    redis_client.setex(f"task:{task_id}", 3600, json.dumps(task_data))
    
    with Session(engine) as session:
        player = session.get(Player, player_id)
        if not player:
            error_msg = f"Player {player_id} not found"
            print(error_msg)
            # Update status to failed
            task_data["status"] = "failed"
            task_data["error"] = error_msg
            redis_client.setex(f"task:{task_id}", 3600, json.dumps(task_data))
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
            
            # Update status to completed
            task_data["status"] = "completed"
            task_data["result"] = f"Report generated for {player.full_name}"
            redis_client.setex(f"task:{task_id}", 3600, json.dumps(task_data))
            
        except Exception as e:
            error_msg = f"Error generating report: {e}"
            print(error_msg)
            # Update status to failed
            task_data["status"] = "failed"
            task_data["error"] = error_msg
            redis_client.setex(f"task:{task_id}", 3600, json.dumps(task_data))
            # Could implement retry logic here using self.retry()
            raise
