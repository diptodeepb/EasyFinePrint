import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Header from './components/Header';
import Footer from './components/Footer';
import BackToTop from './components/BackToTop';
import ScrollToTop from './components/ScrollToTop';
import ErrorBoundary from './components/ErrorBoundary';
import Home from './pages/Home';
import Features from './pages/Features';
import PolicyDetail from './pages/PolicyDetail';
import TermsOfUse from './pages/TermsOfUse';
import PrivacyPolicy from './pages/PolicyDoc';

export default function App() {
  return (
    <BrowserRouter>
      <ScrollToTop />
      <div className="min-h-screen min-h-[100dvh] w-full overflow-x-hidden flex flex-col bg-[#ece5d8] dark:bg-[#09090b] text-[#1c1917] dark:text-zinc-100 selection:bg-[#ded6c6] dark:selection:bg-zinc-800 selection:text-[#1c1917] dark:selection:text-white">
        <Header />

        <main className="flex-1 w-full">
          <ErrorBoundary>
            <Routes>
              <Route path="/" element={<Home />} />
              <Route path="/features" element={<Features />} />
              <Route path="/policies/:id" element={<PolicyDetail />} />
              <Route path="/terms" element={<TermsOfUse />} />
              <Route path="/privacy" element={<PrivacyPolicy />} />
              <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
          </ErrorBoundary>
        </main>

        <BackToTop />

        <Footer />
      </div>
    </BrowserRouter>
  );
}
