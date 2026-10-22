import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Header from './components/Header';
import Footer from './components/Footer';
import BackToTop from './components/BackToTop';
import Home from './pages/Home';
import PolicyDetail from './pages/PolicyDetail';

export default function App() {
  return (
    <BrowserRouter>
      <div className="min-h-screen min-h-[100dvh] w-full overflow-x-hidden flex flex-col bg-[#09090b] text-zinc-100 selection:bg-zinc-800 selection:text-white">
        <Header />

        <main className="flex-1 w-full">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/policies/:id" element={<PolicyDetail />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </main>

        <BackToTop />

        <Footer />
      </div>
    </BrowserRouter>
  );
}
