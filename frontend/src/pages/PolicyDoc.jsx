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
import privacyRaw from "../../../docs/PRIVACY_POLICY.md?raw";
import MarkdownDocViewer from "../components/MarkdownDocViewer";

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
    navigator.clipboard.writeText(privacyRaw);
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
      <div className="p-4 rounded-lg bg-zinc-950 border border-zinc-300 text-xs text-zinc-400 leading-relaxed space-y-1.5 font-mono shadow-sm">
        <div className="text-zinc-200 font-semibold uppercase tracking-wider text-[11px]">
          Privacy Overview & Telemetry Redaction
        </div>
        <p>
          EasyFinePrint operates a privacy-first service with strict telemetry
          redaction. We do not collect personal data, we do not operate tracking
          cookies or advertising pixels, and we do not sell or monetize
          information. URLs submitted for monitoring are public agreements
          processed purely to compute cryptographic hashes and track text
          changes across revisions.
        </p>
      </div>

      {/* Document Body rendered dynamically from docs/PRIVACY_POLICY.md */}
      <MarkdownDocViewer markdown={privacyRaw} id="privacy-content-body" />

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
