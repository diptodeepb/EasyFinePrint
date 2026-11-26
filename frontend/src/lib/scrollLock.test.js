import assert from 'node:assert/strict';
import test from 'node:test';

const scrollCalls = [];

function makeStyle() {
  return {
    overflow: '',
    overscrollBehavior: '',
    position: '',
    top: '',
    left: '',
    right: '',
    width: '',
    paddingRight: '',
  };
}

globalThis.window = {
  scrollY: 320,
  pageYOffset: 320,
  innerWidth: 1280,
  getComputedStyle: () => ({ paddingRight: '0px' }),
  scrollTo: (opts) => scrollCalls.push(opts),
};

globalThis.document = {
  documentElement: {
    clientWidth: 1265,
    scrollTop: 320,
    style: makeStyle(),
  },
  body: {
    style: makeStyle(),
  },
};

const {
  lockBodyScroll,
  unlockBodyScroll,
  resetLockedScrollTop,
  _getLockCountForTest,
} = await import('./scrollLock.js');

test('scrollLock - locks both html and body and restores exact scroll position', () => {
  scrollCalls.length = 0;
  globalThis.window.scrollY = 320;
  lockBodyScroll();

  assert.equal(_getLockCountForTest(), 1);
  assert.equal(globalThis.document.documentElement.style.overflow, 'hidden');
  assert.equal(globalThis.document.body.style.overflow, 'hidden');
  assert.equal(globalThis.document.body.style.position, 'fixed');
  assert.equal(globalThis.document.body.style.top, '-320px');
  assert.equal(globalThis.document.body.style.paddingRight, '15px');

  // Nested lock keeps lockCount > 0 without overwriting savedScrollY
  lockBodyScroll();
  assert.equal(_getLockCountForTest(), 2);
  unlockBodyScroll();
  assert.equal(_getLockCountForTest(), 1);
  assert.equal(globalThis.document.body.style.position, 'fixed');

  unlockBodyScroll();
  assert.equal(_getLockCountForTest(), 0);
  assert.equal(globalThis.document.documentElement.style.overflow, '');
  assert.equal(globalThis.document.body.style.position, '');
  assert.equal(globalThis.document.body.style.paddingRight, '');
  assert.deepEqual(scrollCalls.at(-1), { top: 320, left: 0, behavior: 'instant' });
});

test('scrollLock - resetLockedScrollTop clears offset during route change', () => {
  scrollCalls.length = 0;
  globalThis.window.scrollY = 500;
  lockBodyScroll();
  resetLockedScrollTop();
  assert.equal(globalThis.document.body.style.top, '0px');
  unlockBodyScroll();
  assert.deepEqual(scrollCalls.at(-1), { top: 0, left: 0, behavior: 'instant' });
});
