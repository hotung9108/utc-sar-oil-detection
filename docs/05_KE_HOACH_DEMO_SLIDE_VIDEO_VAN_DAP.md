# KẾ HOẠCH BẢO VỆ: DEMO APP, SLIDE, VIDEO & BỘ CÂU HỎI VẤN ĐÁP
## BÀI TẬP LỚN XỬ LÝ ẢNH — ĐẠI HỌC GIAO THÔNG VẬN TẢI (UTC)
**Đề tài 18:** Phát hiện vết dầu tràn trên biển từ ảnh SAR (★★★) — NASA #6  
**Chủ trì chuẩn bị:** TV1 — Project Manager  
**Thời lượng bảo vệ chính thức:** 20 phút (12 phút thuyết trình + 3 phút demo app + 5 phút vấn đáp)

---

## 1. THIẾT KẾ ỨNG DỤNG DEMO TƯƠNG TÁC (STREAMLIT WEB APP)

> [!IMPORTANT]
> Ứng dụng Demo có giao diện là sản phẩm kỹ thuật trọng tâm của **TV1 (PM)**. Ứng dụng này sẽ được mở trực tiếp trên máy tính để demo trong 3 phút trước Giảng viên và Hội đồng.

### 1.1. Bố cục giao diện người dùng (UI Layout)
Ứng dụng được xây dựng bằng **Streamlit** (`app.py`), chia làm 2 khu vực trực quan:

```
+-----------------------------------------------------------------------------------------+
|                  HỆ THỐNG PHÁT HIỆN VẾT DẦU TRÀN TỪ ẢNH SAR SENTINEL-1                  |
|                   Bộ môn Xử lý ảnh - Đại học Giao thông Vận tải (UTC)                   |
+-----------------------------------+-----------------------------------------------------+
| [SIDEBAR ĐIỀU KHIỂN]              | [KHUNG TRỰC QUAN HÓA 4 BƯỚC THUẬT TOÁN]             |
| 1. Chọn nguồn ảnh:                |                                                     |
|    ( ) Tải ảnh lên (.png/.jpg)    | [Ảnh 1: Gốc SAR]        [Ảnh 2: Sau lọc Trung vị]   |
|    (o) Chọn từ tập mẫu:           | 400x400 Grayscale       Khử nhiễu đốm speckle       |
|        - Class 1 (Có dầu #01)     +-------------------------+---------------------------+
|        - Class 0 (Gió lặng #02)   | [Ảnh 3: Mặt nạ Otsu]    [Ảnh 4: Viền ĐỎ Vết dầu]   |
|                                   | Ngưỡng tối ưu & Morph   Viền đỏ ôm sát đốm dầu      |
| 2. Thanh trượt tham số:           +-----------------------------------------------------+
|    - Kernel lọc: [ 5 ] px         | [BẢNG KẾT QUẢ ĐO ĐẠC & KẾT LUẬN THỜI GIAN THỰC]     |
|    - Diện tích tối thiểu: [ 150 ] | - Trạng thái: PHÁT HIỆN 02 VẾT DẦU TRÀN NGUY HIỂM!  |
|    - Độ tương phản min: [ 12.0 ]  | - Vết #1: Diện tích = 3,420 px | Gradient biên = 9.8|
|    - Gradient biên min: [ 6.0 ]   | - Vết #2: Diện tích = 1,180 px | Tương phản = 16.4  |
|    - Khả tách Otsu min: [ 0.10 ]  | - Thời gian xử lý: 42 ms (Thuần NumPy)              |
+-----------------------------------+-----------------------------------------------------+
```

### 1.2. Kịch bản thao tác Demo (3 phút sống động trước Giảng viên)
1. **Phút 0:00 - 0:45**: Chọn ảnh mẫu `Class_1` (có dầu tràn thực tế).
   - Nhấn chạy: Hệ thống lập tức hiển thị 4 bước.
   - Chỉ vào Ảnh 4: Đường viền **MÀU ĐỎ** ôm khít thân vết dầu theo đúng công thức trích biên hình thái $\beta(A) = A - (A \ominus B)$.
   - Bảng thông số bên dưới hiển thị diện tích, độ tương phản và độ lớn gradient.
