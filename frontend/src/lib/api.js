/**
 * API client for interacting with EasyFinePrint backend.
 */
import { isSafeIdentifier } from './safeUrl.js';

const RAW_API_BASE_URL =
  (typeof import.meta.env !== 'undefined' && import.meta.env?.VITE_API_URL) || '';

// Ensure API base URL is either empty (same-origin) or valid http(s) origin without trailing slash
const API_BASE_URL = (() => {
  const trimmed = String(RAW_API_BASE_URL || '').trim().replace(/\/+$/, '');
  if (!trimmed) return '';
  try {
    const parsed = new URL(trimmed);
    if (parsed.protocol === 'http:' || parsed.protocol === 'https:') {
      return parsed.origin;
    }
  } catch {
    // Fall back to relative same-origin if malformed
  }
  return '';
})();

function assertSafeId(id, label = 'identifier') {
  if (!isSafeIdentifier(id)) {
    throw new Error(`Invalid ${label} format.`);
  }
  return encodeURIComponent(id.trim());
}

async function fetchJson(endpoint, options = {}, timeoutMs = 90000) {
  const url = `${API_BASE_URL}${endpoint}`;
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeoutMs);

  try {
    const response = await fetch(url, {
      signal: controller.signal,
      credentials: 'same-origin',
      headers: {
        'Content-Type': 'application/json',
        'X-Requested-With': 'XMLHttpRequest',
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
    let msg = err.message || 'Request failed';
    if (API_BASE_URL) {
      msg = msg.replaceAll(API_BASE_URL, '');
    }
    if (/failed to fetch/i.test(msg) || /networkerror/i.test(msg) || /load failed/i.test(msg)) {
      throw new Error('Unable to connect to the server. Please check your network connection.');
    }
    msg = msg.replace(/https?:\/\/[^\s/$.?#].[^\s]*/gi, '').trim();
    throw new Error(msg || 'Request failed');
  }
}

export const api = {
  // System Health
  getHealth: () => fetchJson('/api/health'),

  // Policies
  analyzePolicy: (payload) => {
    const body = typeof payload === 'string' ? { url: payload } : payload;
    return fetchJson('/api/policies/analyze', {
      method: 'POST',
      body: JSON.stringify(body),
    });
  },

  listPolicies: (limit = 50) => {
    const safeLimit = Math.min(100, Math.max(1, Number.parseInt(limit, 10) || 50));
    return fetchJson(`/api/policies?limit=${safeLimit}`);
  },

  getPolicy: (policyId) => fetchJson(`/api/policies/${assertSafeId(policyId, 'policy ID')}`),

  checkPolicyUpdates: (policyId) =>
    fetchJson(`/api/policies/${assertSafeId(policyId, 'policy ID')}/check`, {
      method: 'POST',
    }),

  getPolicyHistory: (policyId, limit = 50) => {
    const safeLimit = Math.min(100, Math.max(1, Number.parseInt(limit, 10) || 50));
    return fetchJson(`/api/policies/${assertSafeId(policyId, 'policy ID')}/history?limit=${safeLimit}`);
  },

  getSnapshot: (policyId, snapshotId) =>
    fetchJson(
      `/api/policies/${assertSafeId(policyId, 'policy ID')}/snapshots/${assertSafeId(snapshotId, 'snapshot ID')}`,
    ),

  reanalyzePolicy: (policyId) =>
    fetchJson(`/api/policies/${assertSafeId(policyId, 'policy ID')}/reanalyze`, {
      method: 'POST',
    }),

  deletePolicy: (policyId, adminKey = '') =>
    fetchJson(`/api/policies/${assertSafeId(policyId, 'policy ID')}`, {
      method: 'DELETE',
      headers: adminKey ? { 'X-Admin-Key': adminKey } : {},
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
