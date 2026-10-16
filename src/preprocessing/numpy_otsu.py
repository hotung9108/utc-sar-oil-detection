"""
numpy_otsu.py
=============
Cài đặt thuật toán Phân ngưỡng Otsu tối ưu (Otsu's Thresholding) thuần 100% bằng NumPy,
bám sát nguyên lý toán học trong Slide bài giảng Xử lý ảnh - TS. Phan Thanh Toàn
(Chương 7: Phân vùng ảnh, Trang 48-55).

Tuân thủ nguyên tắc:
- 100% NumPy thuần, không sử dụng `cv2.threshold` hay các thư viện ngoài.
- Vector hóa hoàn toàn trên toàn bộ 256 mức xám với tốc độ dưới 1ms.
- Tính toán đầy đủ: Histogram p_i, trung bình tích lũy mu(k), trọng số tích lũy omega(k),
  phương sai liên lớp sigma_B^2(k), phương sai toàn cục sigma_T^2 và hệ số khả tách eta.
- Trả về mặt nạ nhị phân đốm tối (dark mask) phục vụ bài toán trích xuất vệt dầu loang trên ảnh SAR.

Thành viên thực hiện: TV3 (Cài đặt thuật toán 1: Tiền xử lý & Phân đoạn).
"""

from typing import Tuple, Dict, Any
import numpy as np


def custom_otsu_threshold(
    image: np.ndarray
) -> Tuple[int, float, np.ndarray]:
    """
    Phân ngưỡng Otsu tối ưu và tính hệ số khả tách eta theo Slide TS. Phan Thanh Toàn.

    Cơ sở lý thuyết (Slide Chương 7, P48-55):
    -----------------------------------------
    1. Lược đồ mức xám chuẩn hóa (Xác suất xuất hiện mức xám i):
       p_i = n_i / N, với N = M x N là tổng số pixel, sum_{i=0}^{L-1} p_i = 1 (L = 256).

    2. Với mỗi ngưỡng k in [0, L-1], chia ảnh thành 2 lớp:
       - Lớp C_0 (nền hoặc đốm tối): các mức xám [0, k].
       - Lớp C_1 (vùng biển sáng): các mức xám [k+1, L-1].

    3. Trọng số tích lũy (Xác suất của mỗi lớp):
       omega_0(k) = sum_{i=0}^k p_i = omega(k)
       omega_1(k) = sum_{i=k+1}^{L-1} p_i = 1 - omega_0(k)

    4. Trung bình tích lũy và trung bình các lớp:
       mu(k) = sum_{i=0}^k i * p_i
       mu_T = mu(L-1) = sum_{i=0}^{L-1} i * p_i  (Trung bình toàn cục)
       mu_0(k) = mu(k) / omega_0(k)
       mu_1(k) = (mu_T - mu(k)) / (1 - omega_0(k))

    5. Phương sai liên lớp (Between-class variance):
       sigma_B^2(k) = omega_0(k) * (mu_0(k) - mu_T)^2 + omega_1(k) * (mu_1(k) - mu_T)^2
       Rút gọn đại số tương đương:
       sigma_B^2(k) = [mu_T * omega(k) - mu(k)]^2 / [omega(k) * (1 - omega(k))]

    6. Tổng phương sai toàn cục:
       sigma_T^2 = sum_{i=0}^{L-1} (i - mu_T)^2 * p_i

    7. Ngưỡng tối ưu T* và Hệ số khả tách eta (Separability measure):
       T* = argmax_{0 <= k < L} sigma_B^2(k)
       eta = sigma_B^2(T*) / sigma_T^2,  với eta in [0, 1]
       (eta càng gần 1 thì 2 lớp càng phân tách rõ rệt; nếu eta < 0.1, ảnh đơn điệu không có vệt dầu nổi bật).

    8. Mặt nạ đốm tối (SAR Dark Mask):
       Do vệt dầu làm phẳng sóng mao dẫn biển, triệt tiêu tán xạ ngược radar -> vệt có mức xám tối:
       dark_mask(r, c) = 255 nếu image(r, c) <= T*, ngược lại 0.

    Args:
        image: Mảng NumPy 2D mức xám (uint8 [0, 255]).

    Returns:
        Tuple[int, float, np.ndarray]:
            - optimal_t: Ngưỡng tối ưu T* (int trong khoảng [0, 255]).
            - eta: Hệ số khả tách eta (float trong khoảng [0.0, 1.0]).
            - dark_mask: Mặt nạ nhị phân đốm tối uint8 (255 cho pixel <= T*, 0 cho pixel > T*).

    Raises:
        ValueError: Nếu ảnh không phải mảng 2D.
    """
    if not isinstance(image, np.ndarray):
        raise TypeError("Input 'image' must be a numpy.ndarray.")
    if image.ndim != 2:
        raise ValueError(f"Input 'image' must be a 2D grayscale array, got shape {image.shape}.")

    # Đảm bảo dữ liệu mức xám thuộc dải [0, 255]
    if image.dtype != np.uint8:
        if np.issubdtype(image.dtype, np.floating) and image.max() <= 1.0:
            img_u8 = np.clip(np.round(image * 255.0), 0, 255).astype(np.uint8)
        else:
            img_u8 = np.clip(np.round(image), 0, 255).astype(np.uint8)
    else:
        img_u8 = image

    # 1. Tính histogram 256 bins và phân bố xác suất p_i
    hist, _ = np.histogram(img_u8.ravel(), bins=256, range=(0, 256))
    total_pixels = img_u8.size
    p = hist.astype(np.float64) / float(total_pixels)

    # 2. Tính trọng số tích lũy omega(k) và trung bình tích lũy mu(k)
    gray_levels = np.arange(256, dtype=np.float64)
    omega = np.cumsum(p)
    mu = np.cumsum(p * gray_levels)
    mu_t = mu[-1]  # Trung bình toàn cục mu_T

    # 3. Tính tổng phương sai toàn cục sigma_T^2
    sigma_t_sq = float(np.sum(((gray_levels - mu_t) ** 2) * p))

    # 4. Tính phương sai liên lớp sigma_B^2(k) cho toàn bộ 256 mức xám
    # sigma_B^2(k) = (mu_t * omega - mu)^2 / (omega * (1 - omega))
    denom = omega * (1.0 - omega)
    numer = (mu_t * omega - mu) ** 2

    sigma_b_sq = np.zeros(256, dtype=np.float64)
    valid_mask = denom > 1e-12
    sigma_b_sq[valid_mask] = numer[valid_mask] / denom[valid_mask]

    # 5. Tìm ngưỡng tối ưu T* cực đại hóa sigma_B^2(k)
    # Nếu có nhiều mức xám đạt cực đại ngang nhau, lấy trung bình cộng theo chuẩn lý thuyết
    max_val = np.max(sigma_b_sq)
    if max_val > 0.0:
        candidates = np.where(np.isclose(sigma_b_sq, max_val, rtol=1e-5, atol=1e-7))[0]
        optimal_t = int(np.round(np.mean(candidates)))
    else:
        optimal_t = 0

    # 6. Tính hệ số khả tách eta = sigma_B^2(T*) / sigma_T^2
    if sigma_t_sq > 1e-9:
        eta = float(sigma_b_sq[optimal_t] / sigma_t_sq)
        eta = float(np.clip(eta, 0.0, 1.0))
    else:
        eta = 0.0

    # 7. Sinh mặt nạ đốm tối (dark mask): Pixel có mức xám <= T* được gán 255
    dark_mask = np.where(img_u8 <= optimal_t, np.uint8(255), np.uint8(0))

    return optimal_t, eta, dark_mask


