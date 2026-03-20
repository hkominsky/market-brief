import asyncio
import importlib.util
import os
import sys
from unittest.mock import AsyncMock, MagicMock

sys.path.insert(0, os.path.dirname(__file__))

def _load_qa():
    spec = importlib.util.spec_from_file_location(
        "qa_real",
        os.path.join(os.path.dirname(__file__), "qa_real_src.py"),
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

_qa_mod = _load_qa()
QAClient = _qa_mod.QAClient

def run(coro):
    return asyncio.get_event_loop().run_until_complete(coro)

def _make_qa(answer="Default answer"):
    mock_client = MagicMock()
    mock_client.chat = AsyncMock(return_value=answer)
    return QAClient(client=mock_client), mock_client

class TestQA:
    def test_two_messages_with_no_history(self):
        qa, _ = _make_qa()
        msgs = qa._build_prompt("transcript", "What was revenue?", [])
        assert len(msgs) == 2  # system + user

    def test_first_message_is_system(self):
        qa, _ = _make_qa()
        msgs = qa._build_prompt("t", "q", [])
        assert msgs[0]["role"] == "system"

    def test_last_message_is_question(self):
        qa, _ = _make_qa()
        msgs = qa._build_prompt("t", "What was EPS?", [])
        assert msgs[-1]["content"] == "What was EPS?"

    def test_transcript_in_system_message(self):
        qa, _ = _make_qa()
        transcript = "AAPL reported $95B revenue."
        msgs = qa._build_prompt(transcript, "q", [])
        assert transcript in msgs[0]["content"]

    def test_history_inserted(self):
        qa, _ = _make_qa()
        history = [{"role": "user", "content": "prev"}, {"role": "assistant", "content": "ans"}]
        msgs = qa._build_prompt("t", "new q", history)
        assert msgs[1]["content"] == "prev" and msgs[2]["content"] == "ans"

    def test_total_length_with_history(self):
        qa, _ = _make_qa()
        history = [{"role": "user", "content": "a"}, {"role": "assistant", "content": "b"}]
        msgs = qa._build_prompt("t", "q", history)
        assert len(msgs) == 4  # system + 2 history + user

    def test_system_mentions_financial_analyst(self):
        qa, _ = _make_qa()
        system_content = qa._build_prompt("t", "q", [])[0]["content"]
        assert "financial analyst" in system_content.lower()

    def test_question_role_is_user(self):
        qa, _ = _make_qa()
        msgs = qa._build_prompt("t", "q", [])
        assert msgs[-1]["role"] == "user"

    def test_returns_answer_string(self):
        qa, _ = _make_qa("Revenue was $10B")
        assert run(qa.ask("transcript", "What was revenue?")) == "Revenue was $10B"

    def test_calls_gpt_once(self):
        qa, mock_client = _make_qa()
        run(qa.ask("t", "q"))
        assert mock_client.chat.call_count == 1

    def test_passes_max_tokens(self):
        qa, mock_client = _make_qa()
        run(qa.ask("t", "q"))
        assert mock_client.chat.call_args[1]["max_tokens"] == 512

    def test_passes_temperature(self):
        qa, mock_client = _make_qa()
        run(qa.ask("t", "q"))
        assert mock_client.chat.call_args[1]["temperature"] == 0.3

    def test_none_history_defaults_to_empty(self):
        qa, mock_client = _make_qa()
        run(qa.ask("t", "q", history=None))
        assert mock_client.chat.call_count == 1

    def test_empty_history(self):
        qa, _ = _make_qa("answer")
        assert run(qa.ask("t", "q", history=[])) == "answer"

    def test_with_history(self):
        qa, mock_client = _make_qa("follow-up answer")
        history = [{"role": "user", "content": "prev"}, {"role": "assistant", "content": "ans"}]
        result = run(qa.ask("t", "follow-up?", history=history))
        assert result == "follow-up answer"

    def test_transcript_passed_into_messages(self):
        qa, mock_client = _make_qa()
        run(qa.ask("unique_transcript_text", "q"))
        messages_arg = mock_client.chat.call_args[1]["messages"]
        assert any("unique_transcript_text" in str(m) for m in messages_arg)
