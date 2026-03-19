import React, { useState } from "react";
import useStore from "../store";
import QAChat from "./dashboard/QAChat";
import Header from "./dashboard/Header";
import Tickers from "./dashboard/Tickers";
import Summary from "./dashboard/Summary";
import KPIs from "./dashboard/KPIs";
import SentimentCard from "./dashboard/SentimentCard";

const Dashboard = () => {
  const { earningsCalls, reset } = useStore();
  const [selected, setSelected] = useState<string | null>(earningsCalls?.[0]?.id ?? null);

  if (!earningsCalls || earningsCalls.length === 0) return null;

  const selectedCall = earningsCalls.find((c) => c.id === selected) ?? null;

  return (
    <div className="min-h-screen bg-brand-bg flex items-start justify-center p-6">
      <div className="w-full max-w-lg space-y-4">
        <Header count={earningsCalls.length} onReset={reset} />

        {selectedCall && (
          <>
            <Tickers
              selectedCall={selectedCall}
              earningsCalls={earningsCalls}
              selected={selected}
              onSelect={setSelected}
            />
            <Summary summary={selectedCall.summary} />
            <KPIs kpis={selectedCall.kpis} />
            {selectedCall.sentiment && (
              <SentimentCard sentiment={selectedCall.sentiment} />
            )}
            <QAChat transcript={selectedCall.transcript} />
          </>
        )}
      </div>
    </div>
  );
};

export default Dashboard;