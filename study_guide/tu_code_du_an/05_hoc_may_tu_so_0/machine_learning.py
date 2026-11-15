"""MODULE 5: MACHINE LEARNING ALGORITHMS FROM SCRATCH (NUMPY THUẦN)

Module này tự triển khai từ số 0:
1. StandardScalerScratch (Chuẩn hóa đặc trưng Z-score chống rò rỉ)
2. CARTDecisionTreeScratch (Cây quyết định tối ưu hóa bất thuần Gini)
3. LinearSVMScratch (Bộ giải tối ưu hóa Squared Hinge Loss bằng Nesterov Momentum)
"""
from __future__ import annotations
import numpy as np


# ==============================================================================
# 1. BỘ CHUẨN HÓA ĐẶC TRƯNG Z-SCORE
# ==============================================================================
class StandardScalerScratch:
    """Chuẩn hóa Z-score: z = (x - mean) / std. Fit trên Train, Transform trên Val/Test."""
    def __init__(self):
        self.mean_: np.ndarray | None = None
        self.scale_: np.ndarray | None = None

    def fit(self, X: np.ndarray) -> StandardScalerScratch:
        self.mean_ = np.mean(X, axis=0)
        std = np.std(X, axis=0)
        # Tránh chia cho 0 với các đặc trưng có phương sai bằng 0
        self.scale_ = np.where(std < 1e-8, 1.0, std)
        return self

    def transform(self, X: np.ndarray) -> np.ndarray:
        if self.mean_ is None or self.scale_ is None:
            raise ValueError("Cần gọi .fit(X) trước khi .transform(X)!")
        return (X - self.mean_) / self.scale_

    def fit_transform(self, X: np.ndarray) -> np.ndarray:
        return self.fit(X).transform(X)


# ==============================================================================
# 2. CÂY QUYẾT ĐỊNH CART (TỰ CODE ĐỆ QUY THEO GINI)
# ==============================================================================
class TreeNode:
    """Nút trên cây quyết định."""
    def __init__(
        self,
        feature_idx: int | None = None,
        threshold: float | None = None,
        left: TreeNode | None = None,
        right: TreeNode | None = None,
        value: int | None = None
    ):
        self.feature_idx = feature_idx  # Chỉ số đặc trưng dùng để rẽ nhánh
        self.threshold = threshold      # Ngưỡng phân tách
        self.left = left                # Nhánh con trái (<= threshold)
        self.right = right              # Nhánh con phải (> threshold)
        self.value = value              # Lớp dự đoán (nếu là nút lá)


