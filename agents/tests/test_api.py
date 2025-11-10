"""Tests for FastAPI endpoints."""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch
from app import app
from models import CubeQuery, ChartData


client = TestClient(app)


def test_root_endpoint():
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "service" in data
    assert "version" in data
    assert data["status"] == "running"


def test_health_endpoint():
    """Test health check endpoint."""
    with patch("cubejs_client.cubejs_client.health_check", new_callable=AsyncMock) as mock_health:
        mock_health.return_value = True

        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["cubejs_connected"] is True


def test_chat_endpoint_invalid_request():
    """Test chat endpoint with invalid request."""
    response = client.post("/chat", json={})
    assert response.status_code == 422  # Validation error


def test_chat_endpoint_creates_session():
    """Test that chat endpoint creates a session if none provided."""
    with patch("chat_agent.chat_agent.should_query_data", new_callable=AsyncMock) as mock_should_query, \
         patch("chat_agent.chat_agent.generate_conversational_response", new_callable=AsyncMock) as mock_response:

        mock_should_query.return_value = False
        mock_response.return_value = "Hello! How can I help?"

        response = client.post("/chat", json={"message": "Hello"})

        assert response.status_code == 200
        data = response.json()
        assert "session_id" in data
        assert len(data["session_id"]) > 0
        assert data["message"] == "Hello! How can I help?"


@pytest.mark.asyncio
async def test_chat_endpoint_with_data_query():
    """Test chat endpoint with a data query."""
    with patch("chat_agent.chat_agent.should_query_data", new_callable=AsyncMock) as mock_should_query, \
         patch("data_analyst_agent.data_analyst_agent.translate_to_query", new_callable=AsyncMock) as mock_translate, \
         patch("cubejs_client.cubejs_client.execute_query", new_callable=AsyncMock) as mock_execute, \
         patch("data_analyst_agent.data_analyst_agent.generate_insights", new_callable=AsyncMock) as mock_insights:

        mock_should_query.return_value = True
        mock_translate.return_value = (
            CubeQuery(measures=["ProductionQuality.passRate"], dimensions=["ProductionQuality.componentType"]),
            "bar"
        )
        mock_execute.return_value = {
            "data": [
                {"ProductionQuality.componentType": "refills", "ProductionQuality.passRate": "95"}
            ]
        }
        mock_insights.return_value = ["Refills have 95% pass rate"]

        response = client.post("/chat", json={"message": "What's the pass rate?"})

        assert response.status_code == 200
        data = response.json()
        assert "session_id" in data
        assert "chart" in data
        assert "insights" in data


def test_get_session_not_found():
    """Test getting a non-existent session."""
    response = client.get("/session/non-existent-id")
    assert response.status_code == 404


def test_delete_session():
    """Test deleting a session."""
    # First create a session via chat
    with patch("chat_agent.chat_agent.should_query_data", new_callable=AsyncMock) as mock_should_query, \
         patch("chat_agent.chat_agent.generate_conversational_response", new_callable=AsyncMock) as mock_response:

        mock_should_query.return_value = False
        mock_response.return_value = "Hello!"

        create_response = client.post("/chat", json={"message": "Hi"})
        session_id = create_response.json()["session_id"]

        # Delete the session
        delete_response = client.delete(f"/session/{session_id}")
        assert delete_response.status_code == 200

        # Verify it's gone
        get_response = client.get(f"/session/{session_id}")
        assert get_response.status_code == 404
