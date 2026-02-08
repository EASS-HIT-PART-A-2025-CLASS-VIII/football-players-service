#!/usr/bin/env python
"""
Market Value Refresh Script
Session 09 async refresher deliverable with bounded concurrency, retries, and Redis idempotency.

Usage:
    uv run python scripts/refresh.py --all
    uv run python scripts/refresh.py --player-ids 1 2 3
"""

import asyncio
import argparse
import logging
import os
import sys
from datetime import datetime
from typing import List, Optional
import httpx
from redis import Redis

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger("refresh")

# Configuration
MAX_CONCURRENT_REQUESTS = 5  # Bounded concurrency
MAX_RETRIES = 3
RETRY_DELAY = 1.0  # seconds

# Redis for idempotency
redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
redis_conn = Redis.from_url(redis_url, decode_responses=True)


class RefreshError(Exception):
    """Custom exception for refresh failures."""
    pass


async def refresh_player_market_value(
    client: httpx.AsyncClient,
    player_id: int,
    semaphore: asyncio.Semaphore
) -> dict:
    """
    Refresh market value for a single player with retry logic.
    
    Args:
        client: HTTP client
        player_id: Player ID to refresh
        semaphore: Concurrency limiter
    
    Returns:
        dict: Refresh result
    """
    async with semaphore:  # Bounded concurrency
        # Check idempotency
        idempotency_key = f"market_refresh:{player_id}:{datetime.utcnow().date()}"
        if redis_conn.exists(idempotency_key):
            logger.info(f"Player {player_id}: Already refreshed today (idempotent)")
            return {
                "player_id": player_id,
                "status": "skipped",
                "reason": "already_refreshed_today"
            }
        
        # Retry logic
        last_error = None
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                # Fetch current player data
                response = await client.get(f"/players/{player_id}")
                response.raise_for_status()
                player = response.json()
                
                current_value = player.get("market_value", 0)
                
                # Simulate market update (mock)
                # In production: call external market data API
                import random
                random.seed(player_id + int(datetime.utcnow().timestamp()))
                fluctuation = random.uniform(-0.10, 0.10)
                new_value = int(current_value * (1 + fluctuation))
                random.seed()
                
                # Update player
                update_response = await client.put(
                    f"/players/{player_id}",
                    json={**player, "market_value": new_value}
                )
                update_response.raise_for_status()
                
                # Mark as refreshed (24h TTL)
                redis_conn.setex(idempotency_key, 86400, "1")
                
                logger.info(
                    f"Player {player_id}: ${current_value:,} → ${new_value:,} "
                    f"(attempt {attempt})"
                )
                
                return {
                    "player_id": player_id,
                    "status": "success",
                    "old_value": current_value,
                    "new_value": new_value,
                    "attempts": attempt,
                }
                
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 404:
                    logger.warning(f"Player {player_id}: Not found")
                    return {
                        "player_id": player_id,
                        "status": "not_found"
                    }
                last_error = e
                
            except Exception as e:
                last_error = e
            
            # Retry delay with exponential backoff
            if attempt < MAX_RETRIES:
                delay = RETRY_DELAY * (2 ** (attempt - 1))
                logger.warning(
                    f"Player {player_id}: Attempt {attempt} failed, "
                    f"retrying in {delay}s... ({str(last_error)})"
                )
                await asyncio.sleep(delay)
        
        # All retries exhausted
        logger.error(f"Player {player_id}: Failed after {MAX_RETRIES} attempts")
        return {
            "player_id": player_id,
            "status": "failed",
            "error": str(last_error),
            "attempts": MAX_RETRIES,
        }


async def refresh_all_players(api_url: str, player_ids: Optional[List[int]] = None):
    """
    Refresh market values with bounded concurrency.
    
    Args:
        api_url: Base URL of main API
        player_ids: Optional list of specific player IDs
    """
    semaphore = asyncio.Semaphore(MAX_CONCURRENT_REQUESTS)
    
    async with httpx.AsyncClient(base_url=api_url, timeout=30.0) as client:
        # Determine which players to refresh
        if player_ids:
            ids_to_refresh = player_ids
        else:
            # Fetch all players
            logger.info("Fetching all players...")
            response = await client.get("/players", params={"limit": 1000})
            response.raise_for_status()
            players_data = response.json()
            ids_to_refresh = [p["id"] for p in players_data.get("data", [])]
        
        logger.info(f"Refreshing {len(ids_to_refresh)} players with max {MAX_CONCURRENT_REQUESTS} concurrent requests")
        
        # Create refresh tasks
        tasks = [
            refresh_player_market_value(client, player_id, semaphore)
            for player_id in ids_to_refresh
        ]
        
        # Execute concurrently
        start_time = datetime.utcnow()
        results = await asyncio.gather(*tasks, return_exceptions=True)
        end_time = datetime.utcnow()
        
        # Analyze results
        successful = sum(1 for r in results if isinstance(r, dict) and r.get("status") == "success")
        failed = sum(1 for r in results if isinstance(r, dict) and r.get("status") == "failed")
        skipped = sum(1 for r in results if isinstance(r, dict) and r.get("status") == "skipped")
        
        duration = (end_time - start_time).total_seconds()
        
        logger.info("=" * 60)
        logger.info(f"Refresh Summary:")
        logger.info(f"  Total: {len(ids_to_refresh)}")
        logger.info(f"  Successful: {successful}")
        logger.info(f"  Failed: {failed}")
        logger.info(f"  Skipped: {skipped}")
        logger.info(f"  Duration: {duration:.2f}s")
        logger.info("=" * 60)
        
        return {
            "total": len(ids_to_refresh),
            "successful": successful,
            "failed": failed,
            "skipped": skipped,
            "duration_seconds": duration,
        }


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Refresh player market values")
    parser.add_argument("--all", action="store_true", help="Refresh all players")
    parser.add_argument("--player-ids", type=int, nargs="+", help="Specific player IDs to refresh")
    parser.add_argument("--api-url", default="http://localhost:8000", help="Main API URL")
    
    args = parser.parse_args()
    
    if not args.all and not args.player_ids:
        logger.error("Must specify either --all or --player-ids")
        sys.exit(1)
    
    # Run async refresh
    try:
        asyncio.run(refresh_all_players(args.api_url, args.player_ids))
    except KeyboardInterrupt:
        logger.info("Refresh cancelled by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Refresh failed: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
