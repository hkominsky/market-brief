import asyncio
import json
import re
from typing import List, Dict, Any

from src.model.gpt_client import GPTClient
from src.model.kpi import KPI
from src.model.chunker import Chunker


class Summarizer:
    # Extracts all insights from an earnings call transcript in a single GPT call

    def __init__(self, client: GPTClient):
        # Accepts a shared GPTClient and initializes the chunker
        self.client = client
        self.chunker = Chunker(chunk_size=2000, overlap=200)

    async def summarize(self, transcript: str) -> Dict[str, Any]:
        # Routes to single or multi-chunk pipeline based on transcript length
        chunks = self.chunker.chunk(transcript)
        parsed = await self._process_single(transcript) if len(chunks) == 1 else await self._process_chunks(chunks)
        return self._build_result(parsed)

    def _build_result(self, parsed: Dict[str, Any]) -> Dict[str, Any]:
        # Assembles the final result dict from a parsed GPT response
        return {
            "summary": parsed.get("summary", ""),
            "kpis": [k.to_dict() for k in self._build_kpis(parsed.get("kpis", []))],
            "ticker": parsed.get("ticker"),
            "date": parsed.get("date"),
            "sentiment": parsed.get("sentiment", {}),
        }

    async def _process_single(self, transcript: str) -> Dict[str, Any]:
        # Handles short transcripts with a single GPT call
        return self._parse_response(await self._call_gpt(transcript))

    async def _process_chunks(self, chunks: List[str]) -> Dict[str, Any]:
        # Coordinates the map-reduce flow for long transcripts
        chunk_summaries, all_raw_kpis, metadata = await self._map_chunks(chunks)
        return await self._reduce_summaries(chunk_summaries, all_raw_kpis, metadata)

    async def _map_chunks(self, chunks: List[str]):
        # Fires all chunk GPT calls concurrently and collects summaries, KPIs, and metadata
        results = [self._parse_response(raw) for raw in await asyncio.gather(*[self._call_gpt(c) for c in chunks])]
        chunk_summaries = [p.get("summary", "") for p in results]
        all_raw_kpis = [kpi for p in results for kpi in p.get("kpis", [])]
        metadata = self._extract_metadata(results)
        return chunk_summaries, all_raw_kpis, metadata

    def _extract_metadata(self, parsed_chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
        # Picks the first non-null ticker, date, and sentiment found across all chunk results
        return {
            "ticker": self._first_value(parsed_chunks, "ticker"),
            "date": self._first_value(parsed_chunks, "date"),
            "sentiment": self._first_value(parsed_chunks, "sentiment"),
        }

    def _first_value(self, parsed_chunks: List[Dict[str, Any]], key: str) -> Any:
        # Returns the first truthy value for a given key across a list of parsed dicts
        return next((p[key] for p in parsed_chunks if p.get(key)), None)

    async def _reduce_summaries(self, chunk_summaries: List[str], all_raw_kpis: List[Dict[str, Any]], metadata: Dict[str, Any]) -> Dict[str, Any]:
        # Collapses per-chunk summaries into one final summary and restores metadata
        parsed = self._parse_response(await self._call_gpt("\n\n".join(s for s in chunk_summaries if s)))
        return {**parsed, **self._merge_metadata(parsed, metadata), "kpis": self._deduplicate_kpis(all_raw_kpis)}

    def _merge_metadata(self, parsed: Dict[str, Any], metadata: Dict[str, Any]) -> Dict[str, Any]:
        # Falls back to map-phase metadata for any fields the reduce step did not populate
        return {key: parsed.get(key) or metadata.get(key) for key in ("ticker", "date", "sentiment")}

    def _build_prompt(self, transcript: str) -> List[Dict[str, str]]:
        # Constructs the system prompt that instructs GPT to return a structured JSON response
        return [
            {"role": "system", "content": (
                "You are a senior financial analyst assistant. "
                "Given an earnings call transcript, return a single JSON object with these fields:\n"
                "1. \"summary\": a concise 3-5 sentence summary of the key business highlights.\n"
                "2. \"kpis\": a list of objects each with \"kpi\" (metric name), \"value\" (numeric), and \"unit\" (e.g. USD, %, units). Extract only clearly stated numerical metrics.\n"
                "3. \"ticker\": the company ticker symbol (e.g. AAPL). Return null if not found.\n"
                "4. \"date\": the earnings call period (e.g. Q3 2024). Return null if not found.\n"
                "5. \"sentiment\": an object with two keys \"prepared_statements\" and \"qa\", each containing \"label\" (bullish, neutral, or bearish), \"confidence\" (0.0-1.0), and \"key_phrases\" (list of up to 3 phrases that drove the assessment).\n"
                "Respond with raw JSON only — no markdown, no explanation."
            )},
            {"role": "user", "content": transcript},
        ]

    async def _call_gpt(self, transcript: str) -> str:
        # Sends the prompt to GPT and returns the raw text response
        return await self.client.chat(messages=self._build_prompt(transcript), max_tokens=1024, temperature=0.2)

    def _parse_response(self, raw: str) -> Dict[str, Any]:
        # Strips markdown fences and parses the GPT response as JSON, falling back to a safe default
        cleaned = re.sub(r"```(?:json)?|```", "", raw).strip()
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            return {"summary": raw, "kpis": [], "ticker": None, "date": None, "sentiment": {}}

    def _build_kpis(self, raw_kpis: List[Dict[str, Any]]) -> List[KPI]:
        # Converts raw KPI dicts into validated KPI objects, skipping malformed entries
        return [kpi for kpi in (self._try_build_kpi(item) for item in raw_kpis) if kpi is not None]

    def _try_build_kpi(self, item: Dict[str, Any]):
        # Attempts to construct a single KPI object, returning None if the data is invalid
        try:
            return KPI(kpi=str(item["kpi"]), value=float(item["value"]), unit=str(item["unit"]))
        except (KeyError, TypeError, ValueError):
            return None

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