"""MODULE 1: DATA LOADER & RADIOMETRIC NORMALIZATION (NUMPY THUẦN)

Module này cung cấp các hàm đọc dữ liệu, chuyển đổi thang đo dB,
và tự cài đặt thuật toán nội suy góc tới Bilinear Interpolation.
"""
from __future__ import annotations
import numpy as np


def read_sar_image_from_array(arr: np.ndarray) -> np.ndarray:
    """Chuẩn hóa mảng đầu vào về dạng ma trận 2D số thực float64 [0.0, 1.0].

    Args:
        arr: Mảng NumPy bất kỳ (2D hoặc 3D RGB).

    Returns:
        Ma trận 2D float64 với miền giá trị trong đoạn [0.0, 1.0].
    """
    img = np.asarray(arr, dtype=np.float64)
    # Nếu ảnh là ảnh màu 3 kênh (H, W, 3), chuyển về ảnh xám theo công thức ITU-R 601-2
    if img.ndim == 3:
        img = 0.299 * img[:, :, 0] + 0.587 * img[:, :, 1] + 0.114 * img[:, :, 2]

    # Nếu dữ liệu ở dạng uint8 [0, 255], co về [0.0, 1.0]
    if img.max() > 1.0:
        img = img / 255.0

    return np.clip(img, 0.0, 1.0)


def linear_to_db(linear_val: np.ndarray, eps: float = 1e-7) -> np.ndarray:
    """Chuyển đổi cường độ tán xạ từ thang tuyến tính sang thang Logarit Decibel (dB).

    Công thức: sigma_dB = 10 * log10(max(sigma_linear, eps))
    """
    safe_linear = np.maximum(linear_val, eps)
    return 10.0 * np.log10(safe_linear)


def db_to_linear(db_val: np.ndarray) -> np.ndarray:
    """Chuyển đổi từ thang Decibel (dB) về lại thang tuyến tính (Linear).

    Công thức: sigma_linear = 10^(sigma_dB / 10)
    """
    return np.power(10.0, db_val / 10.0)


def bilinear_interpolate_lut(
    lut_grid: np.ndarray,
    target_shape: tuple[int, int]
) -> np.ndarray:
    """Tự code thuật toán nội suy song tuyến tính (Bilinear Interpolation) từ bảng LUT góc tới.

    Vệ tinh Sentinel-1 chỉ cung cấp góc tới trên lưới thưa (ví dụ 10x10 điểm).
    Hàm này sẽ nội suy mượt mà thành ma trận dày đặc đúng kích thước ảnh (H, W).

    Args:
        lut_grid: Ma trận lưới thưa kích thước (h_lut, w_lut).
        target_shape: Cặp kích thước đích (H, W) cần phủ kín.

    Returns:
        Ma trận góc tới dày đặc kích thước (H, W) tính bằng radian.
    """
    H, W = target_shape
    h_lut, w_lut = lut_grid.shape

    # Tọa độ tỷ đối của lưới đích [0, h_lut - 1] và [0, w_lut - 1]
    r_coords = np.linspace(0, h_lut - 1, H)
    c_coords = np.linspace(0, w_lut - 1, W)

    # Chỉ số 4 đỉnh bao quanh (r0, c0) và (r1, c1)
    r0 = np.floor(r_coords).astype(int)
    r1 = np.minimum(r0 + 1, h_lut - 1)
    c0 = np.floor(c_coords).astype(int)
    c1 = np.minimum(c0 + 1, w_lut - 1)

    # Trọng số nội suy theo phương dọc và phương ngang
    dr = (r_coords - r0)[:, np.newaxis]  # Kích thước (H, 1)
    dc = (c_coords - c0)[np.newaxis, :]  # Kích thước (1, W)

    # Trích xuất 4 góc lưới
    top_left = lut_grid[r0[:, np.newaxis], c0[np.newaxis, :]]
    top_right = lut_grid[r0[:, np.newaxis], c1[np.newaxis, :]]
    bottom_left = lut_grid[r1[:, np.newaxis], c0[np.newaxis, :]]
    bottom_right = lut_grid[r1[:, np.newaxis], c1[np.newaxis, :]]

    # Nội suy 2 chiều: f(r, c) = (1-dr)(1-dc)*TL + (1-dr)*dc*TR + dr*(1-dc)*BL + dr*dc*BR
    interpolated = (
        (1.0 - dr) * (1.0 - dc) * top_left +
        (1.0 - dr) * dc * top_right +
        dr * (1.0 - dc) * bottom_left +
        dr * dc * bottom_right
    )
    return interpolated


def correct_incidence_angle_gamma0(
    sigma0_linear: np.ndarray,
    theta_rad: np.ndarray
) -> np.ndarray:
    """Hiệu chỉnh góc tới để tính hệ số phản xạ diện tích Gamma-nought (gamma0).

    Công thức: gamma0 = sigma0 / cos(theta)

    Args:
        sigma0_linear: Cường độ tán xạ ngược tuyến tính (float64).
        theta_rad: Góc tới tính bằng Radian tại mỗi pixel (float64).

    Returns:
        Ma trận gamma0 đã chuẩn hóa hình học.
    """
    cos_theta = np.cos(theta_rad)
    # Bảo vệ chống chia cho 0 ở các góc cực đoan sát 90 độ
    cos_theta = np.maximum(cos_theta, 1e-4)
    return sigma0_linear / cos_theta


# ==============================================================================
# BÀI TẬP THỰC HÀNH TỰ KIỂM TRA
# ==============================================================================
if __name__ == "__main__":
    print("--- [MODULE 1] KIỂM TRA DỮ LIỆU VÀ GÓC TỚI ---")
    # 1. Giả lập một bảng LUT góc tới 3x3 điểm (từ 30 độ đến 45 độ)
    lut_degrees = np.array([
        [30.0, 37.5, 45.0],
        [30.2, 37.7, 45.2],
        [30.5, 38.0, 45.5]
    ])
    lut_radians = np.deg2rad(lut_degrees)

    # 2. Nội suy lên kích thước ảnh thực tế (100x100)
    theta_matrix = bilinear_interpolate_lut(lut_radians, (100, 100))
    print(f" -> Kích thước ma trận sau nội suy: {theta_matrix.shape}")
    print(f" -> Góc tới ở cột đầu tiên (Near range): {np.rad2deg(theta_matrix[0, 0]):.2f} độ")
    print(f" -> Góc tới ở cột cuối cùng (Far range): {np.rad2deg(theta_matrix[0, -1]):.2f} độ")

    # 3. Thử nghiệm chuẩn hóa gamma0
    sigma_mock = np.ones((100, 100)) * 0.1
    gamma_mock = correct_incidence_angle_gamma0(sigma_mock, theta_matrix)
    print(f" -> Tỷ lệ gamma0/sigma0 tại Near range: {gamma_mock[0, 0] / sigma_mock[0, 0]:.3f}")
    print(f" -> Tỷ lệ gamma0/sigma0 tại Far range : {gamma_mock[0, -1] / sigma_mock[0, -1]:.3f}")
    print("✅ MODULE 1 HOẠT ĐỘNG HOÀN HẢO!")
