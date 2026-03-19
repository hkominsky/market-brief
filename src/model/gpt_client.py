import asyncio
import random
from typing import List, Dict
from openai import AsyncOpenAI, RateLimitError, APIStatusError


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
                response = await self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    max_tokens=max_tokens,
                    temperature=temperature,
                )
                return response.choices[0].message.content
            except RateLimitError:
                if attempt == self.max_retries - 1:
                    raise
                await asyncio.sleep((2 ** attempt) + random.uniform(0, 1))
            except APIStatusError as e:
                if e.status_code >= 500 and attempt < self.max_retries - 1:
                    await asyncio.sleep(2 ** attempt)
                else:
                    raise