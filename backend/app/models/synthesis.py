from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

from app.models.camel_case import CamelCaseModel
from app.models.question_answering import QueryResult


# Schema for structured output for LLM answers
class AnswerPoint(BaseModel):
    """A point made in the answer with a reference to the video."""

    content: str = Field(..., description="The text content explaining this point.")
    timestamp_seconds: float = Field(
        ...,
        description="The timestamp in seconds where this point is discussed in the video.",
    )


class Answer(BaseModel):
    """A structured answer to a question about the video."""

    summary: str = Field(..., description="A concise summary answering the question.")
    points: List[AnswerPoint] = Field(
        ...,
        description="List of specific points that address the question, with timestamps.",
    )
    not_addressed: bool = Field(
        ...,
        description="Flag indicating if the question cannot be fully answered from the transcript.",
    )


# API Models for model management
class ModelInfo(CamelCaseModel):
    id: str
    name: str
    description: str
    requires_gpu: bool
    is_loaded: bool


class ModelListResponse(CamelCaseModel):
    models: List[ModelInfo]
    active_model_id: Optional[str] = None
    has_gpu: bool = False


class ModelSelectRequest(CamelCaseModel):
    model_id: str


class ModelSelectResponse(CamelCaseModel):
    success: bool
    message: str
    model_id: Optional[str] = None


# API Models for LLM answers
class LLMAnswerRequest(CamelCaseModel):
    question: str
    transcript_id: str
    top_k: Optional[int] = 5
    model_id: Optional[str] = None


class LLMAnswerResponse(CamelCaseModel):
    question: str
    transcript_id: str
    summary: str
    points: List[Dict[str, Any]]
    not_addressed: bool
    model_id: str
    supporting_segments: List[QueryResult]
