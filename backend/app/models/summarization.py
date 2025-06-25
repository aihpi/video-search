from typing import Dict, Any
import json

from app.models.camel_case import CamelCaseModel


class SummarizationRequest(CamelCaseModel):
    transcript_id: str


class SummarizationResponse(CamelCaseModel):
    summary: str


# Niederschrift template
SUMMARY_TEMPLATE = {
    "organisation": "Gemeinde/Stadt Name",
    "sitzungsart": "Präsenzsitzung/Hybridsitzung/Videositzung/Audiositzung",
    "datum": "TT.MM.JJJJ",
    "uhrzeit_beginn": "HH:MM",
    "uhrzeit_ende": "HH:MM",
    "ort": "Sitzungsort",
    "vorsitz": "Name des/der Vorsitzenden",
    "protokollfuehrung": "Name des/der Protokollführer(in)",
    "anwesende": ["Vollständige Liste der anwesenden Mitglieder"],
    "entschuldigt": ["Liste der entschuldigt fehlenden Mitglieder"],
    "unentschuldigt": ["Liste der unentschuldigt fehlenden Mitglieder"],
    "gaeste": ["Liste der Gäste/Verwaltung"],
    "tagesordnung": [
        {
            "top_nummer": "1",
            "titel": "Titel des Tagesordnungspunkts",
            "oeffentlich": True,
            "antraege": ["VOLLSTÄNDIGER Wortlaut des Antrags"],
            "beschluesse": ["VOLLSTÄNDIGER Wortlaut des Beschlusses"],
            "abstimmung": {
                "ja_stimmen": 0,
                "nein_stimmen": 0,
                "enthaltungen": 0,
                "ergebnis": "angenommen/abgelehnt",
            },
        }
    ],
    "befangenheiten": [
        {"name": "Name des befangenen Mitglieds", "top_nummer": "Betroffener TOP"}
    ],
    "naechste_sitzung": "TT.MM.JJJJ oder 'noch nicht festgelegt'",
}


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
