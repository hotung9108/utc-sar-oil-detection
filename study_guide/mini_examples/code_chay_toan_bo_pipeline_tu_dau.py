"""Mã nguồn hoàn chỉnh độc lập - Tự code chay toàn bộ pipeline phát hiện dầu tràn SAR bằng NumPy.

Không phụ thuộc vào bất kỳ thư viện xử lý ảnh cao cấp nào (không OpenCV, không skimage, không sklearn).
Chỉ sử dụng NumPy thuần để người học nắm vững bản chất toán học từng bước một.

Cách chạy:
    python study_guide/mini_examples/code_chay_toan_bo_pipeline_tu_dau.py
"""
from __future__ import annotations
import numpy as np


def print_ascii_matrix(mat: np.ndarray, title: str):
    """In ma trận nhỏ trực quan dưới dạng ký tự ASCII trên màn hình terminal."""
    print(f"\n--- {title} ({mat.shape[0]}x{mat.shape[1]}) ---")
    H, W = mat.shape
    for r in range(min(H, 18)):
        line = ""
        for c in range(min(W, 36)):
            val = mat[r, c]
            if isinstance(val, (bool, np.bool_)):
                line += "██" if val else "  "
            elif val > 0.6:
                line += "░░"  # Biển sáng (phản xạ mạnh)
            elif val > 0.35:
                line += ".."  # Trung gian
            else:
                line += "██"  # Vệt dầu tối (dập tắt sóng)
        print(line)


# ==============================================================================
# BƯỚC 1: BỘ LỌC THÍCH NGHI LEE FILTER 7x7 (BẢO TOÀN BIÊN)
# ==============================================================================
def lee_filter_from_scratch(img: np.ndarray, size: int = 7, looks: float = 4.0) -> np.ndarray:
    """Khử nhiễu đốm Speckle bằng mô hình nhiễu nhân thích nghi của Lee.

    Công thức: x_hat = mean + W * (y - mean)
    Trong đó W = max(0, (var - mean^2 / looks) / (var * (1 + 1/looks)))
    """
    H, W = img.shape
    pad = size // 2
    padded = np.pad(img, pad, mode='reflect')
    filtered = np.zeros_like(img, dtype=np.float64)
    noise_var = 1.0 / looks

    for r in range(H):
        for c in range(W):
            window = padded[r : r + size, c : c + size]
            mean = np.mean(window)
            var = np.var(window)

            if var <= 0:
                filtered[r, c] = mean
                continue

            signal_var = max(0.0, (var - (mean ** 2) * noise_var) / (1.0 + noise_var))
            denominator = signal_var + (mean ** 2) * noise_var
            w_weight = np.clip(signal_var / denominator if denominator > 0 else 0.0, 0.0, 1.0)
            filtered[r, c] = mean + w_weight * (img[r, c] - mean)

    return filtered


# ==============================================================================
# BƯỚC 2: PHÂN ĐOẠN NGƯỠNG TOÀN CỤC OTSU TỰ CÀI
# ==============================================================================
def otsu_threshold_from_scratch(img: np.ndarray) -> tuple[float, np.ndarray]:
    """Tìm ngưỡng tối ưu cực đại hóa phương sai liên lớp giữa Nền biển và Vết dầu."""
    img_uint8 = np.clip(img * 255 if img.max() <= 1.0 else img, 0, 255).astype(np.uint8)
    hist, _ = np.histogram(img_uint8, bins=256, range=(0, 256))
    total_pixels = img.size

    current_max_var = -1.0
    best_threshold = 0
    weight_background = 0
    sum_background = 0
    sum_total = np.sum(np.arange(256) * hist)

    for t in range(256):
        weight_background += hist[t]
        if weight_background == 0:
            continue
        weight_foreground = total_pixels - weight_background
        if weight_foreground == 0:
            break

        sum_background += t * hist[t]
        mean_background = sum_background / weight_background
        mean_foreground = (sum_total - sum_background) / weight_foreground

        var_between = weight_background * weight_foreground * ((mean_background - mean_foreground) ** 2)
        if var_between > current_max_var:
            current_max_var = var_between
            best_threshold = t

    dark_mask = (img_uint8 < best_threshold).astype(np.uint8)
    return float(best_threshold), dark_mask


# ==============================================================================
# BƯỚC 3: GÁN NHÃN LIÊN THÔNG 8 HƯỚNG & LỌC DIỆN TÍCH TỐI THIỂU
# ==============================================================================
def connected_components_and_filter(mask: np.ndarray, min_area: int = 40) -> tuple[np.ndarray, list[dict]]:
    """Gom cụm pixel 8 hướng bằng thuật toán Loang BFS và loại bỏ các đốm bụi li ti."""
    H, W = mask.shape
    labeled = np.zeros((H, W), dtype=np.int32)
    current_label = 0
    valid_regions = []
    neighbors = [(-1,-1), (-1,0), (-1,1), (0,-1), (0,1), (1,-1), (1,0), (1,1)]

    for r in range(H):
        for c in range(W):
            if mask[r, c] == 1 and labeled[r, c] == 0:
                current_label += 1
                queue = [(r, c)]
                labeled[r, c] = current_label
                coords = [(r, c)]

                while queue:
                    curr_r, curr_c = queue.pop(0)
                    for dr, dc in neighbors:
                        nr, nc = curr_r + dr, curr_c + dc
                        if 0 <= nr < H and 0 <= nc < W:
                            if mask[nr, nc] == 1 and labeled[nr, nc] == 0:
                                labeled[nr, nc] = current_label
                                queue.append((nr, nc))
                                coords.append((nr, nc))

                area = len(coords)
                if area >= min_area:
                    valid_regions.append({
                        "label": current_label,
                        "area": area,
                        "coords": np.array(coords)
                    })
                else:
                    for cr, cc in coords:
                        labeled[cr, cc] = 0

    return labeled, valid_regions


