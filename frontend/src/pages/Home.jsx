import React, { useState, useEffect, useCallback, useMemo } from "react";
import { useNavigate, Link } from "react-router-dom";
import {
  GitCompare,
  FileCheck,
  Scale,
  ExternalLink,
  ChevronRight,
  ChevronLeft,
  Search,
  RefreshCw,
  Loader2,
  AlertCircle,
  Database,
  Clock,
  X,
} from "lucide-react";
import { api } from "../lib/api";
import { formatLocalDate } from "../lib/dateUtils";
import UrlForm from "../components/UrlForm";
import DiscoveryModal from "../components/DiscoveryModal";

const PAGE_SIZE = 4;

/**
 * Multi-tier fuzzy matching algorithm:
 * 1. Exact substring match in title/URL (highest priority)
 * 2. Token match (all words present in text)
 * 3. Subsequence match (characters in sequential order)
 */
function fuzzyMatchPolicy(policy, query) {
  if (!query) return { match: true, score: 0 };
  const q = query.trim().toLowerCase();
  if (!q) return { match: true, score: 0 };

  const title = (policy.title || "").toLowerCase();
  const canonical = (policy.canonical_url || "").toLowerCase();
  const url = (policy.url || "").toLowerCase();
  const level = (policy.latest_analysis?.risk_level || "").toLowerCase();
  const scoreStr =
    policy.latest_analysis?.risk_score !== undefined &&
    policy.latest_analysis?.risk_score !== null
      ? String(policy.latest_analysis.risk_score)
      : "";

  // 1. Exact substring in title
  const titleIdx = title.indexOf(q);
  if (titleIdx !== -1) {
    const isWordStart =
      titleIdx === 0 ||
      title[titleIdx - 1] === " " ||
      title[titleIdx - 1] === "|";
    return { match: true, score: 1000 + (isWordStart ? 250 : 0) - titleIdx };
  }

  // 2. Exact substring in canonical URL or URL
  const urlIdx = canonical.indexOf(q);
  if (urlIdx !== -1) {
    return { match: true, score: 800 - urlIdx };
  }

  // 3. Exact match in risk level or score
  if (level.includes(q) || scoreStr === q) {
    return { match: true, score: 600 };
  }

  // 4. Token match: all space-separated tokens in query appear in policy info
  const combined = `${title} ${canonical} ${url} ${level}`;
  const tokens = q.split(/\s+/).filter(Boolean);
  if (tokens.length > 1) {
    const allTokensMatch = tokens.every((token) => combined.includes(token));
    if (allTokensMatch) {
      return { match: true, score: 500 };
    }
  }

  // 5. Sequential subsequence match (fzf-style)
  const targetForSubseq = `${title} ${canonical}`;
  let qIdx = 0;
  let subseqScore = 0;
  let lastMatch = -1;
  for (let i = 0; i < targetForSubseq.length && qIdx < q.length; i++) {
    if (targetForSubseq[i] === q[qIdx]) {
      if (lastMatch === i - 1) {
        subseqScore += 20; // Consecutive character bonus
      } else {
        subseqScore += 5;
      }
      lastMatch = i;
      qIdx++;
    }
  }

  if (qIdx === q.length) {
    return { match: true, score: 200 + subseqScore };
  }

  return { match: false, score: 0 };
}

