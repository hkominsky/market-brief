import json
import os
import re
from typing import List, Dict, Any

from src.model.gpt_client import GPTClient
from src.model.kpi import KPI
class Summarizer:
    # Extracts a structured summary and KPIs from earnings call transcripts using GPT

    def __init__(self, model: str = "gpt-4.1-mini", max_tokens: int = 1024, temperature: float = 0.2):
        # Initializes the GPT client using the provided model settings and API key
        api_key = os.environ.get("OPEN_AI_API_KEY", "")
        self.client = GPTClient(model=model, api_key=api_key)
        self.chunker = Chunker(chunk_size=2000, overlap=200)
        self.max_tokens = max_tokens
        self.temperature = temperature

    async def summarize(self, transcript: str) -> Dict[str, Any]:
        # Entry point — routes to single or multi-chunk pipeline based on transcript length
        chunks = self.chunker.chunk(transcript)
        if len(chunks) == 1:
            parsed = await self._process_single(transcript)
        else:
            parsed = await self._process_chunks(chunks)
        kpis = self._build_kpis(parsed.get("kpis", []))
        return {"summary": parsed.get("summary", ""), "kpis": [k.to_dict() for k in kpis]}

    async def _process_single(self, transcript: str) -> Dict[str, Any]:
        # Handles short transcripts with a single GPT call
        raw = await self._call_gpt(transcript)
        return self._parse_response(raw)

    async def _process_chunks(self, chunks: List[str]) -> Dict[str, Any]:
        # Coordinates the map-reduce flow for long transcripts
        chunk_summaries, all_raw_kpis = await self._map_chunks(chunks)
        return await self._reduce_summaries(chunk_summaries, all_raw_kpis)

    async def _map_chunks(self, chunks: List[str]):
        # Fires all chunk GPT calls concurrently and collects summaries and KPIs
        results = await asyncio.gather(*[self._call_gpt(chunk) for chunk in chunks])
        chunk_summaries, all_raw_kpis = [], []
        for raw in results:
            parsed = self._parse_response(raw)
            chunk_summaries.append(parsed.get("summary", ""))
            all_raw_kpis.extend(parsed.get("kpis", []))
        return chunk_summaries, all_raw_kpis

    async def _reduce_summaries(self, chunk_summaries: List[str], all_raw_kpis: List[Dict[str, Any]]) -> Dict[str, Any]:
        # Collapses per-chunk summaries into one final summary and attaches deduped KPIs
        combined = "\n\n".join(s for s in chunk_summaries if s)
        raw = await self._call_gpt(combined)
        parsed = self._parse_response(raw)
        parsed["kpis"] = self._deduplicate_kpis(all_raw_kpis)
        return parsed

    def _build_prompt(self, transcript: str) -> List[Dict[str, str]]:
        # Constructs the system and user messages sent to GPT
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

    async def _call_gpt(self, transcript: str) -> str:
        # Sends the prompt to GPT and returns the raw text response
        messages = self._build_prompt(transcript)
        return await self.client.chat(messages=messages, max_tokens=self.max_tokens, temperature=self.temperature)

    def _parse_response(self, raw: str) -> Dict[str, Any]:
        # Strips markdown fences and parses the GPT response as JSON
        cleaned = re.sub(r"```(?:json)?|```", "", raw).strip()
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            return {"summary": raw, "kpis": []}

    def _build_kpis(self, raw_kpis: List[Dict[str, Any]]) -> List[KPI]:
        # Converts raw KPI dicts into validated KPI objects, skipping malformed entries
        kpis = []
        for item in raw_kpis:
            try:
                kpis.append(KPI(kpi=str(item["kpi"]), value=float(item["value"]), unit=str(item["unit"])))
            except (KeyError, TypeError, ValueError):
                continue
        return kpis

    def _deduplicate_kpis(self, raw_kpis: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        # Keeps the first occurrence of each KPI name across all chunks
        seen: set = set()
        result: List[Dict[str, Any]] = []
        for item in raw_kpis:
            key = str(item.get("kpi", "")).lower().strip()
            if key and key not in seen:
                seen.add(key)
                result.append(item)
        return result