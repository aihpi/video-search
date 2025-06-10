from enum import Enum
from typing import List, Optional

from app.models.camel_case import CamelCaseModel
from app.models.llms import AnswerPoint


class SearchType(str, Enum):
    KEYWORD = "keyword"
    SEMANTIC = "semantic"
    LLM = "llm"
    MULTIMODAL = "multimodal"


class QueryResult(CamelCaseModel):
    segment_id: str
    start_time: float
    end_time: float
    text: str
    transcript_id: str
    relevance_score: float | None = None


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
    points: List[AnswerPoint]
    not_addressed: bool
    model_id: str


QuestionResponse = KeywordSearchResponse | SemanticSearchResponse | LLMSearchResponse
