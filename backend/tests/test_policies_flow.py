"""Integration tests for policy tracking, rechecking, and history lifecycle."""
from unittest.mock import patch
import pytest
from httpx import ASGITransport, AsyncClient
from app.main import app
from app.services.extractor import ExtractionError

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
