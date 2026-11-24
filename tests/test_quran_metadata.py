"""Unit tests for quran_metadata."""

import pytest
from src.quran_metadata import (
    TOTAL_AYAHS_HAFFS_KUFI,
    TOTAL_SURAHS,
    get_surah_name,
    get_surah_total_ayahs,
    validate_ayah_range,
    validate_reference,
)


def test_totals():
    assert TOTAL_SURAHS == 114
    assert TOTAL_AYAHS_HAFFS_KUFI == 6236


def test_surah_names_and_counts():
    assert get_surah_name(1) == "الفاتحة"
    assert get_surah_total_ayahs(1) == 7

    assert get_surah_name(2) == "البقرة"
    assert get_surah_total_ayahs(2) == 286

    assert get_surah_name(114) == "الناس"
    assert get_surah_total_ayahs(114) == 6


def test_validate_reference_valid():
    is_valid, err = validate_reference(1, 7)
    assert is_valid is True
    assert err is None

    is_valid, err = validate_reference(2, 286)
    assert is_valid is True
    assert err is None


def test_validate_reference_invalid_surah():
    is_valid, err = validate_reference(0, 1)
    assert is_valid is False
    assert "Invalid surah_number 0" in err

    is_valid, err = validate_reference(115, 1)
    assert is_valid is False
    assert "Invalid surah_number 115" in err


def test_validate_reference_invalid_ayah():
    is_valid, err = validate_reference(1, 8)
    assert is_valid is False
    assert "Invalid ayah_number 8 for Surah 1" in err

    is_valid, err = validate_reference(2, 287)
    assert is_valid is False
    assert "Invalid ayah_number 287 for Surah 2" in err


def test_validate_ayah_range():
    is_valid, err = validate_ayah_range(4, 26, 28)
    assert is_valid is True
    assert err is None

    is_valid, err = validate_ayah_range(4, 28, 26)
    assert is_valid is False
    assert "cannot be greater than" in err

    is_valid, err = validate_ayah_range(4, 26, 177)
    assert is_valid is False
    assert "Invalid ayah_number 177" in err