export default function Home() {
  const navigate = useNavigate();
  const [policies, setPolicies] = useState([]);
  const [loadingPolicies, setLoadingPolicies] = useState(true);
  const [analyzing, setAnalyzing] = useState(false);
  const [analyzeError, setAnalyzeError] = useState("");
  const [isDiscoveryOpen, setIsDiscoveryOpen] = useState(false);

  // Search & Pagination State
  const [searchQuery, setSearchQuery] = useState("");
  const [currentPage, setCurrentPage] = useState(1);

  const fetchTrackedPolicies = useCallback(async () => {
    try {
      setLoadingPolicies(true);
      const data = await api.listPolicies(100);
      setPolicies(data);
    } catch (err) {
      console.error("Failed to load policies:", err);
    } finally {
      setLoadingPolicies(false);
    }
  }, []);

  useEffect(() => {
    fetchTrackedPolicies();
  }, [fetchTrackedPolicies]);

  // Filtered & Ranked policies via Fuzzy Search
  const filteredPolicies = useMemo(() => {
    if (!searchQuery.trim()) {
      return policies;
    }
    return policies
      .map((pol) => {
        const res = fuzzyMatchPolicy(pol, searchQuery);
        return { pol, match: res.match, score: res.score };
      })
      .filter((entry) => entry.match)
      .sort((a, b) => b.score - a.score)
      .map((entry) => entry.pol);
  }, [policies, searchQuery]);

  // Pagination calculations (4 per page)
  const totalPages = Math.max(
    1,
    Math.ceil(filteredPolicies.length / PAGE_SIZE),
  );
  const safeCurrentPage = Math.min(currentPage, totalPages);
  const startIndex = (safeCurrentPage - 1) * PAGE_SIZE;
  const endIndex = Math.min(startIndex + PAGE_SIZE, filteredPolicies.length);
  const paginatedPolicies = filteredPolicies.slice(startIndex, endIndex);

  // Window of up to 4 page numbers
  const getVisiblePages = () => {
    const maxVisible = 4;
    if (totalPages <= maxVisible) {
      return Array.from({ length: totalPages }, (_, i) => i + 1);
    }
    let start = Math.max(1, safeCurrentPage - 1);
    let end = start + maxVisible - 1;
    if (end > totalPages) {
      end = totalPages;
      start = Math.max(1, end - maxVisible + 1);
    }
    const pages = [];
    for (let i = start; i <= end; i++) {
      pages.push(i);
    }
    return pages;
  };

  const handleSearchChange = (e) => {
    setSearchQuery(e.target.value);
    setCurrentPage(1);
  };

  const handleClearSearch = () => {
    setSearchQuery("");
    setCurrentPage(1);
  };

  const handlePageChange = (newPage) => {
    setCurrentPage(newPage);
  };

  const handleAnalyze = async (url) => {
    setAnalyzing(true);
    setAnalyzeError("");
    try {
      const policy = await api.analyzePolicy(url);
      navigate(`/policies/${policy.id}`);
    } catch (err) {
      setAnalyzeError(err.message || "Failed to analyze policy URL");
      setAnalyzing(false);
    }
  };

  const handleSelectDiscoveryUrl = (url) => {
    handleAnalyze(url);
  };

  return (
    <div className="flex flex-col gap-8 sm:gap-12 pb-14 sm:pb-16 pt-5 sm:pt-8 max-w-5xl mx-auto px-3.5 sm:px-6">
      {/* Hero Header */}
      <section className="order-1 space-y-4">
        <div className="space-y-2">
          <h1 className="text-xl sm:text-2xl md:text-3xl font-bold text-zinc-100 tracking-tight leading-snug sm:leading-tight">
            Public Legal Agreements Auditor
          </h1>
          <p className="text-xs sm:text-sm text-zinc-400 max-w-2xl leading-relaxed">
            Audit public legal agreements for mandatory arbitration, broad data
            sharing, and unilateral terms. Grounded in verbatim citations with
            automated revision tracking.
          </p>
        </div>

        {/* Global Error Banner */}
        {analyzeError && (
          <div className="p-3.5 rounded-lg bg-rose-950/40 border border-rose-900/60 text-rose-300 text-xs font-mono flex items-start justify-between gap-3 break-words">
            <div className="flex items-start gap-2">
              <AlertCircle className="w-4 h-4 shrink-0 mt-0.5 text-rose-400" />
              <div>
                <span className="font-semibold text-rose-200">
                  Unable to analyze policy:{" "}
                </span>
                <span>{analyzeError}</span>
              </div>
            </div>
            <button
              onClick={() => setAnalyzeError("")}
              className="text-rose-400 hover:text-rose-200 cursor-pointer p-1.5 -mr-1 -mt-1 rounded-md hover:bg-rose-900/40 shrink-0 min-w-[32px] min-h-[32px] flex items-center justify-center active:scale-95"
              title="Dismiss error"
              aria-label="Dismiss error"
            >
              <X className="w-3.5 h-3.5" />
            </button>
          </div>
        )}

        {/* URL Form */}
        <UrlForm
          onAnalyze={handleAnalyze}
          loading={analyzing}
          onOpenDiscovery={() => setIsDiscoveryOpen(true)}
        />
      </section>

      {/* Highlighted Features Section (Below Tracked Policies on mobile, above on desktop) */}
      <section className="order-3 sm:order-2 space-y-3">
        <div>
          <h2 className="text-sm font-semibold text-zinc-200 tracking-tight">
            Highlighted Features
          </h2>
          <p className="text-xs text-zinc-500">
            Core verification guarantees and auditing capabilities
          </p>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
          <div className="panel rounded-xl p-4 border space-y-2">
            <div className="flex items-center gap-2 text-xs font-semibold text-zinc-200">
              <Scale className="w-4 h-4 text-zinc-400 shrink-0" />
              <span>Clause Risk Auditing</span>
            </div>
            <p className="text-xs text-zinc-400 leading-relaxed">
              Identifies mandatory arbitration, class-action waivers, unilateral
              modifications, and liability disclaimers with calibrated risk
              ratings.
            </p>
          </div>

          <div className="panel rounded-xl p-4 border space-y-2">
            <div className="flex items-center gap-2 text-xs font-semibold text-zinc-200">
              <FileCheck className="w-4 h-4 text-zinc-400 shrink-0" />
              <span>Verbatim Source Citations</span>
            </div>
            <p className="text-xs text-zinc-400 leading-relaxed">
              Every flagged concern is anchored to an exact, unedited quotation
              from the source text—ensuring transparent verification without AI
              hallucinations.
            </p>
          </div>

          <div className="panel rounded-xl p-4 border space-y-2">
            <div className="flex items-center gap-2 text-xs font-semibold text-zinc-200">
              <GitCompare className="w-4 h-4 text-zinc-400 shrink-0" />
              <span>Revision &amp; Change Tracking</span>
            </div>
            <p className="text-xs text-zinc-400 leading-relaxed">
              Preserves baseline snapshots across legal agreements, highlighting
              word-for-word additions and removals whenever policies are updated.
            </p>
          </div>
        </div>
      </section>

      {/* Tracked Policies Section (Order 2 on mobile, Order 3 on desktop) */}
      <section className="order-2 sm:order-3 space-y-3.5 sm:space-y-3">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-1">
          <div>
            <h2 className="text-sm font-semibold text-zinc-200 tracking-tight flex items-center gap-1.5">
              <span>Tracked Policies</span>
              {policies.length > 0 && (
                <span className="font-mono text-xs font-normal text-zinc-400">
                  ({policies.length})
                </span>
              )}
            </h2>
            <p className="text-xs text-zinc-500">
              Monitored documents and baseline status
            </p>
          </div>

          <div className="flex items-center gap-2 w-full sm:w-auto">
            {/* Fuzzy Search Input */}
            <div className="relative flex-1 sm:w-64 md:w-72">
              <div className="absolute inset-y-0 left-0 pl-2.5 flex items-center pointer-events-none text-zinc-500">
                <Search className="w-3.5 h-3.5 shrink-0" />
              </div>
              <input
                type="text"
                value={searchQuery}
                onChange={handleSearchChange}
                placeholder="Search policies..."
                autoCapitalize="none"
                autoCorrect="off"
                spellCheck="false"
                className="w-full pl-8 pr-7 py-1.5 rounded-lg bg-zinc-950 border border-zinc-800 text-zinc-100 placeholder-zinc-500 text-xs font-mono focus:outline-none focus:border-zinc-300 focus:ring-1 focus:ring-zinc-300/30 transition-colors"
              />
              {searchQuery && (
                <button
                  type="button"
                  onClick={handleClearSearch}
                  className="absolute inset-y-0 right-0 pr-2 flex items-center text-zinc-500 hover:text-zinc-300 cursor-pointer"
                  title="Clear search"
                  aria-label="Clear search"
                >
                  <X className="w-3.5 h-3.5" />
                </button>
              )}
            </div>

            <button
              onClick={fetchTrackedPolicies}
              disabled={loadingPolicies}
              className="px-3 py-1.5 rounded-lg bg-zinc-900 hover:bg-zinc-800 text-zinc-300 text-xs font-mono flex items-center gap-1.5 transition-colors cursor-pointer border border-zinc-800 active:scale-95 shrink-0 min-h-[34px]"
              title="Refresh tracked policies"
            >
              <RefreshCw
                className={`w-3.5 h-3.5 ${loadingPolicies ? "animate-spin" : ""}`}
              />
              <span className="hidden xs:inline">Refresh</span>
            </button>
          </div>
        </div>

        {loadingPolicies ? (
          <div className="p-8 text-center rounded-xl panel border text-zinc-400 text-xs font-mono">
            <Loader2 className="w-5 h-5 animate-spin text-zinc-400 mx-auto mb-2" />
            <span>Loading tracked policies...</span>
          </div>
        ) : policies.length === 0 ? (
          <div className="p-8 text-center rounded-xl panel border space-y-2">
            <Database className="w-6 h-6 text-zinc-600 mx-auto" />
            <p className="text-xs text-zinc-400 font-mono">
              No policies tracked yet
            </p>
            <p className="text-[11px] text-zinc-500">
              Submit a public URL above to create your first version baseline.
            </p>
          </div>
        ) : filteredPolicies.length === 0 ? (
          <div className="p-8 text-center rounded-xl panel border border-zinc-800 space-y-3 font-mono">
            <div className="w-10 h-10 rounded-full bg-zinc-900 border border-zinc-800 flex items-center justify-center mx-auto text-zinc-500">
              <Search className="w-4 h-4" />
            </div>
            <div className="space-y-1">
              <p className="text-xs text-zinc-300">
                No tracked policies match &ldquo;{searchQuery}&rdquo;
              </p>
              <p className="text-[11px] text-zinc-500">
                Try searching by company name, URL, or agreement type.
              </p>
            </div>
            <button
              type="button"
              onClick={handleClearSearch}
              className="px-3 py-1.5 rounded-md bg-zinc-900 hover:bg-zinc-800 text-zinc-300 border border-zinc-800 text-xs transition-colors cursor-pointer active:scale-95"
            >
              Clear search filter
            </button>
          </div>
        ) : (
          <>
            {/* Desktop / Tablet Table View */}
            <div className="hidden md:block panel rounded-xl border overflow-hidden">
              <div className="w-full overflow-hidden">
                <table className="w-full text-xs font-mono">
                  <thead className="bg-zinc-950 border-b border-zinc-800 text-zinc-400 uppercase tracking-wider text-[11px]">
                    <tr>
                      <th className="py-3 px-4 text-center w-[44%]">
                        Policy Document
                      </th>
                      <th className="py-3 px-3 text-center w-[20%]">
                        Canonical URL
                      </th>
                      <th className="py-3 px-3 text-center whitespace-nowrap">
                        Risk Assessment
                      </th>
                      <th className="py-3 px-3 text-center whitespace-nowrap">
                        Last Checked
                      </th>
                      <th className="py-3 pr-4 pl-2 text-center whitespace-nowrap">
                        Action
                      </th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-zinc-800/80">
                    {paginatedPolicies.map((pol) => {
                      const formattedDate = formatLocalDate(
                        pol.last_checked_at,
                      );
                      const analysis = pol.latest_analysis;
                      const score = analysis?.risk_score;
                      const level = analysis?.risk_level;
                      const isFb =
                        analysis?.model_id === "deterministic-fallback";

                      return (
                        <tr
                          key={pol.id}
                          className="hover:bg-zinc-900/50 transition-colors"
                        >
                          <td className="py-3.5 pl-4 pr-3 text-left">
                            <Link
                              to={`/policies/${pol.id}`}
                              className="font-medium text-zinc-100 hover:text-white transition-colors block text-xs line-clamp-2"
                              title={pol.title || "Policy Document"}
                            >
                              {pol.title || "Policy Document"}
                            </Link>
                          </td>
                          <td className="py-3.5 px-3 text-zinc-500 text-left max-w-[180px] lg:max-w-xs truncate">
                            {pol.canonical_url?.startsWith("/") ? (
                              <Link
                                to={pol.canonical_url}
                                className="hover:text-zinc-300 transition-colors inline-flex items-center gap-1.5 max-w-full text-[11px] truncate"
                                title={pol.canonical_url}
                              >
                                <span className="truncate">
                                  {pol.canonical_url}
                                </span>
                              </Link>
                            ) : (
                              <a
                                href={pol.canonical_url}
                                target="_blank"
                                rel="noreferrer"
                                className="hover:text-zinc-300 transition-colors inline-flex items-center gap-1.5 max-w-full text-[11px] truncate"
                                title={pol.canonical_url}
                              >
                                <span className="truncate">
                                  {pol.canonical_url}
                                </span>
                                <ExternalLink className="w-2.5 h-2.5 shrink-0 opacity-60" />
                              </a>
                            )}
                          </td>
                          <td className="py-3.5 px-3 whitespace-nowrap text-left">
                            {score !== null && score !== undefined ? (
                              <span
                                className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md text-[11px] font-mono font-medium tracking-wide whitespace-nowrap ${
                                  level === "high" || (!level && score > 80)
                                    ? "bg-rose-950/50 border border-rose-800/80 text-rose-300"
                                    : level === "elevated" ||
                                        (!level && score > 65)
                                      ? "bg-amber-950/50 border border-amber-800/80 text-amber-300"
                                      : level === "moderate" ||
                                          (!level && score > 35)
                                        ? "bg-yellow-950/40 border border-yellow-800/70 text-yellow-300"
                                        : "bg-emerald-950/40 border border-emerald-800/70 text-emerald-300"
                                }`}
                              >
                                <span
                                  className={`w-1.5 h-1.5 rounded-full shrink-0 ${
                                    level === "high" || (!level && score > 80)
                                      ? "bg-rose-400"
                                      : level === "elevated" ||
                                          (!level && score > 65)
                                        ? "bg-amber-400"
                                        : level === "moderate" ||
                                            (!level && score > 35)
                                          ? "bg-yellow-400"
                                          : "bg-emerald-400"
                                  }`}
                                />
                                <span className="font-semibold">{score}</span>
                                <span className="text-[10px] text-zinc-500 font-normal">
                                  /100
                                </span>
                                <span className="text-zinc-600 font-normal">
                                  ·
                                </span>
                                <span className="capitalize">
                                  {level || "rated"}
                                </span>
                              </span>
                            ) : (
                              <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md text-[11px] font-mono text-zinc-400 bg-zinc-900 border border-zinc-800 whitespace-nowrap">
                                <span className="w-1.5 h-1.5 rounded-full bg-zinc-600 shrink-0" />
                                <span>{isFb ? "Fallback" : "Pending"}</span>
                              </span>
                            )}
                          </td>
                          <td className="py-3.5 px-3 text-zinc-400 whitespace-nowrap text-left">
                            {formattedDate}
                          </td>
                          <td className="py-3.5 pr-4 pl-2 text-right whitespace-nowrap">
                            <Link
                              to={`/policies/${pol.id}`}
                              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-zinc-900 hover:bg-zinc-800 text-zinc-200 border border-zinc-800 hover:border-zinc-700 transition-colors text-xs active:scale-95"
                            >
                              <span>Inspect</span>
                              <ChevronRight className="w-3.5 h-3.5 text-zinc-500" />
                            </Link>
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            </div>

            {/* Mobile Dedicated 2x2 Grid View with final card centered in between */}
            <div className="md:hidden grid grid-cols-2 gap-3 sm:gap-4">
              {paginatedPolicies.map((pol, idx) => {
                const formattedDate = formatLocalDate(pol.last_checked_at);
                const shortDate = formatLocalDate(pol.last_checked_at, {
                  month: "short",
                  day: "numeric",
                });
                const analysis = pol.latest_analysis;
                const score = analysis?.risk_score;
                const level = analysis?.risk_level;
                const isFb = analysis?.model_id === "deterministic-fallback";
                const isFinalOdd =
                  idx === paginatedPolicies.length - 1 &&
                  paginatedPolicies.length % 2 === 1;

                return (
                  <div
                    key={pol.id}
                    className={`panel panel-hover rounded-xl p-3.5 sm:p-4.5 border flex flex-col justify-between min-h-[195px] sm:min-h-[215px] text-xs transition-all ${
                      isFinalOdd
                        ? "col-span-2 w-full max-w-[calc(50%-0.375rem)] sm:max-w-[calc(50%-0.5rem)] justify-self-center"
                        : ""
                    }`}
                  >
                    {/* Top: Title & URL */}
                    <div className="space-y-1.5 min-w-0">
                      <div className="flex items-start justify-between gap-1.5">
                        <Link
                          to={`/policies/${pol.id}`}
                          className="font-semibold text-zinc-100 hover:text-white transition-colors text-[13px] sm:text-sm leading-snug break-words"
                          title={pol.title || "Policy Document"}
                        >
                          {pol.title || "Policy Document"}
                        </Link>
                        <Link
                          to={`/policies/${pol.id}`}
                          className="text-zinc-500 hover:text-zinc-300 p-0.5 shrink-0 mt-0.5"
                          aria-label="Inspect policy"
                        >
                          <ChevronRight className="w-3.5 h-3.5" />
                        </Link>
                      </div>

                      <div className="text-zinc-500 font-mono text-[11px] truncate">
                        {pol.canonical_url?.startsWith("/") ? (
                          <Link
                            to={pol.canonical_url}
                            className="truncate hover:text-zinc-300 transition-colors block"
                            title={pol.canonical_url}
                          >
                            {pol.canonical_url}
                          </Link>
                        ) : (
                          <a
                            href={pol.canonical_url}
                            target="_blank"
                            rel="noreferrer"
                            className="truncate hover:text-zinc-300 transition-colors inline-flex items-center gap-1 max-w-full"
                            title={pol.canonical_url}
                          >
                            <span className="truncate">{pol.canonical_url}</span>
                            <ExternalLink className="w-2.5 h-2.5 shrink-0 opacity-60" />
                          </a>
                        )}
                      </div>
                    </div>

                    {/* Bottom: Score pill + Date + Action Button */}
                    <div className="pt-3 mt-3 border-t border-zinc-800/80 space-y-2.5">
                      <div className="flex items-center justify-between gap-1">
                        {score !== null && score !== undefined ? (
                          <span
                            className={`inline-flex items-center gap-1.5 px-2 py-0.5 rounded-md text-[11px] font-mono font-medium ${
                              level === "high" || (!level && score > 80)
                                ? "bg-rose-950/50 border border-rose-800/80 text-rose-300"
                                : level === "elevated" || (!level && score > 65)
                                  ? "bg-amber-950/50 border border-amber-800/80 text-amber-300"
                                  : level === "moderate" || (!level && score > 35)
                                    ? "bg-yellow-950/40 border border-yellow-800/70 text-yellow-300"
                                    : "bg-emerald-950/40 border border-emerald-800/70 text-emerald-300"
                            }`}
                          >
                            <span
                              className={`w-1.5 h-1.5 rounded-full shrink-0 ${
                                level === "high" || (!level && score > 80)
                                  ? "bg-rose-400"
                                  : level === "elevated" || (!level && score > 65)
                                    ? "bg-amber-400"
                                    : level === "moderate" || (!level && score > 35)
                                      ? "bg-yellow-400"
                                      : "bg-emerald-400"
                              }`}
                            />
                            <span>{score}</span>
                            <span className="text-zinc-500 font-normal">/100</span>
                          </span>
                        ) : (
                          <span className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded-md text-[11px] font-mono text-zinc-400 bg-zinc-900 border border-zinc-800">
                            <span className="w-1.5 h-1.5 rounded-full bg-zinc-600 shrink-0" />
                            <span>{isFb ? "Fallback" : "Pending"}</span>
                          </span>
                        )}

                        <span
                          className="text-[11px] font-mono text-zinc-500 flex items-center gap-1"
                          title={formattedDate}
                        >
                          <Clock className="w-3 h-3 text-zinc-600 shrink-0" />
                          <span>{shortDate}</span>
                        </span>
                      </div>

                      <Link
                        to={`/policies/${pol.id}`}
                        className="w-full py-2 px-3 rounded-lg bg-zinc-900 hover:bg-zinc-850 active:bg-zinc-800 border border-zinc-800 text-zinc-200 text-xs font-mono font-medium flex items-center justify-center gap-1 active:scale-[0.98] transition-all"
                      >
                        <span>Inspect</span>
                        <ChevronRight className="w-3.5 h-3.5 text-zinc-400" />
                      </Link>
                    </div>
                  </div>
                );
              })}
            </div>

            {/* Pagination Controls - Centered cleanly without an outside box */}
            {filteredPolicies.length > 0 && (
              <div className="flex flex-col sm:flex-row items-center justify-center gap-4 sm:gap-6 pt-3 pb-1 text-xs font-mono">
                <div className="text-zinc-500 text-center sm:text-left">
                  <span>
                    Showing{" "}
                    {startIndex + 1 === endIndex ? (
                      <span className="text-zinc-300 font-semibold">{endIndex}</span>
                    ) : (
                      <>
                        <span className="text-zinc-300 font-semibold">{startIndex + 1}</span>
                        &ndash;
                        <span className="text-zinc-300 font-semibold">{endIndex}</span>
                      </>
                    )}{" "}
                    of{" "}
                    <span className="text-zinc-300 font-semibold">
                      {filteredPolicies.length}
                    </span>{" "}
                    {filteredPolicies.length === 1 ? "policy" : "policies"}
                  </span>
                  {searchQuery && (
                    <span className="text-zinc-500 text-[11px] block sm:inline sm:ml-1.5">
                      (filtered from {policies.length} total)
                    </span>
                  )}
                </div>

                <div className="flex items-center gap-1 sm:gap-1.5">
                  <button
                    type="button"
                    onClick={() => handlePageChange(Math.max(1, safeCurrentPage - 1))}
                    disabled={safeCurrentPage <= 1}
                    className="px-2.5 py-1.5 rounded-md bg-zinc-900 hover:bg-zinc-850 active:bg-zinc-800 text-zinc-300 hover:text-white border border-zinc-800 text-xs font-mono transition-colors cursor-pointer active:scale-95 disabled:opacity-40 disabled:cursor-not-allowed flex items-center gap-1"
                    aria-label="Previous page"
                  >
                    <ChevronLeft className="w-3.5 h-3.5" />
                    <span>Prev</span>
                  </button>

                  <div className="flex items-center gap-1">
                    {getVisiblePages().map((page) => (
                      <button
                        key={page}
                        type="button"
                        onClick={() => handlePageChange(page)}
                        className={`min-w-[30px] h-[28px] rounded-md text-xs font-mono transition-colors cursor-pointer active:scale-95 flex items-center justify-center ${
                          page === safeCurrentPage
                            ? "bg-zinc-100 text-zinc-950 font-bold shadow-xs"
                            : "bg-zinc-900 hover:bg-zinc-850 text-zinc-400 hover:text-zinc-200 border border-zinc-800"
                        }`}
                        aria-label={`Page ${page}`}
                        aria-current={
                          page === safeCurrentPage ? "page" : undefined
                        }
                      >
                        {page}
                      </button>
                    ))}
                  </div>

                  <button
                    type="button"
                    onClick={() =>
                      handlePageChange(Math.min(totalPages, safeCurrentPage + 1))
                    }
                    disabled={safeCurrentPage >= totalPages}
                    className="px-2.5 py-1.5 rounded-md bg-zinc-900 hover:bg-zinc-850 active:bg-zinc-800 text-zinc-300 hover:text-white border border-zinc-800 text-xs font-mono transition-colors cursor-pointer active:scale-95 disabled:opacity-40 disabled:cursor-not-allowed flex items-center gap-1"
                    aria-label="Next page"
                  >
                    <span>Next</span>
                    <ChevronRight className="w-3.5 h-3.5" />
                  </button>
                </div>
              </div>
            )}
          </>
        )}
      </section>

      {/* Discovery Modal */}
      <DiscoveryModal
        isOpen={isDiscoveryOpen}
        onClose={() => setIsDiscoveryOpen(false)}
        onSelectUrl={handleSelectDiscoveryUrl}
      />
    </div>
  );
}
