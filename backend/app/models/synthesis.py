from pydantic import BaseModel, Field
from typing import List


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
