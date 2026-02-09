from fastapi.testclient import TestClient
from ai_service.main import app
import os
from unittest.mock import patch

client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

@patch("ai_service.main.genai")
def test_generate_report_mock(mock_genai):
    # Mock the Gemini API
    mock_instance = mock_genai.GenerativeModel.return_value
    mock_instance.generate_content.return_value.text = "Mocked Scouting Report"
    
    # Set API Key env var (mocked)
    with patch.dict(os.environ, {"GEMINI_API_KEY": "fake-key"}):
        payload = {
            "player_name": "Test Player",
            "position": "Forward",
            "age": 20,
            "stats": {"goals": 10}
        }
        response = client.post("/generate", json=payload)
        assert response.status_code == 200
        assert response.json()["report"] == "Mocked Scouting Report"

def test_generate_report_no_key():
    # Test fallback behavior when no key is present
    with patch.dict(os.environ, {}, clear=True):
        payload = {
            "player_name": "Test Player",
            "position": "Forward",
            "age": 20,
            "stats": {"goals": 10}
        }
        response = client.post("/generate", json=payload)
        # Depending on implementation: mine returns a simulated report
        assert response.status_code == 200
        assert "Simulated Report" in response.json()["report"]
