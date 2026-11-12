"""
Module filters.py: Toàn bộ hệ thống các bộ lọc khử nhiễu không gian và lọc đốm SAR thuần NumPy (Nhóm A - Đề 2).
BTL Xử lý ảnh - Khoa CNTT, Đại học Giao thông Vận tải (UTC)
"""

import numpy as np

from src.validation import gray_image, odd_window, positive


def _pad_reflect(image: np.ndarray, pad_w: int) -> np.ndarray:
    """Đệm biên phản xạ bằng pure NumPy."""
    return np.pad(image, pad_w, mode="reflect")


def _box_filter_2d(image: np.ndarray, size: int) -> np.ndarray:
    """
    Lọc trung bình (Box filter) tối ưu mảng tích lũy Integral Image O(1) thuần NumPy.
    Giáo trình UTC: Chương 3.1 - Slide 93-99.
    """
    h, w = image.shape
    r = size // 2
    padded = _pad_reflect(image, r)

    integral = np.pad(
        padded.cumsum(axis=0).cumsum(axis=1), ((1, 0), (1, 0)), mode="constant", constant_values=0
    )

    D = integral[2 * r + 1 : h + 2 * r + 1, 2 * r + 1 : w + 2 * r + 1]
    A = integral[0:h, 0:w]
    B = integral[0:h, 2 * r + 1 : w + 2 * r + 1]
    C = integral[2 * r + 1 : h + 2 * r + 1, 0:w]

    patch_sum = D + A - B - C
    return patch_sum / float(size * size)


def custom_box_filter(image: np.ndarray, window_size: int = 5) -> np.ndarray:
    """Lọc trung bình 2D thuần NumPy."""
    image = gray_image(image)
    odd_window(window_size)
    img_f = image.astype(np.float64)
    out = _box_filter_2d(img_f, window_size)
    return np.clip(np.round(out), 0, 255).astype(np.uint8)


def custom_gaussian_filter(
    image: np.ndarray, window_size: int = 5, sigma: float = 1.0
) -> np.ndarray:
    """
    Lọc Gauss (Gaussian Filter) 2D tách được (separable) thuần NumPy.
    Giáo trình UTC: Chương 3.1 - Slide 97-100.
    """
    odd_window(window_size)
    r = window_size // 2
    positive(sigma, "sigma")
    x = np.arange(-r, r + 1, dtype=np.float64)
    kernel_1d = np.exp(-(x**2) / (2.0 * sigma**2))
    kernel_1d /= np.sum(kernel_1d)

    image = gray_image(image)
    odd_window(window_size)
    img_f = image.astype(np.float64)
    h, w = img_f.shape

    # 1. Lọc theo hàng
    padded_h = np.pad(img_f, ((0, 0), (r, r)), mode="reflect")
    temp = np.zeros((h, w), dtype=np.float64)
    for i, k in enumerate(kernel_1d):
        temp += k * padded_h[:, i : i + w]

    # 2. Lọc theo cột
    padded_v = np.pad(temp, ((r, r), (0, 0)), mode="reflect")
    out = np.zeros((h, w), dtype=np.float64)
    for i, k in enumerate(kernel_1d):
        out += k * padded_v[i : i + h, :]

    return np.clip(np.round(out), 0, 255).astype(np.uint8)


def custom_median_filter(image: np.ndarray, window_size: int = 5) -> np.ndarray:
    """
    Lọc trung vị (Median Filter) thuần NumPy.
    Giáo trình UTC: Chương 3.1 - Slide 104-106.
    """
    odd_window(window_size)
    r = window_size // 2
    padded = _pad_reflect(image.astype(np.float64), r)

    from numpy.lib.stride_tricks import sliding_window_view

    windows = sliding_window_view(padded, (window_size, window_size))
    medians = np.median(windows, axis=(-2, -1))
    return np.clip(np.round(medians), 0, 255).astype(np.uint8)


