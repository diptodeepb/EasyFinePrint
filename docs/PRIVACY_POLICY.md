# EasyFinePrint Privacy Policy

**Effective Date:** October 24, 2026  
**Document Version:** 1.0.0  
**License:** Apache License 2.0  
**Repository:** [https://github.com/diptodeepb/EasyFinePrint](https://github.com/diptodeepb/EasyFinePrint)  

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
- **No Private Documents:** We do not accept or store private contracts, non-disclosure agreements, or confidential personal records.

---

## 3. Processing of Public Agreement URLs

When you submit a URL for analysis or change monitoring:

1. **Document Retrieval:** The Service retrieves the publicly accessible HTML document from the destination server.
2. **Normalization and Hashing:** Markup is stripped and whitespace is normalized to calculate a SHA-256 cryptographic hash.
3. **Snapshot Storage:** The normalized public text, word count, hash, and timestamp are stored as an immutable snapshot to enable sequence diffing when the target agreement updates.
4. **Public Scope:** All stored documents are public legal agreements already accessible on the open web.

---

## 4. Language Model and Text Analysis

When agreement clauses are evaluated, public policy text is processed statelessly. Inputs are evaluated solely to classify clause categories and identify potential concerns. Text processed through our evaluation pipeline is not retained for training commercial foundation models.

---

## 5. Security and Telemetry Protection

We implement strict operational security controls:

- **Telemetry Redaction:** Operational error monitoring is configured with automated filters that strip sensitive headers (including Authorization and Cookie headers) before any report is transmitted.
- **Outbound SSRF Protection:** Document retrieval enforces DNS verification at each redirect hop, blocking loopback addresses (`127.0.0.1`), private subnets, and cloud provider metadata addresses (`169.254.169.254`).
- **Request Boundaries:** Inbound requests enforce strict size limits (10 MB) to prevent buffer exhaustion.

---

## 6. Open Source Transparency and Self-Hosting

EasyFinePrint is licensed under the **Apache License 2.0**. The full source code is publicly accessible and auditable on GitHub, allowing anyone to verify our data processing practices or run an independent instance locally with complete data sovereignty.

---

## 7. Data Retention and Removal Requests

Public agreement snapshots are retained to maintain historical change records. If you are an authorized representative of an organization and wish to request the removal of an indexed public agreement from our demonstration instances, you may submit a request through our repository issue tracker.

---

## 8. Changes to This Privacy Policy

Any revisions to this Privacy Policy will be published directly to our source repository with timestamped version history. Your continued use of the Platform after changes are posted represents your acknowledgment of the updated policy.

---

## 9. Contact Information

For any inquiries regarding this Privacy Policy, please open an issue on our GitHub repository: [https://github.com/diptodeepb/EasyFinePrint/issues](https://github.com/diptodeepb/EasyFinePrint/issues).
