> **Tài liệu lịch sử:** nội dung dưới đây được giữ để tham khảo quá trình phát triển. Thuật toán, số liệu và demo hiện tại được mô tả trong [báo cáo chính](report/BAO_CAO_BTL_XLA.pdf), [README](../README.md) và [đối chiếu hiện tại](management/KIEM_TRA_HIEN_TAI.md). Không dùng các kết luận cũ để xác nhận phiên bản mới.

# CHƯƠNG 1: TỔNG QUAN ĐỀ TÀI & CƠ SỞ VẬT LÝ ẢNH RADAR SAR

> **Học phần**: Xử lý ảnh (Digital Image Processing - DIP)  
> **Khoa**: Công nghệ Thông tin — Trường Đại học Giao thông Vận tải (UTC)  
> **Giảng viên phụ trách**: TS. Phan Thanh Toàn, TS. Cao Thị Luyên  
> **Đề tài**: *Tăng Cường Độ Tương Phản, Khử Nhiễu & Xử Lý Biên Bộc Lộ Vết Dầu Tràn Trên Biển Từ Ảnh Radar SAR Sentinel-1*  
> **Định hướng học thuật**: Ánh xạ **Nhóm A (Tăng cường & Lọc ảnh)** kết hợp **Đề 5 (Làm nét & Phát hiện biên)** và **Đề 18 NASA (Phát hiện vết dầu loang trên ảnh SAR vi ba)**.

---

## 1.1. ĐẶT VẤN ĐỀ VÀ TÍNH CẤP THIẾT CỦA ĐỀ TÀI

### 1.1.1. Thảm họa ô nhiễm dầu tràn trên biển
Sự cố tràn dầu từ tàu chở dầu, giàn khoan khai thác ngoài khơi hoặc hoạt động xả thải trái phép của tàu thuyền thương mại là một trong những thảm họa sinh thái biển nghiêm trọng nhất hiện nay:
- **Tác động môi trường**: Lớp màng dầu ngăn cản quá trình trao đổi oxy giữa khí quyển và đại dương, dập tắt ánh sáng mặt trời đối với các sinh vật quang hợp dưới nước, hủy hoại hệ sinh thái rừng ngập mặn và bờ biển.
- **Tác động kinh tế**: Gây thiệt hại nặng nề cho ngành đánh bắt thủy hải sản, du lịch biển và chi phí phục hồi môi trường có thể lên tới hàng tỷ USD.
- **Yêu cầu ứng phó**: Cần phải phát hiện, khoanh vùng ranh giới và ước lượng diện tích loang dầu **càng sớm càng tốt** để các lực lượng cứu nạn, ứng phó sự cố triển khai phao quây và hóa chất phân tán kịp thời trước khi vệt dầu dạt vào bờ.

### 1.1.2. Tại sao phải sử dụng ảnh Radar khẩu độ tổng hợp (SAR)?
Trong giám sát biển diện rộng, các hệ thống cảm biến quang học truyền thống (chụp ảnh vệ tinh bằng ánh sáng nhìn thấy) bộc lộ những nhược điểm chí mạng:
1. **Phụ thuộc vào thời tiết**: Vùng biển nhiệt đới và các vùng đại dương thường xuyên bị mây mù bao phủ ($> 60\%$ thời gian trong năm). Cảm biến quang học hoàn toàn bất lực trước lớp mây dày.
2. **Phụ thuộc vào chu kỳ ngày - đêm**: Các sự cố xả dầu trộm thường diễn ra vào ban đêm. Cảm biến quang học thụ động không thể chụp ảnh khi thiếu ánh sáng mặt trời.

**Giải pháp đột phá: Radar khẩu độ tổng hợp (Synthetic Aperture Radar - SAR)**:
- SAR là hệ thống cảm biến vi ba chủ động (Active Microwave Sensor). Vệ tinh tự phát chùm sóng điện từ vi ba xuống mặt đất và thu lại tín hiệu tán xạ phản hồi (Backscattered signal).
- Chùm sóng vi ba băng C ($\lambda \approx 5.6\text{ cm}$) có khả năng **xuyên thấu qua mây, mưa, sương mù, khói bụi** và hoạt động **24/7 bất kể ngày đêm**.
- Do đó, ảnh vệ tinh Sentinel-1 SAR của Cơ quan Vũ trụ Châu Âu (ESA) và NASA là nguồn dữ liệu chuẩn mực số một thế giới cho việc giám sát dầu tràn đại dương.

---

## 1.2. CƠ SỞ VẬT LÝ VI BA & BẢN CHẤT HÌNH THÀNH VẾT DẦU TRÊN ẢNH SAR

### 1.2.1. Cơ chế tán xạ phản hồi Bragg trên mặt biển tự nhiên
Trên bề mặt đại dương, gió tương tác với mặt nước tạo ra các gợn sóng mao dẫn nhỏ (Capillary waves) và sóng trọng lực ngắn có bước sóng từ vài centimet đến vài chục centimet:
1. Khi bước sóng của sóng biển $\lambda_w$ thỏa mãn **điều kiện cộng hưởng Bragg** với bước sóng radar $\lambda_r$ và góc tới $\theta$:
   $$\lambda_w = \frac{\lambda_r}{2 \sin \theta}$$
