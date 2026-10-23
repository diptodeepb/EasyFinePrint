import React, { useState, useEffect } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Menu, X, ArrowRight } from 'lucide-react';

export default function Header() {
  const location = useLocation();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  // Close mobile menu on route change
  useEffect(() => {
    setMobileMenuOpen((open) => (open ? false : open));
  }, [location.pathname]);

  const isCurrent = (path) => location.pathname === path;

  return (
    <header className="sticky top-0 z-50 w-full border-b border-zinc-800/80 bg-[#09090b]/90 backdrop-blur-md pt-[env(safe-area-inset-top,0px)] transition-all">
      <div className="max-w-6xl mx-auto px-3.5 sm:px-6 h-15 flex items-center justify-between gap-3">
        {/* Left: Brand Logo & Title */}
        <div className="flex items-center gap-3 shrink-0">
          <Link
            to="/"
            className="flex items-center gap-2.5 group active:scale-95 transition-transform"
            aria-label="EasyFinePrint Home"
          >
            <img
              src="/logo.svg"
              alt="EasyFinePrint Logo"
              className="w-7 h-7 rounded-lg border border-zinc-700/80 shadow-sm transition-transform duration-200 group-hover:scale-105"
            />
            <div className="flex items-center gap-1.5 sm:gap-2">
              <span className="font-semibold text-sm sm:text-base text-zinc-100 tracking-tight group-hover:text-white transition-colors">
                EasyFinePrint
              </span>
              <span className="text-[10px] font-mono text-zinc-400 bg-zinc-900 border border-zinc-800 px-1.5 py-0.5 rounded">
                v1.0
              </span>
            </div>
          </Link>
        </div>

        {/* Center: Desktop Navigation */}
        <nav className="hidden md:flex items-center gap-1 sm:gap-1.5">
          <Link
            to="/"
            className={`text-xs font-mono transition-all px-3 py-1.5 rounded-md min-h-[36px] flex items-center active:scale-95 ${
              isCurrent('/')
                ? 'text-zinc-100 bg-zinc-900 border border-zinc-800 shadow-xs'
                : 'text-zinc-400 hover:text-zinc-200 hover:bg-zinc-900/40'
            }`}
          >
            Dashboard
          </Link>

          <Link
            to="/terms"
            className={`text-xs font-mono transition-all px-3 py-1.5 rounded-md min-h-[36px] flex items-center active:scale-95 ${
              isCurrent('/terms')
                ? 'text-zinc-100 bg-zinc-900 border border-zinc-800 shadow-xs'
                : 'text-zinc-400 hover:text-zinc-200 hover:bg-zinc-900/40'
            }`}
          >
            Terms of Use
          </Link>

          <Link
            to="/privacy"
            className={`text-xs font-mono transition-all px-3 py-1.5 rounded-md min-h-[36px] flex items-center active:scale-95 ${
              isCurrent('/privacy')
                ? 'text-zinc-100 bg-zinc-900 border border-zinc-800 shadow-xs'
                : 'text-zinc-400 hover:text-zinc-200 hover:bg-zinc-900/40'
            }`}
          >
            Privacy Policy
          </Link>
        </nav>

        {/* Right Actions: GitHub */}
        <div className="hidden md:flex items-center gap-2.5">
          <a
            href="https://github.com/diptodeepb/EasyFinePrint"
            target="_blank"
            rel="noreferrer"
            className="flex items-center gap-1.5 text-xs font-mono text-zinc-400 hover:text-zinc-100 transition-all px-2.5 py-1.5 rounded-md min-h-[36px] hover:bg-zinc-900/60 border border-transparent hover:border-zinc-800 active:scale-95"
            title="View Source on GitHub"
          >
            <svg className="w-3.5 h-3.5 fill-current shrink-0" viewBox="0 0 24 24">
              <path
                fillRule="evenodd"
                clipRule="evenodd"
                d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.53 1.032 1.53 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z"
              />
            </svg>
            <span className="hidden lg:inline">GitHub</span>
          </a>
        </div>

        {/* Mobile Hamburger Toggle */}
        <div className="flex md:hidden items-center gap-2">
          <button
            type="button"
            onClick={() => setMobileMenuOpen((prev) => !prev)}
            className="p-2 rounded-md bg-zinc-900 border border-zinc-800 text-zinc-300 hover:text-white transition-colors cursor-pointer active:scale-95 min-h-[38px] min-w-[38px] flex items-center justify-center"
            aria-label="Toggle navigation menu"
            aria-expanded={mobileMenuOpen}
          >
            {mobileMenuOpen ? <X className="w-4 h-4" /> : <Menu className="w-4 h-4" />}
          </button>
        </div>
      </div>

      {/* Mobile Menu Drawer */}
      {mobileMenuOpen && (
        <div className="md:hidden border-t border-zinc-800/80 bg-[#09090b]/98 backdrop-blur-xl px-4 py-4 space-y-4 animate-in slide-in-from-top-2 duration-150">
          <nav className="flex flex-col space-y-1">
            <Link
              to="/"
              className={`px-3 py-2.5 rounded-lg text-xs font-mono transition-colors flex items-center justify-between ${
                isCurrent('/')
                  ? 'bg-zinc-900 text-white font-semibold border border-zinc-800'
                  : 'text-zinc-400 hover:text-white hover:bg-zinc-900/50'
              }`}
            >
              <span>Dashboard</span>
              <ArrowRight className="w-3.5 h-3.5 text-zinc-600" />
            </Link>

            <Link
              to="/terms"
              className={`px-3 py-2.5 rounded-lg text-xs font-mono transition-colors flex items-center justify-between ${
                isCurrent('/terms')
                  ? 'bg-zinc-900 text-white font-semibold border border-zinc-800'
                  : 'text-zinc-400 hover:text-white hover:bg-zinc-900/50'
              }`}
            >
              <span>Terms of Use</span>
              <ArrowRight className="w-3.5 h-3.5 text-zinc-600" />
            </Link>

            <Link
              to="/privacy"
              className={`px-3 py-2.5 rounded-lg text-xs font-mono transition-colors flex items-center justify-between ${
                isCurrent('/privacy')
                  ? 'bg-zinc-900 text-white font-semibold border border-zinc-800'
                  : 'text-zinc-400 hover:text-white hover:bg-zinc-900/50'
              }`}
            >
              <span>Privacy Policy</span>
              <ArrowRight className="w-3.5 h-3.5 text-zinc-600" />
            </Link>
          </nav>

          {/* GitHub link */}
          <div className="flex items-center justify-end pt-2 border-t border-zinc-800 text-xs font-mono text-zinc-400">
            <a
              href="https://github.com/diptodeepb/EasyFinePrint"
              target="_blank"
              rel="noreferrer"
              className="hover:text-white transition-colors"
            >
              GitHub ↗
            </a>
          </div>
        </div>
      )}
    </header>
  );
}
