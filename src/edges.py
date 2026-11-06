"""
src/edges.py: Module xử lý và phát hiện biên ảnh thuần NumPy (Đề 5 & Chương 5 UTC).
BTL Xử lý ảnh - Khoa CNTT, Đại học Giao thông Vận tải (UTC).
Cam kết: 100% Pure NumPy, không sử dụng API phát hiện biên của OpenCV hay Scikit-Image.
"""

from collections import deque
from typing import Optional, Tuple
import numpy as np
from src.filters import custom_gaussian_filter


def custom_roberts(image: np.ndarray) -> np.ndarray:
    """
    Toán tử phát hiện biên Roberts Cross (2x2).
    Giáo trình UTC: Chương 5 - Slide 24-29.
    Kx = [[1, 0], [0, -1]], Ky = [[0, 1], [-1, 0]]
    """
    img_f = image.astype(np.float64)
    h, w = img_f.shape

    # Padded reflect
    padded = np.pad(img_f, ((0, 1), (0, 1)), mode="reflect")

    # Convolution 2x2
    p00 = padded[0:h, 0:w]
    p01 = padded[0:h, 1 : w + 1]
    p10 = padded[1 : h + 1, 0:w]
    p11 = padded[1 : h + 1, 1 : w + 1]

    gx = p00 - p11
    gy = p01 - p10

    mag = np.sqrt(gx**2 + gy**2)
    return np.clip(np.round(mag), 0, 255).astype(np.uint8)


