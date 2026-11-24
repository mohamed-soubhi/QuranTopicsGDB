"""Tests for formatter module."""

import json
from src.validator import TopicItem, TopicReference
from src.formatter import (
    format_references_markdown,
    generate_markdown,
    generate_marqoom_json,
)


def test_format_references_markdown():
    refs = [
        TopicReference(surah_number=2, ayahs=[117, 185, 253]),
        TopicReference(surah_number=4, ayahs=[(26, 28)]),
    ]
    formatted = format_references_markdown(refs)
    assert formatted == "2: 117, 185, 253 | 4: 26-28"


def test_generate_markdown():
    items = [
        TopicItem(title="أركان الإسلام", level="major_topic"),
        TopicItem(title="أولاً : التوحيد", level="section"),
        TopicItem(title="توحيد الله تعالى", level="topic"),
        TopicItem(
            title="إرادته",
            level="subtopic",
            references=[TopicReference(surah_number=2, ayahs=[117, 185])],
        ),
    ]
    md = generate_markdown(items)
    assert "## أركان الإسلام" in md
    assert "### أولاً : التوحيد" in md
    assert "#### توحيد الله تعالى" in md
    assert "* **إرادته:** 2: 117, 185" in md


def test_generate_marqoom_json():
    items = [
        TopicItem(
            title="إرادته",
            level="subtopic",
            page_number=2,
            column="right",
            references=[TopicReference(surah_number=2, ayahs=[117, (26, 28)])],
        )
    ]
    data = generate_marqoom_json(items)
    assert data["metadata"]["riwayah"] == "hafs_an_asim"
    assert data["metadata"]["total_surahs"] == 114
    assert data["metadata"]["total_ayahs"] == 6236
    assert len(data["topics"]) == 1
    assert data["topics"][0]["references"][0]["surah_number"] == 2
    assert data["topics"][0]["references"][0]["ayahs"] == [117, [26, 28]]
