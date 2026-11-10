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


@pytest.mark.asyncio
async def test_known_directory_scale_and_aliases():
    """Verify expanded known directory coverage across AI, fintech, SaaS, and aliases."""
    # Test multiple categories
    res_ai = await discover_policy_urls("OpenAI")
    assert len(res_ai["candidates"]) >= 2
    assert any("openai.com" in c["url"] for c in res_ai["candidates"])

    res_alias_chatgpt = await discover_policy_urls("chatgpt")
    assert any("openai.com" in c["url"] for c in res_alias_chatgpt["candidates"])

    res_alias_fb = await discover_policy_urls("fb")
    assert any("facebook.com" in c["url"] for c in res_alias_fb["candidates"])

    res_stripe = await discover_policy_urls("Stripe")
    assert any("stripe.com" in c["url"] for c in res_stripe["candidates"])

    res_salesforce = await discover_policy_urls("Salesforce")
    assert any("salesforce.com" in c["url"] for c in res_salesforce["candidates"])

    res_starlink = await discover_policy_urls("spacex")
    assert any("starlink.com" in c["url"] for c in res_starlink["candidates"])


@pytest.mark.asyncio
async def test_policy_prioritization():
    """Verify that Terms documents are ranked ahead of other policy documents."""
    res = await discover_policy_urls("Google")
    candidates = res["candidates"]
    assert len(candidates) >= 2
    # First candidate should be Terms of Service
    first_title = candidates[0]["title"].lower()
    assert "terms" in first_title or "service" in first_title


@pytest.mark.asyncio
async def test_discovery_endpoint_response_total():
    """Verify that /api/discovery/search returns total count matching candidates."""
    from httpx import ASGITransport, AsyncClient
    from app.main import app

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.post("/api/discovery/search", json={"query": "Apple"})
        assert resp.status_code == 200
        data = resp.json()
        assert "candidates" in data
        assert "total" in data
        assert data["total"] == len(data["candidates"])
        assert data["total"] >= 2


@pytest.mark.asyncio
async def test_auto_discovery_more_than_five_policies_and_ranking(monkeypatch):
    """
    Verify auto-discovery handles companies with > 5 policies,
    ranks them correctly (Terms -> Privacy -> Cookies -> Other),
    and enforces maximum restriction limits.
    """
    from app.services import discovery as discovery_mod

    # Simulate dynamic discovery returning 8 policy candidates for an unknown company
    mock_candidates = [
        {"title": "Cookie Notice", "url": "https://examplecorp.com/cookies", "snippet": "Cookies info"},
        {"title": "Security Whitepaper", "url": "https://examplecorp.com/security", "snippet": "Security info"},
        {"title": "Terms of Service", "url": "https://examplecorp.com/terms", "snippet": "Terms of service"},
        {"title": "Privacy Policy", "url": "https://examplecorp.com/privacy", "snippet": "Privacy policy"},
        {"title": "Acceptable Use Policy", "url": "https://examplecorp.com/aup", "snippet": "Acceptable use"},
        {"title": "Developer Terms", "url": "https://examplecorp.com/dev-terms", "snippet": "API terms"},
        {"title": "Subprocessor List", "url": "https://examplecorp.com/subprocessors", "snippet": "Vendors"},
        {"title": "Service Level Agreement", "url": "https://examplecorp.com/sla", "snippet": "Uptime guarantee"},
    ]

    async def mock_crawl(base_url):
        return mock_candidates

    monkeypatch.setattr(discovery_mod, "crawl_homepage_for_policy_links", mock_crawl)
    monkeypatch.setattr(discovery_mod, "search_known_directory", lambda q: [])

    # Clear query cache
    discovery_mod._query_cache.clear()

    res = await discovery_mod.discover_policy_urls("examplecorp")
    candidates = res["candidates"]

    # Verify candidate count exceeds 5 (edge case requiring pagination)
    assert len(candidates) >= 6
    assert res["total"] == len(candidates)

    # Verify ranking: Terms must be first, Privacy second
    assert "terms" in candidates[0]["title"].lower()
    assert "privacy" in candidates[1]["title"].lower()


@pytest.mark.asyncio
async def test_e2e_search_for_abc_and_unlisted_companies(monkeypatch):
    """
    End-to-end integration test:
    Simulates searching for 'abc' through the FastAPI HTTP route,
    verifying realistic auto-discovery response, caching behavior,
    and payload structure for frontend progress and pagination.
    """
    from httpx import ASGITransport, AsyncClient
    from app.main import app
    from app.services import discovery as discovery_mod

    # Clear query cache to ensure fresh search
    discovery_mod._query_cache.clear()

    # Simulate dynamic crawl finding 6 policy links for 'abc'
    mock_abc_policies = [
        {"title": "ABC Terms of Use", "url": "https://www.abc.com/terms", "snippet": "Official Terms of Use for ABC"},
        {"title": "ABC Privacy Policy", "url": "https://www.abc.com/privacy", "snippet": "Official Privacy Policy for ABC"},
        {"title": "ABC Cookie Notice", "url": "https://www.abc.com/cookies", "snippet": "Cookie disclosures"},
        {"title": "ABC Subscriber Agreement", "url": "https://www.abc.com/agreement", "snippet": "Subscription terms"},
        {"title": "ABC Security Disclosure", "url": "https://www.abc.com/security", "snippet": "Security guidelines"},
        {"title": "ABC Developer API Agreement", "url": "https://www.abc.com/developer", "snippet": "API usage rules"},
    ]

    async def mock_crawl_abc(base_url):
        return mock_abc_policies

    monkeypatch.setattr(discovery_mod, "crawl_homepage_for_policy_links", mock_crawl_abc)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # 1. First E2E search for "abc"
        resp = await client.post("/api/discovery/search", json={"query": "abc"})
        assert resp.status_code == 200
        data = resp.json()

        assert data["query"] == "abc"
        assert data["cached"] is False
        assert "candidates" in data
        assert data["total"] == 6
        assert len(data["candidates"]) == 6

        # Verify candidate document attributes
        first = data["candidates"][0]
        assert "title" in first
        assert "url" in first
        assert "snippet" in first
        assert "source" in first

        # Verify core Terms and Privacy ranking
        assert "terms" in data["candidates"][0]["title"].lower()
        assert "privacy" in data["candidates"][1]["title"].lower()

        # 2. Second search for "abc" should hit cache
        resp2 = await client.post("/api/discovery/search", json={"query": "abc"})
        assert resp2.status_code == 200
        data2 = resp2.json()
        assert data2["cached"] is True
        assert data2["total"] == 6
        assert len(data2["candidates"]) == 6


@pytest.mark.asyncio
async def test_expanded_consumer_and_media_services():
    """Verify discovery coverage for popular consumer platforms, streaming services, and telecom providers."""
    test_queries = [
        ("meesho", "meesho.com"),
        ("swiggy", "swiggy.com"),
        ("flipkart", "flipkart.com"),
        ("blinkit", "blinkit.com"),
        ("crunchyroll", "crunchyroll.com"),
        ("airtel", "airtel.in"),
        ("vodafone", "myvi.in"),
        ("jio", "jio.com"),
        ("cred", "cred.club"),
        ("zerodha", "zerodha.com"),
        ("prime video", "primevideo.com"),
    ]
    for q, expected_domain in test_queries:
        res = await discover_policy_urls(q)
        assert "candidates" in res
        candidates = res["candidates"]
        assert len(candidates) >= 2, f"Failed for query {q}"
        assert any(expected_domain in c["url"] for c in candidates), f"Domain {expected_domain} not found for {q}"
        assert res["total"] == len(candidates)



