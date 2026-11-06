"""
src/morphology.py: Module xử lý hình thái học toán học và phân vùng ảnh thuần NumPy.
BTL Xử lý ảnh - Khoa CNTT, Đại học Giao thông Vận tải (UTC).
Căn cứ lý thuyết:
- Giáo trình UTC Chương 6: Xử lý hình thái học (c6-Xu ly hinh thai.pdf - Slide 10-18)
- Giáo trình UTC Chương 7: Phân vùng / Phân đoạn ảnh (Chapter7_PhanDoanAnh_Tiếng Việt.pdf)
- Hướng dẫn BTL Đề 18 NASA: Phát hiện vết dầu loang trên ảnh SAR vi ba.

Cam kết: 100% Thuần NumPy/SciPy kinh điển, KHÔNG sử dụng ML/DL.
"""

from collections import deque
from typing import Dict, List, Optional, Tuple
import numpy as np

try:
    import scipy.ndimage as ndi
    HAS_SCIPY = True
except ImportError:
    HAS_SCIPY = False


# ==============================================================================
# 1. TẠO CÁC PHẦN TỬ CẤU TRÚC (STRUCTURING ELEMENTS) - CHƯƠNG 6
# ==============================================================================

def disk_kernel(radius: int) -> np.ndarray:
    """
    Tạo phần tử cấu trúc hình đĩa tròn tâm đối xứng (Chương 6 Slide 11).
    Phù hợp nhất cho các vết dầu loang hữu cơ biến thiên theo dòng chảy.
    """
    y, x = np.ogrid[-radius : radius + 1, -radius : radius + 1]
    return (x**2 + y**2 <= radius**2).astype(np.uint8)


def box_kernel(size: int) -> np.ndarray:
    """Tạo phần tử cấu trúc hình vuông size x size (Chương 6 Slide 11)."""
    return np.ones((size, size), dtype=np.uint8)


def cross_kernel(size: int) -> np.ndarray:
    """Tạo phần tử cấu trúc hình chữ thập (Chương 6 Slide 11)."""
    k = np.zeros((size, size), dtype=np.uint8)
    mid = size // 2
    k[mid, :] = 1
    k[:, mid] = 1
    return k


# ==============================================================================
# 2. CÁC PHÉP TOÁN HÌNH THÁI HỌC CƠ BẢN (PURE NUMPY) - CHƯƠNG 6 SLIDE 10-18
# ==============================================================================

def custom_erosion(binary_img: np.ndarray, kernel: np.ndarray, pad_val: int = 1) -> np.ndarray:
    """
    Phép co hình thái học (Erosion): [A ⊖ B](x, y) = min_{(i,j) in B} A(x+i, y+j).
    Giáo trình UTC: Chương 6 - Slide 11-12.
    Vector hóa tối ưu bằng ma trận trượt thuần NumPy.
    pad_val=1 (True) nhằm đảm bảo các pixel ở biên ảnh không bị co mất biên giả.
    """
    h, w = binary_img.shape
    kh, kw = kernel.shape
    pad_h, pad_w = kh // 2, kw // 2

    fg = binary_img > 0
    padded = np.pad(fg, ((pad_h, pad_h), (pad_w, pad_w)), mode="constant", constant_values=bool(pad_val))

    result = np.ones((h, w), dtype=bool)
    for i in range(kh):
        for j in range(kw):
            if kernel[i, j]:
                result &= padded[i : i + h, j : j + w]

    return (result.astype(np.uint8)) * 255


def custom_dilation(binary_img: np.ndarray, kernel: np.ndarray, pad_val: int = 0) -> np.ndarray:
    """
    Phép giãn hình thái học (Dilation): [A ⊕ B](x, y) = max_{(i,j) in B} A(x+i, y+j).
    Giáo trình UTC: Chương 6 - Slide 11-12.
    Vector hóa tối ưu bằng ma trận trượt thuần NumPy.
    """
    h, w = binary_img.shape
    kh, kw = kernel.shape
    pad_h, pad_w = kh // 2, kw // 2

    fg = binary_img > 0
    padded = np.pad(fg, ((pad_h, pad_h), (pad_w, pad_w)), mode="constant", constant_values=bool(pad_val))

    result = np.zeros((h, w), dtype=bool)
    for i in range(kh):
        for j in range(kw):
            if kernel[i, j]:
                result |= padded[i : i + h, j : j + w]

    return (result.astype(np.uint8)) * 255


