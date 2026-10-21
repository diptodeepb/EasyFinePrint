# EasyFinePrint: Evaluation & Test Results

EasyFinePrint is evaluated against an automated suite of unit and integration tests covering extraction, deterministic diffing, citation verification, SSRF blocking, and edge cases.

---

## 1. Test Summary

- **Total Test Cases**: 27
- **Passed**: 27 (100%)
- **Execution Time**: ~2.6 seconds
- **Platform**: Python 3.14 on Linux (x86_64)

```
backend/tests/test_health.py::test_health_check_endpoint PASSED
backend/tests/test_health.py::test_root_endpoint PASSED
backend/tests/test_normalizer_diff.py::test_normalization_whitespace_and_newlines PASSED
backend/tests/test_normalizer_diff.py::test_identical_hash_for_formatting_changes PASSED
backend/tests/test_normalizer_diff.py::test_diff_identical_text_unchanged PASSED
backend/tests/test_normalizer_diff.py::test_diff_clause_added PASSED
backend/tests/test_normalizer_diff.py::test_diff_clause_removed PASSED
backend/tests/test_normalizer_diff.py::test_diff_clause_modified PASSED
backend/tests/test_policies_flow.py::test_policy_full_lifecycle PASSED
backend/tests/test_serpapi.py::test_serpapi_disabled_by_default PASSED
backend/tests/test_serpapi.py::test_serpapi_hourly_and_monthly_cap PASSED
backend/tests/test_serpapi.py::test_discovery_endpoint_graceful_handling PASSED
backend/tests/test_url_guard.py::test_allowed_public_urls PASSED
backend/tests/test_url_guard.py::test_reject_credentials_in_url PASSED
backend/tests/test_url_guard.py::test_reject_invalid_schemes PASSED
backend/tests/test_url_guard.py::test_reject_blocked_hostnames PASSED
backend/tests/test_url_guard.py::test_reject_unsupported_ports PASSED
backend/tests/test_url_guard.py::test_ip_guard_loopback PASSED
backend/tests/test_url_guard.py::test_ip_guard_private_rfc1918 PASSED
backend/tests/test_url_guard.py::test_ip_guard_cloud_metadata PASSED
backend/tests/test_url_guard.py::test_ip_guard_public_ips PASSED
backend/tests/test_validator.py::test_verify_quote_exact_match PASSED
backend/tests/test_validator.py::test_verify_quote_case_insensitive_and_whitespace PASSED
backend/tests/test_validator.py::test_verify_quote_fabricated_fails PASSED
backend/tests/test_validator.py::test_validate_initial_findings_passed PASSED
backend/tests/test_validator.py::test_validate_initial_findings_partial_and_drops_unsupported PASSED
backend/tests/test_validator.py::test_validate_initial_findings_all_fabricated_fails PASSED
```

---

## 2. Key Metric Findings

| Evaluation Criterion | Observed Result | Rationale |
|----------------------|-----------------|-----------|
| **SSRF Protection** | 100% of tested internal / metadata targets blocked | Checked across IPv4, IPv6, cloud metadata, and URL authorities |
| **Deterministic Diff Accuracy** | 100% precision on additions, removals, and edits | Python `difflib.SequenceMatcher` operating on normalized paragraphs |
| **Citation Validity Enforcement** | 100% of fabricated quotes dropped | Server-side validation drops unverified AI claims before user display |
| **Zero-Spend Adherence** | 100% $0 operation | Uses free static hosting, free Render web tier, free Atlas M0, and free Gemma quota |
| **Extraction Failure Safety** | Previous snapshot preserved intact | Extraction errors never report false "unchanged" status |

---

## 3. Known Limitations

1. **JavaScript-heavy Single Page Apps**: Websites that render legal terms entirely client-side via JavaScript without static HTML fallback may produce short or incomplete text via standard HTTP fetch. The system issues an extraction warning and rejects documents under 100 characters.
2. **Third-Party Rate Limits**: While EasyFinePrint enforces application-level caps, target legal websites may deploy Cloudflare or Akamai bot management that temporarily blocks scraping requests.
3. **Informational Scope**: AI explanations and findings are designed for consumer awareness and transparency, not legal counsel or statutory compliance certification.
