"""Tests for page_preprocessor module."""

import os
import pytest
from src.page_preprocessor import (
    extract_page_image,
    find_column_boundaries,
    slice_page_columns,
    get_color_masks,
)

PDF_PATH = "BOOK_27464_1.pdf"


@pytest.mark.skipif(not os.path.exists(PDF_PATH), reason="PDF file not found")
def test_extract_page_image():
    img = extract_page_image(PDF_PATH, 2)
    assert img is not None
    assert img.width > 500
    assert img.height > 500


@pytest.mark.skipif(not os.path.exists(PDF_PATH), reason="PDF file not found")
def test_slice_page_columns():
    img = extract_page_image(PDF_PATH, 2)
    left_x, mid_x, right_x, top_y, bottom_y = find_column_boundaries(img)

    assert left_x < mid_x < right_x
    assert top_y < bottom_y

    col_right, col_left = slice_page_columns(img)
    assert col_right.width > 0 and col_right.height > 0
    assert col_left.width > 0 and col_left.height > 0


@pytest.mark.skipif(not os.path.exists(PDF_PATH), reason="PDF file not found")
def test_get_color_masks():
    img = extract_page_image(PDF_PATH, 2)
    col_right, _ = slice_page_columns(img)
    red_mask, black_mask = get_color_masks(col_right)

    assert red_mask.shape == (col_right.height, col_right.width)
    assert black_mask.shape == (col_right.height, col_right.width)
    # Both masks should detect pixels
    assert red_mask.sum() > 500
    assert black_mask.sum() > 500
