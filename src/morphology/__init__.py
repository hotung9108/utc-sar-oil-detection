"""
Module Xử lý Hình thái học ảnh (Mathematical Morphology) thuần NumPy 100%.
Đồ án Xử lý ảnh - Đề tài: Phát hiện vết dầu tràn trên ảnh SAR Sentinel-1.
Giảng viên hướng dẫn: TS. Phan Thanh Toàn - Đại học Giao thông Vận tải (UTC).
Cài đặt bởi TV4: Hình thái học & Trích xuất đặc trưng vật lý.
"""

from .numpy_morphology import (
    get_structuring_element,
    custom_erode,
    custom_dilate,
    custom_open,
    custom_close,
    custom_fill_holes,
    custom_extract_boundary,
    custom_connected_components,
)

__all__ = [
    "get_structuring_element",
    "custom_erode",
    "custom_dilate",
    "custom_open",
    "custom_close",
    "custom_fill_holes",
    "custom_extract_boundary",
    "custom_connected_components",
]