def custom_prewitt(image: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Toán tử phát hiện biên Prewitt (3x3).
    Giáo trình UTC: Chương 5 - Slide 30-35.
    Trả về: (Gx, Gy, Gradient_Magnitude)
    """
    img_f = image.astype(np.float64)
    h, w = img_f.shape
    padded = np.pad(img_f, 1, mode="reflect")

    p00, p01, p02 = padded[0:h, 0:w], padded[0:h, 1 : w + 1], padded[0:h, 2 : w + 2]
    p10, _, p12 = padded[1 : h + 1, 0:w], None, padded[1 : h + 1, 2 : w + 2]
    p20, p21, p22 = padded[2 : h + 2, 0:w], padded[2 : h + 2, 1 : w + 1], padded[2 : h + 2, 2 : w + 2]

    # Prewitt Kernels
    gx = (p02 + p12 + p22) - (p00 + p10 + p20)
    gy = (p20 + p21 + p22) - (p00 + p01 + p02)

    mag = np.sqrt(gx**2 + gy**2)
    mag_u8 = np.clip(np.round(mag), 0, 255).astype(np.uint8)
    return gx, gy, mag_u8


def custom_sobel(image: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """
    Toán tử phát hiện biên Sobel (3x3).
    Giáo trình UTC: Chương 5 - Slide 36-41.
    Trả về: (Gx, Gy, Gradient_Magnitude, Gradient_Theta_Degrees)
    """
    img_f = image.astype(np.float64)
    h, w = img_f.shape
    padded = np.pad(img_f, 1, mode="reflect")

    p00, p01, p02 = padded[0:h, 0:w], padded[0:h, 1 : w + 1], padded[0:h, 2 : w + 2]
    p10, _, p12 = padded[1 : h + 1, 0:w], None, padded[1 : h + 1, 2 : w + 2]
    p20, p21, p22 = padded[2 : h + 2, 0:w], padded[2 : h + 2, 1 : w + 1], padded[2 : h + 2, 2 : w + 2]

    # Sobel Kernels
    gx = (p02 + 2.0 * p12 + p22) - (p00 + 2.0 * p10 + p20)
    gy = (p20 + 2.0 * p21 + p22) - (p00 + 2.0 * p01 + p02)

    mag = np.sqrt(gx**2 + gy**2)
    theta = np.arctan2(gy, gx) * (180.0 / np.pi)
    theta[theta < 0] += 180.0

    mag_u8 = np.clip(np.round(mag), 0, 255).astype(np.uint8)
    return gx, gy, mag_u8, theta


def custom_log(image: np.ndarray, sigma: float = 1.4, threshold: float = 4.0) -> np.ndarray:
    """
    Toán tử Laplacian of Gaussian (LoG - Marr-Hildreth) với dò điểm qua 0 (Zero-Crossing).
    Giáo trình UTC: Chương 5 - Slide 21 & Đề 5 ds btl xla.
    """
    img_f = image.astype(np.float64)
    # 1. Tạo mặt nạ LoG kích thước 2*ceil(3*sigma)+1
    r = int(np.ceil(3.0 * sigma))
    window_size = 2 * r + 1
    y, x = np.ogrid[-r : r + 1, -r : r + 1]
    r2 = x**2 + y**2
    sigma2 = sigma**2
    kernel = -((r2 - 2.0 * sigma2) / (sigma2**2)) * np.exp(-r2 / (2.0 * sigma2))
    kernel -= np.mean(kernel)  # Đảm bảo tổng trọng số = 0

    # 2. Tích chập không gian
    h, w = img_f.shape
    padded = np.pad(img_f, r, mode="reflect")

    log_resp = np.zeros((h, w), dtype=np.float64)
    for i in range(window_size):
        for j in range(window_size):
            log_resp += kernel[i, j] * padded[i : i + h, j : j + w]

    # 3. Dò điểm qua 0 (Zero-Crossing Detection)
    pad_log = np.pad(log_resp, 1, mode="reflect")
    zero_cross = np.zeros((h, w), dtype=np.uint8)

    # 4 cặp lân cận đối diện: (trên-dưới), (trái-phải), (chéo 1), (chéo 2)
    pairs = [
        (pad_log[0:h, 1 : w + 1], pad_log[2 : h + 2, 1 : w + 1]),
        (pad_log[1 : h + 1, 0:w], pad_log[1 : h + 1, 2 : w + 2]),
        (pad_log[0:h, 0:w], pad_log[2 : h + 2, 2 : w + 2]),
        (pad_log[0:h, 2 : w + 2], pad_log[2 : h + 2, 0:w]),
    ]

    for p1, p2 in pairs:
        # Tích âm biểu thị đổi dấu qua 0 và chênh lệch vượt ngưỡng
        cond = (p1 * p2 < 0) & (np.abs(p1 - p2) > threshold)
        zero_cross[cond] = 255

    return zero_cross


def custom_canny(
    image: np.ndarray,
    low_thresh: Optional[float] = None,
    high_thresh: Optional[float] = None,
    sigma: float = 1.2,
) -> np.ndarray:
    """
    Bộ dò biên tối ưu Canny Edge Detector 4 bước kinh điển tự cài đặt 100% bằng Pure NumPy.
    Giáo trình UTC: Chương 7 Tiếng Việt - Slide 21-26 & Đề 5 ds btl xla.

    4 Bước thuật toán:
        1. Làm mịn ảnh bằng lọc Gauss tách được 1D giảm nhiễu đốm.
        2. Tính độ lớn và góc gradient bằng toán tử Sobel.
        3. Triệt tiêu không cực đại (Non-Maximum Suppression - NMS) làm mảnh biên.
        4. Phân ngưỡng kép (Double Thresholding) & Dò vết cạnh liên thông (Hysteresis Tracking).
    """
    img_u8 = image.astype(np.uint8)

    # Tự động chọn ngưỡng theo trung vị ảnh (theo yêu cầu Đề 5) nếu không truyền vào
    if low_thresh is None or high_thresh is None:
        med = float(np.median(img_u8))
        auto_low = max(15.0, 0.66 * med)
        auto_high = min(220.0, 1.33 * med)
        low_thresh = low_thresh or auto_low
        high_thresh = high_thresh or auto_high

    # BƯỚC 1: Làm mịn Gaussian
    smoothed = custom_gaussian_filter(img_u8, window_size=5, sigma=sigma)

    # BƯỚC 2: Tính Gradient Sobel & Góc hướng
    gx, gy, mag, theta = custom_sobel(smoothed)
    h, w = mag.shape

    # BƯỚC 3: Triệt tiêu không cực đại (Non-Maximum Suppression - NMS)
    # Lượng tử hóa góc gradient thành 4 hướng:
    # 0 độ: [0..22.5) hoặc [157.5..180] -> Ngang (so sánh trái/phải)
    # 45 độ: [22.5..67.5) -> Đường chéo chính (so sánh trên-phải và dưới-trái)
    # 90 độ: [67.5..112.5) -> Dọc (so sánh trên/dưới)
    # 135 độ: [112.5..157.5) -> Đường chéo phụ (so sánh trên-trái và dưới-phải)

    padded_mag = np.pad(mag.astype(np.float64), 1, mode="constant", constant_values=0)
    p_center = padded_mag[1 : h + 1, 1 : w + 1]

    # Các láng giềng
    p_right = padded_mag[1 : h + 1, 2 : w + 2]
    p_left = padded_mag[1 : h + 1, 0:w]
    p_top = padded_mag[0:h, 1 : w + 1]
    p_bottom = padded_mag[2 : h + 2, 1 : w + 1]
    p_top_right = padded_mag[0:h, 2 : w + 2]
    p_bottom_left = padded_mag[2 : h + 2, 0:w]
    p_top_left = padded_mag[0:h, 0:w]
    p_bottom_right = padded_mag[2 : h + 2, 2 : w + 2]

    nms = np.zeros((h, w), dtype=np.float64)

    # Sector 0 (Ngang)
    mask0 = ((theta >= 0.0) & (theta < 22.5)) | ((theta >= 157.5) & (theta <= 180.0))
    keep0 = mask0 & (p_center >= p_right) & (p_center >= p_left)
    nms[keep0] = p_center[keep0]

    # Sector 1 (45 độ)
    mask1 = (theta >= 22.5) & (theta < 67.5)
    keep1 = mask1 & (p_center >= p_top_right) & (p_center >= p_bottom_left)
    nms[keep1] = p_center[keep1]

    # Sector 2 (90 độ - Dọc)
    mask2 = (theta >= 67.5) & (theta < 112.5)
    keep2 = mask2 & (p_center >= p_top) & (p_center >= p_bottom)
    nms[keep2] = p_center[keep2]

    # Sector 3 (135 độ)
    mask3 = (theta >= 112.5) & (theta < 157.5)
    keep3 = mask3 & (p_center >= p_top_left) & (p_center >= p_bottom_right)
    nms[keep3] = p_center[keep3]

    # BƯỚC 4: Phân ngưỡng kép (Double Thresholding) & Hysteresis Tracking
    # Phân loại điểm biên
    strong_edges = nms >= high_thresh
    weak_edges = (nms >= low_thresh) & (nms < high_thresh)

    output = np.zeros((h, w), dtype=np.uint8)
    output[strong_edges] = 255

    # Lần vết liên thông bằng BFS queue để kết nối các weak edges với strong edges
    strong_y, strong_x = np.nonzero(strong_edges)
    queue = deque(zip(strong_y, strong_x))

    # Bảng đánh dấu để tránh duyệt lặp
    visited = np.zeros((h, w), dtype=bool)
    visited[strong_edges] = True

    directions = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]

    while queue:
        cy, cx = queue.popleft()
        for dy, dx in directions:
            ny, nx = cy + dy, cx + dx
            if 0 <= ny < h and 0 <= nx < w:
                if not visited[ny, nx] and weak_edges[ny, nx]:
                    visited[ny, nx] = True
                    output[ny, nx] = 255
                    queue.append((ny, nx))

    return output


def overlay_edges(
    image: np.ndarray,
    binary_edges: np.ndarray,
    color: Tuple[int, int, int] = (255, 30, 30),
    alpha: float = 0.85,
) -> np.ndarray:
    """
    Phủ đường viền biên phát hiện được lên ảnh gốc xám dưới dạng ảnh RGB màu nổi bật.
    Mặc định tô viền màu đỏ rực rỡ (255, 30, 30) bộc lộ rõ vùng ranh giới vết dầu.
    """
    img_u8 = image.astype(np.uint8)
    h, w = img_u8.shape

    # Chuyển ảnh xám sang 3 kênh RGB
    rgb = np.stack([img_u8, img_u8, img_u8], axis=-1).astype(np.float64)

    # Vị trí có đường biên
    edge_mask = binary_edges > 0

    target_color = np.array(color, dtype=np.float64)

    # Phủ màu với hệ số alpha
    rgb[edge_mask] = (1.0 - alpha) * rgb[edge_mask] + alpha * target_color

    return np.clip(np.round(rgb), 0, 255).astype(np.uint8)


# Tái xuất các hàm bộc lộ ranh giới hình thái học (Chương 6 & 7 UTC + Đề 18 NASA)
from src.morphology import (
    custom_morphological_boundary,
    detect_oil_slick_morphological,
)
