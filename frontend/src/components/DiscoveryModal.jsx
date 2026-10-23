import React, { useState } from 'react';
import { X, Search, ExternalLink, Loader2, AlertCircle } from 'lucide-react';
import { api } from '../lib/api';

export default function DiscoveryModal({ isOpen, onClose, onSelectUrl }) {
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);
  const [error, setError] = useState('');

  if (!isOpen) return null;

  const handleSearch = async (e) => {
    e.preventDefault();
    const clean = query.trim();
    if (!clean) return;

    if (clean.length < 2) {
      setError('Please enter at least 2 characters to search for a company.');
      return;
    }

    setLoading(true);
    setError('');
    setResults(null);

    try {
      const data = await api.discoverPolicyUrls(clean);
      setResults(data);
      if (!data.candidates || data.candidates.length === 0) {
        setError('No candidate policy links found. Try entering the URL directly.');
      }
    } catch (err) {
      setError(err.message || 'Discovery search failed.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-end sm:items-center justify-center p-0 sm:p-4 bg-black/80 backdrop-blur-sm">
      <div className="relative w-full max-w-lg bg-[#121215] rounded-t-2xl sm:rounded-xl p-4 sm:p-5 border border-zinc-800 shadow-2xl text-zinc-100 max-h-[88vh] sm:max-h-[85vh] flex flex-col">
        {/* Close Button */}
        <button
          onClick={onClose}
          className="absolute top-3.5 right-3.5 p-2 rounded-lg text-zinc-400 hover:text-zinc-100 hover:bg-zinc-800 transition-colors cursor-pointer min-h-[40px] min-w-[40px] flex items-center justify-center active:scale-95"
          aria-label="Close modal"
        >
          <X className="w-4 h-4" />
        </button>

        {/* Header */}
        <div className="mb-3.5 pr-8">
          <h3 className="text-sm sm:text-base font-semibold text-zinc-100">Company Policy Lookup</h3>
          <p className="text-xs text-zinc-400">Search for candidate Terms of Service and Privacy Policy URLs</p>
        </div>

        {/* Input */}
        <form onSubmit={handleSearch} className="mb-3">
          <div className="flex gap-2">
            <div className="relative flex-1">
              <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-zinc-500 pointer-events-none" />
              <input
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Company name (e.g. Spotify, Discord)"
                className="w-full pl-9 pr-3 py-2.5 sm:py-2 rounded-lg bg-zinc-950 border border-zinc-800 text-zinc-100 placeholder-zinc-500 text-base sm:text-xs focus:outline-none focus:border-zinc-500 font-mono min-h-[42px] sm:min-h-0"
              />
            </div>
            <button
              type="submit"
              disabled={loading || !query.trim()}
              className="px-4 py-2.5 sm:py-2 rounded-lg bg-zinc-100 hover:bg-white text-zinc-950 font-medium text-xs font-mono transition-all disabled:opacity-50 cursor-pointer min-h-[42px] sm:min-h-0 flex items-center justify-center active:scale-95 shrink-0"
            >
              {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : 'Search'}
            </button>
          </div>
        </form>

        {/* Error notice */}
        {error && (
          <div className="p-2.5 mb-3 rounded-md bg-amber-950/30 border border-amber-900/50 text-amber-300 text-xs font-mono flex items-start gap-2 break-words">
            <AlertCircle className="w-3.5 h-3.5 shrink-0 mt-0.5" />
            <span>{error}</span>
          </div>
        )}

        {/* Candidates list */}
        {results?.candidates && results.candidates.length > 0 && (
          <div className="space-y-2 flex-1 overflow-y-auto pr-1 min-h-0">
            {results.candidates.map((cand, idx) => (
              <div
                key={idx}
                className="p-3 sm:p-3 rounded-lg bg-zinc-950 border border-zinc-800 hover:border-zinc-700 transition-all flex flex-col justify-between gap-1.5 text-left"
              >
                <div className="flex items-start justify-between gap-2">
                  <span className="text-xs font-medium text-zinc-200 leading-snug">
                    {cand.title}
                  </span>
                  <button
                    onClick={() => {
                      onSelectUrl(cand.url);
                      onClose();
                    }}
                    className="shrink-0 text-xs sm:text-[11px] font-mono px-3 py-1.5 sm:px-2.5 sm:py-1 rounded bg-zinc-800 hover:bg-zinc-750 active:bg-zinc-700 text-zinc-200 transition-colors cursor-pointer min-h-[34px] sm:min-h-0 flex items-center active:scale-95"
                  >
                    Select
                  </button>
                </div>
                {cand.snippet && (
                  <p className="text-xs sm:text-[11px] text-zinc-400 line-clamp-2 leading-relaxed">{cand.snippet}</p>
                )}
                <span className="text-[11px] font-mono text-zinc-500 truncate flex items-center gap-1">
                  <ExternalLink className="w-3 h-3 shrink-0" />
                  <span className="truncate">{cand.url}</span>
                </span>
              </div>
            ))}
          </div>
        )}

        <div className="mt-3 pt-3 border-t border-zinc-800/80 text-[11px] text-zinc-500 font-mono leading-relaxed">
          Discovered via verified directory and direct website inspection. All selected URLs undergo strict multi-hop SSRF validation prior to extraction.
        </div>
      </div>
    </div>
  );
}
