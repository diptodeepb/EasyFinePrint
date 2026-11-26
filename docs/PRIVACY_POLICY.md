# EasyFinePrint Privacy Policy

**Effective Date:** November 27, 2026  
**License:** Apache License 2.0

---

## 1. Overview & Commitment to Privacy

**EasyFinePrint** ("we", "our", "us", or "the Platform") is built on a straightforward principle: we do not collect personal data. We believe software that analyzes privacy policies should lead by example.

We do not sell personal data, we do not operate tracking cookies or advertising pixels, and we do not profile users. Public URLs submitted for analysis are processed purely to extract public policy text, calculate cryptographic SHA-256 hashes, and track changes across revisions.

---

## 2. Information We Do Not Collect

We deliberately design our systems to avoid collecting personal information:

- **No Personal Identifiable Information (PII):** No names, email addresses, phone numbers, billing details, or user accounts.
- **No Advertising Trackers:** No third-party advertising pixels, Google Analytics, or marketing beacons.
- **No Persistent Tracking Cookies:** No cookies tracking your browsing behavior across visits or domains.
- **No Session Replays:** We do not embed session recording scripts (`rrweb`) or capture user keystrokes or screen interactions.
- **No Private Documents:** We do not accept or store private contracts, non-disclosure agreements, or confidential personal records.

---

## 3. Processing of Public Agreement URLs

When you submit a URL for analysis or change monitoring:

1. **Document Retrieval:** The Service retrieves the publicly accessible HTML document from the destination server (or falls back to the public Internet Archive Wayback Machine or user-pasted text with explicit provenance tags).
2. **Normalization and Hashing:** Markup is stripped and whitespace is normalized to calculate a SHA-256 cryptographic hash.
3. **Snapshot Storage:** The normalized public text, word count, hash, and timestamp are stored as an immutable snapshot to enable sequence diffing when the target agreement updates.
4. **Public Scope:** All stored documents are public legal agreements already accessible on the open web.

---

## 4. Language Model and Text Analysis

When agreement clauses are evaluated, public policy text is processed statelessly inside untrusted-content boundaries. Inputs are evaluated solely to classify clause categories and identify potential concerns. Text processed through our evaluation pipeline is not retained for training commercial foundation models.

---

## 5. Security, Audit Logging, and Telemetry Protection

We implement defense-in-depth operational security controls aligned with OWASP Top 10 (2025) and OWASP API Security Top 10 (2023):

- **Zero-PII Telemetry & Safe Tunneling:** Operational error monitoring strips sensitive headers (`Authorization`, `Cookie`, `X-Admin-Key`), query parameters, and request payloads before transmission, and anonymizes client IPs (`0.0.0.0`). Same-origin telemetry tunneling (`/api/tunnel`) validates `https://*.sentry.io` hosts and numeric project IDs strictly.
- **Privacy-Preserving Security Audit Logs:** Security events (such as rate-limit triggers, SSRF blocks, or unauthorized requests) use one-way SHA-256 IP reference prefixes (`ip_<hash>`) and automatic credential redaction rather than storing raw personal IP logs.
- **Outbound SSRF Protection:** All outbound document fetches and company discovery probes disable automatic redirects and enforce hop-by-hop DNS/IP verification, blocking loopback addresses (`127.0.0.1`, `::1`), private subnets, IPv6 tunneling ranges, and cloud provider metadata addresses (`169.254.169.254`).
- **Transport, Browser & Payload Boundaries:** Production deployments enforce HSTS, strict Content Security Policy (`script-src 'self'`), `X-Frame-Options: DENY`, CSRF origin checks, per-IP rate limiting, and streaming request size limits (10 MB general, 256 KB tunnel, 64 KB discovery).

---

## 6. Open Source Transparency and Self-Hosting

EasyFinePrint is licensed under the **Apache License 2.0**. The full source code is publicly accessible and auditable on GitHub, allowing anyone to verify our data processing practices or run an independent instance locally with complete data sovereignty.

---

## 7. Data Retention and Removal Requests

Public agreement snapshots are retained to maintain historical change records. If you are an authorized representative of an organization and wish to request the removal of an indexed public agreement from our demonstration instances, you may submit a request through our repository issue tracker.

---

## 8. Changes to This Privacy Policy

We may revise this Privacy Policy from time to time. Any revisions will be committed directly to our public repository with verifiable commit timestamps. Your continued use of EasyFinePrint following published updates constitutes your acceptance of the modified Privacy Policy.

---

## 9. Contact Information

For any inquiries regarding this Privacy Policy, please open an issue on our GitHub repository: [https://github.com/diptodeepb/EasyFinePrint/issues](https://github.com/diptodeepb/EasyFinePrint/issues).
