"""Page preprocessing and column slicing for BOOK_27464_1.pdf."""

from typing import Tuple, Optional
import numpy as np
from PIL import Image
import pypdf


def extract_page_image(pdf_path: str, page_number_1_based: int) -> Image.Image:
    """Extract full page PIL Image from PDF (1-based page number)."""
    reader = pypdf.PdfReader(pdf_path)
    page = reader.pages[page_number_1_based - 1]
    if not page.images:
        raise ValueError(f"No image found on page {page_number_1_based}")
    return page.images[0].image


def find_column_boundaries(image: Image.Image) -> Tuple[int, int, int, int, int]:
    """Finds left_border, divider_x, right_border, top_border, bottom_border."""
    arr = np.array(image.convert("L"))
    h, w = arr.shape

    # Horizontal slice to find vertical lines
    col_avg = np.mean(arr[int(h * 0.15) : int(h * 0.85), :], axis=0)

    # Divider line around the middle (between 45% and 55% of width)
    mid_start = int(w * 0.45)
    mid_end = int(w * 0.58)
    divider_x = mid_start + int(np.argmin(col_avg[mid_start:mid_end]))

    # Outer left and right borders
    left_start = int(w * 0.05)
    left_end = int(w * 0.15)
    left_border = left_start + int(np.argmin(col_avg[left_start:left_end]))

    right_start = int(w * 0.85)
    right_end = int(w * 0.98)
    right_border = right_start + int(np.argmin(col_avg[right_start:right_end]))

    # Vertical slice to find top and bottom frame borders
    row_avg = np.mean(arr[:, left_border:right_border], axis=1)
    top_start = int(h * 0.02)
    top_end = int(h * 0.08)
    top_border = top_start + int(np.argmin(row_avg[top_start:top_end]))

    bottom_start = int(h * 0.90)
    bottom_end = int(h * 0.98)
    bottom_border = bottom_start + int(np.argmin(row_avg[bottom_start:bottom_end]))

    return left_border, divider_x, right_border, top_border, bottom_border


def slice_page_columns(image: Image.Image) -> Tuple[Image.Image, Image.Image]:
    """Slices a page into (right_column, left_column).

    In Arabic RTL layout, the right column is read first.
    """
    left_x, mid_x, right_x, top_y, bottom_y = find_column_boundaries(image)

    # Right column (from divider to right border)
    # Add slight 2-pixel margin inside borders to eliminate outer frame lines
    col_right = image.crop((mid_x + 2, top_y + 2, right_x - 2, bottom_y - 2))

    # Left column (from left border to divider)
    col_left = image.crop((left_x + 2, top_y + 2, mid_x - 2, bottom_y - 2))

    return col_right, col_left


def get_color_masks(image: Image.Image) -> Tuple[np.ndarray, np.ndarray]:
    """Returns boolean masks (red_mask, black_mask) for Surah and Ayah separation."""
    arr = np.array(image.convert("RGB"))

    # Red mask: red channel significantly stronger than green and blue
    r = arr[:, :, 0].astype(int)
    g = arr[:, :, 1].astype(int)
    b = arr[:, :, 2].astype(int)

    red_mask = (r > 100) & (r > g + 30) & (r > b + 30)
    black_mask = (r < 90) & (g < 90) & (b < 90)

    return red_mask, black_mask
