import os
import sys
import tempfile
from unittest.mock import MagicMock
import pytest

sys.path.insert(0, os.path.dirname(__file__))

_whisper_stub = MagicMock()
sys.modules["whisper"] = _whisper_stub

from transcriber import Transcriber

def _make_transcriber(transcribe_return="mocked transcription"):
    mock_model = MagicMock()
    mock_model.transcribe.return_value = {"text": transcribe_return}
    _whisper_stub.load_model.return_value = mock_model
    t = Transcriber()
    t._model = mock_model
    return t


def _write_tmp(content, suffix=".txt", mode="w", encoding="utf-8"):
    kw = {"mode": mode, "suffix": suffix, "delete": False}
    if encoding and mode == "w":
        kw["encoding"] = encoding
    with tempfile.NamedTemporaryFile(**kw) as f:
        f.write(content)
        return f.name


class TestTranscriber:
    def test_default_model_name(self):
        assert Transcriber().model_name == "base"

    def test_custom_model_name(self):
        assert Transcriber("small").model_name == "small"

    def test_model_none_initially(self):
        assert Transcriber()._model is None

    def test_lazy_loads_whisper(self):
        _whisper_stub.load_model.reset_mock()
        _whisper_stub.load_model.return_value = MagicMock()
        t = Transcriber("medium")
        _ = t.model  # trigger lazy load
        _whisper_stub.load_model.assert_called_once_with("medium")

    def test_model_only_loaded_once(self):
        _whisper_stub.load_model.reset_mock()
        _whisper_stub.load_model.return_value = MagicMock()
        t = Transcriber()
        _ = t.model
        _ = t.model
        assert _whisper_stub.load_model.call_count == 1

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

    def test_transcribe_whisper_returns_text(self):
        t = _make_transcriber("quarterly revenue was strong")
        assert t._transcribe_whisper("fake.mp3") == "quarterly revenue was strong"

    def test_whisper_called_with_path(self):
        t = _make_transcriber()
        t._transcribe_whisper("/some/audio.mp3")
        t._model.transcribe.assert_called_once_with("/some/audio.mp3")

    def test_transcribe_audio_delegates(self):
        t = _make_transcriber("delegated result")
        assert t._transcribe_audio("fake.wav") == "delegated result"

    def test_empty_transcription(self):
        t = _make_transcriber("")
        assert t._transcribe_whisper("f.mp3") == ""

    def test_routes_txt(self):
        t = _make_transcriber()
        path = _write_tmp("transcript content")
        try:
            assert t.process(path, ".txt") == "transcript content"
        finally:
            os.unlink(path)

    def test_routes_mp3(self):
        t = _make_transcriber("mp3 result")
        assert t.process("fake.mp3", ".mp3") == "mp3 result"

    def test_routes_wav(self):
        t = _make_transcriber("wav result")
        assert t.process("fake.wav", ".wav") == "wav result"

    def test_pdf_raises_value_error(self):
        t = _make_transcriber()
        with pytest.raises(ValueError, match="Unsupported file type"):
            t.process("file.pdf", ".pdf")

    def test_docx_raises_value_error(self):
        t = _make_transcriber()
        with pytest.raises(ValueError):
            t.process("file.docx", ".docx")

    def test_error_message_contains_suffix(self):
        t = _make_transcriber()
        with pytest.raises(ValueError) as exc_info:
            t.process("file.docx", ".docx")
        assert ".docx" in str(exc_info.value)

    def test_uppercase_extension_raises(self):
        t = _make_transcriber()
        with pytest.raises(ValueError):
            t.process("file.MP4", ".MP4")