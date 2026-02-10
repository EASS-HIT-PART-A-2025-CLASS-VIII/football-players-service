import os
import ssl
import time
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
from celery import Celery
from sqlmodel import Session
from football_player_service.app.database import engine
from football_player_service.app.repository import PlayerRepository
from football_player_service.app.models import Player


try:
    from google import genai
    HAS_GEMINI = True
except ImportError:
    HAS_GEMINI = False

_raw_redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
_parsed = urlparse(_raw_redis_url)
_params = parse_qs(_parsed.query)
_params.pop("ssl_cert_reqs", None)
REDIS_URL = urlunparse(_parsed._replace(query=urlencode(_params, doseq=True)))

celery_app = Celery("ai_scout", broker=REDIS_URL, backend=REDIS_URL)
if REDIS_URL.startswith("rediss://"):
    _ssl_opts = {"ssl_cert_reqs": ssl.CERT_NONE}
    celery_app.conf.broker_use_ssl = _ssl_opts
    celery_app.conf.redis_backend_use_ssl = _ssl_opts

@celery_app.task(name="ai_scout.generate_report")
def generate_report(player_id: int):
    with Session(engine) as session:
        repo = PlayerRepository(session)
        player = repo.get(player_id)
        if not player:
            print(f"Player {player_id} not found.")
            return
        prompt = f"Generate a detailed football scouting report for the following player: Name: {player.full_name}, Country: {player.country}, Age: {player.age}, Status: {player.status}, Team: {player.current_team}, League: {player.league}, Market Value: {player.market_value}."
        api_key = os.getenv("GEMINI_API_KEY")
        if HAS_GEMINI and api_key:
            try:
                client = genai.Client(api_key=api_key)
                response = client.models.generate_content(
                    model="gemini-3-flash-preview",
                    contents=prompt
                )
                report = response.text
            except Exception as e:
                report = f"[Gemini API error: {e}]"
        else:
            # Mock response if Gemini not available
            report = f"[MOCK REPORT] Scouting report for {player.full_name} (ID: {player_id}) generated."
        player.scouting_report = report
        session.add(player)
        session.commit()
        print(f"Scouting report updated for player {player_id}.")
