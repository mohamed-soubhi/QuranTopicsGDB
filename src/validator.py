"""Validation engine for extracted Quran topics and verse references.

Enforces strict Hafs/Kufi Quranic constraints and Marqoom naming conventions.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Tuple
from src.quran_metadata import validate_ayah_range, validate_reference, TOTAL_SURAHS


@dataclass
class TopicReference:
    surah_number: int
    ayahs: List[Any]  # Can be int (single ayah) or tuple (start_ayah, end_ayah)


@dataclass
class TopicItem:
    title: str
    level: str  # "major_topic", "section", "topic", "subtopic"
    references: List[TopicReference] = field(default_factory=list)
    page_number: Optional[int] = None
    column: Optional[str] = None  # "right", "left"

    def __post_init__(self):
        if self.title:
            self.title = " ".join(self.title.replace("\\n", " ").replace("\n", " ").split()).strip()


@dataclass
class ValidationReport:
    total_topics: int = 0
    total_references: int = 0
    valid_references: int = 0
    invalid_references: List[Dict[str, Any]] = field(default_factory=list)
    unique_surahs_covered: Set[int] = field(default_factory=set)

    @property
    def is_clean(self) -> bool:
        return len(self.invalid_references) == 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_topics": self.total_topics,
            "total_references": self.total_references,
            "valid_references": self.valid_references,
            "invalid_references_count": len(self.invalid_references),
            "invalid_references": self.invalid_references,
            "unique_surahs_count": len(self.unique_surahs_covered),
            "unique_surahs_covered": sorted(list(self.unique_surahs_covered)),
            "is_clean": self.is_clean,
        }


def validate_topic_item(item: TopicItem, report: Optional[ValidationReport] = None) -> ValidationReport:
    """Validates a single TopicItem and updates or creates a ValidationReport."""
    if report is None:
        report = ValidationReport()

    report.total_topics += 1

    for ref in item.references:
        surah_number = ref.surah_number
        if 1 <= surah_number <= TOTAL_SURAHS:
            report.unique_surahs_covered.add(surah_number)

        for ayah_spec in ref.ayahs:
            report.total_references += 1
            if isinstance(ayah_spec, int):
                is_valid, err = validate_reference(surah_number, ayah_spec)
                if is_valid:
                    report.valid_references += 1
                else:
                    report.invalid_references.append({
                        "topic": item.title,
                        "surah_number": surah_number,
                        "ayah_number": ayah_spec,
                        "error": err,
                        "page": item.page_number,
                        "column": item.column,
                    })
            elif isinstance(ayah_spec, (list, tuple)) and len(ayah_spec) == 2:
                start_ayah, end_ayah = ayah_spec
                is_valid, err = validate_ayah_range(surah_number, int(start_ayah), int(end_ayah))
                if is_valid:
                    report.valid_references += 1
                else:
                    report.invalid_references.append({
                        "topic": item.title,
                        "surah_number": surah_number,
                        "range": [start_ayah, end_ayah],
                        "error": err,
                        "page": item.page_number,
                        "column": item.column,
                    })
            else:
                report.invalid_references.append({
                    "topic": item.title,
                    "surah_number": surah_number,
                    "invalid_ayah_spec": ayah_spec,
                    "error": f"Invalid ayah specification format: {ayah_spec}",
                    "page": item.page_number,
                    "column": item.column,
                })

    return report


def validate_all_topics(items: List[TopicItem]) -> ValidationReport:
    """Validates a list of all extracted topics."""
    report = ValidationReport()
    for item in items:
        validate_topic_item(item, report)
    return report
