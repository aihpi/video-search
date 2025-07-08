from typing import Optional
from enum import Enum

from app.models.camel_case import CamelCaseModel


class SummarizationRequest(CamelCaseModel):
    transcript_id: str


class SummarizationResponse(CamelCaseModel):
    summary: str
