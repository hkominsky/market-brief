import React, { useState } from "react";
import useStore from "../store";
import QAChat from "./QAChat";

const SentimentBlock = ({ label, data }: { label: string; data: any }) => {
  const labelClass =
    data?.label === "bullish" ? "text-brand-positive" :
    data?.label === "bearish" ? "text-brand-negative" :
    "text-brand-muted";

  return (
    <div className="flex flex-col gap-1">
      <p className="text-xs text-brand-subtext uppercase tracking-widest">{label}</p>
      <div className="flex items-center gap-2">
        <span className={`text-sm font-semibold capitalize ${labelClass}`}>
          {data?.label ?? "—"}
        </span>
        <span className="text-xs text-brand-muted">
          {data?.confidence != null ? `${Math.round(data.confidence * 100)}% confidence` : ""}
        </span>
      </div>
    </div>
  );
};

const Dashboard = () => {
  const { earningsCalls, reset } = useStore();
  const [selected, setSelected] = useState<string | null>(earningsCalls?.[0]?.id ?? null);

  if (!earningsCalls || earningsCalls.length === 0) return null;

  const selectedCall = earningsCalls.find((c) => c.id === selected) ?? null;

  return (
    <div className="min-h-screen bg-brand-bg flex items-start justify-center p-6">
      <div className="w-full max-w-lg space-y-4">

        {/* Header + Ticker */}
        <div className="flex gap-4">
          <div className="flex-1 bg-brand-card border border-brand-border rounded-card p-6">
            <h2 className="font-sans text-xl font-semibold text-brand-text mb-1">Earnings Analysis</h2>
            <p className="font-sans text-sm text-brand-subtext mb-3">
              {earningsCalls.length === 1 ? "1 transcript processed." : `${earningsCalls.length} transcripts processed.`}
            </p>
            <button
              onClick={reset}
              className="text-xs font-semibold text-brand-muted hover:text-brand-text transition-colors duration-150 cursor-pointer"
            >
              ← New Upload
            </button>
          </div>

          {selectedCall && (
            <div className="bg-brand-card border border-brand-border rounded-card p-6">
              <p className="text-xs text-brand-subtext uppercase tracking-widest mb-1">Ticker</p>
              <h1 className="font-sans text-3xl font-semibold text-brand-accent">{selectedCall.ticker}</h1>
              <p className="font-sans text-sm text-brand-muted mt-1">{selectedCall.date}</p>
            </div>
          )}
        </div>

        {/* Ticker selector */}
        {earningsCalls.length > 1 && (
          <div className="bg-brand-card border border-brand-border rounded-card p-8">
            <p className="text-sm font-semibold text-brand-text mb-3">Select Result</p>
            <div className="flex flex-wrap gap-2">
              {earningsCalls.map((call) => (
                <button
                  key={call.id}
                  onClick={() => setSelected(call.id)}
                  className={`
                    px-4 py-2 rounded-card text-sm font-semibold transition-all duration-150 cursor-pointer
                    ${selected === call.id
                      ? "bg-brand-accent text-brand-bg"
                      : "bg-brand-bg border border-brand-border text-brand-subtext hover:border-brand-muted hover:text-brand-text"
                    }
                  `}
                >
                  {call.ticker} — {call.date}
                </button>
              ))}
            </div>
          </div>
        )}

        {selectedCall && (
          <>
            {/* Summary */}
            <div className="bg-brand-card border border-brand-border rounded-card p-8">
              <p className="text-md font-semibold text-brand-text mb-3">Summary</p>
              <p className="font-sans text-sm text-brand-subtext leading-relaxed">
                {selectedCall.summary ?? "No summary available."}
              </p>
            </div>

            {/* KPIs */}
            <div className="bg-brand-card border border-brand-border rounded-card p-8">
              <p className="text-md font-semibold text-brand-text mb-4">KPIs</p>
              {!selectedCall.kpis || selectedCall.kpis.length === 0 ? (
                <p className="text-sm text-brand-muted">No KPIs extracted.</p>
              ) : (
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-brand-border">
                      <th className="text-left text-xs text-brand-subtext font-semibold uppercase tracking-widest pb-2">Metric</th>
                      <th className="text-left text-xs text-brand-subtext font-semibold uppercase tracking-widest pb-2">Value</th>
                      <th className="text-left text-xs text-brand-subtext font-semibold uppercase tracking-widest pb-2">Unit</th>
                    </tr>
                  </thead>
                  <tbody>
                    {selectedCall.kpis.map((k: any, i: number) => (
                      <tr key={i} className="border-b border-brand-border last:border-0">
                        <td className="py-2 text-brand-text font-medium">{k.kpi}</td>
                        <td className="py-2 text-brand-accent font-semibold">{k.value}</td>
                        <td className="py-2 text-brand-muted">{k.unit}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              )}
            </div>

            {/* Sentiment */}
            {selectedCall.sentiment && (
              <div className="bg-brand-card border border-brand-border rounded-card p-8">
                <p className="text-md font-semibold text-brand-text mb-4">Sentiment</p>
                <div className="flex flex-col gap-4">
                  <SentimentBlock label="Prepared Remarks" data={selectedCall.sentiment.prepared_remarks} />
                  <div className="border-t border-brand-border" />
                  <SentimentBlock label="Q&A" data={selectedCall.sentiment.qa} />
                </div>
              </div>
            )}

            {/* Q&A Chat */}
            <QAChat transcript={selectedCall.transcript} />
          </>
        )}
      </div>
    </div>
  );
};

export default Dashboard;