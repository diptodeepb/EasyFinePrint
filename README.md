# EasyFinePrint 🔍📜

> **An evidence-backed monitor for public Terms of Service and Privacy Policy changes.**
> Deterministic text diffing paired with hosted Gemma AI. No hallucinated claims—every finding is strictly tied to verifiable source quotations.

[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-19-61DAFB?logo=react&logoColor=black)](https://react.dev)
[![Vite](https://img.shields.io/badge/Vite-8.3+-646CFF?logo=vite&logoColor=white)](https://vitejs.dev)
[![TailwindCSS](https://img.shields.io/badge/TailwindCSS-v4-06B6D4?logo=tailwindcss&logoColor=white)](https://tailwindcss.com)
[![Google Gemma](https://img.shields.io/badge/Gemma-Gemini%20API%20Free-4285F4?logo=google&logoColor=white)](https://ai.google.dev)
[![MongoDB Atlas](https://img.shields.io/badge/MongoDB-Atlas%20M0%20Free-47A248?logo=mongodb&logoColor=white)](https://www.mongodb.com/atlas)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)

---

## 💡 The Core Idea

People rarely revisit lengthy legal agreements after initial signup. When companies revise their Terms of Service or Privacy Policies, consumers are left in the dark about new auto-renewals, arbitration clauses, or expanded data sharing.

**EasyFinePrint solves this with an architectural guarantee:**

```
                  KEEP FACTS AND INTERPRETATION SEPARATE
       ┌──────────────────────────────┐  ┌──────────────────────────────┐
       │     Deterministic Facts      │  │  Probabilistic Explanation  │
       │  - Trafilatura extraction    │  │  - Hosted Gemma AI          │
       │  - SHA-256 content hashes    │  │  - Plain-English wording    │
       │  - difflib paragraph diffs   │  │  - Consumer impact context  │
       │  - Verbatim quote validation │  │  - Uncertainty notes        │
       └──────────────────────────────┘  └──────────────────────────────┘
```

The deterministic pipeline is the authoritative truth for what text was retrieved and what changed. Gemma explains bounded differences in plain English. If an AI finding references an excerpt that cannot be found verbatim in the source text, **the finding is dropped**.

---

## ✨ Key Features

1. **Policy Risk Analyzer**: Extracts public policy text and identifies consumer concerns (auto-renewals, dispute resolution, liability limits, price modifications, data sharing) paired with verbatim quotations.
2. **Deterministic Change Monitor**: Stores immutable snapshots. On recheck, computes paragraph-level diffs (`additions`, `removals`, `modifications`). If identical, the model call is skipped to save quota.
3. **Fail-Safe Baseline Protection**: A 404, network error, or anti-bot challenge is recorded as an `extraction_failed` event; the previous baseline snapshot is **never overwritten** and never reported as "unchanged".
4. **Strict SSRF Guard**: Enforces absolute URL checks, DNS resolution across IPv4 and IPv6, blocking loopback (`127.0.0.1`, `::1`), private networks (RFC 1918), and cloud metadata (`169.254.169.254`, `fd00:ec2::254`). Re-validates each destination across redirect chains.
5. **Quota-Guarded Discovery Fallback**: Optional SerpApi company name lookup with in-memory caching and strict monthly (200) and hourly (40) caps. Disabled by default.
6. **Strictly Zero-Cost Architecture**: Operates entirely within free tiers (Render Static Site, Render Free Web Service, MongoDB Atlas M0, Google GenAI free tier).

---

## 🛠️ Technology Stack

| Layer | Technology | Role |
|---|---|---|
| **Frontend** | React 19, Vite, Tailwind CSS v4, Lucide React, React Router | Modern glassmorphic SPA |
| **Backend** | FastAPI, Pydantic Settings, Uvicorn, httpx | Asynchronous REST API & SSRF Guard |
| **Extraction** | Trafilatura, BeautifulSoup4 | Legal text extraction with fallback |
| **Diff & Hashing** | Python `difflib.SequenceMatcher`, `hashlib.sha256` | Deterministic change detection |
| **AI Inference** | Google GenAI SDK (`google-genai`), Gemma 4 | Structured plain-English explanation |
| **Database** | MongoDB Atlas Free (M0) via Motor (asyncio) | Immutable snapshots and check history |
| **Testing** | Pytest, Pytest-Asyncio | 27 automated unit & lifecycle tests |

---

## 🚀 Quickstart & Local Setup

### Prerequisites
- Python 3.10+ (tested on Python 3.14)
- Node.js 18+ and npm

### 1. Clone the repository
```bash
git clone https://github.com/diptodeepb/EasyFinePrint.git
cd EasyFinePrint
```

### 2. Configure Backend Environment
```bash
cp backend/.env.example backend/.env
```
*(Optional: Add your `GEMINI_API_KEY` for live AI explanations. If left blank, EasyFinePrint operates in deterministic fallback mode with all diffs and version tracking fully functional!)*

### 3. Install Dependencies
```bash
# Backend virtual environment
python3 -m venv backend/.venv
source backend/.venv/bin/activate
pip install -r backend/requirements.txt

# Frontend dependencies
cd frontend
npm install
cd ..
```

### 4. Run Both Servers Concurrently
Run the unified runner script:
```bash
./start.py
```
- **Frontend SPA**: [http://localhost:5173](http://localhost:5173)
- **FastAPI Backend**: [http://localhost:8000](http://localhost:8000)
- **Interactive OpenAPI Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 🧪 Automated Test Suite

Run the complete test suite:
```bash
backend/.venv/bin/pytest backend/tests/ -v
```

The test suite validates:
- **SSRF Defenses**: Private IPv4, IPv6 loopback, cloud metadata endpoints, bad protocols, and credentials.
- **Normalization & Hashing**: Format-only changes, punctuation stability, and deterministic hash matching.
- **Deterministic Diffing**: Clause additions, removals, and wording modifications.
- **Evidence Validator**: Verbatim quote acceptance, fabricated quote rejection, and partial finding filtering.
- **Lifecycle & Fail-Safe Flow**: Initial baseline, unchanged recheck, failed fetch snapshot preservation, and check events.
- **SerpApi Quota Guard**: Hourly and monthly limits, caching, and graceful degradation.

---

## ☁️ Zero-Cost Deployment Runbook (Render + MongoDB Atlas)

EasyFinePrint includes an automated Render Blueprint in [`render.yaml`](render.yaml):

1. **MongoDB Atlas M0 Cluster**:
   - Create a free M0 cluster on [MongoDB Atlas](https://www.mongodb.com/atlas).
   - Create a database user and whitelist network access (`0.0.0.0/0` with user authentication).
   - Copy the MongoDB connection string.
2. **Deploy on Render**:
   - Push your code to GitHub.
   - On [Render](https://dashboard.render.com), click **New +** → **Blueprint** and select your repository.
   - Set the environment variables in the Render dashboard:
     - `MONGODB_URI`: Your MongoDB Atlas URI.
     - `GEMINI_API_KEY`: Your Google Gemini API key.
   - Render automatically provisions the FastAPI Web Service and the React Static Site!

---

## 🔒 Security & Privacy Disclosures

- **Public Policies Only**: EasyFinePrint is designed exclusively for public Terms of Service and Privacy Policies. Never upload private or confidential contracts.
- **Untrusted Input Boundaries**: Policy text is treated as potentially adversarial data. Prompts strictly forbid executing instructions found within document bodies.
- **Source Quote Provenance**: AI summaries are for convenience; always click to review the exact source excerpts provided in each finding card.
- **Zero Financial Risk**: The application enforces application-level limits below third-party free quotas and never requires a credit card or pay-as-you-go infrastructure.

---

## 📄 License

Distributed under the Apache 2.0 License. See [`LICENSE`](LICENSE) for details.
