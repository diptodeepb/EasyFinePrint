"""End-to-End Tests for the 4-Tier Hybrid Ingestion & Diff Engine.

Tests:
1. Tier 3 User-Provided Direct Text Ingestion (valid text >= 100 chars).
2. Tier 3 Short Text Rejection (< 100 chars rejected with 422).
3. Tier 3 Revision & Myers Diff Tracking (updating user-pasted text generates diff).
4. Provenance & Warning Validation (user-pasted badge and disclaimer).
5. Tier 2 Public Web Archive (Wayback Machine) Fallback integration.
6. Tier 4 Zero-Drift Baseline Database Cache Fallback.
"""
from __future__ import annotations
import pytest
from unittest.mock import patch, AsyncMock
from httpx import ASGITransport, AsyncClient

from app.main import app
from app.db.repositories import repo


@pytest.fixture(autouse=True)
def clean_memory_db():
    repo._mem_policies.clear()
    repo._mem_snapshots.clear()
    repo._mem_analyses.clear()
    repo._mem_check_events.clear()
    yield


@pytest.mark.asyncio
async def test_tier3_user_provided_text_ingestion():
    """Verify Tier 3 allows direct pasting of agreement text with provenance tagging."""
    pasted_text = (
        "Welcome to the Acme Cloud Platform. By accessing or using our services, you expressly agree "
        "to be bound by these Terms of Service. Any disputes arising from these terms or your use of "
        "the services shall be resolved through binding confidential individual arbitration rather than court litigation."
    )
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        resp = await ac.post(
            "/api/policies/analyze",
            json={
                "url": "https://example-waf-blocked.com/terms",
                "raw_text": pasted_text,
                "title": "Custom Acme Agreement",
            },
        )
        assert resp.status_code == 200, resp.text
        data = resp.json()
        assert data["title"] == "Custom Acme Agreement"
        assert data["provenance"] == "user_pasted"
        assert any("User-Provided Text" in w for w in data["warnings"])

        # Check analysis response
        latest_analysis = data.get("latest_analysis")
        assert latest_analysis is not None
        assert latest_analysis["provenance"] == "user_pasted"
        assert any("User-Provided Text" in w for w in latest_analysis["warnings"])


