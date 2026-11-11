import React from "react";
import { Link } from "react-router-dom";
import {
  Scale,
  FileCheck,
  GitCompare,
  Search,
  ShieldCheck,
  Zap,
  ChevronRight,
  ArrowRight,
  CheckCircle2,
  Cpu,
  Layers,
  Globe,
  Archive,
  FileText,
  Database,
} from "lucide-react";

export default function Features() {
  return (
    <div className="max-w-5xl mx-auto px-3.5 sm:px-6 py-6 sm:py-12 space-y-8 sm:space-y-10 font-sans">
      {/* Navigation Breadcrumb */}
      <nav
        aria-label="Breadcrumb"
        className="flex items-center gap-2 text-xs font-mono text-[#78716c] dark:text-zinc-500"
      >
        <Link to="/" className="hover:text-[#1c1917] dark:hover:text-zinc-300 transition-colors">
          Dashboard
        </Link>
        <ChevronRight className="w-3.5 h-3.5 text-[#bfb4a0] dark:text-zinc-700" />
        <span className="text-[#1c1917] dark:text-zinc-300">Features</span>
      </nav>

      {/* Header */}
      <header className="space-y-3 border-b border-[#d5cbba] dark:border-zinc-800/80 pb-6">
        <div className="inline-flex items-center gap-2 px-2.5 py-1 rounded-md bg-[#f5eedf] dark:bg-zinc-900 border border-[#d5cbba] dark:border-zinc-800 text-[10px] sm:text-[11px] font-mono text-[#5c5549] dark:text-zinc-400 shadow-2xs">
          <Layers className="w-3.5 h-3.5 text-[#5c5549] dark:text-zinc-400 shrink-0" />
          <span>Platform Architecture &amp; Capabilities</span>
        </div>
        <h1 className="text-xl sm:text-3xl md:text-4xl font-semibold tracking-tight text-[#1c1917] dark:text-zinc-100">
          Auditing Capabilities &amp; System Guarantees
        </h1>
        <p className="text-xs sm:text-sm md:text-base text-[#5c5549] dark:text-zinc-400 max-w-3xl leading-relaxed">
          EasyFinePrint is an automated legal agreement monitor designed to detect
          hidden consumer liabilities, track word-for-word policy revisions, and anchor
          every risk assessment in strict verbatim source quotations.
        </p>
      </header>

      {/* Primary Highlighted Features Grid */}
      <section className="space-y-3.5 sm:space-y-4">
        <div>
          <h2 className="text-sm sm:text-base md:text-lg font-semibold text-[#1c1917] dark:text-zinc-200 tracking-tight flex items-center gap-2">
            <span>Core Auditing Pillars</span>
          </h2>
          <p className="text-xs text-[#5c5549] dark:text-zinc-500">
            Three foundational verification guarantees governing every policy audit
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-3.5 sm:gap-4">
          {/* Feature 1: Clause Risk Auditing */}
          <div className="rounded-xl p-4 sm:p-5 bg-[#f5eedf] dark:bg-[#121215] border border-[#d5cbba] dark:border-zinc-800 flex flex-col justify-between space-y-4 shadow-xs hover:border-[#bfb4a0] dark:hover:border-zinc-700 transition-colors">
            <div className="space-y-3">
              <div className="flex items-start gap-3">
                <div className="w-8 h-8 sm:w-9 sm:h-9 rounded-lg bg-[#e5ddcf] dark:bg-zinc-900 border border-[#d5cbba] dark:border-zinc-800 flex items-center justify-center text-[#1c1917] dark:text-zinc-200 shrink-0 shadow-2xs">
                  <Scale className="w-4 h-4 text-[#5c5549] dark:text-zinc-300" />
                </div>
                <div className="min-w-0 flex-1">
                  <h3 className="text-sm font-semibold text-[#1c1917] dark:text-zinc-100">
                    Clause Risk Auditing
                  </h3>
                  <p className="text-[11px] sm:text-xs text-[#78716c] dark:text-zinc-500 font-mono mt-0.5">
                    Calibrated severity scoring
                  </p>
                </div>
              </div>
              <p className="text-xs text-[#5c5549] dark:text-zinc-400 leading-relaxed">
                Systematically scans terms and privacy documents for binding arbitration,
                class-action waivers, unilateral modification rights, data telemetry expansions,
                and sweeping liability disclaimers with calibrated severity tiers.
              </p>
            </div>

            <ul className="space-y-2 sm:space-y-1.5 pt-3 border-t border-[#d5cbba]/60 dark:border-zinc-800/60 text-[11px] font-mono text-[#5c5549] dark:text-zinc-400">
              <li className="flex items-center gap-2 leading-tight">
                <CheckCircle2 className="w-3.5 h-3.5 text-[#78716c] dark:text-zinc-500 shrink-0" />
                <span>Arbitration &amp; Jury Waivers</span>
              </li>
              <li className="flex items-center gap-2 leading-tight">
                <CheckCircle2 className="w-3.5 h-3.5 text-[#78716c] dark:text-zinc-500 shrink-0" />
                <span>Unilateral Policy Changes</span>
              </li>
              <li className="flex items-center gap-2 leading-tight">
                <CheckCircle2 className="w-3.5 h-3.5 text-[#78716c] dark:text-zinc-500 shrink-0" />
                <span>Third-Party Data Telemetry</span>
              </li>
            </ul>
          </div>

          {/* Feature 2: Verbatim Source Citations */}
          <div className="rounded-xl p-4 sm:p-5 bg-[#f5eedf] dark:bg-[#121215] border border-[#d5cbba] dark:border-zinc-800 flex flex-col justify-between space-y-4 shadow-xs hover:border-[#bfb4a0] dark:hover:border-zinc-700 transition-colors">
            <div className="space-y-3">
              <div className="flex items-start gap-3">
                <div className="w-8 h-8 sm:w-9 sm:h-9 rounded-lg bg-[#e5ddcf] dark:bg-zinc-900 border border-[#d5cbba] dark:border-zinc-800 flex items-center justify-center text-[#1c1917] dark:text-zinc-200 shrink-0 shadow-2xs">
                  <FileCheck className="w-4 h-4 text-[#5c5549] dark:text-zinc-300" />
                </div>
                <div className="min-w-0 flex-1">
                  <h3 className="text-sm font-semibold text-[#1c1917] dark:text-zinc-100">
                    Verbatim Source Citations
                  </h3>
                  <p className="text-[11px] sm:text-xs text-[#78716c] dark:text-zinc-500 font-mono mt-0.5">
                    Zero hallucination guarantee
                  </p>
                </div>
              </div>
              <p className="text-xs text-[#5c5549] dark:text-zinc-400 leading-relaxed">
                Every flagged risk is anchored to an exact, unedited quotation verified directly
                against the ingested document. If a quoted phrase does not exist character-for-character
                in the source text, the finding is automatically purged.
              </p>
            </div>

            <ul className="space-y-2 sm:space-y-1.5 pt-3 border-t border-[#d5cbba]/60 dark:border-zinc-800/60 text-[11px] font-mono text-[#5c5549] dark:text-zinc-400">
              <li className="flex items-center gap-2 leading-tight">
                <CheckCircle2 className="w-3.5 h-3.5 text-[#78716c] dark:text-zinc-500 shrink-0" />
                <span>Exact Character Matching</span>
              </li>
              <li className="flex items-center gap-2 leading-tight">
                <CheckCircle2 className="w-3.5 h-3.5 text-[#78716c] dark:text-zinc-500 shrink-0" />
                <span>Interactive Quote Anchoring</span>
              </li>
              <li className="flex items-center gap-2 leading-tight">
                <CheckCircle2 className="w-3.5 h-3.5 text-[#78716c] dark:text-zinc-500 shrink-0" />
                <span>Automated Finding Pruning</span>
              </li>
            </ul>
          </div>

          {/* Feature 3: Revision & Change Tracking */}
          <div className="rounded-xl p-4 sm:p-5 bg-[#f5eedf] dark:bg-[#121215] border border-[#d5cbba] dark:border-zinc-800 flex flex-col justify-between space-y-4 shadow-xs hover:border-[#bfb4a0] dark:hover:border-zinc-700 transition-colors">
            <div className="space-y-3">
              <div className="flex items-start gap-3">
                <div className="w-8 h-8 sm:w-9 sm:h-9 rounded-lg bg-[#e5ddcf] dark:bg-zinc-900 border border-[#d5cbba] dark:border-zinc-800 flex items-center justify-center text-[#1c1917] dark:text-zinc-200 shrink-0 shadow-2xs">
                  <GitCompare className="w-4 h-4 text-[#5c5549] dark:text-zinc-300" />
                </div>
                <div className="min-w-0 flex-1">
                  <h3 className="text-sm font-semibold text-[#1c1917] dark:text-zinc-100">
                    Revision &amp; Change Tracking
                  </h3>
                  <p className="text-[11px] sm:text-xs text-[#78716c] dark:text-zinc-500 font-mono mt-0.5">
                    Deterministic Myers sequence diff
                  </p>
                </div>
              </div>
              <p className="text-xs text-[#5c5549] dark:text-zinc-400 leading-relaxed">
                Stores immutable baseline snapshots over time. Whenever agreements are updated,
                the engine highlights word-for-word insertions and deletions alongside semantic
                explanations of legal implications.
              </p>
            </div>

            <ul className="space-y-2 sm:space-y-1.5 pt-3 border-t border-[#d5cbba]/60 dark:border-zinc-800/60 text-[11px] font-mono text-[#5c5549] dark:text-zinc-400">
              <li className="flex items-center gap-2 leading-tight">
                <CheckCircle2 className="w-3.5 h-3.5 text-[#78716c] dark:text-zinc-500 shrink-0" />
                <span>Word-for-Word Visual Diff</span>
              </li>
              <li className="flex items-center gap-2 leading-tight">
                <CheckCircle2 className="w-3.5 h-3.5 text-[#78716c] dark:text-zinc-500 shrink-0" />
                <span>Immutable Version History</span>
              </li>
              <li className="flex items-center gap-2 leading-tight">
                <CheckCircle2 className="w-3.5 h-3.5 text-[#78716c] dark:text-zinc-500 shrink-0" />
                <span>Automated Semantic Deltas</span>
              </li>
            </ul>
          </div>
        </div>
      </section>

      {/* 4-Tier Ingestion & Fallback Pipeline */}
      <section className="space-y-3.5 sm:space-y-4 pt-2 sm:pt-4">
        <div>
          <h2 className="text-sm sm:text-base md:text-lg font-semibold text-[#1c1917] dark:text-zinc-200 tracking-tight flex items-center gap-2">
            <span>4-Tier Ingestion &amp; Diff Pipeline</span>
          </h2>
          <p className="text-xs text-[#5c5549] dark:text-zinc-500">
            Multi-stage retrieval hierarchy for continuous document ingestion across network barriers
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-3.5 sm:gap-4">
          {/* Tier 1 */}
          <div className="rounded-xl p-4 sm:p-5 bg-[#f5eedf] dark:bg-[#121215] border border-[#d5cbba] dark:border-zinc-800 space-y-3 shadow-xs hover:border-[#bfb4a0] dark:hover:border-zinc-700 transition-colors">
            <div className="flex items-start sm:items-center gap-2.5 sm:gap-3">
              <div className="w-8 h-8 rounded-lg bg-[#e5ddcf] dark:bg-zinc-900 border border-[#d5cbba] dark:border-zinc-800 flex items-center justify-center text-[#1c1917] dark:text-zinc-300 shrink-0 shadow-2xs">
                <Globe className="w-4 h-4 text-emerald-700 dark:text-emerald-400" />
              </div>
              <div className="min-w-0 flex-1">
                <h3 className="text-sm font-semibold text-[#1c1917] dark:text-zinc-100">
                  Tier 1: Live Fetch &amp; SPA Hydration
                </h3>
                <span className="text-[11px] font-mono text-[#78716c] dark:text-zinc-500 block">
                  Direct Outbound HTTP &amp; Client State Extraction
                </span>
              </div>
            </div>
            <p className="text-xs text-[#5c5549] dark:text-zinc-400 leading-relaxed">
              Fetches agreements directly with desktop Chrome profiles and multi-hop SSRF validation.
              Recursively extracts DOM content and client JSON hydration state (Next.js __NEXT_DATA__, Redux, Vue).
            </p>
          </div>

          {/* Tier 2 */}
          <div className="rounded-xl p-4 sm:p-5 bg-[#f5eedf] dark:bg-[#121215] border border-[#d5cbba] dark:border-zinc-800 space-y-3 shadow-xs hover:border-[#bfb4a0] dark:hover:border-zinc-700 transition-colors">
            <div className="flex items-start sm:items-center gap-2.5 sm:gap-3">
              <div className="w-8 h-8 rounded-lg bg-[#e5ddcf] dark:bg-zinc-900 border border-[#d5cbba] dark:border-zinc-800 flex items-center justify-center text-[#1c1917] dark:text-zinc-300 shrink-0 shadow-2xs">
                <Archive className="w-4 h-4 text-sky-700 dark:text-sky-400" />
              </div>
              <div className="min-w-0 flex-1">
                <h3 className="text-sm font-semibold text-[#1c1917] dark:text-zinc-100">
                  Tier 2: Wayback Machine Archive Fallback
                </h3>
                <span className="text-[11px] font-mono text-[#78716c] dark:text-zinc-500 block">
                  Public Archive Availability API Integration
                </span>
              </div>
            </div>
            <p className="text-xs text-[#5c5549] dark:text-zinc-400 leading-relaxed">
              When origin servers return 403, 429, or bot challenges (&lt;100 characters), the engine queries
              the Internet Archive for the latest verified public snapshot, stripping archive navigation toolbars.
            </p>
          </div>

          {/* Tier 3 */}
          <div className="rounded-xl p-4 sm:p-5 bg-[#f5eedf] dark:bg-[#121215] border border-[#d5cbba] dark:border-zinc-800 space-y-3 shadow-xs hover:border-[#bfb4a0] dark:hover:border-zinc-700 transition-colors">
            <div className="flex items-start sm:items-center gap-2.5 sm:gap-3">
              <div className="w-8 h-8 rounded-lg bg-[#e5ddcf] dark:bg-zinc-900 border border-[#d5cbba] dark:border-zinc-800 flex items-center justify-center text-[#1c1917] dark:text-zinc-300 shrink-0 shadow-2xs">
                <FileText className="w-4 h-4 text-amber-700 dark:text-amber-400" />
              </div>
              <div className="min-w-0 flex-1">
                <h3 className="text-sm font-semibold text-[#1c1917] dark:text-zinc-100">
                  Tier 3: User-Provided Document Ingestion
                </h3>
                <span className="text-[11px] font-mono text-[#78716c] dark:text-zinc-500 block">
                  Manual Text Ingestion with Provenance Stamping
                </span>
              </div>
            </div>
            <p className="text-xs text-[#5c5549] dark:text-zinc-400 leading-relaxed">
              Accepts direct text paste for policies behind authentication or corporate intranets. Enforces strict input bounds
              (URL ≤2,048 chars, title ≤200 chars, body ≤500,000 chars), canonical deduplication against system policies, and immutable provenance stamping.
            </p>
          </div>

          {/* Tier 4 */}
          <div className="rounded-xl p-4 sm:p-5 bg-[#f5eedf] dark:bg-[#121215] border border-[#d5cbba] dark:border-zinc-800 space-y-3 shadow-xs hover:border-[#bfb4a0] dark:hover:border-zinc-700 transition-colors">
            <div className="flex items-start sm:items-center gap-2.5 sm:gap-3">
              <div className="w-8 h-8 rounded-lg bg-[#e5ddcf] dark:bg-zinc-900 border border-[#d5cbba] dark:border-zinc-800 flex items-center justify-center text-[#1c1917] dark:text-zinc-300 shrink-0 shadow-2xs">
                <Database className="w-4 h-4 text-purple-700 dark:text-purple-400" />
              </div>
              <div className="min-w-0 flex-1">
                <h3 className="text-sm font-semibold text-[#1c1917] dark:text-zinc-100">
                  Tier 4: Zero-Drift Baseline Database Cache
                </h3>
                <span className="text-[11px] font-mono text-[#78716c] dark:text-zinc-500 block">
                  Deterministic Database Snapshot Fallback
                </span>
              </div>
            </div>
            <p className="text-xs text-[#5c5549] dark:text-zinc-400 leading-relaxed">
              If an external server experiences downtime during a check, the engine serves the verified
              database baseline, preserving historical evaluations without destructive overwrites or false diffs.
            </p>
          </div>
        </div>
      </section>

      {/* Deep Architecture Grid */}
      <section className="space-y-3.5 sm:space-y-4 pt-2 sm:pt-4">
        <div>
          <h2 className="text-sm sm:text-base md:text-lg font-semibold text-[#1c1917] dark:text-zinc-200 tracking-tight flex items-center gap-2">
            <span>Engineering Architecture</span>
          </h2>
          <p className="text-xs text-[#5c5549] dark:text-zinc-500">
            Resilient pipeline infrastructure powering automated policy ingestion
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-3.5 sm:gap-4">
          {/* Card 1: Cloudflare Workers AI */}
          <div className="rounded-xl p-4 sm:p-5 bg-[#f5eedf] dark:bg-[#121215] border border-[#d5cbba] dark:border-zinc-800 space-y-3 shadow-xs hover:border-[#bfb4a0] dark:hover:border-zinc-700 transition-colors">
            <div className="flex items-start sm:items-center gap-2.5 sm:gap-3">
              <div className="w-8 h-8 rounded-lg bg-[#e5ddcf] dark:bg-zinc-900 border border-[#d5cbba] dark:border-zinc-800 flex items-center justify-center text-[#1c1917] dark:text-zinc-300 shrink-0 shadow-2xs">
                <Cpu className="w-4 h-4" />
              </div>
              <div className="min-w-0 flex-1">
                <h3 className="text-sm font-semibold text-[#1c1917] dark:text-zinc-100">
                  Single-Pass Gemma 4 Inference
                </h3>
                <span className="text-[11px] font-mono text-[#78716c] dark:text-zinc-500 block">
                  Edge Cloudflare Workers AI with fallback resilience
                </span>
              </div>
            </div>
            <p className="text-xs text-[#5c5549] dark:text-zinc-400 leading-relaxed">
              Runs single-pass JSON inference against Google Gemma 4 (26B IT) at edge nodes.
              Extracts clause category, severity level, plain-language risk explanations, and exact verbatim quotations
              in under 25 seconds. If unavailable, falls back gracefully to a deterministic local rule engine.
            </p>
          </div>

          {/* Card 2: SSRF & Anti-Spam Security */}
          <div className="rounded-xl p-4 sm:p-5 bg-[#f5eedf] dark:bg-[#121215] border border-[#d5cbba] dark:border-zinc-800 space-y-3 shadow-xs hover:border-[#bfb4a0] dark:hover:border-zinc-700 transition-colors">
            <div className="flex items-start sm:items-center gap-2.5 sm:gap-3">
              <div className="w-8 h-8 rounded-lg bg-[#e5ddcf] dark:bg-zinc-900 border border-[#d5cbba] dark:border-zinc-800 flex items-center justify-center text-[#1c1917] dark:text-zinc-300 shrink-0 shadow-2xs">
                <ShieldCheck className="w-4 h-4" />
              </div>
              <div className="min-w-0 flex-1">
                <h3 className="text-sm font-semibold text-[#1c1917] dark:text-zinc-100">
                  Multi-Hop SSRF &amp; IP Protection
                </h3>
                <span className="text-[11px] font-mono text-[#78716c] dark:text-zinc-500 block">
                  DNS re-resolution &amp; RFC-1918 blocking
                </span>
              </div>
            </div>
            <p className="text-xs text-[#5c5549] dark:text-zinc-400 leading-relaxed">
              Prevents Server-Side Request Forgery by pre-resolving hostnames and rejecting private RFC-1918
              ranges, loopback addresses, AWS/GCP metadata endpoints (169.254.169.254), and credential-stuffed URLs
              before any outbound socket is opened. Follows redirects strictly with hop-by-hop verification.
            </p>
          </div>

          {/* Card 3: Zero-Dependency Company Discovery */}
          <div className="rounded-xl p-4 sm:p-5 bg-[#f5eedf] dark:bg-[#121215] border border-[#d5cbba] dark:border-zinc-800 space-y-3 shadow-xs hover:border-[#bfb4a0] dark:hover:border-zinc-700 transition-colors">
            <div className="flex items-start sm:items-center gap-2.5 sm:gap-3">
              <div className="w-8 h-8 rounded-lg bg-[#e5ddcf] dark:bg-zinc-900 border border-[#d5cbba] dark:border-zinc-800 flex items-center justify-center text-[#1c1917] dark:text-zinc-300 shrink-0 shadow-2xs">
                <Search className="w-4 h-4" />
              </div>
              <div className="min-w-0 flex-1">
                <h3 className="text-sm font-semibold text-[#1c1917] dark:text-zinc-100">
                  Curated Directory Discovery
                </h3>
                <span className="text-[11px] font-mono text-[#78716c] dark:text-zinc-500 block">
                  249+ authoritative services with dynamic web fallback
                </span>
              </div>
            </div>
            <p className="text-xs text-[#5c5549] dark:text-zinc-400 leading-relaxed">
              Provides instant lookup across 249+ popular platforms, streaming services, and developer tools
              with zero API keys or external costs. For unlisted companies, an auto-discovery pipeline crawls
              known policy paths and search engine endpoints with realistic progression timers and modal pagination.
            </p>
          </div>

          {/* Card 4: SPA Hydration & State Scraping */}
          <div className="rounded-xl p-4 sm:p-5 bg-[#f5eedf] dark:bg-[#121215] border border-[#d5cbba] dark:border-zinc-800 space-y-3 shadow-xs hover:border-[#bfb4a0] dark:hover:border-zinc-700 transition-colors">
            <div className="flex items-start sm:items-center gap-2.5 sm:gap-3">
              <div className="w-8 h-8 rounded-lg bg-[#e5ddcf] dark:bg-zinc-900 border border-[#d5cbba] dark:border-zinc-800 flex items-center justify-center text-[#1c1917] dark:text-zinc-300 shrink-0 shadow-2xs">
                <Zap className="w-4 h-4" />
              </div>
              <div className="min-w-0 flex-1">
                <h3 className="text-sm font-semibold text-[#1c1917] dark:text-zinc-100">
                  Client Hydration &amp; Sandboxed VM
                </h3>
                <span className="text-[11px] font-mono text-[#78716c] dark:text-zinc-500 block">
                  Next.js, Redux, Nuxt state extraction
                </span>
              </div>
            </div>
            <p className="text-xs text-[#5c5549] dark:text-zinc-400 leading-relaxed">
              Extracts cleanly across traditional web articles and modern Single-Page Applications
              (React, Next.js, Redux, Vue) by recursively parsing client-side JSON hydration state
              and sandboxed script evaluation.
            </p>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="rounded-xl p-5 sm:p-8 bg-[#f5eedf] dark:bg-zinc-950 border border-[#d5cbba] dark:border-zinc-800 text-center space-y-3.5 sm:space-y-4 shadow-xs">
        <h2 className="text-base sm:text-xl font-semibold text-[#1c1917] dark:text-zinc-100">
          Ready to audit a legal agreement?
        </h2>
        <p className="text-xs sm:text-sm text-[#5c5549] dark:text-zinc-400 max-w-xl mx-auto leading-relaxed">
          Paste any public Terms of Use or Privacy Policy URL on the dashboard, or pick
          from over 249+ verified platforms in the directory.
        </p>
        <div className="pt-2 flex justify-center">
          <Link
            to="/"
            className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-5 py-2.5 rounded-lg bg-[#1c1917] hover:bg-[#292524] active:bg-black text-[#faf5ec] dark:bg-zinc-100 dark:hover:bg-white dark:active:bg-zinc-200 dark:text-zinc-950 font-medium text-xs font-mono transition-all active:scale-[0.98] shadow-sm min-h-[44px] border border-[#1c1917] dark:border-zinc-300"
          >
            <span>Go to Dashboard</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </Link>
        </div>
      </section>
    </div>
  );
}
