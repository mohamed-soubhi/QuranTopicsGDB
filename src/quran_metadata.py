"""Canonical Quran metadata and validation helpers.

Follows Marqoom standards for Quranic data and terminology (Hafs 'an 'Asim, Kufi count: 6236 ayahs).
"""

from typing import Dict, List, Optional, Tuple

SURAHS: Dict[int, Dict[str, object]] = {
    1: {"name": "الفاتحة", "total_ayahs": 7},
    2: {"name": "البقرة", "total_ayahs": 286},
    3: {"name": "آل عمران", "total_ayahs": 200},
    4: {"name": "النساء", "total_ayahs": 176},
    5: {"name": "المائدة", "total_ayahs": 120},
    6: {"name": "الأنعام", "total_ayahs": 165},
    7: {"name": "الأعراف", "total_ayahs": 206},
    8: {"name": "الأنفال", "total_ayahs": 75},
    9: {"name": "التوبة", "total_ayahs": 129},
    10: {"name": "يونس", "total_ayahs": 109},
    11: {"name": "هود", "total_ayahs": 123},
    12: {"name": "يوسف", "total_ayahs": 111},
    13: {"name": "الرعد", "total_ayahs": 43},
    14: {"name": "إبراهيم", "total_ayahs": 52},
    15: {"name": "الحجر", "total_ayahs": 99},
    16: {"name": "النحل", "total_ayahs": 128},
    17: {"name": "الإسراء", "total_ayahs": 111},
    18: {"name": "الكهف", "total_ayahs": 110},
    19: {"name": "مريم", "total_ayahs": 98},
    20: {"name": "طه", "total_ayahs": 135},
    21: {"name": "الأنبياء", "total_ayahs": 112},
    22: {"name": "الحج", "total_ayahs": 78},
    23: {"name": "المؤمنون", "total_ayahs": 118},
    24: {"name": "النور", "total_ayahs": 64},
    25: {"name": "الفرقان", "total_ayahs": 77},
    26: {"name": "الشعراء", "total_ayahs": 227},
    27: {"name": "النمل", "total_ayahs": 93},
    28: {"name": "القصص", "total_ayahs": 88},
    29: {"name": "العنكبوت", "total_ayahs": 69},
    30: {"name": "الروم", "total_ayahs": 60},
    31: {"name": "لقمان", "total_ayahs": 34},
    32: {"name": "السجدة", "total_ayahs": 30},
    33: {"name": "الأحزاب", "total_ayahs": 73},
    34: {"name": "سبأ", "total_ayahs": 54},
    35: {"name": "فاطر", "total_ayahs": 45},
    36: {"name": "يس", "total_ayahs": 83},
    37: {"name": "الصافات", "total_ayahs": 182},
    38: {"name": "ص", "total_ayahs": 88},
    39: {"name": "الزمر", "total_ayahs": 75},
    40: {"name": "غافر", "total_ayahs": 85},
    41: {"name": "فصلت", "total_ayahs": 54},
    42: {"name": "الشورى", "total_ayahs": 53},
    43: {"name": "الزخرف", "total_ayahs": 89},
    44: {"name": "الدخان", "total_ayahs": 59},
    45: {"name": "الجاثية", "total_ayahs": 37},
    46: {"name": "الأحقاف", "total_ayahs": 35},
    47: {"name": "محمد", "total_ayahs": 38},
    48: {"name": "الفتح", "total_ayahs": 29},
    49: {"name": "الحجرات", "total_ayahs": 18},
    50: {"name": "ق", "total_ayahs": 45},
    51: {"name": "الذاريات", "total_ayahs": 60},
    52: {"name": "الطور", "total_ayahs": 49},
    53: {"name": "النجم", "total_ayahs": 62},
    54: {"name": "القمر", "total_ayahs": 55},
    55: {"name": "الرحمن", "total_ayahs": 78},
    56: {"name": "الواقعة", "total_ayahs": 96},
    57: {"name": "الحديد", "total_ayahs": 29},
    58: {"name": "المجادلة", "total_ayahs": 22},
    59: {"name": "الحشر", "total_ayahs": 24},
    60: {"name": "الممتحنة", "total_ayahs": 13},
    61: {"name": "الصف", "total_ayahs": 14},
    62: {"name": "الجمعة", "total_ayahs": 11},
    63: {"name": "المنافقون", "total_ayahs": 11},
    64: {"name": "التغابن", "total_ayahs": 18},
    65: {"name": "الطلاق", "total_ayahs": 12},
    66: {"name": "التحريم", "total_ayahs": 12},
    67: {"name": "الملك", "total_ayahs": 30},
    68: {"name": "القلم", "total_ayahs": 52},
    69: {"name": "الحاقة", "total_ayahs": 52},
    70: {"name": "المعارج", "total_ayahs": 44},
    71: {"name": "نوح", "total_ayahs": 28},
    72: {"name": "الجن", "total_ayahs": 28},
    73: {"name": "المزمل", "total_ayahs": 20},
    74: {"name": "المدثر", "total_ayahs": 56},
    75: {"name": "القيامة", "total_ayahs": 40},
    76: {"name": "الإنسان", "total_ayahs": 31},
    77: {"name": "المرسلات", "total_ayahs": 50},
    78: {"name": "النبأ", "total_ayahs": 40},
    79: {"name": "النازعات", "total_ayahs": 46},
    80: {"name": "عبس", "total_ayahs": 42},
    81: {"name": "التكوير", "total_ayahs": 29},
    82: {"name": "الانفطار", "total_ayahs": 19},
    83: {"name": "المطففين", "total_ayahs": 36},
    84: {"name": "الانشقاق", "total_ayahs": 25},
    85: {"name": "البروج", "total_ayahs": 22},
    86: {"name": "الطارق", "total_ayahs": 17},
    87: {"name": "الأعلى", "total_ayahs": 19},
    88: {"name": "الغاشية", "total_ayahs": 26},
    89: {"name": "الفجر", "total_ayahs": 30},
    90: {"name": "البلد", "total_ayahs": 20},
    91: {"name": "الشمس", "total_ayahs": 15},
    92: {"name": "الليل", "total_ayahs": 21},
    93: {"name": "الضحى", "total_ayahs": 11},
    94: {"name": "الشرح", "total_ayahs": 8},
    95: {"name": "التين", "total_ayahs": 8},
    96: {"name": "العلق", "total_ayahs": 19},
    97: {"name": "القدر", "total_ayahs": 5},
    98: {"name": "البينة", "total_ayahs": 8},
    99: {"name": "الزلزلة", "total_ayahs": 8},
    100: {"name": "العاديات", "total_ayahs": 11},
    101: {"name": "القارعة", "total_ayahs": 11},
    102: {"name": "التكاثر", "total_ayahs": 8},
    103: {"name": "العصر", "total_ayahs": 3},
    104: {"name": "الهمزة", "total_ayahs": 9},
    105: {"name": "الفيل", "total_ayahs": 5},
    106: {"name": "قريش", "total_ayahs": 4},
    107: {"name": "الماعون", "total_ayahs": 7},
    108: {"name": "الكوثر", "total_ayahs": 3},
    109: {"name": "الكافرون", "total_ayahs": 6},
    110: {"name": "النصر", "total_ayahs": 3},
    111: {"name": "المسد", "total_ayahs": 5},
    112: {"name": "الإخلاص", "total_ayahs": 4},
    113: {"name": "الفلق", "total_ayahs": 5},
    114: {"name": "الناس", "total_ayahs": 6},
}

