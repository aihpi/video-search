import logging

from app.services.search import search_service
from app.services.llms import llm_service


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


def summarize_transcript_by_id(transcript_id: str) -> str:
    try:
        logger.info(f"Generating summary for transcript ID: {transcript_id}")

        # Get the full transcript text from search service
        transcript_text = search_service.get_transcript_text_by_id(transcript_id)

        if not transcript_text:
            logger.warning(f"No transcript found for ID: {transcript_id}")
            return None

        summary = llm_service.generate_summary(transcript_text)

        logger.info(
            f"Successfully generated summary for transcript ID: {transcript_id}"
        )

        return summary

    except Exception as e:
        logger.error(f"Failed to generate transcript summary: {e}")
        raise
