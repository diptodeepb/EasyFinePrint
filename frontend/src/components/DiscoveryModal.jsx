import React, { useState } from 'react';
import { X, Search, ExternalLink, Loader2, AlertCircle, Check } from 'lucide-react';
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
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm">
      <div className="relative w-full max-w-lg bg-[#121215] rounded-xl p-5 border border-zinc-800 shadow-xl text-zinc-100">
        {/* Close Button */}
        <button
          onClick={onClose}
          className="absolute top-4 right-4 p-1 rounded-md text-zinc-500 hover:text-zinc-200 hover:bg-zinc-800 transition-colors cursor-pointer"
        >
          <X className="w-4 h-4" />
        </button>

        {/* Header */}
        <div className="mb-4">
          <h3 className="text-sm font-semibold text-zinc-100">Company Policy Lookup</h3>
          <p className="text-xs text-zinc-400">Search for candidate Terms of Service and Privacy Policy URLs</p>
        </div>

        {/* Input */}
        <form onSubmit={handleSearch} className="mb-3">
          <div className="flex gap-2">
            <div className="relative flex-1">
              <Search className="w-3.5 h-3.5 absolute left-3 top-1/2 -translate-y-1/2 text-zinc-500" />
              <input
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Company name (e.g. Spotify, Discord, Figma)"
                className="w-full pl-9 pr-3 py-2 rounded-lg bg-zinc-950 border border-zinc-800 text-zinc-100 placeholder-zinc-500 text-xs focus:outline-none focus:border-zinc-500 font-mono"
              />
            </div>
            <button
              type="submit"
              disabled={loading || !query.trim()}
              className="px-4 py-2 rounded-lg bg-zinc-100 hover:bg-white text-zinc-950 font-medium text-xs transition-colors disabled:opacity-50 cursor-pointer"
            >
              {loading ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : 'Search'}
            </button>
          </div>
        </form>

        {/* Quota info */}
        {results?.quota_remaining !== undefined && (
          <div className="text-[11px] font-mono text-zinc-400 mb-3 flex items-center gap-1.5">
            <Check className="w-3 h-3 text-emerald-400" />
            <span>Monthly quota remaining: {results.quota_remaining} searches</span>
            {results.cached && <span className="text-zinc-500">(cached)</span>}
          </div>
        )}

        {/* Error notice */}
        {error && (
          <div className="p-2.5 mb-3 rounded-md bg-amber-950/30 border border-amber-900/50 text-amber-300 text-xs font-mono flex items-center gap-2">
            <AlertCircle className="w-3.5 h-3.5 shrink-0" />
            <span>{error}</span>
          </div>
        )}

        {/* Candidates list */}
        {results?.candidates && results.candidates.length > 0 && (
          <div className="space-y-2 max-h-60 overflow-y-auto pr-1">
            {results.candidates.map((cand, idx) => (
              <div
                key={idx}
                className="p-3 rounded-lg bg-zinc-950 border border-zinc-800 hover:border-zinc-700 transition-all flex flex-col justify-between gap-1 text-left"
              >
                <div className="flex items-start justify-between gap-2">
                  <span className="text-xs font-medium text-zinc-200">
                    {cand.title}
                  </span>
                  <button
                    onClick={() => {
                      onSelectUrl(cand.url);
                      onClose();
                    }}
                    className="shrink-0 text-[11px] font-mono px-2 py-0.5 rounded bg-zinc-800 hover:bg-zinc-700 text-zinc-200 transition-colors cursor-pointer"
                  >
                    Select
                  </button>
                </div>
                {cand.snippet && (
                  <p className="text-[11px] text-zinc-400 line-clamp-2">{cand.snippet}</p>
                )}
                <span className="text-[11px] font-mono text-zinc-500 truncate flex items-center gap-1">
                  <ExternalLink className="w-3 h-3" />
                  {cand.url}
                </span>
              </div>
            ))}
          </div>
        )}

        <div className="mt-3 pt-3 border-t border-zinc-800 text-[11px] text-zinc-500 font-mono">
          Discovery uses SerpApi fallback with rate capping. Selected candidate URLs undergo full SSRF validation before extraction.
        </div>
      </div>
    </div>
  );
}
