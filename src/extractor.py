"""Extractor module using Ollama models and Quranic validation rules."""

import base64
import json
import io
import re
from typing import Any, Dict, List, Optional
import requests
from PIL import Image

from src.validator import TopicItem, TopicReference, validate_topic_item
from src.quran_metadata import TOTAL_SURAHS, get_surah_total_ayahs

OLLAMA_URL = "http://localhost:11434/api/generate"
DEFAULT_MODEL = "deepseek-v4.1-flash:cloud"


def image_to_base64(image: Image.Image) -> str:
    """Converts PIL Image to base64 JPEG string."""
    buf = io.BytesIO()
    image.save(buf, format="JPEG", quality=90)
    return base64.b64encode(buf.getvalue()).decode("utf-8")


def build_extraction_prompt() -> str:
    return """You are an expert Arabic Quranic index analyzer.
Extract the topics and Quran references from this index page snippet.

CRITICAL READING RULES:
1. The text is in Arabic (read right to left, top to bottom).
2. RED NUMBERS are SURAH numbers (1 to 114). Within a topic, Surahs appear in ascending order (e.g. 2, 4, 5, 6...).
3. BLACK NUMBERS are AYAH numbers. They follow their respective red Surah number.
   - Can be individual ayahs: e.g. 117, 185
   - Can be ranges: e.g. 26 - 28 (represent as [26, 28])
   - Note: If a line ends with a red Surah number (e.g. 5) and the next line begins with black numbers (e.g. 6 و 18 و 52), those black numbers belong to Surah 5!
4. Hierarchical Levels:
   - "major_topic": top category banner (e.g. أركان الإسلام)
   - "section": sub-banner / roman numeral section (e.g. أولاً : التوحيد)
   - "topic": numbered main subject (e.g. (١)- توحيد الله تعالى)
   - "subtopic": specific topic with references (e.g. إرادته)

Return ONLY valid JSON array with schema:
[
  {
    "title": "topic title in Arabic",
    "level": "major_topic" | "section" | "topic" | "subtopic",
    "references": [
      {
        "surah_number": <int 1..114>,
        "ayahs": [<int or [start, end]> ...]
      }
    ]
  }
]
"""


def call_ollama_vision(
    image: Image.Image,
    model: str = DEFAULT_MODEL,
    timeout: int = 120,
) -> str:
    """Calls Ollama API with an image and returns response string."""
    b64_img = image_to_base64(image)
    payload = {
        "model": model,
        "prompt": build_extraction_prompt(),
        "images": [b64_img],
        "stream": True,
        "options": {
            "temperature": 0.1,
        },
    }

    resp = requests.post(OLLAMA_URL, json=payload, stream=True, timeout=timeout)
    resp.raise_for_status()

    full_response = ""
    for line in resp.iter_lines():
        if line:
            chunk = json.loads(line)
            full_response += chunk.get("response", "")
            if chunk.get("done"):
                break

    return full_response


def parse_llm_json_response(raw_text: str) -> List[Dict[str, Any]]:
    """Extracts and parses JSON array from model output."""
    # Try finding JSON block between ```json ... ``` or [ ... ]
    match = re.search(r"\[\s*\{.*\}\s*\]", raw_text, re.DOTALL)
    if match:
        json_str = match.group(0)
    else:
        # Fallback to search from first [ to last ]
        start = raw_text.find("[")
        end = raw_text.rfind("]")
        if start != -1 and end != -1 and end > start:
            json_str = raw_text[start : end + 1]
        else:
            raise ValueError(f"No JSON array found in response: {raw_text[:200]}")

    return json.loads(json_str)


def clean_and_normalize_topic(
    raw_item: Dict[str, Any],
    page_number: Optional[int] = None,
    column: Optional[str] = None,
) -> TopicItem:
    """Normalizes raw LLM output into a validated TopicItem."""
    title = str(raw_item.get("title", "")).strip()
    level = str(raw_item.get("level", "subtopic")).strip()

    normalized_refs: List[TopicReference] = []
    for ref_dict in raw_item.get("references", []):
        try:
            surah_number = int(ref_dict.get("surah_number", 0))
        except (ValueError, TypeError):
            continue

        raw_ayahs = ref_dict.get("ayahs", [])
        cleaned_ayahs = []
        for a in raw_ayahs:
            if isinstance(a, int):
                cleaned_ayahs.append(a)
            elif isinstance(a, list) and len(a) == 2:
                try:
                    s_a, e_a = int(a[0]), int(a[1])
                    cleaned_ayahs.append((s_a, e_a))
                except (ValueError, TypeError):
                    continue
            elif isinstance(a, str):
                # Check for range string like "26-28"
                if "-" in a:
                    parts = a.split("-")
                    try:
                        cleaned_ayahs.append((int(parts[0].strip()), int(parts[1].strip())))
                    except ValueError:
                        pass
                else:
                    try:
                        cleaned_ayahs.append(int(a.strip()))
                    except ValueError:
                        pass

        if surah_number > 0 and cleaned_ayahs:
            normalized_refs.append(TopicReference(surah_number=surah_number, ayahs=cleaned_ayahs))

    return TopicItem(
        title=title,
        level=level,
        references=normalized_refs,
        page_number=page_number,
        column=column,
    )
