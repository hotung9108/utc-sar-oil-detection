# CƠ SỞ TOÁN HỌC & GIÁO TRÌNH THUẬT TOÁN COMPUTER VISION
## Chi Tiết 4 Chương Theo Bài Giảng Xử Lý Ảnh — TS. Phan Thanh Toàn (UTC)
**Đề tài 18:** Phát hiện vết dầu tràn trên biển từ ảnh SAR (NASA #6)

---

## 1. CHƯƠNG 3: KHỬ NHIỄU ĐỐM SPECKLE VÀ TĂNG CƯỜNG TƯƠNG PHẢN

### 1.1. Bản chất nhiễu đốm đục hạt (Speckle Noise)
Trong ảnh Radar SAR, nhiễu đốm là hệ quả của sự giao thoa kết hợp (coherent interference) ngẫu nhiên giữa các sóng con phản xạ từ vô số phần tử tán xạ thô ráp trên mặt biển trong cùng một ô phân giải (resolution cell).

Nhiễu tuân theo **mô hình tán xạ nhân (Multiplicative Noise Model)**:
$$I(x,y) = R(x,y) \cdot u(x,y)$$
trong đó:
- $I(x,y)$: Cường độ pixel quan sát được trên ảnh SAR.
- $R(x,y)$: Suất phản xạ tán xạ ngược thực tế (radar backscatter coefficient $\sigma^0$).
- $u(x,y)$: Thành phần nhiễu speckle, có kỳ vọng $\mu_u = 1$ và phương sai $\sigma_u^2 = 1/L$ ($L$ là số nhìn độc lập - Number of Looks).

### 1.2. Bộ lọc trung vị bảo toàn biên 2D (Median Filter)
- Thuộc nhóm lọc thống kê thứ tự (Order-statistic filter):
  $$\hat{I}(x,y) = \text{median} \{ I(x+i, y+j) \mid (i, j) \in W \}$$
- **Ưu điểm vượt trội với ảnh SAR:** Khử triệt để các đốm hạt đơn lẻ mà không làm mờ các đường ranh giới gấp khúc của vệt dầu tràn (Edge-preserving).

### 1.3. Bộ lọc Lee thích nghi (Lee Adaptive Filter)
- Khôi phục tín hiệu tán xạ $\hat{R}(x,y)$ dựa trên biến thiên cục bộ:
  $$\hat{R}(x,y) = \mu_k + W_k \cdot (I(x,y) - \mu_k)$$
  $$W_k = \max\left(0, 1 - \frac{C_u^2}{C_i^2}\right), \quad C_u = \frac{\sigma_u}{\mu_u}, \quad C_i = \frac{\sigma_k}{\mu_k}$$
  - Trong vùng biển đồng nhất: $C_i \approx C_u \rightarrow W_k \approx 0 \rightarrow \hat{R} \approx \mu_k$ (Làm mịn tối đa để khử đốm).
  - Tại đường ranh giới vệt dầu: $C_i \gg C_u \rightarrow W_k \approx 1 \rightarrow \hat{R} \approx I$ (Bảo toàn nguyên vẹn độ sắc nét của biên).

---

## 2. CHƯƠNG 7: PHÂN VÙNG BẰNG NGƯỠNG OTSU TỐI ƯU & HỆ SỐ KHẢ TÁCH $\eta$

### 2.1. Tối đa hóa phương sai liên lớp (Between-Class Variance)
Lược đồ mức xám chuẩn hóa của ảnh được định nghĩa:
$$p_i = \frac{n_i}{N}, \quad i = 0, 1, \dots, L-1, \quad \sum_{i=0}^{L-1} p_i = 1$$

Với một ngưỡng cắt $t \in [0, 255]$, ảnh được chia thành 2 lớp:
- Lớp $C_0$ (Đốm tối ứng viên / Vệt dầu): Các pixel có mức xám $[0, t]$.
- Lớp $C_1$ (Nền biển đại dương): Các pixel có mức xám $[t+1, L-1]$.

Xác suất xuất hiện và kỳ vọng của từng lớp:
$$\omega_0(t) = \sum_{i=0}^t p_i, \quad \omega_1(t) = 1 - \omega_0(t)$$
$$\mu_0(t) = \sum_{i=0}^t \frac{i \cdot p_i}{\omega_0(t)}, \quad \mu_1(t) = \sum_{i=t+1}^{L-1} \frac{i \cdot p_i}{\omega_1(t)}, \quad \mu_T = \sum_{i=0}^{L-1} i \cdot p_i$$

Phương sai giữa hai lớp (Between-class variance):
$$\sigma_B^2(t) = \omega_0(t) (\mu_0(t) - \mu_T)^2 + \omega_1(t) (\mu_1(t) - \mu_T)^2 = \frac{[\mu_T \omega_0(t) - \mu(t)]^2}{\omega_0(t)(1 - \omega_0(t))}$$

Ngưỡng Otsu tối ưu là vị trí đạt cực đại phương sai liên lớp:
$$T^* = \arg\max_{0 \le t \le 255} \sigma_B^2(t)$$

### 2.2. Kiểm định hệ số khả tách $\eta$ (Separability Measure)
Tổng phương sai toàn ảnh:
$$\sigma_T^2 = \sum_{i=0}^{L-1} (i - \mu_T)^2 p_i$$
Hệ số khả tách:
$$\eta = \frac{\sigma_B^2(T^*)}{\sigma_T^2} \in [0, 1]$$

> [!TIP]
> **Cơ chế Dừng Sớm (Early Stop):** Nếu $\eta < 0.08 - 0.10$, lược đồ mức xám đơn đỉnh (unimodal), bề mặt biển hoàn toàn đồng nhất hoặc không có vệt dầu đối lập. Hệ thống dừng sớm và kết luận ngay là mặt biển an toàn mà không cần tốn chi phí tính toán cho các bước sau.

---

## 3. CHƯƠNG 6: HÌNH THÁI HỌC TOÁN HỌC (MATHEMATICAL MORPHOLOGY)

### 3.1. Phép Mở và Phép Đóng (Opening & Closing)
- **Phép Mở (Opening):** Làm mịn đường viền ngoài, triệt tiêu các eo thắt hẹp và loại bỏ các đốm bọt sóng nhỏ li ti:
  $$A \circ B = (A \ominus B) \oplus B$$
- **Phép Đóng (Closing):** Hàn gắn các đoạn nứt gãy hẹp, nối liền các dải dầu bị chia cắt do sóng biển:
  $$A \bullet B = (A \oplus B) \ominus B$$

### 3.2. Lấp lỗ trống (Hole Filling)
Sử dụng thuật toán loang (Flood-fill) từ đường biên ngoài của ảnh để lấp đầy các khoảng khuyết do bọt sóng tạo ra bên trong thân vệt dầu.

### 3.3. Toán tử trích biên hình thái học đơn pixel
Trích xuất đường bao biên $\beta(A)$ phục vụ tính chu vi và đo gradient Sobel dọc theo ranh giới:
$$\beta(A) = A - (A \ominus B)$$
với phần tử cấu trúc $B$ kích thước $3 \times 3$ hình vuông hoặc chữ thập.

---

## 4. CHƯƠNG 5: ĐẠO HÀM SOBEL & ĐO ĐẠC ĐẶC TRƯNG VẬT LÝ

### 4.1. Gradient ranh giới ranh giới Sobel (Border Sharpness)
Tích chập ảnh với hai ma trận mặt nạ Sobel $3 \times 3$:
$$S_x = \begin{bmatrix} -1 & 0 & 1 \\ -2 & 0 & 2 \\ -1 & 0 & 1 \end{bmatrix}, \quad S_y = \begin{bmatrix} -1 & -2 & -1 \\ 0 & 0 & 0 \\ 1 & 2 & 1 \end{bmatrix}$$
Độ lớn gradient tại mỗi pixel:
$$M(x,y) = \sqrt{G_x(x,y)^2 + G_y(x,y)^2}$$
Gradient trung bình dọc đường biên vệt dầu $\partial R$:
$$\overline{G}_{\text{border}} = \frac{1}{|\partial R|} \sum_{(x,y) \in \partial R} M(x,y) \ge 5.0$$

### 4.2. Độ tương phản vành đai lân cận (Annulus Background Contrast)
Tạo vùng vành khuyên đại dương bao quanh vệt dầu bằng cách dãn nở hình thái vết dầu (dilation 9px) trừ đi chính vết dầu:
$$\Delta \mu = \mu_{\text{sea}} - \mu_{\text{oil}} \ge 10.0$$
$$\text{Damping Ratio} = \frac{\mu_{\text{sea}}}{\mu_{\text{oil}}} \ge 1.35$$
