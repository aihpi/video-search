from enum import Enum
from typing import List, Optional

from app.models.camel_case import CamelCaseModel


class SearchType(str, Enum):
    KEYWORD = "keyword"
    SEMANTIC = "semantic"
    LLM = "llm"
    VISUAL = "visual"
    VISUAL_SEMANTIC = "visual_semantic"


class QueryResult(CamelCaseModel):
    segment_id: str
    start_time: float
    end_time: float
    text: str
    transcript_id: str
    relevance_score: float | None = None
    frame_timestamp: float | None = None
    frame_path: str | None = None
    search_type: SearchType | None = None


class QuestionRequest(CamelCaseModel):
    question: str
    transcript_id: str
    top_k: Optional[int] = 5
    search_type: Optional[SearchType] = SearchType.KEYWORD


class BaseSearchResponse(CamelCaseModel):
    question: str
    transcript_id: str
    results: List[QueryResult]
    search_type: SearchType


class KeywordSearchResponse(BaseSearchResponse):
    search_type: SearchType = SearchType.KEYWORD


class SemanticSearchResponse(BaseSearchResponse):
    search_type: SearchType = SearchType.SEMANTIC


class LLMSearchResponse(BaseSearchResponse):
    search_type: SearchType = SearchType.LLM
    summary: str
    not_addressed: bool
    model_id: str


class VisualSearchResponse(BaseSearchResponse):
    search_type: SearchType = SearchType.VISUAL


class VisualSemanticSearchResponse(BaseSearchResponse):
    search_type: SearchType = SearchType.VISUAL_SEMANTIC


QuestionResponse = (
    KeywordSearchResponse
    | SemanticSearchResponse
    | LLMSearchResponse
    | VisualSearchResponse
    | VisualSemanticSearchResponse
)
