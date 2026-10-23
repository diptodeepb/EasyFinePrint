import React, { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import {
  ShieldCheck,
  Copy,
  Check,
  ChevronRight,
  ExternalLink,
  Loader2,
} from "lucide-react";
import { api } from "../lib/api";

export default function PrivacyPolicy() {
  const navigate = useNavigate();
  const [analyzing, setAnalyzing] = useState(false);
  const [copied, setCopied] = useState(false);
  const [error, setError] = useState("");

  const handleRunAnalysis = async () => {
    try {
      setAnalyzing(true);
      setError("");
      const policy = await api.analyzeSelfPolicy("privacy");
      navigate(`/policies/${policy.id}`);
    } catch (err) {
      setError(err.message || "Failed to analyze privacy policy.");
      setAnalyzing(false);
    }
  };

  const copyPrivacy = () => {
    const text =
      document.getElementById("privacy-content-body")?.innerText || "";
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 py-8 sm:py-12 space-y-8">
      {/* Navigation Breadcrumb */}
      <nav
        aria-label="Breadcrumb"
        className="flex items-center gap-2 text-xs font-mono text-zinc-500"
      >
        <Link to="/" className="hover:text-zinc-300 transition-colors">
          Dashboard
        </Link>
        <ChevronRight className="w-3.5 h-3.5 text-zinc-700" />
        <span className="text-zinc-300">Privacy Policy</span>
      </nav>

      {/* Document Header */}
      <header className="space-y-4 border-b border-zinc-800 pb-6">
        <div className="space-y-1.5">
          <h1 className="text-2xl sm:text-3xl font-semibold tracking-tight text-zinc-100">
            Privacy Policy
          </h1>
          <p className="text-xs sm:text-sm text-zinc-400 flex items-center gap-1.5 flex-wrap">
            <span>Effective Date: October 24, 2026</span>
            <span className="text-zinc-600">&middot;</span>
            <a
              href="https://github.com/diptodeepb/EasyFinePrint/blob/main/LICENSE"
              target="_blank"
              rel="noopener noreferrer"
              className="text-zinc-300 hover:text-white underline underline-offset-2 transition-colors inline-flex items-center gap-1"
            >
              <span>Apache License 2.0</span>
              <ExternalLink className="w-3 h-3 text-zinc-500" />
            </a>
          </p>
        </div>

        {/* Action Bar */}
        <div className="flex flex-wrap items-center justify-between gap-3 pt-2">
          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={handleRunAnalysis}
              disabled={analyzing}
              className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-md bg-zinc-900 hover:bg-zinc-850 active:bg-zinc-800 text-zinc-300 hover:text-zinc-100 border border-zinc-800 hover:border-zinc-700 text-xs font-mono transition-colors cursor-pointer active:scale-95 disabled:opacity-50"
            >
              {analyzing ? (
                <>
                  <Loader2 className="w-3.5 h-3.5 animate-spin text-zinc-400" />
                  <span>Analyzing document...</span>
                </>
              ) : (
                <>
                  <ShieldCheck className="w-3.5 h-3.5 text-zinc-400" />
                  <span>Analyze with EasyFinePrint</span>
                </>
              )}
            </button>

            <button
              type="button"
              onClick={copyPrivacy}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-md bg-zinc-900/60 hover:bg-zinc-850 text-zinc-300 border border-zinc-800 text-xs font-mono transition-colors cursor-pointer active:scale-95"
            >
              {copied ? (
                <>
                  <Check className="w-3.5 h-3.5 text-zinc-300" />
                  <span>Copied</span>
                </>
              ) : (
                <>
                  <Copy className="w-3.5 h-3.5 text-zinc-400" />
                  <span>Copy text</span>
                </>
              )}
            </button>
          </div>

          <a
            href="https://github.com/diptodeepb/EasyFinePrint/blob/main/docs/PRIVACY_POLICY.md"
            target="_blank"
            rel="noreferrer"
            className="inline-flex items-center gap-1 text-xs font-mono text-zinc-400 hover:text-zinc-200 transition-colors"
          >
            <span>View markdown source</span>
            <ExternalLink className="w-3 h-3 text-zinc-500" />
          </a>
        </div>

        {error && (
          <div className="text-xs font-mono text-rose-300 bg-rose-950/30 border border-rose-900/40 p-2.5 rounded-md">
            {error}
          </div>
        )}
      </header>

      {/* Summary Box */}
      <div className="p-4 rounded-lg bg-zinc-950 border border-zinc-800 text-xs text-zinc-400 leading-relaxed space-y-1.5 font-mono">
        <div className="text-zinc-200 font-semibold uppercase tracking-wider text-[11px]">
          Privacy Overview & Zero-Tracking Architecture
        </div>
        <p>
          EasyFinePrint operates a zero-tracking service. We do not collect
          personal data, we do not operate tracking cookies or advertising
          pixels, and we do not sell or monetize information. URLs submitted for
          monitoring are public agreements processed purely to compute
          cryptographic hashes and track text changes across revisions.
        </p>
      </div>

      {/* Document Body */}
      <article
        id="privacy-content-body"
        className="rounded-lg border border-zinc-300 bg-zinc-950/40 p-6 sm:p-8 space-y-8 text-sm text-zinc-300 leading-relaxed font-sans"
      >
        <section className="space-y-2.5">
          <h2 className="text-base font-semibold text-zinc-100">
            1. Overview and Commitment to Privacy
          </h2>
          <p>
            <strong>EasyFinePrint</strong> (&ldquo;we&rdquo;, &ldquo;our&rdquo;,
            &ldquo;us&rdquo;, or &ldquo;the Platform&rdquo;) is built on a
            straightforward principle: we do not collect personal data. We
            believe software that analyzes privacy policies should lead by
            example. We do not sell personal data, we do not operate tracking
            cookies or advertising pixels, and we do not profile users. Public
            URLs submitted for analysis are processed purely to extract public
            policy text, calculate cryptographic SHA-256 hashes, and track
            changes across revisions.
          </p>
        </section>

        <section className="space-y-2.5">
          <h2 className="text-base font-semibold text-zinc-100">
            2. Information We Do Not Collect
          </h2>
          <p>
            We deliberately design our systems to avoid collecting personal
            information:
          </p>
          <ul className="list-disc pl-5 space-y-2 text-zinc-400">
            <li>
              <strong>No Personal Identifiable Information (PII):</strong> No
              names, email addresses, phone numbers, billing details, or user
              accounts.
            </li>
            <li>
              <strong>No Advertising Trackers:</strong> No third-party
              advertising pixels, Google Analytics, or marketing beacons.
            </li>
            <li>
              <strong>No Persistent Tracking Cookies:</strong> No cookies
              tracking your browsing behavior across visits or domains.
            </li>
            <li>
              <strong>No Private Documents:</strong> We do not accept or store
              private contracts, non-disclosure agreements, or confidential
              personal records.
            </li>
          </ul>
        </section>

        <section className="space-y-2.5">
          <h2 className="text-base font-semibold text-zinc-100">
            3. Processing of Public Agreement URLs
          </h2>
          <p>When you submit a URL for analysis or change monitoring:</p>
          <ul className="list-disc pl-5 space-y-1.5 text-zinc-400">
            <li>
              <strong>Document Retrieval:</strong> The Service retrieves the
              publicly accessible HTML document from the destination server.
            </li>
            <li>
              <strong>Normalization and Hashing:</strong> Markup is stripped and
              whitespace is normalized to calculate a SHA-256 cryptographic
              hash.
            </li>
            <li>
              <strong>Snapshot Storage:</strong> The normalized public text,
              word count, hash, and timestamp are stored as an immutable
              snapshot to enable sequence diffing when the target agreement
              updates.
            </li>
            <li>
              <strong>Public Scope:</strong> All stored documents are public
              legal agreements already accessible on the open web.
            </li>
          </ul>
        </section>

        <section className="space-y-2.5">
          <h2 className="text-base font-semibold text-zinc-100">
            4. Language Model and Text Analysis
          </h2>
          <p>
            When agreement clauses are evaluated, public policy text is
            processed statelessly. Inputs are evaluated solely to classify
            clause categories and identify potential concerns. Text processed
            through our evaluation pipeline is not retained for training
            commercial foundation models.
          </p>
        </section>

        <section className="space-y-2.5">
          <h2 className="text-base font-semibold text-zinc-100">
            5. Security and Telemetry Protection
          </h2>
          <p>We implement strict operational security controls:</p>
          <ul className="list-disc pl-5 space-y-2 text-zinc-400">
            <li>
              <strong>Telemetry Redaction:</strong> Operational error monitoring
              is configured with automated filters that strip sensitive headers
              (including Authorization and Cookie headers) before any report is
              transmitted.
            </li>
            <li>
              <strong>Outbound SSRF Protection:</strong> Document retrieval
              enforces DNS verification at each redirect hop, blocking loopback
              addresses (
              <code className="text-zinc-300 font-mono text-xs">127.0.0.1</code>
              ), private subnets, and cloud provider metadata addresses (
              <code className="text-zinc-300 font-mono text-xs">
                169.254.169.254
              </code>
              ).
            </li>
            <li>
              <strong>Request Boundaries:</strong> Inbound requests enforce
              strict size limits (10 MB) to prevent buffer exhaustion.
            </li>
          </ul>
        </section>

        <section className="space-y-2.5">
          <h2 className="text-base font-semibold text-zinc-100">
            6. Open Source Transparency and Self-Hosting
          </h2>
          <p>
            EasyFinePrint is licensed under the{" "}
            <strong>Apache License 2.0</strong>. The full source code is
            publicly accessible and auditable on GitHub, allowing anyone to
            verify our data processing practices or run an independent instance
            locally with complete data sovereignty.
          </p>
        </section>

        <section className="space-y-2.5">
          <h2 className="text-base font-semibold text-zinc-100">
            7. Data Retention and Removal Requests
          </h2>
          <p>
            Public agreement snapshots are retained to maintain historical
            change records. If you are an authorized representative of an
            organization and wish to request the removal of an indexed public
            agreement from our demonstration instances, you may submit a request
            through our repository issue tracker.
          </p>
        </section>

        <section className="space-y-2.5">
          <h2 className="text-base font-semibold text-zinc-100">
            8. Changes to This Privacy Policy
          </h2>
          <p>
            Any revisions to this Privacy Policy will be published directly to
            our source repository with timestamped version history. Your
            continued use of the Platform after changes are posted represents
            your acknowledgment of the updated policy.
          </p>
        </section>

        <section className="space-y-2.5">
          <h2 className="text-base font-semibold text-zinc-100">
            9. Contact Information
          </h2>
          <p>
            For inquiries regarding this Privacy Policy, please open an issue on
            our GitHub repository at{" "}
            <a
              href="https://github.com/diptodeepb/EasyFinePrint/issues"
              target="_blank"
              rel="noreferrer"
              className="text-zinc-200 underline underline-offset-4 decoration-zinc-600 hover:decoration-zinc-300"
            >
              github.com/diptodeepb/EasyFinePrint/issues
            </a>
            .
          </p>
        </section>
      </article>

      {/* Footer Navigation */}
      <div className="flex items-center justify-between pt-4 border-t border-zinc-850 text-xs font-mono text-zinc-400">
        <Link to="/terms" className="hover:text-zinc-200 transition-colors">
          &larr; View Terms of Use
        </Link>
        <Link to="/" className="hover:text-zinc-200 transition-colors">
          Return to Dashboard &rarr;
        </Link>
      </div>
    </div>
  );
}
