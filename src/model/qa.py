from typing import List, Dict
from src.model.gpt_client import GPTClient

WORDS_PER_TOKEN = 1.3
SYSTEM_TOKEN_BUDGET = 3000
COMPLETION_TOKEN_BUDGET = 512
MAX_HISTORY_TOKENS = 2000

class QAClient:
    # Answers freeform user questions grounded in an earnings call transcript

    def __init__(self, client: GPTClient):
        # Initialize with a shared GPTClient
        self.client = client

    async def ask(self, transcript: str, question: str, history: List[Dict] = None) -> str:
        # Build a prompt with transcript context and return GPT answer
        history = history or []
        truncated_history = self._truncate_history(history)
        messages = self._build_prompt(transcript, question, truncated_history)
        return await self.client.chat(
            messages=messages,
            max_tokens=COMPLETION_TOKEN_BUDGET,
            temperature=0.3,
        )

    def _estimate_tokens(self, text: str) -> int:
        # Estimate token count from word count
        return int(len(text.split()) / WORDS_PER_TOKEN)

    def _truncate_history(self, history: List[Dict]) -> List[Dict]:
        # Truncate oldest messages until history fits token budget
        total_tokens = self._total_tokens(history)

        while total_tokens > MAX_HISTORY_TOKENS and len(history) >= 2:
            removed, history = history[:2], history[2:]
            total_tokens -= self._total_tokens(removed)

        return history

    def _total_tokens(self, messages: List[Dict]) -> int:
        # Compute total token estimate for a list of messages
        return sum(self._estimate_tokens(m.get("content", "")) for m in messages)

    def _build_prompt(self, transcript: str, question: str, history: List[Dict]) -> List[Dict]:
        # Construct system context, conversation history, and current question
        return [
            {"role": "system", "content": (
                "You are a financial analyst assistant. "
                "Answer questions about the earnings call transcript below. "
                "Be concise and cite specific figures where relevant.\n\n"
                f"TRANSCRIPT:\n{transcript}"
            )},
            *history,
            {"role": "user", "content": question},
        ]