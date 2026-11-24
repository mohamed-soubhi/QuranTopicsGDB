#!/usr/bin/env python3
"""Main extraction and validation pipeline for BOOK_27464_1.pdf (Pages 2 to 49)."""

import argparse
import json
import os
import sys
from typing import List

from src.page_preprocessor import extract_page_image, slice_page_columns
from src.extractor import call_ollama_vision, parse_llm_json_response, clean_and_normalize_topic
from src.validator import TopicItem, validate_all_topics
from src.formatter import save_outputs


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
        try:
            raw_text = call_ollama_vision(chunk_img, model=model)
            raw_items = parse_llm_json_response(raw_text)
            for r_item in raw_items:
                norm_item = clean_and_normalize_topic(r_item, page_number=page_num, column=column_name)
                if norm_item.title or norm_item.references:
                    items.append(norm_item)
        except Exception as e:
            print(f"    [Warning] Chunk {chunk_idx} extraction error: {e}", file=sys.stderr)

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
    args = parser.parse_args()

    os.makedirs("data", exist_ok=True)

    print(f"==================================================")
    print(f"Starting Quran Topics Extraction Pipeline")
    print(f"PDF: {args.pdf}")
    print(f"Pages: {args.start_page} to {args.end_page}")
    print(f"Model: {args.model}")
    print(f"==================================================")

    all_topics: List[TopicItem] = []

    for page_num in range(args.start_page, args.end_page + 1):
        print(f"\n[Page {page_num}/{args.end_page}]")
        try:
            page_img = extract_page_image(args.pdf, page_num)
            col_right, col_left = slice_page_columns(page_img)

            # In Arabic RTL, right column is read first, then left column
            print("Processing Right Column...")
            right_items = process_column(col_right, page_num, "right", args.model)
            all_topics.extend(right_items)

            print("Processing Left Column...")
            left_items = process_column(col_left, page_num, "left", args.model)
            all_topics.extend(left_items)

            print(f"Page {page_num} finished. Total topics so far: {len(all_topics)}")

        except Exception as e:
            print(f"[Error] Failed to process page {page_num}: {e}", file=sys.stderr)

    # Validation
    print("\n--------------------------------------------------")
    print("Running Quranic Coverage & Validation Engine...")
    report = validate_all_topics(all_topics)
    report_dict = report.to_dict()

    print(f"Validation Summary:")
    print(f"  Total Topics: {report.total_topics}")
    print(f"  Total References: {report.total_references}")
    print(f"  Valid References: {report.valid_references}")
    print(f"  Invalid References: {len(report.invalid_references)}")
    print(f"  Surahs Covered: {len(report.unique_surahs_covered)} / 114")

    # Save outputs
    save_outputs(all_topics, args.output_md, args.output_json)
    with open(args.report_json, "w", encoding="utf-8") as f:
        json.dump(report_dict, f, ensure_ascii=False, indent=2)

    print(f"\nSaved Markdown: {args.output_md}")
    print(f"Saved Dataset: {args.output_json}")
    print(f"Saved Report: {args.report_json}")
    print("==================================================")


if __name__ == "__main__":
    main()
