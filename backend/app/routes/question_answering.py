from fastapi import APIRouter, HTTPException, status

from app.models.question_answering import (
    QuestionRequest,
    QuestionResponse,
)
from app.services.question_answering import question_answering_service

question_answering_router = APIRouter()


@question_answering_router.post("/question", response_model=QuestionResponse)
async def query_transcript(request: QuestionRequest):
    """
    Query the vector database with a question to find relevant transcript segments.
    """
    try:
        results = question_answering_service.query_transcript(
            question=request.question,
            transcript_id=request.transcript_id,
            top_k=request.top_k,
        )
        response = QuestionResponse(
            question=request.question,
            transcript_id=request.transcript_id,
            results=results,
        )
        return response
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal Server Error: {e}",
        )
