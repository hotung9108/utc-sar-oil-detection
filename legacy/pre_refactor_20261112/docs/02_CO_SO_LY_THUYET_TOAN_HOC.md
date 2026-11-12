> **Tài liệu lịch sử:** nội dung dưới đây được giữ để tham khảo quá trình phát triển. Thuật toán, số liệu và demo hiện tại được mô tả trong [báo cáo chính](report/BAO_CAO_BTL_XLA.pdf), [README](../README.md) và [đối chiếu hiện tại](management/KIEM_TRA_HIEN_TAI.md). Không dùng các kết luận cũ để xác nhận phiên bản mới.

# CHƯƠNG 2: CƠ SỞ LÝ THUYẾT & GIẢI TÍCH TOÁN HỌC CÁC THUẬT TOÁN

> **Học phần**: Xử lý ảnh (Digital Image Processing - DIP) — Khoa CNTT, Đại học Giao thông Vận tải (UTC)  
> **Giảng viên**: TS. Phan Thanh Toàn, TS. Cao Thị Luyên  
> **Cam kết**: **100% Thuần toán giải tích rời rạc và Pure NumPy (KHÔNG sử dụng Machine Learning hay thư viện đóng gói)**.

---

## 2.1. HỆ THỐNG CÁC PHÉP BIẾN ĐỔI TĂNG CƯỜNG ĐIỂM & TƯƠNG PHẢN (CHƯƠNG 3.1 UTC)

### 2.1.1. Biến đổi Logarit (Logarithmic Transformation - Slide 10–14)
- **Bản chất toán học**:
  $$s = c \cdot \log(1 + r)$$
  Trong đó $r \in [0, 255]$ là mức xám gốc, $s$ là mức xám sau biến đổi, và hằng số chuẩn hóa:
  $$c = \frac{255}{\log(1 + \max(r))}$$
- **Nguyên lý trong ảnh SAR**: Tín hiệu phản xạ radar có dải động cực rộng (Dynamic range). Biến đổi log nén dải mức xám cao và **kéo giãn dải mức xám thấp** trong vùng tối của vết dầu, giúp mắt người phân biệt được các sắc thái cấu trúc bên trong vệt dầu.

---

### 2.1.2. Cân bằng Histogram toàn cục (Global Histogram Equalization - Slide 29–36)
- **Công thức hàm mật độ xác suất (PDF)**:
  $$p(r_k) = \frac{n_k}{M \times N}, \quad k = 0, 1, \dots, L-1$$
- **Hàm phân bố tích lũy (CDF)** và ánh xạ mức xám mới:
  $$s_k = T(r_k) = \text{round}\left( (L - 1) \sum_{j=0}^k p(r_j) \right) = \text{round}\left( \frac{L - 1}{M \times N} \sum_{j=0}^k n_j \right)$$
- **Nhược điểm trên ảnh SAR vi ba**: Vì nền biển chiếm đa số diện tích và tập trung mức xám ở dải giữa, Global HE đẩy toàn bộ nền biển lên mức bão hòa trắng xóa (Cháy sáng - Over-enhancement) và khuếch đại nghiêm trọng nhiễu đốm hạt tiêu.

---

### 2.1.3. Cân bằng Histogram thích nghi có ngưỡng (CLAHE - Slide 38–42)
Để khắc phục hiện tượng cháy sáng của Global HE, thuật toán CLAHE (Contrast Limited Adaptive Histogram Equalization) thực hiện 4 bước giải tích:
1. **Chia khối lưới (Tiling)**: Chia ảnh kích thước $M \times N$ thành lưới các khối nhỏ không chồng lấn $8 \times 8$ ô (kích thước mỗi ô $W \times H$).
2. **Cắt ngưỡng tương phản (Clipping Limit)**:
   Ngưỡng cắt số pixel cho mỗi mức xám trong từng khối:
   $$N_{\text{clip}} = \text{round}\left( \text{ClipLimit} \times \frac{W \times H}{L} \right)$$
   Với mọi mức xám $k$ có $n_k > N_{\text{clip}}$, phần dư $\Delta = n_k - N_{\text{clip}}$ bị cắt bỏ.