TOTAL_SURAHS = 114
TOTAL_AYAHS_HAFFS_KUFI = sum(s["total_ayahs"] for s in SURAHS.values())  # 6236


def get_surah_name(surah_number: int) -> Optional[str]:
    surah = SURAHS.get(surah_number)
    return str(surah["name"]) if surah else None


def get_surah_total_ayahs(surah_number: int) -> Optional[int]:
    surah = SURAHS.get(surah_number)
    return int(surah["total_ayahs"]) if surah else None


def validate_reference(surah_number: int, ayah_number: int) -> Tuple[bool, Optional[str]]:
    """Validate a single surah and ayah reference."""
    if surah_number < 1 or surah_number > TOTAL_SURAHS:
        return False, f"Invalid surah_number {surah_number}. Must be between 1 and {TOTAL_SURAHS}."
    max_ayahs = get_surah_total_ayahs(surah_number)
    if ayah_number < 1 or (max_ayahs is not None and ayah_number > max_ayahs):
        surah_name = get_surah_name(surah_number)
        return False, f"Invalid ayah_number {ayah_number} for Surah {surah_number} ({surah_name}). Max is {max_ayahs}."
    return True, None


def validate_ayah_range(surah_number: int, start_ayah: int, end_ayah: int) -> Tuple[bool, Optional[str]]:
    """Validate a range of ayahs within a surah."""
    if start_ayah > end_ayah:
        return False, f"Range start ({start_ayah}) cannot be greater than range end ({end_ayah})."
    valid_start, err_start = validate_reference(surah_number, start_ayah)
    if not valid_start:
        return False, err_start
    valid_end, err_end = validate_reference(surah_number, end_ayah)
    if not valid_end:
        return False, err_end
    return True, None
