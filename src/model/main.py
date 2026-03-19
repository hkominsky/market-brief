from dotenv import load_dotenv

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import shutil, os, tempfile

from src.model.transcriber import Transcriber
from src.model.summarizer import Summarizer

load_dotenv()

app = FastAPI(title="MarketBrief API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/upload")
async def upload_transcript(file: UploadFile = File(...)):
    # Validates upload file
    suffix = os.path.splitext(file.filename)[1].lower()
    if suffix not in [".txt", ".mp3", ".wav"]:
        raise HTTPException(status_code=400, detail="Unsupported file type. Use .txt, .mp3, or .wav")

    # Creates a temporary file to store the transcription
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = tmp.name

    try:
        # Convert the uploaded file into plain text
        transcriber = Transcriber()
        text = transcriber.process(tmp_path, suffix)

        # Extract key insights and KPIs from the processed text
        summarizer = Summarizer()
        result = summarizer.summarize(text)

        return result
    finally:
        # Ensures the temporary file is deleted
        os.unlink(tmp_path)