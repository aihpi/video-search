import logging
from typing import Dict
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn

from app.routes.transcription import transcription_router, executor
from app.routes.search import search_router
from app.routes.llms import llm_router
from app.services.transcription import get_model, model_cache

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Load default model into memory on startup and unload it on shutdown.
    """
    logger.info("Loading default model...")
    try:
        get_model()
    except Exception as e:
        logger.error(f"Error loading model: {e}")
        raise RuntimeError(f"Model loading failed: {e}")

    yield

    # Cleanup
    logger.info("Shutting down thread pool executor...")
    executor.shutdown(wait=True)

    logger.info("Unloading models...")
    model_cache.clear()

    logger.info("Shutting down...")


app = FastAPI(title="Video search and transcription API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(transcription_router, prefix="/transcribe")
app.include_router(search_router, prefix="/search")
app.include_router(llm_router, prefix="/llms")

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=9091, reload=True)
