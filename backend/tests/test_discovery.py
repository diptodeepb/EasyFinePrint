"""Tests for company policy discovery service (authoritative directory and live crawler)."""
import pytest
from app.services.discovery import discover_policy_urls, KNOWN_DIRECTORY, _query_cache


@pytest.mark.asyncio
async def test_known_company_discovery():
    """Verify that known companies (e.g. Discord, Spotify, GitHub) return official policy URLs."""
    res_discord = await discover_policy_urls("Discord")
    assert "candidates" in res_discord
    candidates = res_discord["candidates"]
    assert len(candidates) >= 2
    urls = [c["url"] for c in candidates]
    assert any("discord.com/terms" in u for u in urls)
    assert any("discord.com/privacy" in u for u in urls)


@pytest.mark.asyncio
async def test_case_insensitive_and_trimmed_query():
    """Verify query normalization and caching."""
    _query_cache.clear()
    res1 = await discover_policy_urls("  sPoTiFy  ")
    assert len(res1["candidates"]) >= 2
    assert res1["cached"] is False

    # Second query must hit cache
    res2 = await discover_policy_urls("spotify")
    assert res2["cached"] is True
    assert len(res2["candidates"]) == len(res1["candidates"])


@pytest.mark.asyncio
async def test_unknown_company_discovery_graceful():
    """Verify that unknown company names gracefully return without error."""
    res = await discover_policy_urls("nonexistent-company-xyz-12345")
    assert "candidates" in res
    assert isinstance(res["candidates"], list)


@pytest.mark.asyncio
async def test_discovery_short_query_validation_message():
    """Verify that short query returns human-readable validation error without Pydantic JSON dump."""
    from httpx import ASGITransport, AsyncClient
    from app.main import app

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.post("/api/discovery/search", json={"query": "e"})
        assert resp.status_code == 422
        data = resp.json()
        assert "Please enter at least 2 characters" in data.get("detail", "")
        # Ensure raw JSON array from Pydantic is not dumped
        assert not isinstance(data.get("detail"), list)
