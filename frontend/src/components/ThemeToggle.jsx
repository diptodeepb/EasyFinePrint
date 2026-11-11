import React, { useState, useEffect, useRef } from "react";
import { flushSync } from "react-dom";
import { Sun, Moon, Monitor, ChevronDown, Check } from "lucide-react";

const THEME_OPTIONS = [
  { id: "light", label: "Light", icon: Sun, iconColor: "text-amber-500" },
  { id: "dark", label: "Dark", icon: Moon, iconColor: "text-indigo-400 dark:text-zinc-200" },
  { id: "system", label: "System", icon: Monitor, iconColor: "text-[#5c5549] dark:text-zinc-400" },
];

export default function ThemeToggle({
  className = "",
  onThemeSelect,
  onToggleOpen,
}) {
  const [theme, setTheme] = useState(() => {
    try {
      const saved = localStorage.getItem("theme");
      if (saved === "light" || saved === "dark" || saved === "system") {
        return saved;
      }
      return "system";
    } catch {
      return "system";
    }
  });

  const [isOpen, setIsOpen] = useState(false);
  const containerRef = useRef(null);

  // Close dropdown on outside click or Escape key
  useEffect(() => {
    if (!isOpen) return;

    const handleOutsideClick = (e) => {
      if (containerRef.current && !containerRef.current.contains(e.target)) {
        setIsOpen(false);
      }
    };

    const handleKeyDown = (e) => {
      if (e.key === "Escape") {
        setIsOpen(false);
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
  }, [isOpen]);

  // Listen to OS system theme changes ONLY when theme === 'system'
  useEffect(() => {
    if (theme !== "system") return;

    const mediaQuery = window.matchMedia("(prefers-color-scheme: dark)");

    const handleMediaChange = (e) => {
      const isSystemDark = e.matches;
      const currentIsDark = document.documentElement.classList.contains("dark");
      if (isSystemDark === currentIsDark) return;

      const toggle = () => {
        if (isSystemDark) {
          document.documentElement.classList.add("dark");
        } else {
          document.documentElement.classList.remove("dark");
        }
        const meta = document.querySelector('meta[name="theme-color"]');
        if (meta) {
          meta.setAttribute("content", isSystemDark ? "#09090b" : "#ece5d8");
        }
      };

      if (!document.startViewTransition) {
        toggle();
        return;
      }

      document.startViewTransition(toggle);
    };

    mediaQuery.addEventListener("change", handleMediaChange);
    return () => mediaQuery.removeEventListener("change", handleMediaChange);
  }, [theme]);

  const selectTheme = (newTheme) => {
    const currentIsDark = document.documentElement.classList.contains("dark");
    let nextIsDark;
    if (newTheme === "dark") {
      nextIsDark = true;
    } else if (newTheme === "light") {
      nextIsDark = false;
    } else {
      nextIsDark = window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches;
    }

    try {
      localStorage.setItem("theme", newTheme);
    } catch {
      // ignore localStorage write errors
    }

    const applyThemeChange = () => {
      flushSync(() => {
        onThemeSelect?.(newTheme);
        setTheme(newTheme);
        setIsOpen(false);
      });
      if (nextIsDark) {
        document.documentElement.classList.add("dark");
      } else {
        document.documentElement.classList.remove("dark");
      }
      const meta = document.querySelector('meta[name="theme-color"]');
      if (meta) {
        meta.setAttribute("content", nextIsDark ? "#09090b" : "#ece5d8");
      }
    };

    if (nextIsDark === currentIsDark) {
      applyThemeChange();
      return;
    }

    if (!document.startViewTransition) {
      applyThemeChange();
      return;
    }

    const isMobile = typeof window !== "undefined" && window.innerWidth < 768;
    const easing = isMobile
      ? "cubic-bezier(0.4, 0, 0.2, 1)"
      : "cubic-bezier(0.5, 0, 1, 1)";

    const rect = containerRef.current?.getBoundingClientRect();
    const x = rect ? rect.left + rect.width / 2 : window.innerWidth / 2;
    const y = rect ? rect.top + rect.height / 2 : window.innerHeight / 2;

    const maxW = Math.max(window.innerWidth, document.documentElement.clientWidth || 0);
    const maxH = Math.max(window.innerHeight, document.documentElement.clientHeight || 0);
    const endRadius = Math.ceil(
      Math.hypot(Math.max(x, maxW - x), Math.max(y, maxH - y))
    );

    if (isMobile) {
      document.documentElement.classList.add("is-theme-transitioning");
    }

    const transition = document.startViewTransition(applyThemeChange);

    transition.finished.finally(() => {
      if (isMobile) {
        document.documentElement.classList.remove("is-theme-transitioning");
      }
    });

    transition.ready.then(() => {
      // Radial outward curve animation
      const clipPath = [
        `circle(0px at ${x}px ${y}px)`,
        `circle(${endRadius}px at ${x}px ${y}px)`,
      ];

      document.documentElement.animate(
        {
          clipPath,
        },
        {
          duration: 700,
          easing,
          pseudoElement: "::view-transition-new(root)",
        }
      );
    });
  };

  // Determine active icon on the trigger button
  const ActiveIcon =
    theme === "light" ? Sun : theme === "dark" ? Moon : Monitor;
  const activeIconColor =
    theme === "light"
      ? "text-amber-500"
      : theme === "dark"
      ? "text-indigo-400 dark:text-zinc-200"
      : "text-[#5c5549] dark:text-zinc-300";

  return (
    <div ref={containerRef} className="relative inline-block text-left">
      {/* Trigger Button with Active Theme Icon + Dropdown Icon */}
      <button
        type="button"
        onClick={() => {
          setIsOpen((prev) => {
            const next = !prev;
            if (next && onToggleOpen) {
              onToggleOpen();
            }
            return next;
          });
        }}
        className={`px-2.5 py-1.5 rounded-lg bg-[#f5eedf] dark:bg-zinc-900 border border-[#d5cbba] dark:border-zinc-800 text-[#5c5549] dark:text-zinc-300 hover:text-[#1c1917] dark:hover:text-white hover:bg-[#e2d9c7] dark:hover:bg-zinc-800/80 transition-colors cursor-pointer active:scale-95 flex items-center gap-1.5 min-h-[36px] shadow-2xs ${className}`}
        title={`Theme: ${theme.charAt(0).toUpperCase() + theme.slice(1)} (Click to change)`}
        aria-label={`Theme: ${theme.charAt(0).toUpperCase() + theme.slice(1)} (Click to change)`}
        aria-haspopup="true"
        aria-expanded={isOpen}
      >
        <ActiveIcon className={`w-4 h-4 shrink-0 ${activeIconColor}`} />
        <ChevronDown
          className={`w-3.5 h-3.5 text-[#78716c] dark:text-zinc-400 shrink-0 transition-transform duration-200 ${
            isOpen ? "rotate-180" : ""
          }`}
        />
      </button>

      {/* Dropdown Menu */}
      {isOpen && (
        <div
          role="menu"
          aria-orientation="vertical"
          className="absolute right-0 mt-1.5 w-36 rounded-xl bg-[#faf5ec] dark:bg-[#121215] border border-[#d5cbba] dark:border-zinc-800 shadow-xl shadow-stone-900/10 dark:shadow-black/60 z-[60] p-1 font-mono text-xs animate-in fade-in zoom-in-95 duration-100"
        >
          {THEME_OPTIONS.map((opt) => {
            const Icon = opt.icon;
            const isSelected = theme === opt.id;
            return (
              <button
                key={opt.id}
                type="button"
                role="menuitem"
                onClick={() => selectTheme(opt.id)}
                className={`w-full flex items-center gap-2 px-2.5 py-2 rounded-lg text-left transition-colors cursor-pointer active:scale-[0.98] ${
                  isSelected
                    ? "bg-[#ece5d8] dark:bg-zinc-800/90 text-[#1c1917] dark:text-white font-semibold"
                    : "text-[#5c5549] dark:text-zinc-400 hover:text-[#1c1917] dark:hover:text-white hover:bg-[#e2d9c7]/60 dark:hover:bg-zinc-900"
                }`}
              >
                <Icon className={`w-3.5 h-3.5 shrink-0 ${opt.iconColor}`} />
                <span className="capitalize">{opt.label}</span>
                {isSelected && (
                  <Check className="w-3.5 h-3.5 ml-auto text-emerald-600 dark:text-emerald-400 shrink-0" />
                )}
              </button>
            );
          })}
        </div>
      )}
    </div>
  );
}
