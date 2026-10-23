/**
 * API client for interacting with EasyFinePrint backend.
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || '';

async function fetchJson(endpoint, options = {}, timeoutMs = 90000) {
  const url = `${API_BASE_URL}${endpoint}`;
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeoutMs);

  try {
    const response = await fetch(url, {
      signal: controller.signal,
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    });
    clearTimeout(timeoutId);

    if (!response.ok) {
      let errorDetail = `Request failed with status ${response.status}`;
      try {
        const errData = await response.json();
        if (errData.detail) {
          if (typeof errData.detail === 'string') {
            errorDetail = errData.detail;
          } else if (Array.isArray(errData.detail)) {
            errorDetail = errData.detail
              .map((d) => d.msg || (typeof d === 'string' ? d : JSON.stringify(d)))
              .join('; ');
          } else if (typeof errData.detail === 'object') {
            errorDetail = errData.detail.message || JSON.stringify(errData.detail);
          }
        } else if (errData.message) {
          errorDetail = errData.message;
        }
      } catch {
        // Use fallback errorDetail
      }
      throw new Error(errorDetail);
    }

    return response.json();
  } catch (err) {
    clearTimeout(timeoutId);
    if (err.name === 'AbortError') {
      throw new Error('Request timed out. The server took longer than 90 seconds to respond.');
    }
    throw err;
  }
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

  reanalyzePolicy: (policyId) =>
    fetchJson(`/api/policies/${policyId}/reanalyze`, {
      method: 'POST',
    }),

  // Discovery
  discoverPolicyUrls: (query) =>
    fetchJson('/api/discovery/search', {
      method: 'POST',
      body: JSON.stringify({ query }),
    }),

  // Self Policies (Dogfooding / Fun testing)
  analyzeSelfPolicy: (policyType = 'terms') =>
    fetchJson('/api/policies/analyze-self', {
      method: 'POST',
      body: JSON.stringify({ policy_type: policyType }),
    }),

  listSelfPolicies: () => fetchJson('/api/policies/self-policies'),
};
