"""
Worker Service - RQ Worker Runner
Processes background tasks from Redis queue
"""

import logging
import os
from redis import Redis
from rq import Worker

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)

logger = logging.getLogger("worker-service")


def run_worker():
    """Start RQ worker to process tasks."""
    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    
    logger.info("=" * 60)
    logger.info("👷 Worker Service v1.0.0")
    logger.info("=" * 60)
    logger.info(f"Redis URL: {redis_url}")
    logger.info("Listening for tasks...")
    logger.info("=" * 60)
    
    redis_conn = Redis.from_url(redis_url, decode_responses=True)
    
    # Create worker with football-tasks queue
    worker = Worker(["football-tasks"], connection=redis_conn)
    
    # Start processing tasks
    worker.work(with_scheduler=True)


if __name__ == "__main__":
    run_worker()
