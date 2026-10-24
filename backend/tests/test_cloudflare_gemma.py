"""Unit tests for Cloudflare Workers AI integration and Gemma 4 model inference."""
from unittest.mock import patch, AsyncMock
import pytest
from app.services.gemma import (
    get_cloudflare_api_token,
    get_cloudflare_account_id,
    get_cloudflare_model,
    is_ai_configured,
    _extract_text_from_cf_response,
    verify_cloudflare_token,
    analyze_policy_risk,
    explain_policy_changes,
    inspect_quota_error,
    compute_risk_score,
)

SAMPLE_POLICY = """
Acme Cloud Platform Terms of Service
Effective Date: October 2026.

1. Mandatory Arbitration and Class Action Waiver
You agree that all claims, disputes, or controversies between you and Acme shall be resolved exclusively through binding individual arbitration administered by the American Arbitration Association, and you expressly waive any right to bring or participate in any class, collective, or representative proceeding.

2. Unilateral Terms Modification
Acme reserves the right to amend, update, or replace any portion of these Terms of Service at any time in its sole discretion without prior written notice to you. Your continued use of the platform following the posting of changes constitutes full acceptance.

3. Automatic Renewal and Subscription Billing
All subscription plans automatically renew at the end of each billing cycle for consecutive periods unless canceled at least 48 hours prior to the renewal date. You authorize recurring charges to your payment method.
"""

MOCK_CF_AI_RESPONSE = """{
  "summary": "Acme imposes binding arbitration, unilateral term modifications, and automatic subscription renewals.",
  "findings": [
    {
      "category": "disputes",
      "severity": "high",
      "exact_excerpt": "You agree that all claims, disputes, or controversies between you and Acme shall be resolved exclusively through binding individual arbitration administered by the American Arbitration Association, and you expressly waive any right to bring or participate in any class, collective, or representative proceeding.",
      "explanation": "Mandatory individual arbitration waives your right to court proceedings and class actions.",
      "why_it_might_matter": "You cannot join other consumers to sue over unfair fees.",
      "uncertainty": null
    },
    {
      "category": "renewal",
      "severity": "high",
      "exact_excerpt": "All subscription plans automatically renew at the end of each billing cycle for consecutive periods unless canceled at least 48 hours prior to the renewal date.",
      "explanation": "Subscriptions automatically renew unless cancelled at least 48 hours in advance.",
      "why_it_might_matter": "You may be billed for another period if cancellation is delayed.",
      "uncertainty": null
    }
  ]
}"""


def test_model_name_resolution():
    with patch.dict("os.environ", {"CLOUDFLARE_AI_MODEL": "@cf/google/gemma-4-26b-a4b-it"}):
        assert get_cloudflare_model() == "@cf/google/gemma-4-26b-a4b-it"

    with patch.dict("os.environ", {"CLOUDFLARE_AI_MODEL": "gemma-4-26b-a4b-it"}):
        assert get_cloudflare_model() == "@cf/google/gemma-4-26b-a4b-it"


def test_extract_text_from_cf_response():
    # 1. Standard Cloudflare result format
    resp1 = {
        "result": {
            "response": '{"summary": "Test policy summary"}'
        },
        "success": True,
    }
    assert _extract_text_from_cf_response(resp1) == '{"summary": "Test policy summary"}'

    # 2. Reasoning model output with <think> tags stripped
    resp2 = {
        "result": {
            "response": '<think>Analyzing clauses...</think>{"summary": "Clean JSON"}'
        }
    }
    assert _extract_text_from_cf_response(resp2) == '{"summary": "Clean JSON"}'

    # 3. Direct string result
    resp3 = {"result": "Plain result string"}
    assert _extract_text_from_cf_response(resp3) == "Plain result string"

    # 4. Empty / None
    assert _extract_text_from_cf_response(None) == ""


def test_inspect_quota_error():
    assert inspect_quota_error(Exception("401 Unauthorized"))[0] == "auth"
    assert inspect_quota_error(Exception("403 Forbidden: Workers AI - Read permission needed"))[0] == "auth"
    assert inspect_quota_error(Exception("HTTP 429 Too Many Requests"))[0] == "quota"
    assert inspect_quota_error(Exception("504 Gateway Timeout"))[0] == "timeout"


@pytest.mark.asyncio
async def test_verify_cloudflare_token_mock():
    mock_success_response = {
        "result": {"id": "token_123", "status": "active"},
        "success": True,
        "errors": [],
        "messages": [{"code": 10000, "message": "This API Token is valid and active"}]
    }

    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        from unittest.mock import MagicMock
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = mock_success_response
        mock_get.return_value = mock_resp

        res = await verify_cloudflare_token("mock_api_token")
        assert res["valid"] is True
        assert res["status"] == "active"


