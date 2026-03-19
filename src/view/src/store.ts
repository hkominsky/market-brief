import { create } from "zustand";

interface KPI {
  kpi: string;
  value: number;
  unit: string;
}

interface SentimentSection {
  label: "bullish" | "neutral" | "bearish";
  confidence: number;
  key_phrases: string[];
}

interface Sentiment {
  prepared_remarks: SentimentSection;
  qa: SentimentSection;
}

interface EarningsCall {
  id: string;
  transcript: string;
  summary: string | null;
  ticker: string | null;
  date: string | null;
  kpis: KPI[];
  sentiment: Sentiment | null;
}

interface StoreState {
  earningsCalls: EarningsCall[] | null;
  loading: boolean;
  error: string | null;

  setEarningsCalls: (earningsCalls: EarningsCall[]) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string) => void;
  reset: () => void;
}

const useStore = create<StoreState>((set) => ({
  earningsCalls: null,
  loading: false,
  error: null,

  setEarningsCalls: (earningsCalls) => set({ earningsCalls, loading: false, error: null }),
  setLoading: (loading) => set({ loading }),
  setError: (error) => set({ error, loading: false }),
  reset: () => set({ earningsCalls: null, loading: false, error: null }),
}));

export default useStore;