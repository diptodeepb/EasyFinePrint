import React, { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import {
  GitCompare,
  FileCheck,
  ShieldCheck,
  Clock,
  ExternalLink,
  ChevronRight,
  RefreshCw,
  Loader2,
  AlertCircle,
  Database,
} from 'lucide-react';
import { api } from '../lib/api';
import UrlForm from '../components/UrlForm';
import DiscoveryModal from '../components/DiscoveryModal';

export default function Home() {
  const navigate = useNavigate();
  const [policies, setPolicies] = useState([]);
  const [loadingPolicies, setLoadingPolicies] = useState(true);
  const [analyzing, setAnalyzing] = useState(false);
  const [analyzeError, setAnalyzeError] = useState('');
  const [isDiscoveryOpen, setIsDiscoveryOpen] = useState(false);

  const fetchTrackedPolicies = async () => {
    try {
      setLoadingPolicies(true);
      const data = await api.listPolicies();
      setPolicies(data);
    } catch (err) {
      console.error('Failed to load policies:', err);
    } finally {
      setLoadingPolicies(false);
    }
  };

  useEffect(() => {
    fetchTrackedPolicies();
  }, []);

  const handleAnalyze = async (url) => {
    setAnalyzing(true);
    setAnalyzeError('');
    try {
      const policy = await api.analyzePolicy(url);
      navigate(`/policies/${policy.id}`);
    } catch (err) {
      setAnalyzeError(err.message || 'Failed to analyze policy URL');
      setAnalyzing(false);
    }
  };

  const handleSelectDiscoveryUrl = (url) => {
    handleAnalyze(url);
  };

  return (
    <div className="space-y-12 pb-16 pt-8 max-w-5xl mx-auto px-4">
      {/* Hero Header */}
      <section className="space-y-4">
        <div className="space-y-2">
          <h1 className="text-2xl sm:text-3xl font-bold text-zinc-100 tracking-tight">
            Terms & Privacy Policy Change Monitor
          </h1>
          <p className="text-xs sm:text-sm text-zinc-400 max-w-2xl leading-relaxed">
            Deterministic paragraph diffing and citation-backed clause analysis. Track revisions across public legal agreements with exact source verification.
          </p>
        </div>

        {/* Global Error Banner */}
        {analyzeError && (
          <div className="p-3.5 rounded-lg bg-rose-950/40 border border-rose-900/60 text-rose-300 text-xs font-mono flex items-start gap-2">
            <AlertCircle className="w-4 h-4 shrink-0 mt-0.5 text-rose-400" />
            <div>
              <span className="font-semibold">Analysis error: </span>
              <span>{analyzeError}</span>
            </div>
          </div>
        )}

        {/* URL Form */}
        <UrlForm
          onAnalyze={handleAnalyze}
          loading={analyzing}
          onOpenDiscovery={() => setIsDiscoveryOpen(true)}
        />
      </section>

      {/* Engineering Principles */}
      <section className="grid grid-cols-1 sm:grid-cols-3 gap-3">
        <div className="panel rounded-lg p-4 border space-y-2">
          <div className="flex items-center gap-2 text-xs font-semibold text-zinc-200">
            <GitCompare className="w-4 h-4 text-zinc-400" />
            <span>Deterministic Diff Engine</span>
          </div>
          <p className="text-xs text-zinc-400 leading-relaxed">
            Sequence matcher and SHA-256 hashes classify additions, removals, and modifications as verifiable facts, independent of model temperature.
          </p>
        </div>

        <div className="panel rounded-lg p-4 border space-y-2">
          <div className="flex items-center gap-2 text-xs font-semibold text-zinc-200">
            <FileCheck className="w-4 h-4 text-zinc-400" />
            <span>Verbatim Evidence Rule</span>
          </div>
          <p className="text-xs text-zinc-400 leading-relaxed">
            Every reported concern requires an exact quotation. The server validates citations against raw source text and discards unsupported claims.
          </p>
        </div>

        <div className="panel rounded-lg p-4 border space-y-2">
          <div className="flex items-center gap-2 text-xs font-semibold text-zinc-200">
            <ShieldCheck className="w-4 h-4 text-zinc-400" />
            <span>Fail-Safe Baselines</span>
          </div>
          <p className="text-xs text-zinc-400 leading-relaxed">
            Extraction errors and rate limits never produce a false "unchanged" status. Existing baseline snapshots are preserved.
          </p>
        </div>
      </section>

      {/* Tracked Policies Table */}
      <section className="space-y-3">
        <div className="flex items-center justify-between pb-1">
          <div>
            <h2 className="text-sm font-semibold text-zinc-200 tracking-tight">Tracked Policies</h2>
            <p className="text-xs text-zinc-500">Monitored documents and baseline status</p>
          </div>

          <button
            onClick={fetchTrackedPolicies}
            disabled={loadingPolicies}
            className="px-2.5 py-1 rounded bg-zinc-900 hover:bg-zinc-800 text-zinc-300 text-xs font-mono flex items-center gap-1.5 transition-colors cursor-pointer border border-zinc-800"
          >
            <RefreshCw className={`w-3 h-3 ${loadingPolicies ? 'animate-spin' : ''}`} />
            <span>Refresh</span>
          </button>
        </div>

        {loadingPolicies ? (
          <div className="p-8 text-center rounded-lg panel border text-zinc-400 text-xs font-mono">
            <Loader2 className="w-4 h-4 animate-spin text-zinc-400 mx-auto mb-2" />
            <span>Loading tracked policies...</span>
          </div>
        ) : policies.length === 0 ? (
          <div className="p-8 text-center rounded-lg panel border space-y-2">
            <Database className="w-5 h-5 text-zinc-600 mx-auto" />
            <p className="text-xs text-zinc-400 font-mono">No policies tracked yet</p>
            <p className="text-[11px] text-zinc-500">
              Submit a public URL above to create your first version baseline.
            </p>
          </div>
        ) : (
          <div className="panel rounded-lg border overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs font-mono">
                <thead className="bg-zinc-950 border-b border-zinc-800 text-zinc-400 uppercase tracking-wider text-[11px]">
                  <tr>
                    <th className="py-2.5 px-3">Policy Document</th>
                    <th className="py-2.5 px-3 hidden sm:table-cell">Canonical URL</th>
                    <th className="py-2.5 px-3">Last Checked</th>
                    <th className="py-2.5 px-3 text-right">Action</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-zinc-800/80">
                  {policies.map((pol) => {
                    const formattedDate = pol.last_checked_at
                      ? new Date(pol.last_checked_at).toLocaleDateString(undefined, {
                          month: 'short',
                          day: 'numeric',
                          hour: '2-digit',
                          minute: '2-digit',
                        })
                      : 'Never';

                    return (
                      <tr
                        key={pol.id}
                        className="hover:bg-zinc-900/50 transition-colors"
                      >
                        <td className="py-2.5 px-3">
                          <Link
                            to={`/policies/${pol.id}`}
                            className="font-medium text-zinc-200 hover:text-white transition-colors"
                          >
                            {pol.title || 'Policy Document'}
                          </Link>
                        </td>
                        <td className="py-2.5 px-3 text-zinc-500 hidden sm:table-cell max-w-xs truncate">
                          <a
                            href={pol.canonical_url}
                            target="_blank"
                            rel="noreferrer"
                            className="hover:text-zinc-300 transition-colors inline-flex items-center gap-1 truncate"
                          >
                            <span className="truncate">{pol.canonical_url}</span>
                            <ExternalLink className="w-2.5 h-2.5 shrink-0 opacity-60" />
                          </a>
                        </td>
                        <td className="py-2.5 px-3 text-zinc-400">
                          {formattedDate}
                        </td>
                        <td className="py-2.5 px-3 text-right">
                          <Link
                            to={`/policies/${pol.id}`}
                            className="inline-flex items-center gap-1 px-2.5 py-1 rounded bg-zinc-900 hover:bg-zinc-800 text-zinc-200 border border-zinc-800 transition-colors text-xs"
                          >
                            <span>Inspect</span>
                            <ChevronRight className="w-3 h-3 text-zinc-500" />
                          </Link>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>
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
