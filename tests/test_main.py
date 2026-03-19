import pytest
import sys, os, io
from unittest.mock import MagicMock
import main as main_mod
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.dirname(__file__))

sys.modules["whisper"] = MagicMock()

_mock_transcriber = MagicMock()
_mock_transcriber.process.return_value = "This is a transcript."
_transcriber_mod = MagicMock()
_transcriber_mod.Transcriber.return_value = _mock_transcriber
sys.modules["transcriber"] = _transcriber_mod

_mock_summarizer = MagicMock()
_mock_summarizer.summarize.return_value = {
    "summary": "Strong quarter.",
    "kpis": [{"kpi": "Revenue", "value": 10.0, "unit": "billion USD"}],
}
_summarizer_mod = MagicMock()
_summarizer_mod.Summarizer.return_value = _mock_summarizer
sys.modules["summarizer"] = _summarizer_mod

@pytest.fixture(scope="module")
def client():
    yield TestClient(main_mod.app)


class TestUploadEndpoint:
    def test_txt_returns_200(self, client):
        resp = client.post("/upload", files={"file": ("report.txt", io.BytesIO(b"text"), "text/plain")})
        assert resp.status_code == 200

    def test_txt_returns_summary(self, client):
        resp = client.post("/upload", files={"file": ("report.txt", io.BytesIO(b"text"), "text/plain")})
        assert "summary" in resp.json()

    def test_txt_returns_kpis(self, client):
        resp = client.post("/upload", files={"file": ("report.txt", io.BytesIO(b"text"), "text/plain")})
        assert "kpis" in resp.json()

    def test_mp3_returns_200(self, client):
        resp = client.post("/upload", files={"file": ("call.mp3", io.BytesIO(b"\xff\xfb" * 10), "audio/mpeg")})
        assert resp.status_code == 200

    def test_wav_returns_200(self, client):
        resp = client.post("/upload", files={"file": ("call.wav", io.BytesIO(b"RIFF" + b"\x00" * 40), "audio/wav")})
        assert resp.status_code == 200

    def test_pdf_returns_400(self, client):
        resp = client.post("/upload", files={"file": ("report.pdf", io.BytesIO(b"%PDF"), "application/pdf")})
        assert resp.status_code == 400

    def test_pdf_error_message(self, client):
        resp = client.post("/upload", files={"file": ("report.pdf", io.BytesIO(b"%PDF"), "application/pdf")})
        assert "Unsupported file type" in resp.json()["detail"]

    def test_docx_returns_400(self, client):
        resp = client.post("/upload", files={"file": ("notes.docx", io.BytesIO(b"PK"), "application/octet-stream")})
        assert resp.status_code == 400

    def test_no_file_returns_422(self, client):
        assert client.post("/upload").status_code == 422

    def test_cors_header_present(self, client):
        resp = client.post(
            "/upload",
            files={"file": ("t.txt", io.BytesIO(b"text"), "text/plain")},
            headers={"Origin": "http://localhost:3000"},
        )
        assert "access-control-allow-origin" in resp.headers

    def test_cors_allows_localhost_3000(self, client):
        resp = client.post(
            "/upload",
            files={"file": ("t.txt", io.BytesIO(b"text"), "text/plain")},
            headers={"Origin": "http://localhost:3000"},
        )
        assert resp.headers.get("access-control-allow-origin") == "http://localhost:3000"