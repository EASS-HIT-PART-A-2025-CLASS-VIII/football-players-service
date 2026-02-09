import asyncio
import os
import random
import logging
from typing import List

import anyio
import redis.asyncio as redis
from sqlmodel import Session, select
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log
)
from football_player_service.app.database import engine
from football_player_service.app.models import Player

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("refresher")

# Redis for idempotency
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=10),
    retry=retry_if_exception_type(Exception),
    before_sleep=before_sleep_log(logger, logging.WARNING)
)
async def refresh_player(player: Player, redis_client: redis.Redis):
    """Simulate a refresh operation with idempotency and exponential backoff retries."""
    lock_key = f"refresh_lock:{player.id}"
    
    # Check if already processed recently (Idempotency)
    if await redis_client.get(f"refreshed:{player.id}"):
        logger.info(f"Skipping Player {player.id} (Recently Refreshed)")
        return

    # Simulate network call with potential failure
    if random.random() < 0.2:
        logger.warning(f"Simulated Network Error for Player {player.id} - Retrying...")
        raise Exception("Simulated Network Error")
    
    # Update something trivial
    logger.info(f"Refreshing Player {player.id}: {player.full_name}")
    await asyncio.sleep(0.5)  # Simulate latency
    
    # Mark as refreshed for 1 minute
    await redis_client.setex(f"refreshed:{player.id}", 60, "1")

async def worker(queue: asyncio.Queue, redis_client: redis.Redis):
    while True:
        player = await queue.get()
        try:
            await refresh_player(player, redis_client)
        except Exception as e:
            # After 3 retries from @retry decorator, log final failure
            logger.error(f"Final failure for Player {player.id} after retries: {e}")
        finally:
            queue.task_done()

async def main():
    logger.info("Starting Async Refresh Job")
    
    r = redis.from_url(REDIS_URL)
    
    # Fetch players
    # Note: SQLModel sync session used in async context for simplicity (step 09 often uses async session but sync is fine for script entry)
    with Session(engine) as session:
        players = session.exec(select(Player)).all()
    
    queue = asyncio.Queue()
    for p in players:
        queue.put_nowait(p)

    # Bounded concurrency (e.g., 5 workers)
    concurrency_limit = 5
    workers = []
    for _ in range(concurrency_limit):
        task = asyncio.create_task(worker(queue, r))
        workers.append(task)
    
    await queue.join()
    
    for task in workers:
        task.cancel()
    
    await r.close()
    logger.info("Refresh Job Completed")

if __name__ == "__main__":
    anyio.run(main)