2. Các đợt sóng mao dẫn này tạo thành các mặt tán xạ phản hồi kết hợp (Constructive interference), phản xạ một phần năng lượng vi ba cực lớn trở lại ăng-ten thu của vệ tinh.
3. Vì nhận được năng lượng tán xạ ngược dồi dào, trên ảnh SAR, **mặt biển tự nhiên luôn xuất hiện với mức xám trung bình hoặc sáng** ($\mu_{\text{sea}} \approx 130 \dots 200$).

```
                Tín hiệu Radar phát/thu
                     \        ^
                      \      /  (Tán xạ Bragg mạnh)
                       \    /
                        v  /
   ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
   Mặt biển có sóng mao dẫn (Capillary Waves) -> SÁNG
```

---

### 1.2.2. Cơ chế dập tắt sóng mao dẫn của váng dầu (Oil Film Damping)
Khi dầu thô hoặc nhũ tương dầu xuất hiện trên mặt biển:
1. **Tăng độ nhớt động lực học**: Lớp màng dầu mỏng (chỉ từ vài micromet đến vài milimet) làm tăng mạnh độ nhớt bề mặt và triệt tiêu sức căng bề mặt chất lỏng.
2. **Dập tắt sóng mao dẫn**: Các sóng mao dẫn Bragg bị dập tắt hoàn toàn. Mặt nước dưới lớp váng dầu trở nên phẳng lặng, nhẵn bóng như gương (Smooth specular surface).
3. **Phản xạ gương (Specular Reflection)**: Chùm sóng vi ba phát từ vệ tinh khi gặp mặt phẳng dầu nhẵn bóng bị phản xạ toàn phần đi theo hướng khác (góc phản xạ bằng góc tới), hầu như **không có bất kỳ năng lượng nào tán xạ ngược trở lại ăng-ten thu của vệ tinh**.
4. **Hệ quả trên ảnh SAR**: Vì ăng-ten thu nhận mức năng lượng gần bằng 0, vùng dầu tràn xuất hiện dưới dạng một **VÙNG TỐI CỤC BỘ (Dark Formation / Dark Patch)** với mức xám rất thấp ($\mu_{\text{slick}} \approx 20 \dots 60$).

```
                 Tín hiệu Radar phát
                     \
                      \
                       \
                        v       \  (Phản xạ gương đi nơi khác,
   ==============================\  không quay về vệ tinh)
   Lớp váng dầu nhẵn bóng (Oil Slick) -> TỐI ĐEN
```

---

## 1.3. BẢN CHẤT NHIỄU ĐỐM NHÂN (MULTIPLICATIVE SPECKLE NOISE)

Mặc dù có ưu thế vượt trội về khả năng xuyên mây và hoạt động ban đêm, ảnh vi ba SAR lại mang một nhược điểm cố hữu cực kỳ nghiêm trọng: **Nhiễu đốm (Speckle Noise)**.

### 1.3.1. Nguồn gốc vật lý của nhiễu đốm
Mỗi pixel trên ảnh SAR biểu diễn cho một ô phân giải trên mặt đất (Resolution cell) có kích thước khoảng $10\text{ m} \times 10\text{ m}$.
- Bên trong một ô phân giải có vô số các vật tán xạ vi mô độc lập (các gợn sóng, bọt biển, giọt nước).
- Các sóng tán xạ từ các vật thể này truyền về vệ tinh với pha ngẫu nhiên, dẫn đến hiện tượng **giao thoa tán xạ kết hợp (Coherent constructive & destructive interference)**.
- Giao thoa triệt tiêu tạo ra các điểm đen cực tối; giao thoa cộng hưởng tạo ra các đốm sáng trắng chói chang. Hiện tượng này tạo thành kết cấu lốm đốm hạt tiêu (Speckle pattern) bao phủ toàn bộ bức ảnh.

### 1.3.2. Mô hình toán học của nhiễu đốm: Nhiễu Nhân (Multiplicative Noise)
Khác với ảnh quang học thông thường bị chi phối bởi nhiễu cộng Gauss $I = f + n$, nhiễu đốm SAR tuân theo **mô hình nhiễu nhân**:
$$I(x, y) = R(x, y) \cdot \eta(x, y)$$
Trong đó:
- $I(x, y)$: Cường độ pixel quan sát được trên ảnh radar.
- $R(x, y)$: Hệ số phản xạ bề mặt thực tế (Radar Cross Section - thông tin ta cần khôi phục).
- $\eta(x, y)$: Thành phần nhiễu đốm có kỳ vọng toán học $E[\eta] = 1$ và phương sai $\sigma_\eta^2 = 1/L$ ($L$ là số tầm nhìn tương đương - Equivalent Number of Looks).

