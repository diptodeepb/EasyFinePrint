/**
 * API client for interacting with EasyFinePrint backend.
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || '';

async function fetchJson(endpoint, options = {}) {
  const url = `${API_BASE_URL}${endpoint}`;
  const response = await fetch(url, {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    ...options,
  });

  if (!response.ok) {
    let errorDetail = `Request failed with status ${response.status}`;
    try {
      const errData = await response.json();
      if (errData.detail) {
        errorDetail = typeof errData.detail === 'string' ? errData.detail : JSON.stringify(errData.detail);
      } else if (errData.message) {
        errorDetail = errData.message;
      }
    } catch {
      // Use fallback errorDetail
    }
    throw new Error(errorDetail);
  }

  return response.json();
}

export const api = {
  // System Health
  getHealth: () => fetchJson('/api/health'),

  // Policies
  analyzePolicy: (url) =>
    fetchJson('/api/policies/analyze', {
      method: 'POST',
      body: JSON.stringify({ url }),
    }),

  listPolicies: (limit = 50) => fetchJson(`/api/policies?limit=${limit}`),

  getPolicy: (policyId) => fetchJson(`/api/policies/${policyId}`),

  checkPolicyUpdates: (policyId) =>
    fetchJson(`/api/policies/${policyId}/check`, {
      method: 'POST',
    }),

  getPolicyHistory: (policyId, limit = 50) =>
    fetchJson(`/api/policies/${policyId}/history?limit=${limit}`),

  getSnapshot: (policyId, snapshotId) =>
    fetchJson(`/api/policies/${policyId}/snapshots/${snapshotId}`),

  // Discovery
  discoverPolicyUrls: (query) =>
    fetchJson('/api/discovery/search', {
      method: 'POST',
      body: JSON.stringify({ query }),
    }),
};
