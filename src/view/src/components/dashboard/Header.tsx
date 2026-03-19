import React from "react";

interface Props {
  count: number;
  onReset: () => void;
}

const Header = ({ count, onReset }: Props) => (
  <div className="relative bg-brand-card border border-brand-border rounded-card p-6">
    <h2 className="font-sans text-xl font-semibold text-brand-text mb-1">Earnings Analysis</h2>
    <p className="font-sans text-sm text-brand-subtext mb-3">
      {count === 1 ? "1 transcript processed." : `${count} transcripts processed.`}
    </p>
    <button
      onClick={onReset}
      className="text-xs font-semibold text-brand-muted hover:text-brand-text transition-colors duration-150 cursor-pointer"
    >
      ← New Upload
    </button>
  </div>
);

export default Header;