from typing import Optional
from enum import Enum

from app.models.camel_case import CamelCaseModel


class SummarizationRequest(CamelCaseModel):
    transcript_id: str
    max_length: Optional[int] = None  # Approximate word count for summary


class SummarizationResponse(CamelCaseModel):
    summary: str
