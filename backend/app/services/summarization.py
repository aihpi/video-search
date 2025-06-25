import os
import logging
import json
from fastapi import requests
from dotenv import load_dotenv
from typing import List, Dict, Any

from app.services.search import search_service
from app.models.summarization import (
    SUMMARY_TEMPLATE,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

load_dotenv()
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
MODEL_NAME = os.getenv("SUMMARIZATION_MODEL", "qwen3:8b")


def create_prompt(transcript_text: str, template: Dict[str, Any]) -> str:
    """Create a structured prompt for Ollama."""
    return f"""Du bist ein Experte für die Erstellung von Sitzungsniederschriften nach brandenburgischer Kommunalverfassung.

DEINE AUFGABE:
Analysiere das folgende Transkript einer Gemeinderatssitzung und erstelle eine strukturierte Niederschrift im JSON-Format.

WICHTIGE REGELN:
1. Extrahiere ALLE Informationen gemäß der vorgegebenen JSON-Struktur
2. Anträge und Beschlüsse müssen VOLLSTÄNDIG und WÖRTLICH übernommen werden
3. Fülle alle Felder aus - wenn Information fehlt, nutze "nicht erfasst" oder "keine"
4. Achte auf korrekte Rechtschreibung und formale Sprache
5. Das Ergebnis MUSS valides JSON sein

JSON-VORLAGE:
{json.dumps(template, ensure_ascii=False, indent=2)}

TRANSKRIPT:
{transcript_text}

AUSGABE:
Gib NUR das ausgefüllte JSON zurück, ohne zusätzlichen Text."""


def summarize_transcript_by_id(transcript_id: str):
    try:
        logger.info(f"Generating summary for transcript ID: {transcript_id}")

        # Get the full transcript text from search service
        transcript_text = search_service.get_transcript_text_by_id(transcript_id)

        if not transcript_text:
            logger.warning(f"No transcript found for ID: {transcript_id}")
            return None

        prompt = create_prompt(transcript_text, SUMMARY_TEMPLATE)

        summary_data = call_ollama(prompt)

        logger.info(
            f"Successfully generated summary for transcript ID: {transcript_id}"
        )

        return summary_data

    except Exception as e:
        logger.error(f"Failed to generate transcript summary: {e}")
        raise


def call_ollama(prompt: str) -> Dict[str, Any]:
    """Call Ollama API and parse JSON response."""
    try:
        response = requests.post(
            f"{OLLAMA_BASE_URL}/api/generate",
            json={
                "model": MODEL_NAME,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.1,  # Very low for consistent output
                    "top_p": 0.9,
                    "seed": 42,  # For reproducibility
                },
            },
            timeout=300,  # 5 minutes timeout for long transcripts
        )
        response.raise_for_status()

        # Extract the generated text
        result = response.json()
        generated_text = result.get("response", "")

        # Try to parse JSON from the response
        # Sometimes LLMs add markdown formatting, so we clean it
        generated_text = generated_text.strip()
        if generated_text.startswith("```json"):
            generated_text = generated_text[7:]
        if generated_text.endswith("```"):
            generated_text = generated_text[:-3]

        # Parse JSON
        niederschrift_data = json.loads(generated_text.strip())
        return niederschrift_data

    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse JSON from Ollama response: {e}")
        logger.error(f"Response text: {generated_text[:500]}...")
        raise ValueError("Model did not return valid JSON")
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to call Ollama: {e}")
        raise


def validate_summary(summary_data: Dict[str, Any]) -> List[str]:
    """Basic validation of the generated Niederschrift."""
    issues = []

    required_fields = [
        "organisation",
        "sitzungsart",
        "datum",
        "ort",
        "vorsitz",
        "protokollfuehrung",
        "anwesende",
        "tagesordnung",
    ]

    for field in required_fields:
        if field not in summary_data or not summary_data[field]:
            issues.append(f"Fehlendes Pflichtfeld: {field}")

    # Check if agenda items have required content
    if "tagesordnung" in summary_data:
        for idx, top in enumerate(summary_data["tagesordnung"]):
            if not top.get("titel"):
                issues.append(f"TOP {idx+1}: Titel fehlt")
            if "oeffentlich" not in top:
                issues.append(f"TOP {idx+1}: Öffentlichkeitsstatus fehlt")

    return issues
