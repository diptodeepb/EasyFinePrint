import React from "react";
import { ShieldCheck, ExternalLink } from "lucide-react";

export default function Footer() {
  const currentYear = new Date().getFullYear();
  const licenseUrl =
    "https://github.com/diptodeepb/EasyFinePrint/blob/main/LICENSE";

  return (
    <footer className="border-t border-zinc-800/80 bg-[#09090b] text-zinc-400 font-mono text-xs pt-8 sm:pt-12 pb-[calc(2rem+env(safe-area-inset-bottom,0px))] mt-auto">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 space-y-8 sm:space-y-10">
        {/* Main Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-8 lg:gap-10">
          {/* Brand & Mission (spans 2 cols on lg) */}
          <div className="lg:col-span-2 space-y-3">
            <div className="flex items-center gap-2.5">
              <img
                src="/logo.svg"
                alt="EasyFinePrint Logo"
                className="w-5 h-5 rounded border border-zinc-700/80 shrink-0"
              />
              <span className="font-semibold text-sm text-zinc-100 tracking-tight">
                EasyFinePrint
              </span>
              <span className="text-[10px] text-zinc-400 bg-zinc-900 border border-zinc-800 px-1.5 py-0.5 rounded">
                v1.0
              </span>
            </div>
            <p className="text-xs text-zinc-400 leading-relaxed max-w-sm">
              Deterministic paragraph diffing and citation-backed clause risk
              analysis for public terms of service and privacy agreements.
              Continuous change monitoring anchored strictly to verbatim source
              records.
            </p>
          </div>

          {/* Links Grid: 2 columns on mobile/tablet, expands via contents on desktop */}
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:contents gap-6 sm:gap-8">
            {/* Architecture */}
            <div className="space-y-2.5 sm:space-y-3">
              <div className="text-[11px] font-semibold uppercase tracking-wider text-zinc-200">
                Architecture
              </div>
              <ul className="space-y-2 text-[11px] text-zinc-400">
                <li className="flex items-center gap-1.5">
                  <span className="w-1 h-1 rounded-full bg-zinc-600 shrink-0"></span>
                  <span>Deterministic Diffing</span>
                </li>
                <li className="flex items-center gap-1.5">
                  <span className="w-1 h-1 rounded-full bg-zinc-600 shrink-0"></span>
                  <span>Verbatim Grounding</span>
                </li>
                <li className="flex items-center gap-1.5">
                  <span className="w-1 h-1 rounded-full bg-zinc-600 shrink-0"></span>
                  <span>SHA-256 Hashes</span>
                </li>
                <li className="flex items-center gap-1.5">
                  <span className="w-1 h-1 rounded-full bg-zinc-600 shrink-0"></span>
                  <span>Single-Pass Eval</span>
                </li>
              </ul>
            </div>

            {/* Resources */}
            <div className="space-y-2.5 sm:space-y-3">
              <div className="text-[11px] font-semibold uppercase tracking-wider text-zinc-200">
                Resources
              </div>
              <ul className="space-y-2 text-[11px]">
                <li>
                  <a
                    href="https://github.com/diptodeepb/EasyFinePrint"
                    target="_blank"
                    rel="noreferrer"
                    className="hover:text-zinc-100 transition-colors inline-flex items-center gap-1 text-zinc-400 group"
                  >
                    <span>Source Code</span>
                    <ExternalLink className="w-2.5 h-2.5 text-zinc-500 group-hover:text-zinc-300 shrink-0" />
                  </a>
                </li>
                <li>
                  <a
                    href="https://github.com/diptodeepb/EasyFinePrint/blob/main/README.md"
                    target="_blank"
                    rel="noreferrer"
                    className="hover:text-zinc-100 transition-colors inline-flex items-center gap-1 text-zinc-400 group"
                  >
                    <span>Documentation</span>
                    <ExternalLink className="w-2.5 h-2.5 text-zinc-500 group-hover:text-zinc-300 shrink-0" />
                  </a>
                </li>
                <li>
                  <a
                    href="https://github.com/diptodeepb/EasyFinePrint/issues"
                    target="_blank"
                    rel="noreferrer"
                    className="hover:text-zinc-100 transition-colors inline-flex items-center gap-1 text-zinc-400 group"
                  >
                    <span>Issue Tracker</span>
                    <ExternalLink className="w-2.5 h-2.5 text-zinc-500 group-hover:text-zinc-300 shrink-0" />
                  </a>
                </li>
                <li>
                  <a
                    href={licenseUrl}
                    target="_blank"
                    rel="noreferrer"
                    className="hover:text-zinc-100 transition-colors inline-flex items-center gap-1 text-zinc-400 group"
                  >
                    <span>Apache 2.0 License</span>
                    <ExternalLink className="w-2.5 h-2.5 text-zinc-500 group-hover:text-zinc-300 shrink-0" />
                  </a>
                </li>
              </ul>
            </div>

            {/* Compliance & Governance */}
            <div className="space-y-2.5 sm:space-y-3 col-span-2 sm:col-span-1">
              <div className="text-[11px] font-semibold uppercase tracking-wider text-zinc-200">
                Compliance
              </div>
              <ul className="space-y-2 text-[11px] text-zinc-400">
                <li className="flex items-center gap-1.5">
                  <span className="w-1 h-1 rounded-full bg-zinc-600 shrink-0"></span>
                  <span>Automated Audit Protocol</span>
                </li>
                <li className="flex items-center gap-1.5">
                  <span className="w-1 h-1 rounded-full bg-zinc-600 shrink-0"></span>
                  <span>Zero-Hallucination Guardrails</span>
                </li>
                <li className="flex items-center gap-1.5">
                  <span className="w-1 h-1 rounded-full bg-zinc-600 shrink-0"></span>
                  <span>Public Domain Disclosures</span>
                </li>
                <li className="flex items-center gap-1.5">
                  <span className="w-1 h-1 rounded-full bg-zinc-600 shrink-0"></span>
                  <span>Consumer Rights Transparency</span>
                </li>
              </ul>
            </div>
          </div>
        </div>

        {/* Legal Disclaimer Box */}
        <div className="p-3.5 sm:p-4 rounded-xl bg-zinc-950/80 border border-zinc-800/80 text-[11px] text-zinc-400 leading-relaxed space-y-1.5">
          <div className="flex items-center gap-2 text-zinc-300 font-semibold uppercase tracking-wider text-[10px]">
            <ShieldCheck className="w-3.5 h-3.5 text-zinc-400 shrink-0" />
            <span>Legal Disclaimer & Transparency Notice</span>
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
        <div className="border-t border-zinc-800/80 pt-5 sm:pt-6 flex flex-col sm:flex-row items-center justify-between gap-3 text-center sm:text-left text-[11px] text-zinc-400">
          <div className="flex flex-wrap items-center justify-center sm:justify-start gap-x-2.5 sm:gap-x-3 gap-y-1">
            <span>
              &copy; {currentYear} EasyFinePrint. All rights reserved.
            </span>
            <span className="text-zinc-700 hidden sm:inline">&middot;</span>
            <a
              href={licenseUrl}
              target="_blank"
              rel="noreferrer"
              className="text-zinc-400 hover:text-zinc-200 transition-colors inline-flex items-center gap-1 underline underline-offset-4 decoration-zinc-700 hover:decoration-zinc-400"
            >
              <span>Apache 2.0 License</span>
              <ExternalLink className="w-2.5 h-2.5 text-zinc-500 shrink-0" />
            </a>
          </div>

          <div className="flex items-center justify-center gap-2.5 sm:gap-3 text-zinc-500 text-[10px] sm:text-[11px]">
            <span>Deterministic Legal Tech</span>
            <span className="text-zinc-700">&middot;</span>
            <span>Verbatim Source Attribution</span>
          </div>
        </div>
      </div>
    </footer>
  );
}
