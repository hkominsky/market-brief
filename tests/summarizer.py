import sys, os
from unittest.mock import MagicMock

sys.path.insert(0, os.path.dirname(__file__))


def _make_summarizer(response_text="", model="gpt-4", max_tokens=1024, temperature=0.2):
    # Patches openai and reloads gpt_client, then wires a Summarizer with a mock GPT client
    mock_openai = MagicMock()
    mock_choice = MagicMock()
    mock_choice.message.content = response_text
    mock_openai.ChatCompletion.create.return_value = MagicMock(choices=[mock_choice])
    sys.modules["openai"] = mock_openai

    from importlib import reload
    import gpt_client as gc_mod
    reload(gc_mod)

    import summarizer as s_mod
    reload(s_mod)

    summarizer = s_mod.Summarizer(model=model, max_tokens=max_tokens, temperature=temperature)
    summarizer.client = gc_mod.GPTClient(model=model, api_key="test-key")
    summarizer.client.client = mock_openai
    return summarizer, mock_openai


_VALID_JSON = '{"summary": "Revenue grew 12% YoY.", "kpis": [{"kpi": "Revenue", "value": 10.5, "unit": "USD billion"}, {"kpi": "EPS", "value": 2.3, "unit": "USD"}]}'
_EMPTY_KPIS_JSON = '{"summary": "Strong quarter overall.", "kpis": []}'


class TestSummarizer:
    def test_stores_model(self):
        s, _ = _make_summarizer(model="gpt-3.5-turbo")
        assert s.client.model == "gpt-3.5-turbo"

    def test_stores_max_tokens(self):
        s, _ = _make_summarizer(max_tokens=512)
        assert s.max_tokens == 512

    def test_stores_temperature(self):
        s, _ = _make_summarizer(temperature=0.5)
        assert s.temperature == 0.5

    def test_prompt_has_two_messages(self):
        s, _ = _make_summarizer()
        messages = s._build_prompt("some transcript")
        assert len(messages) == 2

    def test_first_message_is_system(self):
        s, _ = _make_summarizer()
        messages = s._build_prompt("some transcript")
        assert messages[0]["role"] == "system"

    def test_second_message_is_user(self):
        s, _ = _make_summarizer()
        messages = s._build_prompt("some transcript")
        assert messages[1]["role"] == "user"

    def test_transcript_appears_in_user_message(self):
        s, _ = _make_summarizer()
        transcript = "Q3 revenue was $10B."
        messages = s._build_prompt(transcript)
        assert messages[1]["content"] == transcript

    def test_system_message_mentions_json(self):
        s, _ = _make_summarizer()
        messages = s._build_prompt("transcript")
        assert "JSON" in messages[0]["content"]

    def test_parses_valid_json(self):
        s, _ = _make_summarizer()
        result = s._parse_response(_VALID_JSON)
        assert result["summary"] == "Revenue grew 12% YoY."

    def test_parses_kpis_list(self):
        s, _ = _make_summarizer()
        result = s._parse_response(_VALID_JSON)
        assert len(result["kpis"]) == 2

    def test_strips_markdown_fences(self):
        s, _ = _make_summarizer()
        fenced = f"```json\n{_VALID_JSON}\n```"
        result = s._parse_response(fenced)
        assert result["summary"] == "Revenue grew 12% YoY."

    def test_strips_plain_code_fences(self):
        s, _ = _make_summarizer()
        fenced = f"```\n{_VALID_JSON}\n```"
        result = s._parse_response(fenced)
        assert result["summary"] == "Revenue grew 12% YoY."

    def test_falls_back_on_invalid_json(self):
        s, _ = _make_summarizer()
        result = s._parse_response("not valid json at all")
        assert result["summary"] == "not valid json at all"
        assert result["kpis"] == []

    def test_fallback_preserves_raw_text(self):
        s, _ = _make_summarizer()
        raw = "GPT returned plain text instead of JSON."
        result = s._parse_response(raw)
        assert result["summary"] == raw

    def test_returns_kpi_objects(self):
        s, _ = _make_summarizer()
        raw = [{"kpi": "Revenue", "value": 10.5, "unit": "USD billion"}]
        kpis = s._build_kpis(raw)
        assert len(kpis) == 1

    def test_kpi_fields_are_correct(self):
        s, _ = _make_summarizer()
        raw = [{"kpi": "EPS", "value": 2.3, "unit": "USD"}]
        kpi = s._build_kpis(raw)[0]
        assert kpi.kpi == "EPS"
        assert kpi.value == 2.3
        assert kpi.unit == "USD"

    def test_skips_missing_key(self):
        s, _ = _make_summarizer()
        raw = [{"kpi": "Revenue", "value": 10.5}]  # missing "unit"
        assert s._build_kpis(raw) == []

    def test_skips_non_numeric_value(self):
        s, _ = _make_summarizer()
        raw = [{"kpi": "Revenue", "value": "ten billion", "unit": "USD"}]
        assert s._build_kpis(raw) == []

    def test_skips_none_value(self):
        s, _ = _make_summarizer()
        raw = [{"kpi": "Revenue", "value": None, "unit": "USD"}]
        assert s._build_kpis(raw) == []

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
        kpis = s._build_kpis(raw)
        assert len(kpis) == 2

    def test_returns_summary_key(self):
        s, _ = _make_summarizer(response_text=_VALID_JSON)
        result = s.summarize("transcript")
        assert "summary" in result

    def test_returns_kpis_key(self):
        s, _ = _make_summarizer(response_text=_VALID_JSON)
        result = s.summarize("transcript")
        assert "kpis" in result

    def test_kpis_are_dicts(self):
        s, _ = _make_summarizer(response_text=_VALID_JSON)
        result = s.summarize("transcript")
        for kpi in result["kpis"]:
            assert isinstance(kpi, dict)

    def test_kpi_dict_has_expected_keys(self):
        s, _ = _make_summarizer(response_text=_VALID_JSON)
        result = s.summarize("transcript")
        assert set(result["kpis"][0].keys()) == {"kpi", "value", "unit"}

    def test_correct_kpi_count(self):
        s, _ = _make_summarizer(response_text=_VALID_JSON)
        result = s.summarize("transcript")
        assert len(result["kpis"]) == 2

    def test_correct_summary_text(self):
        s, _ = _make_summarizer(response_text=_VALID_JSON)
        result = s.summarize("transcript")
        assert result["summary"] == "Revenue grew 12% YoY."

    def test_empty_kpis_list(self):
        s, _ = _make_summarizer(response_text=_EMPTY_KPIS_JSON)
        result = s.summarize("transcript")
        assert result["kpis"] == []

    def test_gpt_called_once_per_summarize(self):
        s, mock_openai = _make_summarizer(response_text=_VALID_JSON)
        s.summarize("transcript")
        assert mock_openai.ChatCompletion.create.call_count == 1

    def test_passes_max_tokens_to_gpt(self):
        s, mock_openai = _make_summarizer(response_text=_VALID_JSON, max_tokens=512)
        s.summarize("transcript")
        assert mock_openai.ChatCompletion.create.call_args[1]["max_tokens"] == 512

    def test_passes_temperature_to_gpt(self):
        s, mock_openai = _make_summarizer(response_text=_VALID_JSON, temperature=0.3)
        s.summarize("transcript")
        assert mock_openai.ChatCompletion.create.call_args[1]["temperature"] == 0.3

    def test_fallback_on_bad_gpt_response(self):
        s, _ = _make_summarizer(response_text="not json")
        result = s.summarize("transcript")
        assert result["summary"] == "not json"
        assert result["kpis"] == []