def custom_opening(binary_img: np.ndarray, kernel: np.ndarray) -> np.ndarray:
    """
    Phép mở hình thái học (Opening): A ∘ B = (A ⊖ B) ⊕ B.
    Giáo trình UTC: Chương 6 - Slide 13.
    Tác dụng: Triệt tiêu các đốm sáng nhỏ lẻ (nhiễu phản xạ sóng biển) bên ngoài vết dầu.
    """
    eroded = custom_erosion(binary_img, kernel, pad_val=1)
    return custom_dilation(eroded, kernel, pad_val=0)


def custom_closing(binary_img: np.ndarray, kernel: np.ndarray) -> np.ndarray:
    """
    Phép đóng hình thái học (Closing): A • B = (A ⊕ B) ⊖ B.
    Giáo trình UTC: Chương 6 - Slide 14.
    Tác dụng: Lấp đầy các lỗ thủng, hàn gắn các vết nứt do bọt sóng bên trong vết dầu.
    """
    dilated = custom_dilation(binary_img, kernel, pad_val=0)
    return custom_erosion(dilated, kernel, pad_val=1)


def custom_morphological_boundary(
    binary_img: np.ndarray,
    kernel: Optional[np.ndarray] = None,
) -> np.ndarray:
    r"""
    Trích chọn đường biên hình thái học (Morphological Boundary Extraction).
    Giáo trình UTC: Chương 6 - Slide 16.
    Công thức kinh điển:
        beta(A) = A \ (A ⊖ B) = A - erode(A, B)
    Đặc tính: Tạo ra đường biên khép kín liên tục bề dày đúng 1 pixel bọc quanh vết dầu.
    """
    if kernel is None:
        kernel = box_kernel(3)

    img_bin = (binary_img > 0).astype(np.uint8) * 255
    eroded = custom_erosion(img_bin, kernel, pad_val=0)

    # Hiệu tập hợp A \ (A ⊖ B)
    boundary = np.where((img_bin > 0) & (eroded == 0), 255, 0).astype(np.uint8)
    return boundary


# ==============================================================================
# 3. PHÂN VÙNG NGƯỠNG OTSU & TÍNH KHẢ TÁCH (CHƯƠNG 7 UTC)
# ==============================================================================

def custom_otsu_threshold(image: np.ndarray) -> Tuple[int, float]:
    """
    Phân ngưỡng Otsu tối ưu hóa phương sai giữa các lớp (Between-class Variance).
    Giáo trình UTC: Chương 7 - Slide 12-18.
    Công thức:
        sigma_B^2(t) = w0(t) * w1(t) * [mu0(t) - mu1(t)]^2
    Hệ số đo tính khả tách (Separability measure - Chapter 7 Slide 17):
        eta = sigma_B^2(T*) / sigma_T^2   (0 <= eta <= 1)
    Trả về:
        (best_threshold, separability_eta)
    """
    img_u8 = image.astype(np.uint8)
    hist = np.bincount(img_u8.ravel(), minlength=256).astype(np.float64)
    total_pixels = float(image.size)
    p = hist / total_pixels

    cum_w = np.cumsum(p)
    cum_mu = np.cumsum(p * np.arange(256))
    mu_t = cum_mu[-1]

    sigma_total = np.sum(p * ((np.arange(256) - mu_t) ** 2))
    if sigma_total < 1e-8:
        return 128, 0.0

    best_thresh = 128
    max_sigma_b2 = -1.0

    for t in range(256):
        w0 = cum_w[t]
        w1 = 1.0 - w0
        if w0 > 1e-6 and w1 > 1e-6:
            mu0 = cum_mu[t] / w0
            mu1 = (mu_t - cum_mu[t]) / w1
            sigma_b2 = w0 * w1 * ((mu0 - mu1) ** 2)
            if sigma_b2 > max_sigma_b2:
                max_sigma_b2 = sigma_b2
                best_thresh = t

    eta = float(np.clip(max_sigma_b2 / sigma_total, 0.0, 1.0))
    return int(best_thresh), eta


