from pydantic import BaseModel, HttpUrl
from typing import List, Literal

class TranscriptionRequest(BaseModel):
    video_url: HttpUrl
    language: str = "de"
    model: Literal["tiny", "base", "small", "medium", "large", "turbo"] = "tiny"

class TranscriptSegment(BaseModel):
    id: int
    start: float
    end: float
    text: str

class TranscriptionResponse(BaseModel):
    id: str
    audio_url: str
    language: str
    text: str
    segments: List[TranscriptSegment]