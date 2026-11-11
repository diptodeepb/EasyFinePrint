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

- **Technology**: React 19, Vite 8, Tailwind CSS v4, Lucide React, React Router, CSS View Transitions API.
- **Role**: Client-side application for submitting policy URLs, performing instant company lookups, visualizing risk findings, exploring paragraph-level diffs, and browsing version history. Features custom dark/light-themed scrollbars, responsive 2x2 grid card view with centered odd cards on mobile, 8-per-page sliding window pagination, responsive 4-column tab navigation without horizontal overflow, instant route scroll-to-top restoration, in-place validation dismissals, and direct self-policy auditing. Pages include Home, PolicyDetail, TermsOfUse (`/terms`), and PolicyDoc (`/privacy`, renamed to avoid browser adblocker and Brave Shields false-positive tracking interception). Both legal documents dynamically parse and render Markdown directly from `docs/TERMS_OF_USE.md` and `docs/PRIVACY_POLICY.md` via `MarkdownDocViewer.jsx`.
- **Adaptive Theming Engine**:
  - Tri-state theme switcher ("Light", "Dark", "System") with active checkmarks and `localStorage` persistence.
  - Initial visit auto-selects the user's OS preference (`prefers-color-scheme`) and dynamically syncs with system mode shifts. A pre-mount inline script in `index.html` evaluates theme before DOM render to eliminate Flash of Unstyled Content (FOUC).
  - Eye-comfort warm beige light palette (`#ece5d8` background, `#f5eedf` panels, `#faf5ec` elevated inputs, `#d5cbba` borders, `#1c1917` text) eliminating harsh white glare.
  - Radial outward curve animation using the CSS View Transitions API (`::view-transition-new(root)`), anchored to the trigger coordinates. Utilizes `flushSync` DOM batching and device-calibrated bezier curves (`cubic-bezier(0.4, 0, 0.2, 1)` on mobile; `cubic-bezier(0.5, 0, 1, 1)` on desktop) with shader optimization (`.is-theme-transitioning` suppressing expensive blurs) to maintain 60fps across mobile GPUs.
- **Mobile & Modal Interaction Safety**:
  - **Auto-Closing Mobile Navigation**: Mobile theme selection or toggle interactions automatically close the mobile navigation drawer.
  - **Ghost-Click Elimination**: The mobile drawer's blurred backdrop consumes `onTouchEnd` and `onClick` with `e.preventDefault()` and `e.stopPropagation()`. Per W3C Touch Events specifications, preventing default on `touchend` suppresses synthetic mouse/click events, ensuring taps outside the drawer never trigger underlying input fields or buttons. Background scrolling is locked (`document.body.style.overflow = "hidden"`) while the drawer is open.
  - **Company Discovery Modal Ergonomics**: Full-screen backdrop dismissal across PC and mobile with drag-out protection (`isBackdropMouseDown` / `isBackdropTouchStart`) preventing inadvertent dismissal during text selection. Modal content clicks are isolated via `e.stopPropagation()`. Includes native `Escape` key handling and body scroll locking.
  - **Inline Input Clearing**: Text and URL inputs feature embedded rectangular "clear" buttons with live character boundary monitoring ($\le 2,048$ chars for URLs, $\le 200$ chars for titles, $\le 500,000$ chars for raw text).
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
  - `policies.py`: Manages the 4-Tier Hybrid Policy Ingestion & Diff Engine, single-pass clause risk scoring, Myers diff generation, self-policy intercept, exact-match baseline upgrade, and `DELETE /api/policies/{id}` cascade deletion.
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

### Journey A: Policy Ingestion & Analysis

1. User submits a policy URL via direct link or pastes raw agreement text in **"Paste Text"** mode.
2. **SSRF Guard First**: `url_guard` validates scheme (`http`/`https` only), authority (no inline credentials), port (`80`/`443`), and resolves target hostnames. Private, loopback, or cloud metadata IPs are rejected immediately with HTTP 400 Bad Request, aborting before any external network connection or archive lookup.
3. **Ingestion Tier Resolution**:
   - **Tier 3 (User-Provided Direct Ingestion)**: If `raw_text` is supplied, validates minimum length ($\ge 100$ characters). Ingests with `extractor="user_pasted"`, `provenance="user_pasted"`, and attaches an explicit audit warning.
   - **Tier 1 (High-Fidelity Live Fetch)**: Streams HTML with anti-tarpit timeouts and desktop Chrome headers. Parses Trafilatura text, container DOM, and SPA hydration state. Ingests with `provenance="live"`.
   - **Tier 2 (Wayback Machine Auto-Fallback)**: If live fetch fails or is blocked by an origin WAF (<100 characters extracted), queries the Internet Archive Wayback Machine Availability API (`https://archive.org/wayback/available?url=...`). Cleans archive chrome headers and ingests with `provenance="archive"` plus timestamp warnings.
   - **Tier 4 (Zero-Drift Baseline Database Cache)**: If both live fetch and archive lookup are unavailable, retrieves existing database baseline snapshot with `reanalysis_status="cached_fallback"`.
