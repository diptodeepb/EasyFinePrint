import React, { useState, useEffect } from 'react';
import { ArrowUp } from 'lucide-react';

export default function BackToTop() {
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      if (window.scrollY > 200) {
        setIsVisible(true);
      } else {
        setIsVisible(false);
      }
    };

    window.addEventListener('scroll', handleScroll, { passive: true });
    handleScroll();

    return () => {
      window.removeEventListener('scroll', handleScroll);
    };
  }, []);

  const scrollToTop = () => {
    window.scrollTo({
      top: 0,
      behavior: 'smooth',
    });
  };

  return (
    <button
      type="button"
      onClick={scrollToTop}
      aria-label="Back to top"
      className={`fixed bottom-[calc(1.25rem+env(safe-area-inset-bottom,0px))] right-4 sm:bottom-6 sm:right-6 z-50 p-2.5 sm:p-3 rounded-full bg-[#f5eedf]/90 hover:bg-[#ece5d8] active:bg-[#ded6c6] dark:bg-zinc-900/90 dark:hover:bg-zinc-800 dark:active:bg-zinc-700 text-[#1c1917] dark:text-zinc-300 dark:hover:text-white border border-[#d5cbba] dark:border-zinc-700/80 shadow-xl shadow-stone-900/10 dark:shadow-black/50 backdrop-blur-md transition-all duration-300 cursor-pointer flex items-center justify-center active:scale-90 ${
        isVisible
          ? 'opacity-100 translate-y-0 pointer-events-auto'
          : 'opacity-0 translate-y-4 pointer-events-none'
      }`}
    >
      <ArrowUp className="w-4 h-4 sm:w-5 sm:h-5 text-[#1c1917] dark:text-zinc-200" />
    </button>
  );
}
