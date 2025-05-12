import os
import logging
import subprocess
import asyncio
import whisper
from typing import Dict

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

MODEL_CACHE: Dict[str, whisper.Whisper] = {}

def get_model(model_name: str) -> str:
    try:
        if model_name not in MODEL_CACHE:
            logger.info(f"Model not found in cache. Loading Whisper {model_name} model.")
            MODEL_CACHE[model_name] = whisper.load_model(model_name)
        return MODEL_CACHE[model_name]
    except Exception as e:
        logger.error(f"Error loading model: {e}")
        raise RuntimeError(f"Model loading failed: {e}")

def transcribe_audio(audio_path: str, model_name: str, language: str) -> dict:
    try:
        logger.info(f"Transcribing audio using model {model_name}...")

        model = get_model(model_name)
        result = model.transcribe(audio_path, language=language)
        logger.info("Transcription completed successfully.")
        return result
    except Exception as e:
        logger.error(f"Error during transcription: {e}")
        raise RuntimeError(f"Transcription failed: {e}")


def extract_audio(video_path: str, audio_path: str) -> bool:
    """Extracts audio from a video using ffmpeg."""
    try:
        logger.info(f"Extracting audio from {video_path}...")
        subprocess.run(
            ["ffmpeg", "-i", video_path, "-q:a", "0", "-map", "a", audio_path],
            check=True,
            capture_output=True
        )
        return os.path.exists(audio_path)
    except subprocess.CalledProcessError as e:
        logger.error(f"Error extracting audio: {e.stderr.decode('utf-8')}")
        raise RuntimeError(f"Failed to extract audio: {e}")
    
def download_video(video_url: str, output_path: str) -> None:
    """
    Downloads the video from the given URL using yt-dlp and saves it to the specified path.
    """
    try:
        logger.info(f"Downloading video from URL: {video_url}")
        subprocess.run(
            ["yt-dlp", "-f", "best", "-o", output_path, video_url],
            check=True,
            capture_output=True,
        )
        return os.path.exists(output_path)
    except subprocess.CalledProcessError as e:
        logger.error(f"Error downloading video: {e}")
        raise RuntimeError(f"Failed to download video: {e}")
    

def process_video_sync(video_url: str, video_path: str, audio_path:str, model_name: str, language: str) -> Dict:
    """
    Synchronous function for processing a video to be run in the thread pool.
    """

    try:
        is_video_downloaded = download_video(video_url, video_path)

        if not is_video_downloaded:
            logger.error(f"Failed to download video from {video_url}")
            raise RuntimeError(f"Failed to download video from {video_url}")
        
        logger.info(f"Video downloaded successfully: {video_path}")

        is_audio_extracted = extract_audio(video_path, audio_path)

        if not is_audio_extracted:
            logger.error(f"Failed to extract audio from {video_path}")
            raise RuntimeError(f"Failed to extract audio from {video_path}")
        logger.info(f"Audio extracted successfully: {audio_path}")

        transcription_result = transcribe_audio(audio_path, model_name, language)

        logger.info(f"Transcribed video successfully.")

        return transcription_result
    
    except Exception as e:
        logger.error(f"Error processing video {id}: {e}")
        raise e
    

async def cleanup_file(file_path: str, delay: int = 3600) -> None:
    """
    Asynchronously delete a file after a delay.
    """
    try:
        await asyncio.sleep(delay)
        if os.path.exists(file_path):
            os.remove(file_path)
            logger.info(f"Deleted file: {file_path}")
        else:
            logger.warning(f"File not found for deletion: {file_path}")
    except Exception as e:
        logger.error(f"Error deleting file: {e}")
        raise e