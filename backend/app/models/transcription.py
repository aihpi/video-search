from pydantic import BaseModel, ConfigDict, HttpUrl
from pydantic.alias_generators import to_camel
from typing import List, Literal, Optional

from app.services.transcription import DEFAULT_MODEL


class CamelCaseModel(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True,
    )


class TranscriptionRequest(CamelCaseModel):
    video_url: HttpUrl
    model: Literal["tiny", "base", "small", "medium", "large", "turbo"] = DEFAULT_MODEL
    language: Optional[str]


class TranscriptSegment(CamelCaseModel):
    id: int
    start: float
    end: float
    text: str


class TranscriptionResponse(CamelCaseModel):
    id: str
    audio_url: str
    language: str
    text: str
    segments: List[TranscriptSegment]
