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


@pytest.mark.asyncio
async def test_delete_policy_lifecycle():
    """Verify that deleting a tracked policy cascades and cleans up all related records."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Create a self-policy record
        resp = await client.post("/api/policies/analyze-self", json={"policy_type": "terms"})
        assert resp.status_code == 200
        pol_id = resp.json()["id"]

        # Verify it exists
        resp_get = await client.get(f"/api/policies/{pol_id}")
        assert resp_get.status_code == 200

        # Delete it
        resp_del = await client.delete(f"/api/policies/{pol_id}")
        assert resp_del.status_code == 200
        assert resp_del.json()["status"] == "deleted"

        # Verify 404 after deletion
        resp_after = await client.get(f"/api/policies/{pol_id}")
        assert resp_after.status_code == 404


@pytest.mark.asyncio
async def test_list_policies_with_details_zero_n_plus_one():
    """Verify list_policies_with_details returns pre-joined details without N+1 repository loops."""
    from app.db.repositories import repo
    from unittest.mock import patch

    # 1. Clear and populate repository with multiple policies
    await repo.clear_all_data()

    p1 = await repo.create_policy("https://example.com/terms", "https://example.com/terms", "Terms A", provenance="live")
    s1 = await repo.create_snapshot(p1["id"], "hash1", "Snapshot text 1", "test", "success", 200, "Terms A", provenance="live")
    a1 = await repo.create_analysis(
        p1["id"], "initial", s1["id"], "Summary 1", [], [], "model1", "passed", risk_score=25, risk_level="low", provenance="live"
    )

    p2 = await repo.create_policy("https://example.org/privacy", "https://example.org/privacy", "Privacy B", provenance="user_pasted")
    s2 = await repo.create_snapshot(p2["id"], "hash2", "Snapshot text 2", "user_pasted", "success", 200, "Privacy B", provenance="user_pasted")
    a2 = await repo.create_analysis(
        p2["id"], "initial", s2["id"], "Summary 2", [], [], "model1", "passed", risk_score=75, risk_level="high", provenance="user_pasted"
    )

    # 2. Call list_policies_with_details directly
    results = await repo.list_policies_with_details(limit=10)
    assert len(results) == 2
    r_map = {r["id"]: r for r in results}

    assert r_map[p1["id"]]["latest_analysis"]["risk_score"] == 25
    assert r_map[p1["id"]]["provenance"] == "live"

    assert r_map[p2["id"]]["latest_analysis"]["risk_score"] == 75
    assert r_map[p2["id"]]["provenance"] == "user_pasted"

    # 3. Test through HTTP GET /api/policies and ensure no N+1 calls to get_snapshot_by_id or get_latest_analysis_for_policy
    with patch.object(repo, "get_snapshot_by_id") as mock_get_snap, \
         patch.object(repo, "get_latest_analysis_for_policy") as mock_get_analysis:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.get("/api/policies")
            assert resp.status_code == 200
            data = resp.json()
            assert len(data) == 2
            # Crucial verification: N+1 loop methods must NEVER be called!
            mock_get_snap.assert_not_called()
            mock_get_analysis.assert_not_called()


@pytest.mark.asyncio
async def test_list_policies_with_details_mongo_aggregation_pipeline():
    """Verify that when MongoDB is active, list_policies_with_details executes the single aggregation pipeline."""
    from app.db.repositories import repo
    from unittest.mock import patch, MagicMock

    class AsyncMockCursor:
        def __init__(self, docs):
            self.docs = docs
            self.idx = 0

        def __aiter__(self):
            return self

        async def __anext__(self):
            if self.idx < len(self.docs):
                item = self.docs[self.idx]
                self.idx += 1
                return item
            raise StopAsyncIteration

    mock_raw_mongo_doc = {
        "_id": "pol_100",
        "id": "pol_100",
        "url": "https://company.test/terms",
        "canonical_url": "https://company.test/terms",
        "title": "Company Terms",
        "status": "active",
        "created_at": "2026-01-01T00:00:00Z",
        "last_checked_at": "2026-01-02T00:00:00Z",
        "latest_snapshot_id": "snp_100",
        "latest_analysis_docs": [
            {
                "_id": "ana_100",
                "id": "ana_100",
                "policy_id": "pol_100",
                "analysis_type": "initial",
                "new_snapshot_id": "snp_100",
                "summary": "Mongo summary",
                "risk_score": 42,
                "risk_level": "moderate",
                "findings": [],
                "changes": [],
                "model_id": "gemma",
                "created_at": "2026-01-02T00:00:00Z",
                "validation_status": "passed",
                "provenance": "live",
                "warnings": [],
            }
        ],
        "latest_snapshot_docs": [
            {
                "_id": "snp_100",
                "provenance": "live",
            }
        ],
    }

    mock_db = MagicMock()
    mock_collection = MagicMock()
    mock_cursor = AsyncMockCursor([dict(mock_raw_mongo_doc)])
    mock_collection.aggregate.return_value = mock_cursor
    mock_db.__getitem__.return_value = mock_collection

    with patch.object(repo, "_use_mongo", return_value=True), \
         patch("app.db.repositories.get_db", return_value=mock_db):
        results = await repo.list_policies_with_details(limit=25)
        assert len(results) == 1
        item = results[0]
        assert item["id"] == "pol_100"
        assert item["latest_analysis"]["risk_score"] == 42
        assert item["provenance"] == "live"

        # Verify aggregate was called with $lookup pipeline
        mock_collection.aggregate.assert_called_once()
        pipeline_arg = mock_collection.aggregate.call_args[0][0]
        stages = [list(stage.keys())[0] for stage in pipeline_arg]
        assert "$sort" in stages
        assert "$limit" in stages
        assert "$lookup" in stages


@pytest.mark.asyncio
async def test_legacy_snapshot_with_zwj_reports_unchanged_on_check():
    """Legacy DB snapshots containing U+200D ZWJ characters should not trigger false diffs on check or re-ingest."""
    import uuid
    from app.routes import policies as policies_mod
    from app.db.repositories import repo
    from app.main import app

    slug = uuid.uuid4().hex[:8]
    url = f"https://discord-test-{slug}.example/terms"
    legacy_text = (
        "\u200dIMPORTANT NOTE: Disputes are governed by arbitration.\u200d\n"
        "\u200dArbitration Rules. Standard rules apply.\n"
        "\u200dOpt-out. Email within 30 days."
    )
    clean_html = (
        "<html><head><title>Discord Terms</title></head><body><main>"
        "<p>IMPORTANT NOTE: Disputes are governed by arbitration.</p>"
        "<p>Arbitration Rules. Standard rules apply.</p>"
        "<p>Opt-out. Email within 30 days.</p>"
        "</main></body></html>"
    )

    pol = await repo.create_policy(url=url, canonical_url=url, title="Discord Terms")
    # Simulate a snapshot saved prior to ZWJ stripping (legacy hash + raw text with U+200D)
    snap = await repo.create_snapshot(
        policy_id=pol["id"],
        content_hash="legacy_hash_with_zwj_" + slug,
        extracted_text=legacy_text,
        extractor="http",
        extraction_status="success",
        source_status_code=200,
        title="Discord Terms",
        provenance="live",
        warnings=[],
    )
    await repo.create_analysis(
        policy_id=pol["id"],
        analysis_type="initial",
        new_snapshot_id=snap["id"],
        summary="Baseline summary",
        risk_score=40,
        risk_level="moderate",
        findings=[],
        changes=[],
        model_id="gemma",
        validation_status="passed",
        provenance="live",
        warnings=[],
    )
    await repo.update_policy(pol["id"], {"latest_snapshot_id": snap["id"]})

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        with patch("app.routes.policies.safe_fetch_page", return_value=(clean_html, url, 200)), \
             patch.object(policies_mod, "explain_policy_changes", side_effect=AssertionError("Should not run AI diff")) :
            check_resp = await client.post(f"/api/policies/{pol['id']}/check")
            assert check_resp.status_code == 200
            assert check_resp.json()["status"] == "unchanged"

            reingest_resp = await client.post("/api/policies/analyze", json={"url": url})
            assert reingest_resp.status_code == 200
            assert reingest_resp.json()["reanalysis_status"] == "skipped_unchanged"





