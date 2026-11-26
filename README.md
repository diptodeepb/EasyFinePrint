<div align="center">
  <img src="frontend/public/logo.svg" alt="EasyFinePrint Logo" width="96" height="96" />
  <h1>EasyFinePrint</h1>
  <p>
    <strong>Public Legal Agreements Auditor</strong> — Deterministic Policy Diffing &amp; Single-Pass Clause Risk Intelligence.<br />
    Audit public Terms of Service and Privacy Policies for arbitration traps, broad data sharing, and unilateral changes—grounded strictly in verbatim citations.
  </p>
  <p>
    <a href="https://github.com/diptodeepb/EasyFinePrint/actions/workflows/ci.yml"><img src="https://github.com/diptodeepb/EasyFinePrint/actions/workflows/ci.yml/badge.svg" alt="CI" /></a>
    <a href="LICENSE"><img src="https://img.shields.io/badge/License-Apache_2.0-blue.svg" alt="License: Apache 2.0" /></a>
    <a href="https://www.python.org/downloads/"><img src="https://img.shields.io/badge/python-3.12+-blue.svg" alt="Python 3.12+" /></a>
    <a href="https://fastapi.tiangolo.com"><img src="https://img.shields.io/badge/FastAPI-0.115+-009688.svg" alt="FastAPI" /></a>
    <a href="https://react.dev"><img src="https://img.shields.io/badge/React-19-61dafb.svg" alt="React 19" /></a>
  </p>
</div>

---

## Table of Contents

