/**
 * Session-scoped cache and refresh throttling for dashboard policies.
 *
 * Implements Stale-While-Revalidate (SWR):
 * - Instant rendering from session cache when navigating between routes.
 * - Auto-revalidation in the background when data is older than STALE_TIME.
 * - Manual refresh bypasses cache and triggers a 30-second cooldown timer.
 * - Scoped strictly to the browser session (cleared on new session/tab visit).
 */

import { api } from "./api.js";
import { isSafeIdentifier } from "./safeUrl.js";

const CACHE_KEY = "efp_policies_session_cache_v1";
const COOLDOWN_KEY = "efp_policies_refresh_cooldown_until";

// 60 seconds stale time (industry standard for dashboard listings)
export const STALE_TIME_MS = 60 * 1000;

// 30 seconds cooldown after manual refresh
export const COOLDOWN_DURATION_MS = 30 * 1000;

let memoryCache = null;
let inFlightPromise = null;

function safeGetSessionItem(key) {
  try {
    return sessionStorage.getItem(key);
  } catch {
    return null;
  }
}

function safeSetSessionItem(key, value) {
  try {
    sessionStorage.setItem(key, value);
  } catch {
    // Ignore session quota or access errors in restrictive environments
  }
}

function safeRemoveSessionItem(key) {
  try {
    sessionStorage.removeItem(key);
  } catch {
    // Ignore
  }
}

function isValidPolicyCacheArray(arr) {
  if (!Array.isArray(arr) || arr.length > 250) return false;
  return arr.every(
    (item) =>
      item &&
      typeof item === "object" &&
      !Array.isArray(item) &&
      typeof item.id === "string" &&
      isSafeIdentifier(item.id),
  );
}

/**
 * Retrieve cached policies from in-memory store or sessionStorage.
 * @returns {{ data: Array, timestamp: number } | null}
 */
export function getCachedPolicies() {
  if (memoryCache && isValidPolicyCacheArray(memoryCache.data)) {
    return memoryCache;
  }

  const raw = safeGetSessionItem(CACHE_KEY);
  if (!raw) return null;

  try {
    const parsed = JSON.parse(raw);
    if (
      parsed &&
      typeof parsed === "object" &&
      !Array.isArray(parsed) &&
      isValidPolicyCacheArray(parsed.data) &&
      typeof parsed.timestamp === "number" &&
      Number.isFinite(parsed.timestamp)
    ) {
      memoryCache = parsed;
      return memoryCache;
    }
    safeRemoveSessionItem(CACHE_KEY);
  } catch {
    safeRemoveSessionItem(CACHE_KEY);
  }
  return null;
}

/**
 * Store policies into session cache.
 * @param {Array} data
 */
export function setCachedPolicies(data) {
  if (!Array.isArray(data)) return;
  const entry = {
    data,
    timestamp: Date.now(),
  };
  memoryCache = entry;
  safeSetSessionItem(CACHE_KEY, JSON.stringify(entry));
}

/**
 * Check if the current cache is missing or stale.
 * @returns {boolean}
 */
export function isCacheStale() {
  const cached = getCachedPolicies();
  if (!cached) return true;
  return Date.now() - cached.timestamp >= STALE_TIME_MS;
}

/**
 * Invalidate cache so next read marks it stale (triggers background refresh).
 */
export function invalidatePoliciesCache() {
  if (memoryCache) {
    memoryCache.timestamp = 0;
  }
  safeRemoveSessionItem(CACHE_KEY);
}

/**
 * Get remaining cooldown seconds for the manual refresh button (0 if ready).
 * @returns {number}
 */
export function getCooldownRemaining() {
  const untilStr = safeGetSessionItem(COOLDOWN_KEY);
  if (!untilStr) return 0;

  const until = Number(untilStr);
  if (!Number.isFinite(until)) {
    safeRemoveSessionItem(COOLDOWN_KEY);
    return 0;
  }

  const diffMs = until - Date.now();
  if (diffMs <= 0) {
    safeRemoveSessionItem(COOLDOWN_KEY);
    return 0;
  }

  return Math.ceil(diffMs / 1000);
}

/**
 * Start the 30-second cooldown period.
 * @param {number} durationMs
 * @returns {number}
 */
export function startRefreshCooldown(durationMs = COOLDOWN_DURATION_MS) {
  const until = Date.now() + durationMs;
  safeSetSessionItem(COOLDOWN_KEY, String(until));
  return Math.ceil(durationMs / 1000);
}

/**
 * Fetch policies with session caching and in-flight request deduplication.
 * @param {Object} options
 * @param {boolean} [options.force=false] Force fresh network request
 * @param {number} [options.limit=100] Max policies to fetch
 * @returns {Promise<Array>}
 */
export async function fetchPoliciesWithCache({ force = false, limit = 100 } = {}) {
  // If not forcing and cache is fresh, return cached data immediately
  if (!force && !isCacheStale()) {
    const cached = getCachedPolicies();
    if (cached) return cached.data;
  }

  // Deduplicate concurrent requests
  if (inFlightPromise) {
    return inFlightPromise;
  }

  inFlightPromise = (async () => {
    try {
      const data = await api.listPolicies(limit);
      setCachedPolicies(data);
      return data;
    } finally {
      inFlightPromise = null;
    }
  })();

  return inFlightPromise;
}
