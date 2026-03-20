import asyncio
import os
import sys
from unittest.mock import AsyncMock, MagicMock, patch
import pytest

import openai as _real_openai_pkg
_RealRateLimitError = _real_openai_pkg.RateLimitError
_RealAPIStatusError = _real_openai_pkg.APIStatusError

_mock_openai_module = MagicMock()
sys.modules.setdefault("openai", _mock_openai_module)

from gpt_client import GPTClient, QuotaExceededError
import gpt_client as _gpt_client_mod

_gpt_client_mod.RateLimitError = _RealRateLimitError
_gpt_client_mod.APIStatusError = _RealAPIStatusError
RateLimitError = _RealRateLimitError
APIStatusError = _RealAPIStatusError

def run(coro):
    return asyncio.run(coro)

def _make_gpt_client(response_text="ok", max_retries=1, model="gpt-4", api_key="test"):
    client = GPTClient(model=model, api_key=api_key, max_retries=max_retries)
    mock_inner = AsyncMock()
    mock_choice = MagicMock()
    mock_choice.message.content = response_text
    mock_inner.chat.completions.create = AsyncMock(
        return_value=MagicMock(choices=[mock_choice])
    )
    client.client = mock_inner
    return client, mock_inner

def _make_rate_limit_err(body=None):
    # Builds a RateLimitError with an optional body for quota testing
    import httpx
    resp = httpx.Response(429, request=httpx.Request("POST", "https://api.openai.com"))
    return RateLimitError("rate limited", response=resp, body=body or {})

def _make_api_status_err(status_code):
    # Builds an APIStatusError with the given status code
    import httpx
    resp = httpx.Response(status_code, request=httpx.Request("POST", "https://api.openai.com"))
    return APIStatusError("error", response=resp, body={})

def _make_quota_rate_limit_err():
    # Builds a RateLimitError that looks like an insufficient_quota billing error
    return _make_rate_limit_err(body={"code": "insufficient_quota", "message": "quota exceeded"})


