import json
import os
import re
from typing import List, Dict, Any

from src.model.gpt_client import GPTClient
from src.model.kpi import KPI
class Summarizer:
    # Extracts a structured summary and KPIs from earnings call transcripts using GPT

    def __init__(self, model: str = "gpt-4.1-mini", max_tokens: int = 1024, temperature: float = 0.2):
        # Initializes the GPT client using the provided model settings and environment API key
        api_key = os.environ.get("OPEN_AI_API_KEY", "")
        self.client = GPTClient(model=model, api_key=api_key)
        self.max_tokens = max_tokens
        self.temperature = temperature

    def summarize(self, transcript: str) -> Dict[str, Any]:
        # Orchestrates the full summarization pipeline and returns a structured result dict
        raw = self._call_gpt(transcript)
        parsed = self._parse_response(raw)
        kpis = self._build_kpis(parsed.get("kpis", []))
        return {
            "summary": parsed.get("summary", ""),
            "kpis": [k.to_dict() for k in kpis],
        }

    def _build_prompt(self, transcript: str) -> List[Dict[str, str]]:
        # Constructs the message list sent to GPT, including a system role and the transcript
        system_message = (
            "Imagine you are a senior financial analyst assistant. "
            "Given an earnings call transcript, return a JSON object with two fields:\n"
            "1. \"summary\": a concise 3-5 sentence summary of the key business highlights.\n"
            "2. \"kpis\": a list of objects, each with \"kpi\" (metric name), "
            "\"value\" (numeric), and \"unit\" (e.g. USD, %, units). "
            "Extract only clearly stated numerical metrics. "
            "Respond with raw JSON only — no markdown, no explanation."
        )
        return [
            {"role": "system", "content": system_message},
            {"role": "user", "content": transcript},
        ]

    def _call_gpt(self, transcript: str) -> str:
        # Sends the constructed prompt to GPT and returns the raw text response
        messages = self._build_prompt(transcript)
        return self.client.chat(
            messages=messages,
            max_tokens=self.max_tokens,
            temperature=self.temperature,
        )

    def _parse_response(self, raw: str) -> Dict[str, Any]:
        # Strips markdown fences if present and parses the GPT response as JSON
        cleaned = re.sub(r"```(?:json)?|```", "", raw).strip()
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            return {"summary": raw, "kpis": []}

    def _build_kpis(self, raw_kpis: List[Dict[str, Any]]) -> List[KPI]:
        # Converts each raw KPI dict into a validated KPI object, skipping malformed entries
        kpis = []
        for item in raw_kpis:
            try:
                kpis.append(KPI(
                    kpi=str(item["kpi"]),
                    value=float(item["value"]),
                    unit=str(item["unit"]),
                ))
            except (KeyError, TypeError, ValueError):
                continue
        return kpis