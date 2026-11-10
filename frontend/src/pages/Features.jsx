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
        className="flex items-center gap-2 text-xs font-mono text-zinc-500"
      >
        <Link to="/" className="hover:text-zinc-300 transition-colors">
          Dashboard
        </Link>
        <ChevronRight className="w-3.5 h-3.5 text-zinc-700" />
        <span className="text-zinc-300">Features</span>
      </nav>

      {/* Header */}
      <header className="space-y-3 border-b border-zinc-800/80 pb-6">
        <div className="inline-flex items-center gap-2 px-2.5 py-1 rounded-md bg-zinc-900 border border-zinc-800 text-[10px] sm:text-[11px] font-mono text-zinc-400">
          <Layers className="w-3.5 h-3.5 text-zinc-400 shrink-0" />
          <span>Platform Architecture &amp; Capabilities</span>
        </div>
        <h1 className="text-xl sm:text-3xl md:text-4xl font-semibold tracking-tight text-zinc-100">
          Auditing Capabilities &amp; System Guarantees
        </h1>
        <p className="text-xs sm:text-sm md:text-base text-zinc-400 max-w-3xl leading-relaxed">
          EasyFinePrint is an automated legal agreement monitor designed to detect
          hidden consumer liabilities, track word-for-word policy revisions, and anchor
          every risk assessment in strict verbatim source quotations.
        </p>
      </header>

      {/* Primary Highlighted Features Grid */}
      <section className="space-y-3.5 sm:space-y-4">
        <div>
          <h2 className="text-sm sm:text-base md:text-lg font-semibold text-zinc-200 tracking-tight flex items-center gap-2">
            <span>Core Auditing Pillars</span>
          </h2>
          <p className="text-xs text-zinc-500">
            Three foundational verification guarantees governing every policy audit
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-3.5 sm:gap-4">
          {/* Feature 1: Clause Risk Auditing */}
          <div className="rounded-xl p-4 sm:p-5 bg-[#121215] border border-zinc-800 flex flex-col justify-between space-y-4 shadow-sm hover:border-zinc-700 transition-colors">
            <div className="space-y-3">
              <div className="flex items-start gap-3">
                <div className="w-8 h-8 sm:w-9 sm:h-9 rounded-lg bg-zinc-900 border border-zinc-800 flex items-center justify-center text-zinc-200 shrink-0">
                  <Scale className="w-4 h-4 text-zinc-300" />
                </div>
                <div className="min-w-0 flex-1">
                  <h3 className="text-sm font-semibold text-zinc-100">
                    Clause Risk Auditing
                  </h3>
                  <p className="text-[11px] sm:text-xs text-zinc-500 font-mono mt-0.5">
                    Calibrated severity scoring
                  </p>
                </div>
              </div>
              <p className="text-xs text-zinc-400 leading-relaxed">
                Systematically scans terms and privacy documents for binding arbitration,
                class-action waivers, unilateral modification rights, data telemetry expansions,
                and sweeping liability disclaimers with calibrated severity tiers.
              </p>
            </div>

            <ul className="space-y-2 sm:space-y-1.5 pt-3 border-t border-zinc-800/60 text-[11px] font-mono text-zinc-400">
              <li className="flex items-center gap-2 leading-tight">
                <CheckCircle2 className="w-3.5 h-3.5 text-zinc-500 shrink-0" />
                <span>Arbitration &amp; Jury Waivers</span>
              </li>
              <li className="flex items-center gap-2 leading-tight">
                <CheckCircle2 className="w-3.5 h-3.5 text-zinc-500 shrink-0" />
                <span>Unilateral Policy Changes</span>
              </li>
              <li className="flex items-center gap-2 leading-tight">
                <CheckCircle2 className="w-3.5 h-3.5 text-zinc-500 shrink-0" />
                <span>Third-Party Data Telemetry</span>
              </li>
            </ul>
          </div>

          {/* Feature 2: Verbatim Source Citations */}
          <div className="rounded-xl p-4 sm:p-5 bg-[#121215] border border-zinc-800 flex flex-col justify-between space-y-4 shadow-sm hover:border-zinc-700 transition-colors">
            <div className="space-y-3">
              <div className="flex items-start gap-3">
                <div className="w-8 h-8 sm:w-9 sm:h-9 rounded-lg bg-zinc-900 border border-zinc-800 flex items-center justify-center text-zinc-200 shrink-0">
                  <FileCheck className="w-4 h-4 text-zinc-300" />
                </div>
                <div className="min-w-0 flex-1">
                  <h3 className="text-sm font-semibold text-zinc-100">
                    Verbatim Source Citations
                  </h3>
                  <p className="text-[11px] sm:text-xs text-zinc-500 font-mono mt-0.5">
                    Zero hallucination guarantee
                  </p>
                </div>
              </div>
              <p className="text-xs text-zinc-400 leading-relaxed">
                Every flagged risk is anchored to an exact, unedited quotation verified directly
                against the ingested document. If a quoted phrase does not exist character-for-character
                in the source text, the finding is automatically purged.
              </p>
            </div>

            <ul className="space-y-2 sm:space-y-1.5 pt-3 border-t border-zinc-800/60 text-[11px] font-mono text-zinc-400">
              <li className="flex items-center gap-2 leading-tight">
                <CheckCircle2 className="w-3.5 h-3.5 text-zinc-500 shrink-0" />
                <span>Exact Character Matching</span>
              </li>
              <li className="flex items-center gap-2 leading-tight">
                <CheckCircle2 className="w-3.5 h-3.5 text-zinc-500 shrink-0" />
                <span>Interactive Quote Anchoring</span>
              </li>
              <li className="flex items-center gap-2 leading-tight">
                <CheckCircle2 className="w-3.5 h-3.5 text-zinc-500 shrink-0" />
                <span>Automated Finding Pruning</span>
              </li>
            </ul>
          </div>

          {/* Feature 3: Revision & Change Tracking */}
          <div className="rounded-xl p-4 sm:p-5 bg-[#121215] border border-zinc-800 flex flex-col justify-between space-y-4 shadow-sm hover:border-zinc-700 transition-colors">
            <div className="space-y-3">
              <div className="flex items-start gap-3">
                <div className="w-8 h-8 sm:w-9 sm:h-9 rounded-lg bg-zinc-900 border border-zinc-800 flex items-center justify-center text-zinc-200 shrink-0">
                  <GitCompare className="w-4 h-4 text-zinc-300" />
                </div>
                <div className="min-w-0 flex-1">
                  <h3 className="text-sm font-semibold text-zinc-100">
                    Revision &amp; Change Tracking
                  </h3>
                  <p className="text-[11px] sm:text-xs text-zinc-500 font-mono mt-0.5">
                    Deterministic Myers sequence diff
                  </p>
                </div>
              </div>
              <p className="text-xs text-zinc-400 leading-relaxed">
                Stores immutable baseline snapshots over time. Whenever agreements are updated,
                the engine highlights word-for-word insertions and deletions alongside semantic
                explanations of legal implications.
              </p>
            </div>

            <ul className="space-y-2 sm:space-y-1.5 pt-3 border-t border-zinc-800/60 text-[11px] font-mono text-zinc-400">
              <li className="flex items-center gap-2 leading-tight">
                <CheckCircle2 className="w-3.5 h-3.5 text-zinc-500 shrink-0" />
                <span>Word-for-Word Visual Diff</span>
              </li>
              <li className="flex items-center gap-2 leading-tight">
                <CheckCircle2 className="w-3.5 h-3.5 text-zinc-500 shrink-0" />
                <span>Immutable Version History</span>
              </li>
              <li className="flex items-center gap-2 leading-tight">
                <CheckCircle2 className="w-3.5 h-3.5 text-zinc-500 shrink-0" />
                <span>Automated Semantic Deltas</span>
              </li>
            </ul>
          </div>
        </div>
      </section>

      {/* 4-Tier Ingestion & Fallback Pipeline */}
      <section className="space-y-3.5 sm:space-y-4 pt-2 sm:pt-4">
        <div>
          <h2 className="text-sm sm:text-base md:text-lg font-semibold text-zinc-200 tracking-tight flex items-center gap-2">
            <span>4-Tier Ingestion &amp; Diff Pipeline</span>
          </h2>
          <p className="text-xs text-zinc-500">
            Multi-stage retrieval hierarchy for continuous document ingestion across network barriers
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-3.5 sm:gap-4">
          {/* Tier 1 */}
          <div className="rounded-xl p-4 sm:p-5 bg-[#121215] border border-zinc-800 space-y-3">
            <div className="flex items-start sm:items-center gap-2.5 sm:gap-3">
              <div className="w-8 h-8 rounded-lg bg-zinc-900 border border-zinc-800 flex items-center justify-center text-zinc-300 shrink-0">
                <Globe className="w-4 h-4" />
              </div>
              <div className="min-w-0 flex-1">
                <h3 className="text-sm font-semibold text-zinc-100">
                  Tier 1: Live Fetch &amp; SPA Hydration
                </h3>
                <span className="text-[11px] font-mono text-zinc-500 block">
                  Direct Outbound HTTP &amp; Client State Extraction
                </span>
              </div>
            </div>
            <p className="text-xs text-zinc-400 leading-relaxed">
              Fetches agreements directly with desktop Chrome profiles and multi-hop SSRF validation.
              Recursively extracts DOM content and client JSON hydration state (Next.js __NEXT_DATA__, Redux, Vue).
            </p>
          </div>

          {/* Tier 2 */}
          <div className="rounded-xl p-4 sm:p-5 bg-[#121215] border border-zinc-800 space-y-3">
            <div className="flex items-start sm:items-center gap-2.5 sm:gap-3">
              <div className="w-8 h-8 rounded-lg bg-zinc-900 border border-zinc-800 flex items-center justify-center text-zinc-300 shrink-0">
                <Archive className="w-4 h-4" />
              </div>
              <div className="min-w-0 flex-1">
                <h3 className="text-sm font-semibold text-zinc-100">
                  Tier 2: Wayback Machine Archive Fallback
                </h3>
                <span className="text-[11px] font-mono text-zinc-500 block">
                  Public Archive Availability API Integration
                </span>
              </div>
            </div>
            <p className="text-xs text-zinc-400 leading-relaxed">
              When origin servers return 403, 429, or bot challenges (&lt;100 characters), the engine queries
              the Internet Archive for the latest verified public snapshot, stripping archive navigation toolbars.
            </p>
          </div>

          {/* Tier 3 */}
          <div className="rounded-xl p-4 sm:p-5 bg-[#121215] border border-zinc-800 space-y-3">
            <div className="flex items-start sm:items-center gap-2.5 sm:gap-3">
              <div className="w-8 h-8 rounded-lg bg-zinc-900 border border-zinc-800 flex items-center justify-center text-zinc-300 shrink-0">
                <FileText className="w-4 h-4" />
              </div>
              <div className="min-w-0 flex-1">
                <h3 className="text-sm font-semibold text-zinc-100">
                  Tier 3: User-Provided Document Ingestion
                </h3>
                <span className="text-[11px] font-mono text-zinc-500 block">
                  Manual Text Ingestion with Provenance Stamping
                </span>
              </div>
            </div>
            <p className="text-xs text-zinc-400 leading-relaxed">
              Accepts direct text paste for policies behind authentication or corporate intranets. Enforces strict input bounds
              (URL ≤2,048 chars, title ≤200 chars, body ≤500,000 chars), canonical deduplication against system policies, and immutable provenance stamping.
            </p>
          </div>

          {/* Tier 4 */}
          <div className="rounded-xl p-4 sm:p-5 bg-[#121215] border border-zinc-800 space-y-3">
            <div className="flex items-start sm:items-center gap-2.5 sm:gap-3">
              <div className="w-8 h-8 rounded-lg bg-zinc-900 border border-zinc-800 flex items-center justify-center text-zinc-300 shrink-0">
                <Database className="w-4 h-4" />
              </div>
              <div className="min-w-0 flex-1">
                <h3 className="text-sm font-semibold text-zinc-100">
                  Tier 4: Zero-Drift Baseline Database Cache
                </h3>
                <span className="text-[11px] font-mono text-zinc-500 block">
                  Deterministic Database Snapshot Fallback
                </span>
              </div>
            </div>
            <p className="text-xs text-zinc-400 leading-relaxed">
              If an external server experiences downtime during a check, the engine serves the verified
              database baseline, preserving historical evaluations without destructive overwrites or false diffs.
            </p>
          </div>
        </div>
      </section>

      {/* Deep Architecture Grid */}
      <section className="space-y-3.5 sm:space-y-4 pt-2 sm:pt-4">
        <div>
          <h2 className="text-sm sm:text-base md:text-lg font-semibold text-zinc-200 tracking-tight flex items-center gap-2">
            <span>Engineering Architecture</span>
          </h2>
          <p className="text-xs text-zinc-500">
            Resilient pipeline infrastructure designed for production reliability
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-3.5 sm:gap-4">
          {/* Discovery Engine */}
          <div className="rounded-xl p-4 sm:p-5 bg-[#121215] border border-zinc-800 space-y-3">
            <div className="flex items-start sm:items-center gap-2.5 sm:gap-3">
              <div className="w-8 h-8 rounded-lg bg-zinc-900 border border-zinc-800 flex items-center justify-center text-zinc-300 shrink-0">
                <Search className="w-4 h-4" />
              </div>
              <div className="min-w-0 flex-1">
                <h3 className="text-sm font-semibold text-zinc-100">
                  Dynamic Legal Discovery Engine
                </h3>
                <span className="text-[11px] font-mono text-zinc-500 block">
                  Verified Directory &amp; Dynamic Crawler
                </span>
              </div>
            </div>
            <p className="text-xs text-zinc-400 leading-relaxed">
              Provides one-click search across 249+ pre-verified platform agreements with 501+ legal documents,
              paired with an autonomous multi-stage fallback crawler that probes domains, inspects
              footer DOM legal links, and resolves canonical legal endpoints.
            </p>
          </div>

          {/* SSRF Security */}
          <div className="rounded-xl p-4 sm:p-5 bg-[#121215] border border-zinc-800 space-y-3">
            <div className="flex items-start sm:items-center gap-2.5 sm:gap-3">
              <div className="w-8 h-8 rounded-lg bg-zinc-900 border border-zinc-800 flex items-center justify-center text-zinc-300 shrink-0">
                <ShieldCheck className="w-4 h-4" />
              </div>
              <div className="min-w-0 flex-1">
                <h3 className="text-sm font-semibold text-zinc-100">
                  Multi-Hop SSRF Guard
                </h3>
                <span className="text-[11px] font-mono text-zinc-500 block">
                  DNS Resolution &amp; CIDR Enforcement
                </span>
              </div>
            </div>
            <p className="text-xs text-zinc-400 leading-relaxed">
              Every outbound request undergoes strict multi-hop SSRF validation across DNS resolutions,
              preventing access to internal networks, private CIDR blocks (RFC 1918, RFC 4193),
              cloud metadata endpoints (169.254.169.254), and loopback interfaces.
            </p>
          </div>

          {/* Single-Pass Inference & Zero-Drift Cache */}
          <div className="rounded-xl p-4 sm:p-5 bg-[#121215] border border-zinc-800 space-y-3">
            <div className="flex items-start sm:items-center gap-2.5 sm:gap-3">
              <div className="w-8 h-8 rounded-lg bg-zinc-900 border border-zinc-800 flex items-center justify-center text-zinc-300 shrink-0">
                <Zap className="w-4 h-4" />
              </div>
              <div className="min-w-0 flex-1">
                <h3 className="text-sm font-semibold text-zinc-100">
                  Zero-Drift Baseline Cache
                </h3>
                <span className="text-[11px] font-mono text-zinc-500 block">
                  Deterministic SHA-256 Hashing
                </span>
              </div>
            </div>
            <p className="text-xs text-zinc-400 leading-relaxed">
              Ingested policies are normalized and hashed via SHA-256. If a policy URL or body
              has not changed, previously audited risk baselines are returned instantly without
              redundant AI computation or score drift.
            </p>
          </div>

          {/* Multi-Tier Content Extraction */}
          <div className="rounded-xl p-4 sm:p-5 bg-[#121215] border border-zinc-800 space-y-3">
            <div className="flex items-start sm:items-center gap-2.5 sm:gap-3">
              <div className="w-8 h-8 rounded-lg bg-zinc-900 border border-zinc-800 flex items-center justify-center text-zinc-300 shrink-0">
                <Cpu className="w-4 h-4" />
              </div>
              <div className="min-w-0 flex-1">
                <h3 className="text-sm font-semibold text-zinc-100">
                  Multi-Tier SPA &amp; Hydration Extractor
                </h3>
                <span className="text-[11px] font-mono text-zinc-500 block">
                  Trafilatura, DOM, and Client State Parsing
                </span>
              </div>
            </div>
            <p className="text-xs text-zinc-400 leading-relaxed">
              Extracts cleanly across traditional web articles and modern Single-Page Applications
              (React, Next.js, Redux, Vue) by recursively parsing client-side JSON hydration state
              and sandboxed script evaluation.
            </p>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="rounded-xl p-5 sm:p-8 bg-zinc-950 border border-zinc-800 text-center space-y-3.5 sm:space-y-4">
        <h2 className="text-base sm:text-xl font-semibold text-zinc-100">
          Ready to audit a legal agreement?
        </h2>
        <p className="text-xs sm:text-sm text-zinc-400 max-w-xl mx-auto leading-relaxed">
          Paste any public Terms of Use or Privacy Policy URL on the dashboard, or pick
          from over 249+ verified platforms in the directory.
        </p>
        <div className="pt-2 flex justify-center">
          <Link
            to="/"
            className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-4 py-2.5 rounded-lg bg-zinc-100 hover:bg-white active:bg-zinc-200 text-zinc-950 font-medium text-xs font-mono transition-all active:scale-[0.98] shadow-sm min-h-[44px]"
          >
            <span>Go to Dashboard</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </Link>
        </div>
      </section>
    </div>
  );
}
