import os
import re
import logging
from openai import OpenAI
from dotenv import load_dotenv

from app.services.search import search_service

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

load_dotenv()

# LLM Backend configuration
LLM_BACKEND = os.getenv("LLM_BACKEND", "ollama").lower()

if LLM_BACKEND == "ollama":
    BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")
    API_KEY = "ollama"  # Ollama doesn't require API key
elif LLM_BACKEND == "vllm":
    BASE_URL = os.getenv("VLLM_BASE_URL", "http://localhost:8000/v1")
    API_KEY = os.getenv("VLLM_API_KEY", "vllm")
else:
    raise ValueError(f"Unsupported LLM backend: {LLM_BACKEND}")

MODEL_NAME = os.getenv("SUMMARIZATION_MODEL", "qwen3:8b")

# Initialize OpenAI client
client = OpenAI(
    base_url=BASE_URL,
    api_key=API_KEY,
)


def create_prompt(transcript_text: str, max_length: int = None) -> str:
    """Create a prompt for video summarization."""
    length_instruction = ""
    if max_length:
        length_instruction = (
            f"\nThe summary should be approximately {max_length} words long."
        )

    return f"""You are an expert at summarizing video transcripts. Your task is to create a clear, comprehensive summary that captures the main points, key insights, and important details from the video.

Please analyze the following video transcript and provide a well-structured summary that:
1. Identifies the main topic or theme
2. Highlights key points and important information
3. Captures any conclusions or takeaways
4. Maintains the original context and meaning
5. Is written in a clear, concise manner{length_instruction}

IMPORTANT OUTPUT REQUIREMENTS:
- Write in plain text without any markdown formatting (no **, *, #, etc.)
- Do NOT include "Summary:" or "SUMMARY:" at the beginning
- Do NOT use bullet points or numbered lists
- Write in paragraph form with clear transitions between ideas
- Start directly with the content (e.g., "This video discusses...")
- Output ONLY the final summary text, nothing else

TRANSCRIPT:
{transcript_text}"""


def summarize_transcript_by_id(transcript_id: str, max_length: int = None) -> str:
    """Generate a summary for a video transcript."""
    try:
        logger.info(f"Generating summary for transcript ID: {transcript_id}")

        # Get the full transcript text from search service
        transcript_text = search_service.get_transcript_text_by_id(transcript_id)

        if not transcript_text:
            logger.warning(f"No transcript found for ID: {transcript_id}")
            return None

        prompt = create_prompt(transcript_text, max_length)

        summary = call_llm(prompt)

        logger.info(
            f"Successfully generated summary for transcript ID: {transcript_id}"
        )

        return summary

    except Exception as e:
        logger.error(f"Failed to generate transcript summary: {e}")
        raise


def call_llm(prompt: str) -> str:
    """Call LLM API using OpenAI client for text generation."""
    try:
        # Use chat completion API
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant that creates clear, concise summaries of video transcripts. Output only the requested summary content.",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.3,  # Slightly higher for more natural summaries
            top_p=0.9,
            max_tokens=1024,  # Reasonable limit for summaries
        )

        # Extract and return the generated text
        summary = response.choices[0].message.content.strip()

        # Clean up any thinking tags or meta-commentary
        if "<think>" in summary:
            # Remove everything between <think> and </think>
            summary = re.sub(
                r"<think>.*?</think>", "", summary, flags=re.DOTALL
            ).strip()

        # Remove any leading/trailing whitespace or empty lines
        summary = summary.strip()

        return summary

    except Exception as e:
        logger.error(f"Failed to call LLM: {e}")
        raise
