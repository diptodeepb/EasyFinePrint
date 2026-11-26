/**
 * URL and Identifier Sanitization Utilities (OWASP A05:2025 Injection / XSS Defense).
 */

const SAFE_ID_REGEX = /^[a-zA-Z0-9_-]{1,128}$/;

/**
 * Strip ASCII control characters and zero-width whitespace before scheme inspection.
 */
function cleanRawUrl(rawUrl) {
  if (typeof rawUrl !== 'string') return '';
  let result = '';
  for (let i = 0; i < rawUrl.length; i += 1) {
    const code = rawUrl.charCodeAt(i);
    if (code >= 0x20 && code !== 0x7f) {
      result += rawUrl[i];
    }
  }
  return result.trim();
}

/**
 * Validate and sanitize a URL for safe use in <a href> or <Link to>.
 * Permits only http://, https://, or safe single-slash relative paths (/terms, /policies/...).
 * Rejects javascript:, data:, vbscript:, file:, protocol-relative //evil.com, and embedded credentials.
 * @param {string} rawUrl
 * @returns {string | null}
 */
export function getSafeHref(rawUrl) {
  const cleaned = cleanRawUrl(rawUrl);
  if (!cleaned || cleaned.length > 2048) return null;

  // Allow safe internal relative paths starting with a single '/' (reject '//' protocol-relative)
  if (cleaned.startsWith('/')) {
    if (cleaned.startsWith('//') || cleaned.startsWith('/\\')) {
      return null;
    }
    return cleaned;
  }

  try {
    const parsed = new URL(cleaned);
    const protocol = parsed.protocol.toLowerCase();
    if (protocol !== 'http:' && protocol !== 'https:') {
      return null;
    }
    if (parsed.username || parsed.password) {
      return null;
    }
    return parsed.toString();
  } catch {
    return null;
  }
}

/**
 * Return true only if the URL is a safe http:// or https:// URL without embedded credentials.
 * @param {string} rawUrl
 * @returns {boolean}
 */
export function isSafeHttpUrl(rawUrl) {
  const safe = getSafeHref(rawUrl);
  return Boolean(safe && (safe.startsWith('http://') || safe.startsWith('https://')));
}

/**
 * Validate resource identifiers before interpolating into API routes.
 * @param {string} id
 * @returns {boolean}
 */
export function isSafeIdentifier(id) {
  return typeof id === 'string' && SAFE_ID_REGEX.test(id.trim());
}