def custom_bilateral_filter(
    image: np.ndarray,
    window_size: int = 5,
    sigma_s: float = 3.0,
    sigma_r: float = 25.0,
) -> np.ndarray:
    """
    Bộ lọc hai chiều Bilateral Filter bảo toàn biên thuần NumPy.
    Đề 2 Nhóm A trong ds btl xla VÀ HƯỚNG DẪN.docx.

    Trọng số lọc kết hợp khoảng cách không gian d(i,j) và chênh lệch độ xám |I(i,j) - I(x,y)|:
        w(i, j) = exp(-d(i,j)^2 / (2*sigma_s^2)) * exp(-(I(i,j) - I(x,y))^2 / (2*sigma_r^2))
    """
    image = gray_image(image)
    odd_window(window_size)
    img_f = image.astype(np.float64)
    h, w = img_f.shape
    odd_window(window_size)
    r = window_size // 2

    # Trọng số không gian Gauss cố định
    y, x = np.ogrid[-r : r + 1, -r : r + 1]
    spatial_dist2 = x**2 + y**2
    positive(sigma_s, "sigma_s")
    positive(sigma_r, "sigma_r")
    spatial_weights = np.exp(-spatial_dist2 / (2.0 * sigma_s**2))

    padded = _pad_reflect(img_f, r)
    from numpy.lib.stride_tricks import sliding_window_view

    windows = sliding_window_view(padded, (window_size, window_size))

    # Chênh lệch độ xám giữa từng pixel trong cửa sổ và pixel trung tâm img_f
    center_val = img_f[:, :, np.newaxis, np.newaxis]
    range_diff2 = (windows - center_val) ** 2
    range_weights = np.exp(-range_diff2 / (2.0 * sigma_r**2))

    total_weights = spatial_weights[np.newaxis, np.newaxis, :, :] * range_weights
    weight_sum = np.sum(total_weights, axis=(-2, -1))

    filtered = np.sum(windows * total_weights, axis=(-2, -1)) / np.maximum(weight_sum, 1e-8)
    return np.clip(np.round(filtered), 0, 255).astype(np.uint8)


def custom_lee_filter(
    image: np.ndarray,
    window_size: int = 5,
    num_looks: float = 4.0,
) -> np.ndarray:
    """
    Bộ lọc đốm thích nghi Lee Filter (MMSE) thuần NumPy.
    Mô hình đốm nhân SAR I = R * eta với Var(eta) = 1/num_looks.
    Giáo trình UTC: Chương 3.1 & 3.2.
    """
    image = gray_image(image)
    odd_window(window_size)
    img_f = image.astype(np.float64)
    positive(num_looks, "num_looks")
    sigma_v2 = 1.0 / float(num_looks)

    mean_I = _box_filter_2d(img_f, window_size)
    mean_I2 = _box_filter_2d(img_f**2, window_size)
    var_I = np.maximum(mean_I2 - (mean_I**2), 0.0)

    denom = np.where(var_I > 1e-8, var_I, 1e-8)
    noise_var = (mean_I**2) * sigma_v2
    K = np.clip(1.0 - (noise_var / denom), 0.0, 1.0)

    R_hat = mean_I + K * (img_f - mean_I)
    return np.clip(np.round(R_hat), 0, 255).astype(np.uint8)


def custom_frost_filter(
    image: np.ndarray,
    window_size: int = 5,
    damping_factor: float = 2.0,
) -> np.ndarray:
    """
    Bộ lọc Frost Filter bảo toàn biên dựa trên hàm trọng số mũ khoảng cách.
    """
    image = gray_image(image)
    odd_window(window_size)
    img_f = image.astype(np.float64)
    h, w = img_f.shape
    odd_window(window_size)
    r = window_size // 2

    mean_I = _box_filter_2d(img_f, window_size)
    mean_I2 = _box_filter_2d(img_f**2, window_size)
    var_I = np.maximum(mean_I2 - (mean_I**2), 0.0)
    std_I = np.sqrt(var_I)

    coeff_var = std_I / np.maximum(mean_I, 1e-6)

    y, x = np.ogrid[-r : r + 1, -r : r + 1]
    dist = np.sqrt(x**2 + y**2)

    padded = _pad_reflect(img_f, r)
    from numpy.lib.stride_tricks import sliding_window_view

    windows = sliding_window_view(padded, (window_size, window_size))

    B = (damping_factor * coeff_var)[:, :, np.newaxis, np.newaxis]
    dist_4d = dist[np.newaxis, np.newaxis, :, :]

    weights = np.exp(-B * dist_4d)
    w_sum = np.sum(weights, axis=(-2, -1), keepdims=True)
    norm_weights = weights / np.maximum(w_sum, 1e-8)

    filtered = np.sum(windows * norm_weights, axis=(-2, -1))
    return np.clip(np.round(filtered), 0, 255).astype(np.uint8)


def custom_kuan_filter(
    image: np.ndarray,
    window_size: int = 5,
    num_looks: float = 4.0,
) -> np.ndarray:
    """
    Bộ lọc Kuan Filter (MMSE không tuyến tính hóa) thuần NumPy.
    """
    image = gray_image(image)
    odd_window(window_size)
    img_f = image.astype(np.float64)
    positive(num_looks, "num_looks")
    Cu2 = 1.0 / float(num_looks)

    mean_I = _box_filter_2d(img_f, window_size)
    mean_I2 = _box_filter_2d(img_f**2, window_size)
    var_I = np.maximum(mean_I2 - (mean_I**2), 0.0)

    Ci2 = var_I / np.maximum(mean_I**2, 1e-8)
    W = np.clip((1.0 - Cu2 / np.maximum(Ci2, 1e-8)) / (1.0 + Cu2), 0.0, 1.0)

    R_hat = mean_I + W * (img_f - mean_I)
    return np.clip(np.round(R_hat), 0, 255).astype(np.uint8)