# ==============================================================================
# 4. PHÂN TÍCH THÀNH PHẦN LIÊN THÔNG (CONNECTED COMPONENT ANALYSIS)
# ==============================================================================

def find_connected_components(binary_img: np.ndarray) -> Tuple[int, np.ndarray, List[Dict]]:
    """
    Dán nhãn các thành phần liên thông 8-hướng và trích xuất đặc trưng hình học.
    Sử dụng SciPy ndimage.label (nếu có) hoặc hàng đợi BFS thuần Python.
    """
    fg = (binary_img > 0).astype(np.uint8)
    h, w = fg.shape

    if HAS_SCIPY:
        # Cấu trúc liên thông 8 hướng
        structure = np.ones((3, 3), dtype=np.int32)
        labeled, num_components = ndi.label(fg, structure=structure)
    else:
        # Thuần Python BFS Queue
        labeled = np.zeros((h, w), dtype=np.int32)
        visited = np.zeros((h, w), dtype=bool)
        fg_y, fg_x = np.nonzero(fg)
        num_components = 0

        directions = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]

        for sy, sx in zip(fg_y, fg_x):
            if visited[sy, sx]:
                continue
            num_components += 1
            queue = deque([(sy, sx)])
            visited[sy, sx] = True
            labeled[sy, sx] = num_components

            while queue:
                cy, cx = queue.popleft()
                for dy, dx in directions:
                    ny, nx = cy + dy, cx + dx
                    if 0 <= ny < h and 0 <= nx < w:
                        if fg[ny, nx] and not visited[ny, nx]:
                            visited[ny, nx] = True
                            labeled[ny, nx] = num_components
                            queue.append((ny, nx))

    components_info = []
    if num_components > 0:
        # Trích xuất diện tích và bounding box cho từng vùng
        for comp_id in range(1, num_components + 1):
            mask = labeled == comp_id
            area = int(np.count_nonzero(mask))
            if area == 0:
                continue
            ys, xs = np.nonzero(mask)
            min_y, max_y = int(np.min(ys)), int(np.max(ys))
            min_x, max_x = int(np.min(xs)), int(np.max(xs))
            cy = float(np.mean(ys))
            cx = float(np.mean(xs))

            components_info.append({
                "id": comp_id,
                "area": area,
                "bbox": (min_y, min_x, max_y, max_x),
                "centroid": (cy, cx),
                "mask": mask,
            })

    return num_components, labeled, components_info


# ==============================================================================
# 5. QUY TRÌNH PHÁT HIỆN & BỘC LỘ BIÊN VẾT DẦU TOÀN DIỆN (ĐỀ 18 NASA & CHƯƠNG 6, 7)
# ==============================================================================

