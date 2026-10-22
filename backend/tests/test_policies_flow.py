"""Integration tests for policy tracking, rechecking, and history lifecycle."""
import uuid
from unittest.mock import patch
import pytest
from httpx import ASGITransport, AsyncClient
from app.main import app
from app.services.extractor import ExtractionError
from app.routes import policies as policies_mod

MOCK_HTML_V1 = """
<!DOCTYPE html>
<html>
<head><title>Acme Privacy Policy</title></head>
<body>
<main>
<h1>Acme Privacy Policy</h1>
<p>Effective Date: January 1, 2026</p>
<p>We collect basic email addresses when you register for an account.</p>
<p>We do not sell personal information to third parties.</p>
</main>
</body>
</html>
"""

MOCK_HTML_V2 = """
<!DOCTYPE html>
<html>
<head><title>Acme Privacy Policy</title></head>
<body>
<main>
<h1>Acme Privacy Policy</h1>
<p>Effective Date: October 20, 2026</p>
<p>We collect basic email addresses and precise geolocation data continuously.</p>
<p>We may share aggregated behavioral analytics with trusted promotional partners.</p>
</main>
</body>
</html>
"""


@pytest.mark.asyncio
async def test_policy_full_lifecycle():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # 1. Analyze initial policy URL
        with patch("app.routes.policies.safe_fetch_page", return_value=(MOCK_HTML_V1, "https://acme.test/privacy", 200)):
            resp1 = await client.post("/api/policies/analyze", json={"url": "https://acme.test/privacy"})
            assert resp1.status_code == 200
            data1 = resp1.json()
            policy_id = data1["id"]
            assert data1["canonical_url"] == "https://acme.test/privacy"
            assert data1["latest_snapshot_id"] is not None
            snap1_id = data1["latest_snapshot_id"]
            assert data1["latest_analysis"] is not None

        # 2. Check for updates when unchanged
        with patch("app.routes.policies.safe_fetch_page", return_value=(MOCK_HTML_V1, "https://acme.test/privacy", 200)):
            resp2 = await client.post(f"/api/policies/{policy_id}/check")
            assert resp2.status_code == 200
            data2 = resp2.json()
            assert data2["status"] == "unchanged"
            assert data2["old_snapshot_id"] == snap1_id
            assert data2["new_snapshot_id"] == snap1_id

        # 3. Check for updates when extraction fails (e.g. 500 error / timeout)
        # Should record failure and preserve old baseline!
        with patch("app.routes.policies.safe_fetch_page", side_effect=ExtractionError("Target server returned HTTP status 503")):
            resp3 = await client.post(f"/api/policies/{policy_id}/check")
            assert resp3.status_code == 200
            data3 = resp3.json()
            assert data3["status"] == "extraction_failed"
            assert "HTTP status 503" in data3["message"]
            assert data3["old_snapshot_id"] == snap1_id

        # Verify policy still has original snapshot as latest!
        pol_check = await client.get(f"/api/policies/{policy_id}")
        assert pol_check.status_code == 200
        assert pol_check.json()["latest_snapshot_id"] == snap1_id

        # 4. Check for updates when text changed
        with patch("app.routes.policies.safe_fetch_page", return_value=(MOCK_HTML_V2, "https://acme.test/privacy", 200)):
            resp4 = await client.post(f"/api/policies/{policy_id}/check")
            assert resp4.status_code == 200
            data4 = resp4.json()
            assert data4["status"] == "changed"
            assert data4["new_snapshot_id"] != snap1_id
            assert data4["diff_summary"]["total_changes"] >= 1

        # 5. Verify history lists all events
        resp_hist = await client.get(f"/api/policies/{policy_id}/history")
        assert resp_hist.status_code == 200
        events = resp_hist.json()
        assert len(events) >= 3  # initial, unchanged, extraction_failed, changed
        statuses = [e["status"] for e in events]
        assert "unchanged" in statuses
        assert "extraction_failed" in statuses
        assert "changed" in statuses


