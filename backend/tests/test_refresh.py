"""
Tests for async refresh script (Session 09 requirement).
Validates idempotency, bounded concurrency, and retry logic.
"""
import sys
from pathlib import Path

# Add backend directory to path for imports
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

import pytest
from unittest.mock import AsyncMock, patch
import asyncio
from tenacity import RetryError

from scripts.refresh import refresh_player, worker
from football_player_service.app.models import Player


@pytest.mark.anyio
async def test_refresh_player_idempotency():
    """Test that refresh_player skips recently processed players (Redis idempotency)."""
    player = Player(
        id=1,
        full_name="Test Player",
        country="Test Country",
        age=25,
        club="Test FC",
        position="Forward",
        market_value_eur=1000000
    )
    
    # Mock Redis client that returns "already processed" flag
    mock_redis = AsyncMock()
    mock_redis.get.return_value = "1"  # Simulates player was recently refreshed
    
    # Should skip without calling setex
    await refresh_player(player, mock_redis)
    
    # Verify it checked for existing refresh
    mock_redis.get.assert_called_once_with(f"refreshed:{player.id}")
    
    # Verify it did NOT set a new refresh mark (skipped processing)
    mock_redis.setex.assert_not_called()


@pytest.mark.anyio
async def test_refresh_player_processes_new_player():
    """Test that refresh_player processes a player not in Redis cache."""
    player = Player(
        id=2,
        full_name="New Player",
        country="Brazil",
        age=23,
        club="Real Madrid",
        position="Midfielder",
        market_value_eur=5000000
    )
    
    # Mock Redis client with no existing cache
    mock_redis = AsyncMock()
    mock_redis.get.return_value = None  # Not in cache
    
    # Mock random to avoid simulated failures
    with patch('scripts.refresh.random.random', return_value=0.5):  # > 0.2, won't fail
        await refresh_player(player, mock_redis)
    
    # Verify it checked cache
    mock_redis.get.assert_called_once()
    
    # Verify it marked as refreshed (60 second TTL)
    mock_redis.setex.assert_called_once_with(f"refreshed:{player.id}", 60, "1")


@pytest.mark.anyio
async def test_refresh_player_handles_network_failure():
    """Test that refresh_player raises RetryError after 3 failed attempts."""
    player = Player(
        id=3,
        full_name="Unlucky Player",
        country="Portugal",
        age=28,
        club="Bayern Munich",
        position="Defender",
        market_value_eur=3000000
    )
    
    mock_redis = AsyncMock()
    mock_redis.get.return_value = None
    
    # Force simulated failure (random < 0.2) - will retry 3 times then raise RetryError
    with patch('scripts.refresh.random.random', return_value=0.1):
        with pytest.raises(RetryError):
            await refresh_player(player, mock_redis)
    
    # Should NOT have marked as refreshed (failed before setex)
    mock_redis.setex.assert_not_called()


@pytest.mark.anyio
async def test_worker_processes_queue():
    """Test that worker picks tasks from queue and processes them."""
    player = Player(
        id=4,
        full_name="Queue Player",
        country="Argentina",
        age=30,
        club="PSG",
        position="Forward",
        market_value_eur=8000000
    )
    
    mock_redis = AsyncMock()
    mock_redis.get.return_value = None
    
    queue = asyncio.Queue()
    await queue.put(player)
    
    # Run worker for a short time with success case
    worker_task = asyncio.create_task(worker(queue, mock_redis))
    
    # Wait for queue to be processed
    with patch('scripts.refresh.random.random', return_value=0.5):
        await asyncio.wait_for(queue.join(), timeout=2.0)
    
    # Cancel worker
    worker_task.cancel()
    try:
        await worker_task
    except asyncio.CancelledError:
        pass
    
    # Verify Redis was called (player was processed)
    assert mock_redis.get.called