def detect_oil_slick_morphological(
    image: np.ndarray,
    min_area: int = 300,
    min_contrast: float = 0.10,
    manual_threshold: Optional[int] = None,
) -> Dict:
    r"""
    Quy trình phát hiện và bộc lộ ranh giới vết dầu loang SAR dựa trên Xử lý hình thái
    (Chương 6 UTC), Phân vùng ngưỡng Otsu (Chương 7 UTC) và Tiêu chuẩn NASA Đề 18.

    Các bước xử lý:
        1. Phân đoạn ngưỡng Otsu tách vùng tối tiềm năng (Dark spot candidate).
        2. Phép mở hình thái học (Opening với đĩa tròn 5x5) xóa nhiễu biển li ti.
        3. Phép đóng hình thái học (Closing với đĩa tròn 7x7) hàn gắn bọt sóng trong vết dầu.
        4. Dán nhãn liên thông & Lọc diện tích (Area >= min_area).
        5. Lọc tỷ số tương phản nền biển lân cận (Contrast ratio C_R >= min_contrast):
           C_R = (mu_sea - mu_slick) / mu_sea.
        6. Trích chọn đường biên hình thái học beta(A) = A \ (A ⊖ B_3x3) (Chương 6 Slide 16).
    """
    img_u8 = image.astype(np.uint8)
    h, w = img_u8.shape

    # 1. Ngưỡng phân tách vùng tối
    if manual_threshold is not None:
        thresh = int(np.clip(manual_threshold, 1, 254))
        _, eta = custom_otsu_threshold(img_u8)
    else:
        thresh, eta = custom_otsu_threshold(img_u8)

    # Vết dầu trên SAR là vùng tối (radar backscatter thấp do sóng mao dẫn bị dập tắt)
    dark_mask = (img_u8 < thresh).astype(np.uint8) * 255

    # 2. Phép mở (Opening r=2 -> 5x5 disk) loại bỏ gai nhiễu sóng biển
    k_open = disk_kernel(2)
    opened = custom_opening(dark_mask, k_open)

    # 3. Phép đóng (Closing r=3 -> 7x7 disk) liền mạch các vết nứt bọt sóng
    k_close = disk_kernel(3)
    closed = custom_closing(opened, k_close)

    # 4. Phân tích thành phần liên thông
    _, _, components = find_connected_components(closed)

    # Phần tử cấu trúc dãn nở vùng đệm biển (Ring buffer 15x15)
    k_ring = box_kernel(15)

    clean_mask = np.zeros((h, w), dtype=np.uint8)
    slicks_detected = []
    total_area_px = 0
    contrast_ratios = []

    for comp in components:
        area = comp["area"]
        # Lọc diện tích (Loại bỏ các đốm nhiễu nhỏ < min_area px)
        if area < min_area:
            continue

        comp_mask = comp["mask"]
        comp_u8 = comp_mask.astype(np.uint8) * 255

        # Cường độ xám trung bình của vết dầu
        slick_mean = float(np.mean(img_u8[comp_mask]))

        # Vùng đệm biển lân cận bao quanh vết dầu (Ring buffer = Dilate - Mask)
        dilated_comp = custom_dilation(comp_u8, k_ring, pad_val=0) > 0
        ring_mask = dilated_comp & (~comp_mask)

        if np.any(ring_mask):
            sea_mean = float(np.mean(img_u8[ring_mask]))
        else:
            sea_mean = 255.0

        # Tỷ số tương phản nền biển (NASA Topic 18: C_R = (mu_sea - mu_slick) / mu_sea)
        if sea_mean > 1e-3:
            cr = float((sea_mean - slick_mean) / sea_mean)
        else:
            cr = 0.0

        # Vết dầu thực sự phải có tương phản tối hơn nền biển lân cận
        if cr >= min_contrast:
            clean_mask[comp_mask] = 255
            total_area_px += area
            contrast_ratios.append(cr)
            slicks_detected.append({
                "id": len(slicks_detected) + 1,
                "area": area,
                "bbox": comp["bbox"],
                "centroid": comp["centroid"],
                "slick_mean": round(slick_mean, 1),
                "sea_mean": round(sea_mean, 1),
                "contrast_ratio": round(cr, 3),
            })

    # 5. Trích chọn đường biên hình thái học beta(A) = A \ (A ⊖ B_3x3)
    k_boundary = box_kernel(3)
    boundary_mask = custom_morphological_boundary(clean_mask, k_boundary)

    # Thống kê tổng hợp
    total_pixels = float(h * w)
    area_pct = round((total_area_px / total_pixels) * 100.0, 2)
    mean_cr = round(float(np.mean(contrast_ratios)), 3) if contrast_ratios else 0.0

    return {
        "boundary_mask": boundary_mask,
        "clean_mask": clean_mask,
        "slicks_detected": slicks_detected,
        "slicks_count": len(slicks_detected),
        "total_area_px": total_area_px,
        "area_pct": area_pct,
        "mean_contrast_ratio": mean_cr,
        "otsu_threshold": thresh,
        "separability_eta": round(eta, 3),
    }