4. `normalizer` cleans whitespace and calculates SHA-256 hash.
5. If text matches the existing baseline identically, redundant model inference is skipped, serving cached risk scores in <100ms.
6. If novel, baseline snapshot is persisted in MongoDB with immutable `provenance` and `warnings`.
7. `gemma` evaluates high-risk clauses (disputes/arbitration, liability, human harm, renewal, privacy) using isolated JSON prompting with Gemma 4 on Cloudflare Workers AI.
8. `validator` validates all quoted excerpts against the snapshot. Unsupported findings are dropped.
9. Frontend renders executive summary, finding cards, provenance warning banners, and verified source quotes.

### Journey B: Recheck Tracked Policy

1. User clicks "Check for Updates" on a tracked policy.
2. `extractor` attempts a live fetch of the target policy URL.
   - _If live fetch blocks (e.g., origin CDN/WAF challenge)_: The engine automatically queries Tier 2 (Wayback Machine Availability API) for the latest public snapshot. If a newer archive record is available, it is ingested for diff analysis.
   - _If both live fetch and archive fail_: Check event is recorded as `extraction_failed`; the previous baseline snapshot remains completely intact and immutable.
3. `normalizer` calculates the retrieved content's SHA-256 hash.
   - _If hash matches_: Status is set to `unchanged`. Model execution is skipped entirely (preserving zero-cost quota and preventing score drift).
   - _If hash differs_: `diff_engine` calculates exact paragraph additions, removals, and modifications using Myers diff algorithms.
4. `gemma` explains the legal implications of the bounded changes.
5. `validator` verifies quotes against the respective old/new snapshots.
6. Frontend displays side-by-side / unified diffs and AI delta explanations with appropriate provenance badges.

---

## 4. 4-Tier Hybrid Policy Ingestion & Provenance Architecture

```
                                 [ Incoming Request ]
                                          │
                                 ┌────────┴────────┐
                                 │   SSRF Guard    │──(Private/Metadata IP)──> [ HTTP 400 Bad Request ]
                                 └────────┬────────┘
                                          │ (Public Safe IP)
                                          ▼
                                 ┌─────────────────┐
                       ┌─────────┤ Raw Text Paste? ├─────────┐
                       │ (Yes)   └─────────────────┘   (No)  │
                       ▼                                     ▼
             ┌───────────────────┐                 ┌───────────────────┐
             │      Tier 3       │                 │      Tier 1       │
             │   User-Provided   │                 │    Live Fetch     │
             │   Text Ingestion  │                 │   & SPA Extract   │
             │ (Length bounds &  │                 └─────────┬─────────┘
             │  Deduplication)   │                           │
             └─────────┬─────────┘                (Firewall Block or <100 chars)
                       │                                     ▼
                       │                           ┌───────────────────┐
                       │                           │      Tier 2       │
                       │                           │  Wayback Machine  │
                       │                           │  Archive Fallback │
                       │                           └─────────┬─────────┘
                       │                                     │
                       │                           (Archive Unavailable)
                       │                                     ▼
                       │                           ┌───────────────────┐
                       │                           │      Tier 4       │
                       │                           │ Baseline Database │
                       │                           │   Cached Lookup   │
                       │                           └─────────┬─────────┘
                       │                                     │
                       └──────────────────┬──────────────────┘
                                          ▼
                             ┌─────────────────────────┐
                             │    Provenance Stamped   │
                             │ (live / archive / user) │
                             └────────────┬────────────┘
                                          ▼
                             ┌─────────────────────────┐
                             │ Normalizer & Hash Match │
                             └─────────────────────────┘
```

### 4.1 Anti-Spam Bounds & Canonical Deduplication

1. **Character Length Bounds (Universal Web Standards)**:
   - **Policy URL**: Maximum 2,048 characters (aligned with RFC 7230 and cross-browser URL limits).
   - **Document Title**: Maximum 200 characters (accommodating descriptive legal titles while preventing payload inflation). Auto-derived from the URL domain and path if omitted.
   - **Text Body**: Minimum 100 characters (ensuring substantive legal prose for evaluation) and maximum 500,000 characters (~100,000 words, protecting server memory).
2. **Canonical URL Deduplication Guard**:
   - To prevent evasion or duplication of system-maintained agreements, user paste submissions are verified against the system repository using canonicalized URLs.
   - Normalization resolves trailing slashes, root slashes, protocol schemes (`http`/`https`), default ports (`:80`/`:443`), `www.` prefixes, query parameters (`?utm=...`), hash fragments (`#tos`), and case differences. Duplicate submissions return HTTP 400 Bad Request.
3. **Dashboard Segmentation**:
   - Monitored agreements are cleanly partitioned into "System Maintained" and "User Maintained" segmented tabs with independent counters and responsive desktop/mobile layouts.

### 4.2 Provenance Tracking Guarantees

| Provenance Key | Trigger Condition | UI Representation | Audit Guarantee |
| :--- | :--- | :--- | :--- |
| `live` | Direct successful live HTTP fetch & DOM/SPA extraction | Standard verified status | Fully autonomous, independently verified live crawl. |
| `archive` | Live site blocked by origin firewall; fetched via Wayback Machine | Blue `Public Web Archive Record` notice & timestamp banner | Verified public historical record from the Internet Archive; independent of datacenter IP blocks. |
| `user_pasted` | Direct user text submission via "Paste Text" mode | Segmented `User Maintained` tab & amber disclaimer notice banner | Explicitly flags that findings reflect user-submitted text and may not represent the complete official agreement. |
| `cached_fallback`| Both live site and archive unavailable; database fallback | Gray fallback note | Historical baseline snapshot preserved without destructive overwrites. |
