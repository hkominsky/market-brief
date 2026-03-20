export interface KPI {
  kpi: string;
  value: number;
  unit: string;
}

export interface SentimentSection {
  label: "bullish" | "neutral" | "bearish";
  confidence: number;
  key_phrases: string[];
}

export interface Sentiment {
  prepared_statements: SentimentSection;
  qa: SentimentSection;
}

export interface EarningsCall {
  id: string;
  transcript: string;
  summary: string | null;
  ticker: string | null;
  date: string | null;
  kpis: KPI[];
  sentiment: Sentiment | null;
}