2. **Phút 0:45 - 1:45**: Thao tác điều khiển thanh trượt (Interactive Sliders).
   - Kéo thanh trượt `Kernel lọc` từ 3 lên 5 để thấy nhiễu đốm đục hạt biến mất.
   - Kéo thanh `Độ tương phản tối thiểu` để chứng minh cơ chế phân loại linh hoạt.
3. **Phút 1:45 - 2:45**: Chọn ảnh mẫu `Class_0` (Vùng gió lặng tự nhiên / Look-alike).
   - Hệ thống hiển thị ảnh: Không có viền đỏ nào xuất hiện!
   - Giải thích: Vùng gió lặng tuy tối màu nhưng bị chặn bởi tiêu chí độ dốc Gradient biên và hệ số tương phản vành đai $\rightarrow$ **Không báo động giả**.
4. **Phút 2:45 - 3:00**: Kết luận thời gian thực thi (chỉ mất ~40-60 ms cho 1 ảnh) và chuyển sang phần vấn đáp.

---

## 2. KHUNG CẤU TRÚC 18 SLIDE THUYẾT TRÌNH BẢO VỆ (12 PHÚT)

Phân bổ thời gian nghiêm ngặt 12 phút giữa 5 thành viên (trung bình 2 - 2.5 phút/người):

| Slide | Nội dung chính | Người trình bày | Thời gian |
| :---: | :--- | :---: | :---: |
| **Slide 1** | Tiêu đề đề tài 18, Giảng viên TS. Phan Thanh Toàn, Danh sách 5 thành viên & vai trò. | **TV1** (PM) | 0.5 phút |
| **Slide 2** | Vấn đề dầu vón cục ô nhiễm bờ biển miền Trung & Ý nghĩa ảnh radar SAR Sentinel-1. | **TV1** (PM) | 1.0 phút |
| **Slide 3** | Mục tiêu, chuẩn đầu ra CDIO và nguyên tắc tự cài đặt 100% mã nguồn bằng NumPy. | **TV1** (PM) | 0.5 phút |
| **Slide 4** | Bản chất vật lý ảnh SAR: Hiện tượng dập tắt sóng mao dẫn & Thách thức Look-alikes. | **TV2** (Lý thuyết) | 1.0 phút |
| **Slide 5** | Mô hình toán học: Lọc trung vị, phân ngưỡng Otsu tối ưu và hệ số khả tách $\eta$. | **TV2** (Lý thuyết) | 1.0 phút |
| **Slide 6** | Minh họa ví dụ số tính tay (Toy Example ma trận $5 \times 5$). | **TV2** (Lý thuyết) | 0.5 phút |
| **Slide 7** | Sơ đồ khối kiến trúc Pipeline 4 bước tuần tự của hệ thống. | **TV3** (Thuật toán 1) | 0.5 phút |
| **Slide 8** | Cài đặt Tiền xử lý: Lọc trung vị bảo toàn biên khử nhiễu speckle bằng NumPy. | **TV3** (Thuật toán 1) | 1.0 phút |
| **Slide 9** | Cài đặt Phân ngưỡng Otsu tối ưu & tính $\eta$ phân lập đốm tối bằng NumPy. | **TV3** (Thuật toán 1) | 0.5 phút |
| **Slide 10** | Cài đặt Toán tử hình thái học: Co, dãn, mở, đóng và trích biên $\beta(A)$ bằng NumPy. | **TV4** (Thuật toán 2) | 1.0 phút |
| **Slide 11** | Trích xuất 4 đặc trưng phân biệt: Thuôn dài, phức tạp biên, gradient Sobel, tương phản. | **TV4** (Thuật toán 2) | 1.0 phút |
| **Slide 12** | Tổng quan tập dữ liệu CSIRO Sentinel-1 (3,725 ảnh Class 0 + 1,905 ảnh Class 1). | **TV5** (Thực nghiệm) | 0.5 phút |
| **Slide 13** | Bảng số liệu thực nghiệm: Precision, Recall, F1-Score & Ma trận nhầm lẫn (Confusion Matrix). | **TV5** (Thực nghiệm) | 1.0 phút |
| **Slide 14** | Phân tích định tính: Minh họa ca phát hiện xuất sắc & Phân tích nguyên nhân ca dự đoán sai. | **TV5** (Thực nghiệm) | 1.0 phút |
| **Slide 15** | Bảng kiểm chứng tính đúng giữa thuật toán NumPy tự viết vs Thư viện OpenCV chuẩn. | **TV2** (Kiểm chứng) | 0.5 phút |
| **Slide 16** | Giới thiệu Kiến trúc Ứng dụng Giao diện Web tương tác Streamlit. | **TV1** (PM) | 0.5 phút |
| **Slide 17** | Kết luận mức độ hoàn thành & Hướng mở rộng: Mô phỏng trôi dầu Lagrangian + Tích hợp AIS. | **TV1** (PM) | 0.5 phút |
| **Slide 18** | Lời cảm ơn Thầy và Hội đồng — Sẵn sàng chuyển sang phần Demo và Vấn đáp! | **TV1** (PM) | 0.5 phút |

