from fastapi import APIRouter, HTTPException, status
from fastapi.responses import FileResponse
import logging
import os

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

media_router = APIRouter()

TEMP_DIR = os.getenv("TMPDIR", "/tmp")


@media_router.get("/audio/{filename}")
async def get_audio(filename: str):
    """
    Serves an audio file.
    """
    audio_path = os.path.join(TEMP_DIR, filename)

    if not os.path.exists(audio_path):
        logger.warning(f"Audio file not found: {audio_path}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Audio file not found"
        )

    logger.info(f"Serving audio file: {audio_path}")
    return FileResponse(audio_path, media_type="audio/mpeg")


@media_router.get("/frames/{video_id}/{filename}")
async def get_frame(video_id: str, filename: str):
    """
    Serves a frame image file.
    """
    # Security check: ensure filename doesn't contain path traversal
    if ".." in filename or "/" in filename or "\\" in filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid filename"
        )
    
    # Frames are stored in data/frames/{video_id}/{filename}
    frame_path = os.path.join("data/frames", video_id, filename)

    if not os.path.exists(frame_path):
        logger.warning(f"Frame file not found: {frame_path}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Frame file not found"
        )

    logger.info(f"Serving frame file: {frame_path}")
    return FileResponse(
        frame_path, 
        media_type="image/jpeg",
        headers={"Cache-Control": "public, max-age=86400"}  # Cache for 1 day
    )