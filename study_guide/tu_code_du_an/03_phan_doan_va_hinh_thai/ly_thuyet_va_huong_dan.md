# ✂️ MODULE 3: PHÂN ĐOẠN ĐỐM TỐI VÀ HÌNH THÁI HỌC LIÊN THÔNG

> **Phạm vi tài liệu tự học — cập nhật 17/11/2026:** đây là giải thích và mã minh họa độc lập, không phải pipeline đã nghiệm thu hoặc bằng chứng đạt 100% đề. Công thức giản lược, ảnh giả lập, ví dụ ghép greedy và mô phỏng trôi dầu không thay thế kết quả trong `src/sar_oil`, `scripts` và `results`. Lee không bảo đảm giữ biên tuyệt đối; agreement 100% chỉ áp dụng cho ca đã đo; F1 SOS 0,3403 là cấu hình được chọn theo quy tắc dung sai, không phải cực đại nghiêm ngặt. Ưu tiên [đối chiếu hiện tại](../../../docs/DANH_GIA_DU_AN_VA_DOI_CHIEU_DE_18.md) khi có khác biệt.

## 1. PHÂN ĐOẠN TÁCH ĐỐM TỐI (DARK SPOT SEGMENTATION)

Sau khi ảnh đã được khử nhiễu đốm sạch sẽ, ta cần tìm các "đốm tối" nghi ngờ là dầu tràn.

### 1.1. Ngưỡng toàn cục Otsu (Nobuyuki Otsu 1979)
- Giả sử bức ảnh có 2 nhóm pixel: Nhóm 0 (Đốm tối/Dầu) và Nhóm 1 (Nền biển sáng).
- Otsu tìm một ngưỡng $t \in [0, 255]$ sao cho **phương sai liên lớp (Between-Class Variance)** đạt cực đại:
$$\sigma_B^2(t) = \omega_0(t) \cdot \omega_1(t) \cdot \left(\mu_0(t) - \mu_1(t)\right)^2$$
Trong đó:
- $\omega_0(t), \omega_1(t)$: Tỷ lệ số pixel thuộc Nhóm 0 và Nhóm 1.
- $\mu_0(t), \mu_1(t)$: Cường độ sáng trung bình của Nhóm 0 và Nhóm 1.

**Chứng minh tại sao cực đại hóa $\sigma_B^2$ lại tối ưu:**
Tổng phương sai toàn ảnh là hằng số: $\sigma_{\text{total}}^2 = \sigma_W^2(t) + \sigma_B^2(t)$ (trong đó $\sigma_W^2$ là phương sai nội lớp - độ hỗn loạn bên trong từng nhóm).
$\implies$ Cực đại hóa khoảng cách giữa 2 nhóm ($\sigma_B^2$) cũng chính là cực tiểu hóa sự hỗn loạn nội bộ bên trong từng nhóm ($\sigma_W^2$)!

### 1.2. Ngưỡng thích nghi cục bộ Niblack (Wayne Niblack 1986)
- Nếu ảnh SAR bị chênh lệch độ sáng lớn giữa Near range (rất sáng) và Far range (tối dần), ngưỡng Otsu toàn cục sẽ bị sai.
- Niblack trượt một cửa sổ kích thước $W \times W$ qua từng pixel $(x, y)$, tính giá trị trung bình cục bộ $m(x, y)$ và độ lệch chuẩn cục bộ $s(x, y)$:
$$T(x, y) = m(x, y) - k \cdot s(x, y)$$
- Hệ số $k$ (thường chọn $0.2$ hoặc $0.5$) quyết định độ "thụt lùi" dưới mức trung bình để đón bắt các vệt tối do dầu dập sóng.
- Pixel $(x, y)$ được coi là đốm tối nếu $img(x, y) < T(x, y)$.

---

## 2. HÌNH THÁI HỌC VÀ GÁN NHÃN LIÊN THÔNG 8 HƯỚNG

### 2.1. Toán tử hình thái học Erode & Dilate tự viết
- **Co (Erode):** Pixel chỉ giữ giá trị 1 nếu TẤT CẢ các pixel trong lân cận cấu trúc đều bằng 1. Tác dụng: Cắt đứt các eo nối mỏng manh giả tạo giữa hai vệt.
- **Giãn (Dilate):** Pixel thành 1 nếu CÓ ÍT NHẤT MỘT pixel lân cận bằng 1. Tác dụng: Hàn gắn các lỗ thủng li ti bên trong vệt dầu.
- **Đóng (Closing = Dilate rồi Erode):** Lấp đầy các vết nứt mà không làm thay đổi kích thước tổng thể.

### 2.2. Gán nhãn liên thông 8 hướng bằng thuật toán Union-Find
- Mỗi đốm tối bao gồm nhiều pixel nằm kề cạnh nhau. Ta xét liên thông **8 hướng** (kể cả đường chéo).
- **Thuật toán quét 2 lượt (Two-Pass) với cấu trúc Disjoint-Set (Union-Find):**
  1. *Lượt 1 (Quét xuôi từ trên xuống dưới, trái sang phải):* Gán nhãn tạm cho pixel dựa trên các pixel lân cận đã duyệt. Nếu gặp 2 nhãn khác nhau cùng chạm vào pixel hiện tại, ghi nhận 2 nhãn đó thuộc về cùng một gia đình bằng hàm `union(label_a, label_b)`.
  2. *Lượt 2 (Giải quyết nhãn tương đương):* Duyệt lại toàn bộ ảnh, thay thế nhãn tạm bằng nhãn gốc đại diện (`find_root`).
- **Lọc diện tích rác:** Đếm số pixel của từng nhãn. Vùng nào có $\text{area} < \text{min\_area}$ (mặc định 64 px) $\to$ gán về 0!

Mở file `segmentation.py` để tự tay gõ từng dòng thuật toán!
