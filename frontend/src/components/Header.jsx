import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { FileText, ExternalLink } from 'lucide-react';
import { api } from '../lib/api';

export default function Header() {
  const [health, setHealth] = useState(null);

  useEffect(() => {
    let mounted = true;
    api.getHealth()
      .then((data) => {
        if (mounted) setHealth(data);
      })
      .catch(() => {
        if (mounted) setHealth({ status: 'offline' });
      });
    return () => {
      mounted = false;
    };
  }, []);

  return (
    <header className="sticky top-0 z-40 w-full border-b border-zinc-800 bg-[#09090b]/90 backdrop-blur-md">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 h-14 flex items-center justify-between">
        {/* Brand */}
        <Link to="/" className="flex items-center gap-2.5 group">
          <div className="w-7 h-7 rounded-md bg-zinc-800 border border-zinc-700 flex items-center justify-center">
            <FileText className="w-3.5 h-3.5 text-zinc-200" />
          </div>
          <div className="flex items-center gap-2">
            <span className="font-semibold text-sm text-zinc-100 tracking-tight">EasyFinePrint</span>
            <span className="text-[10px] font-mono text-zinc-400 bg-zinc-900 border border-zinc-800 px-1.5 py-0.5 rounded">
              v1.0
            </span>
          </div>
        </Link>

        {/* Status & Navigation */}
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2 px-2.5 py-1 rounded-md bg-zinc-900 border border-zinc-800 text-xs font-mono">
            <span
              className={`w-1.5 h-1.5 rounded-full ${
                health?.status === 'healthy' ? 'bg-emerald-400' : 'bg-rose-400'
              }`}
            />
            <span className="text-zinc-400 text-[11px]">
              {health?.status === 'healthy' ? 'Engine ready' : 'Engine offline'}
            </span>
          </div>

          <nav className="flex items-center gap-2">
            <Link
              to="/"
              className="text-xs text-zinc-400 hover:text-zinc-100 transition-colors px-2 py-1"
            >
              Dashboard
            </Link>
            <a
              href="https://github.com/diptodeepb/EasyFinePrint"
              target="_blank"
              rel="noreferrer"
              className="flex items-center gap-1.5 text-xs text-zinc-400 hover:text-zinc-100 transition-colors px-2 py-1"
            >
              <svg className="w-3.5 h-3.5 fill-current" viewBox="0 0 24 24">
                <path fillRule="evenodd" clipRule="evenodd" d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.53 1.032 1.53 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z" />
              </svg>
              <span>GitHub</span>
            </a>
          </nav>
        </div>
      </div>
    </header>
  );
}
