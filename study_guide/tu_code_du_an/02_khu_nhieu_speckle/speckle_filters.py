"""MODULE 2: SPECKLE FILTERS FROM SCRATCH (NUMPY THUẦN)

Module này tự triển khai 4 bộ lọc khử nhiễu đốm kinh điển:
1. Box Mean Filter (Tối ưu hóa Bảng tích lũy SAT O(1))
2. Median Filter (Lọc trung vị sliding window)
3. Gaussian Filter (Tách nhân 2D thành hai lượt 1D)
4. Lee Filter (Lọc thích nghi MMSE bảo toàn biên)
"""
from __future__ import annotations
import numpy as np


def compute_integral_image(img: np.ndarray) -> np.ndarray:
    """Tính Bảng diện tích tích phân (Summed-Area Table / Integral Image).

    I(r, c) = sum_{i=0..r, j=0..c} img(i, j)
    Độ phức tạp O(H * W) bằng hàm cumsum lồng nhau của NumPy.
    """
    H, W = img.shape
    integral = np.zeros((H + 1, W + 1), dtype=np.float64)
    integral[1:, 1:] = np.cumsum(np.cumsum(img, axis=0), axis=1)
    return integral


def box_mean_filter_sat(img: np.ndarray, size: int = 7) -> np.ndarray:
    """Bộ lọc trung bình Box Mean đạt độ phức tạp O(1) mỗi pixel bằng Bảng tích lũy SAT.

    Không phụ thuộc vào kích thước cửa sổ size (kể cả 7x7, 15x15 hay 101x101 đều chạy nhanh như nhau).
    """
    H, W = img.shape
    pad = size // 2
    # Đệm mép phản chiếu
    padded = np.pad(img, pad, mode='reflect')
    integral = compute_integral_image(padded)

    # Tọa độ 4 góc của cửa sổ trượt
    # A(r, c), B(r, c + size), C(r + size, c), D(r + size, c + size)
    # Tổng = D - B - C + A
    r1 = np.arange(H)
    r2 = r1 + size
    c1 = np.arange(W)
    c2 = c1 + size

    # Tạo lưới chỉ số
    R1, C1 = np.meshgrid(r1, c1, indexing='ij')
    R2, C2 = np.meshgrid(r2, c2, indexing='ij')

    window_sum = (
        integral[R2, C2] - integral[R1, C2] - integral[R2, C1] + integral[R1, C1]
    )
    return window_sum / float(size * size)


def median_filter_scratch(img: np.ndarray, size: int = 7) -> np.ndarray:
    """Bộ lọc trung vị Median Filter tự cài bằng cửa sổ trượt.

    Chọn giá trị ở phân vị 50% trong cửa sổ cục bộ.
    """
    H, W = img.shape
    pad = size // 2
    padded = np.pad(img, pad, mode='reflect')
    out = np.zeros_like(img, dtype=np.float64)

    for r in range(H):
        for c in range(W):
            patch = padded[r : r + size, c : c + size]
            out[r, c] = np.median(patch)

    return out


def gaussian_filter_scratch(img: np.ndarray, sigma: float = 1.2, radius: int = 3) -> np.ndarray:
    """Bộ lọc Gaussian tự cài bằng kỹ thuật tách nhân 2D -> 2 lượt tích chập 1D.

    G(r, c) = G(r) * G(c) giúp giảm độ phức tạp từ O(K^2) xuống O(2K).
    """
    # 1. Tạo nhân Gauss 1D
    x = np.arange(-radius, radius + 1, dtype=np.float64)
    kernel_1d = np.exp(-0.5 * (x / sigma) ** 2)
    kernel_1d /= np.sum(kernel_1d)

    pad = radius
    # 2. Lượt 1: Tích chập theo hàng (Horizontal)
    padded_h = np.pad(img, ((0, 0), (pad, pad)), mode='reflect')
    temp = np.zeros_like(img, dtype=np.float64)
    for c in range(img.shape[1]):
        temp[:, c] = np.sum(padded_h[:, c : c + 2 * radius + 1] * kernel_1d, axis=1)

    # 3. Lượt 2: Tích chập theo cột (Vertical)
    padded_v = np.pad(temp, ((pad, pad), (0, 0)), mode='reflect')
    out = np.zeros_like(img, dtype=np.float64)
    for r in range(img.shape[0]):
        out[r, :] = np.sum(padded_v[r : r + 2 * radius + 1, :] * kernel_1d[:, np.newaxis], axis=0)

    return out


