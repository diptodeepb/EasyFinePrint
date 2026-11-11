import React from "react";
import { Link } from "react-router-dom";
import { ShieldCheck, ExternalLink } from "lucide-react";

export default function Footer() {
  const currentYear = new Date().getFullYear();
  const licenseUrl =
    "https://github.com/diptodeepb/EasyFinePrint/blob/main/LICENSE";

  return (
    <footer className="relative bg-[#e5ddcf] dark:bg-[#09090b] text-[#5c5549] dark:text-zinc-400 font-mono text-xs pt-8 sm:pt-12 pb-[calc(2rem+env(safe-area-inset-bottom,0px))] mt-auto border-t border-[#d5cbba] dark:border-zinc-800/80 transition-colors">
      {/* Architectural Top Divider Line */}
      <div
        className="absolute inset-x-0 top-0 h-[1px] pointer-events-none select-none overflow-hidden"
        aria-hidden="true"
      >
        {/* Subtle base gradient line fading to screen edges */}
        <div className="w-full h-full bg-gradient-to-r from-transparent via-[#d5cbba] dark:via-zinc-800/80 to-transparent" />
        {/* Luminous center shimmer */}
        <div className="absolute left-1/2 -translate-x-1/2 top-0 w-3/4 max-w-4xl h-full bg-gradient-to-r from-transparent via-[#bfb4a0]/50 dark:via-zinc-600/50 to-transparent" />
        {/* Delicate centered highlight accent */}
        <div className="absolute left-1/2 -translate-x-1/2 top-0 w-1/3 max-w-lg h-full bg-gradient-to-r from-transparent via-white/40 dark:via-white/25 to-transparent blur-[0.5px]" />
      </div>

      <div className="max-w-6xl mx-auto px-4 sm:px-6 space-y-8 sm:space-y-10">
        {/* Main Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-8 lg:gap-10">
          {/* Brand & Mission (spans 2 cols on lg) */}
          <div className="lg:col-span-2 space-y-3">
            <div className="flex items-center gap-2.5">
              <img
                src="/logo.svg"
                alt="EasyFinePrint Logo"
                className="w-5 h-5 rounded border border-[#d5cbba] dark:border-zinc-700/80 shrink-0"
              />
              <span className="font-semibold text-sm text-[#1c1917] dark:text-zinc-100 tracking-tight">
                EasyFinePrint
              </span>
            </div>
            <p className="text-xs text-[#5c5549] dark:text-zinc-400 leading-relaxed max-w-sm">
              Automated clause risk analysis and revision tracking for public
              terms of service and privacy agreements, grounded strictly in
              verbatim source records.
            </p>
          </div>

          {/* Links Grid: 1 column left-aligned on mobile (Architecture, then Resources, then Compliance), 3 columns on tablet/desktop */}
          <div className="grid grid-cols-1 sm:grid-cols-3 lg:contents gap-6 sm:gap-8">
            {/* Architecture */}
            <div className="space-y-2.5 sm:space-y-3 text-left">
              <h4 className="text-[#1c1917] dark:text-zinc-200 font-semibold text-xs tracking-wider uppercase">
                Architecture
              </h4>
              <ul className="space-y-2 text-[11px] text-[#5c5549] dark:text-zinc-400">
                <li>
                  <Link
                    to="/features"
                    className="hover:text-[#1c1917] dark:hover:text-zinc-200 transition-colors"
                  >
                    4-Tier Hybrid Ingestion
                  </Link>
                </li>
                <li>
                  <Link
                    to="/features"
                    className="hover:text-[#1c1917] dark:hover:text-zinc-200 transition-colors"
                  >
                    Verbatim Quote Grounding
                  </Link>
                </li>
                <li>
                  <Link
                    to="/features"
                    className="hover:text-[#1c1917] dark:hover:text-zinc-200 transition-colors"
                  >
                    Myers Diff Sequence Engine
                  </Link>
                </li>
                <li>
                  <Link
                    to="/features"
                    className="hover:text-[#1c1917] dark:hover:text-zinc-200 transition-colors"
                  >
                    SSRF &amp; Anti-Spam Bounds
                  </Link>
                </li>
              </ul>
            </div>

            {/* Resources */}
            <div className="space-y-2.5 sm:space-y-3 text-left">
              <h4 className="text-[#1c1917] dark:text-zinc-200 font-semibold text-xs tracking-wider uppercase">
                Resources
              </h4>
              <ul className="space-y-2 text-[11px] text-[#5c5549] dark:text-zinc-400">
                <li>
                  <a
                    href="https://github.com/diptodeepb/EasyFinePrint"
                    target="_blank"
                    rel="noreferrer"
                    className="hover:text-[#1c1917] dark:hover:text-zinc-200 transition-colors inline-flex items-center gap-1"
                  >
                    <span>GitHub Repository</span>
                    <ExternalLink className="w-2.5 h-2.5 text-[#78716c] dark:text-zinc-500 shrink-0" />
                  </a>
                </li>
                <li>
                  <a
                    href="https://github.com/diptodeepb/EasyFinePrint/tree/main/docs"
                    target="_blank"
                    rel="noreferrer"
                    className="hover:text-[#1c1917] dark:hover:text-zinc-200 transition-colors inline-flex items-center gap-1"
                  >
                    <span>Documentation &amp; Threat Model</span>
                    <ExternalLink className="w-2.5 h-2.5 text-[#78716c] dark:text-zinc-500 shrink-0" />
                  </a>
                </li>
                <li>
                  <a
                    href="https://github.com/diptodeepb/EasyFinePrint/actions"
                    target="_blank"
                    rel="noreferrer"
                    className="hover:text-[#1c1917] dark:hover:text-zinc-200 transition-colors inline-flex items-center gap-1"
                  >
                    <span>Continuous Integration CI</span>
                    <ExternalLink className="w-2.5 h-2.5 text-[#78716c] dark:text-zinc-500 shrink-0" />
                  </a>
                </li>
                <li>
                  <a
                    href="https://github.com/diptodeepb/EasyFinePrint/issues"
                    target="_blank"
                    rel="noreferrer"
                    className="hover:text-[#1c1917] dark:hover:text-zinc-200 transition-colors inline-flex items-center gap-1"
                  >
                    <span>Issue Tracker</span>
                    <ExternalLink className="w-2.5 h-2.5 text-[#78716c] dark:text-zinc-500 shrink-0" />
                  </a>
                </li>
              </ul>
            </div>

            {/* Compliance & Trust */}
            <div className="space-y-2.5 sm:space-y-3 text-left">
              <h4 className="text-[#1c1917] dark:text-zinc-200 font-semibold text-xs tracking-wider uppercase">
                Trust &amp; Legal
              </h4>
              <ul className="space-y-2 text-[11px] text-[#5c5549] dark:text-zinc-400">
                <li>
                  <Link
                    to="/terms"
                    className="hover:text-[#1c1917] dark:hover:text-zinc-200 transition-colors"
                  >
                    Terms of Use
                  </Link>
                </li>
                <li>
                  <Link
                    to="/privacy"
                    className="hover:text-[#1c1917] dark:hover:text-zinc-200 transition-colors"
                  >
                    Privacy Policy
                  </Link>
                </li>
                <li>
                  <a
                    href={licenseUrl}
                    target="_blank"
                    rel="noreferrer"
                    className="hover:text-[#1c1917] dark:hover:text-zinc-200 transition-colors inline-flex items-center gap-1"
                  >
                    <span>Apache 2.0 License</span>
                  </a>
                </li>
                <li className="flex items-start gap-1.5 leading-snug">
                  <span className="w-1 h-1 rounded-full bg-[#78716c] dark:bg-zinc-600 shrink-0 mt-1.5"></span>
                  <span>No Personal Data Stored</span>
                </li>
                <li className="flex items-start gap-1.5 leading-snug">
                  <span className="w-1 h-1 rounded-full bg-[#78716c] dark:bg-zinc-600 shrink-0 mt-1.5"></span>
                  <span>No Legal Advice</span>
                </li>
              </ul>
            </div>
          </div>
        </div>

        {/* Legal Disclaimer Box */}
        <div className="p-3.5 sm:p-4 rounded-xl bg-[#f5eedf]/90 dark:bg-zinc-950/80 border border-[#d5cbba] dark:border-zinc-800/80 text-[11px] text-[#5c5549] dark:text-zinc-400 leading-relaxed space-y-1.5">
          <div className="flex items-center gap-2 text-[#1c1917] dark:text-zinc-300 font-semibold uppercase tracking-wider text-[10px]">
            <ShieldCheck className="w-3.5 h-3.5 text-[#5c5549] dark:text-zinc-400 shrink-0" />
            <span>Legal Disclaimer &amp; Transparency Notice</span>
          </div>
          <p>
            EasyFinePrint is an automated legal agreement monitoring tool and
            does not constitute formal legal counsel, statutory certification,
            or attorney representation. Risk scores, clause severity
            classifications, and baseline assessments are computed via
            deterministic sequence diffing and semantic evaluation grounded
            strictly in verbatim public source text. Users should consult
            licensed legal counsel for binding contractual matters.
          </p>
        </div>

        {/* Bottom Bar: Copyright & Rights */}
        <div className="relative pt-5 sm:pt-6 flex flex-col sm:flex-row items-center justify-between gap-3 text-center sm:text-left text-[11px] text-[#5c5549] dark:text-zinc-400">
          {/* Subtle gradient divider line */}
          <div
            className="absolute inset-x-0 top-0 h-[1px] pointer-events-none select-none overflow-hidden"
            aria-hidden="true"
          >
            <div className="w-full h-full bg-gradient-to-r from-transparent via-[#d5cbba] dark:via-zinc-800/80 to-transparent" />
            <div className="absolute left-1/2 -translate-x-1/2 top-0 w-1/2 h-full bg-gradient-to-r from-transparent via-[#bfb4a0]/40 dark:via-zinc-700/40 to-transparent" />
          </div>

          <div>
            &copy; {currentYear} EasyFinePrint. All rights reserved.
          </div>

          <div className="flex flex-wrap items-center justify-center sm:justify-end gap-x-2.5 sm:gap-x-3 gap-y-1">
            <Link
              to="/features"
              className="text-[#5c5549] dark:text-zinc-400 hover:text-[#1c1917] dark:hover:text-zinc-200 transition-colors underline underline-offset-4 decoration-[#bfb4a0] dark:decoration-zinc-700 hover:decoration-[#5c5549] dark:hover:decoration-zinc-400"
            >
              Features
            </Link>
            <span className="text-[#bfb4a0] dark:text-zinc-700 hidden sm:inline">&middot;</span>
            <Link
              to="/terms"
              className="text-[#5c5549] dark:text-zinc-400 hover:text-[#1c1917] dark:hover:text-zinc-200 transition-colors underline underline-offset-4 decoration-[#bfb4a0] dark:decoration-zinc-700 hover:decoration-[#5c5549] dark:hover:decoration-zinc-400"
            >
              Terms of Use
            </Link>
            <span className="text-[#bfb4a0] dark:text-zinc-700 hidden sm:inline">&middot;</span>
            <Link
              to="/privacy"
              className="text-[#5c5549] dark:text-zinc-400 hover:text-[#1c1917] dark:hover:text-zinc-200 transition-colors underline underline-offset-4 decoration-[#bfb4a0] dark:decoration-zinc-700 hover:decoration-[#5c5549] dark:hover:decoration-zinc-400"
            >
              Privacy Policy
            </Link>
            <span className="text-[#bfb4a0] dark:text-zinc-700 hidden sm:inline">&middot;</span>
            <a
              href={licenseUrl}
              target="_blank"
              rel="noreferrer"
              className="text-[#5c5549] dark:text-zinc-400 hover:text-[#1c1917] dark:hover:text-zinc-200 transition-colors inline-flex items-center gap-1 underline underline-offset-4 decoration-[#bfb4a0] dark:decoration-zinc-700 hover:decoration-[#5c5549] dark:hover:decoration-zinc-400"
            >
              <span>Apache 2.0 License</span>
              <ExternalLink className="w-2.5 h-2.5 text-[#78716c] dark:text-zinc-500 shrink-0" />
            </a>
          </div>
        </div>
      </div>
    </footer>
  );
}
