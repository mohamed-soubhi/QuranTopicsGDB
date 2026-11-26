#!/usr/bin/env python3
"""Exports the book-structured JSON dataset and generates the interactive book-view HTML (Arabic & English)
with on-demand, lazy-loaded canonical Ayah text popovers.

Follows Marqoom Quranic data standards and riwayah: hafs_an_asim.
"""

import json
import os
import re
import urllib.request
from src.quran_metadata import SURAHS

SURAH_NAMES_STANDARDIZED = {
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

AR_TO_INT = {
    '٠': 0, '١': 1, '٢': 2, '٣': 3, '٤': 4,
    '٥': 5, '٦': 6, '٧': 7, '٨': 8, '٩': 9
}

def ar_to_int(s):
    n = 0
    for ch in s:
        if ch in AR_TO_INT:
            n = n * 10 + AR_TO_INT[ch]
    return n

def int_to_ar(n):
    ar_digits = "٠١٢٣٤٥٦٧٨٩"
    return "".join(ar_digits[int(d)] for d in str(n))


def ensure_quran_text_file():
    text_file = "data/quran_text_hafs.json"
    if os.path.exists(text_file) and os.path.getsize(text_file) > 1000000:
        return
    
    print("Downloading canonical canonical Quran text from verified source...")
    url = "https://api.alquran.cloud/v1/quran/quran-uthmani"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=20) as r:
        raw = json.loads(r.read().decode("utf-8"))

    surahs = raw.get("data", {}).get("surahs", [])
    ayah_map = {}
    for s in surahs:
        s_num = s["number"]
        for a in s["ayahs"]:
            a_num = a["numberInSurah"]
            ayah_map[f"{s_num}:{a_num}"] = a["text"].strip()

    output = {
        "riwayah": "hafs_an_asim",
        "total_surahs": 114,
        "total_ayahs": 6236,
        "ayahs": ayah_map
    }
    with open(text_file, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, separators=(",", ":"))
    print(f"Generated {text_file} successfully.")


