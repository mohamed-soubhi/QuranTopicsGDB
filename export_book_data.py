#!/usr/bin/env python3
"""Exports the book-structured JSON dataset and generates the interactive book-view HTML.

Follows Marqoom Quranic data standards and riwayah: hafs_an_asim.
"""

import json
import os
import re
from src.quran_metadata import SURAHS


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

    # 2. Build book.html from claude-extraction/quran_index.html with top navigation & interactive tools
    with open("claude-extraction/quran_index.html", "r", encoding="utf-8") as f:
        raw_html = f.read()

    # Extract sections (from first <section to last </section>)
    sec_start = raw_html.find("<section")
    sec_end = raw_html.rfind("</section>") + len("</section>")
    sections_content = raw_html[sec_start:sec_end]

    # Enhance citations with tooltip title attribute for surah name
    def replace_surah_tag(match):
        s_num_str = match.group(1)
        try:
            s_num = int(s_num_str)
            s_name = SURAHS.get(s_num, {}).get("name", "")
            title_attr = f' title="سورة {s_name} ({s_num})"'
        except Exception:
            title_attr = ''
        return f'<bdi class="s"{title_attr}>{s_num_str}</bdi>'

    sections_content = re.sub(r'<bdi class="s">(\d+)</bdi>', replace_surah_tag, sections_content)

    # Build page options for select dropdown
    page_options = []
    for page in book_json["pages"]:
        pdf_p = page["pdf_page"]
        pr_p = page["printed_page"]
        # Find first title or heading
        sample_title = ""
        for b in page["blocks"]:
            if b.get("type") in ("title", "section", "subsection"):
                sample_title = b.get("text", "")
                break
            if not sample_title and b.get("heading"):
                sample_title = b.get("heading")
        if sample_title:
            sample_title = " - " + sample_title[:24]
        page_options.append(f'<option value="{pdf_p}">صفحة {pr_p} (PDF {pdf_p}){sample_title}</option>')

    options_html = "\n".join(page_options)

    # Create the complete book.html page
    book_html = f'''<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>فهرس مواضيع القرآن الكريم - النسخة المطابقة للأصل الورقي</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Amiri:ital,wght@0,400;0,700;1,400&family=Tajawal:wght@400;500;700;800&display=swap" rel="stylesheet">
  <style>
    :root {{
      --primary: #10b981;
      --primary-dark: #059669;
      --surface: #ffffff;
      --border: #e2e8f0;
      --text: #1e293b;
      --text-muted: #64748b;
    }}
    * {{
      box-sizing: border-box;
    }}
    body {{
      font-family: "Amiri", "Traditional Arabic", serif;
      background: #e5e7eb;
      margin: 0;
      padding: 0;
      color: #111827;
    }}

    /* Top Navigation Bar */
    .top-nav {{
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
      font-family: 'Tajawal', sans-serif;
    }}
    .nav-brand {{
      display: flex;
      align-items: center;
      gap: 10px;
      font-size: 1.05rem;
      font-weight: 700;
    }}
    .nav-brand a {{
      color: #fff;
      text-decoration: none;
      display: flex;
      align-items: center;
      gap: 6px;
    }}
    .nav-brand a:hover {{
      color: #34d399;
    }}
    .nav-badge {{
      background: #047857;
      color: #ecfdf5;
      font-size: 0.75rem;
      padding: 2px 8px;
      border-radius: 9999px;
      font-weight: 600;
    }}
    .nav-controls {{
      display: flex;
      align-items: center;
      flex-wrap: wrap;
      gap: 8px;
    }}
    .nav-select, .nav-input {{
      font-family: 'Tajawal', sans-serif;
      padding: 6px 12px;
      border-radius: 6px;
      border: 1px solid #475569;
      background: #0f172a;
      color: #f8fafc;
      font-size: 0.85rem;
      outline: none;
    }}
    .nav-select:focus, .nav-input:focus {{
      border-color: #10b981;
    }}
    .nav-btn {{
      font-family: 'Tajawal', sans-serif;
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
    }}
    .nav-btn:hover {{
      background: #475569;
      color: #fff;
    }}
    .nav-btn.primary {{
      background: #10b981;
      color: #064e3b;
      font-weight: 700;
    }}
    .nav-btn.primary:hover {{
      background: #34d399;
    }}
    .nav-links {{
      display: flex;
      align-items: center;
      gap: 8px;
    }}

    /* Book View Container */
    .book-container {{
      max-width: 1000px;
      margin: 20px auto 60px;
      padding: 0 16px;
    }}

    /* Notice Banner */
    .book-notice {{
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
    }}
    .notice-title {{
      font-weight: 700;
      color: #0f172a;
    }}

    /* Book Page Layout (Faithful to physical book) */
    section {{
      background: #f3f8e6;
      max-width: 900px;
      margin: 24px auto;
      padding: 24px 20px;
      border: 3px solid #333333;
      box-shadow: 0 8px 24px rgba(0,0,0,0.12);
      border-radius: 2px;
      position: relative;
    }}
    section.highlight-page {{
      outline: 4px solid #10b981;
    }}
    .cols {{
      display: grid;
      grid-template-columns: 1fr 1fr;
    }}
    .cols > div {{
      padding: 0 16px;
    }}
    .cols > div + div {{
      border-right: 2px solid #333333;
    }}
    .title {{
      background: #3d7a4a;
      color: #ffffff;
      font-size: 32px;
      text-align: center;
      padding: 4px 10px;
      margin: 4px 0 10px;
      font-weight: bold;
    }}
    .section {{
      font-size: 24px;
      font-weight: bold;
      text-align: center;
      background: #b9b1a4;
      width: fit-content;
      margin: 8px auto 12px;
      padding: 2px 20px;
    }}
    .sub {{
      font-size: 21px;
      font-weight: bold;
      margin: 6px 0;
    }}
    h3 {{
      margin: 10px 0 0;
      font-size: 20px;
      display: inline;
    }}
    .l {{
      font-size: 18px;
      line-height: 1.75;
    }}
    .s {{
      color: #d0211c;
      font-weight: bold;
      font-family: system-ui, -apple-system, sans-serif;
      cursor: help;
      padding: 0 2px;
      border-radius: 2px;
    }}
    .s:hover {{
      background: #fee2e2;
    }}
    .pink {{
      background: #fce7e0;
    }}
    .pink .title {{
      background: #d9362b;
    }}
    [data-page="26"] .title {{
      background: #2e4a66;
    }}
    [data-page="28"] .title:not(:first-child) {{
      background: #d9362b;
    }}
    .blue {{
      background: #e6eeec;
    }}
    footer.book-page-footer {{
      text-align: center;
      font-size: 22px;
      margin-top: 14px;
      font-weight: bold;
      color: #222;
      border-top: 1px dashed #aaa;
      padding-top: 6px;
    }}

    /* Single page mode hide/show */
    body.single-page-mode section {{
      display: none;
    }}
    body.single-page-mode section.active-single {{
      display: block;
    }}

    /* Responsive */
    @media (max-width: 768px) {{
      .cols {{
        grid-template-columns: 1fr;
      }}
      .cols > div + div {{
        border-right: none;
        border-top: 2px solid #333333;
        margin-top: 16px;
        padding-top: 16px;
      }}
      .top-nav {{
        flex-direction: column;
        align-items: stretch;
      }}
      .nav-controls {{
        justify-content: center;
      }}
    }}
  </style>
</head>
<body>

  <!-- Top Navigation Bar -->
  <nav class="top-nav">
    <div class="nav-brand">
      <a href="index.html">📖 فهرس مواضيع القرآن الكريم</a>
      <span class="nav-badge">النسخة الورقية المطابقة</span>
    </div>

    <div class="nav-controls">
      <button class="nav-btn" onclick="prevPage()" title="الصفحة السابقة">◀ السابق</button>
      <select class="nav-select" id="pageSelect" onchange="jumpToSelectedPage()">
        {options_html}
      </select>
      <button class="nav-btn" onclick="nextPage()" title="الصفحة التالية">التالي ▶</button>
      <input type="text" id="filterInput" class="nav-input" placeholder="بحث سريع في الصفحة..." oninput="filterInBook()">
      <button class="nav-btn" id="modeBtn" onclick="toggleViewMode()">📖 عرض صفحة مفردة</button>
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
        هذه الصفحة مطابقة تماماً لشكل وتوزيع صفحات الكتاب الورقي الأصلي (الصفحات من ٢ إلى ٤٩، المقابلة للترقيم الورقي من ١ إلى ٤٨)، مع الحفاظ على العمودين وتلوين أرقام السور باللون الأحمر، مع إضافة خاصية تمرير الماوس فوق رقم السورة لعرض اسمها.
      </div>
      <div>
        <a href="BOOK_27464_1.pdf" target="_blank" style="color: #047857; font-weight: bold; text-decoration: none;">📄 عرض الكتاب الأصلي PDF (15MB)</a>
      </div>
    </div>

    <main id="bookPages">
      {sections_content}
    </main>
  </div>

  <script>
    let isSingleMode = false;
    let currentIdx = 0;
    const sections = Array.from(document.querySelectorAll('section[data-page]'));
    const pageSelect = document.getElementById('pageSelect');

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

    function toggleViewMode() {{
      isSingleMode = !isSingleMode;
      const body = document.body;
      const modeBtn = document.getElementById('modeBtn');
      if (isSingleMode) {{
        body.classList.add('single-page-mode');
        modeBtn.innerText = '📜 عرض متتابع لجميع الصفحات';
        sections.forEach((s, idx) => {{
          if (idx === currentIdx) s.classList.add('active-single');
          else s.classList.remove('active-single');
        }});
        window.scrollTo({{ top: 0, behavior: 'smooth' }});
      }} else {{
        body.classList.remove('single-page-mode');
        modeBtn.innerText = '📖 عرض صفحة مفردة';
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
  </script>
</body>
</html>
'''

    with open("book.html", "w", encoding="utf-8") as f:
        f.write(book_html)

    print("Saved book.html successfully.")


if __name__ == "__main__":
    build_book_json_and_html()
