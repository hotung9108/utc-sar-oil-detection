"""
Module utils.py: Tiện ích nạp ảnh, hiển thị, vẽ biểu đồ Histogram và đồ thị mức xám cắt ngang (Profile slice).
BTL Xử lý ảnh - Khoa CNTT, Đại học Giao thông Vận tải (UTC)
"""

import os
from typing import Optional, Tuple
import cv2
import matplotlib.pyplot as plt
import numpy as np


def load_sar_image(path: str, target_size: Optional[Tuple[int, int]] = (400, 400)) -> np.ndarray:
    """Nạp ảnh SAR từ ổ đĩa và chuyển sang ma trận xám uint8 2D."""
    if not os.path.exists(path):
        raise FileNotFoundError(f"Không tìm thấy file ảnh: {path}")

    img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise ValueError(f"Không thể đọc ảnh: {path}")

    if target_size is not None and img.shape != target_size:
        img = cv2.resize(img, (target_size[1], target_size[0]), interpolation=cv2.INTER_LINEAR)

    return img


def save_image(path: str, img: np.ndarray) -> None:
    """Lưu ảnh xuống đĩa."""
    parent = os.path.dirname(path)
    if parent and not os.path.exists(parent):
        os.makedirs(parent, exist_ok=True)
    cv2.imwrite(path, img)


def calculate_difference_map(original: np.ndarray, processed: np.ndarray) -> np.ndarray:
    """
    Tính bản đồ sai số vi sai tuyệt đối: Diff = |Processed - Original|.
    Giúp trực quan hóa xem thuật toán tăng cường/lọc ảnh đã thay đổi những chi tiết nào.
    """
    orig_f = original.astype(np.float64)
    proc_f = processed.astype(np.float64)
    diff = np.abs(proc_f - orig_f)
    return np.clip(np.round(diff * 2.0), 0, 255).astype(np.uint8)  # Nhân 2 để làm rõ vi sai


def get_profile_slice(
    image: np.ndarray,
    row_or_col: int = 200,
    axis: int = 0,
) -> np.ndarray:
    """
    Trích xuất một đường cắt mức xám (Profile slice) ngang qua ảnh:
    Nếu axis=0: lấy hàng pixel thứ row_or_col.
    Nếu axis=1: lấy cột pixel thứ row_or_col.
    """
    if axis == 0:
        return image[row_or_col, :].astype(np.float64)
    else:
        return image[:, row_or_col].astype(np.float64)
