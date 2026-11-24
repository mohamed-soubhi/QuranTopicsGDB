# QuranTopicsGDB (فهرس مواضيع القرآن الكريم)

Extraction, structured formatting, and canonical verification of the comprehensive Quranic Subject Index (*فهرس مواضيع القرآن الكريم*), covering 114 Surahs and 6,236 Ayahs.

## Project Scope
- Extraction of scanned thematic index pages (Pages 2 through 49 of the source index book).
- Strict dual-channel parsing:
  - **Surah numbers** (printed in Red Western numerals).
  - **Ayah numbers and ranges** (printed in Black numerals).
  - Arabic topic and subtopic hierarchy.
- **Marqoom Standards Compliance:**
  - Standardized terminology (`surah`, `ayah`, `surah_number`, `ayah_number`).
  - Standardized data metadata specification (`riwayah: hafs-kufi`, canonical verse counts).
  - Integrated with `marqoom-specs/quranic-terminology-lint` pre-commit hooks (`quranic-data`, `quranic-terminology`).

## Setup & Pre-Commit
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pre-commit install
```

## Running Tests & Pre-commit
```bash
pytest
pre-commit run --all-files
```
