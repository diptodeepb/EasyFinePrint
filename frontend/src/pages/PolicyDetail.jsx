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
} from 'lucide-react';
import { api } from '../lib/api';
import { formatLocalDate } from '../lib/dateUtils';
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
        setRawSnapshotText(sData.extracted_text || '');
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
        <Loader2 className="w-6 h-6 animate-spin text-zinc-400 mx-auto" />
        <p className="text-xs text-zinc-500">Retrieving policy snapshot & version delta...</p>
      </div>
    );
  }

  if (error || !policy) {
    return (
      <div className="max-w-2xl mx-auto px-4 py-16 text-center space-y-3 font-mono">
        <div className="p-3.5 rounded-lg bg-rose-950/40 border border-rose-900/60 text-rose-300 text-xs break-words">
          {error || 'Policy not found'}
        </div>
        <Link
          to="/"
          className="inline-flex items-center gap-1.5 text-xs text-zinc-400 hover:text-zinc-200 active:scale-95 py-2 px-3 rounded-lg border border-zinc-800 bg-zinc-900"
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

  return (
    <div className="max-w-5xl mx-auto px-3.5 sm:px-6 py-5 sm:py-8 space-y-5 sm:space-y-6">
      {/* Top Bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <Link
          to="/"
          className="inline-flex items-center gap-1.5 text-xs font-mono text-zinc-400 hover:text-zinc-200 active:text-white transition-colors py-1.5 active:scale-95 self-start"
        >
          <ArrowLeft className="w-3.5 h-3.5" />
          <span>Tracked Policies</span>
        </Link>

        {/* Action Controls - side by side on mobile */}
        <div className="grid grid-cols-2 sm:flex sm:items-center gap-2 w-full sm:w-auto">
          <button
            onClick={handleReanalyze}
            disabled={analyzing || checking}
            className="w-full sm:w-auto px-1.5 min-[360px]:px-2.5 sm:px-3.5 py-2.5 sm:py-1.5 rounded-lg bg-zinc-900 hover:bg-zinc-800 active:bg-zinc-750 border border-zinc-700/80 text-zinc-200 font-medium font-mono flex items-center justify-center gap-1 min-[360px]:gap-1.5 transition-all disabled:opacity-50 cursor-pointer min-h-[42px] sm:min-h-0 active:scale-[0.98]"
            title="Re-run deep semantic single-pass clause analysis across the entire policy"
          >
            {analyzing ? (
              <>
                <Loader2 className="w-3 h-3 min-[360px]:w-3.5 min-[360px]:h-3.5 animate-spin text-zinc-400 shrink-0" />
                <span className="text-[10px] min-[360px]:text-[11px] sm:text-xs whitespace-nowrap">Analyzing...</span>
              </>
            ) : (
              <>
                <Shield className="w-3 h-3 min-[360px]:w-3.5 min-[360px]:h-3.5 text-zinc-400 shrink-0" />
                <span className="text-[10px] min-[360px]:text-[11px] sm:text-xs whitespace-nowrap">Re-analyze Clauses</span>
              </>
            )}
          </button>

          <button
            onClick={handleRecheck}
            disabled={checking || analyzing}
            className="w-full sm:w-auto px-1.5 min-[360px]:px-2.5 sm:px-4 py-2.5 sm:py-1.5 rounded-lg bg-zinc-100 hover:bg-white active:bg-zinc-200 text-zinc-950 font-medium font-mono flex items-center justify-center gap-1 min-[360px]:gap-1.5 transition-all disabled:opacity-50 cursor-pointer min-h-[42px] sm:min-h-0 active:scale-[0.98]"
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
              ? 'bg-zinc-900 border-zinc-700 text-zinc-300'
              : checkResult.status === 'changed'
              ? 'bg-emerald-950/30 border-emerald-900/50 text-emerald-300'
              : 'bg-rose-950/30 border-rose-900/50 text-rose-300'
          }`}
        >
          <div className="flex items-start gap-2">
            {(checkResult.status === 'unchanged' || checkResult.status === 'reanalyzed') && (
              <CheckCircle2 className="w-4 h-4 text-zinc-400 shrink-0 mt-0.5" />
            )}
            {checkResult.status === 'changed' && <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />}
            {checkResult.status === 'extraction_failed' && <AlertTriangle className="w-4 h-4 text-rose-400 shrink-0 mt-0.5" />}
            <div>
              <span className="font-semibold uppercase tracking-wider text-[11px]">
                {checkResult.status.replace('_', ' ')}:
              </span>{' '}
              <span className="leading-relaxed">{checkResult.message}</span>
            </div>
          </div>
          <button
            onClick={() => setCheckResult(null)}
            className="text-zinc-500 hover:text-zinc-300 active:text-white p-1 -mr-1 -mt-1 rounded cursor-pointer min-w-[28px] min-h-[28px] flex items-center justify-center shrink-0"
            aria-label="Dismiss alert"
          >
            <X className="w-3.5 h-3.5" />
          </button>
        </div>
      )}

      {/* Real-time Single-Pass Analyzing Banner */}
      {analyzing && (
        <div className="p-4 rounded-xl panel border space-y-2.5 font-mono text-xs">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-1 text-zinc-200">
            <span className="flex items-center gap-2">
              <Loader2 className="w-4 h-4 animate-spin text-zinc-400 shrink-0" />
              <span>Evaluating policy clauses with Gemma 4...</span>
            </span>
            <span className="font-semibold text-zinc-300 bg-zinc-900 border border-zinc-800 px-2 py-0.5 rounded self-end sm:self-auto">
              {analyzingSeconds}s
            </span>
          </div>
          <div className="flex flex-col xs:flex-row xs:items-center justify-between gap-1 text-[11px] text-zinc-500">
            <span>Model: gemma-4-26b-a4b-it · Source quote verification active</span>
            <span>Realistic estimate: ~20-25s</span>
          </div>
          <div className="w-full bg-zinc-900 h-2 rounded-full overflow-hidden border border-zinc-800">
            <div
              className="bg-zinc-200 h-full transition-all duration-300"
              style={{ width: `${Math.min(95, Math.max(6, (analyzingSeconds / 25) * 100))}%` }}
            />
          </div>
        </div>
      )}

      {/* Policy Meta Panel */}
      <div className="panel rounded-xl p-4 sm:p-5 border space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-3">
          <div className="space-y-1 min-w-0 max-w-full">
            <h1 className="text-lg sm:text-xl font-bold text-zinc-100 tracking-tight leading-snug">
              {policy.title || 'Policy Document'}
            </h1>
            {policy.canonical_url?.startsWith('/') ? (
              <Link
                to={policy.canonical_url}
                className="text-xs font-mono text-zinc-400 hover:text-zinc-200 transition-colors inline-flex items-center gap-1 max-w-full"
              >
                <span className="truncate break-all">{policy.canonical_url}</span>
              </Link>
            ) : (
              <a
                href={policy.canonical_url}
                target="_blank"
                rel="noreferrer"
                className="text-xs font-mono text-zinc-400 hover:text-zinc-200 transition-colors inline-flex items-center gap-1 max-w-full"
              >
                <span className="truncate break-all">{policy.canonical_url}</span>
                <ExternalLink className="w-3 h-3 shrink-0 opacity-70" />
              </a>
            )}
          </div>

          <div className="flex items-center gap-2 flex-wrap text-xs font-mono shrink-0">
            <span className="px-2 py-0.5 rounded bg-zinc-900 border border-zinc-800 text-zinc-400 flex items-center gap-1">
              <Clock className="w-3 h-3 text-zinc-500 shrink-0" />
              <span>{formatLocalDate(policy.last_checked_at)}</span>
            </span>

            <span className="px-2 py-0.5 rounded bg-emerald-950/40 border border-emerald-900/50 text-emerald-400">
              Active baseline
            </span>
          </div>
        </div>

        {/* Consumer Risk Score & Clause Metrics Card */}
        {analysis && (
          <div className="p-4 rounded-xl bg-zinc-950/80 border border-zinc-800 flex flex-col md:flex-row md:items-center justify-between gap-4 shadow-sm">
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
                      <span className="text-[10px] font-mono uppercase text-zinc-500 font-semibold tracking-wider">
                        Consumer Risk Score
                      </span>
                      <div className="flex items-baseline gap-1.5 mt-0.5">
                        {analysis.risk_score !== null && analysis.risk_score !== undefined ? (
                          <>
                            <span
                              className={`text-2xl sm:text-3xl font-bold font-mono ${
                                riskLevel === 'high'
                                  ? 'text-rose-400'
                                  : riskLevel === 'elevated'
                                  ? 'text-amber-400'
                                  : riskLevel === 'moderate'
                                  ? 'text-yellow-400'
                                  : riskLevel === 'low'
                                  ? 'text-emerald-400'
                                  : 'text-zinc-400'
                              }`}
                            >
                              {analysis.risk_score}
                            </span>
                            <span className="text-xs font-mono text-zinc-500">/ 100</span>
                          </>
                        ) : (
                          <span className="text-sm font-semibold font-mono text-amber-400/90 py-1">
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
                            ? 'bg-rose-950/60 border border-rose-800 text-rose-300'
                            : riskLevel === 'elevated'
                            ? 'bg-amber-950/60 border border-amber-800 text-amber-300'
                            : riskLevel === 'moderate'
                            ? 'bg-yellow-950/50 border border-yellow-800 text-yellow-300'
                            : riskLevel === 'low'
                            ? 'bg-emerald-950/50 border border-emerald-800 text-emerald-300'
                            : 'bg-zinc-900 border border-zinc-800 text-zinc-400'
                        }`}
                      >
                        {riskLevel ? `${riskLevel} concern` : 'Pending'}
                      </span>
                    </div>
                  </>
                );
              })()}
            </div>

            <div className="hidden sm:block h-9 w-px bg-zinc-800 shrink-0" />

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
                            ? 'bg-rose-950/60 border border-rose-800 text-rose-300'
                            : riskLevel === 'elevated'
                            ? 'bg-amber-950/60 border border-amber-800 text-amber-300'
                            : riskLevel === 'moderate'
                            ? 'bg-yellow-950/50 border border-yellow-800 text-yellow-300'
                            : riskLevel === 'low'
                            ? 'bg-emerald-950/50 border border-emerald-800 text-emerald-300'
                            : 'bg-zinc-900 border border-zinc-800 text-zinc-400'
                        }`}
                      >
                        {riskLevel ? `${riskLevel} concern` : 'Evaluation pending'}
                      </span>
                      <span className="text-xs text-zinc-400 font-mono">
                        {findings.length} clause{findings.length === 1 ? '' : 's'} flagged
                      </span>
                    </div>

                    <div className="sm:hidden text-xs text-zinc-400 font-mono">
                      {findings.length} clause{findings.length === 1 ? '' : 's'} flagged
                    </div>

                    {/* Progress Bar (fluid on mobile, fixed width on desktop) */}
                    <div className="w-full sm:w-48 h-2 sm:h-1.5 rounded-full bg-zinc-900 border border-zinc-800 overflow-hidden">
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
                            : 'bg-zinc-800'
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
              <span className="px-2 py-1 sm:py-0.5 rounded bg-rose-950/40 border border-rose-900/60 text-rose-300">
                {findings.filter((f) => f.severity === 'high').length} High
              </span>
              <span className="px-2 py-1 sm:py-0.5 rounded bg-amber-950/40 border border-amber-900/60 text-amber-300">
                {findings.filter((f) => f.severity === 'medium').length} Med
              </span>
              <span className="px-2 py-1 sm:py-0.5 rounded bg-zinc-900 border border-zinc-800 text-zinc-400">
                {findings.filter((f) => f.severity === 'low').length} Low
              </span>
            </div>
          </div>
        )}

        {/* Fallback Mode Notice if applicable */}
        {isFallback && (
          <div className="p-3.5 rounded-lg bg-amber-950/20 border border-amber-900/40 flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs font-mono text-amber-300/90">
            <div className="flex items-start gap-2">
              <AlertTriangle className="w-4 h-4 text-amber-400 shrink-0 mt-0.5" />
              <span className="leading-relaxed">
                Policy was indexed in fallback mode. Click <strong>Re-analyze Clauses</strong> above to run deep Gemma evaluation.
              </span>
            </div>
            <button
              onClick={handleReanalyze}
              disabled={analyzing}
              className="w-full sm:w-auto px-3.5 py-2 sm:py-1 rounded-lg bg-amber-500/20 hover:bg-amber-500/30 active:bg-amber-500/40 text-amber-200 border border-amber-500/40 text-xs sm:text-[11px] cursor-pointer whitespace-nowrap min-h-[36px] sm:min-h-0 flex items-center justify-center active:scale-95 transition-all"
            >
              Analyze Now
            </button>
          </div>
        )}

        {/* Executive Summary */}
        {analysis?.summary && (
          <div className="p-3.5 rounded-lg bg-zinc-950 border border-zinc-800/80 space-y-1.5 text-xs">
            <div className="font-mono text-[11px] uppercase tracking-wider text-zinc-500 font-semibold flex flex-wrap items-center justify-between gap-1">
              <span>Policy Overview</span>
              {analysis.model_id && (
                <span className="text-[10px] text-zinc-600 font-normal lowercase">
                  model: {analysis.model_id}
                </span>
              )}
            </div>
            <p className="text-zinc-300 leading-relaxed">{analysis.summary}</p>
          </div>
        )}

        {/* Disclaimer Note */}
        <div className="flex items-start sm:items-center gap-2 text-[11px] text-zinc-500 pt-1 font-mono leading-relaxed">
          <Info className="w-3.5 h-3.5 text-zinc-500 shrink-0 mt-0.5 sm:mt-0" />
          <span>Informational analysis only. Every finding is tied to verbatim excerpts verified against the raw policy text.</span>
        </div>
      </div>

      {/* Tabs */}
      <div className="grid grid-cols-4 gap-1 sm:flex sm:items-center sm:gap-1.5 border-b border-zinc-800 pb-2 text-[11px] sm:text-xs font-mono">
        <button
          onClick={() => setActiveTab('findings')}
          className={`w-full sm:w-auto px-1 sm:px-3 py-2 sm:py-1.5 rounded-lg justify-center whitespace-nowrap min-h-[36px] sm:min-h-0 flex items-center transition-all cursor-pointer active:scale-95 ${
            activeTab === 'findings'
              ? 'bg-zinc-100 text-zinc-950 font-medium shadow-xs'
              : 'text-zinc-400 hover:text-zinc-200 hover:bg-zinc-900 active:bg-zinc-800'
          }`}
        >
          Clauses ({findings.length})
        </button>

        <button
          onClick={() => setActiveTab('diff')}
          className={`w-full sm:w-auto px-1 sm:px-3 py-2 sm:py-1.5 rounded-lg justify-center whitespace-nowrap min-h-[36px] sm:min-h-0 flex items-center transition-all cursor-pointer active:scale-95 ${
            activeTab === 'diff'
              ? 'bg-zinc-100 text-zinc-950 font-medium shadow-xs'
              : 'text-zinc-400 hover:text-zinc-200 hover:bg-zinc-900 active:bg-zinc-800'
          }`}
        >
          Diffs ({changes.length})
        </button>

        <button
          onClick={() => setActiveTab('history')}
          className={`w-full sm:w-auto px-1 sm:px-3 py-2 sm:py-1.5 rounded-lg justify-center whitespace-nowrap min-h-[36px] sm:min-h-0 flex items-center transition-all cursor-pointer active:scale-95 ${
            activeTab === 'history'
              ? 'bg-zinc-100 text-zinc-950 font-medium shadow-xs'
              : 'text-zinc-400 hover:text-zinc-200 hover:bg-zinc-900 active:bg-zinc-800'
          }`}
        >
          Log ({history.length})
        </button>

        <button
          onClick={() => setActiveTab('raw')}
          className={`w-full sm:w-auto px-1 sm:px-3 py-2 sm:py-1.5 rounded-lg justify-center whitespace-nowrap min-h-[36px] sm:min-h-0 flex items-center transition-all cursor-pointer active:scale-95 ${
            activeTab === 'raw'
              ? 'bg-zinc-100 text-zinc-950 font-medium shadow-xs'
              : 'text-zinc-400 hover:text-zinc-200 hover:bg-zinc-900 active:bg-zinc-800'
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
              <div className="p-6 sm:p-8 text-center rounded-xl panel border border-amber-900/40 bg-amber-950/10 text-xs font-mono space-y-3">
                <AlertTriangle className="w-6 h-6 text-amber-400 mx-auto mb-1" />
                <div className="font-semibold text-zinc-200 text-sm">Clause AI Analysis Deferred (Fallback Mode)</div>
                <div className="text-zinc-400 max-w-lg mx-auto text-xs leading-relaxed">
                  {analysis?.summary || 'Policy successfully extracted and indexed. AI clause evaluation is currently in fallback mode due to free-tier rate limits or unconfigured credentials. Deterministic versioning, hashing, and diff monitoring remain 100% active.'}
                </div>
                <button
                  onClick={handleReanalyze}
                  disabled={analyzing}
                  className="w-full sm:w-auto px-4 py-2.5 sm:py-1.5 rounded-lg bg-zinc-100 hover:bg-white text-zinc-950 font-medium text-xs font-mono inline-flex items-center justify-center gap-1.5 cursor-pointer transition-all active:scale-95 min-h-[40px] sm:min-h-0"
                >
                  <RefreshCw className="w-3.5 h-3.5" />
                  <span>Re-analyze Clauses Now</span>
                </button>
              </div>
            ) : (
              <div className="p-6 sm:p-8 text-center rounded-xl panel text-zinc-400 text-xs font-mono space-y-1">
                <CheckCircle2 className="w-5 h-5 text-emerald-400 mx-auto mb-1" />
                <div className="font-semibold text-zinc-200 text-sm">No Notable High-Risk Clauses Flagged</div>
                <div className="text-zinc-500 max-w-md mx-auto text-[11px] leading-relaxed">
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
          <div className="flex flex-col xs:flex-row xs:items-center justify-between gap-1 text-xs font-mono text-zinc-500 border-b border-zinc-800 pb-2">
            <span>Snapshot Baseline ({rawSnapshotText.length.toLocaleString()} characters)</span>
            <span className="break-all">ID: {policy.latest_snapshot_id}</span>
          </div>
          <pre className="font-mono text-xs text-zinc-300 whitespace-pre-wrap leading-relaxed max-h-[450px] sm:max-h-[600px] overflow-y-auto p-3 rounded-lg bg-zinc-950 border border-zinc-800/80 break-words overflow-x-auto">
            {rawSnapshotText || 'No text content available.'}
          </pre>
        </div>
      )}
    </div>
  );
}
