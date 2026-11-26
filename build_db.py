"""Builds the SQLite Database (quran_topics.db) from the golden JSON files.

Includes:
- Surahs catalog (Arabic & English names, total ayahs)
- Topics with hierarchical context (major topic, section, subtopic)
- References & Ayah ranges with relational foreign keys
- Complete canonical Quranic text (6,236 Ayahs, Hafs 'an 'Asim)
- Full-Text Search (FTS5) virtual tables
- Relational views for analytical queries
"""

import json
import os
import sqlite3
import sys
from src.quran_metadata import SURAHS

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "quran_topics.db")
TOPICS_JSON = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "quran_topics.json")
QURAN_TEXT_JSON = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "quran_text_hafs.json")

SURAH_NAMES_EN = {
    1: "Fatihah", 2: "Baqarah", 3: "Ali Imran", 4: "Nisa", 5: "Maidah",
    6: "Anam", 7: "Araf", 8: "Anfal", 9: "Tawbah", 10: "Yunus",
    11: "Hud", 12: "Yusuf", 13: "Rad", 14: "Ibrahim", 15: "Hijr",
    16: "Nahl", 17: "Isra", 18: "Kahf", 19: "Maryam", 20: "Taha",
    21: "Anbiya", 22: "Hajj", 23: "Muminun", 24: "Nur", 25: "Furqan",
    26: "Shuara", 27: "Naml", 28: "Qasas", 29: "Ankabut", 30: "Rum",
    31: "Luqman", 32: "Sajdah", 33: "Ahzab", 34: "Saba", 35: "Fatir",
    36: "Yasin", 37: "Saffat", 38: "Sad", 39: "Zumar", 40: "Ghafir",
    41: "Fussilat", 42: "Shura", 43: "Zukhruf", 44: "Dukhan", 45: "Jathiyah",
    46: "Ahqaf", 47: "Muhammad", 48: "Fath", 49: "Hujurat", 50: "Qaf",
    51: "Dhariyat", 52: "Tur", 53: "Najm", 54: "Qamar", 55: "Rahman",
    56: "Waqiah", 57: "Hadid", 58: "Mujadilah", 59: "Hashr", 60: "Mumtahanah",
    61: "Saff", 62: "Jumuah", 63: "Munafiqun", 64: "Taghabun", 65: "Talaq",
    66: "Tahrim", 67: "Mulk", 68: "Qalam", 69: "Haqqah", 70: "Maarij",
    71: "Nuh", 72: "Jinn", 73: "Muzzammil", 74: "Muddaththir", 75: "Qiyamah",
    76: "Insan", 77: "Mursalat", 78: "Naba", 79: "Naziat", 80: "Abasa",
    81: "Takwir", 82: "Infitar", 83: "Mutaffifin", 84: "Inshiqaq", 85: "Buruj",
    86: "Tariq", 87: "Ala", 88: "Ghashiyah", 89: "Fajr", 90: "Balad",
    91: "Shams", 92: "Layl", 93: "Duha", 94: "Sharh", 95: "Tin",
    96: "Alaq", 97: "Qadr", 98: "Bayyinah", 99: "Zalzalah", 100: "Adiyat",
    101: "Qariah", 102: "Takathur", 103: "Asr", 104: "Humazah", 105: "Fil",
    106: "Quraysh", 107: "Maun", 108: "Kawthar", 109: "Kafirun", 110: "Nasr",
    111: "Masad", 112: "Ikhlas", 113: "Falaq", 114: "Nas"
}


