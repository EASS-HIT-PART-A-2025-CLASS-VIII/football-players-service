"""
Background Worker Tasks
Redis-backed async tasks with retry logic and idempotency
"""

import logging
import os
from typing import Optional, List
from datetime import datetime
import httpx
from redis import Redis
from rq import Queue
from rq.job import Job

logger = logging.getLogger("worker-service")

# Redis connection
redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
redis_conn = Redis.from_url(redis_url, decode_responses=True)

# RQ Queue for background tasks
task_queue = Queue("football-tasks", connection=redis_conn)


def refresh_market_values(player_ids: Optional[List[int]] = None) -> dict:
    """
    Background task: Refresh market values for players.
    
    This simulates fetching updated market data from external sources.
    In production, this would call real market data APIs.
    
    Args:
        player_ids: Optional list of specific player IDs to refresh.
                   If None, refreshes all active players.
    
    Returns:
        dict: Summary of refresh operation
    """
    import random
    
    logger.info(f"Starting market value refresh for players: {player_ids or 'all'}")
    
    main_api_url = os.getenv("MAIN_API_URL", "http://localhost:8000")
    
    try:
        # Fetch players to update
        if player_ids:
            # Refresh specific players
            players_to_update = []
            for player_id in player_ids:
                response = httpx.get(f"{main_api_url}/players/{player_id}")
                if response.status_code == 200:
                    players_to_update.append(response.json())
        else:
            # Refresh all active players
            response = httpx.get(f"{main_api_url}/players", params={"limit": 1000})
            response.raise_for_status()
            players_to_update = response.json().get("data", [])
        
        updated_count = 0
        for player in players_to_update:
            player_id = player["id"]
            
            # Check idempotency key (don't refresh if already done recently)
            idempotency_key = f"market_refresh:{player_id}:{datetime.utcnow().date()}"
            if redis_conn.exists(idempotency_key):
                logger.info(f"Skipping player {player_id} - already refreshed today")
                continue
            
            # Simulate market value update (mock calculation)
            # In production: fetch from real market data API
            current_value = player.get("market_value", 0)
            
            # Random fluctuation: ±10%
            random.seed(player_id + int(datetime.utcnow().timestamp()))
            fluctuation = random.uniform(-0.10, 0.10)
            new_value = int(current_value * (1 + fluctuation))
            random.seed()  # Reset seed
            
            # Update via API
            update_response = httpx.put(
                f"{main_api_url}/players/{player_id}",
                json={**player, "market_value": new_value}
            )
            
            if update_response.status_code == 200:
                updated_count += 1
                logger.info(f"Updated player {player_id}: ${current_value:,} → ${new_value:,}")
                
                # Set idempotency key with 24h expiration
                redis_conn.setex(idempotency_key, 86400, "1")
        
        result = {
            "status": "completed",
            "players_updated": updated_count,
            "total_players": len(players_to_update),
            "timestamp": datetime.utcnow().isoformat(),
        }
        
        logger.info(f"Market refresh complete: {updated_count}/{len(players_to_update)} players updated")
        return result
        
    except Exception as e:
        logger.error(f"Market refresh failed: {str(e)}")
        return {
            "status": "failed",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat(),
        }


def generate_analytics_batch(player_ids: List[int]) -> dict:
    """
    Background task: Generate analytics for multiple players in batch.
    
    Calls the analytics service for each player and caches results.
    
    Args:
        player_ids: List of player IDs to analyze
    
    Returns:
        dict: Summary of analytics generation
    """
    logger.info(f"Starting batch analytics generation for {len(player_ids)} players")
    
    analytics_url = os.getenv("ANALYTICS_URL", "http://localhost:8001")
    
    try:
        successful = 0
        failed = 0
        
        for player_id in player_ids:
            try:
                # Generate full insights
                response = httpx.post(
                    f"{analytics_url}/insights/{player_id}",
                    timeout=30.0
                )
                response.raise_for_status()
                
                # Cache results in Redis
                cache_key = f"analytics:player:{player_id}"
                redis_conn.setex(cache_key, 3600, response.text)  # 1 hour TTL
                
                successful += 1
                logger.info(f"Generated analytics for player {player_id}")
                
            except Exception as e:
                failed += 1
                logger.error(f"Failed to generate analytics for player {player_id}: {str(e)}")
        
        result = {
            "status": "completed",
            "successful": successful,
            "failed": failed,
            "total": len(player_ids),
            "timestamp": datetime.utcnow().isoformat(),
        }
        
        logger.info(f"Batch analytics complete: {successful}/{len(player_ids)} successful")
        return result
        
    except Exception as e:
        logger.error(f"Batch analytics failed: {str(e)}")
        return {
            "status": "failed",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat(),
        }


def enqueue_market_refresh(player_ids: Optional[List[int]] = None) -> Job:
    """
    Enqueue market value refresh task.
    
    Returns:
        Job: RQ job object
    """
    job = task_queue.enqueue(
        refresh_market_values,
        player_ids,
        job_timeout="5m",
        result_ttl=3600,  # Keep result for 1 hour
    )
    logger.info(f"Enqueued market refresh job: {job.id}")
    return job


def enqueue_analytics_batch(player_ids: List[int]) -> Job:
    """
    Enqueue batch analytics generation task.
    
    Returns:
        Job: RQ job object
    """
    job = task_queue.enqueue(
        generate_analytics_batch,
        player_ids,
        job_timeout="10m",
        result_ttl=3600,
    )
    logger.info(f"Enqueued analytics batch job: {job.id}")
    return job


def get_job_status(job_id: str) -> dict:
    """
    Get status of a background job.
    
    Returns:
        dict: Job status information
    """
    try:
        job = Job.fetch(job_id, connection=redis_conn)
        
        return {
            "job_id": job.id,
            "status": job.get_status(),
            "result": job.result if job.is_finished else None,
            "exc_info": job.exc_info if job.is_failed else None,
            "created_at": job.created_at.isoformat() if job.created_at else None,
            "started_at": job.started_at.isoformat() if job.started_at else None,
            "ended_at": job.ended_at.isoformat() if job.ended_at else None,
        }
    except Exception as e:
        return {
            "job_id": job_id,
            "status": "not_found",
            "error": str(e),
        }
