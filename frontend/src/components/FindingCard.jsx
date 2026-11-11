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
  high: 'bg-rose-500/10 text-rose-800 border-rose-500/30 dark:bg-rose-950/40 dark:text-rose-300 dark:border-rose-900/60',
  medium: 'bg-amber-500/10 text-amber-800 border-amber-500/30 dark:bg-amber-950/40 dark:text-amber-300 dark:border-amber-900/60',
  low: 'bg-[#ece5d8] text-[#5c5549] border-[#d5cbba] dark:bg-zinc-800 dark:text-zinc-300 dark:border-zinc-700',
  uncertain: 'bg-[#ece5d8] text-[#78716c] border-[#d5cbba] dark:bg-zinc-900 dark:text-zinc-400 dark:border-zinc-800',
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
    <div className="panel panel-hover rounded-xl p-4 sm:p-5 border flex flex-col justify-between gap-3">
      <div>
        {/* Header tags */}
        <div className="flex items-center justify-between gap-2 flex-wrap mb-3">
          <span className="text-xs font-mono font-medium text-[#1c1917] bg-[#ece5d8] border border-[#d5cbba] dark:text-zinc-300 dark:bg-zinc-900 dark:border-zinc-800 px-2.5 py-1 rounded-md">
            {categoryLabel}
          </span>

          <div className="flex items-center gap-1.5 flex-wrap">
            <span className={`text-[11px] font-mono px-2 py-0.5 rounded border capitalize ${severityClass}`}>
              {finding.severity} concern
            </span>
            <span className="text-[11px] font-mono text-emerald-800 bg-emerald-500/10 border border-emerald-500/30 dark:text-emerald-400 dark:bg-emerald-950/30 dark:border-emerald-900/40 px-1.5 py-0.5 rounded">
              Verified quote
            </span>
          </div>
        </div>

        {/* Verbatim Quote */}
        <div className="p-3.5 rounded-lg bg-[#faf5ec] dark:bg-zinc-950 border border-[#d5cbba] dark:border-zinc-800/80 mb-3 text-xs relative group">
          <div className="flex items-center justify-between text-[11px] font-mono text-[#78716c] dark:text-zinc-500 uppercase tracking-wider mb-1.5">
            <span>Source excerpt</span>
            <button
              onClick={handleCopyQuote}
              className="text-[#5c5549] hover:text-[#1c1917] active:text-[#1c1917] dark:text-zinc-400 dark:hover:text-zinc-200 dark:active:text-white transition-colors p-1.5 -mr-1 -mt-1 rounded-md hover:bg-[#ded6c6]/60 dark:hover:bg-zinc-800 active:bg-[#d5cbba] dark:active:bg-zinc-700 min-w-[32px] min-h-[32px] flex items-center justify-center cursor-pointer"
              title="Copy quote"
              aria-label="Copy quote"
            >
              {copied ? <Check className="w-3.5 h-3.5 text-emerald-600 dark:text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
            </button>
          </div>
          <p className="font-mono text-[#292524] dark:text-zinc-300 leading-relaxed break-words">
            "{expanded || !isLongExcerpt ? finding.exact_excerpt : `${finding.exact_excerpt.slice(0, 200)}...`}"
          </p>
          {isLongExcerpt && (
            <button
              onClick={() => setExpanded(!expanded)}
              className="mt-2.5 text-xs text-[#5c5549] hover:text-[#1c1917] dark:text-zinc-400 dark:hover:text-zinc-200 font-mono flex items-center gap-1 cursor-pointer py-1 active:scale-95 transition-transform"
            >
              {expanded ? (
                <>
                  <ChevronUp className="w-3.5 h-3.5" /> Show less
                </>
              ) : (
                <>
                  <ChevronDown className="w-3.5 h-3.5" /> Show full excerpt
                </>
              )}
            </button>
          )}
        </div>

        {/* Breakdown */}
        <div className="space-y-2.5 text-xs">
          <div>
            <span className="font-semibold text-[#1c1917] dark:text-zinc-300">Plain text statement: </span>
            <span className="text-[#5c5549] dark:text-zinc-400 leading-relaxed">{finding.explanation}</span>
          </div>

          <div>
            <span className="font-semibold text-[#1c1917] dark:text-zinc-300">Potential consumer impact: </span>
            <span className="text-[#5c5549] dark:text-zinc-400 leading-relaxed">{finding.why_it_might_matter}</span>
          </div>

          {finding.uncertainty && (
            <div className="p-2.5 rounded-lg bg-[#ece5d8] dark:bg-zinc-900 border border-[#d5cbba] dark:border-zinc-800 text-[11px] text-[#5c5549] dark:text-zinc-400 font-mono break-words">
              <strong className="text-[#1c1917] dark:text-zinc-300">Note: </strong>
              {finding.uncertainty}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