---

## 3. KỊCH BẢN QUAY VIDEO DEMO (5 – 7 PHÚT)

Video này là một trong các sản phẩm nộp bắt buộc. Độ dài tối ưu là **6 phút**, quay màn hình chất lượng Full HD kèm giọng đọc thuyết minh rõ ràng:

- **Phân cảnh 1 (0:00 - 0:45) — Giới thiệu tổng quan:**
  - Hình ảnh: Slide bìa đề tài và clip ngắn/hình ảnh dầu vón cục tràn vào bãi biển Đà Nẵng, Quảng Trị.
  - Lời thoại: Giới thiệu tên nhóm, đề tài số 18, mục tiêu xây dựng giải pháp cảnh báo sớm dầu tràn ngoài khơi bằng ảnh vệ tinh Sentinel-1 SAR.
- **Phân cảnh 2 (0:45 - 2:00) — Kiến trúc thuật toán & Code NumPy:**
  - Hình ảnh: Sơ đồ Pipeline 4 bước và quay lướt các đoạn code tự viết bằng NumPy trong VS Code (`step1_filter`, `step2_segmentation`, `step3_morphology`, `step4_edge_gradient`).
  - Lời thoại: Nhấn mạnh 100% thuật toán lõi được tự cài đặt bằng NumPy thuần theo bài giảng của TS. Phan Thanh Toàn, không sử dụng hàm đen thư viện.
- **Phân cảnh 3 (2:00 - 4:30) — Demo tương tác trên Streamlit App:**
  - Hình ảnh: Quay toàn màn hình ứng dụng Streamlit.
  - Thao tác:
    1. Chọn ảnh có vết dầu lớn $\rightarrow$ thấy 4 bước phân tích trực quan $\rightarrow$ viền đỏ ôm khít.
    2. Chỉnh slider kích thước kernel và ngưỡng gradient để thấy thuật toán phản ứng linh hoạt.
    3. Chọn ảnh Class 0 (vùng gió lặng) $\rightarrow$ hệ thống thông minh loại bỏ, không báo động giả.
- **Phân cảnh 4 (4:30 - 5:30) — Kết quả thực nghiệm định lượng:**
  - Hình ảnh: Bảng số liệu Precision, Recall, F1 và ma trận nhầm lẫn Confusion Matrix trên 5,630 ảnh.
  - Lời thoại: Tóm tắt hiệu năng, độ chính xác và tốc độ xử lý real-time (~45ms/ảnh).
- **Phân cảnh 5 (5:30 - 6:00) — Kết luận & Hướng phát triển:**
  - Hình ảnh: Bản đồ mô phỏng trôi dầu dạt vào bờ biển miền Trung và dữ liệu tàu biển AIS.
  - Lời thoại: Tổng kết bài học CDIO và cảm ơn người xem.