3. **Phân phối lại phần dư (Redistribution)**:
   Tổng lượng pixel dư $\sum \Delta$ được chia đều cho tất cả $L = 256$ mức xám trong khối:
   $$n_k^{\text{refined}} = n_k + \frac{\sum \Delta}{L}$$
   Sau đó tính CDF và ánh xạ cân bằng riêng cho từng khối.
4. **Nội suy song tuyến (Bilinear Interpolation)**:
   Để xóa các vệt biên gồ ghề giữa các ô láng giềng, mức xám của pixel $(x, y)$ nằm giữa 4 tâm khối $(x_1, y_1), (x_2, y_1), (x_1, y_2), (x_2, y_2)$ được tính bằng nội suy 2D:
   $$f(x, y) = (1 - \Delta x)(1 - \Delta y) f_{11} + \Delta x(1 - \Delta y) f_{21} + (1 - \Delta x)\Delta y f_{12} + \Delta x \Delta y f_{22}$$
   Trong đó $\Delta x = \frac{x - x_1}{x_2 - x_1}$, $\Delta y = \frac{y - y_1}{y_2 - y_1}$.

---

## 2.2. HỆ THỐNG CÁC BỘ LỌC KHÔNG GIAN & KHỬ ĐỐM THÍCH ỨNG SAR (CHƯƠNG 3.1 & 3.2 UTC)

### 2.2.1. Lọc trung bình Box Filter (Slide 93–96)
- **Công thức nhân chập**:
  $$I_{\text{box}}(x, y) = \frac{1}{K^2} \sum_{i=-m}^m \sum_{j=-m}^m I(x + i, y + j)$$
- **Tối ưu hóa $O(1)$ bằng Mảng tích lũy (Integral Image)**:
  $$\text{II}(x, y) = I(x, y) + \text{II}(x-1, y) + \text{II}(x, y-1) - \text{II}(x-1, y-1)$$
  Tổng giá trị cửa sổ chữ nhật bất kỳ được tính trong đúng 4 phép truy xuất bộ nhớ, độc lập với kích thước kernel.

---

### 2.2.2. Lọc Gauss 2D tách được (Separable Gaussian Filter - Slide 97–100)
- **Hàm nhân Gauss 2D**:
  $$G(x, y) = \frac{1}{2\pi \sigma^2} \exp\left( -\frac{x^2 + y^2}{2\sigma^2} \right)$$
- **Tính chất tách được (Separability)**:
  $$G(x, y) = G_1(x) \cdot G_2(y) = \left[ \frac{1}{\sqrt{2\pi}\sigma} \exp\left(-\frac{x^2}{2\sigma^2}\right) \right] \times \left[ \frac{1}{\sqrt{2\pi}\sigma} \exp\left(-\frac{y^2}{2\sigma^2}\right) \right]$$
  Giúp giảm độ phức tạp tính toán từ $O(K^2 \cdot M N)$ xuống $O(2K \cdot M N)$.

---

### 2.2.3. Lọc trung vị phi tuyến (Median Filter - Slide 104–106)
- **Toán tử thống kê thứ tự**:
  $$I_{\text{med}}(x, y) = \text{median}\left\{ I(x + i, y + j) \mid (i, j) \in W \right\}$$
  Triệt tiêu 100% các đỉnh nhiễu xung đơn lẻ (Salt-and-Pepper) mà không làm dịch chuyển vị trí thực tế của đường ranh giới.

---

### 2.2.4. Lọc hai chiều bảo toàn biên (Bilateral Filter - Nhóm A Đề 2)
- **Công thức trọng số kết hợp không gian và dải sáng**:
  $$I_{\text{bi}}(x, y) = \frac{1}{W_p} \sum_{i, j \in \Omega} I(x+i, y+j) \cdot w_s(i, j) \cdot w_r(i, j)$$
  $$w_s(i, j) = \exp\left( -\frac{i^2 + j^2}{2\sigma_s^2} \right) \quad (\text{Trọng số khoảng cách})$$
  $$w_r(i, j) = \exp\left( -\frac{(I(x+i, y+j) - I(x, y))^2}{2\sigma_r^2} \right) \quad (\text{Trọng số chênh lệch độ xám})$$
  Làm phẳng mịn mặt biển nhưng khi gặp bước nhảy xám lớn tại bờ vết dầu, $w_r \to 0$, bảo tồn nguyên vẹn độ sắc nét của bờ mép dầu.

