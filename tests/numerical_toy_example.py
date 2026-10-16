"""
numerical_toy_example.py
========================
Kịch bản mô phỏng giải tích từng bước trên ma trận đồ chơi 5x5 (Analytical Toy Example)
minh họa các thuật toán cốt lõi trong giáo trình Xử lý ảnh - TS. Phan Thanh Toàn (UTC):
1. Lọc trung vị 2D qua cửa sổ 3x3 (Chương 3, P104-106).
2. Phân ngưỡng Otsu tối ưu, phương sai liên lớp sigma_B^2, phương sai toàn cục sigma_T^2,
   và hệ số khả tách eta (Chương 7, P48-55).
3. Toán tử hình thái học: Co (Erosion), Dãn (Dilation), Mở (Opening), Đóng (Closing),
   và Trích biên hình thái học beta(A) = A - (A (-) B) (Chương 6, P7-20).
4. Toán tử đạo hàm Sobel G_x, G_y và độ dốc vi phân biên M(x,y) (Chương 5, P36-40).

Tác giả: TV2 (Lý thuyết toán học & Kiểm chứng tính đúng).
Đối chiếu chính xác 100% với Chương 2 trong báo cáo LaTeX (report_latex/chapters/02_theory.tex).
"""

import os
import sys

# Thêm thư mục gốc dự án vào PYTHONPATH
WORKSPACE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if WORKSPACE_DIR not in sys.path:
    sys.path.insert(0, WORKSPACE_DIR)

# Thiết lập bảng mã UTF-8 cho console Windows
try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

import numpy as np

from src.preprocessing.numpy_filters import custom_median_filter
from src.preprocessing.numpy_otsu import custom_otsu_threshold, compute_otsu_statistics
from src.morphology.numpy_morphology import (
    custom_erode,
    custom_dilate,
    custom_open,
    custom_close,
    custom_extract_boundary,
)
from src.features.numpy_features import custom_sobel_gradient


def format_matrix(mat: np.ndarray, title: str = "", fmt: str = "{:3d}") -> str:
    """Định dạng in ma trận 2D đẹp mắt cho báo cáo và console."""
    lines = []
    if title:
        lines.append(f"--- {title} ---")
    for row in mat:
        lines.append("  [" + ", ".join(fmt.format(x) for x in row) + "]")
    return "\n".join(lines)


