# EasyFinePrint: System Architecture & Design Rationale

EasyFinePrint is an evidence-backed monitor for public Terms of Service and Privacy Policy changes. Its core architectural principle is:

> **KEEP FACTS AND INTERPRETATION SEPARATE.**
> Deterministic algorithms (hashing, difflib, schema validation) establish what text was retrieved and what changed. Probabilistic AI (Gemma 4 via Cloudflare Workers AI REST API) is used exclusively to explain bounded passages in plain English. AI never decides whether a policy changed, never invents excerpts, and never overwrites source evidence.

---

## 1. High-Level Architecture Diagram

```
                 +-----------------------------------------+
                 |   React 19 + Vite + Tailwind CSS SPA    |
                 |      (Vercel Static Edge - Free)        |
                 +--------------------+--------------------+
                                      |
                                      | HTTPS REST API (JSON)
                                      v
                 +--------------------+--------------------+
                 |           FastAPI Backend               |
                 |     (Vercel Serverless Function)        |
                 +--------------------+--------------------+
                                      |
         +----------------------------+----------------------------+
         |                            |                            |
         v                            v                            v
+------------------+         +------------------+         +------------------+
|    SSRF Guard    |         | Deterministic    |         | Evidence         |
|  & Safe Extractor|         | Diff Engine      |         | Validator        |
| - IP resolution  |         | - Paragraph diff |         | - Verbatim quote |
| - Redirect hops  |         | - SHA-256 hash   |         |   verification   |
| - Byte/time caps |         | - difflib ops    |         | - Drops claims   |
+--------+---------+         +--------+---------+         +--------+---------+
         |                            |                            |
         +----------------------------+----------------------------+
                                      |
                 +--------------------+--------------------+
                 |             External Services           |
                 |  - Gemma 4 (Cloudflare Workers AI REST) |
                 |  - MongoDB Atlas Free (M0 Cluster)      |
                 |  - Company Discovery Engine (0-Dep)     |
                 +-----------------------------------------+
```

---

## 2. Component Breakdown

### 2.1 Frontend (`frontend/`)

- **Technology**: React 19, Vite 8, Tailwind CSS v4, Lucide React, React Router.
- **Role**: Client-side application for submitting policy URLs, performing instant company lookups, visualizing risk findings, exploring paragraph-level diffs, and browsing version history. Features custom dark-themed scrollbars, responsive 2x2 grid card view with centered odd cards on mobile, 8-per-page sliding window pagination, responsive 4-column tab navigation without horizontal overflow, instant route scroll-to-top restoration, in-place validation dismissals, and direct self-policy auditing. Pages include Home, PolicyDetail, TermsOfUse (`/terms`), and PolicyDoc (`/privacy`, renamed to avoid browser adblocker and Brave Shields false-positive tracking interception). Both legal documents dynamically parse and render Markdown directly from `docs/TERMS_OF_USE.md` and `docs/PRIVACY_POLICY.md` via `MarkdownDocViewer.jsx`.
- **Hosting**: Vercel Static Edge (Free tier, zero compute costs).

### 2.2 Backend (`backend/app/`)

