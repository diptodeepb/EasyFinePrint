import test from "node:test";
import assert from "node:assert/strict";

// Mock global sessionStorage
const storage = new Map();
globalThis.sessionStorage = {
  getItem: (k) => storage.get(k) ?? null,
  setItem: (k, v) => storage.set(k, String(v)),
  removeItem: (k) => storage.delete(k),
  clear: () => storage.clear(),
};

// Import after sessionStorage is mocked
const {
  getCachedPolicies,
  setCachedPolicies,
  isCacheStale,
  invalidatePoliciesCache,
  getCooldownRemaining,
  startRefreshCooldown,
  fetchPoliciesWithCache,
} = await import("./policiesCache.js");

test("session cache - set and retrieve policies", () => {
  storage.clear();
  invalidatePoliciesCache();
  assert.equal(getCachedPolicies(), null);
  assert.equal(isCacheStale(), true);

  const mockPolicies = [
    { id: "pol_1", title: "Terms 1" },
    { id: "pol_2", title: "Privacy 2" },
  ];

  setCachedPolicies(mockPolicies);

  const cached = getCachedPolicies();
  assert.notEqual(cached, null);
  assert.equal(cached.data.length, 2);
  assert.equal(cached.data[0].id, "pol_1");
  assert.equal(isCacheStale(), false);
});

test("session cache - invalidation marks stale", () => {
  invalidatePoliciesCache();
  assert.equal(isCacheStale(), true);
});

test("cooldown management - starts at 30 seconds and calculates remaining", () => {
  storage.clear();
  assert.equal(getCooldownRemaining(), 0);

  const initialRemaining = startRefreshCooldown(30000);
  assert.equal(initialRemaining, 30);
  assert.equal(getCooldownRemaining() >= 29, true);
  assert.equal(getCooldownRemaining() <= 30, true);
});

test("cooldown management - expires cleanly", () => {
  storage.clear();
  // Set cooldown timestamp 10ms in the past
  globalThis.sessionStorage.setItem("efp_policies_refresh_cooldown_until", String(Date.now() - 100));
  assert.equal(getCooldownRemaining(), 0);
});

test("fetchPoliciesWithCache - returns cached data without calling api when fresh", async () => {
  storage.clear();
  invalidatePoliciesCache();
  setCachedPolicies([{ id: "p1", title: "Cached Title" }]);

  // fetchPoliciesWithCache({ force: false }) should immediately return cached without API call
  const data = await fetchPoliciesWithCache({ force: false });
  assert.equal(data.length, 1);
  assert.equal(data[0].title, "Cached Title");
});