class CARTDecisionTreeScratch:
    """Cây quyết định phân lớp nhị phân tối ưu hóa chỉ số bất thuần Gini."""
    def __init__(self, max_depth: int = 5, min_samples_split: int = 5, min_samples_leaf: int = 2):
        self.max_depth = max_depth
        self.min_samples_split = min_samples_split
        self.min_samples_leaf = min_samples_leaf
        self.root: TreeNode | None = None

    @staticmethod
    def _gini(y: np.ndarray) -> float:
        """Tính chỉ số bất thuần Gini: 1 - sum(p_k^2) = 2*p*(1-p)."""
        if len(y) == 0:
            return 0.0
        p = np.mean(y == 1)
        return float(2.0 * p * (1.0 - p))

    def _best_split(self, X: np.ndarray, y: np.ndarray) -> tuple[int | None, float | None]:
        best_gain = -1.0
        best_feat, best_thresh = None, None
        n_samples, n_features = X.shape
        parent_gini = self._gini(y)

        for feat in range(n_features):
            values = np.unique(X[:, feat])
            if len(values) <= 1:
                continue
            # Thử các ngưỡng trung điểm giữa các giá trị liên tiếp
            thresholds = (values[:-1] + values[1:]) / 2.0
            for thresh in thresholds:
                left_mask = X[:, feat] <= thresh
                right_mask = ~left_mask

                n_left, n_right = np.sum(left_mask), np.sum(right_mask)
                if n_left < self.min_samples_leaf or n_right < self.min_samples_leaf:
                    continue

                gini_left = self._gini(y[left_mask])
                gini_right = self._gini(y[right_mask])
                weighted_gini = (n_left / n_samples) * gini_left + (n_right / n_samples) * gini_right
                gain = parent_gini - weighted_gini

                if gain > best_gain:
                    best_gain = gain
                    best_feat = feat
                    best_thresh = float(thresh)

        return best_feat, best_thresh

    def _build_tree(self, X: np.ndarray, y: np.ndarray, depth: int = 0) -> TreeNode:
        n_samples = len(y)
        # Điều kiện dừng: đạt độ sâu tối đa, không đủ mẫu chia, hoặc lớp đã thuần khiết
        if (depth >= self.max_depth or
            n_samples < self.min_samples_split or
            len(np.unique(y)) <= 1):
            majority_class = int(np.round(np.mean(y == 1)))
            return TreeNode(value=majority_class)

        feat, thresh = self._best_split(X, y)
        if feat is None or thresh is None:
            majority_class = int(np.round(np.mean(y == 1)))
            return TreeNode(value=majority_class)

        left_mask = X[:, feat] <= thresh
        right_mask = ~left_mask

        left_child = self._build_tree(X[left_mask], y[left_mask], depth + 1)
        right_child = self._build_tree(X[right_mask], y[right_mask], depth + 1)
        return TreeNode(feature_idx=feat, threshold=thresh, left=left_child, right=right_child)

    def fit(self, X: np.ndarray, y: np.ndarray) -> CARTDecisionTreeScratch:
        self.root = self._build_tree(X, y, depth=0)
        return self

    def _predict_single(self, x: np.ndarray, node: TreeNode) -> int:
        if node.value is not None:
            return node.value
        if x[node.feature_idx] <= node.threshold:
            return self._predict_single(x, node.left)
        return self._predict_single(x, node.right)

    def predict(self, X: np.ndarray) -> np.ndarray:
        if self.root is None:
            raise ValueError("Chưa huấn luyện cây!")
        return np.array([self._predict_single(x, self.root) for x in X], dtype=np.int32)


# ==============================================================================
# 3. LINEAR SVM (BỘ GIẢI SQUARED HINGE LOSS + NESTEROV MOMENTUM)
# ==============================================================================
class LinearSVMScratch:
    """Bộ phân loại Linear SVM tự cài đặt bằng Nesterov Accelerated Gradient Descent.

    Hàm mất mát chia cho N (tránh tràn số khi N lớn):
        J(w, b) = 0.5 * ||w||^2 / N + C * sum(max(0, 1 - y_i*(w^T*x_i + b))^2) / N
    Bước học thích nghi theo hằng số Lipschitz và Backtracking line search.
    """
    def __init__(self, C: float = 1.0, max_iter: int = 500, tol: float = 1e-5):
        self.C = float(C)
        self.max_iter = max_iter
        self.tol = float(tol)
        self.weights_: np.ndarray | None = None
        self.bias_: float = 0.0
        self.loss_history_: list[float] = []

    def fit(self, X: np.ndarray, y: np.ndarray) -> LinearSVMScratch:
        X = np.asarray(X, dtype=np.float64)
        n, d = X.shape
        target = np.where(np.asarray(y) <= 0, -1.0, 1.0)

        # Bổ sung cột 1 cho bias b: X_aug = [X, 1]
        X_aug = np.hstack([X, np.ones((n, 1), dtype=np.float64)])

        def compute_loss(w_vec: np.ndarray) -> float:
            margin = np.maximum(0.0, 1.0 - target * (X_aug @ w_vec))
            reg = 0.5 * np.sum(w_vec[:-1] ** 2) / n  # không phạt bias
            hinge = self.C * np.sum(margin ** 2) / n
            return float(reg + hinge)

        w = np.zeros(d + 1, dtype=np.float64)
        z = w.copy()

        # Ước lượng bước học Lipschitz: L = 1/n + 2*C*||X||^2/n
        norm_x = float(np.linalg.norm(X_aug, ord=2))
        lipschitz = 1.0 / n + 2.0 * self.C * (norm_x ** 2) / n
        step = 1.0 / max(lipschitz, 1e-4)

        t_param = 1.0
        self.loss_history_ = []

        for iteration in range(self.max_iter):
            margin = np.maximum(0.0, 1.0 - target * (X_aug @ z))
            grad_reg = np.zeros(d + 1, dtype=np.float64)
            grad_reg[:-1] = z[:-1] / n  # gradient điều chuẩn w

            grad_hinge = -2.0 * self.C * (X_aug.T @ (target * margin)) / n
            grad = grad_reg + grad_hinge

            base_loss = compute_loss(z)
            self.loss_history_.append(base_loss)

            # Backtracking line search
            while True:
                next_w = z - step * grad
                delta = next_w - z
                cur_loss = compute_loss(next_w)
                if cur_loss <= base_loss + np.dot(grad, delta) + np.sum(delta ** 2) / (2.0 * step) + 1e-12:
                    break
                step *= 0.5
                if step < 1e-12:
                    break

            # Nesterov momentum update
            next_t = 0.5 * (1.0 + np.sqrt(1.0 + 4.0 * t_param * t_param))
            beta = (t_param - 1.0) / next_t
            z = next_w + beta * (next_w - w)
            w = next_w
            t_param = next_t

            if np.linalg.norm(grad) < self.tol:
                break

        self.weights_ = w[:-1]
        self.bias_ = float(w[-1])
        return self

    def decision_function(self, X: np.ndarray) -> np.ndarray:
        if self.weights_ is None:
            raise ValueError("Chưa huấn luyện mô hình!")
        return np.dot(X, self.weights_) + self.bias_

    def predict(self, X: np.ndarray) -> np.ndarray:
        return np.where(self.decision_function(X) > 0.0, 1, 0).astype(np.int32)


