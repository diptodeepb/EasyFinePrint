import React, { useState, useEffect, useRef } from 'react';
import { X, Search, ExternalLink, Loader2, AlertCircle, ChevronLeft, ChevronRight, CheckCircle2, Globe } from 'lucide-react';
import { api } from '../lib/api';

const PAGE_SIZE = 5;

export default function DiscoveryModal({ isOpen, onClose, onSelectUrl }) {
  const [query, setQuery] = useState('');
  const [activeQuery, setActiveQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [elapsed, setElapsed] = useState(0);
  const [results, setResults] = useState(null);
  const [error, setError] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const modalRef = useRef(null);
  const isBackdropMouseDown = useRef(false);
  const isBackdropTouchStart = useRef(false);

  // Close modal on Escape key
  useEffect(() => {
    if (!isOpen) return;
    const handleKeyDown = (e) => {
      if (e.key === 'Escape') {
        onClose();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, onClose]);

  // Lock body scroll while modal is open
  useEffect(() => {
    if (!isOpen) return;
    const originalOverflow = document.body.style.overflow;
    document.body.style.overflow = 'hidden';
    return () => {
      document.body.style.overflow = originalOverflow;
    };
  }, [isOpen]);

  useEffect(() => {
    if (!loading) {
      return;
    }
    const start = Date.now();
    const timer = setInterval(() => {
      setElapsed(Math.floor((Date.now() - start) / 1000));
    }, 400);
    return () => {
      clearInterval(timer);
      setElapsed(0);
    };
  }, [loading]);

  if (!isOpen) return null;

  const handleSearch = async (e) => {
    e?.preventDefault();
    const clean = query.trim();
    if (!clean) return;

    if (clean.length < 2) {
      setError('Please enter at least 2 characters to search for a company.');
      return;
    }

    setActiveQuery(clean);
    setLoading(true);
    setError('');
    setResults(null);
    setCurrentPage(1);

    try {
      const data = await api.discoverPolicyUrls(clean);
      setResults(data);
      if (!data.candidates || data.candidates.length === 0) {
        setError('No candidate policy links found. Try entering the URL directly or verify the company name.');
      }
    } catch (err) {
      let msg = err?.message || 'Discovery search failed.';
      if (/failed to fetch/i.test(msg) || /unable to connect/i.test(msg) || /network/i.test(msg) || /load failed/i.test(msg)) {
        msg = 'Unable to connect to the policy discovery service. Please check your connection or enter the URL directly.';
      } else {
        msg = msg.replace(/https?:\/\/[^\s/$.?#].[^\s]*/gi, '').trim();
      }
      setError(msg || 'Discovery search failed. Please try entering the URL directly.');
    } finally {
      setLoading(false);
    }
  };

  const getProgressPercent = (sec) => {
    if (sec <= 0) return 18;
    if (sec === 1) return 35;
    if (sec === 2) return 52;
    if (sec === 3) return 66;
    if (sec === 4) return 76;
    if (sec === 5) return 84;
    if (sec === 6) return 89;
    if (sec === 7) return 93;
    return Math.min(96, 93 + (sec - 7) * 0.5);
  };

  const getStageMessage = (sec, q) => {
    const target = q ? `"${q}"` : 'company';
    if (sec < 2) return `Checking verified directory & aliases for ${target}...`;
    if (sec < 4) return `Probing candidate domains & top-level TLDs (.com, .io, .ai)...`;
    if (sec < 6) return `Inspecting homepage DOM & extracting footer legal links...`;
    if (sec < 8) return `Verifying canonical endpoints (/terms, /privacy, /legal)...`;
    return `Querying search fallback & enforcing SSRF safety checks...`;
  };

  const allCandidates = results?.candidates || [];
  const totalItems = allCandidates.length;
  const totalPages = Math.ceil(totalItems / PAGE_SIZE);
  const startIndex = (currentPage - 1) * PAGE_SIZE;
  const paginatedCandidates = allCandidates.slice(startIndex, startIndex + PAGE_SIZE);

  const handlePrevPage = () => {
    setCurrentPage((prev) => Math.max(1, prev - 1));
  };

  const handleNextPage = () => {
    setCurrentPage((prev) => Math.min(totalPages, prev + 1));
  };

  return (
    <div
      className="fixed inset-0 z-50 flex items-end sm:items-center justify-center p-0 sm:p-4 bg-black/60 dark:bg-black/80 backdrop-blur-sm animate-in fade-in duration-200"
      onMouseDown={(e) => {
        isBackdropMouseDown.current = e.target === e.currentTarget;
      }}
      onClick={(e) => {
        if (
          isBackdropMouseDown.current &&
          (e.target === e.currentTarget || (modalRef.current && !modalRef.current.contains(e.target)))
        ) {
          e.preventDefault();
          e.stopPropagation();
          onClose();
        }
        isBackdropMouseDown.current = false;
      }}
      onTouchStart={(e) => {
        isBackdropTouchStart.current = e.target === e.currentTarget;
      }}
      onTouchEnd={(e) => {
        if (
          isBackdropTouchStart.current &&
          (e.target === e.currentTarget || (modalRef.current && !modalRef.current.contains(e.target)))
        ) {
          e.preventDefault();
          e.stopPropagation();
          onClose();
        }
        isBackdropTouchStart.current = false;
      }}
    >
      <div
        ref={modalRef}
        onClick={(e) => e.stopPropagation()}
        className="relative w-full max-w-lg bg-[#f5eedf] dark:bg-[#121215] rounded-t-2xl sm:rounded-xl p-4 sm:p-5 border border-[#d5cbba] dark:border-zinc-800 shadow-2xl text-[#1c1917] dark:text-zinc-100 max-h-[88vh] sm:max-h-[85vh] flex flex-col"
      >
        {/* Close Button */}
        <button
          onClick={onClose}
          className="absolute top-3.5 right-3.5 p-2 rounded-lg text-[#5c5549] hover:text-[#1c1917] hover:bg-[#ded6c6]/60 dark:text-zinc-400 dark:hover:text-zinc-100 dark:hover:bg-zinc-800 transition-colors cursor-pointer min-h-[40px] min-w-[40px] flex items-center justify-center active:scale-95"
          aria-label="Close modal"
        >
          <X className="w-4 h-4" />
        </button>

        {/* Header */}
        <div className="mb-3.5 pr-8">
          <h3 className="text-sm sm:text-base font-semibold text-[#1c1917] dark:text-zinc-100 flex items-center gap-2">
            <span>Company Policy Directory &amp; Auto-Discovery</span>
          </h3>
          <p className="text-xs text-[#5c5549] dark:text-zinc-400">
            Search 249+ verified platforms (500+ legal documents) or auto-find policies dynamically for any company
          </p>
        </div>

        {/* Input */}
        <form onSubmit={handleSearch} className="mb-3">
          <div className="flex gap-2">
            <div className="relative flex-1">
              <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-[#78716c] dark:text-zinc-500 pointer-events-none" />
              <input
                type="text"
                value={query}
                onChange={(e) => {
                  setQuery(e.target.value);
                  if (error) setError('');
                }}
                disabled={loading}
                placeholder="Company name or domain (e.g. Spotify, Linear, Stripe)"
                className="w-full pl-9 pr-9 py-2.5 sm:py-2 rounded-lg bg-[#faf5ec] dark:bg-zinc-950 border border-[#d5cbba] dark:border-zinc-800 text-[#1c1917] dark:text-zinc-100 placeholder-[#78716c] dark:placeholder-zinc-500 text-base sm:text-xs focus:outline-none focus:border-[#1c1917] dark:focus:border-zinc-500 font-mono min-h-[42px] sm:min-h-0 disabled:opacity-50"
              />
              {query && !loading && (
                <button
                  type="button"
                  onClick={() => {
                    setQuery('');
                    if (error) setError('');
                  }}
                  className="absolute inset-y-0 right-0 pr-3 flex items-center text-[#78716c] hover:text-[#1c1917] dark:text-zinc-400 dark:hover:text-zinc-100 transition-colors cursor-pointer"
                  title="Clear search query"
                  aria-label="Clear search query"
                >
                  <X className="w-4 h-4 shrink-0" />
                </button>
              )}
            </div>
            <button
              type="submit"
              disabled={loading || !query.trim()}
              className="px-4 py-2.5 sm:py-2 rounded-lg bg-[#1c1917] hover:bg-[#292524] text-[#faf5ec] dark:bg-zinc-100 dark:hover:bg-white dark:text-zinc-950 font-medium text-xs font-mono transition-all disabled:opacity-50 cursor-pointer min-h-[42px] sm:min-h-0 flex items-center justify-center active:scale-95 shrink-0"
            >
              {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : 'Search'}
            </button>
          </div>
        </form>

        {/* Realistic Progress Bar during Discovery */}
        {loading && (
          <div className="p-3.5 mb-3 rounded-lg bg-[#faf5ec] dark:bg-zinc-950 border border-[#d5cbba] dark:border-zinc-800 space-y-2.5 font-mono text-xs">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-1 text-[#1c1917] dark:text-zinc-300">
              <span className="flex items-start sm:items-center gap-2">
                <Loader2 className="w-3.5 h-3.5 animate-spin text-[#5c5549] dark:text-zinc-400 shrink-0 mt-0.5 sm:mt-0" />
                <span className="leading-tight">
                  {getStageMessage(elapsed, activeQuery)}
                </span>
              </span>
              <span className="text-[#1c1917] dark:text-zinc-400 font-semibold self-end sm:self-auto shrink-0 bg-[#ece5d8] dark:bg-zinc-900 px-2 py-0.5 rounded border border-[#d5cbba] dark:border-zinc-800">
                {elapsed}s
              </span>
            </div>
            <div className="flex flex-col xs:flex-row xs:items-center justify-between gap-1 text-[11px] text-[#78716c] dark:text-zinc-500">
              <span>Multi-stage policy discovery engine</span>
              <span>
                {elapsed < 8 ? 'Realistic estimate: ~3-6s' : 'Deep network verification in progress...'}
              </span>
            </div>
            <div className="w-full bg-[#ece5d8] dark:bg-zinc-900 h-1.5 rounded-full overflow-hidden border border-[#d5cbba] dark:border-zinc-800/80">
              <div
                className="bg-[#1c1917] dark:bg-zinc-300 h-full transition-all duration-300"
                style={{ width: `${getProgressPercent(elapsed)}%` }}
              />
            </div>
          </div>
        )}

        {/* Error notice */}
        {!loading && error && (
          <div className="p-2.5 mb-3 rounded-md bg-amber-500/10 dark:bg-amber-950/30 border border-amber-500/30 dark:border-amber-900/50 text-amber-900 dark:text-amber-300 text-xs font-mono flex items-start gap-2 break-words">
            <AlertCircle className="w-3.5 h-3.5 shrink-0 mt-0.5" />
            <span>{error}</span>
          </div>
        )}

        {/* Candidates list with pagination */}
        {!loading && totalItems > 0 && (
          <div className="space-y-2 flex-1 overflow-y-auto pr-1 min-h-0">
            {paginatedCandidates.map((cand, idx) => {
              const isKnown = cand.source === 'known_directory';
              return (
                <div
                  key={`${cand.url}-${idx}`}
                  className="p-3 sm:p-3 rounded-lg bg-[#faf5ec] dark:bg-zinc-950 border border-[#d5cbba] dark:border-zinc-800 hover:border-[#bfb4a0] dark:hover:border-zinc-700 transition-all flex flex-col justify-between gap-1.5 text-left"
                >
                  <div className="flex items-start justify-between gap-2">
                    <div className="min-w-0 flex-1">
                      <div className="flex items-center gap-1.5 flex-wrap">
                        <span className="text-xs font-medium text-[#1c1917] dark:text-zinc-200 leading-snug break-words">
                          {cand.title}
                        </span>
                        {isKnown ? (
                          <span className="inline-flex items-center gap-1 px-1.5 py-0.2 rounded text-[10px] font-mono bg-emerald-500/10 dark:bg-emerald-950/50 text-emerald-800 dark:text-emerald-400 border border-emerald-500/30 dark:border-emerald-900/40">
                            <CheckCircle2 className="w-2.5 h-2.5" />
                            <span>Verified</span>
                          </span>
                        ) : (
                          <span className="inline-flex items-center gap-1 px-1.5 py-0.2 rounded text-[10px] font-mono bg-sky-500/10 dark:bg-sky-950/50 text-sky-800 dark:text-sky-400 border border-sky-500/30 dark:border-sky-900/40">
                            <Globe className="w-2.5 h-2.5" />
                            <span>Discovered</span>
                          </span>
                        )}
                      </div>
                    </div>
                    <button
                      onClick={() => {
                        onSelectUrl(cand.url);
                        onClose();
                      }}
                      className="shrink-0 text-xs sm:text-[11px] font-mono px-3 py-1.5 sm:px-2.5 sm:py-1 rounded bg-[#ece5d8] hover:bg-[#ded6c6] active:bg-[#d5cbba] text-[#1c1917] border border-[#d5cbba] dark:bg-zinc-800 dark:hover:bg-zinc-750 dark:active:bg-zinc-700 dark:text-zinc-200 dark:border-transparent transition-colors cursor-pointer min-h-[34px] sm:min-h-0 flex items-center active:scale-95"
                    >
                      Select
                    </button>
                  </div>
                  {cand.snippet && (
                    <p className="text-xs sm:text-[11px] text-[#5c5549] dark:text-zinc-400 line-clamp-2 leading-relaxed">
                      {cand.snippet}
                    </p>
                  )}
                  <a
                    href={cand.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    onClick={(e) => e.stopPropagation()}
                    className="text-[11px] font-mono text-[#5c5549] hover:text-[#1c1917] dark:text-zinc-400 dark:hover:text-zinc-200 transition-colors truncate flex items-center gap-1.5 w-fit max-w-full hover:underline underline-offset-2 cursor-pointer group/url"
                    title={`Open ${cand.url} in new tab`}
                  >
                    <ExternalLink className="w-3 h-3 shrink-0 text-[#78716c] group-hover/url:text-[#1c1917] dark:text-zinc-500 dark:group-hover/url:text-zinc-300 transition-colors" />
                    <span className="truncate">{cand.url}</span>
                  </a>
                </div>
              );
            })}
          </div>
        )}

        {/* Pagination Navigation Bar */}
        {!loading && totalItems > PAGE_SIZE && (
          <div className="mt-2.5 pt-2 border-t border-[#d5cbba] dark:border-zinc-800/80 flex items-center justify-between text-xs font-mono text-[#5c5549] dark:text-zinc-400 shrink-0">
            <span className="text-[11px] text-[#78716c] dark:text-zinc-500">
              Showing {startIndex + 1}&ndash;{Math.min(startIndex + PAGE_SIZE, totalItems)} of {totalItems} policies
            </span>
            <div className="flex items-center gap-1.5">
              <button
                type="button"
                onClick={handlePrevPage}
                disabled={currentPage === 1}
                className="px-2 py-1 rounded bg-[#ece5d8] border border-[#d5cbba] text-[#1c1917] hover:bg-[#ded6c6] active:bg-[#d5cbba] dark:bg-zinc-900 dark:border-zinc-800 dark:text-zinc-300 dark:hover:bg-zinc-800 dark:active:bg-zinc-750 disabled:opacity-40 disabled:cursor-not-allowed transition-all flex items-center gap-1 text-[11px] cursor-pointer"
                aria-label="Previous page"
              >
                <ChevronLeft className="w-3 h-3" />
                <span>Prev</span>
              </button>
              <span className="px-2 py-0.5 rounded bg-[#ece5d8] border border-[#d5cbba] text-[11px] text-[#5c5549] dark:bg-zinc-900 dark:border-zinc-800 dark:text-zinc-400">
                {currentPage} / {totalPages}
              </span>
              <button
                type="button"
                onClick={handleNextPage}
                disabled={currentPage === totalPages}
                className="px-2 py-1 rounded bg-[#ece5d8] border border-[#d5cbba] text-[#1c1917] hover:bg-[#ded6c6] active:bg-[#d5cbba] dark:bg-zinc-900 dark:border-zinc-800 dark:text-zinc-300 dark:hover:bg-zinc-800 dark:active:bg-zinc-750 disabled:opacity-40 disabled:cursor-not-allowed transition-all flex items-center gap-1 text-[11px] cursor-pointer"
                aria-label="Next page"
              >
                <span>Next</span>
                <ChevronRight className="w-3 h-3" />
              </button>
            </div>
          </div>
        )}

        {/* Security & Verification Footer */}
        <div className="mt-3 pt-2.5 border-t border-[#d5cbba] dark:border-zinc-800/80 text-[11px] text-[#78716c] dark:text-zinc-500 font-mono leading-relaxed shrink-0">
          Discovered via verified directory &amp; direct legal endpoint inspection. All candidate URLs undergo strict multi-hop SSRF validation prior to extraction.
        </div>
      </div>
    </div>
  );
}
