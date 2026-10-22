/**
 * Date and timezone utilities.
 * Ensures all UTC timestamps from server/Mongo are accurately rendered in the client's local timezone.
 */

export function formatLocalDate(dateVal, options = { dateStyle: 'medium', timeStyle: 'short' }) {
  if (!dateVal) return 'Just now';
  try {
    let str = typeof dateVal === 'string' ? dateVal.trim() : dateVal.toISOString();
    // If string has no timezone indicator, treat as UTC
    if (!str.endsWith('Z') && !/[+-]\d{2}:?\d{2}$/.test(str)) {
      str = str + 'Z';
    }
    const d = new Date(str);
    if (isNaN(d.getTime())) return String(dateVal);
    return d.toLocaleString(undefined, options);
  } catch {
    return String(dateVal);
  }
}

export function formatShortDate(dateVal) {
  return formatLocalDate(dateVal, {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
    hour: 'numeric',
    minute: '2-digit',
  });
}
