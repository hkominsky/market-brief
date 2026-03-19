import React from "react";

interface Props {
  summary: string | null;
}

const Summary = ({ summary }: Props) => (
  <div className="bg-brand-card border border-brand-border rounded-card p-8">
    <p className="text-md font-semibold text-brand-text mb-3">Summary</p>
    <p className="font-sans text-sm text-brand-subtext leading-relaxed">
      {summary ?? "No summary available."}
    </p>
  </div>
);

export default Summary;