---

### 2.2.5. Bộ lọc đốm thích nghi SAR Lee MMSE (Chuẩn mực Radar - Đề 18 NASA & Chương 3.2)
Dựa trên tiêu chuẩn sai số toàn phương trung bình cực tiểu (Minimum Mean Square Error - MMSE) cho mô hình nhiễu nhân $I = R \cdot \eta$:
1. **Ước lượng thống kê cục bộ trên cửa sổ $W \times W$**:
   $$\mu_I = \frac{1}{|W|} \sum_{(i, j) \in W} I(i, j)$$
   $$\sigma_I^2 = \frac{1}{|W|} \sum_{(i, j) \in W} (I(i, j) - \mu_I)^2$$
2. **Phương sai nhiễu vi ba lý thuyết**:
   $$\sigma_v^2 = \frac{1}{L} \quad (L \text{ là số tầm nhìn Sentinel-1, mặc định } L = 4.0)$$
3. **Hệ số thích ứng Lee $K$**:
   $$K = 1 - \frac{\sigma_v^2 \cdot \mu_I^2}{\sigma_I^2} = \max\left(0, \frac{\sigma_I^2 - \sigma_v^2 \mu_I^2}{\sigma_I^2}\right)$$
4. **Công thức khôi phục pixel**:
   $$\hat{R}(x, y) = \mu_I + K \cdot (I(x, y) - \mu_I)$$
   - **Vùng đồng nhất (Trong lòng dầu hoặc ngoài biển)**: $\sigma_I^2 \approx \sigma_v^2 \mu_I^2 \implies K \to 0 \implies \hat{R} = \mu_I$ (Lọc triệt để như lọc trung bình).
   - **Vùng ranh giới vết dầu**: $\sigma_I^2 \gg \sigma_v^2 \mu_I^2 \implies K \to 1 \implies \hat{R} = I(x, y)$ (Giữ nguyên cấu trúc biên sắc nét, không bị làm nhòe).

---

### 2.2.6. Lọc đồng hình trong miền tần số FFT2D (Homomorphic Filtering - Chương 3.2 Slide 37)
Tách rời thành phần chiếu xạ tần số thấp (Illumination $L$) và phản xạ tần số cao (Reflectance $R$) từ mô hình tích $I = L \cdot R$:
$$\ln(I) = \ln(L) + \ln(R)$$
$$\xrightarrow{\text{FFT2D}} S(u, v) \xrightarrow{\times H(u, v)} S'(u, v) \xrightarrow{\text{IFFT2D}} s'(x, y) \xrightarrow{\exp} I_{\text{enhanced}}(x, y)$$
Hàm truyền thông cao Gauss:
$$H(u, v) = (\gamma_H - \gamma_L) \left[ 1 - \exp\left( -\frac{D^2(u, v)}{2 D_0^2} \right) \right] + \gamma_L$$
Với $\gamma_L = 0.5$ (dìm thành phần chiếu xạ không đều) và $\gamma_H = 1.5$ (khuếch đại độ tương phản biên).

---

## 2.3. HỆ THỐNG CÁC KỸ THUẬT LÀM NÉT ẢNH (CHƯƠNG 3.2 UTC & ĐỀ 5)

### 2.3.1. Unsharp Masking & High-Boost Filtering (Slide 32–36)
- **Công thức tạo mặt nạ vi sai tần số cao**:
  $$g_{\text{mask}}(x, y) = f(x, y) - f_{\text{blur}}(x, y)$$
- **Cộng tăng cường**:
  $$f_{\text{sharp}}(x, y) = f(x, y) + k \cdot g_{\text{mask}}(x, y)$$
