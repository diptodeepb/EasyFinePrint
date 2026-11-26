import { useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import { resetLockedScrollTop } from '../lib/scrollLock';

/**
 * Automatically scrolls window and document to the top whenever
 * the route, pathname, or query parameters change.
 */
export default function ScrollToTop() {
  const { pathname, search } = useLocation();

  useEffect(() => {
    resetLockedScrollTop();
    window.scrollTo({ top: 0, left: 0, behavior: 'instant' });
    if (document.documentElement) {
      document.documentElement.scrollTop = 0;
    }
    if (document.body) {
      document.body.scrollTop = 0;
    }
  }, [pathname, search]);

  return null;
}
