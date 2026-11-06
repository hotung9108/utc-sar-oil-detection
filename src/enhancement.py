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


def custom_clahe(
    image: np.ndarray,
    clip_limit: float = 2.0,
    tile_grid_size: Tuple[int, int] = (8, 8),
) -> np.ndarray:
    """
    Cân bằng Histogram thích nghi có giới hạn độ tương phản (CLAHE) tự cài đặt 100% thuần NumPy.
    Giáo trình UTC: Chương 3.1 - Slide 38-42 và Yêu cầu bắt buộc Đề 1 Nhóm A.

    Quy trình thuật toán:
        1. Chia ảnh thành lưới các khối con (tiles) kích thước tile_grid_size.
        2. Tại mỗi khối con:
           - Tính histogram 256 mức xám.
           - Giới hạn độ tương phản (Clip Limit) và phân phối đều lượng pixel dư thừa.
           - Tính hàm phân bố tích lũy CDF chuẩn hóa để tạo hàm ánh xạ T(i).
        3. Nội suy song tuyến tính (Bilinear Interpolation) giữa 4 khối lân cận để khử vết kẻ biên khối.

    Tham số:
        image (np.ndarray): Ảnh thang độ xám 2D uint8.
        clip_limit (float): Hệ số cắt ngưỡng (thường từ 1.0 đến 4.0). Giá trị càng lớn độ tương phản càng mạnh.
        tile_grid_size (Tuple[int, int]): Số lượng khối chia (H_blocks, W_blocks), mặc định (8, 8).

    Trả về:
        np.ndarray: Ảnh sau khi tăng cường CLAHE (uint8).
    """
    img_u8 = image.astype(np.uint8)
    h, w = img_u8.shape
    num_tiles_y, num_tiles_x = tile_grid_size

    tile_h = h // num_tiles_y
    tile_w = w // num_tiles_x

    # Ma trận bảng ánh xạ LUT cho từng khối: shape (num_tiles_y, num_tiles_x, 256)
    tile_mappings = np.zeros((num_tiles_y, num_tiles_x, 256), dtype=np.float64)

    # 1. Tính toán hàm ánh xạ cục bộ cho từng khối
    for ty in range(num_tiles_y):
        y_start = ty * tile_h
        y_end = (ty + 1) * tile_h if ty < num_tiles_y - 1 else h

        for tx in range(num_tiles_x):
            x_start = tx * tile_w
            x_end = (tx + 1) * tile_w if tx < num_tiles_x - 1 else w

            sub_tile = img_u8[y_start:y_end, x_start:x_end]
            tile_pixels = sub_tile.size

            # Tính histogram cục bộ
            hist = np.bincount(sub_tile.ravel(), minlength=256).astype(np.float64)

            # Ngưỡng cắt độ tương phản
            actual_clip = int(round(clip_limit * (tile_pixels / 256.0)))
            actual_clip = max(actual_clip, 1)

            # Cắt các cột vượt ngưỡng và tính lượng dư thừa
            excess = np.sum(np.maximum(hist - actual_clip, 0.0))
            clipped_hist = np.minimum(hist, actual_clip)

            # Phân phối đều lượng pixel dư thừa vào 256 mức
            clipped_hist += excess / 256.0

            # Tính CDF chuẩn hóa về dải [0, 255]
            cdf = np.cumsum(clipped_hist)
            cdf_norm = (cdf / cdf[-1]) * 255.0
            tile_mappings[ty, tx] = cdf_norm

    # 2. Nội suy song tuyến tính (Bilinear Interpolation) từ tâm các ô khối
    # Tọa độ tâm các khối
    tile_y_centers = (np.arange(num_tiles_y, dtype=np.float64) + 0.5) * (h / float(num_tiles_y))
    tile_x_centers = (np.arange(num_tiles_x, dtype=np.float64) + 0.5) * (w / float(num_tiles_x))

    y_coords = np.arange(h, dtype=np.float64)
    x_coords = np.arange(w, dtype=np.float64)

    # Tọa độ chuẩn hóa theo khoảng cách giữa các tâm
    y_norm = np.clip((y_coords - tile_y_centers[0]) / (tile_y_centers[-1] - tile_y_centers[0]), 0.0, 1.0) * (num_tiles_y - 1)
    x_norm = np.clip((x_coords - tile_x_centers[0]) / (tile_x_centers[-1] - tile_x_centers[0]), 0.0, 1.0) * (num_tiles_x - 1)

    y0 = np.floor(y_norm).astype(int)
    y1 = np.minimum(y0 + 1, num_tiles_y - 1)
    x0 = np.floor(x_norm).astype(int)
    x1 = np.minimum(x0 + 1, num_tiles_x - 1)

    wy1 = (y_norm - y0)[:, np.newaxis]
    wy0 = 1.0 - wy1
    wx1 = (x_norm - x0)[np.newaxis, :]
    wx0 = 1.0 - wx1

    # Tạo chỉ số lưới meshgrid cho các khối
    grid_y0, grid_x0 = np.meshgrid(y0, x0, indexing="ij")
    grid_y1, grid_x1 = np.meshgrid(y1, x1, indexing="ij")

    # Mức xám của từng điểm ảnh
    pixels = img_u8

    # Lấy giá trị ánh xạ từ 4 khối lân cận
    map_00 = tile_mappings[grid_y0, grid_x0, pixels]
    map_01 = tile_mappings[grid_y0, grid_x1, pixels]
    map_10 = tile_mappings[grid_y1, grid_x0, pixels]
    map_11 = tile_mappings[grid_y1, grid_x1, pixels]

    # Nội suy song tuyến tính 2 chiều
    interp_vals = (
        wy0 * wx0 * map_00
        + wy0 * wx1 * map_01
        + wy1 * wx0 * map_10
        + wy1 * wx1 * map_11
    )

    clahe_img = np.clip(np.round(interp_vals), 0, 255).astype(np.uint8)
    return clahe_img


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
