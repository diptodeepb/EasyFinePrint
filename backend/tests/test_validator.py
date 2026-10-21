"""Tests for quote verification and AI evidence validation."""
from app.services.validator import (
    verify_quote_in_text,
    validate_initial_findings,
    validate_change_explanations,
)

SOURCE_POLICY = """
Terms of Service
Effective Date: October 2026

1. Auto-Renewal and Subscription Fees
Your subscription will automatically renew at the conclusion of each billing cycle unless you provide written notice of cancellation at least 30 days prior to the renewal date.

2. Limitation of Liability
Under no circumstances shall the company be liable for any indirect, incidental, or consequential damages arising out of the use of this service.

3. Dispute Resolution and Arbitration
You agree that all disputes must be resolved through binding individual arbitration rather than court proceedings. You explicitly waive any right to participate in a class-action lawsuit.
"""


def test_verify_quote_exact_match():
    quote = "subscription will automatically renew at the conclusion of each billing cycle"
    assert verify_quote_in_text(quote, SOURCE_POLICY) is True


def test_verify_quote_case_insensitive_and_whitespace():
    quote = "Subscription   will AUTOMATICALLY renew\nat the conclusion"
    assert verify_quote_in_text(quote, SOURCE_POLICY) is True


def test_verify_quote_fabricated_fails():
    quote = "The company guarantees a 100% full cash refund within 90 days."
    assert verify_quote_in_text(quote, SOURCE_POLICY) is False


def test_validate_initial_findings_passed():
    findings = [
        {
            "category": "renewal",
            "severity": "high",
            "exact_excerpt": "subscription will automatically renew at the conclusion of each billing cycle unless you provide written notice",
            "explanation": "Subscriptions automatically renew without prompt.",
            "why_it_might_matter": "Users may be charged unexpectedly.",
        },
        {
            "category": "disputes",
            "severity": "medium",
            "exact_excerpt": "binding individual arbitration rather than court proceedings. You explicitly waive any right",
            "explanation": "Mandatory arbitration and class action waiver.",
            "why_it_might_matter": "Limits legal remedies.",
        },
    ]

    validated, status = validate_initial_findings(findings, SOURCE_POLICY)
    assert status == "passed"
    assert len(validated) == 2


def test_validate_initial_findings_partial_and_drops_unsupported():
    findings = [
        {
            "category": "liability",
            "severity": "medium",
            "exact_excerpt": "Under no circumstances shall the company be liable for any indirect, incidental",
            "explanation": "Disclaims consequential liability.",
            "why_it_might_matter": "Limits damages recoverability.",
        },
        {
            "category": "price_change",
            "severity": "high",
            "exact_excerpt": "Prices can be doubled at midnight without notifying you at all.",  # Hallucinated!
            "explanation": "Unilateral price increases.",
            "why_it_might_matter": "Surprise billing.",
        },
    ]

    validated, status = validate_initial_findings(findings, SOURCE_POLICY)
    assert status == "partial"
    assert len(validated) == 1
    assert "Under no circumstances" in validated[0]["exact_excerpt"]


def test_validate_initial_findings_all_fabricated_fails():
    findings = [
        {
            "category": "data",
            "severity": "high",
            "exact_excerpt": "We sell all your biometric iris scans to advertising brokers worldwide.",
            "explanation": "Invasive data selling.",
            "why_it_might_matter": "Severe privacy violation.",
        }
    ]

    validated, status = validate_initial_findings(findings, SOURCE_POLICY)
    assert status == "failed"
    assert len(validated) == 0
