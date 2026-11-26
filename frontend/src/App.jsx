import React, { Suspense, lazy } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Header from './components/Header';
import Footer from './components/Footer';
import BackToTop from './components/BackToTop';
import ScrollToTop from './components/ScrollToTop';
import ErrorBoundary from './components/ErrorBoundary';

const Home = lazy(() => import('./pages/Home'));
const Features = lazy(() => import('./pages/Features'));
const PolicyDetail = lazy(() => import('./pages/PolicyDetail'));
const TermsOfUse = lazy(() => import('./pages/TermsOfUse'));
const PrivacyPolicy = lazy(() => import('./pages/PolicyDoc'));

function RouteFallback() {
  return (
    <div className="min-h-[50vh] flex items-center justify-center font-mono text-xs text-[#5c5549] dark:text-zinc-400">
      Loading view...
    </div>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <ScrollToTop />
      <div className="min-h-screen min-h-[100dvh] w-full overflow-x-hidden flex flex-col bg-transparent text-[#1c1917] dark:text-zinc-100 selection:bg-[#ded6c6] dark:selection:bg-zinc-800 selection:text-[#1c1917] dark:selection:text-white">
        <Header />

        <main className="flex-1 w-full">
          <ErrorBoundary>
            <Suspense fallback={<RouteFallback />}>
              <Routes>
                <Route path="/" element={<Home />} />
                <Route path="/features" element={<Features />} />
                <Route path="/policies/:id" element={<PolicyDetail />} />
                <Route path="/terms" element={<TermsOfUse />} />
                <Route path="/privacy" element={<PrivacyPolicy />} />
                <Route path="*" element={<Navigate to="/" replace />} />
              </Routes>
            </Suspense>
          </ErrorBoundary>
        </main>

        <BackToTop />

        <Footer />
      </div>
    </BrowserRouter>
  );
}
