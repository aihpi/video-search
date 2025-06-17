from pydantic import BaseModel
from typing import List, Optional

from app.models.camel_case import CamelCaseModel


# Schema for structured output for LLM answers
class LlmAnswer(BaseModel):
    summary: str
    not_addressed: bool
    model_id: str


# API Models for model management
class LlmInfo(CamelCaseModel):
    model_id: str
    display_name: str
    hf_model_id: str
    requires_gpu: bool
    loaded: bool


CurrentLlmInfoResponse = LlmInfo | None


class LlmListResponse(CamelCaseModel):
    models: List[LlmInfo]
    active_model_id: Optional[str] = None
    has_gpu: bool = False


class LlmSelectRequest(CamelCaseModel):
    model_id: str


class LlmSelectResponse(CamelCaseModel):
    success: bool
    model_id: Optional[str] = None
