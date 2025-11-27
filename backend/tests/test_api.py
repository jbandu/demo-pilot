import pytest
from httpx import AsyncClient
from unittest.mock import Mock, AsyncMock, patch


@pytest.mark.asyncio
async def test_root_endpoint(client: AsyncClient):
    """Test root endpoint"""
    response = await client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "service" in data
    assert data["service"] == "Demo Copilot"


@pytest.mark.asyncio
async def test_health_check(client: AsyncClient):
    """Test health check endpoint"""
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


@pytest.mark.asyncio
async def test_start_demo(client: AsyncClient, sample_demo_request):
    """Test starting a demo"""
    with patch("api.main.DemoCopilot") as mock_copilot:
        mock_instance = Mock()
        mock_instance.start_demo = AsyncMock(return_value="test-session-123")
        mock_copilot.return_value = mock_instance

        response = await client.post("/api/demo/start", json=sample_demo_request)

        assert response.status_code == 200
        data = response.json()
        assert "session_id" in data
        assert data["status"] == "started"


@pytest.mark.asyncio
async def test_get_demo_status_not_found(client: AsyncClient):
    """Test getting status of non-existent demo"""
    response = await client.get("/api/demo/nonexistent-id/status")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_ask_question(client: AsyncClient):
    """Test asking a question"""
    # First start a demo
    with patch("api.main.DemoCopilot") as mock_copilot:
        mock_instance = Mock()
        mock_instance.start_demo = AsyncMock(return_value="test-session-123")
        mock_instance.ask_question = AsyncMock()
        mock_instance.state = {"status": "running"}
        mock_copilot.return_value = mock_instance

        # Add to active demos
        from api.main import active_demos

        active_demos["test-session-123"] = mock_instance

        # Ask question
        response = await client.post(
            "/api/demo/test-session-123/question",
            json={"session_id": "test-session-123", "question": "Test question?"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "question_received"
