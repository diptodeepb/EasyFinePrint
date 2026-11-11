import React, { useState, useEffect, useCallback, useMemo } from "react";
import { useNavigate, Link } from "react-router-dom";
import {
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

const PAGE_SIZE = 8;

function getRiskTier(analysis) {
  if (!analysis) return { level: "", score: null };
  const score = analysis.risk_score;
  const rawLevel = (analysis.risk_level || "").toLowerCase();
  const level =
    rawLevel ||
    (score > 74
      ? "high"
      : score > 55
      ? "elevated"
      : score > 30
      ? "moderate"
      : score !== null && score !== undefined
      ? "low"
      : "");
  return { level, score };
}

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
  const { level, score } = getRiskTier(policy.latest_analysis);
  const scoreStr = score !== undefined && score !== null ? String(score) : "";

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
  const [policyTab, setPolicyTab] = useState("system"); // "system" | "user"

  const isUserMaintained = (pol) => {
    return (
      pol?.provenance === "user_pasted" ||
      pol?.latest_analysis?.provenance === "user_pasted" ||
      pol?.extractor === "user_pasted"
    );
  };

  const systemCount = useMemo(() => {
    return policies.filter((p) => !isUserMaintained(p)).length;
  }, [policies]);

  const userCount = useMemo(() => {
    return policies.filter((p) => isUserMaintained(p)).length;
  }, [policies]);

  const tabPolicies = useMemo(() => {
    if (policyTab === "user") {
      return policies.filter((p) => isUserMaintained(p));
    }
    return policies.filter((p) => !isUserMaintained(p));
  }, [policies, policyTab]);

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
      return tabPolicies;
    }
    return tabPolicies
      .map((pol) => {
        const res = fuzzyMatchPolicy(pol, searchQuery);
        return { pol, match: res.match, score: res.score };
      })
      .filter((entry) => entry.match)
      .sort((a, b) => b.score - a.score)
      .map((entry) => entry.pol);
  }, [tabPolicies, searchQuery]);

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

  const handleTabChange = (newTab) => {
    if (newTab !== policyTab) {
      setPolicyTab(newTab);
      setCurrentPage(1);
    }
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
      <section className="space-y-4">
        <div className="space-y-2">
          <h1 className="text-xl sm:text-2xl md:text-3xl font-bold text-black dark:text-zinc-100 tracking-tight leading-snug sm:leading-tight">
            Public Legal Agreements Auditor
          </h1>
          <p className="text-xs sm:text-sm text-black dark:text-zinc-400 max-w-2xl leading-relaxed">
            Audit public legal agreements for mandatory arbitration, broad data
            sharing, and unilateral terms. Grounded in verbatim citations with
            automated revision tracking.
          </p>
        </div>

        {/* Global Error Banner */}
        {analyzeError && (
          <div className="p-3.5 rounded-lg bg-rose-500/10 dark:bg-rose-950/40 border border-rose-300 dark:border-rose-900/60 text-rose-800 dark:text-rose-300 text-xs font-mono flex items-start justify-between gap-3 break-words">
            <div className="flex items-start gap-2">
              <AlertCircle className="w-4 h-4 shrink-0 mt-0.5 text-rose-600 dark:text-rose-400" />
              <div>
                <span className="font-semibold text-rose-900 dark:text-rose-200">
                  Unable to analyze policy:{" "}
                </span>
                <span>{analyzeError}</span>
              </div>
            </div>
            <button
              onClick={() => setAnalyzeError("")}
              className="text-rose-600 dark:text-rose-400 hover:text-rose-800 dark:hover:text-rose-200 cursor-pointer p-1.5 -mr-1 -mt-1 rounded-md hover:bg-rose-500/20 dark:hover:bg-rose-900/40 shrink-0 min-w-[32px] min-h-[32px] flex items-center justify-center active:scale-95"
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
          trackedPolicies={policies}
        />
      </section>

      {/* Tracked Policies Section */}
      <section className="space-y-3.5 sm:space-y-3">
        {/* Dedicated Line: Section Title & Description */}
        <div>
          <h2 className="text-sm font-semibold text-[#1c1917] dark:text-zinc-200 tracking-tight flex items-center gap-1.5">
            <span>Tracked Policies</span>
            {policies.length > 0 && (
              <span className="font-mono text-xs font-normal text-[#78716c] dark:text-zinc-400">
                ({policies.length})
              </span>
            )}
          </h2>
          <p className="text-xs text-[#5c5549] dark:text-zinc-500">
            Monitored documents and baseline status
          </p>
        </div>

        {/* Dedicated Line: Left-aligned Tabs and Right-aligned Search/Refresh on PC */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2.5 pb-1">
          {/* Switchable Ingestion Tabs (Left-aligned) */}
          <div className="h-[34px] inline-flex items-center p-0.5 rounded-lg bg-[#e5ddcf] dark:bg-zinc-950 border border-[#d5cbba] dark:border-zinc-800 text-[11px] font-mono self-start shadow-xs">
            <button
              type="button"
              onClick={() => handleTabChange("system")}
              className={`h-full px-2.5 rounded-md transition-all cursor-pointer flex items-center gap-1.5 text-[11px] leading-none ${
                policyTab === "system"
                  ? "bg-[#f5eedf] dark:bg-zinc-800 text-[#1c1917] dark:text-zinc-100 font-medium shadow-xs border border-[#d5cbba] dark:border-zinc-700/60"
                  : "text-[#5c5549] dark:text-zinc-400 hover:text-[#1c1917] dark:hover:text-zinc-200"
              }`}
            >
              <span>System Maintained</span>
              <span
                className={`text-[10px] ${
                  policyTab === "system" ? "text-[#78716c] dark:text-zinc-300" : "text-[#78716c] dark:text-zinc-500"
                }`}
              >
                ({systemCount})
              </span>
            </button>
            <button
              type="button"
              onClick={() => handleTabChange("user")}
              className={`h-full px-2.5 rounded-md transition-all cursor-pointer flex items-center gap-1.5 text-[11px] leading-none ${
                policyTab === "user"
                  ? "bg-[#f5eedf] dark:bg-zinc-800 text-[#1c1917] dark:text-zinc-100 font-medium shadow-xs border border-[#d5cbba] dark:border-zinc-700/60"
                  : "text-[#5c5549] dark:text-zinc-400 hover:text-[#1c1917] dark:hover:text-zinc-200"
              }`}
            >
              <span>User Maintained</span>
              <span
                className={`text-[10px] ${
                  policyTab === "user" ? "text-[#78716c] dark:text-zinc-300" : "text-[#78716c] dark:text-zinc-500"
                }`}
              >
                ({userCount})
              </span>
            </button>
          </div>

          {/* Search Input & Refresh Button (Right-aligned on PC, full-width on mobile) */}
          <div className="flex items-center gap-2 w-full sm:w-auto">
            {/* Fuzzy Search Input */}
            <div className="relative flex-1 sm:w-64 md:w-72">
              <div className="absolute inset-y-0 left-0 pl-2.5 flex items-center pointer-events-none text-[#78716c] dark:text-zinc-500">
                <Search className="w-3.5 h-3.5 shrink-0" />
              </div>
              <input
                type="text"
                value={searchQuery}
                onChange={handleSearchChange}
                disabled={loadingPolicies}
                placeholder="Search policies..."
                autoCapitalize="none"
                autoCorrect="off"
                spellCheck="false"
                className="w-full pl-8 pr-8 py-1.5 rounded-lg bg-[#faf5ec] dark:bg-zinc-950 border border-[#d5cbba] dark:border-zinc-800 text-[#1c1917] dark:text-zinc-100 placeholder-[#8c8273] dark:placeholder-zinc-500 text-xs font-mono focus:outline-none focus:border-[#5c5549] dark:focus:border-zinc-300 focus:ring-1 focus:ring-[#5c5549]/30 dark:focus:ring-zinc-300/30 transition-colors disabled:opacity-50 h-[34px] shadow-xs"
              />
              {searchQuery && !loadingPolicies && (
                <button
                  type="button"
                  onClick={handleClearSearch}
                  className="absolute inset-y-0 right-0 pr-2.5 flex items-center text-[#78716c] hover:text-[#1c1917] dark:text-zinc-400 dark:hover:text-zinc-100 transition-colors cursor-pointer"
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
              className="px-3 py-1.5 rounded-lg bg-[#faf5ec] hover:bg-[#e2d9c7] text-[#5c5549] hover:text-[#1c1917] dark:bg-zinc-900 dark:hover:bg-zinc-800 dark:text-zinc-300 text-xs font-mono flex items-center gap-1.5 transition-colors cursor-pointer border border-[#d5cbba] dark:border-zinc-800 active:scale-95 shrink-0 h-[34px] shadow-xs"
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
          <div className="p-8 text-center rounded-xl panel border text-[#5c5549] dark:text-zinc-400 text-xs font-mono">
            <Loader2 className="w-5 h-5 animate-spin text-[#5c5549] dark:text-zinc-400 mx-auto mb-2" />
            <span>Loading tracked policies...</span>
          </div>
        ) : policies.length === 0 ? (
          <div className="p-8 text-center rounded-xl panel border space-y-2">
            <Database className="w-6 h-6 text-[#78716c] dark:text-zinc-600 mx-auto" />
            <p className="text-xs text-[#5c5549] dark:text-zinc-400 font-mono">
              No policies tracked yet
            </p>
            <p className="text-[11px] text-[#78716c] dark:text-zinc-500">
              Submit a public URL above to create your first version baseline.
            </p>
          </div>
        ) : tabPolicies.length === 0 ? (
          <div className="p-8 text-center rounded-xl panel border space-y-2 font-mono">
            <Database className="w-6 h-6 text-[#78716c] dark:text-zinc-600 mx-auto mb-1" />
            <p className="text-xs text-[#1c1917] dark:text-zinc-300">
              {policyTab === "user"
                ? "No user-maintained policies tracked yet"
                : "No system-maintained policies tracked yet"}
            </p>
            <p className="text-[11px] text-[#78716c] dark:text-zinc-500 max-w-sm mx-auto">
              {policyTab === "user"
                ? "Use the 'Paste Text' tab above to audit an internal agreement or bypass strict bot challenges."
                : "Submit a public URL above or discover verified company policies to begin tracking."}
            </p>
          </div>
        ) : filteredPolicies.length === 0 ? (
          <div className="p-8 text-center rounded-xl panel border border-[#d5cbba] dark:border-zinc-800 space-y-3 font-mono">
            <div className="w-10 h-10 rounded-full bg-[#faf5ec] dark:bg-zinc-900 border border-[#d5cbba] dark:border-zinc-800 flex items-center justify-center mx-auto text-[#78716c] dark:text-zinc-500">
              <Search className="w-4 h-4" />
            </div>
            <div className="space-y-1">
              <p className="text-xs text-[#1c1917] dark:text-zinc-300">
                No {policyTab === "user" ? "user-maintained" : "system-maintained"} policies match &ldquo;{searchQuery}&rdquo;
              </p>
              <p className="text-[11px] text-[#78716c] dark:text-zinc-500">
                Try searching by company name, URL, or agreement type.
              </p>
            </div>
            <button
              type="button"
              onClick={handleClearSearch}
              className="px-3 py-1.5 rounded-md bg-[#faf5ec] hover:bg-[#e2d9c7] text-[#1c1917] border border-[#d5cbba] dark:bg-zinc-900 dark:hover:bg-zinc-800 dark:text-zinc-300 dark:border-zinc-800 text-xs transition-colors cursor-pointer active:scale-95 shadow-2xs"
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
                  <thead className="bg-[#e5ddcf] dark:bg-zinc-950 border-b border-[#d5cbba] dark:border-zinc-800 text-[#5c5549] dark:text-zinc-400 uppercase tracking-wider text-[11px]">
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
                  <tbody className="divide-y divide-[#d5cbba]/60 dark:divide-zinc-800/80">
                    {paginatedPolicies.map((pol) => {
                      const formattedDate = formatLocalDate(
                        pol.last_checked_at,
                      );
                      const analysis = pol.latest_analysis;
                      const { score, level } = getRiskTier(analysis);
                      const isFb =
                        analysis?.model_id === "deterministic-fallback";

                      return (
                        <tr
                          key={pol.id}
                          className="hover:bg-[#e5ddcf]/50 dark:hover:bg-zinc-900/50 transition-colors"
                        >
                          <td className="py-3.5 pl-4 pr-3 text-left">
                            <div className="flex items-center gap-2">
                              <Link
                                to={`/policies/${pol.id}`}
                                className="font-medium text-[#1c1917] dark:text-zinc-100 hover:text-black dark:hover:text-white transition-colors block text-xs line-clamp-2"
                                title={pol.title || "Policy Document"}
                              >
                                {pol.title || "Policy Document"}
                              </Link>
                              {pol.provenance === "archive" ? (
                                <span className="shrink-0 px-1.5 py-0.5 rounded text-[10px] font-mono bg-blue-500/10 dark:bg-blue-950/40 border border-blue-300 dark:border-blue-800/60 text-blue-800 dark:text-blue-300">
                                  Archive
                                </span>
                              ) : null}
                            </div>
                          </td>
                          <td className="py-3.5 px-3 text-[#78716c] dark:text-zinc-500 text-left max-w-[180px] lg:max-w-xs truncate">
                            {pol.canonical_url?.startsWith("/") ? (
                              <Link
                                to={pol.canonical_url}
                                className="hover:text-[#1c1917] dark:hover:text-zinc-300 transition-colors inline-flex items-center gap-1.5 max-w-full text-[11px] truncate"
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
                                className="hover:text-[#1c1917] dark:hover:text-zinc-300 transition-colors inline-flex items-center gap-1.5 max-w-full text-[11px] truncate"
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
                                  level === "high"
                                    ? "bg-rose-500/10 dark:bg-rose-950/50 border border-rose-300 dark:border-rose-800/80 text-rose-800 dark:text-rose-300"
                                    : level === "elevated"
                                      ? "bg-amber-500/10 dark:bg-amber-950/50 border border-amber-300 dark:border-amber-800/80 text-amber-800 dark:text-amber-300"
                                      : level === "moderate"
                                        ? "bg-yellow-500/10 dark:bg-yellow-950/40 border border-yellow-300 dark:border-yellow-800/70 text-yellow-800 dark:text-yellow-300"
                                        : "bg-emerald-500/10 dark:bg-emerald-950/40 border border-emerald-300 dark:border-emerald-800/70 text-emerald-800 dark:text-emerald-300"
                                }`}
                              >
                                <span className="font-semibold">{score}</span>
                                <span className="text-[10px] text-[#78716c] dark:text-zinc-500 font-normal">
                                  /100
                                </span>
                                <span className="text-[#bfb4a0] dark:text-zinc-600 font-normal">
                                  ·
                                </span>
                                <span className="capitalize">
                                  {level ? `${level}` : "rated"}
                                </span>
                              </span>
                            ) : (
                              <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md text-[11px] font-mono text-[#5c5549] dark:text-zinc-400 bg-[#faf5ec] dark:bg-zinc-900 border border-[#d5cbba] dark:border-zinc-800 whitespace-nowrap">
                                <span>{isFb ? "Fallback" : "Pending"}</span>
                              </span>
                            )}
                          </td>
                          <td className="py-3.5 px-3 text-[#5c5549] dark:text-zinc-400 whitespace-nowrap text-left">
                            {formattedDate}
                          </td>
                          <td className="py-3.5 pr-4 pl-2 text-right whitespace-nowrap">
                            <Link
                              to={`/policies/${pol.id}`}
                              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-[#faf5ec] hover:bg-[#e2d9c7] text-[#5c5549] hover:text-[#1c1917] dark:bg-zinc-900 dark:hover:bg-zinc-800 dark:text-zinc-200 border border-[#d5cbba] dark:border-zinc-800 hover:border-[#bfb4a0] dark:hover:border-zinc-700 transition-colors text-xs active:scale-95 shadow-2xs"
                            >
                              <span>Inspect</span>
                              <ChevronRight className="w-3.5 h-3.5 text-[#78716c] dark:text-zinc-500" />
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
                const { score, level } = getRiskTier(analysis);
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
                        <div className="space-y-1 min-w-0 flex-1">
                          <Link
                            to={`/policies/${pol.id}`}
                            className="font-semibold text-[#1c1917] dark:text-zinc-100 hover:text-black dark:hover:text-white transition-colors text-[13px] sm:text-sm leading-snug break-words block"
                            title={pol.title || "Policy Document"}
                          >
                            {pol.title || "Policy Document"}
                          </Link>
                          {pol.provenance === "archive" ? (
                            <span className="inline-block px-1.5 py-0.5 rounded text-[10px] font-mono bg-blue-500/10 dark:bg-blue-950/40 border border-blue-300 dark:border-blue-800/60 text-blue-800 dark:text-blue-300">
                              Public Archive
                            </span>
                          ) : null}
                        </div>
                        <Link
                          to={`/policies/${pol.id}`}
                          className="text-[#78716c] dark:text-zinc-500 hover:text-[#1c1917] dark:hover:text-zinc-300 p-0.5 shrink-0 mt-0.5"
                          aria-label="Inspect policy"
                        >
                          <ChevronRight className="w-3.5 h-3.5" />
                        </Link>
                      </div>

                      <div className="text-[#78716c] dark:text-zinc-500 font-mono text-[11px] truncate">
                        {pol.canonical_url?.startsWith("/") ? (
                          <Link
                            to={pol.canonical_url}
                            className="truncate hover:text-[#1c1917] dark:hover:text-zinc-300 transition-colors block"
                            title={pol.canonical_url}
                          >
                            {pol.canonical_url}
                          </Link>
                        ) : (
                          <a
                            href={pol.canonical_url}
                            target="_blank"
                            rel="noreferrer"
                            className="truncate hover:text-[#1c1917] dark:hover:text-zinc-300 transition-colors inline-flex items-center gap-1 max-w-full"
                            title={pol.canonical_url}
                          >
                            <span className="truncate">{pol.canonical_url}</span>
                            <ExternalLink className="w-2.5 h-2.5 shrink-0 opacity-60" />
                          </a>
                        )}
                      </div>
                    </div>

                    {/* Bottom: Score pill + Date + Action Button */}
                    <div className="pt-3 mt-3 border-t border-[#d5cbba]/60 dark:border-zinc-800/80 space-y-2.5">
                      <div className="flex items-center justify-between gap-1">
                        {score !== null && score !== undefined ? (
                          <span
                            className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-md text-[11px] font-mono font-medium ${
                              level === "high"
                                ? "bg-rose-500/10 dark:bg-rose-950/50 border border-rose-300 dark:border-rose-800/80 text-rose-800 dark:text-rose-300"
                                : level === "elevated"
                                  ? "bg-amber-500/10 dark:bg-amber-950/50 border border-amber-300 dark:border-amber-800/80 text-amber-800 dark:text-amber-300"
                                  : level === "moderate"
                                    ? "bg-yellow-500/10 dark:bg-yellow-950/40 border border-yellow-300 dark:border-yellow-800/70 text-yellow-800 dark:text-yellow-300"
                                    : "bg-emerald-500/10 dark:bg-emerald-950/40 border border-emerald-300 dark:border-emerald-800/70 text-emerald-800 dark:text-emerald-300"
                            }`}
                          >
                            <span>{score}</span>
                            <span className="text-[#78716c] dark:text-zinc-500 font-normal">/100</span>
                          </span>
                        ) : (
                          <span className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded-md text-[11px] font-mono text-[#5c5549] dark:text-zinc-400 bg-[#faf5ec] dark:bg-zinc-900 border border-[#d5cbba] dark:border-zinc-800">
                            <span>{isFb ? "Fallback" : "Pending"}</span>
                          </span>
                        )}

                        <span
                          className="text-[11px] font-mono text-[#78716c] dark:text-zinc-500 flex items-center gap-1"
                          title={formattedDate}
                        >
                          <Clock className="w-3 h-3 text-[#78716c] dark:text-zinc-600 shrink-0" />
                          <span>{shortDate}</span>
                        </span>
                      </div>

                      <Link
                        to={`/policies/${pol.id}`}
                        className="w-full py-2 px-3 rounded-lg bg-[#faf5ec] hover:bg-[#e2d9c7] active:bg-[#ded6c6] dark:bg-zinc-900 dark:hover:bg-zinc-850 dark:active:bg-zinc-800 border border-[#d5cbba] dark:border-zinc-800 text-[#5c5549] dark:text-zinc-200 text-xs font-mono font-medium flex items-center justify-center gap-1 active:scale-[0.98] transition-all shadow-2xs"
                      >
                        <span>Inspect</span>
                        <ChevronRight className="w-3.5 h-3.5 text-[#78716c] dark:text-zinc-400" />
                      </Link>
                    </div>
                  </div>
                );
              })}
            </div>

            {/* Pagination Controls - Centered cleanly without an outside box */}
            {filteredPolicies.length > 0 && (
              <div className="flex flex-col sm:flex-row items-center justify-center gap-4 sm:gap-6 pt-3 pb-1 text-xs font-mono">
                <div className="text-[#5c5549] dark:text-zinc-500 text-center sm:text-left">
                  <span>
                    Showing{" "}
                    {startIndex + 1 === endIndex ? (
                      <span className="text-[#1c1917] dark:text-zinc-300 font-semibold">{endIndex}</span>
                    ) : (
                      <>
                        <span className="text-[#1c1917] dark:text-zinc-300 font-semibold">{startIndex + 1}</span>
                        &ndash;
                        <span className="text-[#1c1917] dark:text-zinc-300 font-semibold">{endIndex}</span>
                      </>
                    )}{" "}
                    of{" "}
                    <span className="text-[#1c1917] dark:text-zinc-300 font-semibold">
                      {filteredPolicies.length}
                    </span>{" "}
                    {filteredPolicies.length === 1 ? "policy" : "policies"}
                  </span>
                  {searchQuery && (
                    <span className="text-[#78716c] dark:text-zinc-500 text-[11px] block sm:inline sm:ml-1.5">
                      (filtered from {policies.length} total)
                    </span>
                  )}
                </div>

                <div className="flex items-center gap-1 sm:gap-1.5">
                  <button
                    type="button"
                    onClick={() => handlePageChange(Math.max(1, safeCurrentPage - 1))}
                    disabled={safeCurrentPage <= 1}
                    className="px-2.5 py-1.5 rounded-md bg-[#faf5ec] hover:bg-[#e2d9c7] text-[#5c5549] hover:text-[#1c1917] dark:bg-zinc-900 dark:hover:bg-zinc-850 dark:active:bg-zinc-800 dark:text-zinc-300 dark:hover:text-white border border-[#d5cbba] dark:border-zinc-800 text-xs font-mono transition-colors cursor-pointer active:scale-95 disabled:opacity-40 disabled:cursor-not-allowed flex items-center gap-1 shadow-2xs"
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
                            ? "bg-[#1c1917] text-[#faf5ec] dark:bg-zinc-100 dark:text-zinc-950 font-bold shadow-xs border border-[#1c1917] dark:border-transparent"
                            : "bg-[#faf5ec] hover:bg-[#e2d9c7] text-[#5c5549] hover:text-[#1c1917] dark:bg-zinc-900 dark:hover:bg-zinc-850 dark:text-zinc-400 dark:hover:text-zinc-200 border border-[#d5cbba] dark:border-zinc-800 shadow-2xs"
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
                    className="px-2.5 py-1.5 rounded-md bg-[#faf5ec] hover:bg-[#e2d9c7] text-[#5c5549] hover:text-[#1c1917] dark:bg-zinc-900 dark:hover:bg-zinc-850 dark:active:bg-zinc-800 dark:text-zinc-300 dark:hover:text-white border border-[#d5cbba] dark:border-zinc-800 text-xs font-mono transition-colors cursor-pointer active:scale-95 disabled:opacity-40 disabled:cursor-not-allowed flex items-center gap-1 shadow-2xs"
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