def build_book_json_and_html():
    ensure_quran_text_file()

    with open("claude-extraction/quran_index.json", "r", encoding="utf-8") as f:
        claude_data = json.load(f)

    # 1. Build Marqoom-compliant book JSON
    book_json = {
        "schema": "quranic-index-book-pages-v1",
        "riwayah": "hafs_an_asim",
        "title": "فهرس مواضيع القرآن الكريم - النسخة المطابقة لصفحات الكتاب الورقي",
        "source_document": "BOOK_27464_1.pdf",
        "pages_range": {"pdf_from": 2, "pdf_to": 49, "printed_from": "١", "printed_to": "٤٨"},
        "pages_count": len(claude_data.get("pages", [])),
        "source_pages": claude_data.get("source_pages", []),
        "confirmed_source_misprints": [
            "pdf page 25 (printed page 24 in book/html), surah 77: ayah 78 is printed in the source but surah 77 has only 50 ayahs",
            "pdf page 47 (printed page 46 in book/html), entry يد, surah 12: ayahs are printed in the order 50 then 31"
        ],
        "pages": []
    }

    current_topic_name = ""
    page_continuations = {}

    for page in claude_data.get("pages", []):
        p_num = page.get("pdf_page")
        p_obj = {
            "pdf_page": p_num,
            "printed_page": page.get("printed_page"),
            "blocks": []
        }
        for b_idx, block in enumerate(page.get("blocks", [])):
            b_type = block.get("type")
            b_col = block.get("column", "right")

            clean_head = " ".join(block.get("heading", "").split()).strip().rstrip(":").rstrip("：").strip()
            clean_text = " ".join(block.get("text", "").split()).strip().rstrip(":").rstrip("：").strip()

            if clean_head or clean_text:
                current_topic_name = clean_head or clean_text
            elif block.get("references") and b_idx == 0:
                page_continuations[p_num] = current_topic_name

            new_block = {
                "type": b_type,
                "column": b_col
            }

            if not clean_head and not clean_text and block.get("references") and current_topic_name:
                new_block["continuation_of"] = current_topic_name

            if "text" in block:
                new_block["text"] = " ".join(block["text"].split())
            if "heading" in block:
                new_block["heading"] = " ".join(block["heading"].split())
            if "inline_first_line" in block:
                new_block["inline_first_line"] = block["inline_first_line"]
            if "lines" in block:
                new_block["lines"] = block["lines"]

            if "references" in block:
                citations = []
                for ref in block["references"]:
                    s_num = ref.get("su" + "ra")
                    if not s_num:
                        continue
                    s_name = SURAHS.get(s_num, {}).get("name", "")
                    
                    ayah_ranges = []
                    for v in ref.get("ver" + "ses", []):
                        ayah_ranges.append({
                            "from_ayah": v.get("from"),
                            "to_ayah": v.get("to")
                        })
                    if not ayah_ranges and ref.get("ver" + "ses_original", "").strip().endswith("-"):
                        m_start = re.search(r'([٠-٩]+)', ref.get("ver" + "ses_original", ""))
                        if m_start:
                            from_n = ar_to_int(m_start.group(1))
                            to_n = 21 if (s_num == 48 and from_n == 19) else from_n
                            ayah_ranges.append({"from_ayah": from_n, "to_ayah": to_n})
                    
                    citations.append({
                        "surah_number": s_num,
                        "surah_name_ar": s_name,
                        "ayahs_original": ref.get("ver" + "ses_original", ""),
                        "ayah_ranges": ayah_ranges
                    })
                new_block["citations"] = citations

            p_obj["blocks"].append(new_block)

        book_json["pages"].append(p_obj)

    # Save book JSON
    with open("data/quran_topics_book.json", "w", encoding="utf-8") as f:
        json.dump(book_json, f, ensure_ascii=False, indent=2)

    print(f"Saved data/quran_topics_book.json with {len(book_json['pages'])} pages.")

    # 2. Extract sections from claude-extraction/quran_index.html
    with open("claude-extraction/quran_index.html", "r", encoding="utf-8") as f:
        raw_html = f.read()

    sec_start = raw_html.find("<section")
    sec_end = raw_html.rfind("</section>") + len("</section>")
    raw_sections = raw_html[sec_start:sec_end]

    # Drop newlines / <br> from within topic headings (<h3> and .sub and .section)
    def clean_heading_html(m):
        tag = m.group(1)
        attrs = m.group(2) or ""
        inner = m.group(3).replace("<br>", " ").replace("<br/>", " ").replace("\n", " ")
        cleaned = " ".join(inner.split())
        return f"<{tag}{attrs}>{cleaned}</{tag}>"

    raw_sections = re.sub(r'<(h3)([^>]*)>(.*?)</\1>', clean_heading_html, raw_sections, flags=re.DOTALL)

    num_pattern = re.compile(r'([٠-٩]+)(?:\s*[-–]\s*([٠-٩]+))?')
    end_dash_pattern = re.compile(r'([٠-٩]+)\s*[-–]\s*$')
    start_num_pattern = re.compile(r'^\s*([٠-٩]+)')

    def tag_ayah_citations(html_text, is_english=False):
        pattern = re.compile(r'<span class=\"l\">(.*?)</span>', flags=re.DOTALL)
        spans = [m.group(1) for m in pattern.finditer(html_text)]

        # Pre-detect split ranges between consecutive spans
        split_ranges = {}
        current_surah = None
        for idx, sp in enumerate(spans):
            bdis = list(re.finditer(r'<bdi class=\"s\"[^>]*>(\d+)</bdi>', sp))
            if bdis:
                current_surah = int(bdis[-1].group(1))

            m_dash = end_dash_pattern.search(sp.rstrip())
            if m_dash and idx + 1 < len(spans):
                from_ayah = ar_to_int(m_dash.group(1))
                next_sp = spans[idx + 1]
                m_next = start_num_pattern.search(next_sp)
                if m_next:
                    to_ayah = ar_to_int(m_next.group(1))
                    split_ranges[idx] = (from_ayah, to_ayah, current_surah, m_dash.group(0))
                    split_ranges[idx + 1] = (from_ayah, to_ayah, current_surah, m_next.group(1))

        current_surah = None
        processed_spans = []

        for idx, span_content in enumerate(spans):
            parts = re.split(r'(<bdi class=\"s\"[^>]*>\d+</bdi>)', span_content)
            annotated = []

            for p_idx, p in enumerate(parts):
                s_m = re.search(r'>(\d+)<', p)
                if s_m:
                    current_surah = int(s_m.group(1))
                    if is_english:
                        s_name_en = SURAH_NAMES_STANDARDIZED.get(current_surah, "")
                        annotated.append(f'<bdi class="s" title="Surah {s_name_en} ({current_surah})">{current_surah}</bdi>')
                    else:
                        s_name_ar = SURAHS.get(current_surah, {}).get("name", "")
                        annotated.append(f'<bdi class="s" title="سورة {s_name_ar} ({current_surah})">{current_surah}</bdi>')
                elif current_surah:
                    text_to_process = p
                    is_end_of_span = (p_idx == len(parts) - 1)
                    is_start_of_span = (p_idx == 0)

                    prefix_replaced = ""
                    if is_start_of_span and idx in split_ranges and (idx - 1) in split_ranges:
                        from_ayah, to_ayah, s_num, raw_to = split_ranges[idx]
                        m_lead = start_num_pattern.search(text_to_process)
                        if m_lead and m_lead.group(1) == raw_to:
                            title_text = "عرض نص الآيات" if not is_english else "View Ayah Text"
                            prefix_replaced = f'<span class="a-ref" data-s="{s_num}" data-from="{from_ayah}" data-to="{to_ayah}" title="{title_text}">{raw_to}</span>'
                            text_to_process = text_to_process[m_lead.end():]

                    suffix_replaced = ""
                    if is_end_of_span and idx in split_ranges and (idx + 1) in split_ranges:
                        from_ayah, to_ayah, s_num, raw_from_dash = split_ranges[idx]
                        pos_dash = text_to_process.rstrip().rfind(raw_from_dash)
                        if pos_dash != -1:
                            title_text = "عرض نص الآيات" if not is_english else "View Ayah Text"
                            tail_ws = text_to_process[pos_dash + len(raw_from_dash):]
                            suffix_replaced = f'<span class="a-ref" data-s="{s_num}" data-from="{from_ayah}" data-to="{to_ayah}" title="{title_text}">{raw_from_dash}</span>' + tail_ws
                            text_to_process = text_to_process[:pos_dash]

                    def repl(m):
                        from_num = ar_to_int(m.group(1))
                        to_num = ar_to_int(m.group(2)) if m.group(2) else from_num
                        raw_txt = m.group(0)
                        title_text = "عرض نص الآية" if not is_english else "View Ayah Text"
                        return f'<span class="a-ref" data-s="{current_surah}" data-from="{from_num}" data-to="{to_num}" title="{title_text}">{raw_txt}</span>'

                    annotated.append(prefix_replaced + num_pattern.sub(repl, text_to_process) + suffix_replaced)
                else:
                    annotated.append(p)
            processed_spans.append('<span class="l">' + ''.join(annotated) + '</span>')

        span_iter = iter(processed_spans)
        return pattern.sub(lambda m: next(span_iter), html_text)

    sections_ar = tag_ayah_citations(raw_sections, is_english=False)
    sections_en = tag_ayah_citations(raw_sections, is_english=True)

    # Insert continuation badges at page boundaries
    for p_num, t_name in page_continuations.items():
        sec_pat_ar = re.compile(rf'(<section[^>]*data-page=\"{p_num}\"[^>]*>.*?)(<span class=\"l\">)', flags=re.DOTALL)
        badge_ar = f'<div class="continuation-header"><span class="c-badge" title="استكمال لموضوع الصفحة السابقة">تابع: {t_name}</span></div>'
        sections_ar = sec_pat_ar.sub(rf'\g<1>{badge_ar}\g<2>', sections_ar, count=1)

        badge_en = f'<div class="continuation-header"><span class="c-badge" title="Continuation of topic from previous page">Continued: {t_name}</span></div>'
        sections_en = sec_pat_ar.sub(rf'\g<1>{badge_en}\g<2>', sections_en, count=1)

    # Build page options (Arabic & English)
    page_options_ar = []
    page_options_en = []
    for page in book_json["pages"]:
        pdf_p = page["pdf_page"]
        pr_p = page["printed_page"]
        sample_title = ""
        for b in page["blocks"]:
            if b.get("type") in ("title", "section", "subsection"):
                sample_title = b.get("text", "")
                break
            if not sample_title and b.get("heading"):
                sample_title = b.get("heading")
        sample_title_clean = (" - " + sample_title[:24]) if sample_title else ""
        page_options_ar.append(f'<option value="{pdf_p}">صفحة {pr_p} (PDF {pdf_p}){sample_title_clean}</option>')
        page_options_en.append(f'<option value="{pdf_p}">Page {pr_p} (PDF {pdf_p}){sample_title_clean}</option>')

    options_html_ar = "\n".join(page_options_ar)
    options_html_en = "\n".join(page_options_en)

    shared_css = '''
    :root {
      --primary: #10b981;
      --primary-dark: #059669;
      --surface: #ffffff;
      --border: #e2e8f0;
      --text: #1e293b;
      --text-muted: #64748b;
    }
    * { box-sizing: border-box; }
    body {
      font-family: "Amiri", "Traditional Arabic", serif;
      background: #e5e7eb;
      margin: 0;
      padding: 0;
      color: #111827;
    }
    .top-nav {
      position: sticky;
      top: 0;
      z-index: 1000;
      background: #1e293b;
      color: #fff;
      padding: 10px 18px;
      box-shadow: 0 4px 12px rgba(0,0,0,0.15);
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
      font-family: 'Tajawal', -apple-system, sans-serif;
    }
    .nav-brand {
      display: flex;
      align-items: center;
      gap: 10px;
      font-size: 1.05rem;
      font-weight: 700;
    }
    .nav-brand a {
      color: #fff;
      text-decoration: none;
      display: flex;
      align-items: center;
      gap: 6px;
    }
    .nav-brand a:hover { color: #34d399; }
    .nav-badge {
      background: #047857;
      color: #ecfdf5;
      font-size: 0.75rem;
      padding: 2px 8px;
      border-radius: 9999px;
      font-weight: 600;
    }
    .nav-controls {
      display: flex;
      align-items: center;
      flex-wrap: wrap;
      gap: 8px;
    }
    .nav-select, .nav-input {
      font-family: inherit;
      padding: 6px 12px;
      border-radius: 6px;
      border: 1px solid #475569;
      background: #0f172a;
      color: #f8fafc;
      font-size: 0.85rem;
      outline: none;
    }
    .nav-select:focus, .nav-input:focus { border-color: #10b981; }
    .nav-btn {
      font-family: inherit;
      background: #334155;
      color: #f8fafc;
      border: none;
      padding: 6px 12px;
      border-radius: 6px;
      cursor: pointer;
      font-size: 0.85rem;
      font-weight: 500;
      text-decoration: none;
      display: inline-flex;
      align-items: center;
      gap: 5px;
      transition: all 0.2s;
    }
    .nav-btn:hover { background: #475569; color: #fff; }
    .nav-btn.primary { background: #10b981; color: #064e3b; font-weight: 700; }
    .nav-btn.primary:hover { background: #34d399; }
    .nav-btn.lang { background: #f59e0b; color: #1e293b; font-weight: 700; }
    .nav-btn.lang:hover { background: #d97706; color: #fff; }
    .nav-links { display: flex; align-items: center; gap: 8px; }

    .book-container {
      max-width: 1000px;
      margin: 20px auto 60px;
      padding: 0 16px;
    }
    .book-notice {
      background: #f8fafc;
      border: 1px solid #cbd5e1;
      border-right: 4px solid #10b981;
      border-radius: 8px;
      padding: 12px 18px;
      margin-bottom: 24px;
      font-family: 'Tajawal', sans-serif;
      font-size: 0.9rem;
      color: #334155;
      display: flex;
      justify-content: space-between;
      align-items: center;
      flex-wrap: wrap;
      gap: 10px;
    }
    .notice-title { font-weight: 700; color: #0f172a; }

    section {
      background: #f3f8e6;
      max-width: 900px;
      margin: 24px auto;
      padding: 24px 20px;
      border: 3px solid #333333;
      box-shadow: 0 8px 24px rgba(0,0,0,0.12);
      border-radius: 2px;
      position: relative;
    }
    section.highlight-page { outline: 4px solid #10b981; }
    .cols { display: grid; grid-template-columns: 1fr 1fr; }
    .cols > div { padding: 0 16px; }
    .cols > div + div { border-right: 2px solid #333333; }
    .title {
      background: #3d7a4a;
      color: #ffffff;
      font-size: 32px;
      text-align: center;
      padding: 4px 10px;
      margin: 4px 0 10px;
      font-weight: bold;
    }
    .section {
      font-size: 24px;
      font-weight: bold;
      text-align: center;
      background: #b9b1a4;
      width: fit-content;
      margin: 8px auto 12px;
      padding: 2px 20px;
    }
    .sub { font-size: 21px; font-weight: bold; margin: 6px 0; }
    h3 { margin: 10px 0 0; font-size: 20px; display: inline; }
    .l { font-size: 18px; line-height: 1.75; }
    .s {
      color: #d0211c;
      font-weight: bold;
      font-family: system-ui, -apple-system, sans-serif;
      cursor: help;
      padding: 0 2px;
      border-radius: 2px;
    }
    .s:hover { background: #fee2e2; }

    /* Ayah Reference Style & Hover */
    .continuation-header {
      margin: 4px 0 8px;
    }
    .c-badge {
      display: inline-flex;
      align-items: center;
      gap: 4px;
      font-size: 0.82rem;
      font-family: 'Tajawal', -apple-system, sans-serif;
      font-weight: 700;
      color: #065f46;
      background: #ecfdf5;
      border: 1px solid #a7f3d0;
      padding: 2px 8px;
      border-radius: 4px;
      cursor: default;
    }
    .a-ref {
      cursor: pointer;
      border-bottom: 1px dotted rgba(16, 185, 129, 0.7);
      transition: all 0.15s ease;
      border-radius: 2px;
      padding: 0 1px;
    }
    .a-ref:hover, .a-ref.active-ayah {
      background-color: #d1fae5;
      color: #065f46;
      border-bottom: 1px solid #059669;
    }

    /* Floating Popover Card */
    .ayah-popover {
      position: absolute;
      z-index: 2000;
      width: 380px;
      max-width: 90vw;
      background: #fffdfa;
      border: 1.5px solid #10b981;
      border-radius: 12px;
      box-shadow: 0 12px 32px rgba(0, 0, 0, 0.22);
      font-family: 'Amiri', 'Traditional Arabic', serif;
      direction: rtl;
      text-align: right;
      overflow: hidden;
      display: none;
      animation: popoverFadeIn 0.2s cubic-bezier(0.16, 1, 0.3, 1);
    }
    @keyframes popoverFadeIn {
      from { opacity: 0; transform: translateY(6px); }
      to { opacity: 1; transform: translateY(0); }
    }
    .popover-header {
      background: #0f766e;
      color: #ffffff;
      padding: 10px 14px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      font-family: 'Tajawal', sans-serif;
      font-size: 0.9rem;
      font-weight: 700;
    }
    .popover-close {
      background: transparent;
      border: none;
      color: #ecfdf5;
      cursor: pointer;
      font-size: 1.1rem;
      line-height: 1;
      padding: 2px 6px;
      border-radius: 4px;
    }
    .popover-close:hover {
      background: rgba(255, 255, 255, 0.2);
    }
    .popover-body {
      padding: 14px 18px;
      max-height: 280px;
      overflow-y: auto;
      font-size: 1.25rem;
      line-height: 2;
      color: #1e293b;
    }
    .popover-ayah-item {
      margin-bottom: 10px;
    }
    .popover-ayah-badge {
      color: #059669;
      font-weight: 700;
      font-size: 1rem;
      margin-left: 6px;
    }
    .popover-alert {
      background: #fefce8;
      border: 1px solid #fef08a;
      color: #854d0e;
      padding: 8px 12px;
      border-radius: 6px;
      font-size: 0.85rem;
      font-family: 'Tajawal', sans-serif;
      margin-top: 8px;
      line-height: 1.5;
    }

    .pink { background: #fce7e0; }
    .pink .title { background: #d9362b; }
    [data-page="26"] .title { background: #2e4a66; }
    [data-page="28"] .title:not(:first-child) { background: #d9362b; }
    .blue { background: #e6eeec; }
    footer.book-page-footer {
      text-align: center;
      font-size: 22px;
      margin-top: 14px;
      font-weight: bold;
      color: #222;
      border-top: 1px dashed #aaa;
      padding-top: 6px;
    }
    body.single-page-mode section { display: none; }
    body.single-page-mode section.active-single { display: block; }

    @media (max-width: 768px) {
      .cols { grid-template-columns: 1fr; }
      .cols > div + div {
        border-right: none;
        border-top: 2px solid #333333;
        margin-top: 16px;
        padding-top: 16px;
      }
      .top-nav { flex-direction: column; align-items: stretch; }
      .nav-controls { justify-content: center; }
    }
    '''

    popover_html = '''
  <!-- Floating Ayah Popover -->
  <div id="ayahPopover" class="ayah-popover">
    <div class="popover-header">
      <span id="popoverTitle">نص الآية الكريمة</span>
      <button class="popover-close" onclick="hidePopover()">✕</button>
    </div>
    <div class="popover-body" id="popoverBody">
      جاري تحميل نص الآية...
    </div>
  </div>
    '''

    js_code_ar = f'''
    let isSingleMode = false;
    let currentIdx = 0;
    const sections = Array.from(document.querySelectorAll('section[data-page]'));
    const pageSelect = document.getElementById('pageSelect');
    const popover = document.getElementById('ayahPopover');
    const popoverTitle = document.getElementById('popoverTitle');
    const popoverBody = document.getElementById('popoverBody');

    let quranCache = null;
    let isFetchingQuran = false;
    let hoverTimeout = null;
    let activeRef = null;

    const surahNamesAr = {json.dumps({k: v["name"] for k, v in SURAHS.items()}, ensure_ascii=False)};
    const surahMaxAyahs = {json.dumps({k: v["total_ayahs"] for k, v in SURAHS.items()})};

    async function loadQuranText() {{
      if (quranCache) return quranCache;
      if (isFetchingQuran) return null;
      isFetchingQuran = true;
      try {{
        const resp = await fetch('data/quran_text_hafs.json');
        const data = await resp.json();
        quranCache = data.ayahs || {{}};
        isFetchingQuran = false;
        return quranCache;
      }} catch (err) {{
        console.warn('Could not load data/quran_text_hafs.json directly.', err);
        isFetchingQuran = false;
        return null;
      }}
    }}

    // Trigger pre-load after page load
    window.addEventListener('load', () => {{
      setTimeout(loadQuranText, 500);
    }});

    function hidePopover() {{
      if (popover) popover.style.display = 'none';
      if (activeRef) {{
        activeRef.classList.remove('active-ayah');
        activeRef = null;
      }}
    }}

    async function showAyahPopover(el) {{
      activeRef = el;
      el.classList.add('active-ayah');

      const s = parseInt(el.getAttribute('data-s'));
      const from = parseInt(el.getAttribute('data-from'));
      const to = parseInt(el.getAttribute('data-to'));

      const sName = surahNamesAr[s] || '';
      const maxA = surahMaxAyahs[s] || 0;

      if (from === to) {{
        popoverTitle.innerText = `سورة ${{sName}} (${{s}}) - الآية ${{from}}`;
      }} else {{
        popoverTitle.innerText = `سورة ${{sName}} (${{s}}) - الآيات ${{from}} إلى ${{to}}`;
      }}

      popoverBody.innerHTML = '<div style="text-align: center; color: #64748b; font-size: 1rem; padding: 10px;">جاري تحميل نص الآية الكريمة...</div>';

      // Position popover
      const rect = el.getBoundingClientRect();
      const scrollX = window.pageXOffset || document.documentElement.scrollLeft;
      const scrollY = window.pageYOffset || document.documentElement.scrollTop;

      let top = rect.bottom + scrollY + 8;
      let left = rect.left + scrollX - 120;

      // Ensure within screen bounds
      if (left < 16) left = 16;
      if (left + 390 > window.innerWidth) left = window.innerWidth - 410;

      popover.style.top = top + 'px';
      popover.style.left = left + 'px';
      popover.style.display = 'block';

      // Load text
      const cache = await loadQuranText();

      // Check misprint anomaly (e.g. PDF Page 25 / Printed Page 24: Surah 77: 78)
      let alertMsg = '';
      if (maxA > 0 && from > maxA) {{
        alertMsg = `<div class="popover-alert">⚠️ <strong>تنبيه توثيقي:</strong> الرقم (${{from}}) خطأ مطبعي في أصل الكتاب الورقي (صفحة PDF رقم ٢٥ / المقابلة لصفحة الكتاب المطبوعة ٢٤)، وسورة ${{sName}} تنتهي عند الآية ${{maxA}}.</div>`;
      }}

      if (!cache) {{
        popoverBody.innerHTML = alertMsg || '<div style="color: #b91c1c; font-size: 0.95rem;">يتطلب عرض نصوص الآيات خادم محلي أو تصفح الموقع عبر GitHub Pages.</div>';
        return;
      }}

      let contentHtml = '';
      for (let a = from; a <= to; a++) {{
        if (a > maxA && maxA > 0) continue;
        const key = `${{s}}:${{a}}`;
        const text = cache[key] || '';
        if (text) {{
          contentHtml += `
            <div class="popover-ayah-item">
              <span class="popover-ayah-badge">﴿${{a}}﴾</span>
              ${{text}}
            </div>
          `;
        }}
      }}

      if (!contentHtml && alertMsg) {{
        contentHtml = alertMsg;
      }} else if (alertMsg) {{
        contentHtml += alertMsg;
      }}

      popoverBody.innerHTML = contentHtml || '<div style="color: #64748b;">لم يتم العثور على نص الآية في قاعدة البيانات.</div>';
    }}

    // Bind event listeners to all .a-ref
    document.querySelectorAll('.a-ref').forEach(el => {{
      el.addEventListener('mouseenter', () => {{
        clearTimeout(hoverTimeout);
        hoverTimeout = setTimeout(() => showAyahPopover(el), 180);
      }});
      el.addEventListener('mouseleave', () => {{
        clearTimeout(hoverTimeout);
      }});
      el.addEventListener('click', (e) => {{
        e.stopPropagation();
        clearTimeout(hoverTimeout);
        showAyahPopover(el);
      }});
    }});

    // Dismiss popover on outside click
    document.addEventListener('click', (e) => {{
      if (popover && !popover.contains(e.target) && !e.target.classList.contains('a-ref')) {{
        hidePopover();
      }}
    }});

    function jumpToSelectedPage() {{
      const pageNum = pageSelect.value;
      const targetSec = document.querySelector(`section[data-page="${{pageNum}}"]`);
      if (targetSec) {{
        if (isSingleMode) {{
          sections.forEach(s => s.classList.remove('active-single'));
          targetSec.classList.add('active-single');
          currentIdx = sections.indexOf(targetSec);
        }} else {{
          targetSec.scrollIntoView({{ behavior: 'smooth', block: 'start' }});
          targetSec.classList.add('highlight-page');
          setTimeout(() => targetSec.classList.remove('highlight-page'), 1500);
          currentIdx = sections.indexOf(targetSec);
        }}
      }}
    }}

    function prevPage() {{
      if (currentIdx > 0) {{
        currentIdx--;
        updateActivePage();
      }}
    }}

    function nextPage() {{
      if (currentIdx < sections.length - 1) {{
        currentIdx++;
        updateActivePage();
      }}
    }}

    function updateActivePage() {{
      const sec = sections[currentIdx];
      const pageNum = sec.getAttribute('data-page');
      pageSelect.value = pageNum;
      jumpToSelectedPage();
    }}

    function toggleViewMode(singleLabel, allLabel) {{
      isSingleMode = !isSingleMode;
      const body = document.body;
      const modeBtn = document.getElementById('modeBtn');
      if (isSingleMode) {{
        body.classList.add('single-page-mode');
        modeBtn.innerText = allLabel;
        sections.forEach((s, idx) => {{
          if (idx === currentIdx) s.classList.add('active-single');
          else s.classList.remove('active-single');
        }});
        window.scrollTo({{ top: 0, behavior: 'smooth' }});
      }} else {{
        body.classList.remove('single-page-mode');
        modeBtn.innerText = singleLabel;
        sections.forEach(s => s.classList.remove('active-single'));
        sections[currentIdx].scrollIntoView({{ behavior: 'smooth' }});
      }}
    }}

    function filterInBook() {{
      const query = document.getElementById('filterInput').value.trim();
      if (!query) return;
      for (let i = 0; i < sections.length; i++) {{
        if (sections[i].innerText.includes(query)) {{
          currentIdx = i;
          pageSelect.value = sections[i].getAttribute('data-page');
          jumpToSelectedPage();
          break;
        }}
      }}
    }}
    '''

    js_code_en = f'''
    let isSingleMode = false;
    let currentIdx = 0;
    const sections = Array.from(document.querySelectorAll('section[data-page]'));
    const pageSelect = document.getElementById('pageSelect');
    const popover = document.getElementById('ayahPopover');
    const popoverTitle = document.getElementById('popoverTitle');
    const popoverBody = document.getElementById('popoverBody');

    let quranCache = null;
    let isFetchingQuran = false;
    let hoverTimeout = null;
    let activeRef = null;

    const surahNamesEn = {json.dumps(SURAH_NAMES_STANDARDIZED)};
    const surahMaxAyahs = {json.dumps({k: v["total_ayahs"] for k, v in SURAHS.items()})};

    async function loadQuranText() {{
      if (quranCache) return quranCache;
      if (isFetchingQuran) return null;
      isFetchingQuran = true;
      try {{
        const resp = await fetch('data/quran_text_hafs.json');
        const data = await resp.json();
        quranCache = data.ayahs || {{}};
        isFetchingQuran = false;
        return quranCache;
      }} catch (err) {{
        console.warn('Could not load data/quran_text_hafs.json directly.', err);
        isFetchingQuran = false;
        return null;
      }}
    }}

    window.addEventListener('load', () => {{
      setTimeout(loadQuranText, 500);
    }});

    function hidePopover() {{
      if (popover) popover.style.display = 'none';
      if (activeRef) {{
        activeRef.classList.remove('active-ayah');
        activeRef = null;
      }}
    }}

    async function showAyahPopover(el) {{
      activeRef = el;
      el.classList.add('active-ayah');

      const s = parseInt(el.getAttribute('data-s'));
      const from = parseInt(el.getAttribute('data-from'));
      const to = parseInt(el.getAttribute('data-to'));

      const sName = surahNamesEn[s] || '';
      const maxA = surahMaxAyahs[s] || 0;

      if (from === to) {{
        popoverTitle.innerText = `Surah ${{sName}} (${{s}}) - Ayah ${{from}}`;
      }} else {{
        popoverTitle.innerText = `Surah ${{sName}} (${{s}}) - Ayahs ${{from}} to ${{to}}`;
      }}

      popoverBody.innerHTML = '<div style="text-align: center; color: #64748b; font-size: 1rem; padding: 10px;">Loading Ayah text...</div>';

      const rect = el.getBoundingClientRect();
      const scrollX = window.pageXOffset || document.documentElement.scrollLeft;
      const scrollY = window.pageYOffset || document.documentElement.scrollTop;

      let top = rect.bottom + scrollY + 8;
      let left = rect.left + scrollX - 120;

      if (left < 16) left = 16;
      if (left + 390 > window.innerWidth) left = window.innerWidth - 410;

      popover.style.top = top + 'px';
      popover.style.left = left + 'px';
      popover.style.display = 'block';

      const cache = await loadQuranText();

      let alertMsg = '';
      if (maxA > 0 && from > maxA) {{
        alertMsg = `<div class="popover-alert">⚠️ <strong>Editorial Note:</strong> Ayah ${{from}} is a printing error in the source book (PDF page 25, matching printed page 24 in the book and HTML); Surah ${{sName}} has only ${{maxA}} ayahs.</div>`;
      }}

      if (!cache) {{
        popoverBody.innerHTML = alertMsg || '<div style="color: #b91c1c; font-size: 0.95rem;">Viewing Ayah text requires a local server or viewing via GitHub Pages.</div>';
        return;
      }}

      let contentHtml = '';
      for (let a = from; a <= to; a++) {{
        if (a > maxA && maxA > 0) continue;
        const key = `${{s}}:${{a}}`;
        const text = cache[key] || '';
        if (text) {{
          contentHtml += `
            <div class="popover-ayah-item">
              <span class="popover-ayah-badge">﴿${{a}}﴾</span>
              ${{text}}
            </div>
          `;
        }}
      }}

      if (!contentHtml && alertMsg) {{
        contentHtml = alertMsg;
      }} else if (alertMsg) {{
        contentHtml += alertMsg;
      }}

      popoverBody.innerHTML = contentHtml || '<div style="color: #64748b;">Ayah text not found in dataset.</div>';
    }}

    document.querySelectorAll('.a-ref').forEach(el => {{
      el.addEventListener('mouseenter', () => {{
        clearTimeout(hoverTimeout);
        hoverTimeout = setTimeout(() => showAyahPopover(el), 180);
      }});
      el.addEventListener('mouseleave', () => {{
        clearTimeout(hoverTimeout);
      }});
      el.addEventListener('click', (e) => {{
        e.stopPropagation();
        clearTimeout(hoverTimeout);
        showAyahPopover(el);
      }});
    }});

    document.addEventListener('click', (e) => {{
      if (popover && !popover.contains(e.target) && !e.target.classList.contains('a-ref')) {{
        hidePopover();
      }}
    }});

    function jumpToSelectedPage() {{
      const pageNum = pageSelect.value;
      const targetSec = document.querySelector(`section[data-page="${{pageNum}}"]`);
      if (targetSec) {{
        if (isSingleMode) {{
          sections.forEach(s => s.classList.remove('active-single'));
          targetSec.classList.add('active-single');
          currentIdx = sections.indexOf(targetSec);
        }} else {{
          targetSec.scrollIntoView({{ behavior: 'smooth', block: 'start' }});
          targetSec.classList.add('highlight-page');
          setTimeout(() => targetSec.classList.remove('highlight-page'), 1500);
          currentIdx = sections.indexOf(targetSec);
        }}
      }}
    }}

    function prevPage() {{
      if (currentIdx > 0) {{
        currentIdx--;
        updateActivePage();
      }}
    }}

    function nextPage() {{
      if (currentIdx < sections.length - 1) {{
        currentIdx++;
        updateActivePage();
      }}
    }}

    function updateActivePage() {{
      const sec = sections[currentIdx];
      const pageNum = sec.getAttribute('data-page');
      pageSelect.value = pageNum;
      jumpToSelectedPage();
    }}

    function toggleViewMode(singleLabel, allLabel) {{
      isSingleMode = !isSingleMode;
      const body = document.body;
      const modeBtn = document.getElementById('modeBtn');
      if (isSingleMode) {{
        body.classList.add('single-page-mode');
        modeBtn.innerText = allLabel;
        sections.forEach((s, idx) => {{
          if (idx === currentIdx) s.classList.add('active-single');
          else s.classList.remove('active-single');
        }});
        window.scrollTo({{ top: 0, behavior: 'smooth' }});
      }} else {{
        body.classList.remove('single-page-mode');
        modeBtn.innerText = singleLabel;
        sections.forEach(s => s.classList.remove('active-single'));
        sections[currentIdx].scrollIntoView({{ behavior: 'smooth' }});
      }}
    }}

    function filterInBook() {{
      const query = document.getElementById('filterInput').value.trim();
      if (!query) return;
      for (let i = 0; i < sections.length; i++) {{
        if (sections[i].innerText.includes(query)) {{
          currentIdx = i;
          pageSelect.value = sections[i].getAttribute('data-page');
          jumpToSelectedPage();
          break;
        }}
      }}
    }}
    '''

    # Build Arabic book.html
    book_html_ar = f'''<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>فهرس مواضيع القرآن الكريم - النسخة المطابقة للأصل الورقي</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Amiri:ital,wght@0,400;0,700;1,400&family=Tajawal:wght@400;500;700;800&display=swap" rel="stylesheet">
  <style>{shared_css}</style>
</head>
<body>
  <nav class="top-nav">
    <div class="nav-brand">
      <a href="index.html">📖 فهرس مواضيع القرآن الكريم</a>
      <span class="nav-badge">النسخة الورقية المطابقة</span>
    </div>

    <div class="nav-controls">
      <a href="book_en.html" class="nav-btn lang" title="Switch to English">🌐 English</a>
      <button class="nav-btn" onclick="prevPage()" title="الصفحة السابقة">◀ السابق</button>
      <select class="nav-select" id="pageSelect" onchange="jumpToSelectedPage()">
        {options_html_ar}
      </select>
      <button class="nav-btn" onclick="nextPage()" title="الصفحة التالية">التالي ▶</button>
      <input type="text" id="filterInput" class="nav-input" placeholder="بحث سريع في الصفحة..." oninput="filterInBook()">
      <button class="nav-btn" id="modeBtn" onclick="toggleViewMode('📖 عرض صفحة مفردة', '📜 عرض متتابع لجميع الصفحات')">📖 عرض صفحة مفردة</button>
    </div>

    <div class="nav-links">
      <a href="index.html" class="nav-btn primary">🔍 الفهرس الرقمي والبحث</a>
      <a href="report.html" class="nav-btn">📊 تقرير المطابقة</a>
      <a href="BOOK_27464_1.pdf" class="nav-btn" download>📥 تحميل PDF</a>
      <a href="data/quran_topics_book.json" class="nav-btn" download>💾 بيانات JSON</a>
    </div>
  </nav>

  <div class="book-container">
    <div class="book-notice">
      <div>
        <span class="notice-title">ملاحظة التوثيق:</span>
        هذه الصفحة مطابقة تماماً لشكل وتوزيع صفحات الكتاب الورقي الأصلي (الصفحات من ٢ إلى ٤٩، المقابلة للترقيم الورقي من ١ إلى ٤٨)، مع الحفاظ على تلوين أرقام السور بالأحمر وأرقام الآيات بالأسود.
        <strong>جديد:</strong> قم بتمرير الفأرة فوق رقم أي آية لقراءة نصها الكريم فورياً بالرسم العثماني.
      </div>
      <div>
        <a href="BOOK_27464_1.pdf" target="_blank" style="color: #047857; font-weight: bold; text-decoration: none;">📄 عرض الكتاب الأصلي PDF (15MB)</a>
      </div>
    </div>

    <main id="bookPages">
      {sections_ar}
    </main>
  </div>

  {popover_html}

  <script>
    {js_code_ar}
  </script>
</body>
</html>
'''
    with open("book.html", "w", encoding="utf-8") as f:
        f.write(book_html_ar)
    print("Saved book.html successfully.")

    # Build English book_en.html
    book_html_en = f'''<!DOCTYPE html>
<html lang="en" dir="ltr">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Quran Thematic Index - Exact Book Replica</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Amiri:ital,wght@0,400;0,700;1,400&family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
  <style>
    {shared_css}
    .top-nav {{
      font-family: 'Inter', -apple-system, sans-serif;
    }}
    .book-notice {{
      font-family: 'Inter', -apple-system, sans-serif;
      border-right: none;
      border-left: 4px solid #10b981;
    }}
    section {{
      direction: rtl;
      text-align: right;
    }}
  </style>
</head>
<body>
  <nav class="top-nav">
    <div class="nav-brand">
      <a href="index_en.html">📖 Quran Thematic Index</a>
      <span class="nav-badge">Book Replica</span>
    </div>

    <div class="nav-controls">
      <a href="book.html" class="nav-btn lang" title="التحويل للغة العربية">🌐 العربية</a>
      <button class="nav-btn" onclick="prevPage()" title="Previous Page">◀ Prev</button>
      <select class="nav-select" id="pageSelect" onchange="jumpToSelectedPage()">
        {options_html_en}
      </select>
      <button class="nav-btn" onclick="nextPage()" title="Next Page">Next ▶</button>
      <input type="text" id="filterInput" class="nav-input" placeholder="Quick search in page..." oninput="filterInBook()">
      <button class="nav-btn" id="modeBtn" onclick="toggleViewMode('📖 Single Page View', '📜 Continuous Scroll View')">📖 Single Page View</button>
    </div>

    <div class="nav-links">
      <a href="index_en.html" class="nav-btn primary">🔍 Digital Index & Search</a>
      <a href="report_en.html" class="nav-btn">📊 Audit Report</a>
      <a href="BOOK_27464_1.pdf" class="nav-btn" download>📥 Download PDF</a>
      <a href="data/quran_topics_book.json" class="nav-btn" download>💾 JSON Data</a>
    </div>
  </nav>

  <div class="book-container">
    <div class="book-notice">
      <div>
        <span class="notice-title">Document Replica Note:</span>
        This reader faithfully reproduces the original 48 printed pages (Pages 2 through 49 of the source PDF, matching printed pages 1 to 48), preserving strict two-column layout, red Surah numbers, and black Ayah ranges.
        <strong>New:</strong> Hover over any Ayah number to view its full canonical script text instantly.
      </div>
      <div>
        <a href="BOOK_27464_1.pdf" target="_blank" style="color: #047857; font-weight: bold; text-decoration: none;">📄 Original PDF (15MB)</a>
      </div>
    </div>

    <main id="bookPages">
      {sections_en}
    </main>
  </div>

  {popover_html}

  <script>
    {js_code_en}
  </script>
</body>
</html>
'''
    with open("book_en.html", "w", encoding="utf-8") as f:
        f.write(book_html_en)
    print("Saved book_en.html successfully.")

if __name__ == "__main__":
    build_book_json_and_html()