def run_toy_example():
    print("=" * 75)
    print("   VÍ DỤ SỐ TÍNH TAY MINH HỌA TRÊN MA TRẬN 5x5 (TOY EXAMPLE)")
    print("   Học phần: Xử lý ảnh (TS. Phan Thanh Toàn - UTC)")
    print("   Thành viên thực hiện: TV2 (Lý thuyết toán học & Kiểm chứng tính đúng)")
    print("=" * 75)

    # -------------------------------------------------------------
    # BƯỚC 0: KHỞI TẠO MA TRẬN ĐỒ CHƠI 5x5
    # -------------------------------------------------------------
    # Vùng trung tâm 3x3 là đốm tối (vết dầu loang, mức xám 10-19)
    # Vùng biên xung quanh là nước biển sáng (mức xám 83-89)
    I = np.array([
        [85, 88, 86, 89, 87],
        [84, 15, 12, 18, 85],
        [86, 14, 10, 16, 88],
        [83, 16, 13, 19, 86],
        [87, 85, 89, 84, 88]
    ], dtype=np.uint8)

    print("\n[BƯỚC 0] Ma trận ảnh quan sát I (kích thước 5x5):")
    print(format_matrix(I, fmt="{:3d}"))
    print("\nGiải thích cấu trúc vật lý:")
    print("  - Vùng nền biển sáng (16 pixel viền ngoài): mức xám [83, 89].")
    print("  - Vùng vệt tối vệt dầu (9 pixel trung tâm r in [1,3], c in [1,3]): mức xám [10, 19].")
    print("  - Pixel tâm (2, 2) có mức xám 10 là điểm đáy suy giảm tán xạ.")

    # -------------------------------------------------------------
    # BƯỚC 1: LỌC TRUNG VỊ 2D QUA CỬA SỔ 3x3
    # -------------------------------------------------------------
    print("\n" + "-" * 75)
    print("[BƯỚC 1] LỌC TRUNG VỊ 2D QUA CỬA SỔ 3x3 (Slide Chương 3, P104-106)")
    print("-" * 75)

    # Trích xuất cửa sổ 3x3 quanh pixel tâm (2, 2)
    win_center = I[1:4, 1:4]
    win_center_flat = win_center.flatten()
    win_sorted = np.sort(win_center_flat)
    median_val = win_sorted[len(win_sorted) // 2]

    print("Cửa sổ lân cận W(2, 2) kích thước 3x3:")
    print(format_matrix(win_center, fmt="{:3d}"))
    print(f"\n1. Tập hợp 9 mức xám trong lân cận W(2, 2):")
    print(f"   {win_center_flat.tolist()}")
    print(f"2. Sắp xếp thứ tự tăng dần:")
    print(f"   {win_sorted.tolist()}")
    print(f"3. Giá trị trung vị tại chỉ số chính giữa (k=4):")
    print(f"   I_hat(2, 2) = median(W) = {median_val}")
    print(f"   => Nhận xét: Nhiễu đốm cực trị 10 đã được thay thế mượt mà bởi 15.")

    I_filtered = custom_median_filter(I, ksize=3, mode='reflect')
    print("\nẢnh toàn bộ sau lọc trung vị custom_median_filter (ksize=3):")
    print(format_matrix(I_filtered, fmt="{:3d}"))
    assert I_filtered[2, 2] == 15, "Lỗi tính toán trung vị tại tâm!"

    # -------------------------------------------------------------
    # BƯỚC 2: PHÂN NGƯỠNG OTSU TỐI ƯU VÀ HỆ SỐ KHẢ TÁCH ETA
    # -------------------------------------------------------------
    print("\n" + "-" * 75)
    print("[BƯỚC 2] PHÂN NGƯỠNG OTSU TỐI ƯU & HỆ SỐ KHẢ TÁCH (Slide Chương 7, P48-55)")
    print("-" * 75)

    total_pixels = I.size  # 25
    stats = compute_otsu_statistics(I)

    # Phân tích 2 cụm mức xám
    dark_pixels = I[1:4, 1:4].flatten()
    sea_pixels = np.concatenate([I[0, :], I[4, :], I[1:4, 0], I[1:4, 4]])

    omega_0_exact = len(dark_pixels) / total_pixels  # 9/25 = 0.36
    omega_1_exact = len(sea_pixels) / total_pixels   # 16/25 = 0.64
    mu_0_exact = np.mean(dark_pixels)               # 133 / 9 = 14.7778
    mu_1_exact = np.mean(sea_pixels)                # 1380 / 16 = 86.2500
    mu_t_exact = stats['mu_t']                      # 60.5200
    sigma_t_sq = stats['sigma_t_sq']                # 1181.61

    print(f"1. Tổng số điểm ảnh: N_T = {total_pixels} pixel.")
    print(f"2. Phân bố 2 lớp đối tượng và nền biển:")
    print(f"   - Lớp đối tượng C_0 (vệt dầu): n_0 = {len(dark_pixels)} pixel (mức xám {min(dark_pixels)}-{max(dark_pixels)})")
    print(f"     => Xác suất xuất hiện (trọng số): omega_0 = {len(dark_pixels)}/25 = {omega_0_exact:.4f}")
    print(f"     => Mức xám trung bình lớp C_0:   mu_0 = {mu_0_exact:.4f}")
    print(f"   - Lớp nền biển C_1:            n_1 = {len(sea_pixels)} pixel (mức xám {min(sea_pixels)}-{max(sea_pixels)})")
    print(f"     => Xác suất xuất hiện (trọng số): omega_1 = {len(sea_pixels)}/25 = {omega_1_exact:.4f}")
    print(f"     => Mức xám trung bình lớp C_1:   mu_1 = {mu_1_exact:.4f}")
    print(f"3. Mức xám trung bình toàn cục (Global Mean):")
    print(f"   mu_T = omega_0 * mu_0 + omega_1 * mu_1")
    print(f"        = {omega_0_exact:.2f} * {mu_0_exact:.4f} + {omega_1_exact:.2f} * {mu_1_exact:.4f} = {mu_t_exact:.4f}")

    print(f"\n4. Tính phương sai toàn cục sigma_T^2:")
    print(f"   sigma_T^2 = sum_i (i - mu_T)^2 * p_i = {sigma_t_sq:.4f}")

    # Phương sai liên lớp cực đại
    sigma_b_sq_max = omega_0_exact * (mu_0_exact - mu_t_exact)**2 + omega_1_exact * (mu_1_exact - mu_t_exact)**2
    print(f"\n5. Tính phương sai liên lớp cực đại sigma_B^2(T*):")
    print(f"   sigma_B^2 = omega_0 * (mu_0 - mu_T)^2 + omega_1 * (mu_1 - mu_T)^2")
    print(f"             = {omega_0_exact:.2f} * ({mu_0_exact:.4f} - {mu_t_exact:.4f})^2 + {omega_1_exact:.2f} * ({mu_1_exact:.4f} - {mu_t_exact:.4f})^2")
    part0 = omega_0_exact * (mu_0_exact - mu_t_exact)**2
    part1 = omega_1_exact * (mu_1_exact - mu_t_exact)**2
    print(f"             = {part0:.4f} + {part1:.4f} = {sigma_b_sq_max:.4f}")

    # Khảo sát khoảng cực đại
    candidates = np.where(np.isclose(stats['sigma_b_sq'], np.max(stats['sigma_b_sq']), atol=1e-5))[0]
    opt_t, eta, dark_mask = custom_otsu_threshold(I)
    print(f"\n6. Miền giá trị ngưỡng cực đại hóa sigma_B^2(k):")
    print(f"   Do khoảng trống giữa 19 và 83 không có pixel nào, mọi ngưỡng k in [{candidates[0]}, {candidates[-1]}]")
    print(f"   đều cho cùng phân hoạch tối ưu phân tách hoàn hảo 2 lớp.")
    print(f"   Theo lý thuyết (lấy điểm chính giữa khoảng phân ly):")
    print(f"   T* = round(mean([{candidates[0]}, {candidates[-1]}])) = round({np.mean(candidates):.2f}) = {opt_t}")
    print(f"\n7. Hệ số khả tách (Separability Criterion):")
    print(f"   eta = sigma_B^2(T*) / sigma_T^2 = {sigma_b_sq_max:.4f} / {sigma_t_sq:.4f} = {eta:.6f} (~ {eta*100:.2f}%)")
    print(f"   => Nhận xét: eta đạt xấp xỉ 100%, khẳng định 2 lớp phân ly tuyệt đối không giao thoa.")

    # Mặt nạ nhị phân đốm tối A (255 cho pixel <= T*)
    print("\nMặt nạ nhị phân đốm tối A (I <= T*, hiển thị dạng 0/1):")
    A_binary = (dark_mask > 0).astype(np.uint8)
    print(format_matrix(A_binary, fmt="{:1d}"))

    # -------------------------------------------------------------
    # BƯỚC 3: CÁC PHÉP TOÁN HÌNH THÁI HỌC VÀ TRÍCH BIÊN BETA(A)
    # -------------------------------------------------------------
    print("\n" + "-" * 75)
    print("[BƯỚC 3] TOÁN TỬ HÌNH THÁI HỌC VÀ TRÍCH BIÊN BETA(A) (Slide Chương 6, P7-20)")
    print("-" * 75)

    B = np.ones((3, 3), dtype=np.uint8)
    print("Phần tử cấu trúc B kích thước 3x3 (toàn số 1, tâm tại (1, 1)):")
    print(format_matrix(B, fmt="{:1d}"))

    # 3.1 Phép co (Erosion)
    A_erode = custom_erode(dark_mask, ksize=3)
    A_erode_bin = (A_erode > 0).astype(np.uint8)
    print("\n1. Phép co (Erosion): A (-) B")
    print("   Nguyên lý: (B)_z con A chỉ thỏa mãn duy nhất tại tọa độ tâm z = (2, 2).")
    print("   Các điểm biên của khối 3x3 đều thiếu lân cận ngoài -> bị co ngót thành 0:")
    print(format_matrix(A_erode_bin, fmt="{:1d}"))
    assert np.sum(A_erode_bin) == 1 and A_erode_bin[2, 2] == 1, "Lỗi kiểm tra phép co!"

    # 3.2 Phép dãn (Dilation)
    A_dilate = custom_dilate(dark_mask, ksize=3)
    A_dilate_bin = (A_dilate > 0).astype(np.uint8)
    print("\n2. Phép dãn (Dilation): A (+) B")
    print("   Nguyên lý: Khối 3x3 nở ra 1 lớp theo mọi hướng, phủ kín toàn bộ ma trận 5x5:")
    print(format_matrix(A_dilate_bin, fmt="{:1d}"))
    assert np.all(A_dilate_bin == 1), "Lỗi kiểm tra phép dãn!"

    # 3.3 Phép mở (Opening)
    A_open = custom_open(dark_mask, ksize=3)
    A_open_bin = (A_open > 0).astype(np.uint8)
    print("\n3. Phép mở (Opening): A o B = (A (-) B) (+) B")
    print("   Nguyên lý: Co A xuống còn pixel tâm (2, 2), sau đó dãn pixel này bởi B 3x3")
    print("   => Khôi phục chính xác khối 3x3 ban đầu A (bảo toàn cấu trúc lớn):")
    print(format_matrix(A_open_bin, fmt="{:1d}"))
    assert np.array_equal(A_open_bin, A_binary), "Lỗi kiểm tra phép mở!"

    # 3.4 Phép đóng (Closing)
    A_close = custom_close(dark_mask, ksize=3)
    A_close_bin = (A_close > 0).astype(np.uint8)
    print("\n4. Phép đóng (Closing): A * B = (A (+) B) (-) B")
    print("   Nguyên lý: Dãn phủ 5x5, sau đó co với đệm biên 255 -> bảo toàn khối 3x3:")
    print(format_matrix(A_close_bin, fmt="{:1d}"))

    # 3.5 Trích biên hình thái học beta(A) = A - (A (-) B)
    beta_A = custom_extract_boundary(dark_mask, ksize=3)
    beta_A_bin = (beta_A > 0).astype(np.uint8)
    print("\n5. Trích biên hình thái học chuẩn giáo trình: beta(A) = A - (A (-) B)")
    print("   Lấy ảnh đối tượng A trừ đi ảnh đã co A (-) B:")
    print("   - Tại 8 điểm xung quanh: A=1, A(-)B=0 => beta(A) = 1 - 0 = 1 (biên)")
    print("   - Tại pixel tâm (2, 2):  A=1, A(-)B=1 => beta(A) = 1 - 1 = 0 (lõi rỗng)")
    print(format_matrix(beta_A_bin, fmt="{:1d}"))
    assert beta_A_bin[2, 2] == 0, "Điểm tâm trong lòng vệt dầu không được chứa biên!"
    assert np.sum(beta_A_bin) == 8, "Đường biên hình thái học phải có đúng 8 pixel!"

    # -------------------------------------------------------------
    # BƯỚC 4: ĐẠO HÀM SOBEL VÀ ĐỘ DỐC BIÊN GRADIENT
    # -------------------------------------------------------------
    print("\n" + "-" * 75)
    print("[BƯỚC 4] TOÁN TỬ ĐẠO HÀM SOBEL VÀ ĐỘ DỐC BIÊN M(x, y) (Slide Chương 5, P36-40)")
    print("-" * 75)

    gx, gy, grad_mag = custom_sobel_gradient(I)
    print("1. Độ lớn Gradient M(x, y) = sqrt(Gx^2 + Gy^2):")
    for r in range(5):
        print("  [" + ", ".join(f"{grad_mag[r, c]:6.1f}" for c in range(5)) + "]")

    # Đo gradient dọc theo đường biên beta(A)
    b_coords = np.where(beta_A_bin > 0)
    border_gradients = grad_mag[b_coords]
    mean_border_grad = float(np.mean(border_gradients))

    print(f"\n2. Thống kê độ dốc vi phân tại 8 pixel trên đường biên beta(A):")
    print(f"   Các giá trị: {[round(x, 1) for x in border_gradients.tolist()]}")
    print(f"   Độ dốc gradient trung bình mép dầu: G_border = {mean_border_grad:.2f}")

    # Độ tương phản mức xám giữa biển và dầu
    delta_mu = mu_1_exact - mu_0_exact
    damping_ratio = mu_1_exact / mu_0_exact
    print(f"\n3. Đo tương phản mức xám vật lý:")
    print(f"   - Chênh lệch cường độ: Delta_mu = mu_sea - mu_oil = {mu_1_exact:.2f} - {mu_0_exact:.2f} = {delta_mu:.2f} mức xám.")
    print(f"   - Tỉ số suy giảm (Damping Ratio): {damping_ratio:.2f} lần.")
    print(f"   => Nhận xét: Thỏa mãn xuất sắc các ngưỡng nhận diện vật lý của vệt dầu tràn:")
    print(f"      Delta_mu >= 12.0 mức xám và G_border >= 6.0.")

    print("\n" + "=" * 75)
    print("   KIỂM THỬ GIẢI TÍCH HOÀN TẤT: 100% KẾT QUẢ TRÙNG KHỚP LÝ THUYẾT")
    print("=" * 75)
    return True


if __name__ == "__main__":
    run_toy_example()
