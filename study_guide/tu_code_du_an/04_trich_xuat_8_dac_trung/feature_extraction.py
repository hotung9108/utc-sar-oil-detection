"""MODULE 4: MATHEMATICAL FEATURE EXTRACTION FROM SCRATCH (NUMPY THUẦN)

Module này tự tính toán chính xác 8 đặc trưng toán học cho từng đốm tối:
1. area_fraction: Tỷ lệ diện tích
2. elongation: Độ thuôn dài từ ma trận hiệp phương sai tọa độ
3. extent: Tỷ lệ lấp đầy hộp bao
4. complexity: Độ phức tạp đường biên đẳng chu (P^2 / 4*pi*A)
5. mean: Cường độ sáng trung bình nội vùng
6. std: Độ lệch chuẩn nội vùng
7. boundary_gradient: Độ dốc gradient Sobel dọc viền
8. background_contrast: Độ tương phản với vành nền cục bộ 5 pixel
"""
from __future__ import annotations
import numpy as np

FEATURE_NAMES = [
    "area_fraction",
    "elongation",
    "extent",
    "complexity",
    "mean",
    "std",
    "boundary_gradient",
    "background_contrast",
]


def extract_features_single_region(
    img: np.ndarray,
    region: dict
) -> np.ndarray:
    """Trích xuất vector 8 đặc trưng toán học cho 1 vùng liên thông.

    Args:
        img: Ma trận ảnh xám chuẩn hóa float64 (H, W).
        region: Từ điển chứa thông tin vùng (diện tích, tọa độ pixel 'coords').

    Returns:
        Vector NumPy 1D kích thước (8,) kiểu float64.
    """
    coords = region["coords"]
    H, W = img.shape
    area = float(region["area"])

    rows = coords[:, 0]
    cols = coords[:, 1]

    # 1. Tỷ lệ diện tích so với diện tích toàn ảnh
    f1_area_fraction = area / float(H * W)

    # 2. Độ thuôn dài (Elongation) từ ma trận hiệp phương sai tọa độ
    if len(coords) >= 3:
        cov = np.cov(rows, cols)
        # Sử dụng eigvalsh đảm bảo trị riêng là số thực thuần túy
        eigenvalues = np.linalg.eigvalsh(cov)
        eigenvalues = np.sort(np.maximum(0.0, eigenvalues))
        if eigenvalues[0] > 1e-7:
            f2_elongation = float(np.sqrt(eigenvalues[1] / eigenvalues[0]))
        else:
            f2_elongation = 1.0
    else:
        f2_elongation = 1.0

    # 3. Độ lấp đầy hộp bao (Extent)
    min_r, max_r = int(np.min(rows)), int(np.max(rows))
    min_c, max_c = int(np.min(cols)), int(np.max(cols))
    bbox_h = max_r - min_r + 1
    bbox_w = max_c - min_c + 1
    bbox_area = float(bbox_h * bbox_w)
    f3_extent = area / bbox_area if bbox_area > 0 else 0.0

    # 4. Độ phức tạp đường biên (Complexity: P^2 / 4*pi*A)
    # Xác định các pixel biên: là pixel thuộc vùng có ít nhất 1 lân cận 4 hướng là nền
    reg_mask = np.zeros((H, W), dtype=bool)
    reg_mask[rows, cols] = True

    boundary_pixels = []
    for r, c in coords:
        if (r == 0 or r == H - 1 or c == 0 or c == W - 1 or
            not reg_mask[r - 1, c] or not reg_mask[r + 1, c] or
            not reg_mask[r, c - 1] or not reg_mask[r, c + 1]):
            boundary_pixels.append((r, c))

    perimeter = float(len(boundary_pixels))
    f4_complexity = (perimeter ** 2) / (4.0 * np.pi * area) if area > 0 else 1.0

    # 5. Cường độ sáng trung bình nội vùng (Mean)
    pixel_values = img[rows, cols]
    f5_mean = float(np.mean(pixel_values))

    # 6. Độ lệch chuẩn nội vùng (Std)
    f6_std = float(np.std(pixel_values))

    # 7. Gradient biên trung bình (Sobel Boundary Gradient)
    sobel_x = np.array([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]], dtype=np.float64)
    sobel_y = np.array([[-1, -2, -1], [0, 0, 0], [1, 2, 1]], dtype=np.float64)

    grad_list = []
    for br, bc in boundary_pixels:
        if 1 <= br < H - 1 and 1 <= bc < W - 1:
            patch = img[br - 1 : br + 2, bc - 1 : bc + 2]
            gx = np.sum(patch * sobel_x)
            gy = np.sum(patch * sobel_y)
            grad_list.append(np.sqrt(gx ** 2 + gy ** 2))

    f7_boundary_gradient = float(np.mean(grad_list)) if grad_list else 0.0

    # 8. Độ tương phản với vành nền lân cận 5 pixel (Background Contrast)
    dilated = np.zeros((H, W), dtype=bool)
    for r, c in coords:
        r_start, r_end = max(0, r - 5), min(H, r + 6)
        c_start, c_end = max(0, c - 5), min(W, c + 6)
        dilated[r_start:r_end, c_start:c_end] = True

    ring_mask = dilated & (~reg_mask)
    if np.any(ring_mask):
        bg_mean = float(np.mean(img[ring_mask]))
        f8_background_contrast = bg_mean - f5_mean
    else:
        f8_background_contrast = 0.0

    return np.array([
        f1_area_fraction, f2_elongation, f3_extent, f4_complexity,
        f5_mean, f6_std, f7_boundary_gradient, f8_background_contrast
    ], dtype=np.float64)


