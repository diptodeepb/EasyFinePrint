"""Tests for Cross-Origin Resource Sharing (CORS) preflights and production origin rules."""
import pytest
from httpx import ASGITransport, AsyncClient
from app.main import app


@pytest.mark.asyncio
async def test_cors_localhost_post_preflight():
    """Verify OPTIONS preflight succeeds for POST requests from localhost."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        res = await client.options(
            "/api/policies/analyze",
            headers={
                "Origin": "http://localhost:5173",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "content-type",
            },
        )
        assert res.status_code == 200
        assert res.headers.get("access-control-allow-origin") == "http://localhost:5173"
        assert "POST" in res.headers.get("access-control-allow-methods", "")
        assert res.headers.get("access-control-allow-credentials") == "true"


@pytest.mark.asyncio
async def test_cors_localhost_delete_preflight():
    """Verify OPTIONS preflight succeeds for DELETE requests (cascade policy deletion)."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        res = await client.options(
            "/api/policies/pol_test_123",
            headers={
                "Origin": "http://localhost:5173",
                "Access-Control-Request-Method": "DELETE",
                "Access-Control-Request-Headers": "content-type",
            },
        )
        assert res.status_code == 200
        assert res.headers.get("access-control-allow-origin") == "http://localhost:5173"
        assert "DELETE" in res.headers.get("access-control-allow-methods", "")


@pytest.mark.asyncio
async def test_cors_vercel_preview_branch_preflight():
    """Verify that dynamic Vercel preview deployment origins match regex and pass preflight."""
    preview_origin = "https://easyfineprint-git-feature-preview.vercel.app"
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        res = await client.options(
            "/api/policies/analyze",
            headers={
                "Origin": preview_origin,
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "content-type",
            },
        )
        assert res.status_code == 200
        assert res.headers.get("access-control-allow-origin") == preview_origin


@pytest.mark.asyncio
async def test_cors_production_domain_preflight():
    """Verify that production canonical domain passes preflight."""
    prod_origin = "https://easyfineprint.vercel.app"
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        res = await client.options(
            "/api/health",
            headers={
                "Origin": prod_origin,
                "Access-Control-Request-Method": "GET",
            },
        )
        assert res.status_code == 200
        assert res.headers.get("access-control-allow-origin") == prod_origin


@pytest.mark.asyncio
async def test_cors_untrusted_origin_rejected():
    """Verify that unauthorized origins are not granted access-control-allow-origin headers."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        res = await client.options(
            "/api/policies/analyze",
            headers={
                "Origin": "https://malicious-external-site.com",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "content-type",
            },
        )
        # Unauthorized origin must not have access-control-allow-origin header
        assert "access-control-allow-origin" not in res.headers