---

## 4. NGÂN HÀNG 15 CÂU HỎI VẤN ĐÁP CỦA GIẢNG VIÊN & GỢI Ý TRẢ LỜI MẪU

> [!CAUTION]
> Giảng viên (TS. Phan Thanh Toàn) sẽ **chỉ định bất kỳ thành viên nào** trả lời câu hỏi, kể cả câu hỏi về phần bạn khác làm. Cả 5 thành viên phải học thuộc lòng các câu trả lời dưới đây!

### 🔹 Nhóm câu hỏi về Bản chất Vật lý SAR & Dữ liệu (Dành cho TV1, TV2, TV5)
1. **Câu 1: Tại sao vết dầu trên ảnh radar SAR lại có màu tối hơn nền nước biển xung quanh?**
   - *Gợi ý trả lời:* Dầu làm giảm sức căng bề mặt của nước biển, triệt tiêu các sóng mao dẫn (capillary waves). Bề mặt nước có dầu trở nên nhẵn phẳng như gương, khiến sóng radar từ vệ tinh chiếu xuống bị phản xạ gương ra xa (specular reflection), không tán xạ ngược trở lại máy thu (backscatter rất thấp) $\rightarrow$ thể hiện bằng các điểm ảnh màu tối trên ảnh xám.
2. **Câu 2: Vùng gió lặng (Low wind area) và Màng sinh học (Biogenic slick) khác gì với Vết dầu tràn thực tế (Oil slick)?**
   - *Gợi ý trả lời:* Cả hai đều tạo đốm tối trên ảnh SAR (gọi là Look-alikes). Tuy nhiên:
     - Vùng gió lặng: Thường có diện tích rất rộng, ranh giới mờ nhạt thoai thoải (gradient biên thấp), độ thuôn dài thấp ($Elongation \approx 1-2$).
     - Vết dầu thực tế: Có sức căng bề mặt mạnh tạo đường biên sắc nét với nước biển xung quanh (gradient biên Sobel cao), độ tương phản vành đai cao, và nếu do tàu xả thải thì thường có dạng vệt kéo dài ($Elongation \ge 3$).

### 🔹 Nhóm câu hỏi về Tiền xử lý & Phân ngưỡng Otsu (Dành cho TV2, TV3)
3. **Câu 3: Tại sao lại chọn Lọc trung vị (Median Filter) để khử nhiễu ảnh SAR thay vì Lọc trung bình (Mean Filter) hay Lọc Gaussian?**
   - *Gợi ý trả lời:* Nhiễu trên ảnh SAR là nhiễu đốm nhân tính (Speckle noise) có biên độ xung cục bộ cao tương tự nhiễu muối tiêu. Lọc trung bình hay Gaussian sẽ làm mờ nhòe (blur) đường biên ranh giới của vết dầu, làm mất thông tin sắc nét của mép dầu. Lọc trung vị là bộ lọc phi tuyến xuất sắc nhất có khả năng triệt tiêu các đốm nhiễu dị biệt mà vẫn **bảo toàn hoàn hảo độ sắc nét của đường biên**.
4. **Câu 4: Trình bày ý nghĩa toán học của Hệ số khả tách $\eta = \sigma_B^2 / \sigma_T^2$ trong thuật toán Otsu (Slide Chương 7 trang 52)?**
   - *Gợi ý trả lời:* $\sigma_B^2$ là phương sai giữa 2 lớp (inter-class variance), $\sigma_T^2$ là tổng phương sai của toàn bộ ảnh. Hệ số $\eta$ đo lường mức độ tách biệt giữa đối tượng và nền, luôn nằm trong đoạn $[0, 1]$. Nếu $\eta$ quá nhỏ ($< 0.10$), chứng tỏ ảnh có phân bố xám đồng nhất, không có 2 đỉnh rõ rệt $\rightarrow$ hệ thống có thể kết luận ngay ảnh không có vết tối dị biệt mà không cần phân đoạn sai.
