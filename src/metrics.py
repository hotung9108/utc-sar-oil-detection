"""
Module metrics.py: Các chỉ số định lượng đánh giá chất lượng Tăng cường và Lọc ảnh (Nhóm A).
BTL Xử lý ảnh - Khoa CNTT, Đại học Giao thông Vận tải (UTC)
"""

from typing import Dict, Optional, Tuple, Union
import numpy as np


def calculate_enl(image: np.ndarray, roi: Optional[Tuple[int, int, int, int]] = None) -> float:
    """
    Tính số quan sát tương đương ENL (Equivalent Number of Looks) trên vùng đồng nhất.
    Công thức: ENL = mu^2 / sigma^2
    Chỉ số này phản ánh mức độ làm mịn phẳng nhiễu đốm trong ảnh vi ba SAR.
    """
    img_f = image.astype(np.float64)
    h, w = img_f.shape

    if roi is not None:
        ymin, ymax, xmin, xmax = roi
        patch = img_f[ymin:ymax, xmin:xmax]
    else:
        # Lấy vùng đồng nhất 60x60 ở góc trên
        patch = img_f[20 : min(h, 80), 20 : min(w, 80)]

    mu = float(np.mean(patch))
    var = float(np.var(patch))
    if var < 1e-8:
        return 999.0
    return float((mu**2) / var)


def calculate_ssi(original: np.ndarray, filtered: np.ndarray) -> float:
    """
    Tính chỉ số triệt tiêu đốm SSI (Speckle Suppression Index).
    Công thức: SSI = (std_f / mu_f) / (std_o / mu_o)
    SSI < 1 biểu thị đốm nhiễu đã được triệt tiêu tốt.
    """
    orig_f = original.astype(np.float64)
    filt_f = filtered.astype(np.float64)

    mu_o = float(np.mean(orig_f))
    std_o = float(np.std(orig_f))

    mu_f = float(np.mean(filt_f))
    std_f = float(np.std(filt_f))

    if mu_o < 1e-6 or std_o < 1e-6 or mu_f < 1e-6:
        return 1.0

    return float((std_f / mu_f) / (std_o / mu_o))


def calculate_rms_contrast(image: np.ndarray) -> float:
    """
    Tính độ tương phản RMS (Root Mean Square Contrast).
    Giáo trình UTC: Chương 3.1 - Slide 70.
    Công thức: RMS = sqrt( (1 / (M*N)) * sum((I(x,y) - mu)^2) ) = std(I).
    Đo độ biến thiên và dải tương phản tổng thể của ảnh.
    """
    img_f = image.astype(np.float64)
    return float(np.std(img_f))


def calculate_entropy(image: np.ndarray) -> float:
    """
    Tính Entropy thông tin (Shannon Information Entropy) của ảnh xám 8-bit.
    Giáo trình UTC: Chương 3.1 - Slide 21.
    Công thức: H = - sum( p_i * log2(p_i + epsilon) )
    Phản ánh lượng thông tin chi tiết bộc lộ. Với ảnh 8-bit phân bố đều, H_max = 8.0 bits.
    """
    img_u8 = image.astype(np.uint8)
    hist = np.bincount(img_u8.ravel(), minlength=256).astype(np.float64)
    total = img_u8.size
    prob = hist / float(total)

    # Lọc các xác suất > 0
    non_zero_p = prob[prob > 0]
    entropy = -float(np.sum(non_zero_p * np.log2(non_zero_p)))
    return entropy


def calculate_ambe(original: np.ndarray, enhanced: np.ndarray) -> float:
    """
    Tính sai số độ sáng tuyệt đối trung bình AMBE (Absolute Mean Brightness Error).
    Công thức: AMBE = |mu_enhanced - mu_original|
    Đo mức độ bảo toàn độ sáng nền. AMBE càng thấp chứng tỏ phương pháp không làm biến dạng độ sáng tổng thể.
    """
    mu_orig = float(np.mean(original.astype(np.float64)))
    mu_enh = float(np.mean(enhanced.astype(np.float64)))
    return float(abs(mu_enh - mu_orig))


def calculate_epi(original: np.ndarray, filtered: np.ndarray) -> float:
    """
    Tính chỉ số bảo toàn biên EPI (Edge Preservation Index).
    Sử dụng toán tử vi sai bậc hai Laplacian trên ảnh gốc và ảnh sau lọc:
        EPI = sum(|Laplacian(filtered)|) / sum(|Laplacian(original)|)
    EPI gần 1.0 chứng tỏ các đường biên vết dầu được bảo toàn nguyên vẹn sau khi khử đốm.
    """
    from scipy.ndimage import laplace

    orig_f = original.astype(np.float64)
    filt_f = filtered.astype(np.float64)

    lap_orig = np.abs(laplace(orig_f))
    lap_filt = np.abs(laplace(filt_f))

    denom = float(np.sum(lap_orig))
    if denom < 1e-8:
        return 1.0

    return float(np.sum(lap_filt) / denom)


def calculate_all_enhancement_metrics(
    original: np.ndarray,
    enhanced: np.ndarray,
) -> Dict[str, float]:
    """
    Tính toán trọn bộ 6 chỉ số định lượng phục vụ báo cáo Nhóm A:
    ENL, SSI, RMS Contrast, Entropy, AMBE, EPI.
    """
    return {
        "ENL": calculate_enl(enhanced),
        "SSI": calculate_ssi(original, enhanced),
        "RMS_Contrast": calculate_rms_contrast(enhanced),
        "Entropy": calculate_entropy(enhanced),
        "AMBE": calculate_ambe(original, enhanced),
        "EPI": calculate_epi(original, enhanced),
    }
