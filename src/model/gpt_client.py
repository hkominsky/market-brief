from typing import List, Dict
from openai import OpenAI
class GPTClient:
    # Abstracts OpenAI call

    def __init__(self, model: str, api_key: str):
        self.model = model
        self.client = OpenAI(api_key=api_key)

    def chat(self, messages: List[Dict[str, str]], max_tokens: int, temperature: float) -> str:
        # Sends a list of messages to the specified GPT model and returns the text response
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
        )
        return response.choices[0].message.content