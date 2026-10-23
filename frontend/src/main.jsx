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
    integrations: [
      Sentry.browserTracingIntegration(),
      Sentry.replayIntegration({
        maskAllText: true,
        blockAllMedia: true,
      }),
    ],
    tracesSampleRate: 0.1,
    replaysSessionSampleRate: 0.0,
    replaysOnErrorSampleRate: 1.0,
    beforeSend(event) {
      // Redact query strings from URLs to prevent leaking tokens or user identifiers
      if (event.request && event.request.url) {
        try {
          const u = new URL(event.request.url);
          u.search = '';
          event.request.url = u.toString();
        } catch {
          // ignore parsing error
        }
      }
      return event;
    },
  });
}

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <App />
  </StrictMode>,
);
