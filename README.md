# QuranTopicsGDB (فهرس مواضيع القرآن الكريم)

[![Marqoom Standards Compliant](https://img.shields.io/badge/Marqoom-Compliant-0d9488.svg)](https://github.com/marqoom-specs/quranic-terminology-lint)
[![Release](https://img.shields.io/badge/Release-v1.0.0-16a34a.svg)](https://github.com/mohamed-soubhi/QuranTopicsGDB/releases/tag/v1.0.0)
[![Coverage](https://img.shields.io/badge/Surahs-114%2F114-blue.svg)](#metrics)

Extraction, structured formatting, multi-model comparative audit, and canonical verification of the comprehensive Quranic Subject Index (*فهرس مواضيع القرآن الكريم*), covering 114 Surahs and 6,236 Ayahs.

---

## Release v1.0.0 Highlights

- **Complete Page Coverage:** All 48 index pages (Pages 2 through 49 of `BOOK_27464_1.pdf`).
- **Comprehensive Index:** **1,292 topic entries** and **10,767 ayah citations**.
- **Canonical Quranic Verification:** **99.991% validity** tested against Hafs 'an 'Asim (Kufi: 6,236 Ayahs).
- **Physical Misprints Discovered:** Identified and documented authentic printing errors in the physical source book (e.g., Page 25 Surah 77:78 misprint).
- **Multi-Model Comparative Audit:** Cross-evaluation across **Claude**, **Gemini**, and **Ollama (DeepSeek)**, detailed in [`COMPARISON_REPORT.md`](COMPARISON_REPORT.md).
- **Interactive Visual Report:** Complete audit report available in [`report.html`](report.html).
- **Marqoom Standards Compliance:** Full alignment with Marqoom terminology (`surah_number`, `ayah_number`, `riwayah: hafs_an_asim`), validated by `quranic-data` and `quranic-terminology` pre-commit hooks (0 errors, 0 warnings).

---

## Deliverables & Dataset Structure

| File | Description |
| :--- | :--- |
| **[`data/quran_topics.json`](data/quran_topics.json)** | Golden structured JSON dataset conforming to Marqoom data standards. |
| **[`quran_topics_index.md`](quran_topics_index.md)** | Full Markdown thematic index preserving visual hierarchy and numeric citations. |
| **[`report.html`](report.html)** | Interactive HTML audit report with statistical cards and benchmark tables. |
| **[`COMPARISON_REPORT.md`](COMPARISON_REPORT.md)** | Technical comparison between Claude, Gemini, and Ollama extractions. |
| **[`data/validation_report.json`](data/validation_report.json)** | Complete verification audit trail checking every ayah against surah bounds. |

---

## Setup & Pre-Commit

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pre-commit install
```

## Running Tests & Pre-Commit Linters

```bash
pytest tests/
pre-commit run --all-files
```
