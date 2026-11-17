"""Demo 01: Tính toán từng bước bộ lọc thích nghi Lee Filter trên ma trận 5x5.

Mục đích:
- Giúp bạn nhìn tận mắt từng con số: Trung bình cục bộ (mean), Phương sai cục bộ (var),
  Phương sai nhiễu (noise_var = mean^2 / looks), Trọng số thích nghi (W), và Giá trị sau lọc.
- Chạy độc lập hoàn toàn, không phụ thuộc pipeline chính.
"""

import numpy as np


def run_demo():
    print("=" * 70)
    print("DEMO 01: GIẢI THÍCH TỪNG BƯỚC BỘ LỌC THÍCH NGHI LEE FILTER TRÊN MA TRẬN 5x5")
    print("=" * 70)

    # 1. Khởi tạo một ma trận 5x5 giả lập một đường biên vết dầu:
    # Nửa trên là biển sáng (mức xám ~ 90-110, có nhiễu lốm đốm)
    # Nửa dưới là vết dầu tối (mức xám ~ 20-30, dập sóng phẳng)
    np.random.seed(42)
    a = np.array(
        [
            [105.0, 95.0, 100.0, 110.0, 90.0],
            [90.0, 105.0, 95.0, 100.0, 105.0],
            [25.0, 20.0, 30.0, 25.0, 20.0],  # <- Đường biên phân cách
            [20.0, 25.0, 20.0, 20.0, 25.0],
            [25.0, 20.0, 25.0, 20.0, 20.0],
        ],
        dtype=float,
    )

    print("\n1. MA TRẬN ẢNH GỐC (5x5):")
    print(np.array2string(a, precision=1, floatmode="fixed"))

    # Tham số bộ lọc:
    size = 3  # Cửa sổ 3x3 để dễ quan sát tính toán
    looks = 4  # Số lượt nhìn L = 4 (như trong Sentinel-1 GRD)
    radius = size // 2

    # Padding phản xạ đối xứng (reflect)
    padded = np.pad(a, radius, mode="reflect")

    filtered = np.zeros_like(a)
    weights = np.zeros_like(a)
    means = np.zeros_like(a)
    variances = np.zeros_like(a)

    for r in range(a.shape[0]):
        for c in range(a.shape[1]):
            # Trích xuất cửa sổ 3x3 quanh pixel (r, c)
            window = padded[r : r + size, c : c + size]
            m = np.mean(window)
            v = np.var(window)  # Phương sai cục bộ

            # Ước lượng phương sai nhiễu nhân SAR: sigma_noise^2 = mean^2 / looks
            noise_var = (m * m) / looks

            # Trọng số thích nghi W = max(0, (v - noise_var) / v)
            if v > 1e-12:
                w = max(0.0, (v - noise_var) / v)
            else:
                w = 0.0

            # Giá trị sau lọc: x_hat = mean + W * (y - mean)
            x_hat = m + w * (a[r, c] - m)

            means[r, c] = m
            variances[r, c] = v
            weights[r, c] = w
            filtered[r, c] = x_hat

    print("\n2. MA TRẬN TRUNG BÌNH CỤC BỘ (Mean Window 3x3):")
    print(np.array2string(means, precision=1, floatmode="fixed"))

    print("\n3. MA TRẬN PHƯƠNG SAI CỤC BỘ (Variance Window 3x3):")
    print(np.array2string(variances, precision=1, floatmode="fixed"))

    print("\n4. MA TRẬN TRỌNG SỐ THÍCH NGHI W:")
    print(np.array2string(weights, precision=3, floatmode="fixed"))

    print("\n5. MA TRẬN KẾT QUẢ SAU LỌC LEE FILTER:")
    print(np.array2string(filtered, precision=1, floatmode="fixed"))

    print("\n" + "-" * 70)
    print("PHÂN TÍCH BẢN CHẤT TẠI 2 ĐIỂM ĐẶC TRƯNG:")
    print("-" * 70)

    # Điểm 1: Nằm sâu trong lòng biển phẳng (hàng 0, cột 2 - giá trị gốc 100.0)
    print("📌 Điểm 1: Nằm trong lòng biển (hàng 0, cột 2):")
    print(f"   - Mức xám gốc y = {a[0, 2]:.1f}")
    print(f"   - Trung bình cục bộ mean = {means[0, 2]:.1f}")
    print(f"   - Phương sai cục bộ var = {variances[0, 2]:.1f}")
    print(f"   - Trọng số W = {weights[0, 2]:.3f} (Rất nhỏ)")
    print(f"   - Giá trị sau lọc = {filtered[0, 2]:.1f}")
    print("   ==> Nhận xét: W nhỏ làm bộ lọc hoạt động như Mean, làm mịn nhiễu phẳng lì!")

    # Điểm 2: Nằm ngay tại ranh giới mép vết dầu (hàng 2, cột 2 - giá trị gốc 30.0)
    print("\n📌 Điểm 2: Nằm ngay tại biên vết dầu (hàng 2, cột 2):")
    print(f"   - Mức xám gốc y = {a[2, 2]:.1f}")
    print(f"   - Trung bình cục bộ mean = {means[2, 2]:.1f}")
    print(f"   - Phương sai cục bộ var = {variances[2, 2]:.1f} (Cực kỳ lớn do có bước nhảy sáng-tối)")
    print(f"   - Trọng số W = {weights[2, 2]:.3f} (Lớn vượt trội!)")
    print(f"   - Giá trị sau lọc = {filtered[2, 2]:.1f}")
    print("   ==> Nhận xét: W lớn kéo giá trị lọc về gần 30.0, bảo toàn độ sắc nét của biên!")
    print("=" * 70)


if __name__ == "__main__":
    run_demo()
