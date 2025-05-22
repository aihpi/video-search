from enum import Enum
from typing import List, Optional

from app.models.camel_case import CamelCaseModel


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


class QuestionResponse(CamelCaseModel):
    question: str
    transcript_id: str
    results: List[QueryResult]
    search_type: str


class QuestionRequest(CamelCaseModel):
    question: str
    transcript_id: str
    top_k: Optional[int] = 5
    search_type: Optional[SearchType] = SearchType.KEYWORD
