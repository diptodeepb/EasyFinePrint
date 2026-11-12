import React from "react";
import { Link } from "react-router-dom";
import { ExternalLink } from "lucide-react";

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
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8 lg:gap-10 lg:translate-x-8 xl:translate-x-12">
          {/* Brand & Mission (spans 2 cols on lg) */}
          <div className="lg:col-span-2 space-y-3 sm:space-y-4">
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
            <p className="text-xs text-[#5c5549] dark:text-zinc-400 leading-relaxed max-w-sm sm:max-w-[300px] pt-0.5 sm:pt-1.5">
              Automated clause risk analysis and revision tracking for public
              terms of service and privacy agreements, grounded strictly in
              verbatim source records.
            </p>
          </div>

          {/* Links Grid: 1 column left-aligned on mobile (Resources, then Trust & Legal), 2 columns on tablet, flat on desktop */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:contents gap-6 sm:gap-8">
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
                    className="hover:text-[#1c1917] dark:hover:text-white transition-colors inline-flex items-center gap-1 group"
                  >
                    <span>GitHub Repository</span>
                    <ExternalLink className="w-2.5 h-2.5 text-[#78716c] dark:text-zinc-500 group-hover:text-[#1c1917] dark:group-hover:text-white transition-colors shrink-0" />
                  </a>
                </li>
                <li>
                  <a
                    href="https://github.com/diptodeepb/EasyFinePrint/issues"
                    target="_blank"
                    rel="noreferrer"
                    className="hover:text-[#1c1917] dark:hover:text-white transition-colors inline-flex items-center gap-1 group"
                  >
                    <span>Issue Tracker</span>
                    <ExternalLink className="w-2.5 h-2.5 text-[#78716c] dark:text-zinc-500 group-hover:text-[#1c1917] dark:group-hover:text-white transition-colors shrink-0" />
                  </a>
                </li>
                <li>
                  <a
                    href="https://github.com/diptodeepb/EasyFinePrint/blob/main/docs/architecture.md"
                    target="_blank"
                    rel="noreferrer"
                    className="hover:text-[#1c1917] dark:hover:text-white transition-colors inline-flex items-center gap-1 group"
                  >
                    <span>architecture.md</span>
                    <ExternalLink className="w-2.5 h-2.5 text-[#78716c] dark:text-zinc-500 group-hover:text-[#1c1917] dark:group-hover:text-white transition-colors shrink-0" />
                  </a>
                </li>
                <li>
                  <a
                    href="https://github.com/diptodeepb/EasyFinePrint/blob/main/docs/evaluation.md"
                    target="_blank"
                    rel="noreferrer"
                    className="hover:text-[#1c1917] dark:hover:text-white transition-colors inline-flex items-center gap-1 group"
                  >
                    <span>evaluation.md</span>
                    <ExternalLink className="w-2.5 h-2.5 text-[#78716c] dark:text-zinc-500 group-hover:text-[#1c1917] dark:group-hover:text-white transition-colors shrink-0" />
                  </a>
                </li>
                <li>
                  <a
                    href="https://github.com/diptodeepb/EasyFinePrint/blob/main/docs/threat-model.md"
                    target="_blank"
                    rel="noreferrer"
                    className="hover:text-[#1c1917] dark:hover:text-white transition-colors inline-flex items-center gap-1 group"
                  >
                    <span>threat-model.md</span>
                    <ExternalLink className="w-2.5 h-2.5 text-[#78716c] dark:text-zinc-500 group-hover:text-[#1c1917] dark:group-hover:text-white transition-colors shrink-0" />
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
                    className="hover:text-[#1c1917] dark:hover:text-white transition-colors"
                  >
                    Terms of Use
                  </Link>
                </li>
                <li>
                  <Link
                    to="/privacy"
                    className="hover:text-[#1c1917] dark:hover:text-white transition-colors"
                  >
                    Privacy Policy
                  </Link>
                </li>
                <li>
                  <a
                    href={licenseUrl}
                    target="_blank"
                    rel="noreferrer"
                    className="hover:text-[#1c1917] dark:hover:text-white transition-colors inline-flex items-center gap-1 group"
                  >
                    <span>Apache 2.0 License</span>
                    <ExternalLink className="w-2.5 h-2.5 text-[#78716c] dark:text-zinc-500 group-hover:text-[#1c1917] dark:group-hover:text-white transition-colors shrink-0" />
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

        {/* Large Brand Showcase Wordmark */}
        <div className="pt-8 sm:pt-14 md:pt-20 pb-2 sm:pb-4 flex justify-center items-center overflow-hidden select-none">
          <Link
            to="/"
            onClick={() => window.scrollTo({ top: 0, behavior: "smooth" })}
            className="font-sans text-[clamp(2.4rem,11.5vw,9.5rem)] font-bold tracking-tighter leading-none text-[#1c1917] hover:text-[#5c5549] dark:text-zinc-500/80 dark:hover:text-zinc-200 transition-colors duration-300 text-center block w-full whitespace-nowrap cursor-pointer active:scale-[0.99]"
            title="EasyFinePrint - Back to Top"
            aria-label="EasyFinePrint Home"
          >
            EasyFinePrint.
          </Link>
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

          <div>&copy; {currentYear} EasyFinePrint. All rights reserved.</div>

          <div className="flex flex-wrap items-center justify-center sm:justify-end gap-x-2.5 sm:gap-x-3 gap-y-1">
            <Link
              to="/features"
              className="text-[#5c5549] dark:text-zinc-400 hover:text-[#1c1917] dark:hover:text-white transition-colors underline underline-offset-4 decoration-[#bfb4a0] dark:decoration-zinc-700 hover:decoration-[#1c1917] dark:hover:decoration-white"
            >
              Features
            </Link>
            <span className="text-[#bfb4a0] dark:text-zinc-700 hidden sm:inline">
              &middot;
            </span>
            <Link
              to="/terms"
              className="text-[#5c5549] dark:text-zinc-400 hover:text-[#1c1917] dark:hover:text-white transition-colors underline underline-offset-4 decoration-[#bfb4a0] dark:decoration-zinc-700 hover:decoration-[#1c1917] dark:hover:decoration-white"
            >
              Terms of Use
            </Link>
            <span className="text-[#bfb4a0] dark:text-zinc-700 hidden sm:inline">
              &middot;
            </span>
            <Link
              to="/privacy"
              className="text-[#5c5549] dark:text-zinc-400 hover:text-[#1c1917] dark:hover:text-white transition-colors underline underline-offset-4 decoration-[#bfb4a0] dark:decoration-zinc-700 hover:decoration-[#1c1917] dark:hover:decoration-white"
            >
              Privacy Policy
            </Link>
            <span className="text-[#bfb4a0] dark:text-zinc-700 hidden sm:inline">
              &middot;
            </span>
            <a
              href={licenseUrl}
              target="_blank"
              rel="noreferrer"
              className="text-[#5c5549] dark:text-zinc-400 hover:text-[#1c1917] dark:hover:text-white transition-colors inline-flex items-center gap-1 underline underline-offset-4 decoration-[#bfb4a0] dark:decoration-zinc-700 hover:decoration-[#1c1917] dark:hover:decoration-white group"
            >
              <span>Apache 2.0 License</span>
              <ExternalLink className="w-2.5 h-2.5 text-[#78716c] dark:text-zinc-500 group-hover:text-[#1c1917] dark:group-hover:text-white transition-colors shrink-0" />
            </a>
          </div>
        </div>
      </div>
    </footer>
  );
}