- [Core Guarantee: Facts vs. Interpretation](#core-guarantee-facts-vs-interpretation)
- [Tech Stack](#tech-stack)
- [API Endpoints](#api-endpoints)
- [Local Setup](#local-setup)
- [Testing & Verification](#testing--verification)
- [Vercel Deployment](#vercel-deployment)
- [Documentation](#documentation)
- [License](#license)

---

## Core Guarantee: Facts vs. Interpretation

EasyFinePrint separates deterministic evidence from probabilistic AI interpretation:

- **Deterministic Facts**: `trafilatura` / `BeautifulSoup` / SPA hydration extraction, SHA-256 content hashing, exact character-for-character cache reuse, and `difflib` paragraph diffs.
- **Evidence-Grounded AI**: Single-pass clause extraction via Cloudflare Workers AI (`@cf/google/gemma-4-26b-a4b-it`). Every finding requires a verbatim `exact_excerpt` verified against the source text—unsupported claims are dropped server-side.
- **4-Tier Ingestion**: (1) Live fetch + SPA hydration, (2) Wayback Machine archive fallback, (3) User-pasted text with immutable `user_pasted` provenance, and (4) Database baseline fallback.
- **Zero-Cost Discovery**: Instant search across 438+ curated services (869+ policy URLs) with SSRF-safe website fallback.
- **OWASP Top 10 (2025) & API Security Top 10 (2023)**: Hop-by-hop SSRF protection (IPv4/IPv6/tunneling), strict CSP (`script-src 'self'`), XSS URL sanitization, per-IP sliding-window rate limiting, streaming body caps, isolated `node:vm` execution, production OpenAPI hiding, and zero-PII audit logs.

---

## Tech Stack

| Layer            | Technologies                                                                                   |
| :--------------- | :--------------------------------------------------------------------------------------------- |
| **Frontend**     | React 19, Vite 8, Tailwind CSS v4, React Router, Lucide Icons, Sentry (`@sentry/react`)        |
| **Backend**      | FastAPI (Python 3.12+), Pydantic v2, `httpx`, `trafilatura`, `beautifulsoup4`                  |
| **AI & Diffing** | Cloudflare Workers AI (Gemma 4 26B), `difflib`, `hashlib` (SHA-256)                            |
| **Database**     | MongoDB Atlas (Motor AsyncIO + single-roundtrip `$lookup` aggregation) with in-memory fallback |
| **Hosting**      | Vercel (Static Edge SPA + Python Serverless Functions)                                         |

---

## API Endpoints

| Method   | Endpoint                                     | Purpose                                                                    |
| :------- | :------------------------------------------- | :------------------------------------------------------------------------- |
| `POST`   | `/api/policies/analyze`                      | Ingests a public URL (or pasted text) and runs single-pass clause analysis |
| `POST`   | `/api/policies/analyze-self`                 | Audits EasyFinePrint's own Terms of Use or Privacy Policy                  |
| `GET`    | `/api/policies`                              | Lists monitored policies with latest score and provenance                  |
| `GET`    | `/api/policies/{id}`                         | Retrieves policy details and verified clause findings                      |
| `POST`   | `/api/policies/{id}/check`                   | Checks for updates and computes paragraph diffs on change                  |
| `POST`   | `/api/policies/{id}/reanalyze`               | Re-evaluates baseline (skips AI if text is unchanged)                      |
| `GET`    | `/api/policies/{id}/history`                 | Lists chronological check events and snapshot transitions                  |
| `GET`    | `/api/policies/{id}/snapshots/{snapshot_id}` | Returns raw normalized snapshot text and metadata                          |
| `DELETE` | `/api/policies/{id}`                         | Deletes a policy (`ADMIN_API_KEY` protected; disabled in prod if unset)    |
| `GET`    | `/api/policies/self-policies`                | Lists EasyFinePrint's own Terms of Use and Privacy Policy                  |
| `POST`   | `/api/discovery/search`                      | Searches company policy URLs via directory + safe crawling                 |
| `POST`   | `/api/tunnel`                                | Host-validated Sentry envelope relay (`*.sentry.io`)                       |
| `GET`    | `/api/health`                                | Minimal service readiness status                                           |

---

## Local Setup

```bash
git clone https://github.com/diptodeepb/EasyFinePrint.git
cd EasyFinePrint

# 1. Configure environment (AI & MongoDB are optional; deterministic fallback runs without them)
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env

# 2. Install dependencies
python3 -m venv backend/.venv
backend/.venv/bin/pip install -r backend/requirements.txt
npm --prefix frontend install

# 3. Start backend (:8000) + frontend (:5173) with log redaction
python3 start.py
```

---

## Testing & Verification

```bash
# Backend dependency & test suite (107 passed, 1 live-model test skipped offline)
backend/.venv/bin/pip check
backend/.venv/bin/pytest backend/tests/ -v

# Frontend lint, unit tests, and production build
npm --prefix frontend run lint
node --test frontend/src/lib/policiesCache.test.js frontend/src/lib/scrollLock.test.js frontend/src/lib/safeUrl.test.js
npm --prefix frontend run build
```

---

## Vercel Deployment

- **Option A (Two Projects — Recommended)**: Deploy `backend/` (`backend/vercel.json`) and `frontend/` (`frontend/vercel.json`) separately. Set `VITE_API_URL` on the frontend project; set `MONGODB_URI`, `CLOUDFLARE_API_TOKEN`, `CLOUDFLARE_ACCOUNT_ID`, `FRONTEND_ORIGIN`, and `ENVIRONMENT=production` on the backend project.
- **Option B (Monorepo)**: Deploy `/` using the root [`vercel.json`](vercel.json) and [`api/index.py`](api/index.py) with the same backend environment variables.

_(In production, `/docs` and `/openapi.json` are hidden by default, `DELETE` requires `ADMIN_API_KEY` or fails closed with `403`, and Vercel proxy headers are auto-detected via `VERCEL=1`.)_

---

## Documentation

- [System Architecture](docs/architecture.md)
- [Security & OWASP Threat Model](docs/threat-model.md)
- [Evaluation & Test Results](docs/evaluation.md)
- [Terms of Use](docs/TERMS_OF_USE.md)
- [Privacy Policy](docs/PRIVACY_POLICY.md)

---

## License

This project is released under the [Apache 2.0 License](LICENSE).