# ==============================================================================
# BƯỚC 4: TRÍCH XUẤT 8 ĐẶC TRƯNG TOÁN HỌC BẰNG NUMPY
# ==============================================================================
def extract_8_features_from_scratch(img: np.ndarray, region: dict) -> np.ndarray:
    """Tính 8 đặc trưng hình dáng và cường độ cho một vùng đốm tối nghi dầu."""
    coords = region["coords"]
    H, W = img.shape
    area = region["area"]

    # 1. Tỷ lệ diện tích so với toàn ảnh
    f1_area_fraction = area / (H * W)

    # 2. Độ thuôn dài (Elongation) từ ma trận hiệp phương sai tọa độ
    rows = coords[:, 0]
    cols = coords[:, 1]
    cov = np.cov(rows, cols)
    eigenvalues = np.linalg.eigvalsh(cov)
    eigenvalues = np.sort(np.maximum(0.0, eigenvalues))
    f2_elongation = float(np.sqrt(eigenvalues[1] / eigenvalues[0])) if eigenvalues[0] > 1e-6 else 1.0

    # 3. Tỷ lệ lấp đầy hộp bao (Extent)
    min_r, max_r = np.min(rows), np.max(rows)
    min_c, max_c = np.min(cols), np.max(cols)
    bbox_area = (max_r - min_r + 1) * (max_c - min_c + 1)
    f3_extent = area / bbox_area if bbox_area > 0 else 0.0

    # 4. Độ phức tạp biên (Complexity: P^2 / 4*pi*A)
    reg_mask = np.zeros((H, W), dtype=bool)
    reg_mask[rows, cols] = True
    perimeter = 0
    for r, c in coords:
        if (r == 0 or r == H-1 or c == 0 or c == W-1 or
            not reg_mask[r-1, c] or not reg_mask[r+1, c] or
            not reg_mask[r, c-1] or not reg_mask[r, c+1]):
            perimeter += 1
    f4_complexity = (perimeter ** 2) / (4.0 * np.pi * area) if area > 0 else 0.0

    # 5. Cường độ sáng trung bình nội vùng (Mean)
    pixel_values = img[rows, cols]
    f5_mean = np.mean(pixel_values)

    # 6. Độ lệch chuẩn cường độ nội vùng (Std)
    f6_std = np.std(pixel_values)

    # 7. Độ dốc biên độ trung bình (Boundary Gradient bằng Sobel)
    sobel_x = np.array([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]])
    sobel_y = np.array([[-1, -2, -1], [0, 0, 0], [1, 2, 1]])
    grad_vals = []
    for r, c in coords:
        if 1 <= r < H-1 and 1 <= c < W-1:
            patch = img[r-1:r+2, c-1:c+2]
            gx = np.sum(patch * sobel_x)
            gy = np.sum(patch * sobel_y)
            grad_vals.append(np.sqrt(gx**2 + gy**2))
    f7_boundary_gradient = np.mean(grad_vals) if grad_vals else 0.0

    # 8. Độ tương phản với vành nền lân cận 5 pixel (Background Contrast)
    dilated = np.zeros((H, W), dtype=bool)
    for r, c in coords:
        r_min, r_max = max(0, r - 5), min(H, r + 6)
        c_min, c_max = max(0, c - 5), min(W, c + 6)
        dilated[r_min:r_max, c_min:c_max] = True
    ring_mask = dilated & (~reg_mask)
    bg_mean = np.mean(img[ring_mask]) if np.any(ring_mask) else f5_mean
    f8_background_contrast = bg_mean - f5_mean

    return np.array([
        f1_area_fraction, f2_elongation, f3_extent, f4_complexity,
        f5_mean, f6_std, f7_boundary_gradient, f8_background_contrast
    ], dtype=np.float64)


# ==============================================================================
# BƯỚC 5: BỘ PHÂN LỚP LINEAR SVM TỰ TÍNH (PREDICT FROM SCRATCH)
# ==============================================================================
def predict_svm_from_scratch(features: np.ndarray, weights: np.ndarray, bias: float) -> tuple[int, float]:
    """Phán quyết: Điểm số = w . x + b > 0 là DẦU TRÀN THẬT, <= 0 là LOOK-ALIKE."""
    score = float(np.dot(weights, features) + bias)
    label = 1 if score > 0 else 0
    return label, score


