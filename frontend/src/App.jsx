import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Header from './components/Header';
import Home from './pages/Home';
import PolicyDetail from './pages/PolicyDetail';

export default function App() {
  return (
    <BrowserRouter>
      <div className="min-h-screen flex flex-col bg-[#09090b] text-zinc-100 selection:bg-zinc-800 selection:text-white">
        <Header />

        <main className="flex-1">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/policies/:id" element={<PolicyDetail />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </main>

        <footer className="border-t border-zinc-800/80 py-6 text-xs text-zinc-500 font-mono bg-[#09090b]">
          <div className="max-w-5xl mx-auto px-4 flex flex-col sm:flex-row items-center justify-between gap-2">
            <div className="flex items-center gap-2">
              <img src="/logo.svg" alt="" className="w-4 h-4 rounded" />
              <span className="font-semibold text-zinc-400">EasyFinePrint</span>
              <span>/</span>
              <span>Deterministic policy change monitor</span>
            </div>
            <div className="text-[11px] text-zinc-600">
              Informational tool. Verbatim source quotations.
            </div>
          </div>
        </footer>
      </div>
    </BrowserRouter>
  );
}
