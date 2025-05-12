from fastapi import APIRouter, BackgroundTasks, HTTPException, status
from fastapi.responses import FileResponse
from uuid import uuid4
from typing import Dict
import logging
import os
import asyncio

from app.models.transcription import TranscriptionRequest, TranscriptionResponse, TranscriptSegment
from app.services.transcription import process_video_sync, cleanup_file

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

cleanup_tasks: Dict[str, asyncio.Task] = {}
router = APIRouter()

TEMP_DIR = os.getenv("TMPDIR", "/tmp")

@router.post("/transcribe-video", response_model=TranscriptionResponse)
async def transcribe_video(request: TranscriptionRequest, background_tasks: BackgroundTasks):
    """
    Transcribe a video using Whisper.
    
    1. Downloads the video
    2. Extracts the audio
    3. Transcribes the audio
    4. Returns the transcription and audio URL
    """
    logger.info(f"Received request: {request}")

    id = str(uuid4())
    os.makedirs(TEMP_DIR, exist_ok=True)
    video_path = os.path.join(TEMP_DIR, f"{id}.mp4")
    audio_path = os.path.join(TEMP_DIR, f"{id}.mp3")   

    try:
        logger.info(f"Processing video from URL: {request.video_url}")

        result = await asyncio.get_event_loop().run_in_executor(
            None,
            process_video_sync,
            str(request.video_url),
            video_path,
            audio_path,
            request.model,
            request.language
        )

        # Create a background task to clean up the audio file after a delay of 1 hour
        cleanup_tasks[audio_path] = asyncio.create_task(cleanup_file(audio_path))

        response = TranscriptionResponse(
            id=id,
            audio_url=f"/audio/{id}.mp3",
            language=request.language,
            text=result["text"],
            segments=[
                TranscriptSegment(
                    id=i,
                    start=seg["start"],
                    end=seg["end"],
                    text=seg["text"]
                ) for i, seg in enumerate(result["segments"])
            ]
        )
        return response        
    except Exception as e:
        logger.error(f"Error processing video: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    
@router.get("/audio/{filename}")
async def get_audio(filename: str):
    """
    Serves an audio file.
    """
    audio_path = os.path.join(TEMP_DIR, filename)
    
    if not os.path.exists(audio_path):
        logger.warning(f"Audio file not found: {audio_path}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Audio file not found")
    
    logger.info(f"Serving audio file: {audio_path}")
    return FileResponse(audio_path)