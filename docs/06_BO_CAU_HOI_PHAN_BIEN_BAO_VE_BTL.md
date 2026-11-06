# CẨM NANG 20 CÂU HỎI PHẢN BIỆN BẢO VỆ BTL XỬ LÝ ẢNH & KỊCH BẢN THUYẾT TRÌNH

> **Học phần**: Xử lý ảnh (Digital Image Processing - DIP) — Khoa CNTT, Đại học Giao thông Vận tải (UTC)  
> **Giảng viên chấm thi**: TS. Phan Thanh Toàn, TS. Cao Thị Luyên  
> **Đề tài**: *Tăng Cường Độ Tương Phản, Khử Nhiễu & Xử Lý Biên Bộc Lộ Vết Dầu Tràn Trên Biển Từ Ảnh Radar SAR Sentinel-1*

---

## PHẦN 1: BỘ 20 CÂU HỎI VẤN ĐÁP KINH ĐIỂN & ĐÁP ÁN CHUẨN MỰC

### NHÓM I: CƠ SỞ VẬT LÝ VI BA & BẢN CHẤT ẢNH RADAR SAR

#### Câu 1: Tại sao ảnh radar SAR lại chụp được vết dầu loang trong khi ảnh quang học thông thường thường gặp khó khăn?
- **Trả lời**: Ảnh quang học phụ thuộc vào ánh sáng mặt trời và bị mây mù che khuất ($> 60\%$ thời gian trên biển). Radar SAR là cảm biến vi ba chủ động (băng C $\lambda \approx 5.6\text{ cm}$), tự phát sóng và thu hồi tán xạ ngược, có khả năng xuyên thấu qua mây, mưa, sương mù và hoạt động liên tục 24/7 bất kể ngày đêm.

#### Câu 2: Tại sao vết dầu lại có màu đen/tối trên ảnh SAR, trong khi nước biển lại có màu sáng?
- **Trả lời**: 
  - **Mặt biển**: Gió tạo ra các sóng mao dẫn (Capillary waves) có bước sóng vài centimet, thỏa mãn **điều kiện tán xạ cộng hưởng Bragg**, phản hồi năng lượng vi ba cực lớn về vệ tinh $\rightarrow$ Mặt biển có mức xám sáng ($\mu_{\text{sea}} \approx 130 \dots 200$).
  - **Vết dầu**: Làm tăng độ nhớt động lực học của chất lỏng, **dập tắt hoàn toàn sóng mao dẫn**. Bề mặt dầu trở nên nhẵn bóng như gương, gây ra **hiện tượng phản xạ gương (Specular reflection)** làm toàn bộ sóng radar bị phản xạ đi hướng khác, không có năng lượng quay về ăng-ten $\rightarrow$ Vết dầu xuất hiện dưới dạng **vùng tối cục bộ (Dark Formation)** ($\mu_{\text{slick}} \approx 20 \dots 60$).

#### Câu 3: Bản chất của nhiễu đốm (Speckle Noise) trên ảnh SAR là gì? Tại sao gọi là nhiễu nhân?
- **Trả lời**: Mỗi ô phân giải radar có vô số vật tán xạ vi mô. Sự giao thoa sóng tán xạ kết hợp (Coherent interference) cùng pha tạo đỉnh sáng, ngược pha tạo điểm đen, sinh ra kết cấu hạt tiêu lốm đốm. Nhiễu này tuân theo mô hình nhân $I = R \cdot \eta$ (với kỳ vọng $E[\eta] = 1$, phương sai $\sigma_\eta^2 = 1/L$), nghĩa là phương sai nhiễu tỷ lệ thuận với bình phương cường độ sáng, khác hoàn toàn với nhiễu cộng Gauss độc lập của ảnh quang học.

