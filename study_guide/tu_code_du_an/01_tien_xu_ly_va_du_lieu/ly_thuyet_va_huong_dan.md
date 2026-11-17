# 📡 MODULE 1: TIỀN XỬ LÝ VÀ QUẢN LÝ DỮ LIỆU SAR

> **Phạm vi tài liệu tự học — cập nhật 17/11/2026:** đây là giải thích và mã minh họa độc lập, không phải pipeline đã nghiệm thu hoặc bằng chứng đạt 100% đề. Công thức giản lược, ảnh giả lập, ví dụ ghép greedy và mô phỏng trôi dầu không thay thế kết quả trong `src/sar_oil`, `scripts` và `results`. Lee không bảo đảm giữ biên tuyệt đối; agreement 100% chỉ áp dụng cho ca đã đo; F1 SOS 0,3403 là cấu hình được chọn theo quy tắc dung sai, không phải cực đại nghiêm ngặt. Ưu tiên [đối chiếu hiện tại](../../../docs/DANH_GIA_DU_AN_VA_DOI_CHIEU_DE_18.md) khi có khác biệt.

## 1. BẢN CHẤT VẬT LÝ CỦA DỮ LIỆU SAR (BẠN ĐANG XỬ LÝ CÁI GÌ?)

### 1.1. Ảnh SAR khác ảnh máy ảnh thông thường (RGB) như thế nào?
- **Ảnh thông thường (Optical RGB):** Máy ảnh là cảm biến **thụ động (passive)**. Nó đợi ánh sáng mặt trời chiếu vào vật thể rồi dội vào ống kính. Giá trị pixel là 3 số nguyên $[0, 255]$ tương ứng với 3 kênh Đỏ - Lục - Lam.
- **Ảnh Radar SAR:** Vệ tinh Sentinel-1 là cảm biến **chủ động (active)**. Nó mang theo máy phát sóng vi ba (băng tần C, bước sóng $\lambda \approx 5.546\text{ cm}$). Nó tự bắn sóng xuống biển rồi đo thời gian và công suất dội lại.
  - Giá trị nguyên thủy thu được là số phức biểu diễn biên độ và pha.
  - Khi phát hiện dầu tràn, ta quan tâm đến **hệ số tán xạ ngược (Radar Backscatter Coefficient)** ký hiệu là $\sigma^0$ (Sigma-nought) — là một số thực dương dấu phẩy động (`float32` hoặc `float64`), đo bằng đơn vị $\text{m}^2/\text{m}^2$.

### 1.2. Thang tuyến tính (Linear) vs Thang Đề-xi-ben (dB)
Vì công suất sóng radar dội lại có thể chênh lệch nhau hàng triệu lần giữa một con tàu thép khổng lồ và một vệt dầu loang phẳng lặng, các nhà khoa học thường chuyển đổi sang thang logarit (dB):
$$\sigma^0_{\text{dB}} = 10 \cdot \log_{10}(\sigma^0_{\text{linear}})$$

- Mặt biển bình thường có $\sigma^0_{\text{dB}} \approx -12\text{ dB}$ đến $-18\text{ dB}$.
- Vết dầu tràn dập tắt sóng mao dẫn, làm giảm năng lượng phản xạ từ $6\text{ dB}$ đến $12\text{ dB}$, khiến giá trị tụt xuống $-20\text{ dB}$ đến $-28\text{ dB}$ (đen sẫm).
- Tàu biển bằng kim loại phản xạ cực mạnh góc vuông (Corner Reflector), có giá trị dương $+5\text{ dB}$ đến $+15\text{ dB}$ (sáng chói).

### 1.3. Góc tới (Incidence Angle $\theta$) và Chuẩn hóa Gamma-nought ($\gamma^0$)
- Vệ tinh không chụp thẳng đứng từ trên đầu (nadir) mà bắn sóng chéo sang một bên (side-looking radar).
- Góc giữa tia radar và đường pháp tuyến vuông góc với mặt biển gọi là **Góc tới $\theta$** (Incidence angle):
  - Ở rìa gần vệ tinh (Near range): $\theta \approx 29^\circ$ $\to$ Sóng đập dốc đứng hơn $\to$ Biển sáng hơn.
  - Ở rìa xa vệ tinh (Far range): $\theta \approx 46^\circ$ $\to$ Sóng đập thoai thoải $\to$ Biển tối hơn.
- Nếu không xử lý góc tới, một thuật toán ngây thơ sẽ nhầm tưởng toàn bộ mép bên phải bức ảnh là dầu tràn!
- Để khử sai lệch hình học này, ta chuyển sang hệ số phản xạ **Gamma-nought ($\gamma^0$)**:
$$\gamma^0 = \frac{\sigma^0}{\cos\theta}$$

---

## 2. HƯỚNG DẪN CODE CHAY: MODULE `data_loader.py`

Trong module này, bạn sẽ tự lập trình các hàm:
1. `read_sar_image()`: Đọc ảnh mức xám (PNG chuẩn hóa về $[0, 1]$ hoặc mảng số thực NPZ).
2. `linear_to_db()` & `db_to_linear()`: Chuyển đổi qua lại giữa thang đo tuyến tính và dB mà không bị lỗi chia cho 0 (`log(0)`).
3. `interpolate_incidence_angle()`: Tự viết thuật toán nội suy song tuyến tính (Bilinear Interpolation) ma trận góc tới $\theta(x, y)$ từ bảng tra cứu thưa (LUT - Look-Up Table).
4. `normalize_to_gamma0()`: Áp dụng công thức $\gamma^0 = \sigma^0 / \cos\theta$.

Hãy xem mã nguồn đầy đủ và chú thích chi tiết trong file `data_loader.py`!
