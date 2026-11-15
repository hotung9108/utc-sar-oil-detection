# 🧹 MODULE 2: KHỬ NHIỄU ĐỐM SPECKLE VÀ BẢO TOÀN BIÊN

> **Phạm vi tài liệu tự học — cập nhật 17/11/2026:** đây là giải thích và mã minh họa độc lập, không phải pipeline đã nghiệm thu hoặc bằng chứng đạt 100% đề. Công thức giản lược, ảnh giả lập, ví dụ ghép greedy và mô phỏng trôi dầu không thay thế kết quả trong `src/sar_oil`, `scripts` và `results`. Lee không bảo đảm giữ biên tuyệt đối; agreement 100% chỉ áp dụng cho ca đã đo; F1 SOS 0,3403 là cấu hình được chọn theo quy tắc dung sai, không phải cực đại nghiêm ngặt. Ưu tiên [đối chiếu hiện tại](../../../docs/DANH_GIA_DU_AN_VA_DOI_CHIEU_DE_18.md) khi có khác biệt.

## 1. BẢN CHẤT TOÁN HỌC CỦA NHIỄU ĐỐM (SPECKLE NOISE)

### 1.1. Tại sao nhiễu trong ảnh thường là "Nhiễu cộng", còn SAR là "Nhiễu nhân"?
- **Ảnh thông thường (Additive Noise):** Pixel quan sát được bằng tín hiệu gốc cộng thêm nhiễu cảm biến:
$$y = x + n \quad (\text{với } n \sim \mathcal{N}(0, \sigma_n^2))$$
Muốn lọc nhiễu cộng rất dễ: Chỉ cần lấy trung bình cộng xung quanh, nhiễu âm dương sẽ tự triệt tiêu về 0.

- **Ảnh Radar SAR (Multiplicative Noise):** Do sóng vi ba kết hợp (coherent) tự giao thoa với nhau trên bề mặt nhám của sóng biển, nhiễu tỷ lệ thuận với chính độ sáng của vật thể:
$$y = x \cdot v$$
Trong đó:
- $x$: Cường độ tán xạ thực sự của mặt biển (cần tìm).
- $v$: Biến ngẫu nhiên nhiễu nhân có kỳ vọng $E[v] = 1$ và phương sai $\mathrm{Var}(v) = \sigma_v^2 = \frac{1}{L}$ (với $L$ là số lượt nhìn - looks).
- Vì là **nhiễu nhân**, chỗ nào càng sáng thì hạt nhiễu dao động càng dữ dội! Bộ lọc tuyến tính thông thường (như Mean) sẽ làm méo mó nghiêm trọng tín hiệu gốc.

---

## 2. NGUYÊN LÝ 4 BỘ LỌC VÀ CHỨNG MINH BỘ LỌC LEE (MMSE)

### 2.1. Box Mean Filter (Tối ưu bảng tích lũy SAT $O(1)$)
- Cộng toàn bộ pixel trong cửa sổ $K \times K$ chia cho $K^2$.
- **Kỹ thuật tối ưu:** Nếu dùng 2 vòng lặp lồng nhau tính tổng, độ phức tạp là $O(K^2 \cdot H \cdot W)$ (rất chậm). Trong file code, ta sử dụng **Bảng diện tích tích phân (Summed-Area Table / Integral Image)**:
$$I(r, c) = \sum_{i=0}^r \sum_{j=0}^c img(i, j)$$
Tổng của bất kỳ hình chữ nhật nào chỉ cần 4 phép tra cứu: $D - B - C + A$, đưa độ phức tạp về $O(1)$ mỗi pixel!

### 2.2. Median Filter (Lọc trung vị)
- Xếp thứ tự các giá trị trong cửa sổ và chọn phần tử ở vị trí giữa ($50\%$).
- Rất giỏi loại trừ các đốm cực đoan (spikes), nhưng làm tròn các góc nhọn của vết dầu hẹp.

### 2.3. Gaussian Filter (Lọc Gauss tách nhân 2D $\to$ hai lượt 1D)
- Trọng số suy giảm theo hàm mũ bán kính: $G(r, c) = \frac{1}{2\pi\sigma^2} e^{-\frac{r^2+c^2}{2\sigma^2}}$.
- Được tính bằng 2 lượt tích chập 1D (theo chiều ngang rồi theo chiều dọc) giúp tăng tốc độ gấp hàng chục lần.

### 2.4. Lee Filter — Đỉnh cao của lọc thích nghi bảo toàn biên
J.S. Lee (1980) đặt bài toán: Hãy tìm ước lượng tuyến tính tối ưu $\hat{x} = a + b \cdot y$ sao cho sai số bình phương trung bình cực tiểu (MMSE - Minimum Mean Square Error):
$$\min_{a, b} E\left[ (x - \hat{x})^2 \right]$$

Giải bài toán tối ưu vi phân này ta thu được:
$$\hat{x} = \bar{y} + W \cdot (y - \bar{y})$$
Trong đó $W$ là **hệ số trọng số thích nghi**:
$$W = \frac{\mathrm{Var}(x)}{\mathrm{Var}(y)} = \max\left(0, \frac{\sigma_y^2 - \bar{y}^2 \cdot \sigma_v^2}{\sigma_y^2 \cdot (1 + \sigma_v^2)}\right)$$
với $\sigma_v^2 = 1/L$.

**Ý nghĩa vật lý tuyệt vời của $W$:**
1. **Ở giữa vùng biển phẳng lặng:** Không có biên giới, phương sai $\sigma_y^2 \approx \bar{y}^2 \cdot \sigma_v^2 \implies W \approx 0$.
   $$\hat{x} \approx \bar{y} + 0 \cdot (y - \bar{y}) = \bar{y}$$
   $\implies$ Bộ lọc hành xử giống như bộ lọc Mean: **Làm mịn tuyệt đối mọi hạt tiêu!**
2. **Ở ranh giới mép vết dầu:** Có bước nhảy cường độ đột ngột, phương sai $\sigma_y^2 \gg \bar{y}^2 \cdot \sigma_v^2 \implies W \approx 1$.
   $$\hat{x} \approx \bar{y} + 1 \cdot (y - \bar{y}) = y$$
   $\implies$ Bộ lọc giữ nguyên giá trị gốc $y$: **Không làm mờ ranh giới mép vết dầu dù chỉ 1 pixel!**

---

## 3. THỰC NGHIỆM CHỌN BỘ LỌC CỦA DỰ ÁN

Trên tập kiểm chuẩn **671 ảnh Validation**, nhóm nghiên cứu đã cho 13 cấu hình thi đấu đối kháng:
- Không lọc: F1 = $0.0243$ (rất tệ vì nhiễu làm vỡ nát vùng liên thông).
- Box Mean $7\times 7$: Recall = $34.74\%$, F1 = $0.0841$ (nhòe biên).
- Median $7\times 7$: Recall = $34.44\%$, F1 = $0.0751$ (mất vết dầu mảnh).
- **Lee Filter $7\times 7$ ($L=4$): Recall = $38.28\%$, F1 = $0.0855$ (Chiến thắng thuyết phục ⭐)**.

Mở file `speckle_filters.py` để tự tay gõ từng dòng thuật toán!
