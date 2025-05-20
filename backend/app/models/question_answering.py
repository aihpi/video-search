from typing import List, Optional

from app.models.camel_case import CamelCaseModel


class QueryResult(CamelCaseModel):
    segment_id: str
    start_time: float
    end_time: float
    text: str
    transcript_id: str


class QuestionResponse(CamelCaseModel):
    question: str
    transcript_id: str
    results: List[QueryResult]


class QuestionRequest(CamelCaseModel):
    question: str
    transcript_id: str
    top_k: Optional[int] = 5
