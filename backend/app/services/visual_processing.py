import cv2
import logging
import shutil
import torch

from pathlib import Path
from PIL import Image
from typing import Any, Dict, List

from transformers import AutoModel, AutoProcessor
from app.models.transcription import TranscriptSegment

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


class VisualProcessingService:
    """
    Service for extracting frames from videos and generating visual embeddings.
    Uses SigLIP for visual embeddings that can be compared with text queries.
    """

    def __init__(self):
        self._model = None
        self._processor = None
        self._device = None
        self._frame_output_dir = Path("data/frames")
        self._frame_output_dir.mkdir(parents=True, exist_ok=True)

        # Load model on initialization
        self._load_model()

    def _load_model(self):
        """
        Load SigLIP model for visual embeddings.
        """

        if self._model is None:
            logger.info("Loading SigLIP model for visual embeddings...")
            if torch.cuda.is_available():
                self._device = "cuda"
            elif torch.backends.mps.is_available() and torch.backends.mps.is_built():
                self._device = "mps"
            else:
                self._device = "cpu"

            model_name = "google/siglip2-base-patch16-384"
            self._processor = AutoProcessor.from_pretrained(model_name)
            self._model = AutoModel.from_pretrained(model_name).to(self._device)
            self._model.eval()

            logger.info(f"SigLIP2 model loaded successfully on {self._device}.")

    def extract_frames_for_segments(
        self,
        video_path: str,
        segments: List[TranscriptSegment],
        frames_per_second: float = 0.5,  # Default: extract 1 frame every 2 seconds
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Extract frames from video for given transcript segments."""
        
        logger.info(f"Starting frame extraction from video: {video_path}")
        logger.info(f"Number of segments to process: {len(segments)}")
        
        # Check if video file exists
        if not os.path.exists(video_path):
            logger.error(f"Video file not found: {video_path}")
            return {}

        cap = cv2.VideoCapture(video_path)
        
        # Check if video opened successfully
        if not cap.isOpened():
            logger.error(f"Failed to open video: {video_path}")
            return {}
        
        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        logger.info(f"Video FPS: {fps}, Total frames: {total_frames}")

        video_id = Path(video_path).stem
        video_frame_dir = self._frame_output_dir / video_id
        video_frame_dir.mkdir(exist_ok=True, parents=True)
        logger.info(f"Frame output directory: {video_frame_dir}")

        frames_by_segment = {}
        total_frames_extracted = 0
        try:

            for segment in segments:
                segment_frames = []

                # Calculate frame extraction times within this segment
                start_time = segment.start
                end_time = segment.end
                interval = 1.0 / frames_per_second

                # Extract frames at regular intervals within the segment
                current_time = start_time
                while current_time <= end_time:
                    # Seek to the specific timestamp in the video
                    frame_number = int(current_time * fps)
                    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)

                    ret, frame = cap.read()
                    if ret:
                        # Save the frame to disk
                        frame_filename = f"frame_{current_time:.2f}.jpg"
                        frame_path = video_frame_dir / frame_filename
                        success = cv2.imwrite(str(frame_path), frame)
                        
                        if success:
                            segment_frames.append(
                                {
                                    "timestamp": current_time,
                                    "path": str(frame_path),
                                    "segment_id": segment.id,
                                }
                            )
                            total_frames_extracted += 1
                        else:
                            logger.error(f"Failed to save frame at {current_time:.2f}s to {frame_path}")
                    else:
                        logger.warning(f"Failed to read frame at {current_time:.2f}s (frame {frame_number})")

                    current_time += interval

                # Also extract frame at segment end if not already included
                if (
                    len(segment_frames) == 0
                    or segment_frames[-1]["timestamp"] < end_time
                ):
                    frame_number = int(end_time * fps)
                    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
                    ret, frame = cap.read()
                    if ret:
                        frame_filename = f"frame_{end_time:.2f}.jpg"
                        frame_path = video_frame_dir / frame_filename
                        cv2.imwrite(str(frame_path), frame)
                        segment_frames.append(
                            {
                                "timestamp": end_time,
                                "path": str(frame_path),
                                "segment_id": segment.id,
                            }
                        )

                frames_by_segment[segment.id] = segment_frames
                logger.info(
                    f"Extracted {len(segment_frames)} frames for segment {segment.id} ({segment.start:.2f}s to {segment.end:.2f}s)"
                )

        finally:
            cap.release()
            logger.info(f"Frame extraction complete. Total frames extracted: {total_frames_extracted}")
            logger.info(f"Segments with frames: {len(frames_by_segment)}")

        return frames_by_segment

    def generate_frame_embeddings(self, frame_paths: List[str]) -> List[List[float]]:
        """Generate SigLIP embeddings for a list of frame images."""

        self._load_model()

        embeddings = []

        # Process frames in batches for efficiency
        batch_size = 8
        for i in range(0, len(frame_paths), batch_size):
            batch_paths = frame_paths[i : i + batch_size]

            images = []
            for path in batch_paths:
                image = Image.open(path).convert("RGB")
                images.append(image)

            with torch.no_grad():
                inputs = self._processor(images=images, return_tensors="pt").to(
                    self._device
                )
                outputs = self._model.get_image_features(**inputs)

                # Normalize embeddings
                batch_embeddings = outputs / outputs.norm(dim=-1, keepdim=True)
                embeddings.extend(batch_embeddings.cpu().numpy().tolist())

        return embeddings

    def generate_text_embedding(self, text: str) -> List[float]:
        """Generate SigLIP2 embedding for a text query.
        This allows search over images using text queries.
        """
        self._load_model()

        with torch.no_grad():
            # SigLIP2 uses specific formatting and parameters
            # Convert to lowercase as recommended
            text_lower = text.lower()
            # Use prompt template for better results
            formatted_text = f"This is a photo of {text_lower}."
            
            # SigLIP2 requires padding="max_length" with max_length=64
            inputs = self._processor(
                text=formatted_text, 
                padding="max_length", 
                max_length=64,
                return_tensors="pt"
            ).to(self._device)
            outputs = self._model.get_text_features(**inputs)

            # Normalize embedding
            text_embedding = outputs / outputs.norm(dim=-1, keepdim=True)

        return text_embedding[0].cpu().numpy().tolist()

    def cleanup_frames(self, video_id: str):
        """Cleanup extracted frames for a specific video."""
        video_frame_dir = self._frame_output_dir / video_id
        if video_frame_dir.exists():
            shutil.rmtree(video_frame_dir)
            logger.info(f"Cleaned up frames for video {video_id}.")


visual_processing_service = VisualProcessingService()