# ==============================================================================
# HÀM CHÍNH: THỰC THI TOÀN BỘ PIPELINE TỪ ĐẦU ĐẾN CUỐI
# ==============================================================================
def main():
    print("=" * 75)
    print("🛰️ DEMO TỰ CODE CHAY TOÀN BỘ PIPELINE PHÁT HIỆN DẦU TRÀN SAR — ĐỀ 18")
    print("=" * 75)

    # 1. Khởi tạo một bức ảnh biển SAR giả lập kích thước 24x36
    # Có mặt biển gợn sóng (sáng) và 1 vệt dầu tràn dẹt dài ở giữa (tối)
    np.random.seed(2026)
    ocean = 0.72 + 0.14 * np.random.randn(24, 36)
    # Vết dầu loang: dẹt, dài từ cột 8 đến 28, hàng 9 đến 13, rất tối (~0.18)
    ocean[9:14, 8:28] = 0.18 + 0.04 * np.random.randn(5, 20)
    # Thêm một vệt nhiễu nhỏ li ti (3 pixel) để kiểm tra tính năng lọc rác
    ocean[2:4, 2:4] = 0.15
    ocean = np.clip(ocean, 0.0, 1.0)

    print("\n[Ảnh SAR gốc] Mặt biển gợn sóng (░░) và Vệt dầu tối (██) kèm nhiễu hạt tiêu:")
    print_ascii_matrix(ocean, "Ảnh SAR Gốc")

    # 2. Khử nhiễu đốm
    print("\n" + "-" * 75)
    print("[Bước 1] Khử nhiễu đốm Speckle bằng Lee Filter 7x7 (L=4.0)...")
    cleaned = lee_filter_from_scratch(ocean, size=7, looks=4.0)
    print(f" -> Phương sai toàn cảnh trước lọc: {np.var(ocean):.4f} | Sau lọc: {np.var(cleaned):.4f}")
    print_ascii_matrix(cleaned, "Ảnh sau khử nhiễu Lee Filter")

    # 3. Phân đoạn Otsu
    print("\n" + "-" * 75)
    print("[Bước 2] Phân đoạn Otsu tách vùng tối ứng viên...")
    thresh_val, dark_mask = otsu_threshold_from_scratch(cleaned)
    print(f" -> Ngưỡng tối ưu Otsu tìm được: {thresh_val:.1f} / 255 ({thresh_val/255.0:.3f})")
    print_ascii_matrix(dark_mask.astype(bool), "Mặt nạ nhị phân đốm tối (Otsu)")

    # 4. Gán nhãn liên thông và Lọc diện tích
    print("\n" + "-" * 75)
    print("[Bước 3] Gán nhãn thành phần liên thông 8 hướng & Lọc diện tích rác (min_area=40)...")
    labeled, regions = connected_components_and_filter(dark_mask, min_area=40)
    print(f" -> Tìm thấy {len(regions)} vùng thỏa mãn điều kiện (đã tự động vứt bỏ đốm nhiễu li ti)!")

    # 5. Trích xuất đặc trưng & Phán quyết SVM
    # Trọng số huấn luyện mẫu (được tối ưu hóa bằng Accelerated Gradient Descent của dự án)
    sample_weights = np.array([-0.6, 1.5, -0.4, 0.9, -1.8, -0.3, 0.7, 2.2])
    sample_bias = -0.8
    feature_names = [
        "1. Diện tích tỷ đối", "2. Độ thuôn dài (Elongation)", "3. Độ lấp đầy hộp bao (Extent)",
        "4. Độ phức tạp biên (Complexity)", "5. Cường độ trung bình", "6. Độ lệch chuẩn nội vùng",
        "7. Gradient biên (Sobel)", "8. Tương phản vành nền (5px)"
    ]

    for i, reg in enumerate(regions):
        print("\n" + "-" * 75)
        print(f"[Bước 4 & 5] Phân tích Thẻ Căn Cước của Vùng Ứng Viên #{i+1} (Diện tích: {reg['area']} pixel):")
        feats = extract_8_features_from_scratch(cleaned, reg)
        for name, val in zip(feature_names, feats):
            print(f"    {name:<36}: {val:.4f}")

        pred_class, score = predict_svm_from_scratch(feats, sample_weights, sample_bias)
        print(f"\n -> Điểm số quyết định Linear SVM (w.x + b): {score:+.3f}")
        if pred_class == 1:
            print(" -> 🚨 KẾT LUẬN: ĐÂY LÀ VẾT DẦU TRÀN THẬT (OIL SPILL)!")
            print("    Lý do: Vùng thuôn dài ngoằn ngoèo, mép viền răng cưa, tối hơn rõ rệt so với nền biển sát nách.")
        else:
            print(" -> ✅ KẾT LUẬN: ĐÂY LÀ VÙNG TỐI GIẢ MẠO (LOOK-ALIKE / BIỂN LẶNG)!")

    print("\n" + "=" * 75)
    print("🏆 TOÀN BỘ PIPELINE ĐÃ CHẠY XONG 100% BẰNG NUMPY THUẦN!")
    print("=" * 75)


if __name__ == "__main__":
    main()