### 1.3.3. Hậu quả của nhiễu đốm đối với xử lý ảnh
1. **Phương sai phụ thuộc vào cường độ sáng**: Tại các vùng sáng, biên độ nhiễu đốm dao động rất mạnh, làm nhòe các chi tiết.
2. **Làm méo mó Histogram**: Nhiễu đốm làm phân bố độ xám bị bẹt ra, che lấp thung lũng phân tách giữa biển và mảng dầu.
3. **Phá vỡ các toán tử đạo hàm biên**: Các bộ lọc phát hiện biên cổ điển (Sobel, Prewitt, Canny) sử dụng đạo hàm $\nabla I$, sẽ phản ứng nhầm với hàng triệu gai nhiễu đốm và vẽ đường viền rác khắp mặt biển.

Do đó, **Khử đốm thích ứng bảo tồn biên (Lee MMSE) và Tăng cường tương phản (CLAHE)** là bước tiền xử lý **bắt buộc tiên quyết** trước khi thực hiện bộc lộ ranh giới vết dầu.

---

## 1.4. THÁCH THỨC VÙNG BIỂN LẶNG GIẢ MẠO (LOOK-ALIKES) & TIÊU CHUẨN NASA ĐỀ 18

Trong thực tế viễn thám, không phải mọi vùng tối trên ảnh SAR đều là dầu tràn. Tồn tại hiện tượng **Vùng tối giả mạo (Look-alikes)**:
1. **Vùng biển lặng gió tự nhiên (Low-wind areas)**: Khi tốc độ gió trên biển $< 2 \dots 3\text{ m/s}$, mặt biển không đủ gió để sinh ra sóng mao dẫn Bragg. Mặt biển tự nhiên trở nên phẳng lặng và cũng tạo ra vùng tối giống hệt vết dầu.
2. **Hiện tượng nở hoa của vi tảo (Algal blooms)**: Các chất hoạt động bề mặt sinh học (Biogenic slicks) do tảo tiết ra cũng làm nhẵn mặt nước.
3. **Bóng râm địa hình và hải lưu (Current shear zones)**.

### Tiêu chuẩn sàng lọc của NASA (NASA Topic 18):
Để loại trừ hiện tượng Look-alike mà không cần dùng đến học máy, hệ thống DIP kinh điển bắt buộc phải kiểm tra 2 tiêu chuẩn vật lý:
1. **Lọc diện tích tối thiểu**:
   $$\text{Area} \ge 300\text{ pixel}$$
   Loại bỏ các đốm tối li ti ngẫu nhiên do thung lũng sóng biển.
2. **Tỷ số tương phản nền biển lân cận (Contrast Ratio $C_R$)**:
   $$C_R = \frac{\mu_{\text{sea}} - \mu_{\text{slick}}}{\mu_{\text{sea}}} \ge 0.10$$
   Vết dầu khoáng thật có độ dập sóng rất mạnh, tạo độ chênh lệch mức xám sâu sắc với vùng biển đệm xung quanh ($C_R > 0.15 \dots 0.40$). Vùng biển lặng tự nhiên có ranh giới chuyển tiếp thoai thoải, mức xám giảm không dứt khoát ($C_R < 0.10$), do đó bị hệ thống loại bỏ chuẩn xác.

---

## 1.5. MỤC TIÊU VÀ NHIỆM VỤ HỌC THUẬT CỦA BÀI TẬP LỚN

Theo đề bài phân công của **TS. Phan Thanh Toàn** và **TS. Cao Thị Luyên**:
1. **Chuyên đề Nhóm A**: Cài đặt và thực nghiệm chuyên sâu các thuật toán Tăng cường độ tương phản (Log, Global HE, CLAHE) và Lọc khử nhiễu đốm SAR (Lee MMSE, Bilateral, Kuan, Frost, Homomorphic, Median, Gaussian, Box).
2. **Chuyên đề Đề 5**: Cài đặt các kỹ thuật làm nét (Unsharp Masking, Laplacian) và toán tử đạo hàm biên (Roberts, Prewitt, Sobel, LoG, Canny 4 bước).
3. **Ứng dụng thực tiễn Đề 18 NASA**: Phát hiện và bộc lộ ranh giới vết dầu loang trên ảnh SAR vi ba Sentinel-1 bằng phương pháp **Ranh giới Hình thái học $\beta(A) = A \setminus (A \ominus B)$** kết hợp phân ngưỡng tối ưu Otsu.
4. **Cam kết học thuật bắt buộc**:
   - **100% Pure NumPy**: Không sử dụng hàm xử lý ảnh có sẵn của OpenCV trong module lõi (`cv2` chỉ dùng để đọc/ghi ảnh).
   - **Tuyệt đối KHÔNG sử dụng Machine Learning hay Deep Learning** (No YOLO, No CNN, No SVM).
   - Kiểm chứng tính đúng giải tích bằng **5 bài toán số tính tay $8 \times 8$ sai số = 0** và đối chuẩn với OpenCV.
   - Xây dựng ứng dụng **Web Studio tương tác thời gian thực** (FastAPI + TailwindCSS) phục vụ bảo vệ đồ án trực quan.