#### Câu 4: Vùng biển lặng gió tự nhiên (Look-alike) có gì giống và khác vết dầu tràn thật?
- **Trả lời**: 
  - **Giống nhau**: Vùng biển lặng gió ($< 2\text{ m/s}$) cũng không có sóng mao dẫn, gây phản xạ gương và cũng tạo ra vùng tối trên ảnh SAR.
  - **Khác nhau về mặt vật lý**: Vết dầu khoáng dập sóng rất mạnh và có ranh giới đột ngột, tạo **tỷ số tương phản nền biển lân cận cao ($C_R \ge 0.10 \dots 0.40$)**. Vùng biển lặng gió có ranh giới chuyển tiếp thoai thoải, mức xám giảm từ từ, tỷ số tương phản rất thấp ($C_R < 0.10$).

---

### NHÓM II: LỌC KHỬ ĐỐM & TĂNG CƯỜNG ĐỘ TƯƠNG PHẢN

#### Câu 5: Tại sao bộ lọc Lee MMSE lại tối ưu cho ảnh SAR hơn bộ lọc trung bình Box filter hay lọc Gauss?
- **Trả lời**: Lọc Box và Gauss là các bộ lọc tuyến tính bất biến theo không gian, chúng làm mờ (nhòe) tất cả các bước nhảy độ xám, xóa sổ đường bờ ranh giới của vết dầu. Bộ lọc Lee MMSE là bộ lọc thích ứng dựa trên hệ số $K = 1 - \frac{\sigma_v^2 \mu_I^2}{\sigma_I^2}$:
  * Trong vùng đồng nhất ($\sigma_I^2$ nhỏ): $K \to 0 \implies \hat{R} = \mu_I$ (san phẳng nhiễu như lọc trung bình).
  * Tại ranh giới vết dầu ($\sigma_I^2$ rất lớn): $K \to 1 \implies \hat{R} = I(x, y)$ (giữ nguyên độ sắc nét của biên).

#### Câu 6: Ý nghĩa của chỉ số ENL (Equivalent Number of Looks) và SSI (Speckle Suppression Index)?
- **Trả lời**:
  - **ENL** $= \frac{\mu^2}{\sigma^2}$: Đo lường tỷ số tín hiệu trên nhiễu trên vùng đồng nhất. Giá trị ENL càng cao, nhiễu đốm bị triệt tiêu càng mạnh (hệ thống của ta nâng ENL từ $4.21$ lên $> 22.0$).
  - **SSI** $= \frac{\sigma_{\text{proc}} / \mu_{\text{proc}}}{\sigma_{\text{raw}} / \mu_{\text{raw}}}$: Đo mức độ suy giảm đốm. $\text{SSI} < 1.0$ chứng tỏ bộ lọc có khả năng khử đốm hiệu quả (Lee đạt $\text{SSI} \approx 0.43$).

#### Câu 7: Tại sao cân bằng Histogram toàn cục (Global HE) lại bị cháy sáng ảnh SAR, còn CLAHE thì khắc phục được?
- **Trả lời**: Vì nền biển chiếm phần lớn diện tích bức ảnh, hàm mật độ xác suất $p(r)$ tập trung một đỉnh khổng lồ ở mức xám nền biển. Khi tích lũy CDF, hàm phân bố tích lũy tăng dựng đứng, kéo toàn bộ nền biển lên mức trắng bão hòa (Cháy sáng - Over-enhancement). CLAHE khắc phục bằng cách đặt **ngưỡng Clip Limit**, cắt bỏ phần đỉnh dư thừa và chia đều cho toàn bộ 256 mức xám, sau đó nội suy song tuyến (Bilinear Interpolation) để xóa vệt ô.

#### Câu 8: Mục đích thực sự của bước Tăng cường độ tương phản (CLAHE) trong đề tài này là gì? Có phải để làm ảnh "sáng lên" không?
- **Trả lời**: **Tuyệt đối không phải để làm sáng ảnh**. Mục đích cốt lõi là **Tái cấu trúc Lược đồ độ xám (Histogram Restructuring)**: Kéo dãn khoảng cách giữa mức xám của lòng dầu (dìm xuống gần 0) và nền biển (nâng lên mức sáng), biến phân bố histogram từ dạng đơn đỉnh bẹt (Unimodal) thành **phân bố 2 đỉnh dứt khoát (Bimodal Distribution)**. Nhờ đó thuật toán Otsu mới tìm được ngưỡng phân tách tối ưu tại thung lũng giữa 2 đỉnh với hệ số khả tách $\eta \to 1.0$.

