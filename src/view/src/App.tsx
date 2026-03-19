import React, { useEffect } from "react";
import useStore from "./store";
import UploadForm from "./components/UploadForm";
import Dashboard from "./components/Dashboard";

const MOCK_CALL = {
  id: "mock-1",
  transcript: "Apple reported record revenue of $94.9 billion for Q1 2024...",
  summary: "Apple reported strong Q1 2024 results driven by record Services revenue and iPhone sales. Gross margin expanded to 45.9%, the highest in over a decade. Management expressed confidence in the Vision Pro launch and continued buyback program.",
  ticker: "AAPL",
  date: "Q1 2024",
  kpis: [
    { kpi: "Revenue", value: 94.9, unit: "USD B" },
    { kpi: "Gross Margin", value: 45.9, unit: "%" },
    { kpi: "EPS", value: 2.18, unit: "USD" },
    { kpi: "Net Income", value: 33.9, unit: "USD B" },
  ],
  sentiment: {
    prepared_remarks: {
      label: "bullish" as const,
      confidence: 0.88,
      key_phrases: ["record Services revenue", "highest gross margin", "strong demand"],
    },
    qa: {
      label: "neutral" as const,
      confidence: 0.72,
      key_phrases: ["China headwinds", "cautious on guidance", "Vision Pro ramp"],
    },
  },
};

export default function App() {
  const { earningsCalls, error, setError, setEarningsCalls } = useStore();

  useEffect(() => {
    if (error) {
      const t = setTimeout(() => setError(""), 4000);
      return () => clearTimeout(t);
    }
  }, [error]);

  return (
    <div>
      {error && (
        <div className="fixed top-4 right-4 z-50 flex items-center gap-3 bg-brand-card border border-brand-negative/30 text-brand-text text-sm px-4 py-3 rounded-card shadow-card max-w-sm">
          <span className="text-brand-negative text-base">⚠</span>
          <span>{error}</span>
        </div>
      )}
      {!earningsCalls && (
        <button
          onClick={() => setEarningsCalls([MOCK_CALL])}
          className="fixed bottom-4 right-4 z-50 px-4 py-2 rounded-card text-xs font-semibold bg-brand-warning text-brand-bg cursor-pointer"
        >
          Load Mock Data
        </button>
      )}
      {earningsCalls ? <Dashboard /> : <UploadForm />}
    </div>
  );
}