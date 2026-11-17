"""Demo 04: Mô phỏng từng bước tối ưu hóa Linear SVM với Squared Hinge Loss bằng Nesterov Gradient.

Mục đích:
- Quan sát cách hàm mất mát Squared Hinge Loss giảm dần qua từng bước lặp.
- Hiểu cách cập nhật trọng số w, tính gradient và kiểm tra điều kiện hội tụ.
"""

import numpy as np


def run_demo():
    print("=" * 75)
    print("DEMO 04: TỐI ƯU HÓA LINEAR SVM VỚI SQUARED HINGE LOSS BẰNG NESTEROV GRADIENT")
    print("=" * 75)

    # 1. Tạo tập dữ liệu 2D giả lập gồm 20 mẫu:
    # 10 mẫu Dầu (y = +1): Đặc trưng thuôn dài cao, tương phản cao
    # 10 mẫu Nền (y = -1): Đặc trưng thuôn dài thấp, tương phản thấp
    np.random.seed(42)
    X_oil = np.random.normal(loc=[3.5, 0.7], scale=[0.5, 0.1], size=(10, 2))
    X_bg = np.random.normal(loc=[1.2, 0.2], scale=[0.4, 0.1], size=(10, 2))

    X = np.vstack([X_oil, X_bg])
    y = np.array([+1] * 10 + [-1] * 10)  # Nhãn +1 và -1
    n, d = X.shape

    # Chuẩn hóa z-score
    X = (X - X.mean(axis=0)) / X.std(axis=0)

    print(f"Tổng số mẫu huấn luyện: n = {n}, Số chiều đặc trưng d = {d}")
    print(" - Nhãn +1 (Dầu tràn): 10 mẫu")
    print(" - Nhãn -1 (Nền biển): 10 mẫu")

    # Tham số SVM:
    C = 10.0  # Hệ số phạt điều hòa
    max_iter = 50
    tol = 1e-5

    # Định nghĩa hàm mất mát Squared Hinge Loss
    def compute_loss(w):
        margins = np.maximum(0.0, 1.0 - y * (X @ w))
        reg_term = 0.5 * (w @ w) / n
        loss_term = C * np.mean(margins**2)
        return reg_term + loss_term

    # Định nghĩa đạo hàm Gradient
    def compute_gradient(w):
        margins = np.maximum(0.0, 1.0 - y * (X @ w))
        grad_reg = w / n
        grad_loss = -2.0 * C * (X.T @ (y * margins)) / n
        return grad_reg + grad_loss

    # Khởi tạo trọng số w = 0
    w = np.zeros(d)
    w_prev = w.copy()

    # Ước lượng bước nhảy Lipschitz: L = 1/n + 2*C*||X||^2 / n
    lipschitz = 1.0 / n + 2.0 * C * (np.linalg.norm(X, ord=2) ** 2) / n
    step_size = 1.0 / lipschitz

    print(f"\nKhởi tạo: w = {w}, Bước nhảy học step_size = {step_size:.4f}")
    print("\n" + "-" * 75)
    print(f"{'Vòng lặp (k)':^12} | {'Trọng số w1, w2':^22} | {'Giá trị Loss':^15} | {'Chuẩn Gradient ||g||':^18}")
    print("-" * 75)

    # Vòng lặp Nesterov Accelerated Gradient
    for k in range(1, max_iter + 1):
        # 1. Điểm nhìn trước Nesterov (Look-ahead point)
        beta = (k - 1) / (k + 2)  # Hệ số quán tính Nesterov
        z = w + beta * (w - w_prev)

        # 2. Tính gradient tại điểm nhìn trước
        grad = compute_gradient(z)
        grad_norm = np.linalg.norm(grad)

        # 3. Cập nhật nghiệm mới
        w_new = z - step_size * grad

        loss = compute_loss(w_new)

        # In tiến trình ở các vòng lặp tiêu biểu
        if k <= 10 or k % 10 == 0 or grad_norm < tol:
            w_str = f"[{w_new[0]:.3f}, {w_new[1]:.3f}]"
            print(f"{k:^12} | {w_str:^22} | {loss:^15.6f} | {grad_norm:^18.6e}")

        # Kiểm tra điều kiện hội tụ
        if grad_norm < tol:
            print(f"\n🎉 THUẬT TOÁN ĐÃ HỘI TỤ CHÍNH XÁC TẠI VÒNG LẶP {k}! (||g|| < {tol})")
            w = w_new
            break

        w_prev = w.copy()
        w = w_new.copy()

    print("-" * 75)
    print(f"Trọng số tối ưu cuối cùng: w = [{w[0]:.4f}, {w[1]:.4f}]")
    print(f"Hàm quyết định: f(x) = {w[0]:.4f} * x1 + {w[1]:.4f} * x2")
    print(" - Nếu f(x) > 0  ==> Phân lớp là DẦU TRÀN")
    print(" - Nếu f(x) <= 0 ==> Phân lớp là NỀN BIỂN")
    print("=" * 75)


if __name__ == "__main__":
    run_demo()