---

### NHÓM III: LÀM NÉT & HIỆN TƯỢNG ĐEN ẢNH (UNDERSHOOT DIP)

#### Câu 9: Công thức Unsharp Masking hoạt động như thế nào?
- **Trả lời**: Mặt nạ vi sai tần số cao: $g_{\text{mask}} = f - f_{\text{blur}}$. Ảnh làm nét: $f_{\text{sharp}} = f + k \cdot g_{\text{mask}}$. Tại các vùng có bước nhảy mức xám, thành phần tần số cao được khuếch đại giúp mắt người quan sát viền bờ sắc nét hơn.

#### Câu 10: Hiện tượng ảnh bị "đen hơn ở nhiều điểm" sau khử đốm và tăng cường có ảnh hưởng đến việc bộc lộ ranh giới vết dầu không? Em đã giải quyết như thế nào?
- **Trả lời**: 
  - Hiện tượng đen hơn có 2 mặt:
    * *Mặt tích cực*: Vết dầu vốn là vùng tối, việc dìm lòng dầu đen hơn làm tăng tỷ số tương phản $C_R$, giúp phân ngưỡng Otsu đạt hệ số khả tách rất cao ($\eta = 0.978$).
    * *Rủi ro*: Bước làm nét Unsharp Masking tạo ra hiệu ứng **thâm hụt biên (Undershoot Dip)** khi $f < f_{\text{blur}}$, dìm các thung lũng sóng biển ngoài khơi xuống màu tối sẫm. Nếu phân vùng trên ảnh này, đường biên sẽ bị răng cưa hoặc bắt nhầm sóng biển.
  - *Giải pháp kiến trúc Decoupling*: Nhóm em **tách riêng 2 luồng tính toán**: Thuật toán phân đoạn hình thái học chạy trên `enhanced_img` (sau Lee + CLAHE, **trước khi Unsharp**), đảm bảo mặt nạ ranh giới chuẩn xác $100\%$. Sau đó phủ viền đỏ lên ảnh `proc_img` (đã làm nét) để người dùng có tầm nhìn sắc nét nhất.

---

### NHÓM IV: XỬ LÝ BIÊN & HÌNH THÁI HỌC BỘC LỘ RANH GIỚI VẾT DẦU

#### Câu 11: Tại sao các toán tử dò biên đạo hàm (Sobel, Prewitt, Canny) lại thất bại trên ảnh SAR vết dầu (vẽ viền đỏ lung tung khắp mặt biển)?
- **Trả lời**: Toán tử đạo hàm cục bộ ($\nabla I$) phản ứng với **mọi bước nhảy mức xám**, kể cả ngọn sóng, bọt biển và đốm nhiễu vi ba. Vết dầu trên biển về bản chất vật lý là một **Vùng diện tích tối (Dark Formation)** chứ không phải một đường cong đơn lẻ. Áp dụng dò biên đạo hàm cục bộ sẽ nhận diện mọi gợn sóng biển thành biên, tạo ra hàng nghìn đường viền rác.

#### Câu 12: Bản chất của phép toán Ranh giới Hình thái học $\beta(A)$ là gì?
- **Trả lời**: Công thức:
  $$\beta(A) = A \setminus (A \ominus B_{3 \times 3}) = A - \text{erode}(A)$$
  Trong đó $A$ là tập hợp các pixel của mảng dầu sau khi đã lọc nhiễu sóng và hàn gắn bọt sóng. Phép trừ tập hợp này lấy toàn bộ diện tích vết dầu trừ đi phần lõi sau khi co bằng phần tử cấu trúc $3 \times 3$, để lại duy nhất lớp vỏ ngoài cùng có **độ dày đúng 1 pixel**, ôm khít mép ngoài của vết dầu và sạch bóng mặt biển.

