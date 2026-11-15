"""Demo 02: Mô phỏng từng bước thuật toán phân ngưỡng Otsu & Biểu đồ phương sai liên lớp.

Mục đích:
- Quan sát cách Otsu quét qua từng ngưỡng T từ 0 đến 255.
- Thấy rõ phương sai liên lớp (between-class variance) đạt đỉnh cực đại chính xác tại điểm phân tách lý tưởng.
"""

import numpy as np


def run_demo():
    print("=" * 70)
    print("DEMO 02: TÍNH TOÁN PHƯƠNG SAI LIÊN LỚP (BETWEEN-CLASS VARIANCE) CỦA OTSU")
    print("=" * 70)

    # 1. Tạo một tập dữ liệu giả lập có phân phối 2 đỉnh (Bimodal Distribution):
    # - 400 pixel biểu diễn vết dầu tối (phân phối chuẩn quanh mức xám 30, std=8)
    # - 600 pixel biểu diễn nền biển sáng (phân phối chuẩn quanh mức xám 110, std=12)
    np.random.seed(2026)
    oil_pixels = np.random.normal(loc=30, scale=8, size=400)
    sea_pixels = np.random.normal(loc=110, scale=12, size=600)
    image_pixels = np.clip(np.concatenate([oil_pixels, sea_pixels]), 0, 255).astype(int)

    print(f"Tổng số pixel mô phỏng: {len(image_pixels)}")
    print(" - Lớp dầu: 400 pixel (trung bình ~ 30)")
    print(" - Lớp biển: 600 pixel (trung bình ~ 110)")

    # 2. Đếm Histogram 256 bin
    hist, bin_edges = np.histogram(image_pixels, bins=256, range=(0, 256))
    prob = hist / len(image_pixels)  # Xác suất p_i

    # 3. Tính toán các đại lượng tích lũy
    # omega(T): Xác suất tích lũy lớp 0
    # mu(T): Trung bình tích lũy lớp 0
    # mu_total: Trung bình toàn ảnh
    omega = prob.cumsum()
    bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2
    mu = (prob * bin_centers).cumsum()
    mu_total = mu[-1]

    # 4. Quét từng ngưỡng T và tính phương sai liên lớp sigma_b^2
    variances = np.zeros(256)
    for t in range(256):
        w0 = omega[t]
        w1 = 1.0 - w0
        if w0 > 1e-6 and w1 > 1e-6:
            # Công thức rút gọn: sigma_b^2 = (mu_total * w0 - mu)^2 / (w0 * w1)
            variances[t] = ((mu_total * w0 - mu[t]) ** 2) / (w0 * w1)
        else:
            variances[t] = 0.0

    optimal_threshold = int(np.argmax(variances))
    max_var = variances[optimal_threshold]

    print("\n" + "-" * 70)
    print(f"KẾT QUẢ TỐI ƯU CỦA OTSU:")
    print(f" 👉 Ngưỡng tối ưu tìm được T* = {optimal_threshold}")
    print(f" 👉 Phương sai liên lớp cực đại sigma_b^2 = {max_var:.2f}")
    print("-" * 70)

    # 5. In bảng giá trị xung quanh điểm cực trị để quan sát đỉnh Parabol
    print("\nBẢNG GIÁ TRỊ PHƯƠNG SAI LIÊN LỚP XUNG QUANH ĐỈNH:")
    print(f"{'Ngưỡng T':^12} | {'Tỉ lệ Lớp 0 (w0)':^18} | {'Tỉ lệ Lớp 1 (w1)':^18} | {'sigma_b^2':^15}")
    print("-" * 70)
    for t in range(optimal_threshold - 5, optimal_threshold + 6):
        mark = " <=== ĐỈNH CỰC ĐẠI!" if t == optimal_threshold else ""
        print(f"{t:^12} | {omega[t]:^18.4f} | {1-omega[t]:^18.4f} | {variances[t]:^15.2f}{mark}")

    # 6. Vẽ biểu đồ ASCII mô phỏng hình dạng đỉnh của phương sai
    print("\nBIỂU ĐỒ ASCII PHƯƠNG SAI LIÊN LỚP TỪ T=10 ĐẾN T=140:")
    print("Ngưỡng T | Biểu đồ độ lớn sigma_b^2")
    step = 5
    for t in range(10, 145, step):
        bar_len = int((variances[t] / max_var) * 45)
        bar = "█" * bar_len
        marker = " (T*)" if abs(t - optimal_threshold) < step else ""
        print(f"{t:^8} | {bar:<45} {variances[t]:.1f}{marker}")

    print("=" * 70)


if __name__ == "__main__":
    run_demo()
