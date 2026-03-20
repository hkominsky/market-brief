from typing import List, Dict
from src.model.gpt_client import GPTClient

class QAClient:
    # Answers freeform user questions grounded in an earnings call transcript

    def __init__(self, client: GPTClient):
        # Accepts a shared GPTClient rather than creating its own
        self.client = client

    async def ask(self, transcript: str, question: str, history: List[Dict] = None) -> str:
        # Builds a prompt with the full transcript as context and returns an answer
        history = history or []
        return await self.client.chat(
            messages=self._build_prompt(transcript, question, history),
            max_tokens=512,
            temperature=0.3,
        )

    def _build_prompt(self, transcript: str, question: str, history: List[Dict]) -> List[Dict]:
        # Constructs the system context, conversation history, and current question
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