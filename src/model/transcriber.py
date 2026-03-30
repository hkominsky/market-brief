import os
import math
from openai import AsyncOpenAI

MAX_FILE_MB = 24
CHUNK_DURATION_MS = 10 * 60 * 1000

class Transcriber:
    # Processes uploaded files into plain text. Accepts .mp3, .wav, and .txt

    def __init__(self, api_key: str):
        # Initialize the async OpenAI client for audio transcription
        self.client = AsyncOpenAI(api_key=api_key)

    async def process(self, file_path: str, suffix: str) -> str:
        # Route the file to the appropriate processing method based on extension
        if suffix == ".txt":
            return self._read_text(file_path)
        elif suffix in [".mp3", ".wav"]:
            return await self._transcribe_audio(file_path, suffix)
        else:
            raise ValueError(f"Unsupported file type: {suffix}")

    def _read_text(self, path: str) -> str:
        # Read the contents of a text file using UTF-8 encoding
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            return f.read()

    async def _transcribe_audio(self, path: str, suffix: str) -> str:
        # Transcribe audio, chunking if the file is too large
        if self._is_small_file(path):
            return await self._transcribe_file(path)
        return await self._transcribe_chunked(path, suffix)

    def _is_small_file(self, path: str) -> bool:
        # Check if the file size is within the direct transcription limit
        return os.path.getsize(path) / (1024 * 1024) <= MAX_FILE_MB

    async def _transcribe_file(self, path: str) -> str:
        # Send a single audio file to OpenAI Whisper API and return transcript
        with open(path, "rb") as f:
            result = await self.client.audio.transcriptions.create(
                model="whisper-1",
                file=f,
            )
        return result.text

    async def _transcribe_chunked(self, path: str, suffix: str) -> str:
        # Split large audio into chunks, transcribe each, and combine results
        audio = self._load_audio(path)
        chunk_ranges = self._get_chunk_ranges(len(audio))
        transcripts = await self._process_chunks(path, suffix, audio, chunk_ranges)
        return " ".join(transcripts)

    def _load_audio(self, path: str):
        # Load an audio file using pydub
        try:
            from pydub import AudioSegment
        except ImportError:
            raise RuntimeError("pydub is required for large audio files. Install it with: pip install pydub")
        return AudioSegment.from_file(path)

    def _get_chunk_ranges(self, total_duration: int) -> list[tuple[int, int]]:
        # Calculate start and end times for each audio chunk
        num_chunks = math.ceil(total_duration / CHUNK_DURATION_MS)
        return [(i * CHUNK_DURATION_MS, min((i + 1) * CHUNK_DURATION_MS, total_duration))
                for i in range(num_chunks)]

    async def _process_chunks(self, path: str, suffix: str, audio, chunk_ranges: list[tuple[int, int]]) -> list[str]:
        # Transcribe each audio chunk and return a list of transcripts
        transcripts = []
        for i, (start, end) in enumerate(chunk_ranges):
            chunk_path = f"{path}_chunk_{i}{suffix}"
            try:
                audio[start:end].export(chunk_path, format=suffix.lstrip("."))
                transcripts.append(await self._transcribe_file(chunk_path))
            finally:
                if os.path.exists(chunk_path):
                    os.unlink(chunk_path)
        return transcripts