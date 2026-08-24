"""TV1: validation shared by the NumPy implementations (no image algorithms)."""

import numpy as np


def gray_image(image):
    """Return a nonempty, finite 2-D uint8 grayscale image; reject invalid input."""
    arr = np.asarray(image)
    if arr.ndim != 2 or not arr.size or not np.isfinite(arr).all():
        raise ValueError("Expected a nonempty finite 2-D grayscale image")
    if np.any(arr < 0) or np.any(arr > 255):
        raise ValueError("Image intensities must be in [0, 255]")
    return arr.astype(np.uint8)


def odd_window(size):
    """Reject fractional, even, or nonpositive neighborhood sizes."""
    if int(size) != size or size < 1 or size % 2 != 1:
        raise ValueError("Window size must be a positive odd integer")


def positive(value, name):
    """Require a finite positive real parameter."""
    if not np.isfinite(value) or value <= 0:
        raise ValueError(f"{name} must be finite and positive")
