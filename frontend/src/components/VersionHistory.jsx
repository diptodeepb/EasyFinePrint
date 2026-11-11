import React from 'react';
import { History, Clock } from 'lucide-react';
import { formatLocalDate } from '../lib/dateUtils';

export default function VersionHistory({ events = [], onViewSnapshot }) {
  if (!events || events.length === 0) {
    return (
      <div className="p-8 text-center rounded-xl panel text-[#78716c] dark:text-zinc-500 text-xs font-mono">
        No check history recorded yet for this policy.
      </div>
    );
  }

  const formatTime = (isoString) => formatLocalDate(isoString);

  return (
    <div className="space-y-3">
      <div className="flex items-center gap-2 text-xs font-mono font-semibold text-[#5c5549] dark:text-zinc-400 mb-1">
        <History className="w-3.5 h-3.5 text-[#5c5549] dark:text-zinc-400" />
        <span>Check Events &amp; Snapshot History</span>
      </div>

      <div className="border-l border-[#d5cbba] dark:border-zinc-800 ml-2.5 sm:ml-3 pl-3 sm:pl-4 space-y-3 sm:space-y-4">
        {events.map((evt, idx) => {
          let badgeClass = 'bg-[#ece5d8] text-[#5c5549] border-[#d5cbba] dark:bg-zinc-800 dark:text-zinc-300 dark:border-zinc-700';
          let label = 'Check event';

          if (evt.status === 'changed') {
            if (!evt.old_snapshot_id) {
              badgeClass = 'bg-sky-500/10 text-sky-800 border-sky-500/30 dark:bg-blue-950/40 dark:text-blue-400 dark:border-blue-900/50';
              label = 'Initial baseline created';
            } else {
              badgeClass = 'bg-emerald-500/10 text-emerald-800 border-emerald-500/30 dark:bg-emerald-950/40 dark:text-emerald-400 dark:border-emerald-900/50';
              label = 'Version updated (text changed)';
            }
          } else if (evt.status === 'reanalyzed') {
            badgeClass = 'bg-indigo-500/10 text-indigo-800 border-indigo-500/30 dark:bg-indigo-950/40 dark:text-indigo-400 dark:border-indigo-900/50';
            label = 'Analysis refreshed (no text change)';
          } else if (evt.status === 'unchanged') {
            badgeClass = 'bg-[#ece5d8] text-[#78716c] border-[#d5cbba] dark:bg-zinc-900 dark:text-zinc-400 dark:border-zinc-800';
            label = 'Unchanged (content match)';
          } else if (evt.status === 'extraction_failed') {
            badgeClass = 'bg-rose-500/10 text-rose-800 border-rose-500/30 dark:bg-rose-950/40 dark:text-rose-400 dark:border-rose-900/50';
            label = 'Extraction failed (baseline kept)';
          }

          return (
            <div key={evt.id || idx} className="relative group">
              {/* Dot on line */}
              <div className="absolute -left-[17px] sm:-left-[21px] top-2 w-2 h-2 rounded-full bg-[#78716c] border border-[#faf5ec] dark:bg-zinc-500 dark:border-zinc-900" />

              <div className="panel rounded-lg p-3 sm:p-3.5 border space-y-2 text-xs">
                <div className="flex flex-wrap items-center justify-between gap-2">
                  <div className="flex flex-wrap items-center gap-1.5 sm:gap-2">
                    <span className={`text-[11px] font-mono px-2 py-0.5 rounded border ${badgeClass}`}>
                      {label}
                    </span>
                    <span className="text-[11px] font-mono text-[#78716c] dark:text-zinc-500 flex items-center gap-1">
                      <Clock className="w-3 h-3 shrink-0" />
                      {formatTime(evt.checked_at)}
                    </span>
                  </div>

                  {evt.new_snapshot_id && onViewSnapshot && (
                    <button
                      onClick={() => onViewSnapshot(evt.new_snapshot_id)}
                      className="text-xs sm:text-[11px] font-mono text-[#5c5549] hover:text-[#1c1917] dark:text-zinc-300 dark:hover:text-white transition-colors cursor-pointer py-1 active:scale-95 flex items-center gap-1"
                    >
                      <span>View text snapshot</span>
                      <span>&rarr;</span>
                    </button>
                  )}
                </div>

                {evt.message && (
                  <p className="text-[#292524] dark:text-zinc-300 font-mono text-xs leading-relaxed break-words">{evt.message}</p>
                )}

                {(evt.old_snapshot_id || evt.new_snapshot_id) && (
                  <div className="flex flex-wrap items-center gap-2 sm:gap-3 text-[11px] text-[#78716c] dark:text-zinc-500 font-mono pt-1 break-all">
                    {evt.old_snapshot_id && <span>Old: {evt.old_snapshot_id}</span>}
                    {evt.new_snapshot_id && <span>New: {evt.new_snapshot_id}</span>}
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
