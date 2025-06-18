from fastapi import APIRouter, HTTPException, status

from app.models.search import (
    QuestionRequest,
    QuestionResponse,
)
from app.services.search import search_service

search_router = APIRouter()


@search_router.post("/query", response_model=QuestionResponse)
async def query_transcript(request: QuestionRequest):
    """
    Query the transcript for relevant segments using the specified search type.

    Args:
        question: The question or search query
        transcript_id: Optional transcript ID to restrict the search
        top_k: Maximum number of results to return
        search_type: The type of search to perform (keyword, semantic, llm)
    """
    try:
        # The service returns different response types based on search_type
        response = search_service.query_transcript(
            question=request.question,
            transcript_id=request.transcript_id,
            top_k=request.top_k,
            search_type=request.search_type,
        )
        return response
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal Server Error: {e}",
        )
