import test from 'node:test';
import assert from 'node:assert/strict';

import { getSafeHref, isSafeHttpUrl, isSafeIdentifier } from './safeUrl.js';

test('getSafeHref permits safe http/https and relative paths', () => {
  assert.equal(getSafeHref('https://example.com/terms'), 'https://example.com/terms');
  assert.equal(getSafeHref('http://example.com/privacy'), 'http://example.com/privacy');
  assert.equal(getSafeHref('/terms'), '/terms');
  assert.equal(getSafeHref('/policies/pol_abc123'), '/policies/pol_abc123');
});

test('getSafeHref blocks XSS schemes, protocol-relative URLs, and credentials', () => {
  const unsafe = [
    'javascript:alert(1)',
    '  JaVaScRiPt:alert(document.cookie)',
    'javascript\x00:alert(1)',
    'data:text/html,<script>alert(1)</script>',
    'vbscript:msgbox(1)',
    'file:///etc/passwd',
    '//evil.example.com/phish',
    '/\\evil.example.com',
    'https://user:pass@example.com/terms',
    '',
    null,
    undefined,
  ];
  for (const val of unsafe) {
    assert.equal(getSafeHref(val), null, `Expected unsafe URL to return null: ${String(val)}`);
  }
});

test('isSafeHttpUrl enforces http/https only', () => {
  assert.equal(isSafeHttpUrl('https://github.com/terms'), true);
  assert.equal(isSafeHttpUrl('/terms'), false);
  assert.equal(isSafeHttpUrl('javascript:alert(1)'), false);
});

test('isSafeIdentifier validates safe resource IDs only', () => {
  assert.equal(isSafeIdentifier('pol_123abcXYZ'), true);
  assert.equal(isSafeIdentifier('snp_001-test'), true);
  assert.equal(isSafeIdentifier('../etc/passwd'), false);
  assert.equal(isSafeIdentifier('pol_123?admin=true'), false);
  assert.equal(isSafeIdentifier('pol_$ne'), false);
  assert.equal(isSafeIdentifier(''), false);
});
