import os
import shutil
import tempfile

from dotenv import load_dotenv
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from src.model.gpt_client import GPTClient, TokenLimitExceededError, QuotaExceededError
from src.model.transcriber import Transcriber
from src.model.summarizer import Summarizer
from src.model.qa import QAClient
from src.model.schemas import AskRequest

load_dotenv()

app = FastAPI(title="MarketBrief API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://marketbrief-gold.vercel.app",
        "https://marketbrief.dev",
        "https://www.marketbrief.dev",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

_gpt = GPTClient(model="gpt-4.1-mini", api_key=os.environ.get("OPEN_AI_API_KEY", ""))
_transcriber = Transcriber(api_key=os.environ.get("OPEN_AI_API_KEY", ""))
_summarizer = Summarizer(client=_gpt)
_qa = QAClient(client=_gpt)


@app.post("/upload")
async def upload_transcript(file: UploadFile = File(...)):
    # Validates, transcribes, and analyzes an uploaded earnings call file
    suffix = os.path.splitext(file.filename)[1].lower()
    if suffix not in [".txt", ".mp3", ".wav"]:
        raise HTTPException(status_code=400, detail="Unsupported file type. Use .txt, .mp3, or .wav")

    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = tmp.name

    try:
        text = await _transcriber.process(tmp_path, suffix)
        result = await _summarizer.summarize(text)
        return {**result, "transcript": text}
    except QuotaExceededError as e:
        raise HTTPException(status_code=402, detail=str(e))
    except TokenLimitExceededError as e:
        raise HTTPException(status_code=422, detail=str(e))
    finally:
        os.unlink(tmp_path)


@app.post("/ask")
async def ask_question(body: AskRequest):
    # Answers a user question grounded in the provided transcript and conversation history
    try:
        answer = await _qa.ask(
            transcript=body.transcript,
            question=body.question,
            history=body.history,
        )
        return {"answer": answer}
    except QuotaExceededError as e:
        raise HTTPException(status_code=402, detail=str(e))
    except TokenLimitExceededError as e:
        raise HTTPException(status_code=422, detail=str(e))