import React from 'react';
import { History, Clock } from 'lucide-react';
import { formatLocalDate } from '../lib/dateUtils';

export default function VersionHistory({ events = [], onViewSnapshot }) {
  if (!events || events.length === 0) {
    return (
      <div className="p-8 text-center rounded-xl panel text-zinc-500 text-xs font-mono">
        No check history recorded yet for this policy.
      </div>
    );
  }

  const formatTime = (isoString) => formatLocalDate(isoString);

  return (
    <div className="space-y-3">
      <div className="flex items-center gap-2 text-xs font-mono font-semibold text-zinc-400 mb-1">
        <History className="w-3.5 h-3.5 text-zinc-400" />
        <span>Check Events & Snapshot History</span>
      </div>

      <div className="border-l border-zinc-800 ml-3 pl-4 space-y-4">
        {events.map((evt, idx) => {
          let badgeClass = 'bg-zinc-800 text-zinc-300 border-zinc-700';
          let label = 'Check event';

          if (evt.status === 'changed') {
            if (!evt.old_snapshot_id) {
              badgeClass = 'bg-blue-950/40 text-blue-400 border-blue-900/50';
              label = 'Initial baseline created';
            } else {
              badgeClass = 'bg-emerald-950/40 text-emerald-400 border-emerald-900/50';
              label = 'Version updated (text changed)';
            }
          } else if (evt.status === 'reanalyzed') {
            badgeClass = 'bg-indigo-950/40 text-indigo-400 border-indigo-900/50';
            label = 'Analysis refreshed (no text change)';
          } else if (evt.status === 'unchanged') {
            badgeClass = 'bg-zinc-900 text-zinc-400 border-zinc-800';
            label = 'Unchanged (content match)';
          } else if (evt.status === 'extraction_failed') {
            badgeClass = 'bg-rose-950/40 text-rose-400 border-rose-900/50';
            label = 'Extraction failed (baseline kept)';
          }

          return (
            <div key={evt.id || idx} className="relative group">
              {/* Dot on line */}
              <div className="absolute -left-[21px] top-1.5 w-2 h-2 rounded-full bg-zinc-600 border border-zinc-900" />

              <div className="panel rounded-lg p-3 border space-y-1.5 text-xs">
                <div className="flex items-center justify-between gap-2 flex-wrap">
                  <div className="flex items-center gap-2">
                    <span className={`text-[11px] font-mono px-2 py-0.5 rounded border ${badgeClass}`}>
                      {label}
                    </span>
                    <span className="text-[11px] font-mono text-zinc-500 flex items-center gap-1">
                      <Clock className="w-3 h-3" />
                      {formatTime(evt.checked_at)}
                    </span>
                  </div>

                  {evt.new_snapshot_id && onViewSnapshot && (
                    <button
                      onClick={() => onViewSnapshot(evt.new_snapshot_id)}
                      className="text-[11px] font-mono text-zinc-400 hover:text-zinc-200 transition-colors cursor-pointer"
                    >
                      View text snapshot →
                    </button>
                  )}
                </div>

                {evt.message && (
                  <p className="text-zinc-300 font-mono text-xs leading-relaxed">{evt.message}</p>
                )}

                {(evt.old_snapshot_id || evt.new_snapshot_id) && (
                  <div className="flex items-center gap-3 text-[11px] text-zinc-500 font-mono pt-1">
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
