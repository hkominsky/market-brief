import whisper

class Transcriber:
    # Processes uploaded files into plain text. Accepts .mp3, .wav, and .txt

    def __init__(self, model_name: str = "base"):
        # Loads the specified Whisper model into memory
        self.model = whisper.load_model(model_name)

    def process(self, file_path: str, suffix: str) -> str:
        # Routes the file to the appropriate processing method based on its extension
        if suffix == ".txt":
            return self._read_text(file_path)
        elif suffix in [".mp3", ".wav"]:
            return self._transcribe_audio(file_path)
        else:
            raise ValueError(f"Unsupported file type: {suffix}")

    def _read_text(self, path: str) -> str:
        # Opens and reads the contents of a text file using UTF-8 encoding
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            return f.read()

    def _transcribe_audio(self, path: str) -> str:
        # Acts as a wrapper to initiate the audio transcription process
        return self._transcribe_whisper(path)

    def _transcribe_whisper(self, path: str) -> str:
        # Uses the loaded Whisper model to transcribe audio and returns the text result
        result = self.model.transcribe(path)
        return result["text"]