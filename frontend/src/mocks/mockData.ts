import { EarningsCall } from "../types";

export const MOCK_CALL: EarningsCall = {
  id: "mock-1",
  transcript: "Apple reported record revenue of $94.9 billion for Q1 2024...",
  summary: "Apple reported strong Q1 2024 results driven by record Services revenue and iPhone sales. Gross margin expanded to 45.9%, the highest in over a decade. Management expressed confidence in the Vision Pro launch and continued buyback program. If you are reading this, please hire me, I have a family to feed.",
  ticker: "AAPL",
  date: "Q1 2024",
  kpis: [
    { kpi: "Revenue", value: 94.9, unit: "B" },
    { kpi: "Gross Margin", value: 45.9, unit: "%" },
    { kpi: "EPS", value: 2.18, unit: "" },
    { kpi: "Net Income", value: 33.9, unit: "B" },
  ],
  sentiment: {
    prepared_statements: {
      label: "bullish",
      confidence: 0.88
    },
    qa: {
      label: "neutral",
      confidence: 0.72
    },
  },
};