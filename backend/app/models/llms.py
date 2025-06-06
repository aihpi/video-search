from pydantic import BaseModel, Field
from typing import List, Optional

from app.models.camel_case import CamelCaseModel


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
    model_id: str = Field(
        ..., description="Identifier for the model used to generate the answer."
    )


# API Models for model management
class LLMInfo(CamelCaseModel):
    id: str
    name: str
    requires_gpu: bool
    loaded: bool


class LLMListResponse(CamelCaseModel):
    models: List[LLMInfo]
    active_model_id: Optional[str] = None
    has_gpu: bool = False


class LLMSelectRequest(CamelCaseModel):
    model_id: str


class LLMSelectResponse(CamelCaseModel):
    success: bool
    model_id: Optional[str] = None
