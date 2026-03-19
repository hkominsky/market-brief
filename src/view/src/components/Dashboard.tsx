import React, { useState } from "react";
import useStore from "../store.ts";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from "recharts";

interface KPI {
  kpi: string;
  value: number;
  unit: string;
}

interface EarningsCall {
  id: string;
  transcript: string;
  summary: string | null;
  ticker: string;
  date: string;
  kpis?: KPI[];
}

const Dashboard = () => {
  const { earningsCalls, reset } = useStore();
  const [selected, setSelected] = useState<string | null>(
    earningsCalls?.[0]?.id ?? null
  );

  if (!earningsCalls || earningsCalls.length === 0) return null;

  const selectedCall = earningsCalls.find((c) => c.id === selected) ?? null;

  return (
    <div>
      <button onClick={reset}>← New Upload</button>

      {earningsCalls.length > 1 && (
        <div>
          <h3>{earningsCalls.length} Results</h3>
          {earningsCalls.map((call) => (
            <div key={call.id}>
              <button onClick={() => setSelected(call.id)}>
                {call.ticker} — {call.date}
              </button>
            </div>
          ))}
        </div>
      )}

      {selectedCall && (
        <div>
          <h1>{selectedCall.ticker}</h1>
          <p>{selectedCall.date}</p>

          <h2>Summary</h2>
          <p>{selectedCall.summary ?? "No summary available."}</p>

          <h2>KPIs</h2>
          {!selectedCall.kpis || selectedCall.kpis.length === 0 ? (
            <p>No KPIs extracted.</p>
          ) : (
            <>
              <table>
                <thead>
                  <tr>
                    <th>Metric</th>
                    <th>Value</th>
                    <th>Unit</th>
                  </tr>
                </thead>
                <tbody>
                  {selectedCall.kpis.map((k, i) => (
                    <tr key={i}>
                      <td>{k.kpi}</td>
                      <td>{k.value}</td>
                      <td>{k.unit}</td>
                    </tr>
                  ))}
                </tbody>
              </table>

              {selectedCall.kpis.length > 1 && (
                <ResponsiveContainer width="100%" height={200}>
                  <BarChart data={selectedCall.kpis}>
                    <XAxis dataKey="kpi" />
                    <YAxis />
                    <Tooltip />
                    <Bar dataKey="value" />
                  </BarChart>
                </ResponsiveContainer>
              )}
            </>
          )}
        </div>
      )}
    </div>
  );
};

export default Dashboard;