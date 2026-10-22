import React, { useState } from 'react';
import { ChevronDown, ChevronUp, Check, Copy } from 'lucide-react';

const CATEGORY_NAMES = {
  renewal: 'Auto-Renewal',
  cancellation: 'Cancellation',
  data: 'Data & Privacy',
  price_change: 'Price Modification',
  disputes: 'Disputes & Arbitration',
  liability: 'Liability Limit',
  termination: 'Account Termination',
  safety: 'Health & Safety Disclaimers',
  other: 'General Clause',
};

const SEVERITY_STYLES = {
  high: 'bg-rose-950/40 text-rose-300 border-rose-900/60',
  medium: 'bg-amber-950/40 text-amber-300 border-amber-900/60',
  low: 'bg-zinc-800 text-zinc-300 border-zinc-700',
  uncertain: 'bg-zinc-900 text-zinc-400 border-zinc-800',
};

export default function FindingCard({ finding }) {
  const [expanded, setExpanded] = useState(false);
  const [copied, setCopied] = useState(false);

  const categoryLabel = CATEGORY_NAMES[finding.category] || CATEGORY_NAMES.other;
  const severityClass = SEVERITY_STYLES[finding.severity] || SEVERITY_STYLES.uncertain;
  const isLongExcerpt = finding.exact_excerpt && finding.exact_excerpt.length > 200;

  const handleCopyQuote = () => {
    if (finding.exact_excerpt) {
      navigator.clipboard.writeText(finding.exact_excerpt);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  return (
    <div className="panel panel-hover rounded-xl p-5 border flex flex-col justify-between gap-3">
      <div>
        {/* Header tags */}
        <div className="flex items-center justify-between gap-2 flex-wrap mb-3">
          <span className="text-xs font-mono font-medium text-zinc-300 bg-zinc-900 border border-zinc-800 px-2 py-0.5 rounded">
            {categoryLabel}
          </span>

          <div className="flex items-center gap-2">
            <span className={`text-[11px] font-mono px-2 py-0.5 rounded border capitalize ${severityClass}`}>
              {finding.severity} concern
            </span>
            <span className="text-[11px] font-mono text-emerald-400 bg-emerald-950/30 border border-emerald-900/40 px-1.5 py-0.5 rounded">
              Verified quote
            </span>
          </div>
        </div>

        {/* Verbatim Quote */}
        <div className="p-3.5 rounded-lg bg-zinc-950 border border-zinc-800/80 mb-3 text-xs relative group">
          <div className="flex items-center justify-between text-[11px] font-mono text-zinc-500 uppercase tracking-wider mb-1.5">
            <span>Source excerpt</span>
            <button
              onClick={handleCopyQuote}
              className="text-zinc-500 hover:text-zinc-300 transition-colors p-1"
              title="Copy quote"
            >
              {copied ? <Check className="w-3 h-3 text-emerald-400" /> : <Copy className="w-3 h-3" />}
            </button>
          </div>
          <p className="font-mono text-zinc-300 leading-relaxed">
            "{expanded || !isLongExcerpt ? finding.exact_excerpt : `${finding.exact_excerpt.slice(0, 200)}...`}"
          </p>
          {isLongExcerpt && (
            <button
              onClick={() => setExpanded(!expanded)}
              className="mt-2 text-[11px] text-zinc-400 hover:text-zinc-200 font-mono flex items-center gap-1 cursor-pointer"
            >
              {expanded ? (
                <>
                  <ChevronUp className="w-3 h-3" /> Show less
                </>
              ) : (
                <>
                  <ChevronDown className="w-3 h-3" /> Show full excerpt
                </>
              )}
            </button>
          )}
        </div>

        {/* Breakdown */}
        <div className="space-y-2 text-xs">
          <div>
            <span className="font-semibold text-zinc-300">Plain text statement: </span>
            <span className="text-zinc-400 leading-relaxed">{finding.explanation}</span>
          </div>

          <div>
            <span className="font-semibold text-zinc-300">Potential consumer impact: </span>
            <span className="text-zinc-400 leading-relaxed">{finding.why_it_might_matter}</span>
          </div>

          {finding.uncertainty && (
            <div className="p-2 rounded bg-zinc-900 border border-zinc-800 text-[11px] text-zinc-400 font-mono">
              <strong className="text-zinc-300">Note: </strong>
              {finding.uncertainty}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
