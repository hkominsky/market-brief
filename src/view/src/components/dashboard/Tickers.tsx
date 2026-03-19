import React from "react";
import { EarningsCall } from "../../types";

interface Props {
  selectedCall: EarningsCall;
  earningsCalls: EarningsCall[];
  selected: string | null;
  onSelect: (id: string) => void;
}

const Tickers = ({ selectedCall, earningsCalls, selected, onSelect }: Props) => (
  <div className="bg-brand-card border border-brand-border rounded-card p-6">
    <div className="flex items-center justify-between mb-4">
      <p className="text-xs text-brand-subtext uppercase tracking-widest">Ticker</p>
      <p className="font-sans text-sm text-brand-muted">{selectedCall.date}</p>
    </div>
    <h1 className="font-sans text-3xl font-semibold text-brand-accent mb-4">
      {selectedCall.ticker}
    </h1>
    {earningsCalls.length > 1 && (
      <div className="flex flex-wrap gap-2 pt-4 border-t border-brand-border">
        {earningsCalls.map((call) => (
          <button
            key={call.id}
            onClick={() => onSelect(call.id)}
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
    )}
  </div>
);

export default Tickers;