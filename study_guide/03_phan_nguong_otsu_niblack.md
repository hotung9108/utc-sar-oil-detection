# Chuyên đề 03: Phân ngưỡng tách vùng tối — Otsu toàn cục & Niblack thích nghi

> **Phạm vi tài liệu tự học — cập nhật 17/11/2026:** đây là giải thích và mã minh họa độc lập, không phải pipeline đã nghiệm thu hoặc bằng chứng đạt 100% đề. Công thức giản lược, ảnh giả lập, ví dụ ghép greedy và mô phỏng trôi dầu không thay thế kết quả trong `src/sar_oil`, `scripts` và `results`. Lee không bảo đảm giữ biên tuyệt đối; agreement 100% chỉ áp dụng cho ca đã đo; F1 SOS 0,3403 là cấu hình được chọn theo quy tắc dung sai, không phải cực đại nghiêm ngặt. Ưu tiên [đối chiếu hiện tại](../docs/DANH_GIA_DU_AN_VA_DOI_CHIEU_DE_18.md) khi có khác biệt.

> 🎯 **Mục tiêu chuyên đề:**\
> Hiểu tại sao không thể dùng một ngưỡng cố định. Nắm chắc chứng minh toán học của thuật toán **Otsu** (tối đa hóa phương sai liên lớp). Hiểu nguyên lý phân ngưỡng thích nghi cục bộ **Niblack** và lý do tại sao Otsu lại được chọn làm cấu hình chính trong pipeline dự án.

---

## 1. Trực giác đời thường: Tại sao không thể dùng Ngưỡng cố định (Fixed Threshold)?

Giả sử sau khi lọc Lee, ảnh có mức xám từ $0$ đến $255$. Bạn nghĩ: *"Vết dầu màu đen, vậy cứ pixel nào $< 80$ thì là dầu, $\ge 80$ là nước biển"*.\
Ý tưởng này sẽ **thất bại ngay từ bức ảnh thứ hai**:
1. **Gió thay đổi:** Hôm nay trời gió mạnh ($8\text{ m/s}$), biển cuộn sóng dữ dội $\to$ Nền biển rất sáng (mức xám $160-200$). Khi đó vết dầu bị kéo lên mức xám $70-90$.
2. **Hôm khác trời gió nhẹ:** Nền biển chỉ đạt mức xám $90-110$. Khi đó vết dầu tụt xuống mức xám $20-40$.
3. **Góc tới thay đổi:** Ở cự ly gần, biển sáng; ở cự ly xa, biển tối.
$\implies$ **Một ngưỡng cố định sẽ biến bạn thành thảm họa:** Hoặc là phát hiện trúng toàn bộ biển thành dầu, hoặc là bỏ sót sạch không phát hiện được vết dầu nào!
$\implies$ **Bắt buộc phải dùng Phân ngưỡng tự động thích ứng với từng bức ảnh!**

---

## 2. Bản chất toán học của thuật toán Otsu (Nobuyuki Otsu, 1979)

Thuật toán Otsu là giải pháp kinh điển và thanh lịch nhất để tìm ra một ngưỡng tối ưu $T^*$ tự động từ biểu đồ tần số mức xám (Histogram).

### Ý tưởng cốt lõi:
Một bức ảnh sau khi phân ngưỡng sẽ bị chia thành 2 lớp pixel:
* **Lớp 0 ($C_0$):** Các pixel tối có mức xám $\le T$ (Vùng dầu ứng viên).
* **Lớp 1 ($C_1$):** Các pixel sáng có mức xám $> T$ (Nền biển).

Một ngưỡng $T$ được gọi là **tốt nhất** khi nó thỏa mãn đồng thời 2 điều kiện:
1. **Nội bộ mỗi lớp phải đồng nhất nhất có thể:** Tức là phương sai bên trong từng lớp (**Within-class variance** $\sigma_w^2$) phải là **nhỏ nhất**.
2. **Hai lớp phải tách biệt nhau xa nhất có thể:** Tức là phương sai giữa hai lớp (**Between-class variance** $\sigma_b^2$) phải là **lớn nhất**.

