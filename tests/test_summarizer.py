import asyncio
import importlib
import json
from unittest.mock import AsyncMock, MagicMock
import pytest
from kpi import KPI
from summarizer import Summarizer

def run(coro):
    return asyncio.run(coro)
    
def _make_summarizer(response_text="{}"):
    mock_client = MagicMock()
    mock_client.chat = AsyncMock(return_value=response_text)
    s = Summarizer(client=mock_client)
    return s, mock_client

_VALID_JSON = json.dumps({
    "summary": "Revenue grew 12% YoY.",
    "kpis": [
        {"kpi": "Revenue", "value": 10.5, "unit": "USD billion"},
        {"kpi": "EPS", "value": 2.3, "unit": "USD"},
    ],
    "ticker": "AAPL",
    "date": "Q3 2024",
    "sentiment": {
        "prepared_statements": {"label": "bullish", "confidence": 0.9},
        "qa": {"label": "neutral", "confidence": 0.6},
    },
})

_EMPTY_KPIS_JSON = json.dumps({
    "summary": "Strong quarter overall.",
    "kpis": [],
    "ticker": None,
    "date": None,
    "sentiment": {},
})

class TestSummarizer:
    def test_parses_valid_json_summary(self):
        s, _ = _make_summarizer()
        assert s._parse_response(_VALID_JSON)["summary"] == "Revenue grew 12% YoY."

    def test_parses_kpis(self):
        s, _ = _make_summarizer()
        assert len(s._parse_response(_VALID_JSON)["kpis"]) == 2

    def test_strips_json_fence(self):
        s, _ = _make_summarizer()
        fenced = f"```json\n{_VALID_JSON}\n```"
        assert s._parse_response(fenced)["summary"] == "Revenue grew 12% YoY."

    def test_strips_plain_fence(self):
        s, _ = _make_summarizer()
        fenced = f"```\n{_VALID_JSON}\n```"
        assert s._parse_response(fenced)["summary"] == "Revenue grew 12% YoY."

    def test_fallback_on_invalid_json(self):
        s, _ = _make_summarizer()
        result = s._parse_response("not valid json at all")
        assert result["summary"] == "not valid json at all" and result["kpis"] == []

    def test_fallback_preserves_raw_text(self):
        s, _ = _make_summarizer()
        raw = "GPT returned plain text."
        assert s._parse_response(raw)["summary"] == raw

    def test_fallback_has_empty_kpis(self):
        s, _ = _make_summarizer()
        assert s._parse_response("bad")["kpis"] == []

    def test_fallback_ticker_is_none(self):
        s, _ = _make_summarizer()
        assert s._parse_response("bad")["ticker"] is None

    def test_parses_ticker(self):
        s, _ = _make_summarizer()
        assert s._parse_response(_VALID_JSON)["ticker"] == "AAPL"

    def test_parses_date(self):
        s, _ = _make_summarizer()
        assert s._parse_response(_VALID_JSON)["date"] == "Q3 2024"

    def test_kpi_fields_correct(self):
        s, _ = _make_summarizer()
        kpi = s._build_kpis([{"kpi": "EPS", "value": 2.3, "unit": "USD"}])[0]
        assert kpi.kpi == "EPS" and kpi.value == 2.3 and kpi.unit == "USD"

    def test_skips_missing_unit(self):
        s, _ = _make_summarizer()
        assert s._build_kpis([{"kpi": "Revenue", "value": 10.5}]) == []

    def test_skips_non_numeric_value(self):
        s, _ = _make_summarizer()
        assert s._build_kpis([{"kpi": "Revenue", "value": "ten billion", "unit": "USD"}]) == []

    def test_skips_none_value(self):
        s, _ = _make_summarizer()
        assert s._build_kpis([{"kpi": "Revenue", "value": None, "unit": "USD"}]) == []

    def test_handles_empty_list(self):
        s, _ = _make_summarizer()
        assert s._build_kpis([]) == []

    def test_partial_bad_entries_skipped(self):
        s, _ = _make_summarizer()
        raw = [
            {"kpi": "Revenue", "value": 10.5, "unit": "USD"},
            {"kpi": "Bad", "value": "oops", "unit": "USD"},
            {"kpi": "EPS", "value": 2.3, "unit": "USD"},
        ]
        assert len(s._build_kpis(raw)) == 2

    def test_two_messages(self):
        s, _ = _make_summarizer()
        assert len(s._build_prompt("transcript")) == 2

    def test_first_message_is_system(self):
        s, _ = _make_summarizer()
        assert s._build_prompt("transcript")[0]["role"] == "system"

    def test_second_message_is_user(self):
        s, _ = _make_summarizer()
        assert s._build_prompt("transcript")[1]["role"] == "user"

    def test_transcript_in_user_content(self):
        s, _ = _make_summarizer()
        assert s._build_prompt("Q3 revenue was $10B.")[1]["content"] == "Q3 revenue was $10B."

    def test_system_mentions_json(self):
        s, _ = _make_summarizer()
        assert "JSON" in s._build_prompt("t")[0]["content"]

    def test_system_mentions_kpis(self):
        s, _ = _make_summarizer()
        assert "kpi" in s._build_prompt("t")[0]["content"].lower()

    def test_returns_summary_key(self):
        s, _ = _make_summarizer(_VALID_JSON)
        assert "summary" in run(s.summarize("transcript"))

    def test_returns_kpis_key(self):
        s, _ = _make_summarizer(_VALID_JSON)
        assert "kpis" in run(s.summarize("transcript"))

    def test_kpis_are_dicts(self):
        s, _ = _make_summarizer(_VALID_JSON)
        result = run(s.summarize("transcript"))
        assert all(isinstance(k, dict) for k in result["kpis"])

    def test_kpi_dict_has_expected_keys(self):
        s, _ = _make_summarizer(_VALID_JSON)
        result = run(s.summarize("transcript"))
        assert set(result["kpis"][0].keys()) == {"kpi", "value", "unit"}

    def test_correct_kpi_count(self):
        s, _ = _make_summarizer(_VALID_JSON)
        assert len(run(s.summarize("transcript"))["kpis"]) == 2

    def test_correct_summary_text(self):
        s, _ = _make_summarizer(_VALID_JSON)
        assert run(s.summarize("transcript"))["summary"] == "Revenue grew 12% YoY."

    def test_empty_kpis_list(self):
        s, _ = _make_summarizer(_EMPTY_KPIS_JSON)
        assert run(s.summarize("transcript"))["kpis"] == []

    def test_gpt_called_once_short_transcript(self):
        s, mock_client = _make_summarizer(_VALID_JSON)
        run(s.summarize("short " * 10))
        assert mock_client.chat.call_count == 1

    def test_fallback_on_bad_response(self):
        s, _ = _make_summarizer("not json")
        result = run(s.summarize("transcript"))
        assert result["summary"] == "not json" and result["kpis"] == []

    def test_returns_ticker(self):
        s, _ = _make_summarizer(_VALID_JSON)
        assert run(s.summarize("transcript"))["ticker"] == "AAPL"

    def test_returns_date(self):
        s, _ = _make_summarizer(_VALID_JSON)
        assert run(s.summarize("transcript"))["date"] == "Q3 2024"

    def test_returns_sentiment(self):
        s, _ = _make_summarizer(_VALID_JSON)
        result = run(s.summarize("transcript"))
        assert "sentiment" in result

    def test_removes_duplicate_by_name(self):
        s, _ = _make_summarizer()
        raw = [
            {"kpi": "Revenue", "value": 10.0, "unit": "USD"},
            {"kpi": "revenue", "value": 9.5, "unit": "USD"},  # duplicate (case insensitive)
            {"kpi": "EPS", "value": 2.0, "unit": "USD"},
        ]
        deduped = s._deduplicate_kpis(raw)
        assert len(deduped) == 2

    def test_keeps_first_occurrence(self):
        s, _ = _make_summarizer()
        raw = [
            {"kpi": "Revenue", "value": 10.0, "unit": "USD"},
            {"kpi": "Revenue", "value": 99.0, "unit": "USD"},
        ]
        assert s._deduplicate_kpis(raw)[0]["value"] == 10.0

    def test_empty_list_returns_empty(self):
        s, _ = _make_summarizer()
        assert s._deduplicate_kpis([]) == []

    def test_skips_items_with_empty_kpi_key(self):
        s, _ = _make_summarizer()
        raw = [{"kpi": "", "value": 1.0, "unit": "USD"}]
        assert s._deduplicate_kpis(raw) == []

    def test_preserves_order_of_unique(self):
        s, _ = _make_summarizer()
        raw = [
            {"kpi": "A", "value": 1.0, "unit": "x"},
            {"kpi": "B", "value": 2.0, "unit": "x"},
            {"kpi": "C", "value": 3.0, "unit": "x"},
        ]
        names = [d["kpi"] for d in s._deduplicate_kpis(raw)]
        assert names == ["A", "B", "C"]

    def test_multi_chunk_calls_gpt_multiple_times(self):
        s, mock_client = _make_summarizer(_VALID_JSON)
        mock_client.chat = AsyncMock(return_value=_VALID_JSON)
        long_transcript = "word " * 5000  # exceeds 2000 words -> multiple chunks
        run(s.summarize(long_transcript))
        assert mock_client.chat.call_count > 1

    def test_multi_chunk_still_returns_summary_key(self):
        s, mock_client = _make_summarizer(_VALID_JSON)
        mock_client.chat = AsyncMock(return_value=_VALID_JSON)
        long_transcript = "word " * 5000
        result = run(s.summarize(long_transcript))
        assert "summary" in result

    def test_multi_chunk_deduplicates_kpis(self):
        s, mock_client = _make_summarizer()
        chunk_json = json.dumps({
            "summary": "chunk summary",
            "kpis": [{"kpi": "Revenue", "value": 10.0, "unit": "USD"}],
            "ticker": "AAPL", "date": "Q3 2024", "sentiment": {},
        })
        reduce_json = json.dumps({
            "summary": "final summary",
            "kpis": [],
            "ticker": None, "date": None, "sentiment": {},
        })
        responses = [chunk_json] * 4 + [reduce_json]
        mock_client.chat = AsyncMock(side_effect=responses)
        long_transcript = "word " * 5000
        result = run(s.summarize(long_transcript))
        kpi_names = [k["kpi"].lower().strip() for k in result["kpis"]]
        assert kpi_names.count("revenue") == 1

    def test_picks_first_non_null_ticker(self):
        s, _ = _make_summarizer()
        chunks = [{"ticker": None}, {"ticker": "GOOG"}, {"ticker": "AAPL"}]
        assert s._extract_metadata(chunks)["ticker"] == "GOOG"

    def test_returns_none_if_all_null(self):
        s, _ = _make_summarizer()
        chunks = [{"ticker": None}, {"ticker": None}]
        assert s._extract_metadata(chunks)["ticker"] is None

    def test_picks_first_non_null_date(self):
        s, _ = _make_summarizer()
        chunks = [
            {"date": None, "ticker": None, "sentiment": None},
            {"date": "Q2 2024", "ticker": None, "sentiment": None},
        ]
        assert s._extract_metadata(chunks)["date"] == "Q2 2024"
