"""
Module sharpening.py: Các phương pháp làm nét ảnh và bộc lộ đường biên vết dầu thuần NumPy.
Giáo trình UTC: Chương 3.2 (Unsharp Masking, High-boost, Laplacian) và Chương 5 (Biên Sobel).
Khoa CNTT - Đại học Giao thông Vận tải (UTC)
"""

from typing import Tuple

import numpy as np

from src.filters import custom_box_filter, custom_gaussian_filter


def unsharp_masking(
    image: np.ndarray,
    k: float = 1.0,
    blur_type: str = "gaussian",
    window_size: int = 5,
    sigma: float = 1.0,
) -> np.ndarray:
    """
    Kỹ thuật Unsharp Masking (k = 1) và High-boost Filtering (k > 1) thuần NumPy.
    Giáo trình UTC: Chương 3.2 - Slide 32-36.

    Quy trình:
        1. Làm mờ ảnh gốc: f_blur = Blur(f)
        2. Tạo mặt nạ chi tiết tần số cao: g_mask = f - f_blur
        3. Khuếch đại và cộng vào ảnh gốc: f_sharp = f + k * g_mask
    """
    img_f = image.astype(np.float64)

    if blur_type == "gaussian":
        blurred = custom_gaussian_filter(image, window_size=window_size, sigma=sigma).astype(
            np.float64
        )
    else:
        blurred = custom_box_filter(image, window_size=window_size).astype(np.float64)

    mask = img_f - blurred
    sharpened = img_f + float(k) * mask

    return np.clip(np.round(sharpened), 0, 255).astype(np.uint8)


def laplacian_sharpening(image: np.ndarray, alpha: float = 0.5) -> np.ndarray:
    """
    Làm nét ảnh bằng toán tử đạo hàm bậc 2 Laplacian thuần NumPy.
    Giáo trình UTC: Chương 3.2 - Slide 32-34.
    Mặt nạ Laplacian tâm âm: [[0, 1, 0], [1, -4, 1], [0, 1, 0]].
    Ảnh sắc nét: f_sharp = f - alpha * Laplacian(f).
    """
    img_f = image.astype(np.float64)
    h, w = img_f.shape

    padded = np.pad(img_f, 1, mode="reflect")

    # Convolution với mặt nạ Laplacian
    p_c = padded[1 : h + 1, 1 : w + 1]
    p_top = padded[0:h, 1 : w + 1]
    p_bot = padded[2 : h + 2, 1 : w + 1]
    p_left = padded[1 : h + 1, 0:w]
    p_right = padded[1 : h + 1, 2 : w + 2]

    lap = (p_top + p_bot + p_left + p_right) - 4.0 * p_c

    sharp = img_f - float(alpha) * lap
    return np.clip(np.round(sharp), 0, 255).astype(np.uint8)


def sobel_edge_enhancement(image: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """
    Đo độ lớn Gradient Sobel và phủ đường biên lên ảnh gốc để bộc lộ rõ viền vết dầu.
    Giáo trình UTC: Chương 5 - Slide 36-40.
    """
    img_f = image.astype(np.float64)
    h, w = img_f.shape

    padded = np.pad(img_f, 1, mode="reflect")

    p00, p01, p02 = padded[0:h, 0:w], padded[0:h, 1 : w + 1], padded[0:h, 2 : w + 2]
    p10, _p11, p12 = (
        padded[1 : h + 1, 0:w],
        padded[1 : h + 1, 1 : w + 1],
        padded[1 : h + 1, 2 : w + 2],
    )
    p20, p21, p22 = (
        padded[2 : h + 2, 0:w],
        padded[2 : h + 2, 1 : w + 1],
        padded[2 : h + 2, 2 : w + 2],
    )

    grad_x = (p02 + 2.0 * p12 + p22) - (p00 + 2.0 * p10 + p20)
    grad_y = (p00 + 2.0 * p01 + p02) - (p20 + 2.0 * p21 + p22)

    grad_mag = np.sqrt(grad_x**2 + grad_y**2)
    grad_u8 = np.clip(np.round(grad_mag), 0, 255).astype(np.uint8)

    # Tạo ảnh biên viền nổi bật (kết hợp biên vào ảnh gốc)
    enhanced = np.clip(img_f + 0.5 * grad_mag, 0, 255).astype(np.uint8)
    return grad_u8, enhanced
