"""Tests for SerpApi discovery integration and quota guard."""
import pytest
from httpx import ASGITransport, AsyncClient
from app.main import app
from app.config import settings
from app.services.serpapi import discover_policy_urls, _monthly_usage, _hourly_usage, _query_cache


@pytest.mark.asyncio
async def test_serpapi_disabled_by_default():
    settings.serpapi_enabled = False
    result = await discover_policy_urls("Spotify")
    assert "error" in result
    assert result["error"] == "serpapi_disabled"


@pytest.mark.asyncio
async def test_serpapi_hourly_and_monthly_cap():
    settings.serpapi_enabled = True
    settings.serpapi_api_key = "test_key_dummy"
    settings.serpapi_hourly_cap = 2

    # Clear query cache and set hourly usage to cap
    _query_cache.clear()
    from app.services.serpapi import _get_hour_bucket
    _hourly_usage[_get_hour_bucket()] = 2

    result = await discover_policy_urls("NewCompany")
    assert "error" in result
    assert result["error"] == "hourly_cap_exhausted"


@pytest.mark.asyncio
async def test_discovery_endpoint_graceful_handling():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Discovery should gracefully return empty candidates without 500
        settings.serpapi_enabled = False
        resp = await client.post("/api/discovery/search", json={"query": "Github"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["query"] == "Github"
        assert data["candidates"] == []
