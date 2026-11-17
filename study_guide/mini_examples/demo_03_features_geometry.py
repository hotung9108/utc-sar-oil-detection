"""Demo 03: Tính toán chi tiết 8 đặc trưng hình học & cường độ trên 1 vết dầu mẫu.

Mục đích:
- Tạo một vết dầu hình elip uốn lượn chéo góc trên lưới pixel 30x30.
- Tính toán tường tận 8 đặc trưng: Elongation qua trị riêng ma trận hiệp phương sai,
  Complexity qua bất đẳng thức đẳng chu, Gradient Sobel và Vành nền cục bộ 5px.
"""

import numpy as np


def run_demo():
    print("=" * 75)
    print("DEMO 03: TÍNH TOÁN 8 ĐẶC TRƯNG HÌNH HỌC & CƯỜNG ĐỘ TRÊN VẾT DẦU MẪU")
    print("=" * 75)

    H, W = 30, 30
    # 1. Tạo ảnh nền biển có mức xám trung bình 120 (kèm nhiễu nhẹ)
    np.random.seed(42)
    image = np.random.normal(loc=120.0, scale=10.0, size=(H, W))

    # 2. Tạo một vết dầu hình elip nghiêng 45 độ (mức xám tối ~ 25)
    # Phương trình elip xoay: ((x-xc)*cos - (y-yc)*sin)^2 / a^2 + ((x-xc)*sin + (y-yc)*cos)^2 / b^2 <= 1
    xc, yc = 15, 15
    a_axis, b_axis = 8, 3  # Trục dài 8, trục ngắn 3 (rất thuôn dài)
    angle = np.pi / 4  # Nghiêng 45 độ

    mask = np.zeros((H, W), dtype=bool)
    for y in range(H):
        for x in range(W):
            x_rot = (x - xc) * np.cos(angle) + (y - yc) * np.sin(angle)
            y_rot = -(x - xc) * np.sin(angle) + (y - yc) * np.cos(angle)
            if (x_rot / a_axis) ** 2 + (y_rot / b_axis) ** 2 <= 1.0:
                mask[y, x] = True
                image[y, x] = np.random.normal(loc=25.0, scale=3.0)  # Vết dầu tối

    print("\n1. MÔ PHỎNG VẾT DẦU HÌNH ELIP NGHIÊNG 45 ĐỘ TRÊN LƯỚI 30x30:")
    for y in range(H):
        line = "".join(["██" if mask[y, x] else "··" for x in range(W)])
        print(f" {line}")

    # Lấy tọa độ các pixel của vết dầu
    y_coords, x_coords = np.nonzero(mask)
    area = len(x_coords)
    print(f"\n👉 Tổng diện tích vết dầu: A = {area} pixel")

    # =========================================================================
    # TÍNH TOÁN TỪNG ĐẶC TRƯNG
    # =========================================================================

    # ĐẶC TRƯNG 1: Tỷ lệ diện tích (area_fraction)
    area_fraction = area / (H * W)

    # ĐẶC TRƯNG 2: Độ thuôn dài (elongation) qua ma trận hiệp phương sai
    x_centered = x_coords - x_coords.mean()
    y_centered = y_coords - y_coords.mean()
    coords = np.stack([x_centered, y_centered])
    cov_matrix = (coords @ coords.T) / area
    eigenvalues = np.linalg.eigvalsh(cov_matrix)  # lambda2 <= lambda1
    elongation = np.sqrt((eigenvalues[1] + 1e-6) / (eigenvalues[0] + 1e-6))

    # Tỉ số bounding box thông thường (để so sánh thấy sự vượt trội của Eigenvalues):
    w_bbox = x_coords.max() - x_coords.min() + 1
    h_bbox = y_coords.max() - y_coords.min() + 1
    bbox_ratio = max(w_bbox, h_bbox) / min(w_bbox, h_bbox)

    # ĐẶC TRƯNG 3: Độ lấp đầy hộp bao (extent)
    extent = area / (w_bbox * h_bbox)

    # ĐẶC TRƯNG 4: Độ phức tạp đường biên (complexity = P^2 / 4*pi*A)
    # Tính chu vi chính xác bằng hiệu sai phân lưới tiếp giáp bên ngoài
    padded_mask = np.pad(mask.astype(np.int8), 1)
    perimeter = np.abs(np.diff(padded_mask, axis=0)).sum() + np.abs(np.diff(padded_mask, axis=1)).sum()
    complexity = (perimeter**2) / (4.0 * np.pi * area)

    # ĐẶC TRƯNG 5 & 6: Mean và Std nội vùng
    mean_val = float(image[mask].mean())
    std_val = float(image[mask].std())

    # ĐẶC TRƯNG 7: Độ dốc biên Sobel (boundary_gradient)
    # Bộ lọc Sobel 3x3
    sx = np.array([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]], dtype=float) / 8.0
    from scipy.signal import correlate2d

    gx = correlate2d(image, sx, mode="same")
    gy = correlate2d(image, sx.T, mode="same")
    grad_magnitude = np.hypot(gx, gy)

    # Đường biên mỏng 1 pixel (Dùng phép Co erosion)
    from scipy.ndimage import binary_erosion

    boundary = mask & ~binary_erosion(mask)
    boundary_gradient = float(grad_magnitude[boundary].mean())

    # ĐẶC TRƯNG 8: Tương phản vành nền cục bộ 5px (background_contrast)
    from scipy.ndimage import binary_dilation

    dilated = binary_dilation(mask, iterations=5)
    ring = dilated & ~mask  # Vành đai 5px bao quanh vết dầu
    bg_mean = float(image[ring].mean())
    background_contrast = (bg_mean - mean_val) / (abs(bg_mean) + 1e-6)

    # =========================================================================
    # IN KẾT QUẢ TỔNG HỢP
    # =========================================================================
    print("\n" + "=" * 75)
    print("BẢNG TỔNG HỢP 8 ĐẶC TRƯNG CỦA VẾT DẦU MẪU:")
    print("=" * 75)
    print(f" 1. area_fraction      = {area_fraction:.4f}  (Chiếm {area_fraction*100:.1f}% diện tích toàn ảnh)")
    print(f" 2. elongation         = {elongation:.4f}  (Trị riêng ma trận hiệp phương sai)")
    print(f"    [Đối chứng BBox    = {bbox_ratio:.4f}]  <-- BBox bị lừa vì elip nghiêng 45 độ!")
    print(f" 3. extent             = {extent:.4f}  (Tỷ lệ lấp đầy hộp bao)")
    print(f" 4. complexity         = {complexity:.4f}  (Thương số đẳng chu P^2/4piA)")
    print(f" 5. mean               = {mean_val:.2f}  (Mức xám trung bình nội vùng)")
    print(f" 6. std                = {std_val:.2f}  (Độ lệch chuẩn nội vùng)")
    print(f" 7. boundary_gradient  = {boundary_gradient:.2f}  (Độ dốc bước nhảy tại viền biên)")
    print(f" 8. background_contrast= {background_contrast:.4f}  (Tối hơn nền biển lân cận {background_contrast*100:.1f}%)")
    print("=" * 75)


if __name__ == "__main__":
    run_demo()