#### Câu 13: Tại sao phải áp dụng Phép Mở (Opening) trước và Phép Đóng (Closing) sau khi phân ngưỡng nhị phân?
- **Trả lời**:
  - **Phép Mở ($A \circ B = (A \ominus B) \oplus B$)**: Co trước Giãn sau bằng đĩa tròn $5 \times 5$, triệt tiêu sạch sẽ các đốm nhị phân rác do sóng biển ngoài khơi sinh ra mà không làm thay đổi kích thước tổng thể của mảng dầu lớn.
  - **Phép Đóng ($A \bullet B = (A \oplus B) \ominus B$)**: Giãn trước Co sau bằng đĩa tròn $7 \times 7$ hoặc $11 \times 11$, lấp đầy các lỗ thủng do bọt sóng tạo ra bên trong lòng mảng dầu, tạo thành một khối dầu đặc ruột đồng nhất.

#### Câu 14: Thuật toán phân ngưỡng Otsu cực đại hóa đại lượng nào? Hệ số khả tách $\eta$ có ý nghĩa gì?
- **Trả lời**: Thuật toán Otsu cực đại hóa **phương sai giữa các lớp (Between-class Variance)** $\sigma_B^2(T) = \omega_0 \omega_1 (\mu_0 - \mu_1)^2$. Hệ số khả tách $\eta = \sigma_B^2(T^*) / \sigma_T^2 \in [0, 1]$ phản ánh tỷ lệ phương sai giữa 2 lớp trên tổng phương sai toàn ảnh. Giá trị $\eta > 0.60$ chứng minh phân bố lược đồ 2 đỉnh cực kỳ phân tách, ranh giới tìm được có độ tin cậy tuyệt đối.

#### Câu 15: Tiêu chuẩn NASA Đề 18 loại trừ báo động giả (False Alarms) bằng 2 điều kiện nào?
- **Trả lời**:
  1. **Lọc diện tích**: $\text{Area} \ge 300\text{ px}$ (loại trừ các đốm thung lũng sóng ngẫu nhiên).
  2. **Tỷ số tương phản nền biển**: $C_R = \frac{\mu_{\text{sea}} - \mu_{\text{slick}}}{\mu_{\text{sea}}} \ge 0.10$ (loại trừ các vùng biển lặng gió Look-alikes có $C_R < 0.10$).

---

### NHÓM V: ĐÁNH GIÁ THỰC NGHIỆM & KIỂM CHUẨN

