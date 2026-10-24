import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import * as Sentry from '@sentry/react';
import './index.css';
import App from './App.jsx';

// Initialize Sentry error & performance monitoring if DSN is configured
const sentryDsn = import.meta.env.VITE_SENTRY_DSN;
const apiBase = import.meta.env.VITE_API_URL || '';

if (sentryDsn) {
  Sentry.init({
    dsn: sentryDsn,
    tunnel: `${apiBase}/api/tunnel`,
    environment: import.meta.env.MODE || 'development',
    sendDefaultPii: false,
    dataCollection: {
      userInfo: false,
    },
    integrations: [
      Sentry.browserTracingIntegration(),
    ],
    tracesSampleRate: 0.1,
    beforeSend(event) {
      // 1. Force anonymous user with zeroed IP (prevents Sentry socket inference)
      event.user = { ip_address: '0.0.0.0' };

      // 2. Strip query strings, cookies, and headers from request data
      if (event.request) {
        if (event.request.url) {
          try {
            const u = new URL(event.request.url);
            u.search = '';
            event.request.url = u.toString();
          } catch {
            // ignore parsing error
          }
        }
        delete event.request.cookies;
        delete event.request.headers;
      }
      return event;
    },
    beforeBreadcrumb(breadcrumb) {
      // Strip query parameters from fetch / XHR network breadcrumbs
      if (breadcrumb.category === 'fetch' || breadcrumb.category === 'xhr') {
        if (breadcrumb.data?.url) {
          try {
            const u = new URL(breadcrumb.data.url);
            u.search = '';
            breadcrumb.data.url = u.toString();
          } catch {
            // ignore parsing error
          }
        }
      }
      // Drop click target details that might contain user input
      if (breadcrumb.category === 'ui.click') {
        delete breadcrumb.data;
      }
      return breadcrumb;
    },
  });
}

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <App />
  </StrictMode>,
);