def build_database(db_path: str = DB_PATH) -> None:
    """Builds the complete SQLite database from JSON sources."""
    if os.path.exists(db_path):
        os.remove(db_path)

    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON;")
    cursor = conn.cursor()

    # 1. Create Tables
    cursor.executescript("""
        CREATE TABLE surahs (
            surah_number INTEGER PRIMARY KEY,
            name_ar TEXT NOT NULL,
            name_en TEXT NOT NULL,
            total_ayahs INTEGER NOT NULL
        );

        CREATE TABLE topics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            level TEXT NOT NULL,
            page_number INTEGER,
            column TEXT,
            parent_major TEXT,
            parent_section TEXT
        );

        CREATE TABLE topic_references (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            topic_id INTEGER NOT NULL REFERENCES topics(id) ON DELETE CASCADE,
            surah_number INTEGER NOT NULL REFERENCES surahs(surah_number)
        );

        CREATE TABLE reference_ayahs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            reference_id INTEGER NOT NULL REFERENCES topic_references(id) ON DELETE CASCADE,
            topic_id INTEGER NOT NULL REFERENCES topics(id) ON DELETE CASCADE,
            surah_number INTEGER NOT NULL REFERENCES surahs(surah_number),
            from_ayah INTEGER NOT NULL,
            to_ayah INTEGER NOT NULL,
            is_range INTEGER NOT NULL
        );

        CREATE TABLE ayahs (
            surah_number INTEGER NOT NULL REFERENCES surahs(surah_number),
            ayah_number INTEGER NOT NULL,
            text_rasmUthmani TEXT NOT NULL,
            PRIMARY KEY (surah_number, ayah_number)
        );

        -- Indexes for high-performance querying
        CREATE INDEX idx_topics_level ON topics(level);
        CREATE INDEX idx_topics_page ON topics(page_number);
        CREATE INDEX idx_ref_topic ON topic_references(topic_id);
        CREATE INDEX idx_ref_surah ON topic_references(surah_number);
        CREATE INDEX idx_ayahs_lookup ON reference_ayahs(surah_number, from_ayah, to_ayah);
        CREATE INDEX idx_ref_ayahs_topic ON reference_ayahs(topic_id);

        -- FTS5 Full-Text Search Virtual Table
        CREATE VIRTUAL TABLE topics_fts USING fts5(
            title,
            parent_major,
            parent_section,
            content='topics',
            content_rowid='id'
        );

        -- Views
        CREATE VIEW v_topics_summary AS
        SELECT t.id, t.title, t.level, t.page_number, t.column, t.parent_major, t.parent_section,
               COUNT(DISTINCT r.id) AS total_surah_citations,
               COUNT(ra.id) AS total_ayah_entries
        FROM topics t
        LEFT JOIN topic_references r ON r.topic_id = t.id
        LEFT JOIN reference_ayahs ra ON ra.topic_id = t.id
        GROUP BY t.id;

        CREATE VIEW v_topic_citations AS
        SELECT t.id AS topic_id, t.title AS topic_title, t.level, t.page_number,
               s.surah_number, s.name_ar AS surah_name_ar, s.name_en AS surah_name_en,
               ra.from_ayah, ra.to_ayah, ra.is_range
        FROM topics t
        JOIN topic_references r ON r.topic_id = t.id
        JOIN surahs s ON s.surah_number = r.surah_number
        JOIN reference_ayahs ra ON ra.reference_id = r.id
        ORDER BY t.id, s.surah_number, ra.from_ayah;
    """)

    # 2. Populate Surahs
    print("Populating Surahs table...")
    surah_rows = []
    for num, meta in sorted(SURAHS.items()):
        name_ar = str(meta["name"])
        name_en = SURAH_NAMES_EN.get(num, f"Surah {num}")
        total = int(meta["total_ayahs"])
        surah_rows.append((num, name_ar, name_en, total))
    cursor.executemany("INSERT INTO surahs VALUES (?, ?, ?, ?)", surah_rows)

    # 3. Populate Ayahs
    print("Populating Ayahs table from Hafs Quranic text...")
    with open(QURAN_TEXT_JSON, "r", encoding="utf-8") as f:
        quran_text_data = json.load(f)

    ayah_rows = []
    for key, text in quran_text_data.get("ayahs", {}).items():
        s_str, a_str = key.split(":")
        ayah_rows.append((int(s_str), int(a_str), text.strip()))
    cursor.executemany("INSERT INTO ayahs VALUES (?, ?, ?)", ayah_rows)

    # 4. Populate Topics, References, and Reference Ayahs
    print("Populating Topics and References...")
    with open(TOPICS_JSON, "r", encoding="utf-8") as f:
        topics_data = json.load(f)

    current_major = ""
    current_section = ""

    for topic_item in topics_data.get("topics", []):
        level = topic_item.get("level", "subtopic")
        title = topic_item.get("title", "").strip()
        page = topic_item.get("page_number")
        col = topic_item.get("column")

        if level == "major_topic":
            current_major = title
            current_section = ""
        elif level == "section":
            current_section = title

        cursor.execute("""
            INSERT INTO topics (title, level, page_number, column, parent_major, parent_section)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (title, level, page, col, current_major, current_section))
        topic_id = cursor.lastrowid

        # Populate FTS
        cursor.execute("""
            INSERT INTO topics_fts (rowid, title, parent_major, parent_section)
            VALUES (?, ?, ?, ?)
        """, (topic_id, title, current_major, current_section))

        for ref in topic_item.get("references", []):
            s_num = int(ref.get("surah_number"))
            cursor.execute("""
                INSERT INTO topic_references (topic_id, surah_number)
                VALUES (?, ?)
            """, (topic_id, s_num))
            ref_id = cursor.lastrowid

            for ayah_spec in ref.get("ayahs", []):
                if isinstance(ayah_spec, list) and len(ayah_spec) == 2:
                    from_a, to_a = int(ayah_spec[0]), int(ayah_spec[1])
                    is_range = 1
                else:
                    from_a = to_a = int(ayah_spec)
                    is_range = 0

                cursor.execute("""
                    INSERT INTO reference_ayahs (reference_id, topic_id, surah_number, from_ayah, to_ayah, is_range)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (ref_id, topic_id, s_num, from_a, to_a, is_range))

    conn.commit()

    # 5. Integrity and Foreign Key Checks
    print("Verifying database integrity...")
    cursor.execute("PRAGMA integrity_check;")
    integrity = cursor.fetchall()
    if integrity != [("ok",)]:
        conn.close()
        raise RuntimeError(f"Integrity check failed: {integrity}")

    cursor.execute("PRAGMA foreign_key_check;")
    fk_errors = cursor.fetchall()
    if fk_errors:
        conn.close()
        raise RuntimeError(f"Foreign key violations found: {fk_errors}")

    # Summary
    cursor.execute("SELECT COUNT(*) FROM surahs")
    surahs_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM ayahs")
    ayahs_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM topics")
    topics_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM topic_references")
    refs_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM reference_ayahs")
    ref_ayahs_count = cursor.fetchone()[0]

    db_size_mb = os.path.getsize(db_path) / (1024 * 1024)
    conn.close()

    print(f"\nSuccessfully built {db_path} ({db_size_mb:.2f} MB):")
    print(f"  Surahs:           {surahs_count}")
    print(f"  Ayahs:            {ayahs_count}")
    print(f"  Topics:           {topics_count}")
    print(f"  Surah References: {refs_count}")
    print(f"  Ayah Entries:     {ref_ayahs_count}")


if __name__ == "__main__":
    build_database()
