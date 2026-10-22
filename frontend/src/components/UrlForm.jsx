import React, { useState, useEffect } from 'react';
import { ArrowRight, Loader2, Globe, Search } from 'lucide-react';

const SAMPLE_POLICIES = [
  { name: 'GitHub Terms', url: 'https://docs.github.com/en/site-policy/github-terms/github-terms-of-service' },
  { name: 'Discord Terms', url: 'https://discord.com/terms' },
  { name: 'Reddit Agreement', url: 'https://redditinc.com/policies/user-agreement' },
  { name: 'Spotify Terms', url: 'https://www.spotify.com/legal/end-user-agreement/' },
];

export default function UrlForm({ onAnalyze, loading, onOpenDiscovery }) {
  const [url, setUrl] = useState('');
  const [error, setError] = useState('');
  const [elapsed, setElapsed] = useState(0);

  useEffect(() => {
    let timer;
    if (loading) {
      setElapsed(0);
      timer = setInterval(() => {
        setElapsed((prev) => prev + 1);
      }, 1000);
    } else {
      setElapsed(0);
    }
    return () => clearInterval(timer);
  }, [loading]);

  const handleSubmit = (e) => {
    e.preventDefault();
    setError('');

    const clean = url.trim();
    if (!clean) {
      setError('Enter a policy URL');
      return;
    }

    if (!clean.startsWith('http://') && !clean.startsWith('https://')) {
      setError('URL must start with http:// or https://');
      return;
    }

    onAnalyze(clean);
  };

  const handleSelectSample = (sampleUrl) => {
    setUrl(sampleUrl);
    setError('');
  };

  return (
    <div className="w-full">
      <div className="panel rounded-xl p-5 sm:p-6 shadow-sm">
        <form onSubmit={handleSubmit} className="space-y-3">
          <div className="flex flex-col sm:flex-row gap-2">
            <div className="relative flex-1">
              <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-zinc-500">
                <Globe className="w-4 h-4" />
              </div>
              <input
                type="url"
                value={url}
                onChange={(e) => {
                  setUrl(e.target.value);
                  if (error) setError('');
                }}
                disabled={loading}
                placeholder="Paste Terms of Service or Privacy Policy URL..."
                className="w-full pl-10 pr-3 py-2.5 rounded-lg bg-zinc-950 border border-zinc-800 text-zinc-100 placeholder-zinc-500 text-sm focus:outline-none focus:border-zinc-500 transition-colors disabled:opacity-50 font-mono text-xs sm:text-sm"
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="px-5 py-2.5 rounded-lg bg-zinc-100 hover:bg-white text-zinc-950 font-medium text-xs sm:text-sm flex items-center justify-center gap-1.5 transition-colors disabled:opacity-50 cursor-pointer shrink-0"
            >
              {loading ? (
                <>
                  <Loader2 className="w-3.5 h-3.5 animate-spin" />
                  <span>Processing...</span>
                </>
              ) : (
                <>
                  <span>Analyze Policy</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </>
              )}
            </button>
          </div>

          {loading && (
            <div className="p-3.5 rounded-lg bg-zinc-950 border border-zinc-800 space-y-2 font-mono text-xs">
              <div className="flex items-center justify-between text-zinc-300">
                <span className="flex items-center gap-2">
                  <Loader2 className="w-3.5 h-3.5 animate-spin text-zinc-400 shrink-0" />
                  <span>
                    {elapsed < 4
                      ? 'Fetching document & validating security rules...'
                      : elapsed < 8
                      ? 'Extracting text & calculating baseline hash...'
                      : elapsed < 30
                      ? 'Evaluating policy clauses with Gemma 4...'
                      : 'Verifying verbatim citations against source text...'}
                  </span>
                </span>
                <span className="text-zinc-400 font-semibold">{elapsed}s</span>
              </div>
              <div className="flex items-center justify-between text-[11px] text-zinc-500">
                <span>Single-pass clause evaluation (Gemma 4)</span>
                <span>
                  {elapsed < 30 ? 'Realistic estimate: ~20-30s' : 'Deep verification in progress...'}
                </span>
              </div>
              <div className="w-full bg-zinc-900 h-1.5 rounded-full overflow-hidden">
                <div
                  className="bg-zinc-300 h-full transition-all duration-300"
                  style={{ width: `${Math.min(96, Math.max(8, (elapsed / 35) * 100))}%` }}
                />
              </div>
            </div>
          )}

          {error && (
            <div className="p-2.5 rounded-md bg-rose-950/30 border border-rose-900/50 text-rose-300 text-xs font-mono">
              {error}
            </div>
          )}

          {/* Quick samples and discovery */}
          <div className="pt-2 flex flex-col sm:flex-row sm:items-center justify-between gap-2 text-xs text-zinc-400">
            <div className="flex items-center flex-wrap gap-1.5">
              <span className="text-zinc-500 text-[11px]">Samples:</span>
              {SAMPLE_POLICIES.map((item) => (
                <button
                  key={item.name}
                  type="button"
                  onClick={() => handleSelectSample(item.url)}
                  disabled={loading}
                  className="px-2 py-0.5 rounded bg-zinc-900 hover:bg-zinc-800 text-zinc-300 transition-colors border border-zinc-800 cursor-pointer text-[11px]"
                >
                  {item.name}
                </button>
              ))}
            </div>

            <button
              type="button"
              onClick={onOpenDiscovery}
              className="inline-flex items-center gap-1 text-zinc-400 hover:text-zinc-200 transition-colors text-[11px] cursor-pointer self-start sm:self-auto"
            >
              <Search className="w-3 h-3 text-zinc-500" />
              <span>Lookup by company name</span>
            </button>
          </div>
        </form>

        {/* Security badge note */}
        <div className="mt-4 pt-3 border-t border-zinc-800/80 flex items-center gap-2 text-[11px] text-zinc-500 font-mono">
          <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 shrink-0" />
          <span>SSRF guard active. Loopback, private subnets, and cloud metadata blocked at every redirect hop.</span>
        </div>
      </div>
    </div>
  );
}