@pytest.mark.asyncio
async def test_tier3_short_text_rejection():
    """Verify Tier 3 rejects maliciously short or truncated pasted text (<100 characters)."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        resp = await ac.post(
            "/api/policies/analyze",
            json={
                "url": "https://example.com/terms",
                "raw_text": "This is too short.",
            },
        )
        assert resp.status_code == 422
        assert "suspiciously short (<100 characters)" in resp.json()["detail"]


@pytest.mark.asyncio
async def test_tier3_revision_diff_tracking_on_updated_paste():
    """Verify that submitting an updated paste for an existing URL triggers Myers diffing."""
    v1_text = (
        "Acme Service Agreement Version 1. All disputes shall be resolved through binding individual arbitration. "
        "Users may cancel their recurring subscriptions at any time through the customer dashboard settings."
    )
    v2_text = (
        "Acme Service Agreement Version 2. All disputes shall be resolved through binding individual arbitration. "
        "Users may cancel their subscriptions only by providing a written notarized notice 60 days in advance."
    )

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # Ingest Version 1
        resp1 = await ac.post(
            "/api/policies/analyze",
            json={
                "url": "https://example-diff.com/terms",
                "raw_text": v1_text,
                "title": "Acme Terms",
            },
        )
        assert resp1.status_code == 200
        pol_id = resp1.json()["id"]

        # Ingest Version 2 (modified cancellation clause)
        resp2 = await ac.post(
            "/api/policies/analyze",
            json={
                "url": "https://example-diff.com/terms",
                "raw_text": v2_text,
                "title": "Acme Terms",
            },
        )
        assert resp2.status_code == 200
        data2 = resp2.json()
        assert data2["id"] == pol_id
        analysis = data2["latest_analysis"]
        assert analysis["analysis_type"] == "change"
        assert analysis["provenance"] == "user_pasted"
        # Verify changes were detected by Myers diff engine
        assert len(analysis["changes"]) > 0


@pytest.mark.asyncio
async def test_tier2_wayback_machine_auto_fallback():
    """Verify that when live fetch fails (e.g. WAF block), Tier 2 automatically falls back to Wayback Machine."""
    mock_wayback_html = """
    <html><head><title>Archived Terms of Service</title></head>
    <body>
    <main>
    <h1>Archived Platform Agreement</h1>
    <p>This document is an official archived electronic record of user obligations and rights.</p>
    <p>All registered accounts are strictly personal and non-transferable under applicable laws.</p>
    <p>Disputes must be settled exclusively via binding individual arbitration in accordance with rules.</p>
    </main>
    </body></html>
    """

    with patch("app.routes.policies.safe_fetch_page", side_effect=Exception("WAF 403 Forbidden")), \
         patch("app.routes.policies.fetch_wayback_snapshot", new_callable=AsyncMock) as mock_wb:
        mock_wb.return_value = (mock_wayback_html, "http://web.archive.org/web/20261015/https://waf-blocked.com/terms", "20261015120000")

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            resp = await ac.post(
                "/api/policies/analyze",
                json={"url": "https://waf-blocked.com/terms"},
            )
            assert resp.status_code == 200, resp.text
            data = resp.json()
            assert data["provenance"] == "archive"
            assert any("Internet Archive" in w for w in data["warnings"])
            assert "Archived" in data["title"]


@pytest.mark.asyncio
async def test_tier4_cached_baseline_fallback():
    """Verify that if both live scrape and archive fail, Tier 4 serves the cached verified baseline."""
    # Seed baseline in memory DB
    pol = await repo.create_policy(
        url="https://offline-service.com/privacy",
        canonical_url="https://offline-service.com/privacy",
        title="Offline Privacy Policy",
    )
    snap = await repo.create_snapshot(
        policy_id=pol["id"],
        content_hash="mockhash12345",
        extracted_text="We collect diagnostic telemetry and never sell personal identification data to third-party brokers.",
        extractor="http",
        extraction_status="success",
        source_status_code=200,
        title="Offline Privacy Policy",
    )
    await repo.create_analysis(
        policy_id=pol["id"],
        analysis_type="initial",
        new_snapshot_id=snap["id"],
        summary="Baseline telemetry audit.",
        findings=[],
        changes=[],
        model_id="mock-model",
        validation_status="passed",
    )

    with patch("app.routes.policies.safe_fetch_page", side_effect=Exception("Connection timed out")), \
         patch("app.routes.policies.fetch_wayback_snapshot", new_callable=AsyncMock) as mock_wb:
        mock_wb.return_value = None  # No archive available

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            resp = await ac.post(
                "/api/policies/analyze",
                json={"url": "https://offline-service.com/privacy"},
            )
            assert resp.status_code == 200, resp.text
            data = resp.json()
            assert data["id"] == pol["id"]
            assert data["reanalysis_status"] == "cached_fallback"
            assert data["provenance"] == "cached_fallback"
            assert any("database" in w for w in data["warnings"])


@pytest.mark.asyncio
async def test_list_policies_provenance_and_tab_segmentation():
    """Verify GET /api/policies returns provenance for system-maintained vs user-maintained segmentation."""
    # 1. Ingest a User-Maintained policy (Tier 3 Paste)
    user_pasted_text = (
        "Acme User-Provided Agreement. By using this private intranet tool, you agree to these terms. "
        "All data processed remains within the enterprise boundary and any disputes are handled internally."
    )
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        user_resp = await ac.post(
            "/api/policies/analyze",
            json={
                "url": "https://internal-portal.corp/terms",
                "raw_text": user_pasted_text,
                "title": "Internal Corp Terms",
            },
        )
        assert user_resp.status_code == 200

        # 2. Ingest a System-Maintained policy (Self Policy)
        sys_resp = await ac.post(
            "/api/policies/analyze-self",
            json={"policy_type": "terms"},
        )
        assert sys_resp.status_code == 200

        # 3. Call GET /api/policies
        list_resp = await ac.get("/api/policies")
        assert list_resp.status_code == 200
        policies = list_resp.json()
        assert len(policies) == 2

        user_policies = [p for p in policies if p.get("provenance") == "user_pasted"]
        system_policies = [p for p in policies if p.get("provenance") != "user_pasted"]

        assert len(user_policies) == 1
        assert user_policies[0]["title"] == "Internal Corp Terms"

        assert len(system_policies) == 1
        assert "EasyFinePrint" in system_policies[0]["title"]


@pytest.mark.asyncio
async def test_tier3_auto_derived_title_from_url():
    """Verify title is auto-derived from URL if omitted when submitting direct paste text."""
    raw_text = (
        "Welcome to CloudPlatform. Under these terms, the company disclaims all liability for incidental, "
        "punsequential, or special damages arising from service interruption. The company retains a non-exclusive, "
        "royalty-free worldwide license to use and train systems on all content submitted by the customer. "
        "Either party may terminate this agreement with 30 days written notice, but fees are strictly non-refundable."
    )
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        resp = await ac.post(
            "/api/policies/analyze",
            json={
                "url": "https://serviceportal.io/terms",
                "raw_text": raw_text,
                # title intentionally omitted to test auto-derivation
            },
        )
        assert resp.status_code == 200, resp.text
        data = resp.json()
        assert data["title"] == "Serviceportal Terms of Service"
        assert data["provenance"] == "user_pasted"


@pytest.mark.asyncio
async def test_tier3_rejects_user_paste_when_url_exists_in_system_maintained():
    """Verify Tier 3 rejects user-maintained text paste if URL is already system-maintained,

    including URL canonicalization tricks (trailing slash, www prefix, http vs https, case, ports, queries).
    """
    system_url = "https://globalcorp.com/terms"
    pasted_text = (
        "GlobalCorp Official Service Agreement. By using this service you agree to our standard terms. "
        "All disputes shall be settled through our designated mediation process. Termination requires 30 days notice."
    )

    # 1. Seed a system-maintained policy in repo
    await repo.create_policy(
        url=system_url,
        canonical_url=system_url,
        title="GlobalCorp Terms",
        provenance="live",
    )

    # 2. Attempt to submit user-pasted text using exact URL -> Should be rejected with 400
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        resp = await ac.post(
            "/api/policies/analyze",
            json={
                "url": system_url,
                "raw_text": pasted_text,
            },
        )
        assert resp.status_code == 400
        assert "already exists as a system-maintained policy" in resp.json()["detail"]

        # 3. Test trick variations that users might attempt
        trick_urls = [
            "https://globalcorp.com/terms/",            # trailing slash
            "http://globalcorp.com/terms",              # http instead of https
            "https://www.globalcorp.com/terms",         # www prefix
            "https://GLOBALCORP.COM/terms",             # uppercase domain
            "https://globalcorp.com:443/terms/",        # explicit default port
            "https://globalcorp.com/terms?ref=promo",   # query parameter
            "https://globalcorp.com/terms#section-1",   # hash fragment
        ]

        for trick_url in trick_urls:
            trick_resp = await ac.post(
                "/api/policies/analyze",
                json={
                    "url": trick_url,
                    "raw_text": pasted_text,
                },
            )
            assert trick_resp.status_code == 400, f"Trick URL {trick_url} was not blocked! Status: {trick_resp.status_code}"
            assert "already exists as a system-maintained policy" in trick_resp.json()["detail"]

        # 4. Self-policies (/terms, /privacy) must also be blocked from user paste
        for self_url in ("/terms", "/terms/", "/privacy", "/privacy/"):
            self_resp = await ac.post(
                "/api/policies/analyze",
                json={
                    "url": self_url,
                    "raw_text": pasted_text,
                },
            )
            assert self_resp.status_code == 400
            assert "system-maintained policy" in self_resp.json()["detail"]


@pytest.mark.asyncio
async def test_max_char_limits_for_url_and_title():
    """Verify strict anti-spam max character limits on URL (2,048) and Agreement Title (200)."""
    valid_text = (
        "Acme Service Agreement. By using our service you agree to our standard terms and conditions. "
        "All disputes shall be settled through our designated mediation process. Termination requires 30 days notice."
    )

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # 1. URL exceeding 2,048 characters should be rejected with 422
        long_url = "https://example.com/terms/" + ("a" * 2050)
        resp_long_url = await ac.post(
            "/api/policies/analyze",
            json={
                "url": long_url,
                "raw_text": valid_text,
            },
        )
        assert resp_long_url.status_code == 422

        # 2. Title exceeding 200 characters should be rejected with 422
        long_title = "A" * 205
        resp_long_title = await ac.post(
            "/api/policies/analyze",
            json={
                "url": "https://valid-portal.com/terms",
                "raw_text": valid_text,
                "title": long_title,
            },
        )
        assert resp_long_title.status_code == 422

        # 3. Valid URL and Title within limits succeed
        valid_title = "Standard Service Agreement (2026)"
        resp_valid = await ac.post(
            "/api/policies/analyze",
            json={
                "url": "https://valid-portal.com/terms",
                "raw_text": valid_text,
                "title": valid_title,
            },
        )
        assert resp_valid.status_code == 200
        assert resp_valid.json()["title"] == valid_title
