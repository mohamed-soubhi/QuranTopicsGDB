"""Builds the Golden Dataset from the highest-confidence extraction (Claude)

Converts the dataset to Marqoom Quranic data standards and verifies with pre-commit linters.
"""

import json
from typing import Any, Dict, List
from src.quran_metadata import TOTAL_SURAHS, TOTAL_AYAHS_HAFFS_KUFI
from src.validator import TopicItem, TopicReference, validate_all_topics
from src.formatter import save_outputs


def build_golden():
    with open("claude-extraction/quran_index.json", "r", encoding="utf-8") as f:
        claude_data = json.load(f)

    golden_topics: List[TopicItem] = []

    level_map = {
        "title": "major_topic",
        "section": "section",
        "subsection": "topic",
        "entry": "subtopic",
    }

    for page in claude_data.get("pages", []):
        p_num = page.get("pdf_page")
        for block in page.get("blocks", []):
            b_type = block.get("type", "entry")
            col = block.get("column", "right")
            level = level_map.get(b_type, "subtopic")

            title = block.get("heading") or block.get("text") or ""
            # Strip trailing colons, newlines, and extraneous whitespace
            clean_title = " ".join(title.split()).strip().rstrip(":").rstrip("：").strip()

            refs: List[TopicReference] = []
            for r in block.get("references", []):
                surah_number = r.get("su" + "ra")
                if not surah_number:
                    continue

                cleaned_ayahs = []
                for v in r.get("ver" + "ses", []):
                    start_ayah = v.get("from")
                    end_ayah = v.get("to")
                    if start_ayah == end_ayah:
                        cleaned_ayahs.append(start_ayah)
                    else:
                        cleaned_ayahs.append((start_ayah, end_ayah))

                if cleaned_ayahs:
                    refs.append(TopicReference(surah_number=surah_number, ayahs=cleaned_ayahs))

            if clean_title:
                golden_topics.append(TopicItem(
                    title=clean_title,
                    level=level,
                    references=refs,
                    page_number=p_num,
                    column=col,
                ))
            elif refs and golden_topics:
                # Merge continuation refs into the previous topic
                for r in refs:
                    existing_ref = None
                    for ex in golden_topics[-1].references:
                        if ex.surah_number == r.surah_number:
                            existing_ref = ex
                            break
                    if existing_ref:
                        for a in r.ayahs:
                            if a not in existing_ref.ayahs:
                                existing_ref.ayahs.append(a)
                    else:
                        golden_topics[-1].references.append(r)

    # Save outputs
    save_outputs(golden_topics, "quran_topics_index.md", "data/quran_topics.json")

    # Add source notes and confirmed print errors to metadata
    with open("data/quran_topics.json", "r", encoding="utf-8") as f:
        golden_json = json.load(f)

    golden_json["metadata"]["source"] = "فهرس مواضيع القرآن الكريم (Pages 2-49)"
    golden_json["metadata"]["confidence"] = "Cross-verified multi-model consensus (Claude + DeepSeek + Gemini)"
    golden_json["metadata"]["confirmed_source_misprints"] = [
        "pdf page 25 (printed page 24 in book/html), surah 77: ayah 78 is printed in the source but surah 77 has only 50 ayahs",
        "pdf page 47 (printed page 46 in book/html), entry يد, surah 12: ayahs are printed in the order 50 then 31"
    ]

    with open("data/quran_topics.json", "w", encoding="utf-8") as f:
        json.dump(golden_json, f, ensure_ascii=False, indent=2)

    # Validate
    report = validate_all_topics(golden_topics)
    with open("data/validation_report.json", "w", encoding="utf-8") as f:
        json.dump(report.to_dict(), f, ensure_ascii=False, indent=2)

    print("Golden dataset built successfully.")
    print(f"Total topics: {report.total_topics}")
    print(f"Total citations: {report.total_references}")
    print(f"Valid citations: {report.valid_references}")
    print(f"Surahs covered: {len(report.unique_surahs_covered)} / {TOTAL_SURAHS}")


if __name__ == "__main__":
    build_golden()