- **Framework**: FastAPI with asynchronous endpoints (`httpx`, `motor`, `asyncio`).
- **Hosting**: Vercel Serverless Function (Python runtime via `api/index.py`).
- **Security & Safety Modules**:
  - `url_guard.py`: Blocks loopback, RFC 1918 private subnets, carrier-grade NAT, and cloud metadata endpoints (`169.254.169.254`, `fd00:ec2::254`). Re-validates destinations across redirect chains and restricts allowed ports to `{80, 443}`.
  - `extractor.py`: Resilient, safe streaming HTTP fetch with strict byte limits (5 MB max), anti-tarpit timeouts (20s read, 10s connect), and high-fidelity modern browser headers (`User-Agent`, `Sec-Ch-Ua`, etc.) preventing anti-bot connection drops. Features a 4-tier extraction pipeline:
    1. Primary `trafilatura` extraction (optimized for static legal articles).
    2. Secondary `BeautifulSoup` DOM cleaner and container parser.
    3. Client-Side JavaScript Hydration parser (extracts rich legal text from React, Next.js `__NEXT_DATA__`, dynamic SPA stores such as `window.__pageData__`, and Redux SSR state).
    4. Sandboxed Node.js VM dynamic evaluation (`node:vm`) with a 2-second timeout for inline JavaScript computations, plus Node.js HTTP/2 fallback fetch.
  - `normalizer.py`: Unicode NFKC normalization and line ending standardization, preserving legal syntax and numbers while stabilizing hashes.
  - `diff_engine.py`: Deterministic paragraph-level sequence matcher (`difflib`). Categorizes changes into additions, removals, and modifications.
  - `gemma.py`: Cloudflare Workers AI REST adapter for Gemma 4 (`@cf/google/gemma-4-26b-a4b-it`) with strict safety prompts isolating untrusted text inside `<UNTRUSTED_DOCUMENT_CONTENT>` tags. Computes an evidence-based consumer risk score (10 to 100) using diminishing-returns severity weighting and calibrated risk tiers: Low (0-30, Emerald), Moderate (31-55, Yellow), Elevated (56-74, Amber), and High (75-100, Rose) with specialized hazard multipliers for mandatory arbitration, court waivers, and bodily harm disclaimers.
  - `validator.py`: Server-side evidence checker. Ensures every quotation returned by the LLM is present verbatim in the source text.
  - `known_directory.py` & `discovery.py`: Expansive legal policy discovery service featuring an audited directory of **249+ leading platforms** (covering AI, SaaS, Cloud, Fintech, E-Commerce, Quick-Commerce, Rideshare, Streaming, Gaming, Hardware, and Telecom) with **501+ verified policy documents** and comprehensive alias resolution (`fb`, `yt`, `amzn`, `chatgpt`, `spacex`, `xfinity`, etc.). For unlisted companies, an automated multi-tier discovery pipeline probes candidate TLDs (`.com`, `.io`, `.ai`, `.app`, `.org`, `.dev`), inspects homepage DOM legal footers, probes canonical endpoints (`/terms`, `/privacy`, `/legal`), and executes privacy-preserving search engine fallback under strict multi-hop SSRF validation. The frontend modal includes a realistic stage-based progress bar and 5-per-page pagination for companies with extensive policy resources.
  - `policies.py`: Manages policy ingestion, single-pass clause risk scoring, Myers diff generation, self-policy intercept, exact-match baseline upgrade, and `DELETE /api/policies/{id}` cascade deletion.
  - `health.py`: Anti-reconnaissance health check endpoint returning minimal status (`status: healthy`) without leaking internal AI models, provider names, environment modes, or database topologies to external scanners.
  - `security.py`: HTTP security middleware enforcing HSTS, CSP, X-Frame-Options (`DENY`), X-Content-Type-Options (`nosniff`), Referrer-Policy, and request body size caps.
  - `sentry_tunnel` (`/api/tunnel`): Same-origin Sentry envelope proxy that validates DSN target hostnames and routes client telemetry server-to-server, preventing Brave Shields and adblockers from misclassifying error monitoring as advertising trackers. HTTP client logging (`httpx`/`httpcore`) is silenced to `WARNING` to prevent telemetry URL leakage.

### 2.3 Persistence Layer (`backend/app/db/`)

- **Database**: MongoDB Atlas Free (M0 sandbox cluster, 512 MB) or local MongoDB.
- **Collections**:
  - `policies`: Tracked URLs, titles, and latest snapshot references.
  - `snapshots`: Immutable version snapshots with content hashes and extracted text.
  - `analyses`: Stored risk and change evaluations with model IDs and validation outcomes.
  - `check_events`: Chronological log of manual rechecks and extraction statuses.
  - `usage_counters`: Ephemeral operational metrics.
- **Security Hardening**:
  - Strict NoSQL injection defenses: All ID queries use strict alphanumeric validation and MongoDB `$eq` operator binding to prevent operator injection attacks.
- **Fallback**: Built-in async in-memory repository for local development and test isolation without database dependencies.

---

## 3. Data Flow

### Journey A: Initial Policy Analysis

1. User submits a public policy URL (or selects a candidate from the Company Lookup modal).
2. `url_guard` validates scheme (http/https only), authority (no credentials), and resolves DNS to ensure all target IPs are public.
3. `extractor` streams the HTML body, capping bytes at 5 MB.
4. `normalizer` cleans whitespace and calculates SHA-256 hash.
5. If new, baseline snapshot is persisted in MongoDB.
6. `gemma` evaluates high-risk clauses (disputes/arbitration, liability, human harm, renewal, privacy) using isolated JSON prompting with Gemma 4 on Cloudflare Workers AI.
7. `validator` validates all quoted excerpts against the snapshot. Unsupported findings are dropped.
8. Frontend renders executive summary, finding cards, and source quotes.

### Journey B: Recheck Tracked Policy

1. User clicks "Check for Updates".
2. `extractor` fetches the current live webpage.
   - _If fetch fails_: Status is set to `extraction_failed`; the previous baseline snapshot remains completely intact and immutable.
3. `normalizer` calculates current SHA-256 hash.
   - _If hash matches_: Status is set to `unchanged`. The model call is skipped entirely (preserving zero-cost quota and preventing false score drift).
   - _If hash differs_: `diff_engine` calculates exact paragraph additions, removals, and modifications.
4. `gemma` explains the bounded differences.
5. `validator` verifies quotes against the respective old/new snapshots.
6. Frontend displays side-by-side / unified diffs and AI implications.
