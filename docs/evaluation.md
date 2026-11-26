# EasyFinePrint: Evaluation & Test Results

EasyFinePrint is evaluated against an automated suite covering extraction, deterministic diffing, citation verification, Cloudflare Workers AI integration, zero-dependency company discovery, and full OWASP Top 10 (2025) & OWASP API Security Top 10 (2023) controls.

---

## 1. Backend Test Summary

- **Total Test Cases**: 108
- **Passed**: 107 (100% of runnable offline tests)
- **Skipped**: 1 (`test_live_gemma_single_pass_analysis`, skipped when live Cloudflare API credentials are omitted)
- **Dependency Integrity (`pip check`)**: 0 broken requirements
- **Platform**: Python 3.14 on Linux (`x86_64`)

Core test suites:
- `test_owasp_security.py`: 23 tests covering `A01`–`A10:2025` and `API1`–`API10:2023` (admin key constant-time auth & fail-closed production `DELETE`, CSRF Origin/Fetch-Metadata guards, scoped CORS, production OpenAPI disablement, Tier 3 XSS/SSRF URL validation, mass assignment `extra="forbid"`, null-byte rejection, `node:vm` sandbox escape & env-stripping, prompt boundary sanitization, tunnel path-traversal & size limits, 429 sliding-window rate limiter, chunked body streaming caps, bounded discovery cache, IPv6 tunneling SSRF, redirect-disabled discovery/Wayback, `SECURITY_EVENT` audit logging, Vercel proxy IP detection, and simulated Vercel production E2E).
- `test_cloudflare_gemma.py` (8), `test_cors.py` (5), `test_discovery.py` (12), `test_extractor.py` (8), `test_health.py` (2), `test_hybrid_pipeline.py` (9), `test_normalizer_diff.py` (6), `test_policies_flow.py` (7), `test_self_policy.py` (5), `test_tunnel.py` (6), `test_url_guard.py` (10), `test_validator.py` (6), `test_gemma_live.py` (1 skipped offline).

---

## 2. Key Security & Functional Evaluation Criteria

| Evaluation Criterion | Observed Result | Rationale |
| :--- | :--- | :--- |
| **OWASP Top 10 (2025) & API Top 10 (2023)** | 23/23 dedicated security tests passing | Covers access control, CSRF, CORS, CSP, rate limiting, chunked body limits, mass assignment, SSRF, Node VM isolation, and audit logging |
| **Database Query Optimization** | 0 N+1 queries, 1 aggregation roundtrip | Pre-joins latest analyses and snapshot provenance in a single MongoDB `$lookup` pipeline, projecting only `provenance: 1` |
| **4-Tier Ingestion & Provenance** | 100% pass across all 4 tiers | Live fetch, Wayback archive fallback, user paste with length bounds & canonical URL deduplication, and database baseline cache |
| **SSRF Protection (`API7:2023`)** | 100% of tested internal / tunneled targets blocked | Enforces IPv4/IPv6/6to4/Teredo checks, literal-IP validation, `archive.org` pinning, and zero `follow_redirects=True` across the backend |
| **Injection & Sandbox Defense (`A05:2025`)** | XSS, NoSQL, prompt, and VM escapes blocked | Tier 3 URL validation, frontend `safeUrl.js`, `--disallow-code-generation-from-strings`, stripped child `env`, and `$eq` ID sanitization |
| **Deterministic Diff & Citation Validity** | 100% verbatim quote enforcement | `difflib.SequenceMatcher` computes exact diffs; unverified AI citations are dropped server-side |
| **Anti-Reconnaissance & Audit Privacy** | Minimal telemetry & hashed IP audit refs | Production hides `/docs`/`/openapi.json`; `SECURITY_EVENT` logs redact secrets and hash client IPs |

---

## 3. Frontend Linting, Unit Tests & Production Build

- **Linter (`oxlint`)**: 0 warnings, 0 errors across 30 files.
- **Unit Tests (`node --test`)**: **11 passed, 0 failed**:
  - `policiesCache.test.js` (5): session cache, SWR staleness, invalidation, and 30s refresh cooldown.
  - `safeUrl.test.js` (4): `getSafeHref`, `isSafeHttpUrl`, `isSafeIdentifier` blocking `javascript:`, `data:`, `vbscript:`, `file:`, protocol-relative `//`, credentials, and path traversal IDs.
  - `scrollLock.test.js` (2): desktop/mobile body scroll locking and route-change offset reset.
- **Production Bundle (`vite build`)**: Verified clean production bundling (`dist/`).

---

## 4. Known Limitations

1. **Interactive Bot Challenges**: Pages gated behind interactive human CAPTCHAs or login walls fall back to Tier 2 (Internet Archive Wayback Machine) or Tier 3 (Paste Text) with explicit provenance tags.
2. **Serverless Rate-Limit Scope**: On stateless serverless platforms (such as Vercel), in-memory sliding-window rate limits operate per warm function instance rather than globally across edge regions.
3. **Informational Scope**: Clause summaries and risk tiers are informational and do not constitute formal legal advice.
