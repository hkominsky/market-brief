from typing import List, Dict


class GPTClient:
    # Abstracts OpenAI call

    def __init__(self, model: str, api_key: str):
        # Initializes the OpenAI client with the provided API key and model name
        import openai
        openai.api_key = api_key
        self.model = model
        self.client = openai

    def chat(self, messages: List[Dict[str, str]], max_tokens: int, temperature: float) -> str:
        # Sends a list of messages to the specified GPT model and returns the text response
        response = self.client.ChatCompletion.create(
            model=self.model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
        )
        return response.choices[0].message.content