def compute_otsu_statistics(image: np.ndarray) -> Dict[str, Any]:
    """
    Hàm phân tích chi tiết các đại lượng thống kê trung gian của thuật toán Otsu.
    Hữu ích cho việc vẽ biểu đồ lược đồ, đường cong phương sai liên lớp và phân tích toán học.

    Returns:
        dict: Chứa {
            'hist': np.ndarray (256,),
            'p': np.ndarray (256,),
            'omega': np.ndarray (256,),
            'mu': np.ndarray (256,),
            'mu_t': float,
            'sigma_b_sq': np.ndarray (256,),
            'sigma_t_sq': float,
            'optimal_t': int,
            'eta': float
        }
    """
    if image.dtype != np.uint8:
        if np.issubdtype(image.dtype, np.floating) and image.max() <= 1.0:
            img_u8 = np.clip(np.round(image * 255.0), 0, 255).astype(np.uint8)
        else:
            img_u8 = np.clip(np.round(image), 0, 255).astype(np.uint8)
    else:
        img_u8 = image

    hist, _ = np.histogram(img_u8.ravel(), bins=256, range=(0, 256))
    total_pixels = img_u8.size
    p = hist.astype(np.float64) / float(total_pixels)

    gray_levels = np.arange(256, dtype=np.float64)
    omega = np.cumsum(p)
    mu = np.cumsum(p * gray_levels)
    mu_t = float(mu[-1])

    sigma_t_sq = float(np.sum(((gray_levels - mu_t) ** 2) * p))

    denom = omega * (1.0 - omega)
    numer = (mu_t * omega - mu) ** 2

    sigma_b_sq = np.zeros(256, dtype=np.float64)
    valid_mask = denom > 1e-12
    sigma_b_sq[valid_mask] = numer[valid_mask] / denom[valid_mask]

    max_val = np.max(sigma_b_sq)
    if max_val > 0.0:
        candidates = np.where(np.isclose(sigma_b_sq, max_val, rtol=1e-5, atol=1e-7))[0]
        optimal_t = int(np.round(np.mean(candidates)))
    else:
        optimal_t = 0

    eta = float(sigma_b_sq[optimal_t] / sigma_t_sq) if sigma_t_sq > 1e-9 else 0.0
    eta = float(np.clip(eta, 0.0, 1.0))

    return {
        'hist': hist,
        'p': p,
        'omega': omega,
        'mu': mu,
        'mu_t': mu_t,
        'sigma_b_sq': sigma_b_sq,
        'sigma_t_sq': sigma_t_sq,
        'optimal_t': optimal_t,
        'eta': eta,
    }
