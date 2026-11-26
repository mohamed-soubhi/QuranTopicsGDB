"""SQLite Database access and query utilities for QuranTopicsGDB."""

import os
import sqlite3
from typing import Any, Dict, List, Optional, Tuple

DEFAULT_DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "quran_topics.db")


def get_connection(db_path: Optional[str] = None) -> sqlite3.Connection:
    """Returns a SQLite connection with foreign keys and row factory enabled."""
    path = db_path or DEFAULT_DB_PATH
    conn = sqlite3.connect(path)
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.row_factory = sqlite3.Row
    return conn


def search_topics(query: str, db_path: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
    """Performs ranked search across topic titles and parent hierarchies.

    Rank 1: Exact/substring match in Topic Title
    Rank 2: Match in Parent Section or Major Topic
    Rank 3: Citations of a Surah (if query is a Surah number or name)
    """
    clean_query = query.strip()
    if not clean_query:
        return []

    conn = get_connection(db_path)
    cursor = conn.cursor()

    # Rank 1: Direct title match
    cursor.execute("""
        SELECT t.id, t.title, t.level, t.page_number, t.column, t.parent_major, t.parent_section, 1 AS rank
        FROM topics t
        WHERE t.title LIKE ?
        LIMIT ?
    """, (f"%{clean_query}%", limit))
    rank1 = [dict(row) for row in cursor.fetchall()]

    # Rank 2: Hierarchy match
    cursor.execute("""
        SELECT t.id, t.title, t.level, t.page_number, t.column, t.parent_major, t.parent_section, 2 AS rank
        FROM topics t
        WHERE (t.parent_section LIKE ? OR t.parent_major LIKE ?)
          AND t.title NOT LIKE ?
        LIMIT ?
    """, (f"%{clean_query}%", f"%{clean_query}%", f"%{clean_query}%", limit))
    rank2 = [dict(row) for row in cursor.fetchall()]

    conn.close()
    return (rank1 + rank2)[:limit]


def get_topic_by_id(topic_id: int, db_path: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """Fetches a complete topic record including all references and Ayah texts."""
    conn = get_connection(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM topics WHERE id = ?", (topic_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return None

    topic = dict(row)

    # Fetch references and ayahs
    cursor.execute("""
        SELECT r.id AS ref_id, r.surah_number, s.name_ar AS surah_name_ar, s.name_en AS surah_name_en,
               ra.from_ayah, ra.to_ayah, ra.is_range
        FROM topic_references r
        JOIN surahs s ON s.surah_number = r.surah_number
        JOIN reference_ayahs ra ON ra.reference_id = r.id
        WHERE r.topic_id = ?
        ORDER BY r.id, ra.from_ayah
    """, (topic_id,))

    references_map: Dict[int, Dict[str, Any]] = {}
    for r in cursor.fetchall():
        ref_id = r["ref_id"]
        if ref_id not in references_map:
            references_map[ref_id] = {
                "surah_number": r["surah_number"],
                "surah_name_ar": r["surah_name_ar"],
                "surah_name_en": r["surah_name_en"],
                "ayahs": []
            }
        
        # Fetch Ayah texts
        ayah_texts = []
        if r["is_range"]:
            cursor.execute("""
                SELECT ayah_number, text_rasmUthmani
                FROM ayahs
                WHERE surah_number = ? AND ayah_number BETWEEN ? AND ?
                ORDER BY ayah_number
            """, (r["surah_number"], r["from_ayah"], r["to_ayah"]))
        else:
            cursor.execute("""
                SELECT ayah_number, text_rasmUthmani
                FROM ayahs
                WHERE surah_number = ? AND ayah_number = ?
            """, (r["surah_number"], r["from_ayah"]))

        for a_row in cursor.fetchall():
            ayah_texts.append({
                "ayah_number": a_row["ayah_number"],
                "text_rasmUthmani": a_row["text_rasmUthmani"]
            })

        references_map[ref_id]["ayahs"].append({
            "from_ayah": r["from_ayah"],
            "to_ayah": r["to_ayah"],
            "is_range": bool(r["is_range"]),
            "texts": ayah_texts
        })

    topic["references"] = list(references_map.values())
    conn.close()
    return topic


def get_topics_by_ayah(surah_number: int, ayah_number: int, db_path: Optional[str] = None) -> List[Dict[str, Any]]:
    """Finds all topics citing a specific Ayah (either single or inside a range)."""
    conn = get_connection(db_path)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT DISTINCT t.id, t.title, t.level, t.page_number, t.column, t.parent_major, t.parent_section,
                        ra.from_ayah, ra.to_ayah, ra.is_range
        FROM reference_ayahs ra
        JOIN topics t ON t.id = ra.topic_id
        WHERE ra.surah_number = ?
          AND ra.from_ayah <= ?
          AND ra.to_ayah >= ?
        ORDER BY t.page_number, t.id
    """, (surah_number, ayah_number, ayah_number))

    results = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return results


def get_database_stats(db_path: Optional[str] = None) -> Dict[str, int]:
    """Returns total counts for topics, references, citations, and ayahs."""
    conn = get_connection(db_path)
    cursor = conn.cursor()

    stats = {}
    for table in ["surahs", "topics", "topic_references", "reference_ayahs", "ayahs"]:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        stats[table] = cursor.fetchone()[0]

    conn.close()
    return stats
