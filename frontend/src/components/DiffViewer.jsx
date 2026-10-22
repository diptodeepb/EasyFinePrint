import React, { useState } from 'react';
import { Plus, Minus, RefreshCw } from 'lucide-react';

export default function DiffViewer({ changes = [], diffSummary = null, analysisSummary = '' }) {
  const [filter, setFilter] = useState('all');

  const additionsCount = diffSummary?.additions ?? changes.filter((c) => c.change_type === 'addition').length;
  const removalsCount = diffSummary?.removals ?? changes.filter((c) => c.change_type === 'removal').length;
  const modificationsCount = diffSummary?.modifications ?? changes.filter((c) => c.change_type === 'modification').length;

  const filteredChanges = changes.filter((c) => {
    if (filter === 'all') return true;
    return c.change_type === filter;
  });

  return (
    <div className="space-y-4">
      {/* Diff Controls & Counters */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2.5 pb-2 border-b border-zinc-800">
        <div className="flex flex-wrap items-center gap-1.5 text-xs font-mono">
          <span className="text-zinc-500 text-[11px] mr-1">Diff stats:</span>
          <span className="px-2 py-0.5 rounded bg-zinc-900 border border-zinc-800 text-zinc-300">
            {changes.length} total
          </span>
          <span className="px-2 py-0.5 rounded bg-emerald-950/40 border border-emerald-900/50 text-emerald-400">
            +{additionsCount}
          </span>
          <span className="px-2 py-0.5 rounded bg-rose-950/40 border border-rose-900/50 text-rose-400">
            -{removalsCount}
          </span>
          <span className="px-2 py-0.5 rounded bg-amber-950/40 border border-amber-900/50 text-amber-400">
            ~{modificationsCount}
          </span>
        </div>

        {/* Filter buttons */}
        <div className="flex flex-wrap items-center gap-1 text-xs">
          {['all', 'addition', 'removal', 'modification'].map((type) => (
            <button
              key={type}
              onClick={() => setFilter(type)}
              className={`px-3 py-1.5 sm:px-2.5 sm:py-1 rounded text-xs font-mono capitalize transition-all cursor-pointer min-h-[32px] sm:min-h-0 flex items-center justify-center active:scale-95 ${
                filter === type
                  ? 'bg-zinc-100 text-zinc-950 font-medium'
                  : 'bg-zinc-900 text-zinc-400 hover:text-zinc-200 border border-zinc-800'
              }`}
            >
              {type}
            </button>
          ))}
        </div>
      </div>

      {/* Change Summary Card */}
      {analysisSummary && (
        <div className="p-3.5 rounded-lg bg-zinc-900 border border-zinc-800 text-xs text-zinc-300 space-y-1">
          <div className="font-mono text-[11px] uppercase tracking-wider text-zinc-500 font-semibold">
            Version Delta Analysis
          </div>
          <p className="leading-relaxed">{analysisSummary}</p>
        </div>
      )}

      {/* Changes list */}
      {filteredChanges.length === 0 ? (
        <div className="p-8 text-center rounded-xl panel text-zinc-500 text-xs font-mono">
          No changes match the selected filter.
        </div>
      ) : (
        <div className="space-y-3">
          {filteredChanges.map((chg) => (
            <div
              key={chg.change_id}
              className="panel rounded-lg overflow-hidden border"
            >
              {/* Header Bar */}
              <div className="px-3 sm:px-4 py-2.5 sm:py-2 bg-zinc-950 border-b border-zinc-800 flex flex-wrap items-center justify-between gap-2 text-xs font-mono">
                <div className="flex flex-wrap items-center gap-2">
                  <span className="text-zinc-500 font-semibold">@@ {chg.change_id} @@</span>
                  {chg.change_type === 'addition' && (
                    <span className="text-emerald-400 bg-emerald-950/40 px-1.5 py-0.5 rounded border border-emerald-900/40 flex items-center gap-1">
                      <Plus className="w-3 h-3" /> Added clause
                    </span>
                  )}
                  {chg.change_type === 'removal' && (
                    <span className="text-rose-400 bg-rose-950/40 px-1.5 py-0.5 rounded border border-rose-900/40 flex items-center gap-1">
                      <Minus className="w-3 h-3" /> Removed clause
                    </span>
                  )}
                  {chg.change_type === 'modification' && (
                    <span className="text-amber-400 bg-amber-950/40 px-1.5 py-0.5 rounded border border-amber-900/40 flex items-center gap-1">
                      <RefreshCw className="w-3 h-3" /> Modified wording
                    </span>
                  )}
                </div>

                {chg.significance && (
                  <span className="text-[11px] text-zinc-400 capitalize bg-zinc-900 px-2 py-0.5 rounded border border-zinc-800">
                    {chg.significance} significance
                  </span>
                )}
              </div>

              {/* Diff blocks */}
              <div className="p-3 space-y-2 text-xs font-mono">
                {chg.old_text && (
                  <div className="p-2.5 rounded bg-rose-950/20 border-l-2 border-rose-500 text-rose-200 whitespace-pre-wrap leading-relaxed break-words overflow-x-auto">
                    <span className="select-none text-rose-500 font-bold mr-2">-</span>
                    {chg.old_text}
                  </div>
                )}

                {chg.new_text && (
                  <div className="p-2.5 rounded bg-emerald-950/20 border-l-2 border-emerald-500 text-emerald-200 whitespace-pre-wrap leading-relaxed break-words overflow-x-auto">
                    <span className="select-none text-emerald-500 font-bold mr-2">+</span>
                    {chg.new_text}
                  </div>
                )}
              </div>

              {/* Explanation section */}
              {(chg.explanation || chg.possible_implication) && (
                <div className="px-3 sm:px-4 py-3 border-t border-zinc-800 bg-zinc-950/50 space-y-1.5 text-xs">
                  {chg.explanation && (
                    <div>
                      <span className="font-semibold text-zinc-300">Wording change: </span>
                      <span className="text-zinc-400 leading-relaxed">{chg.explanation}</span>
                    </div>
                  )}
                  {chg.possible_implication && (
                    <div>
                      <span className="font-semibold text-zinc-300">Practical impact: </span>
                      <span className="text-zinc-400 leading-relaxed">{chg.possible_implication}</span>
                    </div>
                  )}
                  {chg.uncertainty && (
                    <div className="text-[11px] font-mono text-zinc-500 break-words">
                      Note: {chg.uncertainty}
                    </div>
                  )}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
