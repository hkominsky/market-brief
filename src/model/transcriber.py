from openai import AsyncOpenAI

class Transcriber:
    # Processes uploaded files into plain text. Accepts .mp3, .wav, and .txt

    def __init__(self, api_key: str):
        # Initializes the async OpenAI client for audio transcription
        self.client = AsyncOpenAI(api_key=api_key)

    async def process(self, file_path: str, suffix: str) -> str:
        # Routes the file to the appropriate processing method based on its extension
        if suffix == ".txt":
            return self._read_text(file_path)
        elif suffix in [".mp3", ".wav"]:
            return await self._transcribe_audio(file_path)
        else:
            raise ValueError(f"Unsupported file type: {suffix}")

    def _read_text(self, path: str) -> str:
        # Opens and reads the contents of a text file using UTF-8 encoding
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            return f.read()

    async def _transcribe_audio(self, path: str) -> str:
        # Sends the audio file to the OpenAI Whisper API and returns the transcript
        with open(path, "rb") as f:
            result = await self.client.audio.transcriptions.create(
                model="whisper-1",
                file=f,
            )
        return result.text