---

### Chứng minh toán học: Tại sao chỉ cần tìm $\max \sigma_b^2$?

Tổng phương sai của toàn bộ bức ảnh ($\sigma_T^2$) là một hằng số cố định đối với một bức ảnh cho trước:
$$\sigma_T^2 = \sigma_w^2(T) + \sigma_b^2(T) = \text{const}$$

* $\sigma_w^2(T) = \omega_0(T) \sigma_0^2(T) + \omega_1(T) \sigma_1^2(T)$ (Tổng phương sai nội lớp có trọng số).
* $\sigma_b^2(T) = \omega_0(T)(\mu_0(T) - \mu_T)^2 + \omega_1(T)(\mu_1(T) - \mu_T)^2$ (Phương sai liên lớp).

Vì tổng của chúng là hằng số, nên:
$$\min \sigma_w^2(T) \iff \max \sigma_b^2(T)$$

Thay vì phải tính phương sai nội lớp rất tốn kém (phải tính $\sigma_0^2$ và $\sigma_1^2$), ta chỉ cần **tìm ngưỡng $T$ làm cực đại hóa phương sai liên lớp $\sigma_b^2(T)$**!

Biến đổi đại số rút gọn phương sai liên lớp:
$$\sigma_b^2(T) = \omega_0(T) \omega_1(T) \left(\mu_0(T) - \mu_1(T)\right)^2$$
Hoặc biểu diễn qua giá trị trung bình tích lũy:
$$\boxed{\sigma_b^2(T) = \frac{(\mu_T \cdot \omega(T) - \mu(T))^2}{\omega(T) \cdot (1 - \omega(T))}}$$

Trong đó:
* $\omega(T) = \sum_{i=0}^T p_i$: Xác suất tích lũy (tỉ lệ pixel thuộc lớp 0).
* $\mu(T) = \sum_{i=0}^T i \cdot p_i$: Giá trị trung bình tích lũy đến mức xám $T$.
* $\mu_T = \sum_{i=0}^{255} i \cdot p_i$: Giá trị trung bình của toàn ảnh.

### Độ phức tạp cực nhanh:
Nhờ công thức này, ta chỉ cần quét ngưỡng $T$ từ $0$ đến $255$ đúng 256 bước. Mỗi bước chỉ mất vài phép tính cộng trừ nhân chia số học $\to$ Độ phức tạp thời gian là $O(256)$, chạy trong chưa đầy **1 phần nghìn giây**!

---

## 3. Khi nào Otsu thất bại? (Giới hạn của Otsu)

Dù rất mạnh mẽ, Otsu vẫn có một "gót chân Asilles" mà bạn cần nắm chắc để trả lời câu hỏi phản biện:
* **Điều kiện lý tưởng của Otsu:** Histogram của ảnh phải có **dạng 2 đỉnh rõ rệt (Bimodal histogram)**, một đỉnh đại diện cho dầu và một đỉnh đại diện cho biển.
* **Khi nào Otsu bị sập?**
  1. **Vết dầu quá nhỏ (Vài chục đến vài trăm pixel):** Số lượng pixel dầu chiếm chưa tới $1\%$ diện tích ảnh. Khi đó đỉnh của dầu bị chìm hoàn toàn vào sườn của đỉnh nền biển $\to$ Otsu sẽ chọn nhầm ngưỡng, cắt đứt hoặc bỏ sót vết dầu.
  2. **Độ sáng nền biển bị nghiêng (Góc tới hoặc gió không đều):** Một nửa bức ảnh biển sáng, một nửa ảnh biển tối $\to$ Histogram bị bẹt ra, Otsu toàn cục sẽ cắt ngang ảnh làm toàn bộ nửa ảnh tối bị nhận nhầm thành dầu!

---

## 4. Giải pháp phân ngưỡng thích nghi cục bộ: Thuật toán Niblack

