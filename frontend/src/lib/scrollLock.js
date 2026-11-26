let lockCount = 0;
let savedScrollY = 0;
let prevHtmlStyles = null;
let prevBodyStyles = null;

/**
 * Locks page scrolling on both <html> and <body> (desktop and mobile/iOS),
 * preserving the current scroll position and compensating for scrollbar width.
 */
export function lockBodyScroll() {
  if (typeof document === 'undefined' || typeof window === 'undefined') return;

  if (lockCount === 0) {
    const html = document.documentElement;
    const body = document.body;

    savedScrollY = window.scrollY || window.pageYOffset || html.scrollTop || 0;
    const scrollbarWidth = Math.max(0, window.innerWidth - html.clientWidth);

    prevHtmlStyles = {
      overflow: html.style.overflow,
      overscrollBehavior: html.style.overscrollBehavior,
    };
    prevBodyStyles = {
      overflow: body.style.overflow,
      overscrollBehavior: body.style.overscrollBehavior,
      position: body.style.position,
      top: body.style.top,
      left: body.style.left,
      right: body.style.right,
      width: body.style.width,
      paddingRight: body.style.paddingRight,
    };

    html.style.overflow = 'hidden';
    html.style.overscrollBehavior = 'none';

    body.style.overflow = 'hidden';
    body.style.overscrollBehavior = 'none';
    body.style.position = 'fixed';
    body.style.top = `-${savedScrollY}px`;
    body.style.left = '0';
    body.style.right = '0';
    body.style.width = '100%';

    if (scrollbarWidth > 0) {
      const computedPad = Number.parseFloat(window.getComputedStyle(body).paddingRight || '0') || 0;
      body.style.paddingRight = `${computedPad + scrollbarWidth}px`;
    }
  }

  lockCount += 1;
}

/**
 * Releases one scroll lock reference and restores prior document styles and scroll position.
 */
export function unlockBodyScroll() {
  if (typeof document === 'undefined' || typeof window === 'undefined') return;
  if (lockCount === 0) return;

  lockCount -= 1;
  if (lockCount > 0) return;

  const html = document.documentElement;
  const body = document.body;

  if (prevHtmlStyles) {
    html.style.overflow = prevHtmlStyles.overflow;
    html.style.overscrollBehavior = prevHtmlStyles.overscrollBehavior;
  }
  if (prevBodyStyles) {
    body.style.overflow = prevBodyStyles.overflow;
    body.style.overscrollBehavior = prevBodyStyles.overscrollBehavior;
    body.style.position = prevBodyStyles.position;
    body.style.top = prevBodyStyles.top;
    body.style.left = prevBodyStyles.left;
    body.style.right = prevBodyStyles.right;
    body.style.width = prevBodyStyles.width;
    body.style.paddingRight = prevBodyStyles.paddingRight;
  }

  const restoreY = savedScrollY;
  prevHtmlStyles = null;
  prevBodyStyles = null;
  savedScrollY = 0;

  window.scrollTo({ top: restoreY, left: 0, behavior: 'instant' });
}

/**
 * Resets the saved scroll offset to 0 when navigating routes while a lock is active.
 */
export function resetLockedScrollTop() {
  if (typeof document === 'undefined') return;
  if (lockCount > 0) {
    savedScrollY = 0;
    document.body.style.top = '0px';
  }
}

export function _getLockCountForTest() {
  return lockCount;
}