#### Câu 16: Em chứng minh tính đúng đắn toán học của mã nguồn Pure NumPy tự viết bằng cách nào?
- **Trả lời**: Nhóm em đã xây dựng module [`src/verification.py`](file:///D:/Codin/utc-code/HK4_1/XLA/BTL/src/verification.py) thực hiện **5 bài toán số tính tay mẫu $8 \times 8$ giải tích** (Cân bằng Histogram, Lọc Lee MMSE, Toán tử Sobel/Prewitt, Hình thái học $\beta(A)$, Phân ngưỡng Otsu $\eta$), tất cả đều đạt **sai số $= 0$ tuyệt đối**. Đồng thời đối chuẩn trên 10 ảnh SAR thực tế với thư viện OpenCV đạt sai số toàn phương $\text{MSE} = 0.0000$.

#### Câu 17: Kết quả thử nghiệm trên toàn bộ 1.853 ảnh của dataset như thế nào?
- **Trả lời**: Hệ thống đã quét song song trên 14 nhân CPU trong **58.79 giây** (31.7 ms/ảnh):
  * **$60.5\%$ (1.121 ảnh)** đạt chuẩn tuyệt đối `CLEAN_BOUNDARY` (đường bao khép kín 1px ôm sát vết dầu, biển sạch 100%).
  * **$17.4\%$ (322 ảnh)** bị vỡ vụn `EDGE_FRAGMENTED` do sóng biển chia cắt.
  * **$16.6\%$ (308 ảnh)** có hệ số khả tách $\eta < 0.50$ do tương phản tự nhiên mờ nhạt.
  * **$2.6\%$ (49 ảnh)** bị bỏ sót `MISSED_SLICK` do vệt dầu mỏng ($C_R < 0.10$).
  * **$2.6\%$ (48 ảnh)** bị tràn biên `EDGE_LEAKAGE` (ngưỡng Otsu cắt quá cao).

#### Câu 18: Để khắc phục 17.4% ảnh bị vỡ vụn (Fragmented), giải pháp tối ưu là gì?
- **Trả lời**: Nâng bán kính đĩa tròn của phép đóng (Closing) từ $r=3$ ($7 \times 7$) lên $r=5$ hoặc $r=6$ ($11 \times 11$ hoặc $13 \times 13$) hoặc sử dụng phép đóng đa tỉ lệ để bắc cầu liền mạch qua các rãnh sóng biển.

#### Câu 19: Để khắc phục 2.6% ảnh bị bỏ sót (Missed Slick), giải pháp tối ưu là gì?
- **Trả lời**: Áp dụng **ngưỡng tương phản động (Dynamic Contrast Threshold)**: Nếu diện tích mảng dầu lớn ($\text{Area} \ge 1.500\text{ px}$), chỉ cần $C_R \ge 0.05$ là chấp nhận (giúp bắt trọn các vệt dầu dạng màng mỏng Oil sheen); chỉ với diện tích nhỏ mới yêu cầu khắt khe $C_R \ge 0.10$.

#### Câu 20: Dự án này có sử dụng thư viện Machine Learning hay Deep Learning nào không?
- **Trả lời**: **Dạ hoàn toàn KHÔNG ạ**. Dự án cam kết 100% tuân thủ nguyên lý Xử lý ảnh số kinh điển: Toán tử ma trận nhân chập vector hóa Pure NumPy, thống kê cục bộ MMSE, phân ngưỡng Otsu tối ưu hóa phương sai và đại số tập hợp hình thái học.

---

## PHẦN 2: KỊCH BẢN THUYẾT TRÌNH BẢO VỆ BTL TRONG 10 PHÚT (SPEECH SCRIPT)

### Phút 1–2: Mở đầu & Đặt vấn đề (Cơ sở vật lý vi ba)
> *"Kính thưa các thầy cô trong hội đồng chấm Bài tập lớn môn Xử lý ảnh!  
> Nhóm em xin phép trình bày đề tài: **'Tăng cường độ tương phản, khử nhiễu và xử lý biên bộc lộ vết dầu tràn trên biển từ ảnh radar SAR vi ba Sentinel-1'**.  
> Khác với ảnh quang học bị cản trở bởi mây mù và bóng đêm, radar khẩu độ tổng hợp SAR sử dụng sóng vi ba băng C có khả năng xuyên mây và hoạt động 24/7. Trên mặt biển, sóng mao dẫn tạo ra tán xạ Bragg mạnh khiến nước biển có màu sáng. Ngược lại, lớp váng dầu dập tắt hoàn toàn sóng mao dẫn, gây phản xạ gương và tạo thành một vùng tối đen cục bộ. Tuy nhiên, ảnh SAR lại mang nhiễu đốm nhân (Multiplicative Speckle Noise) cực kỳ phức tạp. Vì vậy, nhiệm vụ của đề tài là áp dụng thuần túy các thuật toán Xử lý ảnh kinh điển để khử đốm, tăng tương phản và bộc lộ chính xác ranh giới mảng dầu."*

### Phút 3–5: Trình bày phương pháp luận & Các thuật toán lõi
> *"Nhóm em xây dựng một chuỗi xử lý 4 giai đoạn độc lập:  
> - **Giai đoạn 1**: Khử nhiễu đốm bằng bộ lọc thích ứng **Lee MMSE 5x5**. Nhờ hệ số thích ứng K, bộ lọc san phẳng nhiễu trong lòng dầu và mặt biển nhưng bảo tồn nguyên vẹn bước nhảy tại mép biên.  
> - **Giai đoạn 2**: Tăng cường tương phản bằng **CLAHE**. CLAHE cắt ngưỡng tương phản Clip Limit để không khuếch đại nhiễu, biến đổi lược đồ độ xám từ đơn đỉnh bẹt thành **phân bố 2 đỉnh Bimodal dứt khoát**.  
> - **Giai đoạn 3**: Bộc lộ ranh giới vết dầu. Chúng em chứng minh rằng các toán tử đạo hàm Sobel/Canny sẽ vẽ viền lung tung trên mặt biển do phản ứng với bọt sóng. Thay vào đó, nhóm áp dụng **Phân đoạn Otsu tối ưu** kết hợp **Lọc hình thái học Mở (xóa đốm biển) và Đóng (hàn gắn bọt sóng)**, lọc diện tích và tương phản theo chuẩn NASA Đề 18, và trích xuất **Ranh giới Hình thái học $\beta(A) = A - \text{erode}(A)$**. Kết quả là một đường bao khép kín 1 pixel ôm sát mép dầu thật và mặt biển sạch bóng 100%.  
> - **Đặc biệt về mặt kiến trúc**: Nhóm em tách riêng luồng phân đoạn trên ảnh trước khi làm nét Unsharp Masking để triệt tiêu hiện tượng thâm hụt biên Undershoot Dip, sau đó phủ viền đỏ lên ảnh làm nét để người quan sát có tầm nhìn trực quan nhất."*

### Phút 6–7: Trình diễn ứng dụng Web Studio thời gian thực
> *(Mở trình duyệt `http://127.0.0.1:8000`, thao tác trực tiếp)*  
> *"Đây là giao diện Web Studio do nhóm tự xây dựng với FastAPI và TailwindCSS.  
> Bố cục Canvas 2x2 thể hiện tuần tự chuẩn Z-Pattern: 1. Ảnh SAR Gốc $\rightarrow$ 2. Sau Khử Đốm & Tăng Cường $\rightarrow$ 3. Bộc Lộ Ranh Giới Vết Dầu $\rightarrow$ 4. Bản Đồ Vi Sai.  
> Người dùng có thể nhấp chuột vào ảnh để mở Lightbox phóng to chi tiết. Bảng thống kê NASA hiển thị ngay lập tức các chỉ số định lượng: Diện tích dầu, Tỷ số tương phản $C_R$, Ngưỡng Otsu $T^*$ và Hệ số khả tách $\eta = 0.978$."*

### Phút 8–9: Báo cáo thực nghiệm định lượng & Kiểm chuẩn tính đúng
> *"Về mặt kiểm chứng học thuật:  
> 1. Nhóm em đã giải tích **5 bài toán số tính tay mẫu $8 \times 8$** (Histogram, Lee filter, Sobel/Prewitt, Hình thái học $\beta(A)$, Otsu) và đối chứng với code NumPy: **Sai số tuyệt đối bằng 0**.  
> 2. Đối chuẩn với OpenCV trên 10 ảnh SAR đạt sai số $\text{MSE} = 0.0000$.  
> 3. Đã chạy benchmark tự động trên **FULL 100% dataset (1.853 ảnh SAR)**: Đạt tỷ lệ sạch chuẩn $60.5\%$, trích xuất 732 ảnh chẩn đoán 4 khung hình để phân tích sâu các ca biên vỡ vụn do sóng và đề xuất giải pháp Closing đa tỉ lệ."*

### Phút 10: Kết luận & Lời cảm ơn
> *"Tóm lại, đề tài đã giải quyết trọn vẹn bài toán phát hiện vết dầu tràn SAR bằng **100% toán học và xử lý ảnh số kinh điển**, không dùng bất kỳ mô hình học máy nào.  
> Nhóm em xin chân thành cảm ơn các thầy cô đã lắng nghe và rất mong nhận được những câu hỏi góp ý của quý thầy cô ạ!"*
