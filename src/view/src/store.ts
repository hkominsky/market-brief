import { create } from "zustand";

interface EarningsCall {
  id: string;
  transcript: string;
  summary: string | null;
  ticker: string;
  date: string;
  kpis?: { kpi: string; value: number; unit: string }[];
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