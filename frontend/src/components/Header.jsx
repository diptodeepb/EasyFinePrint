import React, { useState, useEffect, useRef } from "react";
import { Link, useLocation } from "react-router-dom";
import { Menu, X, ArrowRight, Star } from "lucide-react";
import ThemeToggle from "./ThemeToggle";

export default function Header() {
  const location = useLocation();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const headerRef = useRef(null);

  // Close mobile menu on route change
  useEffect(() => {
    setMobileMenuOpen(false);
  }, [location.pathname]);

  // Close mobile menu on Escape key
  useEffect(() => {
    if (!mobileMenuOpen) return;

    const handleKeyDown = (event) => {
      if (event.key === "Escape") {
        setMobileMenuOpen(false);
      }
    };

    document.addEventListener("keydown", handleKeyDown);
    return () => {
      document.removeEventListener("keydown", handleKeyDown);
    };
  }, [mobileMenuOpen]);

  // Lock body scroll while mobile menu is open to prevent background scrolling
  useEffect(() => {
    if (!mobileMenuOpen) return;
    const originalOverflow = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    return () => {
      document.body.style.overflow = originalOverflow;
    };
  }, [mobileMenuOpen]);

  // Auto-close mobile menu if viewport resized to desktop width
  useEffect(() => {
    const handleResize = () => {
      if (window.innerWidth >= 768) {
        setMobileMenuOpen(false);
      }
    };
    window.addEventListener("resize", handleResize);
    return () => window.removeEventListener("resize", handleResize);
  }, []);

  const isCurrent = (path) => location.pathname === path;

  return (
    <>
      <header
        ref={headerRef}
        className="sticky top-0 z-50 w-full bg-[#ece5d8]/85 dark:bg-[#09090b]/85 backdrop-blur-md pt-[env(safe-area-inset-top,0px)] transition-colors relative"
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
                className="w-7 h-7 rounded-lg border border-[#d5cbba] dark:border-zinc-700/80 shadow-xs transition-transform duration-200 group-hover:scale-105"
              />
              <span className="font-semibold text-sm sm:text-base text-[#1c1917] dark:text-zinc-100 tracking-tight group-hover:text-black dark:group-hover:text-white transition-colors">
                EasyFinePrint
              </span>
            </Link>
          </div>

          {/* Center: Desktop Navigation */}
          <nav className="hidden md:flex items-center gap-1 sm:gap-1.5">
            <Link
              to="/"
              className={`text-xs font-mono transition-all px-3 py-1.5 rounded-md min-h-[36px] flex items-center active:scale-95 ${
                isCurrent("/")
                  ? "text-[#1c1917] dark:text-zinc-100 bg-[#f5eedf] dark:bg-zinc-900 border border-[#d5cbba] dark:border-zinc-800 shadow-xs font-medium"
                  : "text-[#5c5549] dark:text-zinc-400 hover:text-[#1c1917] dark:hover:text-zinc-200 hover:bg-[#e2d9c7]/50 dark:hover:bg-zinc-900/40"
              }`}
            >
              Dashboard
            </Link>

            <Link
              to="/features"
              className={`text-xs font-mono transition-all px-3 py-1.5 rounded-md min-h-[36px] flex items-center active:scale-95 ${
                isCurrent("/features")
                  ? "text-[#1c1917] dark:text-zinc-100 bg-[#f5eedf] dark:bg-zinc-900 border border-[#d5cbba] dark:border-zinc-800 shadow-xs font-medium"
                  : "text-[#5c5549] dark:text-zinc-400 hover:text-[#1c1917] dark:hover:text-zinc-200 hover:bg-[#e2d9c7]/50 dark:hover:bg-zinc-900/40"
              }`}
            >
              Features
            </Link>

            <Link
              to="/terms"
              className={`text-xs font-mono transition-all px-3 py-1.5 rounded-md min-h-[36px] flex items-center active:scale-95 ${
                isCurrent("/terms")
                  ? "text-[#1c1917] dark:text-zinc-100 bg-[#f5eedf] dark:bg-zinc-900 border border-[#d5cbba] dark:border-zinc-800 shadow-xs font-medium"
                  : "text-[#5c5549] dark:text-zinc-400 hover:text-[#1c1917] dark:hover:text-zinc-200 hover:bg-[#e2d9c7]/50 dark:hover:bg-zinc-900/40"
              }`}
            >
              Terms of Use
            </Link>

            <Link
              to="/privacy"
              className={`text-xs font-mono transition-all px-3 py-1.5 rounded-md min-h-[36px] flex items-center active:scale-95 ${
                isCurrent("/privacy")
                  ? "text-[#1c1917] dark:text-zinc-100 bg-[#f5eedf] dark:bg-zinc-900 border border-[#d5cbba] dark:border-zinc-800 shadow-xs font-medium"
                  : "text-[#5c5549] dark:text-zinc-400 hover:text-[#1c1917] dark:hover:text-zinc-200 hover:bg-[#e2d9c7]/50 dark:hover:bg-zinc-900/40"
              }`}
            >
              Privacy Policy
            </Link>
          </nav>

          {/* Right Actions: Theme Toggle & Star on GitHub */}
          <div className="hidden md:flex items-center gap-2">
            <ThemeToggle />
            <a
              href="https://github.com/diptodeepb/EasyFinePrint"
              target="_blank"
              rel="noreferrer"
              className="flex items-center gap-1.5 text-xs font-mono text-[#5c5549] dark:text-zinc-300 hover:text-[#1c1917] dark:hover:text-white transition-all px-2.5 py-1.5 rounded-lg min-h-[36px] hover:bg-[#e2d9c7]/50 dark:hover:bg-zinc-900/60 border border-[#d5cbba] dark:border-zinc-800 hover:border-[#bfb4a0] dark:hover:border-zinc-700 active:scale-95 shadow-2xs"
              title="Star on GitHub"
            >
              <Star className="w-3.5 h-3.5 text-amber-500 dark:text-amber-400 fill-none shrink-0" />
              <span>Star on GitHub</span>
            </a>
          </div>

          {/* Mobile Right: Theme Toggle & Hamburger */}
          <div className="flex md:hidden items-center gap-1.5">
            <ThemeToggle
              onToggleOpen={() => setMobileMenuOpen(false)}
              onThemeSelect={() => setMobileMenuOpen(false)}
            />
            <button
              type="button"
              onClick={() => setMobileMenuOpen((prev) => !prev)}
              className="p-2 rounded-lg bg-[#f5eedf] dark:bg-zinc-900 border border-[#d5cbba] dark:border-zinc-800 text-[#5c5549] dark:text-zinc-300 hover:text-[#1c1917] dark:hover:text-white transition-colors cursor-pointer active:scale-95 min-h-[36px] min-w-[36px] flex items-center justify-center shadow-2xs"
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
          <div className="md:hidden relative bg-[#ece5d8]/98 dark:bg-[#09090b]/98 backdrop-blur-xl px-4 py-4 space-y-4 animate-in slide-in-from-top-2 duration-150 border-b border-[#d5cbba] dark:border-zinc-800">
            {/* Architectural Top Divider Line for Mobile Menu */}
            <div
              className="absolute inset-x-0 top-0 h-[1px] pointer-events-none select-none overflow-hidden"
              aria-hidden="true"
            >
              <div className="w-full h-full bg-gradient-to-r from-transparent via-[#d5cbba] dark:via-zinc-800/90 to-transparent" />
              <div className="absolute left-1/2 -translate-x-1/2 top-0 w-4/5 h-full bg-gradient-to-r from-transparent via-[#bfb4a0]/50 dark:via-zinc-600/50 to-transparent" />
              <div className="absolute left-1/2 -translate-x-1/2 top-0 w-2/5 h-full bg-gradient-to-r from-transparent via-white/40 dark:via-white/20 to-transparent blur-[0.5px]" />
            </div>

            <nav className="flex flex-col space-y-1">
              <Link
                to="/"
                onClick={() => setMobileMenuOpen(false)}
                className={`px-3 py-2.5 rounded-lg text-xs font-mono transition-colors flex items-center justify-between ${
                  isCurrent("/")
                    ? "bg-[#f5eedf] dark:bg-zinc-900 text-[#1c1917] dark:text-white font-semibold border border-[#d5cbba] dark:border-zinc-800"
                    : "text-[#5c5549] dark:text-zinc-400 hover:text-[#1c1917] dark:hover:text-white hover:bg-[#e2d9c7]/50 dark:hover:bg-zinc-900/50"
                }`}
              >
                <span>Dashboard</span>
                <ArrowRight className="w-3.5 h-3.5 text-[#78716c] dark:text-zinc-600" />
              </Link>

              <Link
                to="/features"
                onClick={() => setMobileMenuOpen(false)}
                className={`px-3 py-2.5 rounded-lg text-xs font-mono transition-colors flex items-center justify-between ${
                  isCurrent("/features")
                    ? "bg-[#f5eedf] dark:bg-zinc-900 text-[#1c1917] dark:text-white font-semibold border border-[#d5cbba] dark:border-zinc-800"
                    : "text-[#5c5549] dark:text-zinc-400 hover:text-[#1c1917] dark:hover:text-white hover:bg-[#e2d9c7]/50 dark:hover:bg-zinc-900/50"
                }`}
              >
                <span>Features</span>
                <ArrowRight className="w-3.5 h-3.5 text-[#78716c] dark:text-zinc-600" />
              </Link>

              <Link
                to="/terms"
                onClick={() => setMobileMenuOpen(false)}
                className={`px-3 py-2.5 rounded-lg text-xs font-mono transition-colors flex items-center justify-between ${
                  isCurrent("/terms")
                    ? "bg-[#f5eedf] dark:bg-zinc-900 text-[#1c1917] dark:text-white font-semibold border border-[#d5cbba] dark:border-zinc-800"
                    : "text-[#5c5549] dark:text-zinc-400 hover:text-[#1c1917] dark:hover:text-white hover:bg-[#e2d9c7]/50 dark:hover:bg-zinc-900/50"
                }`}
              >
                <span>Terms of Use</span>
                <ArrowRight className="w-3.5 h-3.5 text-[#78716c] dark:text-zinc-600" />
              </Link>

              <Link
                to="/privacy"
                onClick={() => setMobileMenuOpen(false)}
                className={`px-3 py-2.5 rounded-lg text-xs font-mono transition-colors flex items-center justify-between ${
                  isCurrent("/privacy")
                    ? "bg-[#f5eedf] dark:bg-zinc-900 text-[#1c1917] dark:text-white font-semibold border border-[#d5cbba] dark:border-zinc-800"
                    : "text-[#5c5549] dark:text-zinc-400 hover:text-[#1c1917] dark:hover:text-white hover:bg-[#e2d9c7]/50 dark:hover:bg-zinc-900/50"
                }`}
              >
                <span>Privacy Policy</span>
                <ArrowRight className="w-3.5 h-3.5 text-[#78716c] dark:text-zinc-600" />
              </Link>
            </nav>

            {/* Star on GitHub */}
            <div className="flex items-center justify-start pt-2 border-t border-[#d5cbba]/80 dark:border-zinc-800/80 text-xs font-mono text-[#5c5549] dark:text-zinc-400">
              <a
                href="https://github.com/diptodeepb/EasyFinePrint"
                target="_blank"
                rel="noreferrer"
                onClick={() => setMobileMenuOpen(false)}
                className="flex items-center gap-2 px-3 py-2 rounded-lg hover:text-[#1c1917] dark:hover:text-white hover:bg-[#e2d9c7]/50 dark:hover:bg-zinc-900/50 transition-colors w-full"
                title="Star on GitHub"
              >
                <Star className="w-3.5 h-3.5 text-amber-500 dark:text-amber-400 fill-none shrink-0" />
                <span>Star on GitHub</span>
              </a>
            </div>
          </div>
        )}

        {/* Architectural Bottom Divider Line (Desktop and Mobile collapsed navbar) */}
        {!mobileMenuOpen && (
          <div
            className="absolute inset-x-0 bottom-0 h-[1px] pointer-events-none select-none overflow-hidden"
            aria-hidden="true"
          >
            <div className="w-full h-full bg-gradient-to-r from-transparent via-[#d5cbba] dark:via-zinc-800/80 to-transparent" />
            <div className="absolute left-1/2 -translate-x-1/2 top-0 w-3/4 max-w-4xl h-full bg-gradient-to-r from-transparent via-[#bfb4a0]/50 dark:via-zinc-600/50 to-transparent" />
            <div className="absolute left-1/2 -translate-x-1/2 top-0 w-1/3 max-w-lg h-full bg-gradient-to-r from-transparent via-white/40 dark:via-white/25 to-transparent blur-[0.5px]" />
          </div>
        )}
      </header>

      {/* Mobile outside click backdrop */}
      {mobileMenuOpen && (
        <div
          className="fixed inset-0 z-40 bg-stone-900/50 dark:bg-black/60 backdrop-blur-xs md:hidden transition-opacity duration-200"
          onClick={(e) => {
            e.preventDefault();
            e.stopPropagation();
            setMobileMenuOpen(false);
          }}
          onTouchEnd={(e) => {
            e.preventDefault();
            e.stopPropagation();
            setMobileMenuOpen(false);
          }}
          aria-hidden="true"
        />
      )}
    </>
  );
}
