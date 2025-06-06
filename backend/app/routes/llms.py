from fastapi import APIRouter, HTTPException, status

from app.models.llms import (
    LLMListResponse,
    LLMSelectRequest,
    LLMSelectResponse,
)
from app.services.llms import llm_service

llm_router = APIRouter()


@llm_router.get("", response_model=LLMListResponse)
async def list_llms():
    """Get list of available LLM models."""
    try:
        models = llm_service.get_available_models()
        active_model_id = llm_service.get_active_model_id()
        has_gpu = llm_service.has_gpu()

        return LLMListResponse(
            models=models, active_model_id=active_model_id, has_gpu=has_gpu
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list LLMs: {e}",
        )


@llm_router.post("/select", response_model=LLMSelectResponse)
async def select_llm(request: LLMSelectRequest):
    """Select and load a specific LLM model."""
    try:
        success = llm_service.select_model(request.model_id)

        if success:
            return LLMSelectResponse(success=True, model_id=request.model_id)
        else:
            return LLMSelectResponse(success=False, model_id=None)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to select LLM: {e}",
        )


@llm_router.get("/current")
async def get_current_llm():
    """Get the currently active LLM."""
    try:
        current_model_id = llm_service.get_active_model_id()
        if current_model_id:
            models = llm_service.get_available_models()
            current_model = next((m for m in models if m.id == current_model_id), None)
            return {"llm": current_model}
        else:
            return {"llm": None}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get current LLM: {e}",
        )
