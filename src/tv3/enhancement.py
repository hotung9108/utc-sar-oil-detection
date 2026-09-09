"""
Module enhancement.py: Các phương pháp tăng cường tương phản ảnh và cân bằng histogram thuần NumPy.
BTL Xử lý ảnh - Đề tài Nhóm A: Tăng cường và lọc ảnh.
Khoa CNTT - Đại học Giao thông Vận tải (UTC)
"""

from typing import Optional, Tuple

import numpy as np


def log_transform(image: np.ndarray, c: Optional[float] = None) -> np.ndarray:
    """
    Biến đổi điểm dùng hàm logarit nén dải động và kéo giãn vùng tối.
    Giáo trình UTC: Chương 3.1 - Slide 10-14.
    Công thức: s = c * log(1 + r)
    """
    img_f = image.astype(np.float64)
    r_max = np.max(img_f)
    if c is None:
        c = 255.0 / np.log(1.0 + max(r_max, 1.0))

    s = c * np.log(1.0 + img_f)
    return np.clip(np.round(s), 0, 255).astype(np.uint8)


def global_histogram_equalization(image: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """
    Cân bằng Histogram toàn cục (Global Histogram Equalization - HE) thuần NumPy.
    Giáo trình UTC: Chương 3.1 - Slide 29-36.

    Công thức:
        p(r_k) = n_k / n
        s_k = round( (L - 1) * sum_{j=0}^k p(r_j) )

    Trả về:
        Tuple[np.ndarray, np.ndarray]: (ảnh sau cân bằng uint8, bảng ánh xạ LUT 256 phần tử).
    """
    img_u8 = image.astype(np.uint8)
    total_pixels = img_u8.size
    if np.ptp(img_u8) == 0:
        return img_u8.copy(), np.arange(256, dtype=np.uint8)

    # 1. Tính histogram
    hist = np.bincount(img_u8.ravel(), minlength=256).astype(np.float64)

    # 2. Tính hàm phân bố tích lũy CDF
    cdf = np.cumsum(hist)

    # 3. Chuẩn hóa ánh xạ mức xám mới [0, 255]
    cdf_min = cdf[cdf > 0][0] if np.any(cdf > 0) else 0
    lut = np.round((cdf - cdf_min) / max(total_pixels - cdf_min, 1) * 255.0)
    lut = np.clip(lut, 0, 255).astype(np.uint8)

    # Ánh xạ pixel qua bảng tra cứu LUT
    equalized_img = lut[img_u8]
    return equalized_img, lut


def custom_clahe(image, clip_limit=2.0, tile_grid_size=(8, 8)):
    """TV3: NumPy CLAHE, 256-bin integer clipping and bilinear LUT interpolation.

    grid=(rows, columns). Reflect-101 padding makes tiles equal sized.
    clip_limit is normalized by tile area / 256; <=0 disables clipping.
    Redistribution uses quotient and uniformly spaced residual counts.
    The OpenCV comparison reverses grid to (columns, rows).
    """
    from src.validation import gray_image

    img = gray_image(image)
    rows, cols = tile_grid_size
    if any(int(n) != n or n < 1 for n in (rows, cols)):
        raise ValueError("Grid dimensions must be positive integers")
    if not np.isfinite(clip_limit):
        raise ValueError("clip_limit must be finite")
    h, w = img.shape
    if h % rows or w % cols:
        padded = np.pad(img, ((0, rows - h % rows), (0, cols - w % cols)), mode="reflect")
    else:
        padded = img
    th, tw = padded.shape[0] // rows, padded.shape[1] // cols
    lut = np.empty((rows, cols, 256), dtype=np.uint8)
    scale = np.float32(255.0 / (th * tw))
    for y in range(rows):
        for x in range(cols):
            hist = np.bincount(
                padded[y * th : (y + 1) * th, x * tw : (x + 1) * tw].ravel(), minlength=256
            )
            if clip_limit > 0:
                limit = max(int(clip_limit * th * tw / 256), 1)
                excess = int(np.maximum(hist - limit, 0).sum())
                hist = np.minimum(hist, limit)
                batch, residual = divmod(excess, 256)
                hist += batch
                if residual:
                    step = max(256 // residual, 1)
                    hist[np.arange(0, 256, step)[:residual]] += 1
            lut[y, x] = np.clip(np.rint(hist.cumsum().astype(np.float32) * scale), 0, 255)
    yy = np.arange(h, dtype=np.float32) / np.float32(th) - np.float32(0.5)
    xx = np.arange(w, dtype=np.float32) / np.float32(tw) - np.float32(0.5)
    y0, x0 = np.floor(yy).astype(int), np.floor(xx).astype(int)
    wy, wx = (yy - y0).astype(np.float32)[:, None], (xx - x0).astype(np.float32)[None, :]
    y1, x1 = np.clip(y0 + 1, 0, rows - 1), np.clip(x0 + 1, 0, cols - 1)
    y0, x0 = np.clip(y0, 0, rows - 1), np.clip(x0, 0, cols - 1)
    top = lut[y0[:, None], x0[None, :], img] * (1 - wx) + lut[y0[:, None], x1[None, :], img] * wx
    bottom = lut[y1[:, None], x0[None, :], img] * (1 - wx) + lut[y1[:, None], x1[None, :], img] * wx
    return np.clip(np.rint(top * (1 - wy) + bottom * wy), 0, 255).astype(np.uint8)


def homomorphic_filter(
    image: np.ndarray,
    gamma_l: float = 0.5,
    gamma_h: float = 1.5,
    c: float = 1.0,
    d0: float = 30.0,
) -> np.ndarray:
    """
    Bộ lọc đồng hình (Homomorphic Filtering) miền tần số DFT để triệt tiêu nhiễu nhân đốm SAR.
    Giáo trình UTC: Chương 3.2 - Slide 37 (Lọc đồng hình khử nhiễu nhân I = R * eta).

    Công thức bộ lọc Gauss miền tần số:
        H(u, v) = (gamma_h - gamma_l) * [1 - exp(-c * (D(u, v)^2 / d0^2))] + gamma_l
    """
    img_f = image.astype(np.float64)
    h, w = img_f.shape

    # 1. Lấy logarit tự nhiên (chuyển nhân sang cộng)
    log_img = np.log1p(img_f)

    # 2. Biến đổi Fourier 2D
    fft_img = np.fft.fft2(log_img)
    fft_shifted = np.fft.fftshift(fft_img)

    # 3. Tạo mặt nạ lọc Gauss tần số H(u, v)
    u = np.arange(h) - h // 2
    v = np.arange(w) - w // 2
    U, V = np.meshgrid(u, v, indexing="ij")
    D2 = U**2 + V**2

    H = (gamma_h - gamma_l) * (1.0 - np.exp(-c * (D2 / (d0**2)))) + gamma_l

    # 4. Áp dụng lọc trong miền tần số
    filtered_fft = fft_shifted * H

    # 5. Biến đổi ngược IFFT2D
    ifft_shifted = np.fft.ifftshift(filtered_fft)
    ifft_img = np.fft.ifft2(ifft_shifted)
    real_part = np.real(ifft_img)

    # 6. Lấy hàm mũ exp
    enhanced = np.expm1(real_part)

    # Chuẩn hóa về dải [0, 255]
    c_min, c_max = np.min(enhanced), np.max(enhanced)
    if c_max - c_min > 1e-8:
        norm = (enhanced - c_min) / (c_max - c_min) * 255.0
    else:
        norm = np.zeros_like(enhanced)

    return np.clip(np.round(norm), 0, 255).astype(np.uint8)
