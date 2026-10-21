import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import {
  ArrowLeft,
  RefreshCw,
  ExternalLink,
  Clock,
  GitCompare,
  FileText,
  History,
  AlertTriangle,
  CheckCircle2,
  Loader2,
  Info,
  Shield,
} from 'lucide-react';
import { api } from '../lib/api';
import FindingCard from '../components/FindingCard';
import DiffViewer from '../components/DiffViewer';
import VersionHistory from '../components/VersionHistory';

export default function PolicyDetail() {
  const { id } = useParams();
  const [policy, setPolicy] = useState(null);
  const [history, setHistory] = useState([]);
  const [activeTab, setActiveTab] = useState('findings');
  const [loading, setLoading] = useState(true);
  const [checking, setChecking] = useState(false);
  const [checkResult, setCheckResult] = useState(null);
  const [rawSnapshotText, setRawSnapshotText] = useState('');
  const [error, setError] = useState('');

  const loadData = async () => {
    try {
      setLoading(true);
      setError('');
      const pData = await api.getPolicy(id);
      setPolicy(pData);

      const hData = await api.getPolicyHistory(id);
      setHistory(hData);

      if (pData.latest_snapshot_id) {
        const sData = await api.getSnapshot(id, pData.latest_snapshot_id);
        setRawSnapshotText(sData.extracted_text || '');
      }
    } catch (err) {
      setError(err.message || 'Failed to load policy');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [id]);

  const handleRecheck = async () => {
    setChecking(true);
    setCheckResult(null);
    try {
      const res = await api.checkPolicyUpdates(id);
      setCheckResult(res);
      await loadData();
      if (res.status === 'changed') {
        setActiveTab('diff');
      }
    } catch (err) {
      setCheckResult({
        status: 'extraction_failed',
        message: err.message || 'Failed to check policy',
      });
    } finally {
      setChecking(false);
    }
  };

  if (loading) {
    return (
      <div className="max-w-5xl mx-auto px-4 py-20 text-center space-y-2 font-mono">
        <Loader2 className="w-6 h-6 animate-spin text-zinc-400 mx-auto" />
        <p className="text-xs text-zinc-500">Retrieving policy snapshot & version delta...</p>
      </div>
    );
  }

  if (error || !policy) {
    return (
      <div className="max-w-2xl mx-auto px-4 py-16 text-center space-y-3 font-mono">
        <div className="p-3 rounded-lg bg-rose-950/40 border border-rose-900/60 text-rose-300 text-xs">
          {error || 'Policy not found'}
        </div>
        <Link
          to="/"
          className="inline-flex items-center gap-1.5 text-xs text-zinc-400 hover:text-zinc-200"
        >
          <ArrowLeft className="w-3.5 h-3.5" /> Back to dashboard
        </Link>
      </div>
    );
  }

  const analysis = policy.latest_analysis;
  const findings = analysis?.findings || [];
  const changes = analysis?.changes || [];

  return (
    <div className="max-w-5xl mx-auto px-4 py-8 space-y-6">
      {/* Top Bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <Link
          to="/"
          className="inline-flex items-center gap-1.5 text-xs font-mono text-zinc-400 hover:text-zinc-200 transition-colors"
        >
          <ArrowLeft className="w-3.5 h-3.5" />
          <span>Tracked Policies</span>
        </Link>

        {/* Check for Updates Action */}
        <button
          onClick={handleRecheck}
          disabled={checking}
          className="px-3.5 py-1.5 rounded-lg bg-zinc-100 hover:bg-white text-zinc-950 font-medium text-xs font-mono flex items-center justify-center gap-1.5 transition-colors disabled:opacity-50 cursor-pointer self-start sm:self-auto"
        >
          {checking ? (
            <>
              <Loader2 className="w-3 h-3 animate-spin" />
              <span>Fetching & Diffing...</span>
            </>
          ) : (
            <>
              <RefreshCw className="w-3 h-3" />
              <span>Check for Updates</span>
            </>
          )}
        </button>
      </div>

      {/* Recheck Alert Banner */}
      {checkResult && (
        <div
          className={`p-3.5 rounded-lg border flex items-start justify-between gap-3 text-xs font-mono ${
            checkResult.status === 'unchanged'
              ? 'bg-zinc-900 border-zinc-700 text-zinc-300'
              : checkResult.status === 'changed'
              ? 'bg-emerald-950/30 border-emerald-900/50 text-emerald-300'
              : 'bg-rose-950/30 border-rose-900/50 text-rose-300'
          }`}
        >
          <div className="flex items-start gap-2">
            {checkResult.status === 'unchanged' && <CheckCircle2 className="w-3.5 h-3.5 text-zinc-400 shrink-0 mt-0.5" />}
            {checkResult.status === 'changed' && <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 shrink-0 mt-0.5" />}
            {checkResult.status === 'extraction_failed' && <AlertTriangle className="w-3.5 h-3.5 text-rose-400 shrink-0 mt-0.5" />}
            <div>
              <span className="font-semibold uppercase tracking-wider text-[11px]">
                {checkResult.status.replace('_', ' ')}:
              </span>{' '}
              <span>{checkResult.message}</span>
            </div>
          </div>
          <button
            onClick={() => setCheckResult(null)}
            className="text-zinc-500 hover:text-zinc-300 text-xs cursor-pointer"
          >
            Dismiss
          </button>
        </div>
      )}

      {/* Policy Meta Panel */}
      <div className="panel rounded-xl p-5 border space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-3">
          <div className="space-y-1">
            <h1 className="text-lg sm:text-xl font-bold text-zinc-100 tracking-tight">
              {policy.title || 'Policy Document'}
            </h1>
            <a
              href={policy.canonical_url}
              target="_blank"
              rel="noreferrer"
              className="text-xs font-mono text-zinc-400 hover:text-zinc-200 transition-colors inline-flex items-center gap-1"
            >
              <span>{policy.canonical_url}</span>
              <ExternalLink className="w-3 h-3" />
            </a>
          </div>

          <div className="flex items-center gap-2 flex-wrap text-xs font-mono">
            <span className="px-2 py-0.5 rounded bg-zinc-900 border border-zinc-800 text-zinc-400 flex items-center gap-1">
              <Clock className="w-3 h-3 text-zinc-500" />
              <span>
                {policy.last_checked_at
                  ? new Date(policy.last_checked_at).toLocaleString(undefined, {
                      dateStyle: 'short',
                      timeStyle: 'short',
                    })
                  : 'Just now'}
              </span>
            </span>

            <span className="px-2 py-0.5 rounded bg-emerald-950/40 border border-emerald-900/50 text-emerald-400">
              Active baseline
            </span>
          </div>
        </div>

        {/* Executive Summary */}
        {analysis?.summary && (
          <div className="p-3.5 rounded-lg bg-zinc-950 border border-zinc-800/80 space-y-1 text-xs">
            <div className="font-mono text-[11px] uppercase tracking-wider text-zinc-500 font-semibold">
              Policy Overview
            </div>
            <p className="text-zinc-300 leading-relaxed">{analysis.summary}</p>
          </div>
        )}

        {/* Disclaimer Note */}
        <div className="flex items-center gap-2 text-[11px] text-zinc-500 pt-1 font-mono">
          <Info className="w-3 h-3 text-zinc-500 shrink-0" />
          <span>Informational analysis only. Every finding is tied to verbatim excerpts verified against the raw policy text.</span>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex items-center gap-1.5 border-b border-zinc-800 pb-2 text-xs font-mono overflow-x-auto">
        <button
          onClick={() => setActiveTab('findings')}
          className={`px-3 py-1.5 rounded transition-colors cursor-pointer ${
            activeTab === 'findings'
              ? 'bg-zinc-100 text-zinc-950 font-medium'
              : 'text-zinc-400 hover:text-zinc-200 hover:bg-zinc-900'
          }`}
        >
          Clauses ({findings.length})
        </button>

        <button
          onClick={() => setActiveTab('diff')}
          className={`px-3 py-1.5 rounded transition-colors cursor-pointer ${
            activeTab === 'diff'
              ? 'bg-zinc-100 text-zinc-950 font-medium'
              : 'text-zinc-400 hover:text-zinc-200 hover:bg-zinc-900'
          }`}
        >
          Diffs ({changes.length})
        </button>

        <button
          onClick={() => setActiveTab('history')}
          className={`px-3 py-1.5 rounded transition-colors cursor-pointer ${
            activeTab === 'history'
              ? 'bg-zinc-100 text-zinc-950 font-medium'
              : 'text-zinc-400 hover:text-zinc-200 hover:bg-zinc-900'
          }`}
        >
          Log ({history.length})
        </button>

        <button
          onClick={() => setActiveTab('raw')}
          className={`px-3 py-1.5 rounded transition-colors cursor-pointer ${
            activeTab === 'raw'
              ? 'bg-zinc-100 text-zinc-950 font-medium'
              : 'text-zinc-400 hover:text-zinc-200 hover:bg-zinc-900'
          }`}
        >
          Source Text
        </button>
      </div>

      {/* Tab 1: Findings */}
      {activeTab === 'findings' && (
        <div className="space-y-3">
          {findings.length === 0 ? (
            <div className="p-8 text-center rounded-xl panel text-zinc-400 text-xs font-mono space-y-1">
              <CheckCircle2 className="w-5 h-5 text-emerald-400 mx-auto mb-1" />
              <div className="font-semibold text-zinc-200">No Notable High-Risk Clauses Flagged</div>
              <div className="text-zinc-500 max-w-md mx-auto text-[11px]">
                No explicit auto-renewal traps, mandatory arbitration waivers, or unexpected data-sharing clauses were identified in the verified text.
              </div>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {findings.map((f, idx) => (
                <FindingCard key={idx} finding={f} />
              ))}
            </div>
          )}
        </div>
      )}

      {/* Tab 2: Diff & Changes */}
      {activeTab === 'diff' && (
        <DiffViewer
          changes={changes}
          analysisSummary={analysis?.analysis_type === 'change' ? analysis?.summary : ''}
        />
      )}

      {/* Tab 3: History */}
      {activeTab === 'history' && (
        <VersionHistory
          events={history}
          onViewSnapshot={() => setActiveTab('raw')}
        />
      )}

      {/* Tab 4: Raw Extracted Text */}
      {activeTab === 'raw' && (
        <div className="panel rounded-xl p-4 border space-y-2">
          <div className="flex items-center justify-between text-xs font-mono text-zinc-500 border-b border-zinc-800 pb-2">
            <span>Snapshot Baseline ({rawSnapshotText.length.toLocaleString()} characters)</span>
            <span>ID: {policy.latest_snapshot_id}</span>
          </div>
          <pre className="font-mono text-xs text-zinc-300 whitespace-pre-wrap leading-relaxed max-h-[600px] overflow-y-auto p-3 rounded bg-zinc-950 border border-zinc-800/80">
            {rawSnapshotText || 'No text content available.'}
          </pre>
        </div>
      )}
    </div>
  );
}
