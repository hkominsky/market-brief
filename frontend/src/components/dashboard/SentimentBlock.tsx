import React from "react";

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

export default SentimentBlock;