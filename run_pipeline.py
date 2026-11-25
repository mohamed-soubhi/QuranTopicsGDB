#!/usr/bin/env python3
"""Main extraction and validation pipeline for BOOK_27464_1.pdf (Pages 2 to 49)."""

import argparse
import json
import os
import sys
import time
from typing import List

from src.page_preprocessor import extract_page_image, slice_page_columns
from src.extractor import call_ollama_vision, parse_llm_json_response, clean_and_normalize_topic
from src.validator import TopicItem, TopicReference, validate_all_topics
from src.formatter import save_outputs


def serialize_topic_item(item: TopicItem) -> dict:
    """Serializes a TopicItem to dict for caching."""
    refs = []
    for r in item.references:
        formatted_ayahs = [list(a) if isinstance(a, tuple) else a for a in r.ayahs]
        refs.append({
            "surah_number": r.surah_number,
            "ayahs": formatted_ayahs,
        })
    return {
        "title": item.title,
        "level": item.level,
        "references": refs,
        "page_number": item.page_number,
        "column": item.column,
    }


def deserialize_topic_item(data: dict) -> TopicItem:
    """Deserializes dict from cache to TopicItem."""
    refs = []
    for r in data.get("references", []):
        cleaned_ayahs = []
        for a in r.get("ayahs", []):
            if isinstance(a, list) and len(a) == 2:
                cleaned_ayahs.append((a[0], a[1]))
            else:
                cleaned_ayahs.append(a)
        refs.append(TopicReference(surah_number=r.get("surah_number", 0), ayahs=cleaned_ayahs))
    return TopicItem(
        title=data.get("title", ""),
        level=data.get("level", "subtopic"),
        references=refs,
        page_number=data.get("page_number"),
        column=data.get("column"),
    )


def process_column(
    col_img,
    page_num: int,
    column_name: str,
    model: str,
    chunk_height: int = 550,
) -> List[TopicItem]:
    """Slices column into manageable vertical chunks and extracts topics."""
    items: List[TopicItem] = []
    w, h = col_img.size

    y = 0
    chunk_idx = 0
    overlap = 40

    while y < h:
        y_end = min(y + chunk_height, h)
        chunk_img = col_img.crop((0, y, w, y_end))
        chunk_idx += 1

        print(f"  -> Processing {column_name} col, chunk {chunk_idx} (y: {y}..{y_end})...", flush=True)
        # Retry logic
        for attempt in range(1, 3):
            try:
                raw_text = call_ollama_vision(chunk_img, model=model)
                raw_items = parse_llm_json_response(raw_text)
                for r_item in raw_items:
                    norm_item = clean_and_normalize_topic(r_item, page_number=page_num, column=column_name)
                    if norm_item.title or norm_item.references:
                        items.append(norm_item)
                break
            except Exception as e:
                print(f"    [Attempt {attempt}] Chunk {chunk_idx} extraction error: {e}", file=sys.stderr, flush=True)
                if attempt < 2:
                    time.sleep(3)

        if y_end >= h:
            break
        y = y_end - overlap

    return items


def main():
    parser = argparse.ArgumentParser(description="Quran Topics Extraction & Verification Pipeline")
    parser.add_argument("--pdf", default="BOOK_27464_1.pdf", help="Path to PDF book")
    parser.add_argument("--start-page", type=int, default=2, help="Start page (inclusive, default: 2)")
    parser.add_argument("--end-page", type=int, default=49, help="End page (inclusive, default: 49)")
    parser.add_argument("--model", default="deepseek-v4.1-flash:cloud", help="Ollama model to use")
    parser.add_argument("--output-md", default="quran_topics_index.md", help="Output Markdown path")
    parser.add_argument("--output-json", default="data/quran_topics.json", help="Output JSON path")
    parser.add_argument("--report-json", default="data/validation_report.json", help="Validation report path")
    parser.add_argument("--force", action="store_true", help="Force re-extraction of cached pages")
    args = parser.parse_args()

    cache_dir = os.path.join("data", "cache")
    os.makedirs(cache_dir, exist_ok=True)

    print("==================================================")
    print("Starting Quran Topics Extraction Pipeline")
    print(f"PDF: {args.pdf}")
    print(f"Pages: {args.start_page} to {args.end_page}")
    print(f"Model: {args.model}")
    print("==================================================", flush=True)

    all_topics: List[TopicItem] = []

    for page_num in range(args.start_page, args.end_page + 1):
        cache_file = os.path.join(cache_dir, f"page_{page_num}.json")
        page_items: List[TopicItem] = []

        if not args.force and os.path.exists(cache_file):
            print(f"\n[Page {page_num}/{args.end_page}] Loading from cache: {cache_file}", flush=True)
            try:
                with open(cache_file, "r", encoding="utf-8") as f:
                    cached_data = json.load(f)
                page_items = [deserialize_topic_item(d) for d in cached_data]
                all_topics.extend(page_items)
                print(f"  Loaded {len(page_items)} topics from cache.", flush=True)
                continue
            except Exception as e:
                print(f"  [Warning] Failed to load cache for page {page_num}: {e}. Re-extracting...", flush=True)

        print(f"\n[Page {page_num}/{args.end_page}] Extracting fresh from PDF...", flush=True)
        try:
            page_img = extract_page_image(args.pdf, page_num)
            col_right, col_left = slice_page_columns(page_img)

            # In Arabic RTL, right column is read first, then left column
            print("Processing Right Column...", flush=True)
            right_items = process_column(col_right, page_num, "right", args.model)
            page_items.extend(right_items)

            print("Processing Left Column...", flush=True)
            left_items = process_column(col_left, page_num, "left", args.model)
            page_items.extend(left_items)

            # Cache page items
            serialized = [serialize_topic_item(it) for it in page_items]
            with open(cache_file, "w", encoding="utf-8") as f:
                json.dump(serialized, f, ensure_ascii=False, indent=2)

            all_topics.extend(page_items)
            print(f"Page {page_num} finished. Total topics so far: {len(all_topics)}", flush=True)

            # Incremental save
            save_outputs(all_topics, args.output_md, args.output_json)
            report = validate_all_topics(all_topics)
            with open(args.report_json, "w", encoding="utf-8") as f:
                json.dump(report.to_dict(), f, ensure_ascii=False, indent=2)

        except Exception as e:
            print(f"[Error] Failed to process page {page_num}: {e}", file=sys.stderr, flush=True)

    # Final Validation Report
    print("\n--------------------------------------------------")
    print("Running Quranic Coverage & Validation Engine...")
    final_report = validate_all_topics(all_topics)
    report_dict = final_report.to_dict()

    print("Validation Summary:")
    print(f"  Total Topics: {final_report.total_topics}")
    print(f"  Total References: {final_report.total_references}")
    print(f"  Valid References: {final_report.valid_references}")
    print(f"  Invalid References: {len(final_report.invalid_references)}")
    print(f"  Surahs Covered: {len(final_report.unique_surahs_covered)} / 114", flush=True)

    # Final Save outputs
    save_outputs(all_topics, args.output_md, args.output_json)
    with open(args.report_json, "w", encoding="utf-8") as f:
        json.dump(report_dict, f, ensure_ascii=False, indent=2)

    print(f"\nSaved Markdown: {args.output_md}")
    print(f"Saved Dataset: {args.output_json}")
    print(f"Saved Report: {args.report_json}")
    print("==================================================", flush=True)


if __name__ == "__main__":
    main()
