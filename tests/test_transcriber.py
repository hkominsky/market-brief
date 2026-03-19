import pytest
import sys, os, tempfile
from unittest.mock import MagicMock

sys.path.insert(0, os.path.dirname(__file__))

_whisper_stub = MagicMock()
sys.modules["whisper"] = _whisper_stub

from transcriber import Transcriber


def _make_transcriber():
    mock_model = MagicMock()
    mock_model.transcribe.return_value = {"text": "mocked transcription"}
    _whisper_stub.load_model.return_value = mock_model
    t = Transcriber()
    t.model = mock_model
    return t

def _write_tmp_txt(content):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".txt", mode="w", encoding="utf-8") as f:
        f.write(content)
        return f.name


class TestTranscriber:
    def test_loads_whisper_model_name(self):
        _whisper_stub.load_model.reset_mock()
        Transcriber("small")
        _whisper_stub.load_model.assert_called_once_with("small")

    def test_default_model_is_base(self):
        _whisper_stub.load_model.reset_mock()
        Transcriber()
        _whisper_stub.load_model.assert_called_once_with("base")

    def test_reads_plain_text(self):
        t = _make_transcriber()
        path = _write_tmp_txt("Hello earnings call.")
        try:
            assert t._read_text(path) == "Hello earnings call."
        finally:
            os.unlink(path)

    def test_reads_multiline_text(self):
        t = _make_transcriber()
        content = "Line 1\nLine 2\nLine 3"
        path = _write_tmp_txt(content)
        try:
            assert t._read_text(path) == content
        finally:
            os.unlink(path)

    def test_reads_empty_file(self):
        t = _make_transcriber()
        path = _write_tmp_txt("")
        try:
            assert t._read_text(path) == ""
        finally:
            os.unlink(path)

    def test_replaces_bad_encoding_bytes(self):
        t = _make_transcriber()
        with tempfile.NamedTemporaryFile(delete=False, suffix=".txt", mode="wb") as f:
            f.write(b"good text \xff bad byte")
            path = f.name
        try:
            assert "good text" in t._read_text(path)
        finally:
            os.unlink(path)

    def test_transcribe_whisper_returns_text(self):
        t = _make_transcriber()
        t.model.transcribe.return_value = {"text": "quarterly revenue was strong"}
        assert t._transcribe_whisper("fake.mp3") == "quarterly revenue was strong"

    def test_transcribe_audio_delegates_to_whisper(self):
        t = _make_transcriber()
        t.model.transcribe.return_value = {"text": "delegated result"}
        assert t._transcribe_audio("fake.wav") == "delegated result"

    def test_whisper_called_with_path(self):
        t = _make_transcriber()
        t.model.transcribe.return_value = {"text": ""}
        t._transcribe_whisper("/some/audio.mp3")
        t.model.transcribe.assert_called_once_with("/some/audio.mp3")

    def test_process_routes_txt(self):
        t = _make_transcriber()
        path = _write_tmp_txt("transcript content")
        try:
            assert t.process(path, ".txt") == "transcript content"
        finally:
            os.unlink(path)

    def test_process_routes_mp3(self):
        t = _make_transcriber()
        t.model.transcribe.return_value = {"text": "mp3 result"}
        assert t.process("fake.mp3", ".mp3") == "mp3 result"

    def test_process_routes_wav(self):
        t = _make_transcriber()
        t.model.transcribe.return_value = {"text": "wav result"}
        assert t.process("fake.wav", ".wav") == "wav result"

    def test_process_unsupported_raises(self):
        t = _make_transcriber()
        with pytest.raises(ValueError, match="Unsupported file type"):
            t.process("file.pdf", ".pdf")

    def test_process_unsupported_message_contains_suffix(self):
        t = _make_transcriber()
        with pytest.raises(ValueError) as exc_info:
            t.process("file.docx", ".docx")
        assert ".docx" in str(exc_info.value)