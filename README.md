<div align="center">
  <img src="frontend/public/logo.svg" alt="EasyFinePrint Logo" width="128" height="128" />
  <h1>EasyFinePrint</h1>
  <p>
    <strong>Public Legal Agreements Auditor</strong> &mdash; Deterministic Legal Policy Change Monitoring &amp; Single-Pass Clause Risk Intelligence.<br />
    Audit public legal agreements for mandatory arbitration, broad data sharing, and unilateral terms. Grounded in verbatim citations with automated revision tracking.
  </p>
  <p>
    <a href="https://github.com/diptodeepb/EasyFinePrint/actions/workflows/ci.yml"><img src="https://github.com/diptodeepb/EasyFinePrint/actions/workflows/ci.yml/badge.svg" alt="CI" /></a>
    <a href="LICENSE"><img src="https://img.shields.io/badge/License-Apache_2.0-blue.svg" alt="License: Apache 2.0" /></a>
    <a href="https://www.python.org/downloads/"><img src="https://img.shields.io/badge/python-3.12+-blue.svg" alt="Python 3.12+" /></a>
    <a href="https://fastapi.tiangolo.com"><img src="https://img.shields.io/badge/FastAPI-0.115+-009688.svg" alt="FastAPI" /></a>
    <a href="https://react.dev"><img src="https://img.shields.io/badge/React-19-61dafb.svg" alt="React 19" /></a>
    <a href="https://vitejs.dev"><img src="https://img.shields.io/badge/Vite-8-646cff.svg" alt="Vite 8" /></a>
    <a href="https://tailwindcss.com"><img src="https://img.shields.io/badge/Tailwind-4-38bdf8.svg" alt="Tailwind CSS 4" /></a>
    <a href="https://www.mongodb.com/atlas"><img src="https://img.shields.io/badge/MongoDB-Atlas-green.svg" alt="MongoDB Atlas" /></a>
    <a href="https://developers.cloudflare.com/workers-ai/"><img src="https://img.shields.io/badge/AI-Cloudflare_Gemma_4-F38020.svg" alt="Cloudflare Workers AI Gemma 4" /></a>
  </p>
</div>

---

## 🧭 Table of Contents

