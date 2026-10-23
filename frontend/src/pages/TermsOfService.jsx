import React, { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import {
  Scale,
  Copy,
  Check,
  ChevronRight,
  ExternalLink,
  Loader2,
} from "lucide-react";
import { api } from "../lib/api";

export default function TermsOfService() {
  const navigate = useNavigate();
  const [analyzing, setAnalyzing] = useState(false);
  const [copied, setCopied] = useState(false);
  const [error, setError] = useState("");

  const handleRunAnalysis = async () => {
    try {
      setAnalyzing(true);
      setError("");
      const policy = await api.analyzeSelfPolicy("terms");
      navigate(`/policies/${policy.id}`);
    } catch (err) {
      setError(err.message || "Failed to analyze terms.");
      setAnalyzing(false);
    }
  };

  const copyTerms = () => {
    const text = document.getElementById("terms-content-body")?.innerText || "";
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
        <span className="text-zinc-300">Terms of Use</span>
      </nav>

      {/* Document Header */}
      <header className="space-y-4 border-b border-zinc-800 pb-6">
        <div className="space-y-1.5">
          <h1 className="text-2xl sm:text-3xl font-semibold tracking-tight text-zinc-100">
            Terms of Use
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
                  <Scale className="w-3.5 h-3.5 text-zinc-400" />
                  <span>Analyze with EasyFinePrint</span>
                </>
              )}
            </button>

            <button
              type="button"
              onClick={copyTerms}
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
            href="https://github.com/diptodeepb/EasyFinePrint/blob/main/docs/TERMS_OF_SERVICE.md"
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

      {/* Formal Legal Notice Box */}
      <div className="p-4 rounded-lg bg-zinc-950 border border-zinc-800 text-xs text-zinc-400 leading-relaxed space-y-1.5 font-mono">
        <div className="text-zinc-200 font-semibold uppercase tracking-wider text-[11px]">
          Legal Notice & Informational Disclaimer
        </div>
        <p>
          EasyFinePrint provides automated paragraph diffing, cryptographic hash
          verification, and natural language heuristics for informational and
          developer transparency purposes only. EasyFinePrint is not a law firm,
          does not provide formal legal counsel or statutory certifications, and
          does not establish an attorney-client relationship. Users should
          consult licensed legal counsel for binding contractual matters.
        </p>
      </div>

      {/* Document Body */}
      <article
        id="terms-content-body"
        className="rounded-lg border border-zinc-300 bg-zinc-950/40 p-6 sm:p-8 space-y-8 text-sm text-zinc-300 leading-relaxed font-sans"
      >
        <section className="space-y-2.5">
          <h2 className="text-base font-semibold text-zinc-100">
            1. Acceptance of Terms
          </h2>
          <p>
            These Terms of Use (&ldquo;Terms&rdquo;) govern your access to and
            use of EasyFinePrint (&ldquo;the Service&rdquo;, &ldquo;we&rdquo;,
            &ldquo;us&rdquo;, or &ldquo;our&rdquo;), an open-source agreement
            change monitor and document comparison tool. By accessing, browsing,
            self-hosting, or interacting with our web application or API
            endpoints, you agree to be bound by these Terms. If you do not agree
            to all terms and conditions set forth herein, you must discontinue
            use of the Service immediately.
          </p>
        </section>

        <section className="space-y-2.5">
          <h2 className="text-base font-semibold text-zinc-100">
            2. Scope and Nature of Service
          </h2>
          <p>
            EasyFinePrint provides automated paragraph comparison, cryptographic
            hashing, and textual heuristics to assist developers, researchers,
            and consumers in monitoring revisions across public legal
            agreements. All outputs, including change summaries and clause
            classifications, are computed automatically.
          </p>
          <p>
            The outputs generated by the Service do not constitute formal legal
            opinions on the enforceability, fairness, or validity of any
            contract. You remain responsible for reviewing original legal source
            documents and seeking appropriate legal representation.
          </p>
        </section>

        <section className="space-y-2.5">
          <h2 className="text-base font-semibold text-zinc-100">
            3. Permitted and Prohibited Uses
          </h2>
          <p>
            You agree to use EasyFinePrint only for lawful purposes. When using
            the Service, you agree not to:
          </p>
          <ul className="list-disc pl-5 space-y-2 text-zinc-400">
            <li>
              Submit URLs pointing to private internal networks, intranet
              services, loopback interfaces (
              <code className="text-zinc-300 font-mono text-xs">localhost</code>
              ,{" "}
              <code className="text-zinc-300 font-mono text-xs">127.0.0.1</code>
              ), or cloud provider metadata endpoints (
              <code className="text-zinc-300 font-mono text-xs">
                169.254.169.254
              </code>
              ).
            </li>
            <li>
              Attempt to bypass automated rate limits, payload boundaries (10 MB
              request limit), or security controls.
            </li>
            <li>
              Use the Service to execute denial-of-service attacks, automated
              scrapers against unauthorized targets, or port scans.
            </li>
            <li>
              Submit URLs hosting unlawful, harassing, defamatory, or infringing
              content.
            </li>
          </ul>
        </section>

        <section className="space-y-2.5">
          <h2 className="text-base font-semibold text-zinc-100">
            4. Verification and Source Attribution
          </h2>
          <p>
            EasyFinePrint is engineered around the principle that facts and
            interpretations must remain decoupled:
          </p>
          <ul className="list-disc pl-5 space-y-1.5 text-zinc-400">
            <li>
              Text differences are computed using deterministic Myers sequence
              comparison algorithms.
            </li>
            <li>
              Document snapshots are uniquely identified by SHA-256
              cryptographic hashes.
            </li>
            <li>
              Citations identified during clause reviews are anchored to
              verbatim excerpts of public text.
            </li>
            <li>
              Users acknowledge that automated software may occasionally produce
              incomplete interpretations.
            </li>
          </ul>
        </section>

        <section className="space-y-2.5">
          <h2 className="text-base font-semibold text-zinc-100">
            5. Intellectual Property and Open Source License
          </h2>
          <p>
            The EasyFinePrint codebase is released under the{" "}
            <strong>Apache License, Version 2.0</strong>. You may inspect,
            modify, and distribute the software in compliance with the license
            terms.
          </p>
          <p>
            Third-party names, service trademarks, logos, and agreements
            referenced in the application belong to their respective owners.
            Reference to them does not imply affiliation, sponsorship, or
            endorsement. EasyFinePrint claims no copyright over third-party
            legal text.
          </p>
        </section>

        <section className="space-y-2.5">
          <h2 className="text-base font-semibold text-zinc-100">
            6. Disclaimers and Limitation of Liability
          </h2>
          <p className="text-xs font-mono text-zinc-400 uppercase tracking-wide">
            THE SERVICE IS PROVIDED ON AN &ldquo;AS IS&rdquo; AND &ldquo;AS
            AVAILABLE&rdquo; BASIS, WITHOUT WARRANTIES OF ANY KIND, EXPRESS OR
            IMPLIED. TO THE MAXIMUM EXTENT PERMITTED BY LAW, IN NO EVENT SHALL
            EASYFINEPRINT, ITS MAINTAINERS, OR CONTRIBUTORS BE LIABLE FOR ANY
            DIRECT, INDIRECT, INCIDENTAL, CONSEQUENTIAL, OR SPECIAL DAMAGES
            RESULTING FROM THE USE OF OR INABILITY TO USE THE SERVICE.
          </p>
        </section>

        <section className="space-y-2.5">
          <h2 className="text-base font-semibold text-zinc-100">
            7. Revisions to These Terms
          </h2>
          <p>
            We may revise these Terms of Use from time to time. Revisions will
            be committed directly to our public repository with timestamped
            version history. Your continued use of the Service following
            published updates constitutes your acceptance of the modified Terms.
          </p>
        </section>

        <section className="space-y-2.5">
          <h2 className="text-base font-semibold text-zinc-100">
            8. Contact Information
          </h2>
          <p>
            For questions or feedback regarding these Terms of Use, please
            submit an issue through our public repository at{" "}
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
        <Link to="/privacy" className="hover:text-zinc-200 transition-colors">
          &larr; View Privacy Policy
        </Link>
        <Link to="/" className="hover:text-zinc-200 transition-colors">
          Return to Dashboard &rarr;
        </Link>
      </div>
    </div>
  );
}
