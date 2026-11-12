import React, { useState, useEffect, useCallback } from 'react';
import { useParams, Link } from 'react-router-dom';
import {
  ArrowLeft,
  RefreshCw,
  ExternalLink,
  Clock,
  AlertTriangle,
  CheckCircle2,
  Loader2,
  Info,
  Shield,
  X,
  AlertCircle,
  Globe,
} from 'lucide-react';
import { api } from '../lib/api';
import { formatLocalDate } from '../lib/dateUtils';
import FindingCard from '../components/FindingCard';
import DiffViewer from '../components/DiffViewer';
import VersionHistory from '../components/VersionHistory';

export default function PolicyDetail() {
  const { id } = useParams();
  const [policy, setPolicy] = useState(null);
  const [snapshot, setSnapshot] = useState(null);
  const [history, setHistory] = useState([]);
  const [activeTab, setActiveTab] = useState('findings');
  const [loading, setLoading] = useState(true);
  const [checking, setChecking] = useState(false);
  const [checkResult, setCheckResult] = useState(null);
  const [analyzing, setAnalyzing] = useState(false);
  const [analyzingSeconds, setAnalyzingSeconds] = useState(0);
  const [rawSnapshotText, setRawSnapshotText] = useState('');
  const [error, setError] = useState('');

  useEffect(() => {
    if (!analyzing) {
      return;
    }
    const start = Date.now();
    const timer = setInterval(() => {
      setAnalyzingSeconds(Math.floor((Date.now() - start) / 1000));
    }, 500);
    return () => clearInterval(timer);
  }, [analyzing]);

  const loadData = useCallback(async () => {
    try {
      setLoading(true);
      setError('');
      const pData = await api.getPolicy(id);
      setPolicy(pData);

      const hData = await api.getPolicyHistory(id);
      setHistory(hData);

      if (pData.latest_snapshot_id) {
        const sData = await api.getSnapshot(id, pData.latest_snapshot_id);
        setSnapshot(sData);
        setRawSnapshotText(sData.extracted_text || '');
      } else {
        setSnapshot(null);
        setRawSnapshotText('');
      }
    } catch (err) {
      setError(err.message || 'Failed to load policy');
    } finally {
      setLoading(false);
    }
  }, [id]);

  useEffect(() => {
    loadData();
  }, [loadData]);

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

  const handleReanalyze = async () => {
    setAnalyzing(true);
    setCheckResult(null);
    setAnalyzingSeconds(0);
    try {
      const updated = await api.reanalyzePolicy(id);
      await loadData();
      setActiveTab('findings');
      if (updated?.reanalysis_status === 'skipped_unchanged') {
        setCheckResult({
          status: 'unchanged',
          message: 'Document text is unchanged. Preserved existing baseline score and findings.',
        });
      } else {
        setCheckResult({
          status: 'reanalyzed',
          message: 'Clause analysis and risk assessment refreshed successfully.',
        });
      }
    } catch (err) {
      setCheckResult({
        status: 'extraction_failed',
        message: err.message || 'Failed to re-analyze clauses',
      });
    } finally {
      setAnalyzing(false);
    }
  };

  if (loading) {
    return (
      <div className="max-w-5xl mx-auto px-4 py-20 text-center space-y-2 font-mono">
        <Loader2 className="w-6 h-6 animate-spin text-[#5c5549] dark:text-zinc-400 mx-auto" />
        <p className="text-xs text-[#78716c] dark:text-zinc-500">Retrieving policy snapshot &amp; version delta...</p>
      </div>
    );
  }

  if (error || !policy) {
    return (
      <div className="max-w-2xl mx-auto px-4 py-16 text-center space-y-3 font-mono">
        <div className="p-3.5 rounded-lg bg-rose-500/10 dark:bg-rose-950/40 border border-rose-500/30 dark:border-rose-900/60 text-rose-800 dark:text-rose-300 text-xs break-words">
          {error || 'Policy not found'}
        </div>
        <Link
          to="/"
          className="inline-flex items-center gap-1.5 text-xs text-[#5c5549] hover:text-[#1c1917] dark:text-zinc-400 dark:hover:text-zinc-200 active:scale-95 py-2 px-3 rounded-lg border border-[#d5cbba] dark:border-zinc-800 bg-[#f5eedf] dark:bg-zinc-900 transition-colors"
        >
          <ArrowLeft className="w-3.5 h-3.5" /> Back to dashboard
        </Link>
      </div>
    );
  }

  const analysis = policy.latest_analysis;
  const findings = analysis?.findings || [];
  const changes = analysis?.changes || [];
  const isFallback = analysis?.model_id === 'deterministic-fallback';
  const isUserProvided =
    policy?.provenance === 'user_pasted' ||
    analysis?.provenance === 'user_pasted' ||
    snapshot?.extractor === 'user_pasted' ||
    snapshot?.provenance === 'user_pasted';
  const isArchived =
    policy?.provenance === 'archive' ||
    analysis?.provenance === 'archive' ||
    snapshot?.extractor === 'archive' ||
    snapshot?.provenance === 'archive';

  return (
    <div className="max-w-5xl mx-auto px-3.5 sm:px-6 py-5 sm:py-8 space-y-5 sm:space-y-6">
      {/* Top Bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <Link
          to="/"
          className="inline-flex items-center gap-1.5 text-xs font-mono text-[#5c5549] hover:text-[#1c1917] active:text-[#1c1917] dark:text-zinc-400 dark:hover:text-zinc-200 dark:active:text-white transition-colors py-1.5 active:scale-95 self-start"
        >
          <ArrowLeft className="w-3.5 h-3.5" />
          <span>Tracked Policies</span>
        </Link>

        {/* Action Controls - side by side on mobile */}
        <div className="grid grid-cols-2 sm:flex sm:items-center gap-2 w-full sm:w-auto">
          <button
            onClick={handleReanalyze}
            disabled={analyzing || checking}
            className="w-full sm:w-auto px-1.5 min-[360px]:px-2.5 sm:px-3.5 py-2.5 sm:py-1.5 rounded-lg bg-[#faf5ec] hover:bg-[#ece5d8] active:bg-[#ded6c6] dark:bg-zinc-900 dark:hover:bg-zinc-800 dark:active:bg-zinc-750 border border-[#d5cbba] dark:border-zinc-700/80 text-[#1c1917] dark:text-zinc-200 font-medium font-mono flex items-center justify-center gap-1 min-[360px]:gap-1.5 transition-all disabled:opacity-50 cursor-pointer min-h-[42px] sm:min-h-0 active:scale-[0.98]"
            title="Re-run deep semantic single-pass clause analysis across the entire policy"
          >
            {analyzing ? (
              <>
                <Loader2 className="w-3 h-3 min-[360px]:w-3.5 min-[360px]:h-3.5 animate-spin text-[#5c5549] dark:text-zinc-400 shrink-0" />
                <span className="text-[10px] min-[360px]:text-[11px] sm:text-xs whitespace-nowrap">Analyzing...</span>
              </>
            ) : (
              <>
                <Shield className="w-3 h-3 min-[360px]:w-3.5 min-[360px]:h-3.5 text-[#5c5549] dark:text-zinc-400 shrink-0" />
                <span className="text-[10px] min-[360px]:text-[11px] sm:text-xs whitespace-nowrap">Re-analyze Clauses</span>
              </>
            )}
          </button>

          <button
            onClick={handleRecheck}
            disabled={checking || analyzing}
            className="w-full sm:w-auto px-1.5 min-[360px]:px-2.5 sm:px-4 py-2.5 sm:py-1.5 rounded-lg bg-[#1c1917] hover:bg-[#292524] active:bg-[#0c0a09] text-[#faf5ec] dark:bg-zinc-100 dark:hover:bg-white dark:active:bg-zinc-200 dark:text-zinc-950 font-medium font-mono flex items-center justify-center gap-1 min-[360px]:gap-1.5 transition-all disabled:opacity-50 cursor-pointer min-h-[42px] sm:min-h-0 active:scale-[0.98]"
          >
            {checking ? (
              <>
                <Loader2 className="w-3 h-3 min-[360px]:w-3.5 min-[360px]:h-3.5 animate-spin shrink-0" />
                <span className="text-[10px] min-[360px]:text-[11px] sm:text-xs whitespace-nowrap">Fetching...</span>
              </>
            ) : (
              <>
                <RefreshCw className="w-3 h-3 min-[360px]:w-3.5 min-[360px]:h-3.5 shrink-0" />
                <span className="text-[10px] min-[360px]:text-[11px] sm:text-xs whitespace-nowrap">Check for Updates</span>
              </>
            )}
          </button>
        </div>
      </div>

      {/* Recheck / Reanalyze Alert Banner */}
      {checkResult && (
        <div
          className={`p-3.5 rounded-lg border flex items-start justify-between gap-3 text-xs font-mono break-words ${
            checkResult.status === 'unchanged' || checkResult.status === 'reanalyzed'
              ? 'bg-[#f5eedf] border-[#d5cbba] text-[#1c1917] dark:bg-zinc-900 dark:border-zinc-700 dark:text-zinc-300'
              : checkResult.status === 'changed'
              ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-800 dark:bg-emerald-950/30 dark:border-emerald-900/50 dark:text-emerald-300'
              : 'bg-rose-500/10 border-rose-500/30 text-rose-800 dark:bg-rose-950/30 dark:border-rose-900/50 dark:text-rose-300'
          }`}
        >
          <div className="flex items-start gap-2">
            {(checkResult.status === 'unchanged' || checkResult.status === 'reanalyzed') && (
              <CheckCircle2 className="w-4 h-4 text-[#5c5549] dark:text-zinc-400 shrink-0 mt-0.5" />
            )}
            {checkResult.status === 'changed' && <CheckCircle2 className="w-4 h-4 text-emerald-600 dark:text-emerald-400 shrink-0 mt-0.5" />}
            {checkResult.status === 'extraction_failed' && <AlertTriangle className="w-4 h-4 text-rose-600 dark:text-rose-400 shrink-0 mt-0.5" />}
            <div>
              <span className="font-semibold uppercase tracking-wider text-[11px]">
                {checkResult.status.replace('_', ' ')}:
              </span>{' '}
              <span className="leading-relaxed">{checkResult.message}</span>
            </div>
          </div>
          <button
            onClick={() => setCheckResult(null)}
            className="text-[#78716c] hover:text-[#1c1917] dark:text-zinc-500 dark:hover:text-zinc-300 p-1 -mr-1 -mt-1 rounded cursor-pointer min-w-[28px] min-h-[28px] flex items-center justify-center shrink-0"
            aria-label="Dismiss alert"
          >
            <X className="w-3.5 h-3.5" />
          </button>
        </div>
      )}

      {/* Real-time Single-Pass Analyzing Banner */}
      {analyzing && (
        <div className="p-4 rounded-xl panel border space-y-2.5 font-mono text-xs">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-1 text-[#1c1917] dark:text-zinc-200">
            <span className="flex items-center gap-2">
              <Loader2 className="w-4 h-4 animate-spin text-[#5c5549] dark:text-zinc-400 shrink-0" />
              <span>Evaluating policy clauses with Gemma 4...</span>
            </span>
            <span className="font-semibold text-[#1c1917] dark:text-zinc-300 bg-[#faf5ec] dark:bg-zinc-900 border border-[#d5cbba] dark:border-zinc-800 px-2 py-0.5 rounded self-end sm:self-auto">
              {analyzingSeconds}s
            </span>
          </div>
          <div className="flex flex-col xs:flex-row xs:items-center justify-between gap-1 text-[11px] text-[#78716c] dark:text-zinc-500">
            <span>Model: gemma-4-26b-a4b-it &middot; Source quote verification active</span>
            <span>Realistic estimate: ~20-25s</span>
          </div>
          <div className="w-full bg-[#faf5ec] dark:bg-zinc-900 h-2 rounded-full overflow-hidden border border-[#d5cbba] dark:border-zinc-800">
            <div
              className="bg-[#1c1917] dark:bg-zinc-200 h-full transition-all duration-300"
              style={{ width: `${Math.min(95, Math.max(6, (analyzingSeconds / 25) * 100))}%` }}
            />
          </div>
        </div>
      )}

      {/* Policy Meta Panel */}
      <div className="panel rounded-xl p-4 sm:p-5 border space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-3">
          <div className="space-y-1 min-w-0 max-w-full">
            <h1 className="text-lg sm:text-xl font-bold text-[#1c1917] dark:text-zinc-100 tracking-tight leading-snug">
              {policy.title || 'Policy Document'}
            </h1>
            {policy.canonical_url?.startsWith('/') ? (
              <Link
                to={policy.canonical_url}
                className="text-xs font-mono text-[#5c5549] hover:text-[#1c1917] dark:text-zinc-400 dark:hover:text-white transition-colors inline-flex items-center gap-1 max-w-full"
              >
                <span className="truncate break-all">{policy.canonical_url}</span>
              </Link>
            ) : (
              <a
                href={policy.canonical_url}
                target="_blank"
                rel="noreferrer"
                className="text-xs font-mono text-[#5c5549] hover:text-[#1c1917] dark:text-zinc-400 dark:hover:text-white transition-colors inline-flex items-center gap-1 max-w-full group"
              >
                <span className="truncate break-all">{policy.canonical_url}</span>
                <ExternalLink className="w-3 h-3 shrink-0 opacity-70 group-hover:opacity-100 transition-opacity" />
              </a>
            )}
          </div>

          <div className="flex items-center gap-2 flex-wrap text-xs font-mono shrink-0">
            <span className="px-2 py-0.5 rounded bg-[#faf5ec] dark:bg-zinc-900 border border-[#d5cbba] dark:border-zinc-800 text-[#5c5549] dark:text-zinc-400 flex items-center gap-1">
              <Clock className="w-3 h-3 text-[#78716c] dark:text-zinc-500 shrink-0" />
              <span>{formatLocalDate(policy.last_checked_at)}</span>
            </span>

            <span className="px-2 py-0.5 rounded bg-emerald-500/10 dark:bg-emerald-950/40 border border-emerald-500/30 dark:border-emerald-900/50 text-emerald-800 dark:text-emerald-400">
              Active baseline
            </span>

            {isArchived && (
              <span className="px-2 py-0.5 rounded bg-sky-500/10 dark:bg-blue-950/40 border border-sky-500/30 dark:border-blue-900/50 text-sky-800 dark:text-blue-300">
                Archived Snapshot
              </span>
            )}
          </div>
        </div>

        {/* User-Provided Content Warning Notice */}
        {isUserProvided && (
          <div className="p-3 rounded-lg bg-amber-500/10 dark:bg-amber-950/30 border border-amber-500/30 dark:border-amber-900/60 text-amber-900 dark:text-amber-300 text-xs font-mono flex items-start gap-2.5">
            <AlertCircle className="w-4 h-4 text-amber-600 dark:text-amber-400 shrink-0 mt-0.5" />
            <div className="space-y-0.5">
              <span className="font-semibold uppercase tracking-wider text-[11px] text-amber-900 dark:text-amber-200">
                User-Provided Ingestion Notice
              </span>
              <p className="text-amber-800/90 dark:text-amber-300/90 leading-relaxed text-[11px]">
                This policy baseline was provided via direct text paste. Findings, scores, and future diffs reflect user-submitted content and may not represent the complete official agreement.
              </p>
            </div>
          </div>
        )}

        {/* Public Web Archive Record Notice */}
        {isArchived && (
          <div className="p-3 rounded-lg bg-sky-500/10 dark:bg-blue-950/30 border border-sky-500/30 dark:border-blue-900/60 text-sky-900 dark:text-blue-300 text-xs font-mono flex items-start gap-2.5">
            <Globe className="w-4 h-4 text-sky-600 dark:text-blue-400 shrink-0 mt-0.5" />
            <div className="space-y-0.5">
              <span className="font-semibold uppercase tracking-wider text-[11px] text-sky-900 dark:text-blue-200">
                Public Web Archive Record
              </span>
              <p className="text-sky-800/90 dark:text-blue-300/90 leading-relaxed text-[11px]">
                Live fetch was restricted by the origin website; document was retrieved from a verified public snapshot via the Internet Archive Wayback Machine.
              </p>
            </div>
          </div>
        )}

        {/* Consumer Risk Score & Clause Metrics Card */}
        {analysis && (
          <div className="p-4 rounded-xl bg-[#faf5ec] dark:bg-zinc-950/80 border border-[#d5cbba] dark:border-zinc-800 flex flex-col md:flex-row md:items-center justify-between gap-4 shadow-xs">
            <div className="flex flex-col sm:flex-row sm:items-center gap-4 flex-1">
              <div className="flex items-center justify-between sm:justify-start gap-3">
              {(() => {
                const riskLevel =
                  (analysis.risk_level || '').toLowerCase() ||
                  (analysis.risk_score > 74
                    ? 'high'
                    : analysis.risk_score > 55
                    ? 'elevated'
                    : analysis.risk_score > 30
                    ? 'moderate'
                    : analysis.risk_score !== null && analysis.risk_score !== undefined
                    ? 'low'
                    : null);

                return (
                  <>
                    <div className="flex flex-col">
                      <span className="text-[10px] font-mono uppercase text-[#78716c] dark:text-zinc-500 font-semibold tracking-wider">
                        Consumer Risk Score
                      </span>
                      <div className="flex items-baseline gap-1.5 mt-0.5">
                        {analysis.risk_score !== null && analysis.risk_score !== undefined ? (
                          <>
                            <span
                              className={`text-2xl sm:text-3xl font-bold font-mono ${
                                riskLevel === 'high'
                                  ? 'text-rose-600 dark:text-rose-400'
                                  : riskLevel === 'elevated'
                                  ? 'text-amber-600 dark:text-amber-400'
                                  : riskLevel === 'moderate'
                                  ? 'text-yellow-600 dark:text-yellow-400'
                                  : riskLevel === 'low'
                                  ? 'text-emerald-600 dark:text-emerald-400'
                                  : 'text-[#78716c] dark:text-zinc-400'
                              }`}
                            >
                              {analysis.risk_score}
                            </span>
                            <span className="text-xs font-mono text-[#78716c] dark:text-zinc-500">/ 100</span>
                          </>
                        ) : (
                          <span className="text-sm font-semibold font-mono text-amber-700 dark:text-amber-400/90 py-1">
                            Unrated (Fallback)
                          </span>
                        )}
                      </div>
                    </div>

                    {/* Mobile badge indicator */}
                    <div className="sm:hidden">
                      <span
                        className={`px-2 py-0.5 rounded text-[10px] font-mono font-semibold uppercase tracking-wider ${
                          riskLevel === 'high'
                            ? 'bg-rose-500/10 dark:bg-rose-950/60 border border-rose-500/30 dark:border-rose-800 text-rose-800 dark:text-rose-300'
                            : riskLevel === 'elevated'
                            ? 'bg-amber-500/10 dark:bg-amber-950/60 border border-amber-500/30 dark:border-amber-800 text-amber-800 dark:text-amber-300'
                            : riskLevel === 'moderate'
                            ? 'bg-yellow-500/10 dark:bg-yellow-950/50 border border-yellow-500/30 dark:border-yellow-800 text-yellow-800 dark:text-yellow-300'
                            : riskLevel === 'low'
                            ? 'bg-emerald-500/10 dark:bg-emerald-950/50 border border-emerald-500/30 dark:border-emerald-800 text-emerald-800 dark:text-emerald-300'
                            : 'bg-[#ece5d8] dark:bg-zinc-900 border border-[#d5cbba] dark:border-zinc-800 text-[#5c5549] dark:text-zinc-400'
                        }`}
                      >
                        {riskLevel ? `${riskLevel} concern` : 'Pending'}
                      </span>
                    </div>
                  </>
                );
              })()}
            </div>

            <div className="hidden sm:block h-9 w-px bg-[#d5cbba] dark:bg-zinc-800 shrink-0" />

            <div className="space-y-1.5 flex-1 min-w-0">
              {(() => {
                const riskLevel =
                  (analysis.risk_level || '').toLowerCase() ||
                  (analysis.risk_score > 74
                    ? 'high'
                    : analysis.risk_score > 55
                    ? 'elevated'
                    : analysis.risk_score > 30
                    ? 'moderate'
                    : analysis.risk_score !== null && analysis.risk_score !== undefined
                    ? 'low'
                    : null);

                return (
                  <>
                    <div className="hidden sm:flex items-center gap-2">
                      <span
                        className={`px-2 py-0.5 rounded text-[10px] font-mono font-semibold uppercase tracking-wider ${
                          riskLevel === 'high'
                            ? 'bg-rose-500/10 dark:bg-rose-950/60 border border-rose-500/30 dark:border-rose-800 text-rose-800 dark:text-rose-300'
                            : riskLevel === 'elevated'
                            ? 'bg-amber-500/10 dark:bg-amber-950/60 border border-amber-500/30 dark:border-amber-800 text-amber-800 dark:text-amber-300'
                            : riskLevel === 'moderate'
                            ? 'bg-yellow-500/10 dark:bg-yellow-950/50 border border-yellow-500/30 dark:border-yellow-800 text-yellow-800 dark:text-yellow-300'
                            : riskLevel === 'low'
                            ? 'bg-emerald-500/10 dark:bg-emerald-950/50 border border-emerald-500/30 dark:border-emerald-800 text-emerald-800 dark:text-emerald-300'
                            : 'bg-[#ece5d8] dark:bg-zinc-900 border border-[#d5cbba] dark:border-zinc-800 text-[#5c5549] dark:text-zinc-400'
                        }`}
                      >
                        {riskLevel ? `${riskLevel} concern` : 'Evaluation pending'}
                      </span>
                      <span className="text-xs text-[#5c5549] dark:text-zinc-400 font-mono">
                        {findings.length} clause{findings.length === 1 ? '' : 's'} flagged
                      </span>
                    </div>

                    <div className="sm:hidden text-xs text-[#5c5549] dark:text-zinc-400 font-mono">
                      {findings.length} clause{findings.length === 1 ? '' : 's'} flagged
                    </div>

                    {/* Progress Bar (fluid on mobile, fixed width on desktop) */}
                    <div className="w-full sm:w-48 h-2 sm:h-1.5 rounded-full bg-[#ece5d8] dark:bg-zinc-900 border border-[#d5cbba] dark:border-zinc-800 overflow-hidden">
                      <div
                        className={`h-full transition-all duration-500 ${
                          riskLevel === 'high'
                            ? 'bg-rose-500'
                            : riskLevel === 'elevated'
                            ? 'bg-amber-500'
                            : riskLevel === 'moderate'
                            ? 'bg-yellow-500'
                            : riskLevel === 'low'
                            ? 'bg-emerald-500'
                            : 'bg-[#d5cbba] dark:bg-zinc-800'
                        }`}
                        style={{ width: `${Math.min(100, Math.max(8, analysis.risk_score || 8))}%` }}
                      />
                    </div>
                  </>
                );
              })()}
            </div>
            </div>

            {/* Severity Distribution Pills */}
            <div className="grid grid-cols-3 sm:flex items-center gap-1.5 sm:gap-2 text-[11px] font-mono text-center">
              <span className="px-2 py-1 sm:py-0.5 rounded bg-rose-500/10 dark:bg-rose-950/40 border border-rose-500/30 dark:border-rose-900/60 text-rose-800 dark:text-rose-300">
                {findings.filter((f) => f.severity === 'high').length} High
              </span>
              <span className="px-2 py-1 sm:py-0.5 rounded bg-amber-500/10 dark:bg-amber-950/40 border border-amber-500/30 dark:border-amber-900/60 text-amber-800 dark:text-amber-300">
                {findings.filter((f) => f.severity === 'medium').length} Med
              </span>
              <span className="px-2 py-1 sm:py-0.5 rounded bg-[#ece5d8] dark:bg-zinc-900 border border-[#d5cbba] dark:border-zinc-800 text-[#5c5549] dark:text-zinc-400">
                {findings.filter((f) => f.severity === 'low').length} Low
              </span>
            </div>
          </div>
        )}

        {/* Fallback Mode Notice if applicable */}
        {isFallback && (
          <div className="p-3.5 rounded-lg bg-amber-500/10 dark:bg-amber-950/20 border border-amber-500/30 dark:border-amber-900/40 flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs font-mono text-amber-800 dark:text-amber-300/90">
            <div className="flex items-start gap-2">
              <AlertTriangle className="w-4 h-4 text-amber-600 dark:text-amber-400 shrink-0 mt-0.5" />
              <span className="leading-relaxed">
                Policy was indexed in fallback mode. Click <strong>Re-analyze Clauses</strong> above to run deep Gemma evaluation.
              </span>
            </div>
            <button
              onClick={handleReanalyze}
              disabled={analyzing}
              className="w-full sm:w-auto px-3.5 py-2 sm:py-1 rounded-lg bg-amber-500/20 hover:bg-amber-500/30 active:bg-amber-500/40 text-amber-900 dark:text-amber-200 border border-amber-500/40 text-xs sm:text-[11px] cursor-pointer whitespace-nowrap min-h-[36px] sm:min-h-0 flex items-center justify-center active:scale-95 transition-all"
            >
              Analyze Now
            </button>
          </div>
        )}

        {/* Executive Summary */}
        {analysis?.summary && (
          <div className="p-3.5 rounded-lg bg-[#faf5ec] dark:bg-zinc-950 border border-[#d5cbba] dark:border-zinc-800/80 space-y-1.5 text-xs">
            <div className="font-mono text-[11px] uppercase tracking-wider text-[#78716c] dark:text-zinc-500 font-semibold flex flex-wrap items-center justify-between gap-1">
              <span>Policy Overview</span>
              {analysis.model_id && (
                <span className="text-[10px] text-[#78716c] dark:text-zinc-600 font-normal lowercase">
                  model: {analysis.model_id}
                </span>
              )}
            </div>
            <p className="text-[#292524] dark:text-zinc-300 leading-relaxed">{analysis.summary}</p>
          </div>
        )}

        {/* Disclaimer Note */}
        <div className="flex items-start sm:items-center gap-2 text-[11px] text-[#78716c] dark:text-zinc-500 pt-1 font-mono leading-relaxed">
          <Info className="w-3.5 h-3.5 text-[#78716c] dark:text-zinc-500 shrink-0 mt-0.5 sm:mt-0" />
          <span>Informational analysis only. Every finding is tied to verbatim excerpts verified against the raw policy text.</span>
        </div>
      </div>

      {/* Tabs */}
      <div className="grid grid-cols-4 gap-1 sm:flex sm:items-center sm:gap-1.5 border-b border-[#d5cbba] dark:border-zinc-800 pb-2 text-[11px] sm:text-xs font-mono">
        <button
          onClick={() => setActiveTab('findings')}
          className={`w-full sm:w-auto px-1 sm:px-3 py-2 sm:py-1.5 rounded-lg justify-center whitespace-nowrap min-h-[36px] sm:min-h-0 flex items-center transition-all cursor-pointer active:scale-95 ${
            activeTab === 'findings'
              ? 'bg-[#1c1917] text-[#faf5ec] dark:bg-zinc-100 dark:text-zinc-950 font-medium shadow-xs'
              : 'text-[#5c5549] hover:text-[#1c1917] hover:bg-[#ded6c6]/60 dark:text-zinc-400 dark:hover:text-zinc-200 dark:hover:bg-zinc-900 dark:active:bg-zinc-800'
          }`}
        >
          Clauses ({findings.length})
        </button>

        <button
          onClick={() => setActiveTab('diff')}
          className={`w-full sm:w-auto px-1 sm:px-3 py-2 sm:py-1.5 rounded-lg justify-center whitespace-nowrap min-h-[36px] sm:min-h-0 flex items-center transition-all cursor-pointer active:scale-95 ${
            activeTab === 'diff'
              ? 'bg-[#1c1917] text-[#faf5ec] dark:bg-zinc-100 dark:text-zinc-950 font-medium shadow-xs'
              : 'text-[#5c5549] hover:text-[#1c1917] hover:bg-[#ded6c6]/60 dark:text-zinc-400 dark:hover:text-zinc-200 dark:hover:bg-zinc-900 dark:active:bg-zinc-800'
          }`}
        >
          Diffs ({changes.length})
        </button>

        <button
          onClick={() => setActiveTab('history')}
          className={`w-full sm:w-auto px-1 sm:px-3 py-2 sm:py-1.5 rounded-lg justify-center whitespace-nowrap min-h-[36px] sm:min-h-0 flex items-center transition-all cursor-pointer active:scale-95 ${
            activeTab === 'history'
              ? 'bg-[#1c1917] text-[#faf5ec] dark:bg-zinc-100 dark:text-zinc-950 font-medium shadow-xs'
              : 'text-[#5c5549] hover:text-[#1c1917] hover:bg-[#ded6c6]/60 dark:text-zinc-400 dark:hover:text-zinc-200 dark:hover:bg-zinc-900 dark:active:bg-zinc-800'
          }`}
        >
          Log ({history.length})
        </button>

        <button
          onClick={() => setActiveTab('raw')}
          className={`w-full sm:w-auto px-1 sm:px-3 py-2 sm:py-1.5 rounded-lg justify-center whitespace-nowrap min-h-[36px] sm:min-h-0 flex items-center transition-all cursor-pointer active:scale-95 ${
            activeTab === 'raw'
              ? 'bg-[#1c1917] text-[#faf5ec] dark:bg-zinc-100 dark:text-zinc-950 font-medium shadow-xs'
              : 'text-[#5c5549] hover:text-[#1c1917] hover:bg-[#ded6c6]/60 dark:text-zinc-400 dark:hover:text-zinc-200 dark:hover:bg-zinc-900 dark:active:bg-zinc-800'
          }`}
        >
          Source Text
        </button>
      </div>

      {/* Tab 1: Findings */}
      {activeTab === 'findings' && (
        <div className="space-y-3">
          {findings.length === 0 ? (
            isFallback ? (
              <div className="p-6 sm:p-8 text-center rounded-xl panel border border-amber-500/30 dark:border-amber-900/40 bg-amber-500/10 dark:bg-amber-950/10 text-xs font-mono space-y-3">
                <AlertTriangle className="w-6 h-6 text-amber-600 dark:text-amber-400 mx-auto mb-1" />
                <div className="font-semibold text-[#1c1917] dark:text-zinc-200 text-sm">Clause AI Analysis Deferred (Fallback Mode)</div>
                <div className="text-[#5c5549] dark:text-zinc-400 max-w-lg mx-auto text-xs leading-relaxed">
                  {analysis?.summary || 'Policy successfully extracted and indexed. AI clause evaluation is currently in fallback mode due to free-tier rate limits or unconfigured credentials. Deterministic versioning, hashing, and diff monitoring remain 100% active.'}
                </div>
                <button
                  onClick={handleReanalyze}
                  disabled={analyzing}
                  className="w-full sm:w-auto px-4 py-2.5 sm:py-1.5 rounded-lg bg-[#1c1917] hover:bg-[#292524] text-[#faf5ec] dark:bg-zinc-100 dark:hover:bg-white dark:text-zinc-950 font-medium text-xs font-mono inline-flex items-center justify-center gap-1.5 cursor-pointer transition-all active:scale-95 min-h-[40px] sm:min-h-0"
                >
                  <RefreshCw className="w-3.5 h-3.5" />
                  <span>Re-analyze Clauses Now</span>
                </button>
              </div>
            ) : (
              <div className="p-6 sm:p-8 text-center rounded-xl panel text-[#5c5549] dark:text-zinc-400 text-xs font-mono space-y-1">
                <CheckCircle2 className="w-5 h-5 text-emerald-600 dark:text-emerald-400 mx-auto mb-1" />
                <div className="font-semibold text-[#1c1917] dark:text-zinc-200 text-sm">No Notable High-Risk Clauses Flagged</div>
                <div className="text-[#78716c] dark:text-zinc-500 max-w-md mx-auto text-[11px] leading-relaxed">
                  No explicit auto-renewal traps, mandatory arbitration waivers, or unexpected data-sharing clauses were identified in the verified text.
                </div>
              </div>
            )
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
        <div className="panel rounded-xl p-3.5 sm:p-4 border space-y-2">
          <div className="flex flex-col xs:flex-row xs:items-center justify-between gap-1 text-xs font-mono text-[#78716c] dark:text-zinc-500 border-b border-[#d5cbba] dark:border-zinc-800 pb-2">
            <span>Snapshot Baseline ({rawSnapshotText.length.toLocaleString()} characters)</span>
            <span className="break-all">ID: {policy.latest_snapshot_id}</span>
          </div>
          <pre className="font-mono text-xs text-[#292524] dark:text-zinc-300 whitespace-pre-wrap leading-relaxed max-h-[450px] sm:max-h-[600px] overflow-y-auto p-3 rounded-lg bg-[#faf5ec] dark:bg-zinc-950 border border-[#d5cbba] dark:border-zinc-800/80 break-words overflow-x-auto">
            {rawSnapshotText || 'No text content available.'}
          </pre>
        </div>
      )}
    </div>
  );
}
