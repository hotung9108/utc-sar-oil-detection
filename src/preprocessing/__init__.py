"""
Preprocessing module for SAR oil spill detection.
Pure NumPy implementations by TV3.
"""

from .numpy_filters import custom_median_filter, custom_mean_filter
from .numpy_otsu import custom_otsu_threshold, compute_otsu_statistics

__all__ = [
    "custom_median_filter",
    "custom_mean_filter",
    "custom_otsu_threshold",
    "compute_otsu_statistics",
]
