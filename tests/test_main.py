import io
import os
import sys
from unittest.mock import AsyncMock, MagicMock
import pytest

sys.modules.setdefault("whisper", MagicMock())
sys.modules.setdefault("openai", MagicMock())

from schemas import AskRequest
import main as main_mod
from fastapi.testclient import TestClient

_mock_transcriber_inst = MagicMock()
_mock_transcriber_inst.process.return_value = "This is a transcript."

_mock_summarizer_inst = MagicMock()
_mock_summarizer_inst.summarize = AsyncMock(return_value={
    "summary": "Strong quarter.",
    "kpis": [{"kpi": "Revenue", "value": 10.0, "unit": "billion USD"}],
    "ticker": "AAPL",
    "date": "Q3 2024",
    "sentiment": {},
})

_mock_qa_inst = MagicMock()
_mock_qa_inst.ask = AsyncMock(return_value="Revenue was $10B.")

main_mod._transcriber = _mock_transcriber_inst
main_mod._summarizer = _mock_summarizer_inst
main_mod._qa = _mock_qa_inst

_client = TestClient(main_mod.app)


class TestMain:
    def test_valid_request(self):
        req = AskRequest(transcript="some transcript", question="What was revenue?")
        assert req.transcript == "some transcript" and req.question == "What was revenue?"

    def test_history_defaults_to_empty_list(self):
        req = AskRequest(transcript="t", question="q")
        assert req.history == []

    def test_history_accepts_list_of_dicts(self):
        h = [{"role": "user", "content": "prev"}]
        req = AskRequest(transcript="t", question="q", history=h)
        assert req.history == h

    def test_missing_transcript_raises(self):
        import pydantic
        with pytest.raises(pydantic.ValidationError):
            AskRequest(question="q")

    def test_missing_question_raises(self):
        import pydantic
        with pytest.raises(pydantic.ValidationError):
            AskRequest(transcript="t")

    def test_empty_transcript_allowed(self):
        req = AskRequest(transcript="", question="q")
        assert req.transcript == ""

    def test_empty_question_allowed(self):
        req = AskRequest(transcript="t", question="")
        assert req.question == ""

    def test_multi_turn_history(self):
        h = [
            {"role": "user", "content": "q1"},
            {"role": "assistant", "content": "a1"},
            {"role": "user", "content": "q2"},
        ]
        req = AskRequest(transcript="t", question="q3", history=h)
        assert len(req.history) == 3

    def test_txt_returns_200(self):
        resp = _client.post("/upload", files={"file": ("report.txt", io.BytesIO(b"text"), "text/plain")})
        assert resp.status_code == 200

    def test_txt_returns_summary(self):
        resp = _client.post("/upload", files={"file": ("report.txt", io.BytesIO(b"text"), "text/plain")})
        assert "summary" in resp.json()

    def test_txt_returns_kpis(self):
        resp = _client.post("/upload", files={"file": ("report.txt", io.BytesIO(b"text"), "text/plain")})
        assert "kpis" in resp.json()

    def test_txt_returns_transcript(self):
        resp = _client.post("/upload", files={"file": ("report.txt", io.BytesIO(b"text"), "text/plain")})
        assert "transcript" in resp.json()

    def test_mp3_returns_200(self):
        resp = _client.post("/upload", files={"file": ("call.mp3", io.BytesIO(b"\xff\xfb" * 10), "audio/mpeg")})
        assert resp.status_code == 200

    def test_wav_returns_200(self):
        resp = _client.post("/upload", files={"file": ("call.wav", io.BytesIO(b"RIFF" + b"\x00" * 40), "audio/wav")})
        assert resp.status_code == 200

    def test_pdf_returns_400(self):
        resp = _client.post("/upload", files={"file": ("report.pdf", io.BytesIO(b"%PDF"), "application/pdf")})
        assert resp.status_code == 400

    def test_pdf_error_message(self):
        resp = _client.post("/upload", files={"file": ("report.pdf", io.BytesIO(b"%PDF"), "application/pdf")})
        assert "Unsupported file type" in resp.json()["detail"]

    def test_docx_returns_400(self):
        resp = _client.post("/upload", files={"file": ("notes.docx", io.BytesIO(b"PK"), "application/octet-stream")})
        assert resp.status_code == 400

    def test_no_file_returns_422(self):
        assert _client.post("/upload").status_code == 422

    def test_cors_header_present(self):
        resp = _client.post(
            "/upload",
            files={"file": ("t.txt", io.BytesIO(b"text"), "text/plain")},
            headers={"Origin": "http://localhost:3000"},
        )
        assert "access-control-allow-origin" in resp.headers

    def test_cors_allows_localhost_3000(self):
        resp = _client.post(
            "/upload",
            files={"file": ("t.txt", io.BytesIO(b"text"), "text/plain")},
            headers={"Origin": "http://localhost:3000"},
        )
        assert resp.headers.get("access-control-allow-origin") == "http://localhost:3000"

    def test_returns_ticker(self):
        resp = _client.post("/upload", files={"file": ("t.txt", io.BytesIO(b"t"), "text/plain")})
        assert resp.json().get("ticker") == "AAPL"

    def test_returns_date(self):
        resp = _client.post("/upload", files={"file": ("t.txt", io.BytesIO(b"t"), "text/plain")})
        assert resp.json().get("date") == "Q3 2024"

    def test_mp3_calls_transcriber_with_mp3_suffix(self):
        _mock_transcriber_inst.process.reset_mock()
        _client.post("/upload", files={"file": ("call.mp3", io.BytesIO(b"\xff\xfb"), "audio/mpeg")})
        call_args = _mock_transcriber_inst.process.call_args
        assert call_args[0][1] == ".mp3"

    def test_txt_calls_transcriber_with_txt_suffix(self):
        _mock_transcriber_inst.process.reset_mock()
        _client.post("/upload", files={"file": ("r.txt", io.BytesIO(b"x"), "text/plain")})
        call_args = _mock_transcriber_inst.process.call_args
        assert call_args[0][1] == ".txt"

    def test_returns_200(self):
        resp = _client.post("/ask", json={"transcript": "t", "question": "q"})
        assert resp.status_code == 200

    def test_returns_answer_key(self):
        resp = _client.post("/ask", json={"transcript": "t", "question": "q"})
        assert "answer" in resp.json()

    def test_answer_text(self):
        _mock_qa_inst.ask = AsyncMock(return_value="Revenue was $10B.")
        resp = _client.post("/ask", json={"transcript": "t", "question": "q"})
        assert resp.json()["answer"] == "Revenue was $10B."

    def test_missing_transcript_returns_422(self):
        resp = _client.post("/ask", json={"question": "q"})
        assert resp.status_code == 422

    def test_missing_question_returns_422(self):
        resp = _client.post("/ask", json={"transcript": "t"})
        assert resp.status_code == 422

    def test_history_forwarded_to_qa(self):
        _mock_qa_inst.ask.reset_mock()
        history = [{"role": "user", "content": "prior q"}]
        _client.post("/ask", json={"transcript": "t", "question": "q", "history": history})
        call_kwargs = _mock_qa_inst.ask.call_args[1]
        assert call_kwargs["history"] == history

    def test_empty_history_allowed(self):
        resp = _client.post("/ask", json={"transcript": "t", "question": "q", "history": []})
        assert resp.status_code == 200

    def test_transcript_forwarded_to_qa(self):
        _mock_qa_inst.ask.reset_mock()
        _client.post("/ask", json={"transcript": "unique_content_xyz", "question": "q"})
        call_kwargs = _mock_qa_inst.ask.call_args[1]
        assert call_kwargs["transcript"] == "unique_content_xyz"

    def test_question_forwarded_to_qa(self):
        _mock_qa_inst.ask.reset_mock()
        _client.post("/ask", json={"transcript": "t", "question": "What was EPS?"})
        call_kwargs = _mock_qa_inst.ask.call_args[1]
        assert call_kwargs["question"] == "What was EPS?"