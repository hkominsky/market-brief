import React, { useEffect } from "react";
import useStore from "./store";
import UploadForm from "./components/UploadForm";
import Dashboard from "./components/Dashboard";
import { MOCK_CALL } from "./mocks/mockData";
import logo from "./assets/logo.svg";
import { Analytics } from "@vercel/analytics/react";
import { SpeedInsights } from "@vercel/speed-insights/react";

export default function App() {
  const { earningsCalls, error, setError, setEarningsCalls } = useStore();

  useEffect(() => {
    if (error) {
      const t = setTimeout(() => setError(""), 4000);
      return () => clearTimeout(t);
    }
  }, [error]);

  return (
    <div className="relative min-h-screen bg-brand-bg">
      <div className="flex justify-start px-4 pt-4 lg:p-0">
        <div className="flex items-center gap-2 opacity-80 lg:absolute lg:top-4 lg:left-4">
          <img src={logo} alt="Logo" className="h-8 w-auto" />
          <span className="font-display text-sm font-semibold text-brand-text">Market Brief</span>
        </div>
      </div>
      {error && (
        <div className="fixed top-4 right-4 z-50 flex items-center gap-3 bg-brand-card border border-brand-negative/30 text-brand-text text-sm px-4 py-3 rounded-card shadow-card max-w-sm">
          <span className="text-brand-negative text-base">⚠</span>
          <span>{error}</span>
        </div>
      )}
      {earningsCalls
        ? <Dashboard />
        : <UploadForm onLoadMock={() => setEarningsCalls([MOCK_CALL])} />
      }
      <Analytics />
      <SpeedInsights />
    </div>
  );
}