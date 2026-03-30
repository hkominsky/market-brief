import asyncio
import json
import re
from typing import List, Dict, Any

from src.model.gpt_client import GPTClient
from src.model.kpi import KPI
from src.model.chunker import Chunker

class Summarizer:
    # Extracts insights from earnings call transcripts

    def __init__(self, client: GPTClient):
        # Initialize with a shared GPTClient and Chunker
        self.client = client
        self.chunker = Chunker(chunk_size=2000, overlap=200)

    async def summarize(self, transcript: str) -> Dict[str, Any]:
        # Route to single or multi-chunk pipeline based on transcript length
        chunks = self.chunker.chunk(transcript)
        parsed = await (self._process_single(transcript) if len(chunks) == 1 else self._process_chunks(chunks))
        return self._build_result(parsed)

    def _build_result(self, parsed: Dict[str, Any]) -> Dict[str, Any]:
        # Assemble the final result dict from a parsed GPT response
        return {
            "summary": parsed.get("summary", ""),
            "kpis": [k.to_dict() for k in self._build_kpis(parsed.get("kpis", []))],
            "ticker": parsed.get("ticker"),
            "date": parsed.get("date"),
            "sentiment": parsed.get("sentiment", {}),
        }

    async def _process_single(self, transcript: str) -> Dict[str, Any]:
        # Handle short transcripts with a single GPT call
        return self._parse_response(await self._call_gpt(transcript))

    async def _process_chunks(self, chunks: List[str]) -> Dict[str, Any]:
        # Process long transcripts with map-reduce approach
        chunk_summaries, all_raw_kpis, metadata = await self._map_chunks(chunks)
        return await self._reduce_summaries(chunk_summaries, all_raw_kpis, metadata)

    async def _map_chunks(self, chunks: List[str]):
        # Run all GPT calls for each chunk concurrently and collect results
        raw_results = await asyncio.gather(*[self._call_gpt(c) for c in chunks])
        parsed_results = [self._parse_response(r) for r in raw_results]
        return self._extract_map_outputs(parsed_results)

    def _extract_map_outputs(self, parsed_results: List[Dict[str, Any]]):
        # Extract summaries, raw KPIs, and metadata from parsed chunk results
        chunk_summaries = [p.get("summary", "") for p in parsed_results]
        all_raw_kpis = [kpi for p in parsed_results for kpi in p.get("kpis", [])]
        metadata = self._extract_metadata(parsed_results)
        return chunk_summaries, all_raw_kpis, metadata

    def _extract_metadata(self, parsed_chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
        # Aggregate metadata like ticker, date, and sentiment across chunks
        return {
            "ticker": self._first_value(parsed_chunks, "ticker"),
            "date": self._first_value(parsed_chunks, "date"),
            "sentiment": self._aggregate_sentiment(parsed_chunks),
        }

    def _first_value(self, parsed_chunks: List[Dict[str, Any]], key: str) -> Any:
        # Return the first non-null value for a key across chunks
        return next((p[key] for p in parsed_chunks if p.get(key)), None)

    def _aggregate_sentiment(self, parsed_chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
        # Compute confidence-weighted sentiment per section across all chunks
        sections = ["prepared_statements", "qa"]
        return {sec: self._compute_section_sentiment(parsed_chunks, sec) for sec in sections}

    def _compute_section_sentiment(self, parsed_chunks: List[Dict[str, Any]], section: str) -> Dict[str, Any]:
        # Compute the label and confidence for a single sentiment section
        label_weights = {"bullish": 0.0, "neutral": 0.0, "bearish": 0.0}
        total_weight = 0.0

        for p in parsed_chunks:
            section_data = p.get("sentiment", {}).get(section, {})
            label, confidence = section_data.get("label"), section_data.get("confidence", 0.0)
            if label in label_weights and isinstance(confidence, (int, float)):
                label_weights[label] += confidence
                total_weight += confidence

        if total_weight == 0:
            return {"label": "neutral", "confidence": 0.0}

        winning_label = max(label_weights, key=label_weights.get)
        return {"label": winning_label, "confidence": round(label_weights[winning_label] / total_weight, 3)}

    async def _reduce_summaries(self, chunk_summaries: List[str], all_raw_kpis: List[Dict[str, Any]], metadata: Dict[str, Any]) -> Dict[str, Any]:
        # Combine chunk summaries into a final summary and merge metadata
        combined_text = "\n\n".join(s for s in chunk_summaries if s)
        parsed = self._parse_response(await self._call_gpt(combined_text))
        return {**parsed, **self._merge_metadata(parsed, metadata), "kpis": self._deduplicate_kpis(all_raw_kpis)}

    def _merge_metadata(self, parsed: Dict[str, Any], metadata: Dict[str, Any]) -> Dict[str, Any]:
        # Fill missing fields in reduce-phase output from map-phase metadata
        return {key: parsed.get(key) or metadata.get(key) for key in ("ticker", "date", "sentiment")}

    def _build_prompt(self, transcript: str) -> List[Dict[str, str]]:
        # Construct the system prompt for GPT structured JSON output
        return [
            {"role": "system", "content": (
                "You are a senior financial analyst assistant. "
                "Given an earnings call transcript, return a single JSON object with these fields:\n"
                "1. \"summary\": a concise 3-5 sentence summary of key business highlights.\n"
                "2. \"kpis\": list of objects with \"kpi\", \"value\", and \"unit\" (%/B/M/K/x or empty string).\n"
                "3. \"ticker\": company ticker symbol (e.g. AAPL). Return null if not found.\n"
                "4. \"date\": earnings call period (e.g. Q3 2024). Return null if not found.\n"
                "5. \"sentiment\": object with \"prepared_statements\" and \"qa\" each containing \"label\" and \"confidence\".\n"
                "Respond with raw JSON only — no markdown, no explanation."
            )},
            {"role": "user", "content": transcript},
        ]

    async def _call_gpt(self, transcript: str) -> str:
        # Send prompt to GPT and return the raw response
        return await self.client.chat(messages=self._build_prompt(transcript), max_tokens=1024, temperature=0.2)

    def _parse_response(self, raw: str) -> Dict[str, Any]:
        # Parse GPT JSON response safely, fallback to minimal dict on error
        cleaned = re.sub(r"```(?:json)?|```", "", raw).strip()
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            return {"summary": raw, "kpis": [], "ticker": None, "date": None, "sentiment": {}}

    def _build_kpis(self, raw_kpis: List[Dict[str, Any]]) -> List[KPI]:
        # Convert raw KPI dicts into validated KPI objects
        return [kpi for kpi in (self._try_build_kpi(item) for item in raw_kpis) if kpi]

    def _try_build_kpi(self, item: Dict[str, Any]):
        # Attempt to construct a KPI object; return None if invalid
        try:
            return KPI(kpi=str(item["kpi"]), value=float(item["value"]), unit=str(item["unit"]))
        except (KeyError, TypeError, ValueError):
            return None

    def _deduplicate_kpis(self, raw_kpis: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        # Keep the first occurrence of each KPI name across all chunks
        seen: set = set()
        result: List[Dict[str, Any]] = []
        for item in raw_kpis:
            key = str(item.get("kpi", "")).lower().strip()
            if key and key not in seen:
                seen.add(key)
                result.append(item)
        return result