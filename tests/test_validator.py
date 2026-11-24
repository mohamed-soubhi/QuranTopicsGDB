"""Tests for validator module."""

from src.validator import (
    TopicItem,
    TopicReference,
    validate_all_topics,
    validate_topic_item,
)


def test_validator_clean_entry():
    item = TopicItem(
        title="إرادته",
        level="subtopic",
        references=[
            TopicReference(surah_number=2, ayahs=[117, 185, 253]),
            TopicReference(surah_number=4, ayahs=[(26, 28)]),
        ],
        page_number=2,
        column="right",
    )

    report = validate_topic_item(item)
    assert report.total_topics == 1
    assert report.total_references == 4  # 3 single ayahs + 1 range
    assert report.valid_references == 4
    assert report.is_clean is True
    assert report.unique_surahs_covered == {2, 4}


def test_validator_detects_invalid_ayah():
    item = TopicItem(
        title="اختبار خطأ في الآية",
        level="subtopic",
        references=[
            TopicReference(surah_number=1, ayahs=[8]),  # Fatihah only has 7 ayahs
        ],
        page_number=5,
        column="left",
    )

    report = validate_topic_item(item)
    assert report.total_references == 1
    assert report.valid_references == 0
    assert report.is_clean is False
    assert len(report.invalid_references) == 1
    assert "Invalid ayah_number 8 for Surah 1" in report.invalid_references[0]["error"]


def test_validator_detects_invalid_surah():
    item = TopicItem(
        title="اختبار سورة غير موجودة",
        level="subtopic",
        references=[
            TopicReference(surah_number=115, ayahs=[1]),
        ],
    )

    report = validate_topic_item(item)
    assert report.is_clean is False
    assert len(report.invalid_references) == 1
    assert "Invalid surah_number 115" in report.invalid_references[0]["error"]


def test_validator_detects_invalid_range():
    item = TopicItem(
        title="اختبار نطاق مقلوب",
        level="subtopic",
        references=[
            TopicReference(surah_number=2, ayahs=[(50, 40)]),
        ],
    )

    report = validate_topic_item(item)
    assert report.is_clean is False
    assert "cannot be greater than" in report.invalid_references[0]["error"]


def test_validate_all_topics():
    items = [
        TopicItem(title="موضوع 1", level="topic", references=[TopicReference(surah_number=2, ayahs=[1])]),
        TopicItem(title="موضوع 2", level="topic", references=[TopicReference(surah_number=3, ayahs=[10, 20])]),
    ]
    report = validate_all_topics(items)
    assert report.total_topics == 2
    assert report.total_references == 3
    assert report.valid_references == 3
    assert report.is_clean is True
    assert report.unique_surahs_covered == {2, 3}
