import React, { useState, useEffect, useRef, useCallback } from "react";
import { Link, useLocation } from "react-router-dom";
import { Menu, X, ArrowRight, Star } from "lucide-react";
import ThemeToggle from "./ThemeToggle";
import { lockBodyScroll, unlockBodyScroll } from "../lib/scrollLock";

export default function Header() {
  const location = useLocation();
  const [menuState, setMenuState] = useState({
    open: false,
    path: location.pathname,
  });
  const headerRef = useRef(null);
  const mobileBackdropRef = useRef(null);
  const isBackdropPointerDown = useRef(false);

  const mobileMenuOpen = menuState.open && menuState.path === location.pathname;

  const setMobileMenuOpen = useCallback(
    (updater) => {
      setMenuState((prev) => {
        const isOpen = prev.open && prev.path === location.pathname;
        const nextOpen =
          typeof updater === "function" ? updater(isOpen) : updater;
        return { open: nextOpen, path: location.pathname };
      });
    },
    [location.pathname],
  );

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
  }, [mobileMenuOpen, setMobileMenuOpen]);

  // Lock body & html scroll while mobile menu is open to prevent background scrolling
  useEffect(() => {
    if (!mobileMenuOpen) return;
    lockBodyScroll();
    return () => {
      unlockBodyScroll();
    };
  }, [mobileMenuOpen]);

  // Prevent touchmove scroll-through on mobile menu backdrop and header drawer
  useEffect(() => {
    if (!mobileMenuOpen) return;
    const backdrop = mobileBackdropRef.current;
    const header = headerRef.current;

    const handleTouchMove = (e) => {
      if (e.cancelable) {
        e.preventDefault();
      }
    };

    backdrop?.addEventListener("touchmove", handleTouchMove, { passive: false });
    header?.addEventListener("touchmove", handleTouchMove, { passive: false });
    return () => {
      backdrop?.removeEventListener("touchmove", handleTouchMove);
      header?.removeEventListener("touchmove", handleTouchMove);
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
  }, [setMobileMenuOpen]);

  const isCurrent = (path) => location.pathname === path;

  return (
    <>
      <header
        ref={headerRef}
        className={`sticky top-0 z-50 w-full bg-[#f4ecde]/85 dark:bg-[#050507]/85 backdrop-blur-md pt-[env(safe-area-inset-top,0px)] transition-colors relative ${
          mobileMenuOpen ? "rounded-b-2xl md:rounded-none" : ""
        }`}
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
                className="w-7 h-7 rounded-lg border border-[#b5a994] dark:border-[var(--edge-btn)] shadow-[2px_2px_0_0_var(--shadow-btn)] transition-transform duration-200 group-hover:-translate-x-0.5 group-hover:-translate-y-0.5"
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
              className={`text-xs font-mono transition-all px-3 py-1.5 rounded-md min-h-[36px] flex items-center ${
                isCurrent("/")
                  ? "text-[#1c1917] dark:text-zinc-100 bg-[#f5eedf] dark:bg-zinc-900 btn-3d-sm font-medium"
                  : "text-[#5c5549] dark:text-zinc-400 hover:text-[#1c1917] dark:hover:text-zinc-200 hover:bg-[#e2d9c7]/50 dark:hover:bg-zinc-900/40"
              }`}
            >
              Dashboard
            </Link>

            <Link
              to="/features"
              className={`text-xs font-mono transition-all px-3 py-1.5 rounded-md min-h-[36px] flex items-center ${
                isCurrent("/features")
                  ? "text-[#1c1917] dark:text-zinc-100 bg-[#f5eedf] dark:bg-zinc-900 btn-3d-sm font-medium"
                  : "text-[#5c5549] dark:text-zinc-400 hover:text-[#1c1917] dark:hover:text-zinc-200 hover:bg-[#e2d9c7]/50 dark:hover:bg-zinc-900/40"
              }`}
            >
              Features
            </Link>

            <Link
              to="/terms"
              className={`text-xs font-mono transition-all px-3 py-1.5 rounded-md min-h-[36px] flex items-center ${
                isCurrent("/terms")
                  ? "text-[#1c1917] dark:text-zinc-100 bg-[#f5eedf] dark:bg-zinc-900 btn-3d-sm font-medium"
                  : "text-[#5c5549] dark:text-zinc-400 hover:text-[#1c1917] dark:hover:text-zinc-200 hover:bg-[#e2d9c7]/50 dark:hover:bg-zinc-900/40"
              }`}
            >
              Terms of Use
            </Link>

            <Link
              to="/privacy"
              className={`text-xs font-mono transition-all px-3 py-1.5 rounded-md min-h-[36px] flex items-center ${
                isCurrent("/privacy")
                  ? "text-[#1c1917] dark:text-zinc-100 bg-[#f5eedf] dark:bg-zinc-900 btn-3d-sm font-medium"
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
              rel="noopener noreferrer"
              className="flex items-center gap-1.5 text-xs font-mono text-[#5c5549] dark:text-zinc-300 hover:text-[#1c1917] dark:hover:text-white px-2.5 py-1.5 rounded-lg min-h-[36px] bg-[#f5eedf] dark:bg-zinc-900 hover:bg-[#e2d9c7] dark:hover:bg-zinc-800/80 btn-3d-secondary"
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
              className="p-2 rounded-lg bg-[#f5eedf] dark:bg-zinc-900 text-[#5c5549] dark:text-zinc-300 hover:text-[#1c1917] dark:hover:text-white cursor-pointer min-h-[36px] min-w-[36px] flex items-center justify-center btn-3d-secondary"
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
          <div className="md:hidden relative bg-[#f4ecde]/98 dark:bg-[#07070a]/98 backdrop-blur-xl px-4 py-4 space-y-4 animate-in slide-in-from-top-2 duration-150 rounded-b-2xl border-b border-[#b5a994] dark:border-[var(--edge-card)] shadow-[0_4px_0_0_var(--shadow-card)] overscroll-none touch-none">
            {/* Architectural Top Divider Line for Mobile Menu */}
            <div
              className="absolute inset-x-0 top-0 h-[1px] pointer-events-none select-none overflow-hidden"
              aria-hidden="true"
            >
              <div className="w-full h-full bg-gradient-to-r from-transparent via-[#d5cbba] dark:via-zinc-800/90 to-transparent" />
              <div className="absolute left-1/2 -translate-x-1/2 top-0 w-4/5 h-full bg-gradient-to-r from-transparent via-[#bfb4a0]/50 dark:via-zinc-600/50 to-transparent" />
              <div className="absolute left-1/2 -translate-x-1/2 top-0 w-2/5 h-full bg-gradient-to-r from-transparent via-white/40 dark:via-white/20 to-transparent blur-[0.5px]" />
            </div>

            <nav className="flex flex-col space-y-1.5">
              <Link
                to="/"
                onClick={() => setMobileMenuOpen(false)}
                className={`px-3 py-2.5 rounded-lg text-xs font-mono transition-colors flex items-center justify-between ${
                  isCurrent("/")
                    ? "bg-[#f5eedf] dark:bg-zinc-900 text-[#1c1917] dark:text-white font-semibold btn-3d-sm"
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
                    ? "bg-[#f5eedf] dark:bg-zinc-900 text-[#1c1917] dark:text-white font-semibold btn-3d-sm"
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
                    ? "bg-[#f5eedf] dark:bg-zinc-900 text-[#1c1917] dark:text-white font-semibold btn-3d-sm"
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
                    ? "bg-[#f5eedf] dark:bg-zinc-900 text-[#1c1917] dark:text-white font-semibold btn-3d-sm"
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
                rel="noopener noreferrer"
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
          ref={mobileBackdropRef}
          className="fixed inset-0 z-40 bg-stone-900/50 dark:bg-black/60 backdrop-blur-xs md:hidden transition-opacity duration-200 overscroll-none touch-none"
          onPointerDown={(e) => {
            isBackdropPointerDown.current = e.target === e.currentTarget;
          }}
          onClick={(e) => {
            const shouldClose = isBackdropPointerDown.current && e.target === e.currentTarget;
            isBackdropPointerDown.current = false;
            e.preventDefault();
            e.stopPropagation();
            if (shouldClose) {
              setMobileMenuOpen(false);
            }
          }}
          aria-hidden="true"
        />
      )}
    </>
  );
}
