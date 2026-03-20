# MarketBrief

MarketBrief is a full-stack web application for analyzing earnings call transcripts.
Its goal is to efficiently turn raw financial disclosures into structured, interactable insights in seconds.

Live at https://marketbrief.dev

---

## Features

* **Transcript ingestion** — supports `.txt`, `.mp3`, `.wav` (Whisper for audio)
* **Summarization** — 3–5 sentence earnings overview
* **KPI extraction** — key financial metrics with normalized units
* **Sentiment analysis** — bullish / neutral / bearish signals with confidence
* **Interactive Q&A** — chat grounded in transcript context
* **Multi-transcript support** — compare multiple calls via dashboard
* **Long transcript handling** — automatic chunking + map-reduce pipeline

---

## Tech Stack

| Layer        | Technology                            |
| ------------ | ------------------------------------- |
| Frontend     | React, TypeScript, Tailwind CSS, Vite |
| Backend      | Python, FastAPI, asyncio, uvicorn     |
| AI / ML      | OpenAI GPT-4.1-mini                   |
| Testing      | pytest                                |
| Deployment   | Vercel (frontend), Render (backend)   |

---

## Getting Started

### Prerequisites

* Python 3.10+
* Node.js 18+
* OpenAI API key

### Backend

```bash
git clone https://github.com/your-username/marketbrief.git
cd marketbrief

python -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt

cp .env.example .env
# OPEN_AI_API_KEY=your_api_key

uvicorn src.model.main:app --reload
```

API: http://localhost:8000

### Frontend

```bash
cd frontend

npm install

cp .env.example .env
# VITE_API_URL=http://localhost:8000

npm run dev
```

Frontend: http://localhost:5173

---

## API Reference

### POST `/upload`

Uploads a file, runs transcription if needed, and returns analysis.

**Accepted:** `.txt`, `.mp3`, `.wav`

```json
{
  "summary": "string",
  "kpis": [
    { "kpi": "Revenue", "value": 94.9, "unit": "B" }
  ],
  "ticker": "AAPL",
  "date": "Q1 2025",
  "sentiment": {
    "prepared_statements": {
      "label": "bullish",
      "confidence": 0.87
    },
    "qa": {
      "label": "neutral",
      "confidence": 0.65
    }
  },
  "transcript": "string"
}
```

---

### POST `/ask`

Answers questions grounded in the transcript.

```json
{
  "transcript": "string",
  "question": "What was the revenue growth YoY?",
  "history": [
    { "role": "user", "content": "..." },
    { "role": "assistant", "content": "..." }
  ]
}
```

```json
{
  "answer": "string"
}
```

---

## Running Tests

```bash
pytest
pytest -v
pytest tests/test_summarizer.py
```

---

## License

MIT