@pytest.mark.asyncio
async def test_fallback_when_unconfigured():
    with patch("app.services.gemma.is_ai_configured", return_value=False):
        res = await analyze_policy_risk(SAMPLE_POLICY)
        assert res["model_id"] == "deterministic-fallback"
        assert res["validation_status"] == "skipped"
        assert res["risk_score"] is None
        assert res["findings"] == []


@pytest.mark.asyncio
async def test_analyze_policy_risk_with_cf_mock():
    with patch("app.services.gemma.is_ai_configured", return_value=True), \
         patch("app.services.gemma.get_cloudflare_model", return_value="@cf/google/gemma-4-26b-a4b-it"), \
         patch("app.services.gemma.call_cloudflare_ai", new_callable=AsyncMock) as mock_call:

        mock_call.return_value = MOCK_CF_AI_RESPONSE

        res = await analyze_policy_risk(SAMPLE_POLICY)
        assert res["model_id"] == "@cf/google/gemma-4-26b-a4b-it"
        assert res["validation_status"] in ("passed", "partial")
        assert len(res["findings"]) == 2
        assert len(res["findings"][0]["exact_excerpt"]) >= 15
        assert res["risk_score"] is not None
        assert res["risk_level"] in ("high", "elevated", "moderate")


@pytest.mark.asyncio
async def test_explain_policy_changes_with_cf_mock():
    mock_diff = {
        "summary": {"total_changes": 1, "additions": 1, "removals": 0, "modifications": 0},
        "changes": [
            {
                "change_id": "diff_1",
                "change_type": "addition",
                "old_text": "",
                "new_text": "You authorize recurring charges to your payment method.",
            }
        ]
    }

    mock_change_ai_response = """{
      "summary": "Recurring billing authorization added.",
      "changes": [
        {
          "change_id": "diff_1",
          "explanation": "Added authorization for recurring subscription charges.",
          "possible_implication": "Customer payment methods will be billed on cycle.",
          "exact_excerpt": "You authorize recurring charges to your payment method.",
          "source_version": "new",
          "uncertainty": null,
          "significance": "medium"
        }
      ]
    }"""

    with patch("app.services.gemma.is_ai_configured", return_value=True), \
         patch("app.services.gemma.get_cloudflare_model", return_value="@cf/google/gemma-4-26b-a4b-it"), \
         patch("app.services.gemma.call_cloudflare_ai", new_callable=AsyncMock) as mock_call:

        mock_call.return_value = mock_change_ai_response

        res = await explain_policy_changes(
            diff_data=mock_diff,
            old_text="Old policy text.",
            new_text="Old policy text. You authorize recurring charges to your payment method.",
        )
        assert res["model_id"] == "@cf/google/gemma-4-26b-a4b-it"
        assert len(res["changes"]) == 1
        assert res["changes"][0]["exact_excerpt"] == "You authorize recurring charges to your payment method."


def test_compute_risk_score_tiers():
    """Verify calibrated consumer risk score calculation and tier boundaries."""
    # 1. Empty findings -> minimal baseline
    score, level = compute_risk_score([])
    assert score == 12
    assert level == "low"

    # 2. Low-risk findings only (score <= 30 -> low)
    score, level = compute_risk_score([
        {"category": "renewal", "severity": "low", "exact_excerpt": "..."},
        {"category": "cancellation", "severity": "low", "exact_excerpt": "..."},
    ])
    assert score <= 30
    assert level == "low"

    # 3. Moderate-risk findings (e.g. mandatory arbitration clause, score 31-55 -> moderate)
    score, level = compute_risk_score([
        {"category": "disputes", "severity": "high", "exact_excerpt": "All claims shall be resolved in arbitration."},
        {"category": "renewal", "severity": "medium", "exact_excerpt": "Subscriptions renew automatically."},
    ])
    assert 31 <= score <= 55
    assert level == "moderate"

    # 4. Elevated-risk findings (score 56-74 -> elevated)
    score, level = compute_risk_score([
        {"category": "disputes", "severity": "high", "exact_excerpt": "..."},
        {"category": "termination", "severity": "high", "exact_excerpt": "..."},
        {"category": "data", "severity": "high", "exact_excerpt": "..."},
        {"category": "liability", "severity": "medium", "exact_excerpt": "..."},
    ])
    assert 56 <= score <= 74
    assert level == "elevated"

    # 5. High-risk findings (score >= 75 -> high)
    score, level = compute_risk_score([
        {"category": "safety", "severity": "high", "exact_excerpt": "physical injury and death disclaimed"},
        {"category": "disputes", "severity": "high", "exact_excerpt": "..."},
        {"category": "liability", "severity": "high", "exact_excerpt": "bodily harm and death", "explanation": "bodily harm"},
        {"category": "termination", "severity": "high", "exact_excerpt": "..."},
        {"category": "data", "severity": "high", "exact_excerpt": "..."},
    ])
    assert score >= 75
    assert level == "high"
