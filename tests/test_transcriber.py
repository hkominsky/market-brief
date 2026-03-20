import os
import tempfile
from unittest.mock import AsyncMock, MagicMock, patch
from transcriber import Transcriber
import pytest

def _make_transcriber(transcribe_return="mocked transcription"):
    t = Transcriber(api_key="test-key")
    t.client = MagicMock()
    t.client.audio.transcriptions.create = AsyncMock(
        return_value=MagicMock(text=transcribe_return)
    )
    return t

def _write_tmp(content, suffix=".txt", mode="w", encoding="utf-8"):
    kw = {"mode": mode, "suffix": suffix, "delete": False}
    if encoding and mode == "w":
        kw["encoding"] = encoding
    with tempfile.NamedTemporaryFile(**kw) as f:
        f.write(content)
        return f.name

class TestTranscriber:
    def test_stores_api_key(self):
        t = Transcriber(api_key="sk-test")
        assert t.client.api_key == "sk-test"

    def test_reads_plain_text(self):
        t = _make_transcriber()
        path = _write_tmp("Hello earnings call.")
        try:
            assert t._read_text(path) == "Hello earnings call."
        finally:
            os.unlink(path)

    def test_reads_multiline_text(self):
        t = _make_transcriber()
        content = "Line 1\nLine 2\nLine 3"
        path = _write_tmp(content)
        try:
            assert t._read_text(path) == content
        finally:
            os.unlink(path)

    def test_reads_empty_file(self):
        t = _make_transcriber()
        path = _write_tmp("")
        try:
            assert t._read_text(path) == ""
        finally:
            os.unlink(path)

    def test_replaces_bad_encoding_bytes(self):
        t = _make_transcriber()
        path = _write_tmp(b"good text \xff bad byte", suffix=".txt", mode="wb", encoding=None)
        try:
            assert "good text" in t._read_text(path)
        finally:
            os.unlink(path)

    def test_unicode_content(self):
        t = _make_transcriber()
        content = "Revenue: \u20ac500M\nGrowth: 12%"
        path = _write_tmp(content)
        try:
            assert t._read_text(path) == content
        finally:
            os.unlink(path)

    def test_transcribe_audio_returns_text(self):
        t = _make_transcriber("quarterly revenue was strong")
        path = _write_tmp(b"fake audio", suffix=".mp3", mode="wb", encoding=None)
        try:
            assert asyncio.run(t._transcribe_audio(path)) == "quarterly revenue was strong"
        finally:
            os.unlink(path)

    def test_transcribe_audio_calls_api(self):
        t = _make_transcriber()
        path = _write_tmp(b"fake audio", suffix=".mp3", mode="wb", encoding=None)
        try:
            asyncio.run(t._transcribe_audio(path))
            assert t.client.audio.transcriptions.create.call_count == 1
        finally:
            os.unlink(path)

    def test_transcribe_uses_whisper_1_model(self):
        t = _make_transcriber()
        path = _write_tmp(b"fake audio", suffix=".mp3", mode="wb", encoding=None)
        try:
            asyncio.run(t._transcribe_audio(path))
            call_kwargs = t.client.audio.transcriptions.create.call_args[1]
            assert call_kwargs["model"] == "whisper-1"
        finally:
            os.unlink(path)

    def test_process_routes_txt(self):
        t = _make_transcriber()
        path = _write_tmp("transcript content")
        try:
            assert asyncio.run(t.process(path, ".txt")) == "transcript content"
        finally:
            os.unlink(path)

    def test_process_routes_mp3(self):
        t = _make_transcriber("mp3 result")
        path = _write_tmp(b"fake audio", suffix=".mp3", mode="wb", encoding=None)
        try:
            assert asyncio.run(t.process(path, ".mp3")) == "mp3 result"
        finally:
            os.unlink(path)

    def test_process_routes_wav(self):
        t = _make_transcriber("wav result")
        path = _write_tmp(b"fake audio", suffix=".wav", mode="wb", encoding=None)
        try:
            assert asyncio.run(t.process(path, ".wav")) == "wav result"
        finally:
            os.unlink(path)

    def test_pdf_raises_value_error(self):
        t = _make_transcriber()
        with pytest.raises(ValueError, match="Unsupported file type"):
            asyncio.run(t.process("file.pdf", ".pdf"))

    def test_docx_raises_value_error(self):
        t = _make_transcriber()
        with pytest.raises(ValueError):
            asyncio.run(t.process("file.docx", ".docx"))

    def test_error_message_contains_suffix(self):
        t = _make_transcriber()
        with pytest.raises(ValueError) as exc_info:
            asyncio.run(t.process("file.docx", ".docx"))
        assert ".docx" in str(exc_info.value)

    def test_uppercase_extension_raises(self):
        t = _make_transcriber()
        with pytest.raises(ValueError):
            asyncio.run(t.process("file.MP4", ".MP4"))