
"""
Comprehensive test suite for Football Player Service API.

Tests use the 'client' fixture from `conftest.py`, which provides
a TestClient for making HTTP requests to our FastAPI app without
needing a real server.
"""

def test_health_includes_app_name(client):
	"""Health endpoint returns status and app name."""
	response = client.get("/health")
	assert response.status_code == 200
	data = response.json()
	assert data["status"] == "ok"
	assert data["app"] == "Football Player Service"


def test_create_player_returns_201_and_payload(client):
	"""Creating a player returns 201 with normalized payload."""
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
	first = client.post(
		"/players",
		json={
			"full_name": "Kylian Mbappe",
			"country": "france",
			"status": "active",
			"age": 24,
			"market_value": 160000000,
		},
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
	).json()["id"]
	assert second == first + 1


def test_list_players_returns_empty_array_initially(client):
	"""Empty repository returns empty array."""
	response = client.get("/players")
	assert response.status_code == 200
	assert response.json() == []


def test_list_players_returns_created_player(client):
	"""Can retrieve players after creating them."""
	client.post(
		"/players",
		json={
			"full_name": "Erling Haaland",
			"country": "norway",
			"status": "active",
			"age": 22,
			"market_value": 60000000,
		},
	)

	response = client.get("/players")
	assert response.status_code == 200
	players = response.json()
	assert len(players) == 1
	assert players[0]["full_name"] == "Erling Haaland"


def test_get_player_by_id(client):
	"""Can retrieve specific player by ID."""
	create_response = client.post(
		"/players",
		json={
			"full_name": "Harry Kane",
			"country": "england",
			"status": "active",
			"age": 30,
			"market_value": 50000000,
		},
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
	assert response.json()["detail"] == "Player not found"


def test_delete_player(client):
	"""Can delete a player and it's gone afterwards."""
	create_response = client.post(
		"/players",
		json={
			"full_name": "Sergio Ramos",
			"country": "spain",
			"status": "retired",
			"age": 39,
			"market_value": 1000000,
		},
	)
	player_id = create_response.json()["id"]

	response = client.delete(f"/players/{player_id}")
	assert response.status_code == 204

	get_response = client.get(f"/players/{player_id}")
	assert get_response.status_code == 404


def test_delete_missing_player_returns_404(client):
	"""Deleting non-existent player returns 404."""
	response = client.delete("/players/9999")
	assert response.status_code == 404


def test_create_player_rejects_too_short_full_name(client):
	"""Full name shorter than 2 chars is rejected with 422."""
	response = client.post(
		"/players",
		json={"full_name": "A", "country": "X", "status": "active"},
	)
	assert response.status_code == 422


def test_create_player_rejects_missing_country(client):
	"""Missing required field country returns 422."""
	response = client.post(
		"/players",
		json={"full_name": "Zlatan Ibrahimovic", "status": "active"},
	)
	assert response.status_code == 422


def test_create_player_rejects_missing_status(client):
	"""Missing required field status returns 422."""
	response = client.post(
		"/players",
		json={"full_name": "Paulo Dybala", "country": "argentina"},
	)
	assert response.status_code == 422


def test_create_player_rejects_invalid_status(client):
	"""Invalid enum value for status returns 422."""
	response = client.post(
		"/players",
		json={"full_name": "Random Player", "country": "country", "status": "playing"},
	)
	assert response.status_code == 422

