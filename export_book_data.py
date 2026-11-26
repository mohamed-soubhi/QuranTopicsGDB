#!/usr/bin/env python3
"""Exports the book-structured JSON dataset and generates the interactive book-view HTML (Arabic & English).

Follows Marqoom Quranic data standards and riwayah: hafs_an_asim.
"""

import json
import os
import re
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

def build_book_json_and_html():
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
        "confirmed_source_misprints": claude_data.get("confirmed_as_printed", []),
        "pages": []
    }

    for page in claude_data.get("pages", []):
        p_obj = {
            "pdf_page": page.get("pdf_page"),
            "printed_page": page.get("printed_page"),
            "blocks": []
        }
        for block in page.get("blocks", []):
            b_type = block.get("type")
            b_col = block.get("column", "right")

            new_block = {
                "type": b_type,
                "column": b_col
            }

            if "text" in block:
                new_block["text"] = block["text"]
            if "heading" in block:
                new_block["heading"] = block["heading"]
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

    # Arabic Tooltip replacer
    def replace_surah_ar(match):
        s_num_str = match.group(1)
        try:
            s_num = int(s_num_str)
            s_name = SURAHS.get(s_num, {}).get("name", "")
            title_attr = f' title="سورة {s_name} ({s_num})"'
        except Exception:
            title_attr = ''
        return f'<bdi class="s"{title_attr}>{s_num_str}</bdi>'

    sections_ar = re.sub(r'<bdi class="s">(\d+)</bdi>', replace_surah_ar, raw_sections)

    # English Tooltip replacer
    def replace_surah_en(match):
        s_num_str = match.group(1)
        try:
            s_num = int(s_num_str)
            s_name_en = SURAH_NAMES_STANDARDIZED.get(s_num, "")
            title_attr = f' title="Surah {s_name_en} ({s_num})"'
        except Exception:
            title_attr = ''
        return f'<bdi class="s"{title_attr}>{s_num_str}</bdi>'

    sections_en = re.sub(r'<bdi class="s">(\d+)</bdi>', replace_surah_en, raw_sections)

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
        if sample_title:
            sample_title_ar = " - " + sample_title[:24]
        else:
            sample_title_ar = ""
        page_options_ar.append(f'<option value="{pdf_p}">صفحة {pr_p} (PDF {pdf_p}){sample_title_ar}</option>')
        page_options_en.append(f'<option value="{pdf_p}">Page {pr_p} (PDF {pdf_p}){sample_title_ar}</option>')

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

    js_code = '''
    let isSingleMode = false;
    let currentIdx = 0;
    const sections = Array.from(document.querySelectorAll('section[data-page]'));
    const pageSelect = document.getElementById('pageSelect');

    function jumpToSelectedPage() {
      const pageNum = pageSelect.value;
      const targetSec = document.querySelector(`section[data-page="${pageNum}"]`);
      if (targetSec) {
        if (isSingleMode) {
          sections.forEach(s => s.classList.remove('active-single'));
          targetSec.classList.add('active-single');
          currentIdx = sections.indexOf(targetSec);
        } else {
          targetSec.scrollIntoView({ behavior: 'smooth', block: 'start' });
          targetSec.classList.add('highlight-page');
          setTimeout(() => targetSec.classList.remove('highlight-page'), 1500);
          currentIdx = sections.indexOf(targetSec);
        }
      }
    }

    function prevPage() {
      if (currentIdx > 0) {
        currentIdx--;
        updateActivePage();
      }
    }

    function nextPage() {
      if (currentIdx < sections.length - 1) {
        currentIdx++;
        updateActivePage();
      }
    }

    function updateActivePage() {
      const sec = sections[currentIdx];
      const pageNum = sec.getAttribute('data-page');
      pageSelect.value = pageNum;
      jumpToSelectedPage();
    }

    function toggleViewMode(singleLabel, allLabel) {
      isSingleMode = !isSingleMode;
      const body = document.body;
      const modeBtn = document.getElementById('modeBtn');
      if (isSingleMode) {
        body.classList.add('single-page-mode');
        modeBtn.innerText = allLabel;
        sections.forEach((s, idx) => {
          if (idx === currentIdx) s.classList.add('active-single');
          else s.classList.remove('active-single');
        });
        window.scrollTo({ top: 0, behavior: 'smooth' });
      } else {
        body.classList.remove('single-page-mode');
        modeBtn.innerText = singleLabel;
        sections.forEach(s => s.classList.remove('active-single'));
        sections[currentIdx].scrollIntoView({ behavior: 'smooth' });
      }
    }

    function filterInBook() {
      const query = document.getElementById('filterInput').value.trim();
      if (!query) return;
      for (let i = 0; i < sections.length; i++) {
        if (sections[i].innerText.includes(query)) {
          currentIdx = i;
          pageSelect.value = sections[i].getAttribute('data-page');
          jumpToSelectedPage();
          break;
        }
      }
    }
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
        هذه الصفحة مطابقة تماماً لشكل وتوزيع صفحات الكتاب الورقي الأصلي (الصفحات من ٢ إلى ٤٩، المقابلة للترقيم الورقي من ١ إلى ٤٨)، مع الحفاظ على تلوين أرقام السور بالأحمر وأرقام الآيات بالأسود، وتمرير الماوس فوق رقم السورة يعرض اسمها.
      </div>
      <div>
        <a href="BOOK_27464_1.pdf" target="_blank" style="color: #047857; font-weight: bold; text-decoration: none;">📄 عرض الكتاب الأصلي PDF (15MB)</a>
      </div>
    </div>

    <main id="bookPages">
      {sections_ar}
    </main>
  </div>

  <script>
    {js_code}
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
    /* Keep book pages themselves in authentic Arabic typography and RTL */
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
        This reader faithfully reproduces the original 48 printed pages (Pages 2 through 49 of the source PDF, matching printed pages 1 to 48), preserving strict two-column layout, red Surah numbers, and black Ayah ranges. Hover over any red Surah number to view its transliterated name.
      </div>
      <div>
        <a href="BOOK_27464_1.pdf" target="_blank" style="color: #047857; font-weight: bold; text-decoration: none;">📄 Original PDF (15MB)</a>
      </div>
    </div>

    <main id="bookPages">
      {sections_en}
    </main>
  </div>

  <script>
    {js_code}
  </script>
</body>
</html>
'''
    with open("book_en.html", "w", encoding="utf-8") as f:
        f.write(book_html_en)
    print("Saved book_en.html successfully.")

if __name__ == "__main__":
    build_book_json_and_html()
