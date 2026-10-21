# EasyFinePrint: System Architecture & Design Rationale

EasyFinePrint is an evidence-backed monitor for public Terms of Service and Privacy Policy changes. Its core architectural principle is:

> **KEEP FACTS AND INTERPRETATION SEPARATE.**
> Deterministic algorithms (hashing, difflib, schema validation) establish what text was retrieved and what changed. Probabilistic AI (Gemma via Gemini API) is used exclusively to explain bounded passages in plain English. AI never decides whether a policy changed, never invents excerpts, and never overwrites source evidence.

---

## 1. High-Level Architecture Diagram

```
                 +-----------------------------------------+
                 |   React 19 + Vite + Tailwind CSS SPA    |
                 |       (Render Static Site - Free)       |
                 +--------------------+--------------------+
                                      |
                                      | HTTPS REST API (JSON)
                                      v
                 +--------------------+--------------------+
                 |           FastAPI Backend               |
                 |      (Render Web Service - Free)        |
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
                 |  - Gemma (Google GenAI Free Quota)      |
                 |  - MongoDB Atlas Free (M0 Cluster)      |
                 |  - Optional SerpApi (Discovery Capped)  |
                 +-----------------------------------------+
```

---

## 2. Component Breakdown

### 2.1 Frontend (`frontend/`)
- **Technology**: React 19, Vite, Tailwind CSS v4, Lucide React, React Router.
- **Role**: Client-side application for submitting policy URLs, visualizing risk findings, exploring paragraph-level diffs, and browsing version history.
- **Hosting**: Render Static Site (Free tier, zero compute costs).

### 2.2 Backend (`backend/app/`)
- **Framework**: FastAPI with asynchronous endpoints (`httpx`, `motor`, `asyncio`).
- **Hosting**: Render Free Web Service (with automated idle spindown and ephemeral container safety).
- **Security & Safety**:
  - `url_guard.py`: Blocks loopback, RFC 1918 private subnets, carrier-grade NAT, and cloud metadata endpoints (`169.254.169.254`, `fd00:ec2::254`). Re-validates destinations across redirect chains.
  - `extractor.py`: Safe streaming HTTP fetch with strict byte limits (2 MB) and timeouts (15s). Content extraction via `trafilatura` with a cleaned `BeautifulSoup` fallback.
  - `normalizer.py`: Unicode NFKC normalization and line ending standardization, preserving legal syntax and numbers while stabilizing hashes.
  - `diff_engine.py`: Deterministic paragraph-level sequence matcher (`difflib`). Categorizes changes into additions, removals, and modifications.
  - `gemma.py`: Google GenAI adapter for Gemma models with strict safety prompts treating policy text as untrusted data.
  - `validator.py`: Server-side evidence checker. Ensures every quotation returned by the LLM is present verbatim in the source text.
  - `serpapi.py`: Quota-guarded discovery adapter with in-memory caching and strict monthly (200) and hourly (40) application caps.

### 2.3 Persistence Layer (`backend/app/db/`)
- **Database**: MongoDB Atlas Free (M0 sandbox cluster, 512 MB).
- **Collections**:
  - `policies`: Tracked URLs, titles, and latest snapshot references.
  - `snapshots`: Immutable version snapshots with content hashes and extracted text.
  - `analyses`: Stored risk and change evaluations with model IDs and validation outcomes.
  - `check_events`: Chronological log of manual rechecks and extraction statuses.
- **Fallback**: Built-in async in-memory repository for local development and test isolation without database dependencies.

---

## 3. Data Flow

### Journey A: Initial Policy Analysis
1. User submits a public policy URL.
2. `url_guard` validates scheme (http/https only), authority (no credentials), and resolves DNS to ensure all target IPs are public.
3. `extractor` streams the HTML body, capping bytes at 2 MB.
4. `normalizer` cleans whitespace and calculates SHA-256 hash.
5. If new, baseline snapshot is persisted in MongoDB.
6. `gemma` evaluates high-risk clauses (renewal, disputes, privacy, liability) using strict JSON prompting.
7. `validator` validates all quoted excerpts against the snapshot. Unsupported findings are dropped.
8. Frontend renders executive summary, finding cards, and source quotes.

### Journey B: Recheck Tracked Policy
1. User clicks "Check for Updates".
2. `extractor` fetches the current live webpage.
   - *If fetch fails*: Status is set to `extraction_failed`; the previous baseline snapshot remains completely intact and immutable.
3. `normalizer` calculates current SHA-256 hash.
   - *If hash matches*: Status is set to `unchanged`. The model call is skipped entirely (preserving zero-cost quota).
   - *If hash differs*: `diff_engine` calculates exact paragraph additions, removals, and modifications.
4. `gemma` explains the bounded differences.
5. `validator` verifies quotes against the respective old/new snapshots.
6. Frontend displays side-by-side / unified diffs and AI implications.