@pytest.mark.asyncio
async def test_character_for_character_match_bypasses_analysis():
    """Verify that submitting the same policy URL with identical extracted text reuses the baseline instantly without re-invoking AI analysis."""
    from app.routes import policies as policies_mod
    import uuid
    test_slug = uuid.uuid4().hex[:8]
    test_url = f"https://exactmatch-{test_slug}.test/terms"

    unique_html = f"""
    <!DOCTYPE html>
    <html>
    <head><title>Beta Terms of Service {test_slug}</title></head>
    <body>
    <main>
    <h1>Beta Terms of Service Agreement {test_slug}</h1>
    <p>Effective Date: November 15, 2026</p>
    <p>We process your profile data to provide seamless account authentication.</p>
    <p>All dispute arbitrations will be governed under California jurisdiction.</p>
    <p>Subscription payments renew automatically on the first day of each calendar month.</p>
    </main>
    </body>
    </html>
    """
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        with patch("app.routes.policies.safe_fetch_page", return_value=(unique_html, test_url, 200)), \
             patch("app.routes.policies.analyze_policy_risk", wraps=policies_mod.analyze_policy_risk) as mock_analyze:

            # 1. First submission: creates baseline
            resp1 = await client.post("/api/policies/analyze", json={"url": test_url})
            assert resp1.status_code == 200
            data1 = resp1.json()
            initial_snap_id = data1["latest_snapshot_id"]
            initial_score = data1["latest_analysis"]["risk_score"]
            initial_level = data1["latest_analysis"]["risk_level"]
            assert mock_analyze.call_count == 1

            # 2. Second submission with the exact same text / URL:
            # Must detect character-for-character match, bypass analyze_policy_risk (call_count remains 1),
            # return identical score, identical tier, and identical snapshot id.
            resp2 = await client.post("/api/policies/analyze", json={"url": f"{test_url}/"})
            assert resp2.status_code == 200
            data2 = resp2.json()

            assert data2["id"] == data1["id"]
            assert data2["latest_snapshot_id"] == initial_snap_id
            assert data2["latest_analysis"]["risk_score"] == initial_score
            assert data2["latest_analysis"]["risk_level"] == initial_level
            # Crucial requirement: AI analysis was NOT called a second time
            assert mock_analyze.call_count == 1

            # Verify history records unchanged event
            resp_hist = await client.get(f"/api/policies/{data1['id']}/history")
            assert resp_hist.status_code == 200
            events = resp_hist.json()
            assert any(e["status"] == "unchanged" for e in events)


@pytest.mark.asyncio
async def test_reanalyze_skipped_when_text_unchanged():
    """Verify that POST /api/policies/{id}/reanalyze skips AI execution and preserves score when unchanged."""
    test_slug = uuid.uuid4().hex[:8]
    test_url = f"https://reanalyze-{test_slug}.test/terms"
    sample_html = f"""<!DOCTYPE html>
    <html>
    <head><title>Reanalyze Test {test_slug}</title></head>
    <body>
    <main>
    <h1>Reanalyze Agreement {test_slug}</h1>
    <p>Effective Date: December 1, 2026. Please read this agreement carefully.</p>
    <p>All claims, controversies, and legal disputes between you and the company must be submitted to binding individual arbitration within 1 year.</p>
    <p>Subscriptions automatically renew at standard rates unless cancelled prior to the billing cycle.</p>
    </main>
    </body>
    </html>
    """
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        with patch("app.routes.policies.safe_fetch_page", return_value=(sample_html, test_url, 200)), \
             patch("app.routes.policies.analyze_policy_risk", wraps=policies_mod.analyze_policy_risk) as mock_analyze:

            # 1. Initial analysis
            resp1 = await client.post("/api/policies/analyze", json={"url": test_url})
            assert resp1.status_code == 200
            data1 = resp1.json()
            policy_id = data1["id"]
            original_score = data1["latest_analysis"]["risk_score"]
            assert mock_analyze.call_count == 1

            # 2. Re-analyze without changes: MUST skip AI call, preserve score and return skipped_unchanged
            resp_re = await client.post(f"/api/policies/{policy_id}/reanalyze")
            assert resp_re.status_code == 200
            data_re = resp_re.json()
            assert data_re["reanalysis_status"] == "skipped_unchanged"
            assert data_re["latest_analysis"]["risk_score"] == original_score
            # mock_analyze call count must remain 1 (no new AI execution)
            assert mock_analyze.call_count == 1

            # 3. Attempting to bypass with ?force=true: MUST still be ignored and skipped
            resp_force = await client.post(f"/api/policies/{policy_id}/reanalyze?force=true")
            assert resp_force.status_code == 200
            data_force = resp_force.json()
            assert data_force["reanalysis_status"] == "skipped_unchanged"
            assert data_force["latest_analysis"]["risk_score"] == original_score
            # mock_analyze call count must strictly remain 1
            assert mock_analyze.call_count == 1


@pytest.mark.asyncio
async def test_security_protections_and_nosql_mitigation():
    """Verify security headers, NoSQL injection rejection, and SSRF blocking."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # 1. Security Headers verification
        resp_root = await client.get("/")
        assert resp_root.status_code == 200
        assert resp_root.headers.get("X-Content-Type-Options") == "nosniff"
        assert resp_root.headers.get("X-Frame-Options") == "DENY"
        assert "max-age" in resp_root.headers.get("Strict-Transport-Security", "")
        assert "none" in resp_root.headers.get("Content-Security-Policy", "")

        # 2. NoSQL injection attempt on policy_id (illegal characters, operator injection)
        malicious_ids = [
            "pol_$ne_null",
            "pol_{$gt:''}",
            "pol_123'OR'1'='1",
            "pol_123;DROP TABLE",
        ]
        for bad_id in malicious_ids:
            resp_bad = await client.get(f"/api/policies/{bad_id}")
            # Strict regex pattern validation rejects with 422 before touching the DB
            assert resp_bad.status_code == 422

        # 3. SSRF attempt on analyze endpoint
        resp_ssrf = await client.post("/api/policies/analyze", json={"url": "http://169.254.169.254/latest/meta-data/"})
        assert resp_ssrf.status_code == 400
        assert "blocked" in resp_ssrf.json().get("detail", "").lower() or "forbidden" in resp_ssrf.json().get("detail", "").lower()