- [The Core Problem](#the-core-problem)
- [Architectural Guarantee: Facts vs. Interpretation](#architectural-guarantee-facts-vs-interpretation)
- [Core Capabilities](#core-capabilities)
  - [Single-Pass Gemma 4 Risk Scoring](#single-pass-gemma-4-risk-scoring)
  - [High-Impact Clause Prioritization (Disputes, Arbitration &amp; Safety)](#high-impact-clause-prioritization-disputes-arbitration--safety)
  - [Character-for-Character Verification &amp; Cache](#character-for-character-verification--cache)
  - [Server-Side Verbatim Quotation Validation](#server-side-verbatim-quotation-validation)
  - [Deterministic Paragraph Diffing Engine](#deterministic-paragraph-diffing-engine)
  - [Fail-Safe Baseline Snapshot Protection](#fail-safe-baseline-snapshot-protection)
  - [Strict Multi-Layer SSRF Guard](#strict-multi-layer-ssrf-guard)
  - [Zero-Cost Company Policy Discovery Engine](#zero-cost-company-policy-discovery-engine)
  - [NoSQL &amp; Network Hardening (Security Headers &amp; Prompt Isolation)](#nosql--network-hardening-security-headers--prompt-isolation)
- [Technology Stack](#technology-stack)
- [API Reference](#api-reference)
- [Local Development &amp; Setup](#local-development--setup)
  - [Prerequisites](#prerequisites)
  - [Environment Configuration](#environment-configuration)
  - [One-Command Unified Runner](#one-command-unified-runner)
  - [Manual Execution](#manual-execution)
- [Automated Testing &amp; CI](#automated-testing--ci)
- [Zero-Cost Vercel Serverless Deployment](#zero-cost-vercel-serverless-deployment)
- [Security &amp; Threat Model](#security--threat-model)
- [License](#license)

---

## ⚖️ The Core Problem

Consumers routinely accept terms of service and privacy agreements without reading them. Over time, companies update these contracts—introducing mandatory binding arbitration, broad behavioral data-sharing clauses, unilateral termination rights, and unexpected auto-renewal provisions.

Traditional monitoring approaches suffer from two fatal flaws:

1. **Unreliable LLM Summarization**: Generic AI summaries frequently hallucinate claims that do not exist in the source document or paraphrase text so loosely that users cannot verify the legal basis.
2. **Fragile Change Tracking**: Re-analyzing unchanged documents leads to score fluctuations, redundant API calls, and false "policy updated" notifications.

**EasyFinePrint** solves this by enforcing an uncompromising separation between deterministic facts and probabilistic AI interpretations.

---

## 🛡️ Architectural Guarantee: Facts vs. Interpretation

```
              KEEP FACTS AND PROBABILISTIC INTERPRETATION SEPARATE
    ┌───────────────────────────────────┐  ┌───────────────────────────────────┐
    │     Deterministic Facts Pipeline   │  │   Probabilistic AI Pipeline       │
    │  - Trafilatura & BeautifulSoup    │  │  - Cloudflare Workers AI (Gemma 4)│
    │  - SHA-256 Content Hashing        │  │  - Single-pass clause extraction  │
    │  - Character-for-character cache  │  │  - Concise consumer impact context│
    │  - difflib paragraph diffs        │  │  - Verbatim excerpt citation      │
    │  - Server-side quote verification │  │  - Transparent uncertainty flags  │
    └───────────────────────────────────┘  └───────────────────────────────────┘
```

- **The Deterministic Pipeline is Authoritative**: What text was retrieved, when it was fetched, and whether words changed is established by cryptographic hashing and sequence matching.
- **Evidence-Backed Citations Only**: Every single finding presented to the consumer is required to contain an exact, verbatim quotation from the active policy text. If an excerpt cannot be found character-for-character in the source, **it is automatically dropped**.

---

## 🌟 Core Capabilities

### Single-Pass Gemma 4 Risk Scoring

Evaluates comprehensive legal policy text in a single end-to-end inference pass via Cloudflare Workers AI (`@cf/google/gemma-4-26b-a4b-it`) without arbitrary text splitting or chunking. Gemma 4 evaluates clauses across consumer risk categories:

- **Disputes**: Mandatory arbitration, jury trial waivers, class-action bans, venue restrictions.
- **Liability**: Total liability disclaimers, waivers of consequential damages, unilateral indemnification.
- **Termination**: Unilateral suspension or deletion without notice or cause.
- **Data**: Broad third-party sharing, cross-context tracking, AI model training rights.
- **Renewal**: Automatic subscription renewals, silent rollovers.
- **Price Changes**: Unilateral price adjustments without advance opt-out.
- **Cancellation**: Burdensome retention barriers, non-refundable retainers.

### High-Impact Clause Prioritization (Disputes, Arbitration & Safety)

Specialized heuristics ensure that critical legal clauses—specifically mandatory arbitration, court waivers, class action bans, unilateral indemnification, and any provisions impacting human safety or liability—are explicitly surfaced and flagged when present. Risk ratings follow calibrated baselines out of 100 rather than arbitrary spikes.

### Character-for-Character Verification & Cache

Before invoking any AI inference, EasyFinePrint compares newly extracted text against existing database baselines character-for-character:

- If content matches identically end-to-end, the baseline analysis is served immediately (**< 100ms**).
- Re-analyzing an existing tracked policy strictly verifies character identity: if no text changed, redundant LLM inference is bypassed, ensuring consumer risk scores remain stable and deterministic.

### Server-Side Verbatim Quotation Validation

All candidate findings extracted by Gemma undergo server-side substring verification:

- Standardizes unicode quotes (`“`, `”`, `’`, `‘`) and whitespace.
- Verifies that the excerpt appears verbatim in the source document.
- Assigns a formal audit status (`passed`, `partial`, or `failed`).

### Deterministic Paragraph Diffing Engine

Powered by Python's `difflib.SequenceMatcher`:

- Calculates granular additions, removals, and modifications between consecutive snapshots.
- Changes are presented side-by-side with color-coded additions (emerald) and removals (rose).
- Gemma 4 is prompted specifically to evaluate the practical implications of only the deterministic diff blocks.

### Fail-Safe Baseline Snapshot Protection

If an external server returns HTTP 500, encounters a timeout, or triggers a bot challenge:

- EasyFinePrint records an `extraction_failed` check event.
- The previous healthy baseline snapshot is **never overwritten** and never falsely reported as "unchanged".

### Strict Multi-Layer SSRF Guard

Every outbound fetch is guarded by a comprehensive defense-in-depth security layer:

- **Scheme Validation**: Enforces `http://` and `https://` only; rejects `file://`, `ftp://`, `gopher://`, etc.
- **Credential Stripping**: Rejects URLs containing inline user credentials (`http://user:pass@host`).
- **Port Restriction**: Restricts outbound connections strictly to ports `80` and `443`.
- **DNS Resolution & IP Verification**: Resolves both IPv4 and IPv6 addresses before connecting.
- **Blocked Ranges**: Blocks loopback (`127.0.0.0/8`, `::1`), private networks (RFC 1918 `10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`), cloud metadata (`169.254.169.254`, `fd00:ec2::254`), and link-local ranges.
- **Hop-by-Hop Redirect Revalidation**: Follows redirects manually, validating the target IP at every single hop.

### Zero-Cost Company Policy Discovery Engine

Instant policy discovery without third-party search APIs or quota caps:

- **Authoritative Directory**: Curated index of 30+ top platforms (Discord, Spotify, Roblox, GitHub, OpenAI, Google, Apple, Microsoft, Amazon, Meta, Twitter/X, Uber, Airbnb, Stripe, PayPal, Twitch, TikTok, LinkedIn, Steam, Slack, Zoom, Dropbox, Notion, Figma, Anthropic, Vercel, Cloudflare, etc.).
- **SSRF-Safe Direct Website Inspector**: For unindexed companies, safely inspects the corporate homepage under strict multi-hop SSRF validation to discover verified legal links (`terms`, `privacy`, `legal`).
- **In-Memory Cache**: Transparently caches lookup results to eliminate duplicate outbound requests.

### NoSQL & Network Hardening (Security Headers & Prompt Isolation)

- **NoSQL Operator Sanitization**: All database queries sanitize ID strings (`^[a-zA-Z0-9_-]{1,128}$`) and bind criteria strictly with MongoDB's `$eq` operator.
- **Prompt Isolation**: Legal document text is enclosed inside `<UNTRUSTED_DOCUMENT_CONTENT>` boundary tags to prevent indirect prompt injection.
- **Security Headers**: Injects HSTS, CSP, X-Frame-Options (`DENY`), X-Content-Type-Options (`nosniff`), Referrer-Policy, and 10 MB payload caps.

---

## 🛠️ Technology Stack

| Component              | Technology                                                                | Description                                                                 |
| ---------------------- | ------------------------------------------------------------------------- | --------------------------------------------------------------------------- |
| **Frontend Framework** | React 19 + Vite 8                                                         | Ultra-fast client-side SPA with React Router & automatic scroll restoration |
| **Styling & Icons**    | Vanilla CSS + Tailwind CSS v4, Lucide React                               | Sleek dark-mode aesthetic with custom themed scrollbars & responsive grid   |
| **Backend API**        | FastAPI (Python 3.12+)                                                    | Asynchronous REST endpoints with Pydantic validation                        |
| **AI Inference**       | Cloudflare Workers AI REST API, Gemma 4 (`@cf/google/gemma-4-26b-a4b-it`) | Single-pass structured reasoning and clause extraction                      |
| **Content Extraction** | Trafilatura, BeautifulSoup4                                               | Robust HTML parsing and boilerplate removal                                 |
| **Diff & Hashing**     | Python `difflib`, `hashlib.sha256`                                        | Deterministic paragraph diffing and content hashes                          |
| **Database**           | MongoDB Atlas (Motor AsyncIO driver)                                      | Resilient document persistence with in-memory test fallback                 |
| **Company Discovery**  | Authoritative Directory + Direct Website Inspector                        | Zero-cost legal policy discovery                                            |
| **Deployment**         | Vercel Serverless Functions                                               | Production serverless API and edge static frontend                          |

---

## 📡 API Reference

| Method | Endpoint                                     | Description                                                                                          |
| ------ | -------------------------------------------- | ---------------------------------------------------------------------------------------------------- |
| `POST`   | `/api/policies/analyze`                      | Ingests a public policy URL, validates text, caches or runs single-pass risk analysis.               |
| `POST`   | `/api/policies/analyze-self`                 | Evaluates EasyFinePrint's own Terms of Use or Privacy Policy directly without network hops.          |
| `GET`    | `/api/policies`                              | Lists all monitored policies with latest score and status.                                           |
| `GET`    | `/api/policies/{id}`                         | Retrieves detailed policy information and the latest validated clause findings.                      |
| `DELETE` | `/api/policies/{id}`                         | Permanently deletes a monitored policy and its snapshots, analyses, and check events.               |
| `POST`   | `/api/policies/{id}/check`                   | Safely fetches live page, performs character-for-character comparison, and diffs if changed.         |
| `POST`   | `/api/policies/{id}/reanalyze`               | Re-evaluates an existing baseline snapshot through Gemma 4 (skips if text unchanged).                |
| `GET`    | `/api/policies/{id}/history`                 | Retrieves chronologically ordered check events, snapshot transitions, and audit logs.                |
| `GET`    | `/api/policies/{id}/snapshots/{snapshot_id}` | Retrieves raw snapshot text, content hash, and HTTP status code.                                     |
| `GET`    | `/api/self-policies`                         | Lists metadata and markdown content for self-hosted legal policies (Terms of Use & Privacy Policy).  |
| `POST`   | `/api/discovery/search`                      | Legal policy URL lookup via authoritative directory & SSRF-safe direct website inspection.           |
| `POST`   | `/api/tunnel`                                | Sentry envelope reverse-proxy tunnel with DSN host validation (bypasses Brave Shields & adblockers). |
| `GET`    | `/api/health`                                | Service health status and MongoDB connectivity check.                                                |

---

### Sentry Envelope Tunneling & Adblocker Compatibility

When browser privacy shields (like Brave Shields or uBlock Origin) are enabled, third-party error monitoring beacons are frequently intercepted and dropped. EasyFinePrint implements same-origin Sentry envelope tunneling:

- **Same-Origin Route**: The frontend dispatches envelopes to `${API_BASE}/api/tunnel`, which adblockers recognize as first-party application traffic.
- **Host-Bound Relay**: The backend inspects the envelope header and validates that the destination DSN hostname is an authentic Sentry ingest server (`*.sentry.io`), rejecting untrusted targets with HTTP 403 to prevent open proxying.
- **No Session Replays**: We do not embed session replay scripts (such as `rrweb`), screen recording, or DOM mutation listeners. No browser interactions or user sessions are recorded.
- **Telemetry Redaction**: Automated filters strip sensitive headers (including `Authorization` and `Cookie`), request payloads, and URL query strings before diagnostic reports are transmitted.
- **Console Log Redaction**: Outbound HTTP client logging (`httpx`, `httpcore`) is silenced to `WARNING` in the application, and the unified development runner (`start.py`) scrubs Sentry DSNs, ingest hostnames, and telemetry endpoints (`https://[REDACTED_SENTRY_ENDPOINT]`) from console output.

---

## 💻 Local Development & Setup

### Prerequisites

- Python 3.12+ (tested on Python 3.12, 3.13, 3.14)
- Node.js 18+ and npm

### 1. Clone the Repository

```bash
git clone https://github.com/diptodeepb/EasyFinePrint.git
cd EasyFinePrint
```

### 2. Environment Configuration

Create a `.env` file in `backend/`:

```bash
cp backend/.env.example backend/.env
```

Configure your environment variables:

```ini
# Cloudflare Workers AI Configuration (for live Gemma 4 inference)
CLOUDFLARE_API_TOKEN="your_cloudflare_api_token"
CLOUDFLARE_ACCOUNT_ID="your_cloudflare_account_id"
CLOUDFLARE_AI_MODEL="@cf/google/gemma-4-26b-a4b-it"

# MongoDB Atlas connection string (or local mongodb://localhost:27017)
MONGODB_URI="mongodb+srv://user:password@cluster.mongodb.net/?retryWrites=true&w=majority"
MONGODB_DB="easyfineprint"

# Frontend origin for CORS
FRONTEND_ORIGIN="http://localhost:5173"
ENVIRONMENT="development"
```

_(Note: If `CLOUDFLARE_API_TOKEN` / `CLOUDFLARE_ACCOUNT_ID` is omitted, EasyFinePrint runs in deterministic fallback mode with all diffing, hashing, and version tracking fully operational.)_

### 3. Install Dependencies

```bash
# Backend Virtual Environment
python3 -m venv backend/.venv
source backend/.venv/bin/activate
pip install -r backend/requirements.txt

# Frontend Packages
npm --prefix frontend install
```

### 4. One-Command Unified Runner

Start both the FastAPI backend and Vite frontend development servers concurrently with clean, color-coded prefixes (`[system]`, `[backend]`, `[frontend]`, `[error]`) and real-time credential redaction to prevent accidental token or connection string exposure in console logs:

```bash
python3 start.py
```

- **Web Interface**: [http://localhost:5173](http://localhost:5173)
- **FastAPI Engine**: [http://localhost:8000](http://localhost:8000)
- **Interactive OpenAPI Documentation**: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 🧪 Automated Testing & CI

EasyFinePrint includes an automated test suite of **51 comprehensive tests** (100% pass rate) covering Cloudflare Workers AI integration, single-pass clause extraction, SSRF multi-hop validation, deterministic Myers diffing, verbatim quote validation, company discovery, Sentry envelope tunneling, cascade policy deletion, and self-hosted policy analysis:

```bash
# Run tests locally
backend/.venv/bin/pytest backend/tests/ -v
# Output: ======================== 51 passed in 98.24s ========================
```

### CI Pipeline

A GitHub Actions workflow ([`.github/workflows/ci.yml`](.github/workflows/ci.yml)) automatically runs on every push and pull request:

- **Backend Job**: Sets up Python, caches pip dependencies, runs linting, and executes the complete 50-test pytest suite.
- **Frontend Job**: Sets up Node.js, installs dependencies, and runs `npm run build` to verify production bundling.

---

## ☁️ Zero-Cost Vercel Serverless Deployment

EasyFinePrint is configured for both separate two-project deployment and single unified monorepo deployment:

### Option A: Two Separate Vercel Projects (Recommended)

1. **Backend Serverless API**:
   - Create a new project on Vercel importing this repository.
   - Set **Root Directory** to `backend`.
   - Vercel automatically detects [`backend/vercel.json`](backend/vercel.json) and [`backend/api/index.py`](backend/api/index.py).
   - In **Project Settings** → **Environment Variables**, set:
     - `MONGODB_URI`: Your MongoDB Atlas connection string.
     - `CLOUDFLARE_API_TOKEN`: Your Cloudflare Workers AI API token.
     - `CLOUDFLARE_ACCOUNT_ID`: Your Cloudflare Account ID.
     - `CLOUDFLARE_AI_MODEL`: `@cf/google/gemma-4-26b-a4b-it`
     - `FRONTEND_ORIGIN`: Your deployed frontend Vercel URL (e.g., `https://easyfineprint-frontend.vercel.app`).
     - `ENVIRONMENT`: `production`

2. **Frontend React SPA**:
   - Create a second project on Vercel importing the same repository.
   - Set **Root Directory** to `frontend`.
   - Vercel automatically detects [`frontend/vercel.json`](frontend/vercel.json).
   - **404 Prevention Guarantee**: [`frontend/vercel.json`](frontend/vercel.json) includes `cleanUrls: true` and SPA rewrite `/(.*) -> /index.html`, ensuring deep link navigation and page refreshes on `/policies/:id` never trigger Vercel 404 Not Found errors.
   - In **Project Settings** → **Environment Variables**, set:
     - `VITE_API_URL`: Your deployed backend Vercel URL (e.g., `https://easyfineprint-backend.vercel.app`).

---

### Option B: Single Unified Monorepo

Deploy both frontend and backend in a single project using the root [`vercel.json`](vercel.json) and [`api/index.py`](api/index.py):

- Leave **Root Directory** as `/`.
- In **Project Settings** → **Environment Variables**, configure `MONGODB_URI`, `CLOUDFLARE_API_TOKEN`, `CLOUDFLARE_ACCOUNT_ID`, and `FRONTEND_ORIGIN`.
- Vercel builds the React SPA and provisions Python serverless routes for `/api/*` with SPA fallback.

---

## 🔒 Security & Threat Model

- **Anti-Reconnaissance & Info Disclosure Guard**: Public `/api/health` and error responses omit internal model IDs, providers, and database topology. Development runner logs automatically redact Bearer tokens and connection strings.
- **SSRF Defense**: Strict scheme, port, IP resolution, and hop-by-hop redirect verification.
- **NoSQL Injection Resistance**: Alphanumeric ID sanitization with MongoDB `$eq` operator binding.
- **Prompt Injection Isolation**: Policy content is sanitized and sandboxed within `<UNTRUSTED_DOCUMENT_CONTENT>` boundary tags.
- **Zero Hallucination Tolerance**: No finding is presented to the user unless backed by an exact verbatim excerpt verified by the server-side validator.
- **Strict Telemetry Redaction**: Zero personal data collection, anonymized IP masking (`0.0.0.0`), sensitive header and cookie stripping, and zero browser session replay recording.
- **HTTP Security Headers**: HSTS, CSP, X-Frame-Options (`DENY`), X-Content-Type-Options (`nosniff`), Referrer-Policy, and 10 MB payload caps.

For in-depth threat analysis and mitigations, see [`docs/threat-model.md`](docs/threat-model.md).

---

## 📄 License

This project is licensed under the [Apache 2.0 License](LICENSE).
