from pydantic import BaseModel
from typing import List, Dict

class AskRequest(BaseModel):
    # Request body for the Q&A endpoint
    transcript: str
    question: str
    history: List[Dict] = []