Để khắc phục nhược điểm của ngưỡng toàn cục, phương pháp **phân ngưỡng cục bộ thích ứng (Adaptive Thresholding)** ra đời, tiêu biểu là giải thuật **Niblack (1986)**:

### Nguyên lý hoạt động:
Thay vì tính 1 ngưỡng cho toàn bộ ảnh, Niblack dùng một cửa sổ trượt hình chữ nhật kích thước $\text{size} \times \text{size}$ (ví dụ $31\times 31$ hoặc $51\times 51$).
Tại mỗi pixel $(x, y)$, thuật toán tính:
* Giá trị trung bình cục bộ trong cửa sổ: $m(x, y)$
* Độ lệch chuẩn cục bộ trong cửa sổ: $s(x, y) = \sqrt{\frac{1}{N} \sum (I_i - m)^2}$

Ngưỡng động tại pixel $(x, y)$ được tính bằng công thức:
$$\boxed{T(x, y) = m(x, y) - k \cdot s(x, y)}$$

* Pixel $(x, y)$ được coi là dầu nếu:
  $$I(x, y) < T(x, y) \iff I(x, y) < m(x, y) - k \cdot s(x, y)$$

### Ý nghĩa của hệ số $k$:
* $k$ là một hằng số thực (thường chọn từ $0.2$ đến $0.5$).
* Hệ số $k$ quy định mức độ khắt khe: Pixel phải tối hơn mức trung bình lân cận ít nhất là $k$ lần độ lệch chuẩn thì mới được công nhận là vết dầu.
* Nếu $k$ quá nhỏ $\to$ Nhiều nhiễu đốm trên biển bị nhận nhầm.
* Nếu $k$ quá lớn $\to$ Bỏ sót vết dầu loang mỏng.

---

## 5. So sánh thực nghiệm trong dự án: Tại sao cuối cùng lại chọn Otsu?

Trong dự án BTL này, nhóm đã thực hiện cả 2 phương án và so sánh khoa học trên 671 ảnh validation:
* **Nhánh 1 (Otsu toàn cục):** Kết hợp với Lee $7\times 7, L=4$ đạt **F1 ứng viên = 0.0855** (Recall = 0.3828).
* **Nhánh 2 (Niblack thích nghi):** Khảo sát 27 tổ hợp tham số Niblack ($\text{size} \in \{15, 31, 51\}$, $k \in \{0.2, 0.5, 0.8\}$). Cấu hình tốt nhất là $\text{size}=51, k=0.2$ kết hợp với Lee $7\times 7, L=1$ đạt **F1 ứng viên = 0.0325** (Recall = 0.2562).

### Tại sao Otsu lại thắng Niblack trên bộ dữ liệu SOS?
1. **Đặc thù bộ dữ liệu SOS:** Các ảnh trong SOS đã được cắt thành các mảnh patch nhỏ ($256\times 256$ hoặc $512\times 512$). Trên một phạm vi không gian hẹp như vậy, độ sáng của nền biển tương đối đồng nhất, không bị chênh lệch góc tới quá lớn.
2. **Nhược điểm cửa sổ trượt của Niblack:** Ở những vùng biển hoàn toàn sạch dầu (vùng đồng nhất), độ lệch chuẩn $s(x, y) \approx 0$. Khi đó ngưỡng $T \approx m(x, y)$. Khoảng $50\%$ số pixel ngẫu nhiên sẽ có giá trị $< m$, dẫn đến việc Niblack sinh ra một lượng khổng lồ các đốm đen giả mạo trên nền biển phẳng!
$\implies$ Nhóm quyết định khóa **Otsu** làm cấu hình chính của pipeline, nhưng vẫn giữ nhánh Niblack như một thực nghiệm đối chứng nâng cao theo đúng yêu cầu thao tác của Đề 18.

---

## 6. Hệ thống câu hỏi truy vấn bản chất (Socratic Q&A)

