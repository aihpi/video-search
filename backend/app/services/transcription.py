import os
import logging
import subprocess
import asyncio
import whisper
from typing import Dict

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

model_cache: Dict[str, whisper.Whisper] = {}
DEFAULT_MODEL = "small"


def get_model(model_name: str = DEFAULT_MODEL) -> whisper.Whisper:
    try:
        if model_name not in model_cache:
            logger.info(
                f"Model not found in cache. Loading Whisper {model_name} model."
            )
            model_cache[model_name] = whisper.load_model(model_name)
        return model_cache[model_name]
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
            capture_output=True,
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
        # Work around YouTube's recent API restrictions by downloading video+audio separately and merging
        # Format: best video (≤720p) + best audio, fallback to best ≤720p, final fallback to any best
        result = subprocess.run(
            [
                "yt-dlp",
                "-f",
                "bestvideo[height<=720]+bestaudio/best[height<=720]/best",
                "-o",
                output_path,
                video_url,
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        logger.info(f"yt-dlp completed. Output path: {output_path}")

        # Check if file exists at expected location
        if not os.path.exists(output_path):
            # yt-dlp might have added an extension, let's check
            output_dir = os.path.dirname(output_path)
            output_basename = os.path.basename(output_path).split(".")[0]

            # List all files in the temp directory that match our basename
            matching_files = [
                f for f in os.listdir(output_dir) if f.startswith(output_basename)
            ]

            if matching_files:
                actual_file = os.path.join(output_dir, matching_files[0])
                logger.info(f"Found downloaded file at: {actual_file}")
                # Rename to our expected location
                os.rename(actual_file, output_path)
                logger.info(f"Renamed to expected location: {output_path}")
            else:
                logger.error(
                    f"No files found matching pattern {output_basename}* in {output_dir}"
                )
                logger.error(f"Directory contents: {os.listdir(output_dir)}")
                raise RuntimeError(f"Video file not created at expected location")

        logger.info(f"Video downloaded successfully: {output_path}")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"yt-dlp command failed with exit code {e.returncode}")
        logger.error(f"yt-dlp stderr: {e.stderr}")
        logger.error(f"yt-dlp stdout: {e.stdout}")
        raise RuntimeError(f"Failed to download video from {video_url}")
    except Exception as e:
        logger.error(f"Unexpected error downloading video: {type(e).__name__}: {e}")
        raise RuntimeError(f"Failed to download video from {video_url}")


def _process_audio_and_transcribe(
    video_path: str, audio_path: str, model_name: str, language: str
) -> Dict:
    """
    Shared logic for audio extraction and transcription.
    """
    is_audio_extracted = extract_audio(video_path, audio_path)

    if not is_audio_extracted:
        logger.error(f"Failed to extract audio from {video_path}")
        raise RuntimeError(f"Failed to extract audio from {video_path}")
    logger.info(f"Audio extracted successfully: {audio_path}")

    transcription_result = transcribe_audio(audio_path, model_name, language)
    logger.info(f"Transcribed video successfully.")

    return transcription_result


def process_video_from_url(
    video_url: str, video_path: str, audio_path: str, model_name: str, language: str
) -> Dict:
    """
    Process a video from URL by downloading, extracting audio, and transcribing.
    """
    try:
        is_video_downloaded = download_video(video_url, video_path)

        if not is_video_downloaded:
            logger.error(f"Failed to download video from {video_url}")
            raise RuntimeError(f"Failed to download video from {video_url}")

        logger.info(f"Video downloaded successfully: {video_path}")

        return _process_audio_and_transcribe(video_path, audio_path, model_name, language)

    except Exception as e:
        logger.error(f"Error processing video from URL: {e}")
        raise e


def process_video_from_file(
    video_path: str, audio_path: str, model_name: str, language: str
) -> Dict:
    """
    Process a local video file by extracting audio and transcribing.
    """
    try:
        logger.info(f"Processing local video file: {video_path}")

        return _process_audio_and_transcribe(video_path, audio_path, model_name, language)

    except Exception as e:
        logger.error(f"Error processing local video: {e}")
        raise e


async def cleanup_file(file_path: str, delay: int = 3600) -> None:
    """
    Asynchronously delete a file after a delay.

    Note: When used with FastAPI's BackgroundTasks, this function will be
    executed in a separate task, even though it's async.
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
        # Don't raise the exception in a background task as it would be unhandled
        # Just log it instead
