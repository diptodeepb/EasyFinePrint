"""Tests for enhanced policy extractor and JavaScript hydration engine."""
import pytest
from app.services.extractor import (
    extract_policy_content,
    extract_js_hydration_policy,
    evaluate_inline_scripts_with_node,
    ExtractionError,
)


def test_standard_html_extraction():
    """Verify primary extraction on standard static HTML."""
    html = """
    <!DOCTYPE html>
    <html>
    <head><title>Acme Terms of Service</title></head>
    <body>
    <main>
        <h1>Acme Terms of Service Agreement</h1>
        <p>Effective Date: November 2026</p>
        <p>By using the Acme platform, you expressly agree to be bound by these legal terms and conditions.</p>
        <p>All accounts must be registered with accurate information and kept confidential at all times.</p>
        <p>You agree to submit all legal disputes to binding individual arbitration rather than jury trials.</p>
    </main>
    </body>
    </html>
    """
    title, text, warnings = extract_policy_content(html)
    assert "Acme Terms of Service" in title
    assert "binding individual arbitration" in text
    assert len(text) > 100


def test_js_hydration_extraction_spa_pattern():
    """Verify JavaScript hydration extraction for SPA frameworks (evaluating serialized window state stores)."""
    html = """
    <!DOCTYPE html>
    <html>
    <head><title>Terms of use</title></head>
    <body>
        <div id="mountroot"></div>
        <script>
        window["__static_page_data__"] = {
            "details": [
                {
                    "description": "Welcome to our marketplace platform. This document is an electronic record published under Information Technology Rules."
                },
                {
                    "description": "1. User Account, Password, and Security: Users must maintain the confidentiality of their login credentials and are responsible for all account activities."
                },
                {
                    "description": "2. Platform Services: The Platform enables registered users to purchase merchandise and track deliveries subject to standard return policies."
                }
            ]
        };
        </script>
    </body>
    </html>
    """
    title, text, warnings = extract_policy_content(html)
    assert "Terms of use" in title
    assert "electronic record published" in text
    assert "User Account, Password, and Security" in text
    assert any("JavaScript" in w for w in warnings)


def test_nextjs_data_hydration():
    """Verify Next.js __NEXT_DATA__ JSON script extraction."""
    html = """
    <!DOCTYPE html>
    <html>
    <head><title>NextJS Privacy Policy</title></head>
    <body>
        <div id="__next"></div>
        <script id="__NEXT_DATA__" type="application/json">
        {
            "props": {
                "pageProps": {
                    "content": "This Privacy Policy describes how we collect, process, and safeguard your personal data across our cloud services.",
                    "details": [
                        "We do not sell personal information to third parties under any circumstances.",
                        "Data is retained only as long as necessary to provide active subscriptions and meet regulatory obligations."
                    ]
                }
            }
        }
        </script>
    </body>
    </html>
    """
    title, text, warnings = extract_policy_content(html)
    assert "NextJS Privacy Policy" in title
    assert "how we collect, process, and safeguard" in text
    assert "sell personal information" in text


def test_node_vm_sandboxed_evaluation():
    """Verify sandboxed Node.js VM evaluation extracts dynamically computed variables."""
    script_html = """
    <script>
    window.dynamicTerms = {
        title: "Dynamic Evaluation Policy",
        body: [
            "Users must comply with all acceptable use policies and community conduct guidelines.",
            "Any unauthorized automated scraping, reverse engineering, or denial of service attacks will result in immediate termination."
        ]
    };
    </script>
    """
    res = evaluate_inline_scripts_with_node(script_html)
    assert "acceptable use policies" in res
    assert "unauthorized automated scraping" in res


def test_empty_html_raises_extraction_error():
    """Verify that completely blank or unparseable HTML raises ExtractionError."""
    html = "<html><body><div id='root'></div></body></html>"
    with pytest.raises(ExtractionError) as exc_info:
        extract_policy_content(html)
    assert "empty or suspiciously short" in str(exc_info.value)

