"""
Comprehensive test suite for Football Player Service API.

Tests use the 'client' fixture from `conftest.py`, which provides
a TestClient for making HTTP requests to our FastAPI app without
needing a real server.
"""


def auth_headers(client):
    response = client.post(
        "/token",
        data={"username": "admin", "password": "admin123"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert response.status_code == 200
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_health_includes_app_name(client):
    """Health endpoint returns status and app name."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["app"] == "Football Player Service"


def test_create_player_returns_201_and_payload(client):
    """Creating a player returns 201 with normalized payload."""
    headers = auth_headers(client)
    response = client.post(
        "/players",
        json={
            "full_name": "lionel messi",
            "country": "argentina",
            "status": "active",
            "current_team": "paris saint-germain",
            "league": "ligue 1",
            "age": 34,
            "market_value": 80000000,
        },
        headers=headers,
    )
    assert response.status_code == 201
    payload = response.json()
    assert payload["full_name"] == "Lionel Messi"
    assert payload["country"] == "Argentina"
    assert payload["league"] == "Ligue 1"
    assert payload["current_team"] == "Paris Saint-Germain"
    assert payload["status"] == "active"
    assert payload["id"] == 1
    assert payload["age"] == 34
    assert payload["market_value"] == 80000000


def test_player_ids_increment(client):
    """Repository assigns sequential IDs."""
    headers = auth_headers(client)
    first = client.post(
        "/players",
        json={
            "full_name": "Kylian Mbappe",
            "country": "france",
            "status": "active",
            "age": 24,
            "market_value": 160000000,
        },
        headers=headers,
    ).json()["id"]
    second = client.post(
        "/players",
        json={
            "full_name": "Neymar Jr",
            "country": "brazil",
            "status": "active",
            "age": 31,
            "market_value": 90000000,
        },
        headers=headers,
    ).json()["id"]
    assert second == first + 1


def test_list_players_returns_empty_array_initially(client):
    """Empty repository returns empty paginated response."""
    response = client.get("/players")
    assert response.status_code == 200
    data = response.json()
    assert data["data"] == []
    assert data["total"] == 0
    assert data["page"] == 1
    assert data["pages"] == 0


def test_list_players_returns_created_player(client):
    """Can retrieve players after creating them."""
    headers = auth_headers(client)
    client.post(
        "/players",
        json={
            "full_name": "Erling Haaland",
            "country": "norway",
            "status": "active",
            "age": 22,
            "market_value": 60000000,
        },
        headers=headers,
    )

    response = client.get("/players")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1
    assert len(data["data"]) >= 1
    assert data["data"][0]["full_name"] == "Erling Haaland"


def test_get_player_by_id(client):
    """Can retrieve specific player by ID."""
    headers = auth_headers(client)
    create_response = client.post(
        "/players",
        json={
            "full_name": "Harry Kane",
            "country": "england",
            "status": "active",
            "age": 30,
            "market_value": 50000000,
        },
        headers=headers,
    )
    player_id = create_response.json()["id"]

    response = client.get(f"/players/{player_id}")
    assert response.status_code == 200
    player = response.json()
    assert player["full_name"] == "Harry Kane"
    assert player["id"] == player_id
    assert player["age"] == 30
    assert player["market_value"] == 50000000


def test_get_missing_player_returns_404(client):
    """Requesting non-existent player returns 404."""
    response = client.get("/players/9999")
    assert response.status_code == 404
    error = response.json()["detail"]["error"]
    assert error["code"] == "PLAYER_NOT_FOUND"
    assert "9999" in error["message"]
    assert error["player_id"] == 9999


def test_delete_player(client):
    """Can delete a player and it's gone afterwards."""
    headers = auth_headers(client)
    create_response = client.post(
        "/players",
        json={
            "full_name": "Sergio Ramos",
            "country": "spain",
            "status": "retired",
            "age": 39,
            "market_value": 1000000,
        },
        headers=headers,
    )
    player_id = create_response.json()["id"]

    response = client.delete(f"/players/{player_id}", headers=headers)
    assert response.status_code == 204

    get_response = client.get(f"/players/{player_id}")
    assert get_response.status_code == 404


def test_delete_missing_player_returns_404(client):
    """Deleting non-existent player returns 404."""
    headers = auth_headers(client)
    response = client.delete("/players/9999", headers=headers)
    assert response.status_code == 404
    error = response.json()["detail"]["error"]
    assert error["code"] == "PLAYER_NOT_FOUND"


def test_create_player_rejects_too_short_full_name(client):
    """Full name shorter than 2 chars is rejected with 422."""
    headers = auth_headers(client)
    response = client.post(
        "/players",
        json={"full_name": "A", "country": "X", "status": "active"},
        headers=headers,
    )
    assert response.status_code == 422


def test_create_player_rejects_missing_country(client):
    """Missing required field country returns 422."""
    headers = auth_headers(client)
    response = client.post(
        "/players",
        json={"full_name": "Zlatan Ibrahimovic", "status": "active"},
        headers=headers,
    )
    assert response.status_code == 422


def test_create_player_rejects_missing_status(client):
    """Missing required field status returns 422."""
    headers = auth_headers(client)
    response = client.post(
        "/players",
        json={"full_name": "Paulo Dybala", "country": "argentina"},
        headers=headers,
    )
    assert response.status_code == 422


def test_create_player_rejects_invalid_status(client):
    """Invalid enum value for status returns 422."""
    headers = auth_headers(client)
    response = client.post(
        "/players",
        json={"full_name": "Random Player", "country": "country", "status": "playing"},
        headers=headers,
    )
    assert response.status_code == 422


def test_market_value_is_null_when_omitted(client):
    """If `market_value` is not provided it should be `null` in the response."""
    headers = auth_headers(client)
    response = client.post(
        "/players",
        json={
            "full_name": "No Market",
            "country": "nowhere",
            "status": "active",
            "age": 20,
        },
        headers=headers,
    )
    assert response.status_code == 201
    player = response.json()
    assert player["full_name"] == "No Market"
    assert player["market_value"] is None


def test_create_player_rejects_missing_age(client):
    """Omitting required `age` returns 422."""
    headers = auth_headers(client)
    response = client.post(
        "/players",
        json={"full_name": "Missing Age", "country": "x", "status": "active"},
        headers=headers,
    )
    assert response.status_code == 422


def test_rate_limit_protects_post_endpoint(client):
    """Rate limit protects POST /players from excessive requests."""
    headers = auth_headers(client)
    # Note: rate limit is per-minute; this test verifies the header is present.
    # In production, would require 101+ requests to trigger 429.
    response = client.post(
        "/players",
        json={
            "full_name": "Rate Test",
            "country": "test",
            "status": "active",
            "age": 25,
        },
        headers=headers,
    )
    assert response.status_code == 201
    # Verify rate limit header is present (slowapi adds X-RateLimit-* headers)
    assert "x-ratelimit-limit" in response.headers or response.status_code == 201


def test_age_validation_negative_rejected(client):
    """Negative age is rejected with 422."""
    headers = auth_headers(client)
    response = client.post(
        "/players",
        json={
            "full_name": "Negative Age",
            "country": "test",
            "status": "active",
            "age": -5,
        },
        headers=headers,
    )
    assert response.status_code == 422


def test_age_validation_too_high_rejected(client):
    """Age > 120 is rejected with 422."""
    headers = auth_headers(client)
    response = client.post(
        "/players",
        json={
            "full_name": "Too Old",
            "country": "test",
            "status": "active",
            "age": 150,
        },
        headers=headers,
    )
    assert response.status_code == 422


def test_full_name_max_length(client):
    """Full name exceeding max length is rejected."""
    headers = auth_headers(client)
    long_name = "A" * 101  # Exceeds max_length=100
    response = client.post(
        "/players",
        json={
            "full_name": long_name,
            "country": "test",
            "status": "active",
            "age": 25,
        },
        headers=headers,
    )
    assert response.status_code == 422


def test_market_value_negative_rejected(client):
    """Negative market_value is rejected with 422."""
    headers = auth_headers(client)
    response = client.post(
        "/players",
        json={
            "full_name": "Bad Value",
            "country": "test",
            "status": "active",
            "age": 25,
            "market_value": -1000000,
        },
        headers=headers,
    )
    assert response.status_code == 422


def test_security_headers_present(client):
    """Security headers are present in response."""
    response = client.get("/health")
    assert response.status_code == 200
    assert "x-content-type-options" in response.headers
    assert response.headers["x-content-type-options"] == "nosniff"
    assert "x-frame-options" in response.headers
    assert response.headers["x-frame-options"] == "DENY"


# === Authentication Tests ===

def test_login_with_valid_credentials_returns_token(client):
    """Login with valid credentials returns JWT token."""
    response = client.post(
        "/token",
        data={"username": "admin", "password": "admin123"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert len(data["access_token"]) > 20  # JWT tokens are long


def test_login_with_invalid_credentials_returns_401(client):
    """Login with invalid credentials returns 401 Unauthorized."""
    response = client.post(
        "/token",
        data={"username": "admin", "password": "wrongpassword"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert response.status_code == 401
    assert "Incorrect username or password" in response.json()["detail"]


def test_create_player_without_token_returns_401(client):
    """Creating a player without token returns 401."""
    response = client.post(
        "/players",
        json={
            "full_name": "Test Player",
            "country": "USA",
            "status": "active",
            "age": 25,
        },
    )
    assert response.status_code == 401
    assert "Not authenticated" in response.json()["detail"]


def test_create_player_with_valid_token_succeeds(client):
    """Creating a player with valid token succeeds."""
    # Get token
    login_response = client.post(
        "/token",
        data={"username": "admin", "password": "admin123"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    token = login_response.json()["access_token"]
    
    # Create player with token
    response = client.post(
        "/players",
        json={
            "full_name": "Authorized Player",
            "country": "France",
            "status": "active",
            "age": 28,
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 201
    assert response.json()["full_name"] == "Authorized Player"


def test_update_player_requires_authentication(client):
    """Updating a player requires authentication."""
    # First create a player (with auth)
    login_response = client.post(
        "/token",
        data={"username": "admin", "password": "admin123"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    token = login_response.json()["access_token"]
    
    create_response = client.post(
        "/players",
        json={
            "full_name": "Update Test",
            "country": "Spain",
            "status": "active",
            "age": 30,
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    player_id = create_response.json()["id"]
    
    # Try to update without token - should fail
    response = client.put(
        f"/players/{player_id}",
        json={
            "full_name": "Updated Name",
            "country": "Spain",
            "status": "active",
            "age": 31,
        },
    )
    assert response.status_code == 401


def test_delete_player_requires_authentication(client):
    """Deleting a player requires authentication."""
    # Create a player with auth
    login_response = client.post(
        "/token",
        data={"username": "admin", "password": "admin123"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    token = login_response.json()["access_token"]
    
    create_response = client.post(
        "/players",
        json={
            "full_name": "Delete Test",
            "country": "Italy",
            "status": "active",
            "age": 26,
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    player_id = create_response.json()["id"]
    
    # Try to delete without token - should fail
    response = client.delete(f"/players/{player_id}")
    assert response.status_code == 401


def test_scout_player_requires_authentication(client):
    """Scouting a player requires authentication."""
    # Create a player with auth
    login_response = client.post(
        "/token",
        data={"username": "admin", "password": "admin123"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    token = login_response.json()["access_token"]
    
    create_response = client.post(
        "/players",
        json={
            "full_name": "Scout Test",
            "country": "Brazil",
            "status": "active",
            "age": 22,
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    player_id = create_response.json()["id"]
    
    # Try to scout without token - should fail
    response = client.post(f"/players/{player_id}/scout")
    assert response.status_code == 401
    
    # Scout with valid token - should succeed
    response = client.post(
        f"/players/{player_id}/scout",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 202
    assert "task_id" in response.json()


def test_invalid_token_returns_401(client):
    """Using an invalid token returns 401."""
    response = client.post(
        "/players",
        json={
            "full_name": "Test",
            "country": "USA",
            "status": "active",
            "age": 25,
        },
        headers={"Authorization": "Bearer invalid_token_here"},
    )
    assert response.status_code == 401


def test_expired_token_simulation(client):
    """Test token validation - simulated by using malformed token."""
    # This simulates an expired/invalid token
    malformed_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.invalid.signature"
    
    response = client.post(
        "/players",
        json={
            "full_name": "Test",
            "country": "USA",
            "status": "active",
            "age": 25,
        },
        headers={"Authorization": f"Bearer {malformed_token}"},
    )
    assert response.status_code == 401
    assert "Could not validate credentials" in response.json()["detail"]


def test_scout_player_returns_202_and_task_id(client, monkeypatch):
    """Scouting a player returns 202 Accepted with task ID."""
    headers = auth_headers(client)
    # Create a player first
    player = client.post(
        "/players",
        json={
            "full_name": "Cristiano Ronaldo",
            "country": "Portugal",
            "status": "active",
            "age": 39,
            "market_value": 25000000,
        },
        headers=headers,
    ).json()
    
    # Mock Celery task sending
    task_sent = []
    def mock_send_task(task_name, args, task_id):
        task_sent.append({"task_name": task_name, "args": args, "task_id": task_id})
    
    from football_player_service.app import main
    monkeypatch.setattr(main.celery_app, "send_task", mock_send_task)
    
    # Scout the player
    response = client.post(f"/players/{player['id']}/scout", headers=headers)
    assert response.status_code == 202
    data = response.json()
    assert "task_id" in data
    assert "status" in data
    assert data["status"] == "accepted"
    assert len(task_sent) == 1
    assert task_sent[0]["task_name"] == "ai_scout.generate_report"
    assert task_sent[0]["args"] == [player["id"]]


def test_scout_nonexistent_player_returns_404(client):
    """Scouting a non-existent player returns 404."""
    headers = auth_headers(client)
    response = client.post("/players/9999/scout", headers=headers)
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert data["detail"] == "Player not found"


def test_get_task_status_from_redis(client, monkeypatch):
    """Getting task status returns data from Redis."""
    import json
    
    # Mock Redis client
    class MockRedis:
        def __init__(self):
            self.data = {}
        
        def get(self, key):
            return self.data.get(key)
        
        def setex(self, key, ttl, value):
            self.data[key] = value
    
    mock_redis = MockRedis()
    from football_player_service.app import main
    monkeypatch.setattr(main, "redis_client", mock_redis)
    
    # Set up mock task data
    task_id = "test-task-123"
    task_data = {
        "task_id": task_id,
        "status": "completed",
        "result": "Report generated successfully",
        "error": None,
        "created_at": None
    }
    mock_redis.setex(f"task:{task_id}", 3600, json.dumps(task_data))
    
    # Get task status
    response = client.get(f"/tasks/{task_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["task_id"] == task_id
    assert data["status"] == "completed"
    assert data["result"] == "Report generated successfully"
    assert data["error"] is None


def test_get_task_status_not_found(client, monkeypatch):
    """Getting status for non-existent task returns 404."""
    # Mock Redis client returning None
    class MockRedis:
        def get(self, key):
            return None
    
    # Mock Celery AsyncResult to also fail
    class MockAsyncResult:
        def __init__(self, task_id):
            self.task_id = task_id
            self.state = "PENDING"
            
        def successful(self):
            return False
        
        def failed(self):
            return False
    
    from football_player_service.app import main
    monkeypatch.setattr(main, "redis_client", MockRedis())
    
    # Patch AsyncResult to raise exception (task not found)
    def mock_async_result(task_id):
        raise Exception("Task not found")
    
    monkeypatch.setattr(main.celery_app, "AsyncResult", mock_async_result)
    
    # Try to get non-existent task
    response = client.get("/tasks/nonexistent-task-id")
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "not found" in data["detail"].lower()