5. **Câu 5: Nhóm đã tự cài đặt thuật toán Otsu bằng NumPy như thế nào mà không dùng `cv2.threshold`?**
   - *Gợi ý trả lời:* Nhóm tự tính lược đồ histogram bằng mảng NumPy, chuẩn hóa thành xác suất $p_i$, dùng `np.cumsum` để tính trọng số tích lũy $\omega(k)$ và trung bình tích lũy $\mu(k)$. Sau đó tính vector phương sai $\sigma_B^2(k) = \frac{(\mu_T \omega(k) - \mu(k))^2}{\omega(k)(1 - \omega(k))}$ cho toàn bộ 256 mức xám bằng phép toán vector hóa, và lấy chỉ số cực đại bằng `np.argmax`.

### 🔹 Nhóm câu hỏi về Hình thái học & Trích xuất đặc trưng (Dành cho TV2, TV4)
6. **Câu 6: Trình bày công thức toán học và ý nghĩa của việc trích biên hình thái học theo Slide Chương 6 trang 16?**
   - *Gợi ý trả lời:* Công thức trích biên hình thái là $\beta(A) = A - (A \ominus B)$, nghĩa là lấy tập nhị phân gốc $A$ trừ đi tập $A$ sau khi bị co (erosion) bởi phần tử cấu trúc $B$ (kích thước $3 \times 3$). Phép toán này tạo ra đường biên chuẩn xác có độ dày đúng bằng 1 pixel ôm sát rìa đối tượng.
7. **Câu 7: Tại sao nhóm phải kết hợp cả Phép Mở (Opening) và Phép Đóng (Closing) trong tiền xử lý mặt nạ?**
   - *Gợi ý trả lời:*
     - Phép Mở ($A \circ B = (A \ominus B) \oplus B$): Có tác dụng loại bỏ các đốm nhiễu trắng li ti do bọt sóng biển và các mẩu gợn sóng nhỏ ngoài biển khơi.
     - Phép Đóng ($A \bullet B = (A \oplus B) \ominus B$): Có tác dụng hàn gắn các đoạn thân vệt dầu bị đứt khúc do sóng biển chém ngang, tạo nên một thực thể vệt dầu liền mạch.
8. **Câu 8: Độ tương phản với nền biển lân cận (Annulus Contrast) được tính bằng cách nào?**
   - *Gợi ý trả lời:* Nhóm dùng phép dãn nở (Dilation) với phần tử cấu trúc $7 \times 7$ trên mặt nạ vết dầu để tạo ra một vùng bao rộng hơn, sau đó lấy vùng dãn trừ đi chính mặt nạ vết dầu để thu được một "vành đai nước biển lân cận" bao quanh. Độ tương phản $\Delta \mu = \mu_{\text{vành đai biển}} - \mu_{\text{vết dầu}}$. Nếu $\Delta \mu \ge 12$ mức xám, đốm tối mới được coi là có độ suy giảm tín hiệu thực tế của dầu.

### 🔹 Nhóm câu hỏi về Kiểm chứng, Thực nghiệm & Đánh giá (Dành cho TV2, TV5)
9. **Câu 9: Làm thế nào nhóm chứng minh được code tự viết bằng NumPy có kết quả tương đương với hàm của OpenCV?**
   - *Gợi ý trả lời:* Thành viên TV2 đã xây dựng file kiểm thử `tests/verify_correctness.py`. Đưa cùng một ảnh SAR qua cả 2 hàm (NumPy tự viết và OpenCV), sau đó tính hiệu số ma trận $D = |I_{\text{numpy}} - I_{\text{opencv}}|$. Kết quả đo được: sai số tuyệt đối lớn nhất $\max(D) = 0.0$ và Mean Squared Error $= 0.0$, chứng minh thuật toán tự viết đạt độ chính xác toán học tuyệt đối $100\%$.
