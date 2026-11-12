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
import termsRaw from "../../../docs/TERMS_OF_USE.md?raw";
import MarkdownDocViewer from "../components/MarkdownDocViewer";

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
    navigator.clipboard.writeText(termsRaw);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 py-8 sm:py-12 space-y-8">
      {/* Navigation Breadcrumb */}
      <nav
        aria-label="Breadcrumb"
        className="flex items-center gap-2 text-xs font-mono text-[#78716c] dark:text-zinc-500"
      >
        <Link to="/" className="hover:text-[#1c1917] dark:hover:text-white transition-colors">
          Dashboard
        </Link>
        <ChevronRight className="w-3.5 h-3.5 text-[#78716c] dark:text-zinc-700" />
        <span className="text-[#1c1917] dark:text-zinc-300">Terms of Use</span>
      </nav>

      {/* Document Header */}
      <header className="space-y-4 border-b border-[#d5cbba] dark:border-zinc-800 pb-6">
        <div className="space-y-1.5">
          <h1 className="text-2xl sm:text-3xl font-semibold tracking-tight text-[#1c1917] dark:text-zinc-100">
            Terms of Use
          </h1>
          <p className="text-xs sm:text-sm text-[#5c5549] dark:text-zinc-400 flex items-center gap-1.5 flex-wrap">
            <span>Effective Date: October 24, 2026</span>
            <span className="text-[#78716c] dark:text-zinc-600">&middot;</span>
            <a
              href="https://github.com/diptodeepb/EasyFinePrint/blob/main/LICENSE"
              target="_blank"
              rel="noopener noreferrer"
              className="text-[#1c1917] dark:text-zinc-300 hover:text-black dark:hover:text-white underline underline-offset-2 transition-colors inline-flex items-center gap-1 group"
            >
              <span>Apache License 2.0</span>
              <ExternalLink className="w-3 h-3 text-[#78716c] dark:text-zinc-500 group-hover:text-black dark:group-hover:text-white transition-colors" />
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
              className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-md bg-[#1c1917] hover:bg-[#292524] active:bg-[#0c0a09] text-[#faf5ec] dark:bg-white dark:hover:bg-zinc-100 dark:active:bg-zinc-200 dark:text-black dark:border-white font-medium border border-[#1c1917] text-xs font-mono transition-colors cursor-pointer active:scale-95 disabled:opacity-50 shadow-xs"
            >
              {analyzing ? (
                <>
                  <Loader2 className="w-3.5 h-3.5 animate-spin text-current" />
                  <span>Analyzing document...</span>
                </>
              ) : (
                <>
                  <Scale className="w-3.5 h-3.5 text-current" />
                  <span>Analyze with EasyFinePrint</span>
                </>
              )}
            </button>

            <button
              type="button"
              onClick={copyTerms}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-md bg-[#faf5ec] hover:bg-[#e2d9c7] active:bg-[#ded6c6] text-[#1c1917] border border-[#d5cbba] hover:border-[#bfb4a0] dark:bg-zinc-900 dark:hover:bg-zinc-800 dark:active:bg-zinc-750 dark:text-zinc-300 dark:hover:text-zinc-100 dark:border-zinc-800 dark:hover:border-zinc-700 text-xs font-mono transition-colors cursor-pointer active:scale-95"
            >
              {copied ? (
                <>
                  <Check className="w-3.5 h-3.5 text-emerald-600 dark:text-emerald-400" />
                  <span>Copied</span>
                </>
              ) : (
                <>
                  <Copy className="w-3.5 h-3.5 text-[#5c5549] dark:text-zinc-400" />
                  <span>Copy text</span>
                </>
              )}
            </button>
          </div>

          <a
            href="https://github.com/diptodeepb/EasyFinePrint/blob/main/docs/TERMS_OF_USE.md"
            target="_blank"
            rel="noreferrer"
            className="inline-flex items-center gap-1 text-xs font-mono text-[#5c5549] hover:text-[#1c1917] dark:text-zinc-400 dark:hover:text-white transition-colors group"
          >
            <span>View markdown source</span>
            <ExternalLink className="w-3 h-3 text-[#78716c] dark:text-zinc-500 group-hover:text-[#1c1917] dark:group-hover:text-white transition-colors" />
          </a>
        </div>

        {error && (
          <div className="text-xs font-mono text-rose-800 dark:text-rose-300 bg-rose-500/10 dark:bg-rose-950/30 border border-rose-500/30 dark:border-rose-900/40 p-2.5 rounded-md">
            {error}
          </div>
        )}
      </header>

      {/* Formal Legal Notice Box */}
      <div className="p-4 rounded-lg bg-[#faf5ec] dark:bg-zinc-950 border border-[#d5cbba] dark:border-zinc-800 text-xs text-[#5c5549] dark:text-zinc-400 leading-relaxed space-y-1.5 font-mono shadow-xs">
        <div className="text-[#1c1917] dark:text-zinc-200 font-semibold uppercase tracking-wider text-[11px]">
          Legal Notice &amp; Informational Disclaimer
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

      {/* Document Body rendered dynamically from docs/TERMS_OF_USE.md */}
      <MarkdownDocViewer markdown={termsRaw} id="terms-content-body" />

      {/* Footer Navigation */}
      <div className="flex items-center justify-between pt-4 border-t border-[#d5cbba] dark:border-zinc-800 text-xs font-mono text-[#5c5549] dark:text-zinc-400">
        <Link to="/privacy" className="hover:text-[#1c1917] dark:hover:text-white transition-colors">
          &larr; View Privacy Policy
        </Link>
        <Link to="/" className="hover:text-[#1c1917] dark:hover:text-white transition-colors">
          Return to Dashboard &rarr;
        </Link>
      </div>
    </div>
  );
}
