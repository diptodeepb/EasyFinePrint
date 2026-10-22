"""Unit tests for health check endpoint."""
import pytest
from httpx import ASGITransport, AsyncClient
from app.main import app


@pytest.mark.asyncio
async def test_health_check_endpoint():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] in ("healthy", "degraded")
        assert data["service"] == "EasyFinePrint"
        assert "timestamp" in data
        # Ensure infrastructure internals and model IDs are omitted for security
        assert "ai_provider" not in data
        assert "ai_model" not in data
        assert "environment" not in data
        assert "database" not in data


@pytest.mark.asyncio
async def test_root_endpoint():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "EasyFinePrint API"
        assert data["health"] == "/api/health"
