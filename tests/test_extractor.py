"""Tests for extractor module."""

import pytest
from src.extractor import clean_and_normalize_topic, parse_llm_json_response


def test_parse_llm_json_response_with_markdown_fence():
    raw = """
    Some preliminary explanation.
    ```json
    [
      {
        "title": "إرادته",
        "level": "subtopic",
        "references": [
          {"surah_number": 2, "ayahs": [117, 185]}
        ]
      }
    ]
    ```
    Concluding notes.
    """
    parsed = parse_llm_json_response(raw)
    assert len(parsed) == 1
    assert parsed[0]["title"] == "إرادته"
    assert parsed[0]["references"][0]["surah_number"] == 2


def test_parse_llm_json_response_raw_array():
    raw = '[{"title": "التوحيد", "level": "section", "references": []}]'
    parsed = parse_llm_json_response(raw)
    assert len(parsed) == 1
    assert parsed[0]["title"] == "التوحيد"


def test_clean_and_normalize_topic():
    raw_item = {
        "title": "  إرادته  ",
        "level": "subtopic",
        "references": [
            {"surah_number": "2", "ayahs": [117, "185", [26, 28], "40-45"]},
            {"surah_number": 0, "ayahs": [1]},  # should be ignored
        ],
    }
    item = clean_and_normalize_topic(raw_item, page_number=2, column="right")
    assert item.title == "إرادته"
    assert item.page_number == 2
    assert item.column == "right"
    assert len(item.references) == 1
    ref = item.references[0]
    assert ref.surah_number == 2
    assert ref.ayahs == [117, 185, (26, 28), (40, 45)]
