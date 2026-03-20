import asyncio
import random
from typing import List, Dict
from openai import AsyncOpenAI, RateLimitError, APIStatusError

class QuotaExceededError(RuntimeError):
    """Raised when the OpenAI account has insufficient quota/billing."""
    pass

class GPTClient:
    # Single shared async OpenAI client with retry logic for all GPT calls

    def __init__(self, model: str, api_key: str, max_retries: int = 4):
        # Stores model config and initializes the async OpenAI connection
        self.model = model
        self.max_retries = max_retries
        self.client = AsyncOpenAI(api_key=api_key)

    async def chat(self, messages: List[Dict[str, str]], max_tokens: int, temperature: float) -> str:
        # Sends messages to GPT and retries with exponential backoff on rate limit or server errors
        for attempt in range(self.max_retries):
            try:
                return await self._create_completion(messages, max_tokens, temperature)
            except QuotaExceededError:
                raise
            except RateLimitError as e:
                await self._handle_rate_limit(e, attempt)
            except APIStatusError as e:
                await self._handle_server_error(e, attempt)
        raise RuntimeError("GPT chat failed after all retries without a terminal exception")

    async def _create_completion(self, messages: List[Dict[str, str]], max_tokens: int, temperature: float) -> str:
        # Calls the OpenAI completions endpoint and returns the response text
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
        )
        return response.choices[0].message.content

    async def _handle_rate_limit(self, e: RateLimitError, attempt: int) -> None:
        # Raises QuotaExceededError for billing issues, otherwise retries with backoff
        if self._is_quota_error(e):
            raise QuotaExceededError(
                "I'm broke and ran out of tokens 😔"
            ) from e
        if self._is_final_attempt(attempt):
            raise
        await self._backoff(attempt, jitter=True)

    async def _handle_server_error(self, e: APIStatusError, attempt: int) -> None:
        # Retries on 5xx errors until the final attempt, then re-raises
        if e.status_code >= 500 and not self._is_final_attempt(attempt):
            await self._backoff(attempt)
        else:
            raise

    def _is_quota_error(self, e: RateLimitError) -> bool:
        # Distinguishes a hard billing quota error from a temporary rate limit
        try:
            if isinstance(e.body, dict):
                return e.body.get("code") == "insufficient_quota"
            return "insufficient_quota" in str(e)
        except Exception:
            return False

    def _is_final_attempt(self, attempt: int) -> bool:
        # Returns True if this is the last allowed retry attempt
        return attempt == self.max_retries - 1

    async def _backoff(self, attempt: int, jitter: bool = False) -> None:
        # Sleeps for an exponentially increasing duration, with optional random jitter
        delay = (2 ** attempt) + (random.uniform(0, 1) if jitter else 0)
        await asyncio.sleep(delay)