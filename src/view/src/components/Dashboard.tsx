import React, { useState } from "react";
import useStore from "../store";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from "recharts";

const Dashboard = () => {
  const { earningsCalls, reset } = useStore();
  const [selected, setSelected] = useState<string | null>(
    earningsCalls?.[0]?.id ?? null
  );

  if (!earningsCalls || earningsCalls.length === 0) return null;

  const selectedCall = earningsCalls.find((c) => c.id === selected) ?? null;

  return (
    <div className="min-h-screen bg-brand-bg flex items-start justify-center p-6">
      <div className="w-full max-w-lg space-y-4">

        {/* Header card */}
        <div className="bg-brand-card border border-brand-border rounded-card p-8">
          <div className="flex items-center justify-between mb-1">
            <h2 className="font-sans text-xl font-semibold text-brand-text">
              Earnings Analysis
            </h2>
            <button
              onClick={reset}
              className="text-xs font-semibold text-brand-muted hover:text-brand-text transition-colors duration-150 cursor-pointer"
            >
              ← New Upload
            </button>
          </div>
          <p className="font-sans text-sm text-brand-subtext">
            {earningsCalls.length === 1
              ? "1 transcript processed."
              : `${earningsCalls.length} transcripts processed.`}
          </p>
        </div>

        {/* Ticker selector — only shown if multiple results */}
        {earningsCalls.length > 1 && (
          <div className="bg-brand-card border border-brand-border rounded-card p-8">
            <p className="text-xs text-brand-subtext uppercase tracking-widest mb-3">
              Select Result
            </p>
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

        {/* Selected call detail */}
        {selectedCall && (
          <>
            {/* Ticker + date */}
            <div className="bg-brand-card border border-brand-border rounded-card p-8">
              <p className="text-xs text-brand-subtext uppercase tracking-widest mb-1">
                Ticker
              </p>
              <h1 className="font-sans text-3xl font-semibold text-brand-text">
                {selectedCall.ticker}
              </h1>
              <p className="font-sans text-sm text-brand-muted mt-1">
                {selectedCall.date}
              </p>
            </div>

            {/* Summary */}
            <div className="bg-brand-card border border-brand-border rounded-card p-8">
              <p className="text-xs text-brand-subtext uppercase tracking-widest mb-3">
                Summary
              </p>
              <p className="font-sans text-sm text-brand-text leading-relaxed">
                {selectedCall.summary ?? "No summary available."}
              </p>
            </div>

            {/* KPIs */}
            <div className="bg-brand-card border border-brand-border rounded-card p-8">
              <p className="text-xs text-brand-subtext uppercase tracking-widest mb-4">
                KPIs
              </p>

              {!selectedCall.kpis || selectedCall.kpis.length === 0 ? (
                <p className="text-sm text-brand-muted">No KPIs extracted.</p>
              ) : (
                <>
                  <table className="w-full text-sm mb-6">
                    <thead>
                      <tr className="border-b border-brand-border">
                        <th className="text-left text-xs text-brand-subtext font-semibold uppercase tracking-widest pb-2">Metric</th>
                        <th className="text-left text-xs text-brand-subtext font-semibold uppercase tracking-widest pb-2">Value</th>
                        <th className="text-left text-xs text-brand-subtext font-semibold uppercase tracking-widest pb-2">Unit</th>
                      </tr>
                    </thead>
                    <tbody>
                      {selectedCall.kpis.map((k, i) => (
                        <tr
                          key={i}
                          className="border-b border-brand-border last:border-0"
                        >
                          <td className="py-2 text-brand-text font-medium">{k.kpi}</td>
                          <td className="py-2 text-brand-accent font-semibold">{k.value}</td>
                          <td className="py-2 text-brand-muted">{k.unit}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>

                  {selectedCall.kpis.length > 1 && (
                    <ResponsiveContainer width="100%" height={200}>
                      <BarChart data={selectedCall.kpis}>
                        <XAxis
                          dataKey="kpi"
                          tick={{ fontSize: 11, fill: "var(--color-brand-subtext)" }}
                          axisLine={false}
                          tickLine={false}
                        />
                        <YAxis
                          tick={{ fontSize: 11, fill: "var(--color-brand-subtext)" }}
                          axisLine={false}
                          tickLine={false}
                        />
                        <Tooltip
                          contentStyle={{
                            background: "var(--color-brand-card)",
                            border: "1px solid var(--color-brand-border)",
                            borderRadius: "var(--radius-card)",
                            fontSize: 12,
                            color: "var(--color-brand-text)",
                          }}
                          cursor={{ fill: "var(--color-brand-accent)", opacity: 0.08 }}
                        />
                        <Bar
                          dataKey="value"
                          fill="var(--color-brand-accent)"
                          radius={[4, 4, 0, 0]}
                        />
                      </BarChart>
                    </ResponsiveContainer>
                  )}
                </>
              )}
            </div>
          </>
        )}
      </div>
    </div>
  );
};

export default Dashboard;