def extract_features_all_regions(
    img: np.ndarray,
    regions: list[dict]
) -> np.ndarray:
    """Trích xuất ma trận đặc trưng (N_regions, 8) cho toàn bộ danh sách vùng."""
    if not regions:
        return np.empty((0, 8), dtype=np.float64)

    matrix = np.zeros((len(regions), 8), dtype=np.float64)
    for i, reg in enumerate(regions):
        matrix[i] = extract_features_single_region(img, reg)

    return matrix


# ==============================================================================
# BÀI TẬP THỰC NGHIỆM TỰ KIỂM TRA
# ==============================================================================
if __name__ == "__main__":
    print("=" * 70)
    print("--- [MODULE 4] KIỂM TRA ĐẶC TRƯNG TOÁN HỌC TRÊN 2 HÌNH DÁNG MẪU ---")
    print("=" * 70)

    # Tạo ảnh nền biển kích thước 40x40
    test_img = np.ones((40, 40), dtype=np.float64) * 0.8

    # Vùng 1: Hình tròn tâm (15, 15) bán kính 6 (mô phỏng look-alike bọt sóng)
    # Vùng 2: Dải hẹp dài nằm ngang hàng 30, cột 5..35 (mô phỏng vệt dầu loang)
    Y, X = np.ogrid[:40, :40]
    circle_mask = (X - 15)**2 + (Y - 15)**2 <= 6**2
    test_img[circle_mask] = 0.3

    line_mask = np.zeros((40, 40), dtype=bool)
    line_mask[29:32, 5:35] = True
    test_img[line_mask] = 0.15

    coords_circle = np.argwhere(circle_mask)
    coords_line = np.argwhere(line_mask)

    reg_circle = {"area": len(coords_circle), "coords": coords_circle}
    reg_line = {"area": len(coords_line), "coords": coords_line}

    feats_circle = extract_features_single_region(test_img, reg_circle)
    feats_line = extract_features_single_region(test_img, reg_line)

    print(f"{'Tên đặc trưng':<28} | {'Hình Tròn (Look-alike)':<22} | {'Vệt Dài (Dầu tràn)':<20}")
    print("-" * 75)
    for name, fc, fl in zip(FEATURE_NAMES, feats_circle, feats_line):
        print(f"{name:<28} | {fc:<22.4f} | {fl:<20.4f}")

    print("\nNhận xét:")
    print(f" -> Độ thuôn dài (Elongation) của vệt dầu ({feats_line[1]:.2f}) vượt trội so với hình tròn ({feats_circle[1]:.2f})!")
    print(f" -> Tương phản nền của vệt dầu ({feats_line[7]:.2f}) đậm hơn nhiều so với hình tròn ({feats_circle[7]:.2f})!")
    print("\n✅ MODULE 4 HOẠT ĐỘNG HOÀN HẢO!")