### Câu hỏi 1:
* **Hỏi:** *Tại sao trong hàm `core.otsu(a)`, nhóm lại chia histogram thành đúng 256 bin từ 0 đến 1 mà không chia nhiều hơn (ví dụ 1024 bin)?*
* **Trả lời:** Ảnh SAR đầu vào có độ sâu mức xám 8-bit (tương ứng 256 mức giá trị rời rạc). Việc sử dụng 256 bin cố định đảm bảo bao phủ trọn vẹn toàn bộ các mức giá trị mà không làm mất thông tin. Tăng lên 1024 bin không làm tăng độ chính xác phân ngưỡng mà chỉ làm tăng thêm chi phí tính toán không cần thiết.

### Câu hỏi 2:
* **Hỏi:** *Nếu một bức ảnh hoàn toàn không có vết dầu nào (chỉ toàn biển sạch), thuật toán Otsu sẽ xử lý ra sao?*
* **Trả lời:** Đây chính là nhược điểm bẩm sinh của Otsu! Vì Otsu luôn luôn tìm một ngưỡng để chia ảnh làm 2 lớp, nên dù ảnh không có dầu, Otsu vẫn sẽ "ép" phân chia nửa pixel tối hơn của biển thành lớp 0. Tuy nhiên, trong pipeline của dự án, các vùng tối giả mạo này sẽ bị **loại bỏ ở Bước 4 (lọc diện tích $< 64$ px) và Bước 6 (bộ phân lớp SVM dựa trên 8 đặc trưng)**.

---

## 7. Trắc nghiệm ôn tập nhanh (Quiz 03)

**Câu 1:** Mục tiêu tối ưu hóa của thuật toán Otsu là gì?\
A. Tối đa hóa tổng số pixel màu đen.\
B. Tối đa hóa phương sai giữa hai lớp ($\sigma_b^2$) hoặc tối thiểu hóa phương sai nội lớp ($\sigma_w^2$).\
C. Cực tiểu hóa thời gian chạy của máy tính.\
D. Cực đại hóa độ sáng trung bình của toàn ảnh.\
*(Đáp án: **B**)*

**Câu 2:** Độ phức tạp thuật toán của Otsu khi tính trên histogram 256 bin là:\
A. $O(W \cdot H)$ cho khâu đếm histogram, sau đó là $O(256)$ cho khâu tìm ngưỡng.\
B. $O(W^2 \cdot H^2)$\
C. $O(256^2)$\
D. $O(N \log N)$\
*(Đáp án: **A**)*

**Câu 3:** Công thức phân ngưỡng thích nghi cục bộ Niblack là:\
A. $T = m + k \cdot s$\
B. $T = m - k \cdot s$\
C. $T = m \cdot k / s$\
D. $T = s - k \cdot m$\
*(Đáp án: **B**)*

**Câu 4:** Trong điều kiện nào thì thuật toán Otsu toàn cục dễ bị chọn sai ngưỡng nhất?\
A. Khi ảnh có tỷ lệ vết dầu chiếm đúng 50% diện tích.\
B. Khi vết dầu quá nhỏ (chiếm $< 1\%$ diện tích) hoặc độ sáng nền biển không đồng đều.\
C. Khi ảnh có độ phân giải quá cao.\
D. Khi ảnh đã được khử nhiễu hoàn hảo.\
*(Đáp án: **B**)*

**Câu 5:** Tại sao trên bộ dữ liệu SOS, nhánh Otsu lại cho kết quả F1 cao hơn nhánh Niblack?\
A. Vì Otsu chạy nhanh hơn Niblack.\
B. Vì ảnh SOS là các patch nhỏ có nền đồng nhất; Niblack bị sinh nhiều đốm giả ở vùng biển phẳng do độ lệch chuẩn cục bộ quá bé.\
C. Vì Niblack không thể lập trình được bằng NumPy.\
D. Vì Otsu là thuật toán mới hơn Niblack.\
*(Đáp án: **B**)*