- **Hiện tượng Undershoot Dip (Thâm hụt biên âm)**:
  Tại đáy các thung lũng sóng biển (nơi $f < f_{\text{blur}}$), giá trị $(f - f_{\text{blur}}) < 0$, dẫn đến việc dìm mức xám xuống rất thấp gần màu đen. Do đó, thuật toán phân đoạn hình thái học phải chạy trên ảnh **trước khi Unsharp** để không bắt nhầm các điểm đen này.

---

### 2.3.2. Làm nét bằng toán tử vi sai Laplacian (Slide 32–34)
- **Đạo hàm bậc 2 rời rạc**:
  $$\nabla^2 f = \frac{\partial^2 f}{\partial x^2} + \frac{\partial^2 f}{\partial y^2} = [f(x+1, y) + f(x-1, y) + f(x, y+1) + f(x, y-1)] - 4f(x, y)$$
- **Mặt nạ làm nét tâm âm**:
  $$f_{\text{sharp}} = f(x, y) - \alpha \nabla^2 f(x, y)$$

---

## 2.4. HỆ THỐNG CÁC TOÁN TỬ PHÁT HIỆN BIÊN CỔ ĐIỂN (CHƯƠNG 5 UTC & ĐỀ 5)

### 2.4.1. Toán tử Gradient Roberts & Prewitt (Slide 24–35)
- **Roberts $2 \times 2$**:
  $$G_x = \begin{bmatrix} +1 & 0 \\ 0 & -1 \end{bmatrix}, \quad G_y = \begin{bmatrix} 0 & +1 \\ -1 & 0 \end{bmatrix}$$
- **Prewitt $3 \times 3$**:
  $$G_x = \begin{bmatrix} -1 & 0 & +1 \\ -1 & 0 & +1 \\ -1 & 0 & +1 \end{bmatrix}, \quad G_y = \begin{bmatrix} -1 & -1 & -1 \\ 0 & 0 & 0 \\ +1 & +1 & +1 \end{bmatrix}$$

---

### 2.4.2. Toán tử Gradient Sobel $3 \times 3$ (Slide 36–41)
- **Mặt nạ có trọng số làm mịn vuông góc hướng đạo hàm**:
  $$G_x = \begin{bmatrix} -1 & 0 & +1 \\ -2 & 0 & +2 \\ -1 & 0 & +1 \end{bmatrix}, \quad G_y = \begin{bmatrix} -1 & -2 & -1 \\ 0 & 0 & 0 \\ +1 & +2 & +1 \end{bmatrix}$$
- **Độ lớn Gradient và Góc hướng**:
  $$M(x, y) = \sqrt{G_x^2 + G_y^2}, \quad \theta(x, y) = \arctan\left(\frac{G_y}{G_x}\right)$$

---

### 2.4.3. Toán tử Laplacian of Gaussian (LoG) & Dò điểm qua 0 (Slide 21)
- **Mặt nạ LoG liên tục**:
  $$\text{LoG}(x, y) = -\frac{1}{\pi \sigma^4} \left[ 1 - \frac{x^2 + y^2}{2\sigma^2} \right] \exp\left( -\frac{x^2 + y^2}{2\sigma^2} \right)$$
- **Dò điểm cắt qua 0 (Zero-Crossing)**: Điểm $(x, y)$ được công nhận là biên khi tích của 2 điểm đối xứng qua tâm trong lân cận $3 \times 3$ mang dấu âm: $P_1 \cdot P_2 < 0$ và $|P_1 - P_2| > \text{Threshold}$.

---

### 2.4.4. Thuật toán Canny Edge Detector 4 Bước (Chương 7 Tiếng Việt Slide 21–26)
1. **Làm mịn Gauss**: Lọc bằng kernel tách được $\sigma = 1.2$.
2. **Tính Gradient Sobel & Lượng tử hóa góc hướng $\theta$ vào 4 cung**:
   - $0^\circ$ (Ngang), $45^\circ$ (Chéo chính), $90^\circ$ (Dọc), $135^\circ$ (Chéo phụ).
3. **Triệt tiêu không cực đại (Non-Maximum Suppression - NMS)**:
   Nếu $M(x, y)$ nhỏ hơn bất kỳ láng giềng nào theo hướng gradient $\theta(x, y)$, gán $M(x, y) = 0$. Làm mảnh đường biên về độ dày đúng 1 pixel.