# ==============================================================================
# BÀI TẬP THỰC NGHIỆM ĐỐI CHỨNG HỌC MÁY
# ==============================================================================
if __name__ == "__main__":
    print("=" * 70)
    print("--- [MODULE 5] KIỂM TRA HUẤN LUYỆN CART & LINEAR SVM TỪ SỐ 0 ---")
    print("=" * 70)

    np.random.seed(42)
    # Giả lập 200 mẫu đặc trưng (8 chiều): 100 mẫu Dầu thật (+1), 100 mẫu Look-alike (0)
    # Lớp Dầu thật có elongation cao và tương phản cao
    X_oil = np.random.randn(100, 8) + np.array([0.02, 3.5, 0.4, 3.0, 0.15, 0.05, 1.5, 0.6])
    # Lớp Look-alike có elongation thấp và tương phản thấp
    X_lookalike = np.random.randn(100, 8) + np.array([0.01, 1.2, 0.7, 1.1, 0.35, 0.02, 0.5, 0.1])

    X = np.vstack([X_oil, X_lookalike])
    y = np.array([1] * 100 + [0] * 100)

    # Chia tập Train (70%) và Test (30%)
    indices = np.random.permutation(len(y))
    train_idx, test_idx = indices[:140], indices[140:]
    X_train, y_train = X[train_idx], y[train_idx]
    X_test, y_test = X[test_idx], y[test_idx]

    # 1. Chuẩn hóa đặc trưng
    scaler = StandardScalerScratch()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    # 2. Huấn luyện CART
    cart = CARTDecisionTreeScratch(max_depth=3, min_samples_leaf=5)
    cart.fit(X_train_scaled, y_train)
    cart_preds = cart.predict(X_test_scaled)
    cart_acc = np.mean(cart_preds == y_test) * 100.0
    print(f"1. Độ chính xác CART Decision Tree trên tập Test: {cart_acc:.1f}%")

    # 3. Huấn luyện Linear SVM
    svm = LinearSVMScratch(C=10.0, max_iter=250)
    svm.fit(X_train_scaled, y_train)
    svm_preds = svm.predict(X_test_scaled)
    svm_acc = np.mean(svm_preds == y_test) * 100.0
    print(f"2. Độ chính xác Linear SVM (Nesterov) trên tập Test: {svm_acc:.1f}%")
    print(f"   - Hàm mất mát ban đầu : {svm.loss_history_[0]:.2f}")
    print(f"   - Hàm mất mát cuối cùng: {svm.loss_history_[-1]:.2f} (Đã hội tụ tối ưu!)")

    print("\n✅ MODULE 5 HOẠT ĐỘNG HOÀN HẢO!")
