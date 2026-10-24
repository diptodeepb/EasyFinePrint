import React, { useState, useEffect, useRef } from "react";
import { Link, useLocation } from "react-router-dom";
import { Menu, X, ArrowRight, Star } from "lucide-react";

export default function Header() {
  const location = useLocation();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const headerRef = useRef(null);

  // Close mobile menu on route change
  useEffect(() => {
    setMobileMenuOpen(false);
  }, [location.pathname]);

  // Close mobile menu when clicking outside the navbar or pressing Escape
  useEffect(() => {
    if (!mobileMenuOpen) return;

    const handleOutsideClick = (event) => {
      if (headerRef.current && !headerRef.current.contains(event.target)) {
        setMobileMenuOpen(false);
      }
    };

    const handleKeyDown = (event) => {
      if (event.key === "Escape") {
        setMobileMenuOpen(false);
      }
    };

    document.addEventListener("mousedown", handleOutsideClick);
    document.addEventListener("touchstart", handleOutsideClick);
    document.addEventListener("keydown", handleKeyDown);

    return () => {
      document.removeEventListener("mousedown", handleOutsideClick);
      document.removeEventListener("touchstart", handleOutsideClick);
      document.removeEventListener("keydown", handleKeyDown);
    };
  }, [mobileMenuOpen]);

  const isCurrent = (path) => location.pathname === path;

  return (
    <>
      <header
        ref={headerRef}
        className="sticky top-0 z-50 w-full border-b border-zinc-800/80 bg-[#09090b]/90 backdrop-blur-md pt-[env(safe-area-inset-top,0px)] transition-all"
      >
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
                isCurrent("/")
                  ? "text-zinc-100 bg-zinc-900 border border-zinc-800 shadow-xs"
                  : "text-zinc-400 hover:text-zinc-200 hover:bg-zinc-900/40"
              }`}
            >
              Dashboard
            </Link>

            <Link
              to="/terms"
              className={`text-xs font-mono transition-all px-3 py-1.5 rounded-md min-h-[36px] flex items-center active:scale-95 ${
                isCurrent("/terms")
                  ? "text-zinc-100 bg-zinc-900 border border-zinc-800 shadow-xs"
                  : "text-zinc-400 hover:text-zinc-200 hover:bg-zinc-900/40"
              }`}
            >
              Terms of Use
            </Link>

            <Link
              to="/privacy"
              className={`text-xs font-mono transition-all px-3 py-1.5 rounded-md min-h-[36px] flex items-center active:scale-95 ${
                isCurrent("/privacy")
                  ? "text-zinc-100 bg-zinc-900 border border-zinc-800 shadow-xs"
                  : "text-zinc-400 hover:text-zinc-200 hover:bg-zinc-900/40"
              }`}
            >
              Privacy Policy
            </Link>
          </nav>

          {/* Right Actions: Star on GitHub */}
          <div className="hidden md:flex items-center gap-2.5">
            <a
              href="https://github.com/diptodeepb/EasyFinePrint"
              target="_blank"
              rel="noreferrer"
              className="flex items-center gap-1.5 text-xs font-mono text-zinc-300 hover:text-white transition-all px-2.5 py-1.5 rounded-md min-h-[36px] hover:bg-zinc-900/60 border border-zinc-800 hover:border-zinc-700 active:scale-95"
              title="Star on GitHub"
            >
              <Star className="w-3.5 h-3.5 text-amber-400 fill-none shrink-0" />
              <span>Star on GitHub</span>
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
              {mobileMenuOpen ? (
                <X className="w-4 h-4" />
              ) : (
                <Menu className="w-4 h-4" />
              )}
            </button>
          </div>
        </div>

        {/* Mobile Menu Drawer */}
        {mobileMenuOpen && (
          <div className="md:hidden border-t border-zinc-800/80 bg-[#09090b]/98 backdrop-blur-xl px-4 py-4 space-y-4 animate-in slide-in-from-top-2 duration-150">
            <nav className="flex flex-col space-y-1">
              <Link
                to="/"
                onClick={() => setMobileMenuOpen(false)}
                className={`px-3 py-2.5 rounded-lg text-xs font-mono transition-colors flex items-center justify-between ${
                  isCurrent("/")
                    ? "bg-zinc-900 text-white font-semibold border border-zinc-800"
                    : "text-zinc-400 hover:text-white hover:bg-zinc-900/50"
                }`}
              >
                <span>Dashboard</span>
                <ArrowRight className="w-3.5 h-3.5 text-zinc-600" />
              </Link>

              <Link
                to="/terms"
                onClick={() => setMobileMenuOpen(false)}
                className={`px-3 py-2.5 rounded-lg text-xs font-mono transition-colors flex items-center justify-between ${
                  isCurrent("/terms")
                    ? "bg-zinc-900 text-white font-semibold border border-zinc-800"
                    : "text-zinc-400 hover:text-white hover:bg-zinc-900/50"
                }`}
              >
                <span>Terms of Use</span>
                <ArrowRight className="w-3.5 h-3.5 text-zinc-600" />
              </Link>

              <Link
                to="/privacy"
                onClick={() => setMobileMenuOpen(false)}
                className={`px-3 py-2.5 rounded-lg text-xs font-mono transition-colors flex items-center justify-between ${
                  isCurrent("/privacy")
                    ? "bg-zinc-900 text-white font-semibold border border-zinc-800"
                    : "text-zinc-400 hover:text-white hover:bg-zinc-900/50"
                }`}
              >
                <span>Privacy Policy</span>
                <ArrowRight className="w-3.5 h-3.5 text-zinc-600" />
              </Link>
            </nav>

            {/* Star on GitHub */}
            <div className="flex items-center justify-start pt-2 border-t border-zinc-800 text-xs font-mono text-zinc-400">
              <a
                href="https://github.com/diptodeepb/EasyFinePrint"
                target="_blank"
                rel="noreferrer"
                onClick={() => setMobileMenuOpen(false)}
                className="flex items-center gap-2 px-3 py-2 rounded-lg hover:text-white hover:bg-zinc-900/50 transition-colors w-full"
                title="Star on GitHub"
              >
                <Star className="w-3.5 h-3.5 text-amber-400 fill-none shrink-0" />
                <span>Star on GitHub</span>
              </a>
            </div>
          </div>
        )}
      </header>

      {/* Mobile outside click backdrop */}
      {mobileMenuOpen && (
        <div
          className="fixed inset-0 z-40 bg-black/60 backdrop-blur-xs md:hidden transition-opacity duration-200"
          onClick={() => setMobileMenuOpen(false)}
          aria-hidden="true"
        />
      )}
    </>
  );
}
