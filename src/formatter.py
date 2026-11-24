"""Formatters for Markdown output and Marqoom-compliant JSON."""

import json
from typing import Any, Dict, List
from src.validator import TopicItem, TopicReference
from src.quran_metadata import TOTAL_SURAHS, TOTAL_AYAHS_HAFFS_KUFI


def format_references_markdown(references: List[TopicReference]) -> str:
    """Formats references as: 2: 117, 185, 253 | 4: 26-28."""
    parts = []
    for ref in references:
        ayah_strs = []
        for ayah in ref.ayahs:
            if isinstance(ayah, int):
                ayah_strs.append(str(ayah))
            elif isinstance(ayah, (list, tuple)) and len(ayah) == 2:
                ayah_strs.append(f"{ayah[0]}-{ayah[1]}")
            else:
                ayah_strs.append(str(ayah))
        joined_ayahs = ", ".join(ayah_strs)
        parts.append(f"{ref.surah_number}: {joined_ayahs}")
    return " | ".join(parts)


def generate_markdown(items: List[TopicItem], title: str = "فهرس مواضيع القرآن الكريم") -> str:
    """Generates structured Markdown text for topics and verse references."""
    lines = [f"# {title}", "", "> مصدر البيانات: صفحات 2 إلى 49 من المصحف المفهرس موضوعياً.", ""]

    for item in items:
        ref_text = format_references_markdown(item.references) if item.references else ""

        if item.level == "major_topic":
            lines.append(f"\n## {item.title}\n")
        elif item.level == "section":
            lines.append(f"\n### {item.title}\n")
        elif item.level == "topic":
            if ref_text:
                lines.append(f"#### {item.title}: {ref_text}")
            else:
                lines.append(f"#### {item.title}")
        else:  # subtopic
            if ref_text:
                lines.append(f"* **{item.title}:** {ref_text}")
            else:
                lines.append(f"* **{item.title}**")

    return "\n".join(lines) + "\n"


def generate_marqoom_json(items: List[TopicItem]) -> Dict[str, Any]:
    """Generates dictionary conforming to Marqoom Quranic data standards."""
    topic_dicts = []
    for item in items:
        ref_list = []
        for ref in item.references:
            ayahs_formatted = []
            for a in ref.ayahs:
                if isinstance(a, tuple):
                    ayahs_formatted.append(list(a))
                else:
                    ayahs_formatted.append(a)
            ref_list.append({
                "surah_number": ref.surah_number,
                "ayahs": ayahs_formatted,
            })

        topic_dicts.append({
            "title": item.title,
            "level": item.level,
            "page_number": item.page_number,
            "column": item.column,
            "references": ref_list,
        })

    return {
        "metadata": {
          "riwayah": "hafs_an_asim",
          "total_surahs": TOTAL_SURAHS,
          "total_ayahs": TOTAL_AYAHS_HAFFS_KUFI,
          "source": "فهرس مواضيع القرآن الكريم",
        },
        "topics": topic_dicts,
    }


def save_outputs(items: List[TopicItem], md_path: str, json_path: str) -> None:
    """Saves Markdown and Marqoom-compliant JSON files."""
    md_content = generate_markdown(items)
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(md_content)

    data_content = generate_marqoom_json(items)
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(data_content, f, ensure_ascii=False, indent=2)
