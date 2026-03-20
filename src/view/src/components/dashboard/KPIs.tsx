import React from "react";
import { KPI } from "../../types";

interface Props {
  kpis: KPI[];
}

const formatValue = (value: number, unit: string): string => {
  const u = unit.trim().toLowerCase();

  if (u === "%" || u === "percent") {
    return `${value}%`;
  }
  if (u === "b" || u === "billion") {
    return `$${value}B`;
  }
  if (u === "m" || u === "million") {
    return `$${value}M`;
  }
  if (u === "k" || u === "thousand") {
    return `$${value}K`;
  }

  return unit ? `${value} ${unit}` : `${value}`;
};

const KPITable = ({ kpis }: Props) => (
  <div className="bg-brand-card border border-brand-border rounded-card p-8">
    <p className="text-md font-semibold text-brand-text mb-4">KPIs</p>
    {!kpis || kpis.length === 0 ? (
      <p className="text-sm text-brand-muted">No KPIs extracted.</p>
    ) : (
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-brand-border">
            <th className="text-left text-xs text-brand-subtext font-semibold uppercase tracking-widest pb-2">Metric</th>
            <th className="text-right text-xs text-brand-subtext font-semibold uppercase tracking-widest pb-2">Value</th>
          </tr>
        </thead>
        <tbody>
          {kpis.map((k, i) => (
            <tr key={i} className="border-b border-brand-border last:border-0">
              <td className="py-2 text-brand-text font-medium">{k.kpi}</td>
              <td className="py-2 text-brand-accent font-semibold text-right">{formatValue(k.value, k.unit)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    )}
  </div>
);

export default KPITable;