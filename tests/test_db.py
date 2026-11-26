"""Tests for the SQLite database build, schema constraints, and query functions."""

import os
import sqlite3
import pytest
from src.db import (
    DEFAULT_DB_PATH,
    get_connection,
    search_topics,
    get_topic_by_id,
    get_topics_by_ayah,
    get_database_stats
)


def test_db_file_exists():
    assert os.path.exists(DEFAULT_DB_PATH), "Database file data/quran_topics.db must exist."
    assert os.path.getsize(DEFAULT_DB_PATH) > 1024 * 1024, "Database file must be at least 1MB."


def test_db_integrity_and_foreign_keys():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("PRAGMA integrity_check;")
    assert cursor.fetchone()[0] == "ok", "Database integrity check must return 'ok'."

    cursor.execute("PRAGMA foreign_key_check;")
    assert cursor.fetchall() == [], "Database must have zero foreign key violations."

    conn.close()


def test_db_row_counts():
    stats = get_database_stats()
    assert stats["surahs"] == 114, "Must contain all 114 Surahs."
    assert stats["ayahs"] == 6236, "Must contain all 6236 Ayahs (Hafs 'an 'Asim)."
    assert stats["topics"] == 1292, "Must contain all 1292 extracted topics."
    assert stats["topic_references"] == 7918, "Must contain 7918 Surah reference groups."
    assert stats["reference_ayahs"] == 12696, "Must contain 12696 Ayah citation entries."


def test_search_topics_ranking():
    # Search for "محمد"
    results = search_topics("محمد", limit=30)
    assert len(results) > 0, "Search for 'محمد' must return topics."

    # Direct or section matches should be prioritized
    titles = [r["title"] for r in results]
    assert any("محمد" in t for t in titles), "At least one title should directly contain 'محمد'."
    sections = [r["parent_section"] for r in results if r["parent_section"]]
    assert any("محمد" in s for s in sections), "Parent sections should include Prophet Muhammad ﷺ."


def test_get_topic_by_id_with_ayah_texts():
    conn = get_connection()
    cursor = conn.cursor()
    # Find a topic with references
    cursor.execute("SELECT id FROM topics WHERE id IN (SELECT topic_id FROM topic_references) LIMIT 1;")
    topic_id = cursor.fetchone()[0]
    conn.close()

    topic = get_topic_by_id(topic_id)
    assert topic is not None
    assert "references" in topic
    assert len(topic["references"]) > 0

    first_ref = topic["references"][0]
    assert "surah_number" in first_ref
    assert "surah_name_ar" in first_ref
    assert len(first_ref["ayahs"]) > 0

    first_ayah_entry = first_ref["ayahs"][0]
    assert "texts" in first_ayah_entry
    assert len(first_ayah_entry["texts"]) > 0
    assert "text_rasmUthmani" in first_ayah_entry["texts"][0]
    assert len(first_ayah_entry["texts"][0]["text_rasmUthmani"]) > 0


def test_get_topics_by_ayah():
    # Surah 1, Ayah 1 (Fatihah 1)
    topics_1_1 = get_topics_by_ayah(1, 1)
    assert isinstance(topics_1_1, list)

    # Surah 2, Ayah 255 (Al-Kursi)
    topics_kursi = get_topics_by_ayah(2, 255)
    assert len(topics_kursi) > 0, "Al-Kursi (2:255) must be referenced in topics."

    # Verify that range matching works (e.g. 255 between from_ayah and to_ayah)
    for t in topics_kursi:
        assert t["from_ayah"] <= 255 <= t["to_ayah"]