10. **Câu 10: Tại sao chỉ số Recall lại quan trọng hơn Precision trong bài toán phát hiện tràn dầu trên biển?**
    - *Gợi ý trả lời:* Trong giám sát môi trường và phòng chống thiên tai biển, việc bỏ sót một vết dầu thực tế (False Negative) gây hậu quả thảm khốc khi dầu dạt vào phá hủy bãi biển du lịch và lồng bè nuôi cá của ngư dân miền Trung. Do đó, ưu tiên hàng đầu là **Recall phải cao** (không bỏ sót), sau đó dùng thêm các bộ lọc hình học để giảm dần False Positive.
11. **Câu 11: Trên tập dữ liệu 5,630 ảnh, hệ thống của nhóm đạt các chỉ số Precision, Recall và F1 là bao nhiêu?**
    - *Gợi ý trả lời:* (Thành viên TV5 nêu số liệu thực tế đo được từ file benchmark, ví dụ: Precision đạt ~86.5%, Recall đạt ~91.2%, F1-Score đạt ~88.8%, thời gian xử lý trung bình đạt ~45 ms/ảnh).

### 🔹 Nhóm câu hỏi về Kiến trúc Hệ thống & Mở rộng (Dành cho TV1)
12. **Câu 12: Với vai trò PM, bạn đã tổ chức mã nguồn và quản lý tiến độ nhóm như thế nào để đảm bảo chuẩn CDIO?**
    - *Gợi ý trả lời:* Em phân chia công việc theo đúng ma trận CDIO và 5 vai trò đề bài quy định. Nhóm áp dụng Git Flow với các nhánh tính năng độc lập, mỗi thành viên đều có commit riêng mang mã số và tên tính năng. Em thiết lập tài liệu kiến trúc, cẩm nang lộ trình 3 tuần và chủ trì các buổi review mã nguồn hàng tuần.
13. **Câu 13: Ứng dụng demo Streamlit giải quyết bài toán thực tế như thế nào?**
    - *Gợi ý trả lời:* Giao diện giúp các kỹ sư tại Trung tâm cảnh báo môi trường biển dễ dàng tải ảnh vệ tinh Sentinel-1 vừa thu nhận, quan sát ngay lập tức 4 bước xử lý trực quan và kết quả viền đỏ ôm sát vết dầu mà không cần thao tác dòng lệnh phức tạp. Người dùng có thể điều chỉnh ngưỡng linh hoạt theo điều kiện thời tiết thực tế.
14. **Câu 14: Nhóm dự kiến mở rộng bài toán sang mô phỏng trôi dầu Lagrangian và tích hợp AIS như thế nào trong tương lai?**
    - *Gợi ý trả lời:*
      - Về trôi dạt: Lấy tọa độ vết dầu phát hiện được làm hạt điểm ban đầu, tích hợp trường vector gió bề mặt ERA5 và dòng chảy hải lưu (mô hình HYCOM/NEMO) theo phương trình vi phân chuyển động hạt Lagrangian để dự báo sau 24h - 48h vệt dầu sẽ trôi dạt vào bãi biển nào của miền Trung.
      - Về truy vết AIS: Trích xuất lịch sử tín hiệu định vị vệ tinh của các tàu chở dầu đi qua tọa độ phát hiện vết dầu vào thời điểm vệ tinh chụp để khoanh vùng và xác định tàu vi phạm xả thải trộm.
15. **Câu 15: Nếu gặp ảnh chụp mép bờ biển có đất liền bị cắt vào, thuật toán của bạn có bị nhầm lẫn không và giải quyết ra sao?**
    - *Gợi ý trả lời:* Đất liền có độ gồ ghề cao nên thường có độ tán xạ ngược rất sáng (ngược lại với vết dầu tối). Tuy nhiên, một số vùng vịnh kín hoặc hồ nước trên bờ cũng có thể tối màu. Giải pháp chuẩn là dùng mặt nạ phân tách đất liền - biển (Land-sea mask từ dữ liệu địa lý GSHHG hoặc phân ngưỡng mức xám cao) để triệt tiêu phần đất liền trước khi áp dụng thuật toán tìm vệt dầu trên biển.
