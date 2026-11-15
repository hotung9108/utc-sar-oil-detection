# 📏 MODULE 4: TOÁN HỌC TRÍCH XUẤT 8 ĐẶC TRƯNG VÙNG

> **Phạm vi tài liệu tự học — cập nhật 17/11/2026:** đây là giải thích và mã minh họa độc lập, không phải pipeline đã nghiệm thu hoặc bằng chứng đạt 100% đề. Công thức giản lược, ảnh giả lập, ví dụ ghép greedy và mô phỏng trôi dầu không thay thế kết quả trong `src/sar_oil`, `scripts` và `results`. Lee không bảo đảm giữ biên tuyệt đối; agreement 100% chỉ áp dụng cho ca đã đo; F1 SOS 0,3403 là cấu hình được chọn theo quy tắc dung sai, không phải cực đại nghiêm ngặt. Ưu tiên [đối chiếu hiện tại](../../../docs/DANH_GIA_DU_AN_VA_DOI_CHIEU_DE_18.md) khi có khác biệt.

## 1. TẠI SAO PHẢI CẦN 8 ĐẶC TRƯNG NÀY?

Sau khi phân đoạn, ta thu được hàng trăm "đốm tối". Nhưng làm sao biết đốm tối nào là **Vết dầu tràn thật**, đốm nào chỉ là **Vùng biển lặng gió (look-alike)**?
Ta phải trích xuất một vector 8 chiều (gọi là Thẻ Căn Cước) bao hàm cả **Hình học (Geometry)** và **Bức xạ (Radiometry)** theo tiêu chuẩn của Solberg (1999) và Brekke & Solberg (2005).

---

## 2. CHỨNG MINH TOÁN HỌC TỪNG ĐẶC TRƯNG

### 1. `area_fraction` (Tỷ lệ diện tích)
$$f_1 = \frac{\text{Area}}{H \times W}$$
- Vết dầu tràn lớn chiếm tỷ lệ đáng kể trên lát cắt radar; các bọt sóng nhỏ chỉ chiếm tỷ lệ không đáng kể.

### 2. `elongation` (Độ thuôn dài từ Ma trận Quán tính)
Tại sao không lấy chiều dài chia chiều rộng hộp bao?
- Vì vết dầu loang có thể nằm chéo góc $45^\circ$, khi đó hộp bao chữ nhật trục $x-y$ sẽ là một hình vuông (tỷ số = 1), hoàn toàn làm sai lệch bản chất!
- **Giải pháp toán học:** Tính **Ma trận hiệp phương sai tọa độ (Covariance Matrix)** của các pixel trong vùng:
$$C = \begin{bmatrix} \mathrm{Var}(r) & \mathrm{Cov}(r, c) \\ \mathrm{Cov}(r, c) & \mathrm{Var}(c) \end{bmatrix}$$
- Giải phương trình đặc trưng tìm hai trị riêng $\lambda_1 \ge \lambda_2 \ge 0$. Hai trị riêng này chính là phương sai dọc theo 2 trục quán tính chính của elip tương đương:
$$f_2 = \sqrt{\frac{\lambda_1}{\lambda_2}}$$
- Dầu tràn bị dòng hải lưu kéo lê thành dải dài ngoằng $\implies f_2 > 3.0$. Vùng biển lặng gió có xu hướng tròn xoe $\implies f_2 \approx 1.0 \text{ - } 1.5$.

### 3. `extent` (Độ lấp đầy hộp bao)
$$f_3 = \frac{\text{Area}}{\text{BBox\_Height} \times \text{BBox\_Width}}$$
- Đo lường mức độ đặc hay rỗng của vùng.

### 4. `complexity` (Độ phức tạp đường biên / Thương số đẳng chu)
Theo bất đẳng thức đẳng chu trong hình học vi phân, với mọi hình khép kín có chu vi $P$ và diện tích $A$:
$$P^2 \ge 4\pi A$$
Dấu bằng chỉ xảy ra khi hình là một hình tròn hoàn hảo.
Ta định nghĩa độ phức tạp biên:
$$f_4 = \frac{P^2}{4\pi A}$$
- Hình tròn: $f_4 = 1.0$.
- Vết dầu loang có đường biên fractal nhăn nheo, lượn sóng: $f_4 \approx 2.0 \text{ - } 8.0$.

### 5. `mean` (Cường độ trung bình nội vùng)
$$f_5 = \frac{1}{A} \sum_{(r, c) \in \text{Region}} img(r, c)$$
- Dầu dập tắt sóng mao dẫn $\implies f_5$ rất thấp (tối).

### 6. `std` (Độ lệch chuẩn cường độ nội vùng)
$$f_6 = \sqrt{\frac{1}{A} \sum_{(r, c) \in \text{Region}} \left(img(r, c) - f_5\right)^2}$$
- Phản ánh độ đồng nhất của váng dầu.

### 7. `boundary_gradient` (Độ dốc biên độ dọc viền vết dầu)
Sử dụng 2 toán tử vi phân không gian Sobel $3 \times 3$:
$$S_x = \begin{bmatrix} -1 & 0 & 1 \\ -2 & 0 & 2 \\ -1 & 0 & 1 \end{bmatrix}, \quad S_y = \begin{bmatrix} -1 & -2 & -1 \\ 0 & 0 & 0 \\ 1 & 2 & 1 \end{bmatrix}$$
Tại mỗi pixel biên $(r, c)$, độ lớn gradient là:
$$G(r, c) = \sqrt{\left(img * S_x\right)^2 + \left(img * S_y\right)^2}$$
$$f_7 = \frac{1}{P} \sum_{(r, c) \in \text{Boundary}} G(r, c)$$
- Vết dầu thật có ranh giới hóa lý rất rõ ràng giữa dầu và nước biển $\implies$ Gradient biên lớn. Vùng lặng gió mép mờ dần $\implies$ Gradient biên nhỏ.

### 8. `background_contrast` (Độ tương phản vành nền 5 pixel)
- Giãn nở (Dilate) vết dầu thêm 5 pixel, sau đó trừ đi chính vết dầu để thu được một **chiếc phao bao quanh vết dầu dày 50m**:
$$\text{Ring} = \text{Dilate}(\text{Region}, 5) \setminus \text{Region}$$
$$f_8 = \mu_{\text{Ring}} - f_5$$
- So sánh dầu với nước biển ngay sát nách nó giúp loại bỏ hoàn toàn ảnh hưởng của độ sáng toàn cảnh hay góc chiếu xa.

Mở file `feature_extraction.py` để tự tay gõ từng dòng thuật toán!
