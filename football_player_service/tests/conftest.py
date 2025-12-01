import pytest
from fastapi.testclient import TestClient

from football_player_service.app.main import app
from football_player_service.app.dependencies import get_repository


@pytest.fixture(autouse=True)
def clear_repository():
	"""Clear repository before and after each test."""
	repo = next(get_repository())
	repo.clear()
	yield
	repo.clear()


@pytest.fixture
def client():
	"""Provide a TestClient for making requests."""
	return TestClient(app)

