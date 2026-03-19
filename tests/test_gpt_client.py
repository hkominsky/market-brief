import sys, os
from unittest.mock import MagicMock

sys.path.insert(0, os.path.dirname(__file__))


def _make_client(model="gpt-4", api_key="test-key", response_text="mocked response"):
    mock_openai = MagicMock()
    mock_choice = MagicMock()
    mock_choice.message.content = response_text
    mock_openai.ChatCompletion.create.return_value = MagicMock(choices=[mock_choice])
    sys.modules["openai"] = mock_openai

    from importlib import reload
    import gpt_client as gc_mod
    reload(gc_mod)
    client = gc_mod.GPTClient(model=model, api_key=api_key)
    client.client = mock_openai
    return client, mock_openai


class TestGPTClient:
    def test_sets_api_key(self):
        _, mock_openai = _make_client(api_key="sk-secret")
        assert mock_openai.api_key == "sk-secret"

    def test_stores_model(self):
        client, _ = _make_client(model="gpt-3.5-turbo")
        assert client.model == "gpt-3.5-turbo"

    def test_stores_openai_client(self):
        client, mock_openai = _make_client()
        assert client.client is mock_openai

    def test_returns_response_text(self):
        client, _ = _make_client(response_text="EPS beat estimates")
        assert client.chat([], max_tokens=100, temperature=0.0) == "EPS beat estimates"

    def test_passes_model_to_create(self):
        client, mock_openai = _make_client(model="gpt-4")
        client.chat([], max_tokens=50, temperature=0.5)
        assert mock_openai.ChatCompletion.create.call_args[1]["model"] == "gpt-4"

    def test_passes_messages_to_create(self):
        client, mock_openai = _make_client()
        msgs = [{"role": "user", "content": "hello"}]
        client.chat(msgs, max_tokens=50, temperature=0.0)
        assert mock_openai.ChatCompletion.create.call_args[1]["messages"] == msgs

    def test_passes_max_tokens(self):
        client, mock_openai = _make_client()
        client.chat([], max_tokens=256, temperature=0.0)
        assert mock_openai.ChatCompletion.create.call_args[1]["max_tokens"] == 256

    def test_passes_temperature(self):
        client, mock_openai = _make_client()
        client.chat([], max_tokens=50, temperature=0.7)
        assert mock_openai.ChatCompletion.create.call_args[1]["temperature"] == 0.7

    def test_empty_messages(self):
        client, _ = _make_client(response_text="ok")
        assert client.chat([], max_tokens=10, temperature=0.0) == "ok"

    def test_multi_turn_messages(self):
        client, mock_openai = _make_client()
        msgs = [
            {"role": "system", "content": "You are a financial analyst."},
            {"role": "user", "content": "What was the revenue?"},
            {"role": "assistant", "content": "$10B"},
            {"role": "user", "content": "And EPS?"},
        ]
        client.chat(msgs, max_tokens=100, temperature=0.0)
        assert mock_openai.ChatCompletion.create.call_args[1]["messages"] == msgs