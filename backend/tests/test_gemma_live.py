"""Live Gemma API test for single-pass policy clause analysis via Cloudflare Workers AI.

Gracefully skipped in GitHub Actions CI or when CLOUDFLARE_API_TOKEN / CLOUDFLARE_ACCOUNT_ID
is unconfigured, while running when valid credentials are provided.
"""
import os
import pytest
from app.services.gemma import analyze_policy_risk, is_ai_configured


@pytest.mark.asyncio
async def test_live_gemma_single_pass_analysis():
    # Gracefully skip only in CI or if Cloudflare credentials are not configured
    if os.getenv("GITHUB_ACTIONS") or not is_ai_configured():
        pytest.skip("Running in GitHub Actions environment or Cloudflare Workers AI credentials unconfigured; skipping live Gemma test.")

    sample_policy = """
    Acme Cloud Platform Terms of Service
    Effective Date: October 2026.

    1. Mandatory Arbitration and Class Action Waiver
    You agree that all claims, disputes, or controversies between you and Acme shall be resolved exclusively through binding individual arbitration administered by the American Arbitration Association, and you expressly waive any right to bring or participate in any class, collective, or representative proceeding.

    2. Unilateral Terms Modification
    Acme reserves the right to amend, update, or replace any portion of these Terms of Service at any time in its sole discretion without prior written notice to you. Your continued use of the platform following the posting of changes constitutes full acceptance.

    3. Automatic Renewal and Subscription Billing
    All subscription plans automatically renew at the end of each billing cycle for consecutive periods unless canceled at least 48 hours prior to the renewal date. You authorize recurring charges to your payment method.
    """

    res = await analyze_policy_risk(sample_policy)
    assert "findings" in res
    assert "gemma-4" in res["model_id"] or res["model_id"].startswith("@cf/")
    assert res["validation_status"] in ["passed", "partial"]
    assert len(res["findings"]) >= 1

    # Verify at least one finding has a verified verbatim quotation
    quotes = [f.get("exact_excerpt") for f in res["findings"] if f.get("exact_excerpt")]
    assert len(quotes) >= 1