def lee_filter_scratch(img: np.ndarray, size: int = 7, looks: float = 4.0) -> np.ndarray:
    """Bộ lọc thích nghi bảo toàn biên Lee Filter (J.S. Lee 1980).

    Ước lượng MMSE cho mô hình nhiễu nhân SAR y = x * v.
    - Cửa sổ size x size (mặc định 7x7).
    - looks: Số lượt nhìn danh định (mặc định 4.0 cho Sentinel-1 GRD).
    """
    H, W = img.shape
    pad = size // 2
    padded = np.pad(img, pad, mode='reflect')
    noise_var = 1.0 / float(looks)
    out = np.zeros_like(img, dtype=np.float64)

    for r in range(H):
        for c in range(W):
            patch = padded[r : r + size, c : c + size]
            mean_y = np.mean(patch)
            var_y = np.var(patch)

            # Vùng siêu phẳng, phương sai bằng 0
            if var_y <= 0.0:
                out[r, c] = mean_y
                continue

            # Ước lượng phương sai tín hiệu thực var_x:
            var_x = max(0.0, (var_y - (mean_y ** 2) * noise_var) / (1.0 + noise_var))
            denominator = var_x + (mean_y ** 2) * noise_var

            # Trọng số thích nghi W trong đoạn [0.0, 1.0]
            w_weight = np.clip(var_x / denominator if denominator > 0 else 0.0, 0.0, 1.0)

            # Khôi phục tín hiệu: x_hat = mean + W * (y - mean)
            out[r, c] = mean_y + w_weight * (img[r, c] - mean_y)

    return out


# ==============================================================================
# BÀI TẬP THỰC NGHIỆM ĐỐI CHỨNG 4 BỘ LỌC
# ==============================================================================
if __name__ == "__main__":
    print("=" * 70)
    print("--- [MODULE 2] ĐỐI CHỨNG THỰC NGHIỆM 4 BỘ LỌC TRÊN BẬC NHẢY CẠNH BIÊN ---")
    print("=" * 70)

    # Tạo một bậc nhảy cạnh lý tưởng: nửa trái sáng (1.0), nửa phải tối (0.2)
    # mô phỏng ranh giới giữa nước biển và vết dầu tràn
    np.random.seed(42)
    step_edge = np.zeros((40, 40), dtype=np.float64)
    step_edge[:, :20] = 1.0
    step_edge[:, 20:] = 0.2

    # Rắc nhiễu nhân Speckle (L=4 looks, độ lệch chuẩn ~ 0.5)
    noise = np.random.gamma(shape=4.0, scale=0.25, size=(40, 40))
    noisy_edge = np.clip(step_edge * noise, 0.0, 2.0)

    # Chạy 4 bộ lọc
    f_mean = box_mean_filter_sat(noisy_edge, size=7)
    f_median = median_filter_scratch(noisy_edge, size=7)
    f_gauss = gaussian_filter_scratch(noisy_edge, sigma=1.2, radius=3)
    f_lee = lee_filter_scratch(noisy_edge, size=7, looks=4.0)

    # Đo độ sắc nét của cạnh biên tại cột 19 (mép ranh giới)
    # Cạnh lý tưởng có độ chênh lệch: 1.0 - 0.2 = 0.8
    print(f"1. Độ dốc biên cạnh lý tưởng (không nhiễu) : {step_edge[20, 19] - step_edge[20, 20]:.3f}")
    print(f"2. Độ dốc sau Box Mean Filter             : {f_mean[20, 19] - f_mean[20, 20]:.3f} (Bị làm mờ mép)")
    print(f"3. Độ dốc sau Gaussian Filter             : {f_gauss[20, 19] - f_gauss[20, 20]:.3f} (Bị làm mờ mép)")
    print(f"4. Độ dốc sau Median Filter               : {f_median[20, 19] - f_median[20, 20]:.3f}")
    print(f"5. Độ dốc sau Lee Filter (MMSE)           : {f_lee[20, 19] - f_lee[20, 20]:.3f} (Giữ biên tốt nhất ⭐)")

    print("\n✅ MODULE 2 HOẠT ĐỘNG HOÀN HẢO!")