class TestGPTClient:
    def test_stores_model(self):
        c, _ = _make_gpt_client(model="gpt-3.5-turbo")
        assert c.model == "gpt-3.5-turbo"

    def test_stores_max_retries(self):
        c, _ = _make_gpt_client(max_retries=3)
        assert c.max_retries == 3

    def test_default_max_retries(self):
        c = GPTClient(model="gpt-4", api_key="k")
        assert c.max_retries == 4

    def test_client_is_set(self):
        c, inner = _make_gpt_client()
        assert c.client is inner

    def test_returns_response_text(self):
        c, _ = _make_gpt_client(response_text="EPS beat estimates")
        assert run(c.chat([], max_tokens=100, temperature=0.0)) == "EPS beat estimates"

    def test_passes_model(self):
        c, inner = _make_gpt_client(model="gpt-4")
        run(c.chat([], max_tokens=50, temperature=0.0))
        assert inner.chat.completions.create.call_args[1]["model"] == "gpt-4"

    def test_passes_messages(self):
        c, inner = _make_gpt_client()
        msgs = [{"role": "user", "content": "hello"}]
        run(c.chat(msgs, max_tokens=50, temperature=0.0))
        assert inner.chat.completions.create.call_args[1]["messages"] == msgs

    def test_passes_max_tokens(self):
        c, inner = _make_gpt_client()
        run(c.chat([], max_tokens=256, temperature=0.0))
        assert inner.chat.completions.create.call_args[1]["max_tokens"] == 256

    def test_passes_temperature(self):
        c, inner = _make_gpt_client()
        run(c.chat([], max_tokens=50, temperature=0.7))
        assert inner.chat.completions.create.call_args[1]["temperature"] == 0.7

    def test_empty_messages_ok(self):
        c, _ = _make_gpt_client(response_text="ok")
        assert run(c.chat([], max_tokens=10, temperature=0.0)) == "ok"

    def test_multi_turn_messages(self):
        c, inner = _make_gpt_client()
        msgs = [
            {"role": "system", "content": "You are a financial analyst."},
            {"role": "user", "content": "What was revenue?"},
            {"role": "assistant", "content": "$10B"},
            {"role": "user", "content": "And EPS?"},
        ]
        run(c.chat(msgs, max_tokens=100, temperature=0.0))
        assert inner.chat.completions.create.call_args[1]["messages"] == msgs

    def test_retries_on_rate_limit(self):
        c = GPTClient(model="gpt-4", api_key="k", max_retries=3)
        inner = AsyncMock()
        mock_choice = MagicMock()
        mock_choice.message.content = "recovered"
        inner.chat.completions.create = AsyncMock(
            side_effect=[
                _make_rate_limit_err(),
                _make_rate_limit_err(),
                MagicMock(choices=[mock_choice]),
            ]
        )
        c.client = inner
        with patch.object(c, "_backoff", new=AsyncMock()):
            result = run(c.chat([], max_tokens=10, temperature=0.0))
        assert result == "recovered"

    def test_raises_rate_limit_after_max_retries(self):
        c = GPTClient(model="gpt-4", api_key="k", max_retries=2)
        inner = AsyncMock()
        inner.chat.completions.create = AsyncMock(side_effect=_make_rate_limit_err())
        c.client = inner
        with patch.object(c, "_backoff", new=AsyncMock()):
            with pytest.raises(RateLimitError):
                run(c.chat([], max_tokens=10, temperature=0.0))

    def test_retries_on_500_error(self):
        c = GPTClient(model="gpt-4", api_key="k", max_retries=3)
        inner = AsyncMock()
        mock_choice = MagicMock()
        mock_choice.message.content = "ok"
        inner.chat.completions.create = AsyncMock(
            side_effect=[
                _make_api_status_err(503),
                MagicMock(choices=[mock_choice]),
            ]
        )
        c.client = inner
        with patch.object(c, "_backoff", new=AsyncMock()):
            result = run(c.chat([], max_tokens=10, temperature=0.0))
        assert result == "ok"

    def test_raises_immediately_on_400(self):
        c = GPTClient(model="gpt-4", api_key="k", max_retries=3)
        inner = AsyncMock()
        inner.chat.completions.create = AsyncMock(side_effect=_make_api_status_err(400))
        c.client = inner
        with pytest.raises(APIStatusError):
            run(c.chat([], max_tokens=10, temperature=0.0))
        assert inner.chat.completions.create.call_count == 1

    def test_quota_error_raises_immediately(self):
        c = GPTClient(model="gpt-4", api_key="k", max_retries=4)
        inner = AsyncMock()
        inner.chat.completions.create = AsyncMock(side_effect=_make_quota_rate_limit_err())
        c.client = inner
        with patch.object(c, "_backoff", new=AsyncMock()) as mock_backoff:
            with pytest.raises(QuotaExceededError):
                run(c.chat([], max_tokens=10, temperature=0.0))
        mock_backoff.assert_not_called()

    def test_quota_error_does_not_retry(self):
        c = GPTClient(model="gpt-4", api_key="k", max_retries=4)
        inner = AsyncMock()
        inner.chat.completions.create = AsyncMock(side_effect=_make_quota_rate_limit_err())
        c.client = inner
        with patch.object(c, "_backoff", new=AsyncMock()):
            with pytest.raises(QuotaExceededError):
                run(c.chat([], max_tokens=10, temperature=0.0))
        assert inner.chat.completions.create.call_count == 1

    def test_quota_error_message_contains_hint(self):
        c = GPTClient(model="gpt-4", api_key="k", max_retries=1)
        inner = AsyncMock()
        inner.chat.completions.create = AsyncMock(side_effect=_make_quota_rate_limit_err())
        c.client = inner
        with pytest.raises(QuotaExceededError, match="sample dashboard"):
            run(c.chat([], max_tokens=10, temperature=0.0))

    def test_is_quota_error_true_for_insufficient_quota(self):
        c = GPTClient(model="gpt-4", api_key="k")
        assert c._is_quota_error(_make_quota_rate_limit_err()) is True

    def test_is_quota_error_false_for_plain_rate_limit(self):
        c = GPTClient(model="gpt-4", api_key="k")
        assert c._is_quota_error(_make_rate_limit_err()) is False

    def test_is_quota_error_fallback_on_string(self):
        c = GPTClient(model="gpt-4", api_key="k")
        e = _make_rate_limit_err(body=None)
        e.body = "insufficient_quota something"
        assert c._is_quota_error(e) is True

    def test_is_final_attempt_true(self):
        c = GPTClient(model="gpt-4", api_key="k", max_retries=3)
        assert c._is_final_attempt(2) is True

    def test_is_final_attempt_false(self):
        c = GPTClient(model="gpt-4", api_key="k", max_retries=3)
        assert c._is_final_attempt(0) is False

    def test_backoff_sleeps(self):
        c = GPTClient(model="gpt-4", api_key="k")
        with patch("asyncio.sleep", new=AsyncMock()) as mock_sleep:
            run(c._backoff(0, jitter=False))
            assert mock_sleep.call_args[0][0] == 1

    def test_backoff_increases_exponentially(self):
        c = GPTClient(model="gpt-4", api_key="k")
        with patch("asyncio.sleep", new=AsyncMock()) as mock_sleep:
            run(c._backoff(2, jitter=False))
            assert mock_sleep.call_args[0][0] == 4

    def test_backoff_jitter_adds_some_delay(self):
        c = GPTClient(model="gpt-4", api_key="k")
        delays = []

        async def capture_sleep(d):
            delays.append(d)

        with patch("asyncio.sleep", side_effect=capture_sleep):
            run(c._backoff(1, jitter=True))
        assert delays[0] >= 2