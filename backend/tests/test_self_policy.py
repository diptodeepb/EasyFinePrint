"""Tests for EasyFinePrint self-policy ingestion, dynamic env resolution, exact match hashing, and metadata."""
import pytest
from httpx import ASGITransport, AsyncClient
from app.main import app
from app.config import settings


@pytest.mark.asyncio
async def test_self_policies_metadata():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get("/api/policies/self-policies")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) >= 2
        keys = [p["key"] for p in data]
        assert "terms" in keys
        assert "privacy" in keys
        urls = {p["key"]: p["canonical_url"] for p in data}
        assert urls["terms"] == "/terms"
        assert urls["privacy"] == "/privacy"
        assert "localhost" not in urls["terms"]
        assert "localhost" not in urls["privacy"]


@pytest.mark.asyncio
async def test_analyze_self_terms():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.post("/api/policies/analyze-self", json={"policy_type": "terms"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["canonical_url"] == "/terms"
        assert "localhost" not in data["canonical_url"]
        assert "Terms of Use" in data["title"]
        assert data["latest_snapshot_id"] is not None
        assert data["latest_analysis"] is not None
        policy_id = data["id"]

        # Check for updates on self-policy (exact match -> unchanged, 0 external hops)
        check_resp = await client.post(f"/api/policies/{policy_id}/check")
        assert check_resp.status_code == 200
        check_data = check_resp.json()
        assert check_data["status"] == "unchanged"


@pytest.mark.asyncio
async def test_analyze_self_privacy():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.post("/api/policies/analyze-self", json={"policy_type": "privacy"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["canonical_url"] == "/privacy"
        assert "localhost" not in data["canonical_url"]
        assert "Privacy Policy" in data["title"]
        assert data["latest_snapshot_id"] is not None


@pytest.mark.asyncio
async def test_analyze_url_intercept_self_terms_and_exact_match():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # 1. Ingestion via relative path /terms
        resp1 = await client.post("/api/policies/analyze", json={"url": "/terms"})
        assert resp1.status_code == 200
        data1 = resp1.json()
        assert data1["canonical_url"] == "/terms"
        assert "localhost" not in data1["canonical_url"]
        assert data1["latest_analysis"] is not None
        first_policy_id = data1["id"]
        first_snapshot_id = data1["latest_snapshot_id"]
        first_analysis_id = data1["latest_analysis"]["id"]

        # 2. Re-submitting the exact same policy (even via deployed Vercel URL or localhost) should trigger exact-match reuse (0 AI calls)
        resp2 = await client.post("/api/policies/analyze", json={"url": "http://localhost:5173/terms"})
        assert resp2.status_code == 200
        data2 = resp2.json()
        assert data2["id"] == first_policy_id
        assert data2["canonical_url"] == "/terms"
        assert "localhost" not in data2["canonical_url"]
        assert data2["latest_snapshot_id"] == first_snapshot_id
        assert data2["latest_analysis"]["id"] == first_analysis_id
        assert data2.get("reanalysis_status") == "skipped_unchanged"


@pytest.mark.asyncio
async def test_analyze_url_intercept_self_privacy():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.post("/api/policies/analyze", json={"url": "/privacy"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["canonical_url"] == "/privacy"
        assert "localhost" not in data["canonical_url"]
        assert data["latest_analysis"] is not None