4. **Phân ngưỡng kép (Double Thresholding) & Duyệt vết BFS**:
   - $M \ge T_{\text{high}}$: Biên mạnh (Strong Edge).
   - $T_{\text{low}} \le M < T_{\text{high}}$: Biên yếu (Weak Edge).
   - $M < T_{\text{low}}$: Bị loại bỏ.
   - Chỉ giữ lại biên yếu nếu có đường liên thông 8 hướng đến ít nhất một biên mạnh.

---

## 2.5. PHÂN ĐOẠN OTSU TỐI ƯU & HÌNH THÁI HỌC BỘC LỘ RANH GIỚI VẾT DẦU (CHƯƠNG 6, 7 UTC & ĐỀ 18 NASA)

### 2.5.1. Phân đoạn ngưỡng Otsu tối ưu & Hệ số khả tách $\eta$ (Chương 7 Slide 12–18)
Ngưỡng tối ưu $T^*$ được tìm bằng cách cực đại hóa **phương sai giữa các lớp (Between-class Variance)**:
$$\sigma_B^2(T) = \omega_0(T) \cdot \omega_1(T) \cdot [\mu_0(T) - \mu_1(T)]^2$$
Trong đó:
- $\omega_0(T) = \sum_{i=0}^T p(i)$ (Tỷ lệ pixel vết dầu).
- $\omega_1(T) = 1 - \omega_0(T)$ (Tỷ lệ pixel nền biển).
- $\mu_0(T) = \frac{1}{\omega_0} \sum_{i=0}^T i \cdot p(i)$ (Mức xám trung bình vết dầu).
- $\mu_1(T) = \frac{1}{\omega_1} \sum_{i=T+1}^{L-1} i \cdot p(i)$ (Mức xám trung bình nền biển).
- **Hệ số khả tách (Separability Metric)**:
  $$\eta = \frac{\sigma_B^2(T^*)}{\sigma_T^2} \in [0, 1]$$
  Với $\sigma_T^2 = \sum_{i=0}^{L-1} (i - \mu_T)^2 p(i)$. Giá trị $\eta > 0.60$ chứng minh phân bố lược đồ độ xám 2 đỉnh (Bimodal) cực kỳ phân tách.

---

### 2.5.2. Các phép toán Hình thái học toán học (Mathematical Morphology - Chương 6 Slide 10–14)
- **Phép Co (Erosion)** với phần tử cấu trúc $B$:
  $$[A \ominus B](x, y) = \min_{(i, j) \in B} A(x + i, y + j)$$
- **Phép Giãn (Dilation)** với phần tử cấu trúc $B$:
  $$[A \oplus B](x, y) = \max_{(i, j) \in B} A(x + i, y + j)$$
- **Phép Mở (Opening $A \circ B$)**:
  $$A \circ B = (A \ominus B) \oplus B$$
  Dùng đĩa tròn $5 \times 5$, triệt tiêu sạch sẽ các đốm nhị phân rác do sóng biển ngoài khơi.
- **Phép Đóng (Closing $A \bullet B$)**:
  $$A \bullet B = (A \oplus B) \ominus B$$
  Dùng đĩa tròn $7 \times 7$ hoặc $11 \times 11$, lấp đầy các lỗ thủng do bọt sóng bên trong lòng mảng dầu, tạo khối dầu đặc ruột đồng nhất.

---

### 2.5.3. Trích xuất Ranh giới Hình thái học $\beta(A)$ (Chương 6 Slide 16)
Lấy mảng dầu đặc ruột $A$ trừ đi phần lõi sau khi co bằng phần tử cấu trúc $B_{3 \times 3}$:
$$\beta(A) = A \setminus (A \ominus B_{3 \times 3}) = A - \text{erode}(A)$$
- **Tính chất giải tích**: Vì phần tử cấu trúc có bán kính $r=1$, phép trừ tập hợp này bóc tách chính xác lớp vỏ ngoài cùng có **độ dày đúng 1 pixel**, ôm khít $100\%$ đường viền thật của vết dầu và hoàn toàn sạch bóng các đường viền rác trên mặt biển.
