# 🤖 MODULE 5: HỌC MÁY TỰ CODE TỪ SỐ 0 (CART & LINEAR SVM)

> **Phạm vi tài liệu tự học — cập nhật 17/11/2026:** đây là giải thích và mã minh họa độc lập, không phải pipeline đã nghiệm thu hoặc bằng chứng đạt 100% đề. Công thức giản lược, ảnh giả lập, ví dụ ghép greedy và mô phỏng trôi dầu không thay thế kết quả trong `src/sar_oil`, `scripts` và `results`. Lee không bảo đảm giữ biên tuyệt đối; agreement 100% chỉ áp dụng cho ca đã đo; F1 SOS 0,3403 là cấu hình được chọn theo quy tắc dung sai, không phải cực đại nghiêm ngặt. Ưu tiên [đối chiếu hiện tại](../../../docs/DANH_GIA_DU_AN_VA_DOI_CHIEU_DE_18.md) khi có khác biệt.

## 1. CHUẨN HÓA ĐẶC TRƯNG VÀ NGUY CƠ RÒ RỈ DỮ LIỆU (DATA LEAKAGE)

### 1.1. Tại sao phải chuẩn hóa đặc trưng (StandardScaler)?
Trong 8 đặc trưng ta vừa tính:
- `area_fraction` có giá trị rất nhỏ: $0.001$ đến $0.05$.
- `complexity` hoặc `elongation` có thể lên tới $10.0$ đến $50.0$.
Nếu đưa thẳng vào SVM, thuật toán tối ưu sẽ bị các đặc trưng có độ lớn lớn (như elongation) chi phối hoàn toàn, và xem nhẹ các đặc trưng có giá trị nhỏ (như diện tích).
Ta phải đưa tất cả về cùng một phân phối chuẩn có $\mu = 0$ và $\sigma = 1$:
$$z = \frac{x - \mu}{\sigma + \epsilon}$$

### 1.2. Quy tắc vàng chống rò rỉ dữ liệu (Data Leakage)
- **TUYỆT ĐỐI KHÔNG** được lấy toàn bộ dữ liệu (Train + Val + Test) để tính $\mu$ và $\sigma$.
- Ta chỉ được tính $\mu_{\text{train}}$ và $\sigma_{\text{train}}$ trên **Tập Huấn Luyện (Train)**.
- Sau đó dùng đúng cặp $(\mu_{\text{train}}, \sigma_{\text{train}})$ đó để chuẩn hóa tập Validation và Test!

---

## 2. CÂY QUYẾT ĐỊNH CART (CLASSIFICATION AND REGRESSION TREES)

### 2.1. Chỉ số bất thuần Gini (Gini Impurity)
- Đo lường mức độ "hỗn loạn" của một tập mẫu. Với bài toán nhị phân (Dầu $p$ và Look-alike $1-p$):
$$I_G = 1 - \left(p^2 + (1 - p)^2\right) = 2p(1 - p)$$
- Nếu một nút chứa $100\%$ là dầu: $I_G = 2 \times 1 \times 0 = 0$ (Độ tinh khiết tuyệt đối!).
- Nếu một nút chứa $50\%$ dầu và $50\%$ look-alike: $I_G = 2 \times 0.5 \times 0.5 = 0.5$ (Hỗn loạn tối đa).

### 2.2. Tìm nhát cắt tối ưu
Tại mỗi nút, ta quét qua tất cả 8 đặc trưng và tất cả các ngưỡng giá trị phân tách có thể, tính Gini bình quân có trọng số của 2 nhánh con:
$$G_{\text{split}} = \frac{N_{\text{Trái}}}{N} I_G(\text{Trái}) + \frac{N_{\text{Phải}}}{N} I_G(\text{Phải})$$
Nhát cắt nào làm giảm Gini nhiều nhất sẽ được chọn làm câu hỏi rẽ nhánh!

---

## 3. LINEAR SVM (TỐI ƯU HÓA BÌNH PHƯƠNG BẢN LỀ BẰNG NESTEROV GRADIENT DESCENT)

Linear SVM không chỉ phân loại, mà nó còn tìm **khoảng cách an toàn lớn nhất (Maximum Margin)** ngăn cách giữa hai phe.

### 3.1. Hàm mục tiêu Soft-Margin Squared Hinge Loss
Ta gán nhãn: $y_i \in \{-1, +1\}$ (với $+1$ là Dầu, $-1$ là Look-alike).
Hàm mất mát bình phương bản lề (Squared Hinge Loss) có dạng:
$$\min_{\mathbf{w}, b} J(\mathbf{w}, b) = \frac{1}{2} \|\mathbf{w}\|^2 + C \sum_{i=1}^N \max\left(0, 1 - y_i (\mathbf{w}^T \mathbf{x}_i + b)\right)^2$$

**Tại sao dùng Squared Hinge Loss thay vì Hinge Loss thông thường?**
- Hinge Loss thường $\max(0, 1 - m)$ bị gãy góc nhọn tại $m=1$ (không khả vi, không tính được đạo hàm trơn).
- Squared Hinge Loss được bình phương $\implies$ **Khả vi liên tục trên toàn bộ không gian**, cho phép tính đạo hàm chính xác để tối ưu bằng Gradient Descent!

### 3.2. Gradient giải tích (Analytical Gradients)
Đặt độ lề $m_i = y_i (\mathbf{w}^T \mathbf{x}_i + b)$:
- Nếu $m_i \ge 1$: Điểm nằm đúng bên ngoài lề an toàn $\implies$ Gradient bằng 0.
- Nếu $m_i < 1$: Điểm bị vi phạm lề an toàn $\implies$ Gradient đạo hàm là:
$$\nabla_{\mathbf{w}} J = \mathbf{w} - 2C \sum_{i: m_i < 1} (1 - m_i) \cdot y_i \cdot \mathbf{x}_i$$
$$\nabla_b J = -2C \sum_{i: m_i < 1} (1 - m_i) \cdot y_i$$

### 3.3. Tối ưu hóa Nesterov Accelerated Gradient (NAG)
Thay vì dùng Gradient Descent cổ điển chậm chạp, ta áp dụng Nesterov Momentum:
1. Dự đoán vị trí tiếp theo dựa trên quán tính: $\mathbf{w}_{\text{lookahead}} = \mathbf{w}_t + \beta (\mathbf{w}_t - \mathbf{w}_{t-1})$.
2. Tính gradient tại điểm đón đầu $\mathbf{w}_{\text{lookahead}}$.
3. Cập nhật vị trí mới. Thuật toán đạt tốc độ hội tụ $O(1/k^2)$ thay vì $O(1/k)$, hội tụ tuyệt đối sau khoảng 100-200 vòng lặp!

Mở file `machine_learning.py` để tự tay gõ từng dòng thuật toán!
