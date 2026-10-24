import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Header from './components/Header';
import Footer from './components/Footer';
import BackToTop from './components/BackToTop';
import ScrollToTop from './components/ScrollToTop';
import Home from './pages/Home';
import PolicyDetail from './pages/PolicyDetail';
import TermsOfUse from './pages/TermsOfUse';
import PrivacyPolicy from './pages/PolicyDoc';

export default function App() {
  return (
    <BrowserRouter>
      <ScrollToTop />
      <div className="min-h-screen min-h-[100dvh] w-full overflow-x-hidden flex flex-col bg-[#09090b] text-zinc-100 selection:bg-zinc-800 selection:text-white">
        <Header />

        <main className="flex-1 w-full">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/policies/:id" element={<PolicyDetail />} />
            <Route path="/terms" element={<TermsOfUse />} />
            <Route path="/privacy" element={<PrivacyPolicy />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </main>

        <BackToTop />

        <Footer />
      </div>
    </BrowserRouter>
  );
}
