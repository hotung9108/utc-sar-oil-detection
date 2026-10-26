# ĐỀ CƯƠNG CHI TIẾT BÁO CÁO BÀI TẬP LỚN (30 – 60 TRANG)
## BÀI TẬP LỚN XỬ LÝ ẢNH — ĐẠI HỌC GIAO THÔNG VẬN TẢI (UTC)
**Đề tài 18:** Phát hiện vết dầu tràn trên biển từ ảnh SAR (★★★) — NASA #6  
**Chủ biên & Tổng hợp:** TV1 — Project Manager  
**Dung lượng mục tiêu:** 45 – 55 trang (chuẩn quy định 30 – 60 trang)

---

## 1. BẢNG PHÂN BỔ DUNG LƯỢNG TRANG & TÁC GIẢ PHỤ TRÁCH

| Chương / Mục | Tiêu đề | Số trang dự kiến | Tác giả viết chính | Tác giả hỗ trợ |
| :--- | :--- | :---: | :---: | :---: |
| **Phần đầu** | Trang bìa, Lời cảm ơn, Mục lục, Danh mục hình vẽ & bảng biểu, Bảng ký hiệu | **4 trang** | **TV1** | Toàn nhóm |
| **Chương 1** | **MỞ ĐẦU VÀ TỔNG QUAN BÀI TOÁN** | **6 trang** | **TV1** | TV5 |
| **Chương 2** | **CƠ SỞ LÝ THUYẾT VÀ MÔ HÌNH TOÁN HỌC** | **12 trang** | **TV2** | TV3, TV4 |
| **Chương 3** | **THIẾT KẾ VÀ CÀI ĐẶT THUẬT TOÁN** | **16 trang** | Cả nhóm | TV1 chủ trì |
| *Mục 3.1* | Kiến trúc hệ thống và Sơ đồ luồng xử lý | 3 trang | **TV1** | Toàn nhóm |
| *Mục 3.2* | Cài đặt thuật toán Tiền xử lý & Phân ngưỡng Otsu | 4 trang | **TV3** | TV2 |
| *Mục 3.3* | Cài đặt Hình thái học & Trích xuất đặc trưng | 4 trang | **TV4** | TV2 |
| *Mục 3.4* | Thiết kế và Hiện thực Ứng dụng Giao diện tương tác | 2.5 trang | **TV1** | Toàn nhóm |
| *Mục 3.5* | Kiểm chứng tính đúng của mã tự viết so với thư viện | 2.5 trang | **TV2** | TV3, TV4 |
| **Chương 4** | **THỰC NGHIỆM, ĐÁNH GIÁ ĐỊNH LƯỢNG VÀ THẢO LUẬN** | **12 trang** | **TV5** | Cả nhóm |
| **Chương 5** | **KẾT LUẬN VÀ HƯỚNG PHÁT TRIỂN** | **4 trang** | **TV1** | Toàn nhóm |
| **Phần cuối** | Tài liệu tham khảo & Phụ lục mã nguồn | **4 trang** | **TV1** | Toàn nhóm |
| **TỔNG CỘNG** | | **58 trang** | *(Đạt chuẩn quy định 30–60 trang)* | |

---

## 2. KHUNG ĐỀ CƯƠNG CHI TIẾT TỪNG TIỂU MỤC

### TRANG BÌA & MỤC LỤC TỰ ĐỘNG (4 trang)
- Bìa chính (Trường ĐH Giao thông vận tải, Khoa CNTT, Bộ môn Xử lý ảnh, Tên đề tài, Giảng viên: TS. Phan Thanh Toàn, Danh sách 5 sinh viên có ghi rõ vai trò TV1 - TV5).
- Lời cam đoan và Lời cảm ơn.
- Mục lục tự động (Heading 1, 2, 3).
- Danh mục bảng biểu và Danh mục hình vẽ.
- Danh mục từ viết tắt và ký hiệu toán học ($I(x,y)$, $\sigma_B^2$, $\eta$, $\beta(A)$...).

---

### CHƯƠNG 1: MỞ ĐẦU VÀ TỔNG QUAN BÀI TOÁN (6 trang — Do TV1 viết chính)
- **1.1. Bối cảnh thực tiễn tại Việt Nam**:
  - Hiện tượng dầu vón cục và dầu tràn trôi dạt bờ biển miền Trung (Hà Tĩnh, Quảng Bình, Thừa Thiên Huế, Đà Nẵng, Quảng Nam, Quảng Ngãi...).
  - Thiệt hại kinh tế đối với du lịch bãi biển và ngành nuôi trồng thủy hải sản.
- **1.2. Giám sát biển bằng công nghệ Radar khẩu độ tổng hợp (SAR)**:
  - Giới hạn của ảnh quang học (bị mây mù che phủ, không hoạt động ban đêm).
  - Ưu thế vượt trội của vệ tinh Sentinel-1 SAR: Chụp xuyên mây 24/7, độ phân giải cao.
- **1.3. Đặc trưng vật lý của vết dầu trên ảnh SAR & Thách thức "Look-alikes"**:
  - Tại sao vệt dầu lại tối màu? Hiện tượng dập tắt sóng mao dẫn (capillary waves) và phản xạ gương.
  - Vấn đề báo động giả từ các hiện tượng tự nhiên tương tự dầu (Look-alikes): vùng gió lặng, màng sinh học thực vật phù du, dòng chảy biển.
- **1.4. Mục tiêu và Phạm vi của Bài tập lớn**:
  - Xây dựng hệ thống tự động phát hiện vết dầu tràn bằng thuật toán Xử lý ảnh thuần túy.
  - Tự cài đặt 100% thuật toán lõi bằng thư viện NumPy theo giáo trình UTC.
  - Phát triển ứng dụng tương tác giao diện và đánh giá định lượng trên bộ dữ liệu lớn.

---

### CHƯƠNG 2: CƠ SỞ LÝ THUYẾT VÀ MÔ HÌNH TOÁN HỌC (12 trang — Do TV2 viết chính)
- **2.1. Mô hình ảnh SAR và Nhiễu đốm đục hạt (Speckle Noise)**:
  - Bản chất nhiễu đốm nhân tính (multiplicative noise model): $I(x,y) = R(x,y) \cdot u(x,y)$.
  - Phân tích sự cần thiết của việc khử nhiễu đốm bảo toàn đường biên (Chương 3 - Slide P104-106).
- **2.2. Phương pháp lọc không gian bảo toàn biên**:
  - Toán tử lọc trung vị 2D (Median Filter): Công thức toán và thuật toán sắp xếp thứ tự.
  - Toán tử lọc trung bình (Box Filter) và so sánh ưu nhược điểm.
- **2.3. Lý thuyết Phân ngưỡng tối ưu Otsu và Tính khả tách** (Chương 7 - Slide P48-55):
  - Dẫn xuất toán học: Lược đồ tần suất $p_i$, trung bình tích lũy $\mu(k)$, trọng số lớp $\omega(k)$, phương sai liên lớp $\sigma_B^2(k)$, phương sai toàn cục $\sigma_T^2$.
  - Công thức hệ số khả tách: $\eta = \frac{\sigma_B^2(T^*)}{\sigma_T^2} \in [0, 1]$.
  - Cơ chế ứng dụng Otsu để tách lớp đối tượng tối màu ($I \le T^*$).
- **2.4. Lý thuyết Xử lý ảnh hình thái học (Morphological Operations)** (Chương 6):
  - Phần tử cấu trúc (Structuring Element $B$) dạng đĩa / elip.
  - Phép co (Erosion): $A \ominus B = \{z \in Z^2 \mid (B)_z \subseteq A\}$.
  - Phép dãn (Dilation): $A \oplus B = \{z \in Z^2 \mid (\hat{B})_z \cap A \neq \emptyset\}$.
  - Phép mở (Opening $A \circ B$) và Phép đóng (Closing $A \bullet B$).
  - Thuật toán trích biên hình thái học chuẩn toán học (Slide Chương 6 P16): $\beta(A) = A - (A \ominus B)$.
- **2.5. Phân tích đường biên và Đạo hàm ảnh** (Chương 5 - Slide P36-40):
  - Toán tử vi phân Sobel theo hướng ngang $G_x$ và dọc $G_y$.
  - Độ lớn Gradient: $M(x,y) = \sqrt{G_x^2 + G_y^2}$.
- **2.6. Ví dụ số tính tay minh họa (Toy Example trên ma trận $5 \times 5$)**:
  - Bảng số liệu ma trận ảnh giả lập $5 \times 5$.
  - Tính toán từng bước bằng tay: Lọc trung vị qua cửa sổ $3 \times 3$, tính Otsu tìm $T^*$, áp ma trận co dãn và trích biên $\beta(A)$.

---

### CHƯƠNG 3: THIẾT KẾ VÀ CÀI ĐẶT THUẬT TOÁN (16 trang — Phối hợp 5 người)
- **3.1. Kiến trúc hệ thống và Pipeline tổng thể** *(TV1 viết - 3 trang)*:
  - Sơ đồ khối 4 bước xử lý tuần tự (Flowchart).
  - Luồng dữ liệu (Dataflow) từ ảnh thô Sentinel-1 đến ảnh viền đỏ trực quan.
- **3.2. Cài đặt thuật toán Tiền xử lý & Phân đoạn bằng NumPy** *(TV3 viết - 4 trang)*:
  - Cài đặt hàm `custom_median_filter` thuần NumPy (kỹ thuật trượt cửa sổ và padding biên).
  - Cài đặt thuật toán Otsu tối ưu `custom_otsu_threshold` và tính hệ số khả tách $\eta$.
  - Đoạn code mẫu then chốt và phân tích độ phức tạp thời gian.
- **3.3. Cài đặt Hình thái học & Trích xuất đặc trưng bằng NumPy** *(TV4 viết - 4 trang)*:
  - Cài đặt phép co, dãn, mở, đóng và lấp lỗ thủng thuần NumPy.
  - Cài đặt trích biên hình thái học đơn pixel $\beta(A) = A - (A \ominus B)$.
  - Cài đặt trích xuất 4 đặc trưng phân biệt: Độ thuôn dài ($Elongation$), Độ phức tạp biên ($Complexity$), Gradient ranh giới Sobel, Độ tương phản vành khuyên (Annulus Contrast).
  - Quy tắc phân loại Heuristic loại bỏ vùng gió lặng (Look-alikes).
- **3.4. Thiết kế và Hiện thực Ứng dụng Giao diện Demo tương tác** *(TV1 viết - 2.5 trang)*:
  - Kiến trúc giao diện Web Streamlit (`app.py`).
  - Thiết kế các thanh trượt điều khiển tham số (kernel size, min area, min contrast, gradient thresh).
  - Cơ chế hiển thị song song 4 bước xử lý ảnh và bảng dữ liệu thống kê thời gian thực.
- **3.5. Kiểm chứng tính đúng của các thuật toán tự cài đặt** *(TV2 viết - 2.5 trang)*:
  - Phương pháp kiểm chứng đối chiếu với thư viện OpenCV chuẩn (`tests/verify_correctness.py`).
  - Bảng đo đạc sai số cực đại ($\max |I_{np} - I_{cv}|$), sai số MSE và so sánh thời gian chạy.
  - Đánh giá và khẳng định tính tương đương toán học của mã nguồn tự viết.

---

### CHƯƠNG 4: THỰC NGHIỆM, ĐÁNH GIÁ ĐỊNH LƯỢNG VÀ THẢO LUẬN (12 trang — Do TV5 viết chính)
- **4.1. Môi trường thực nghiệm và Bộ dữ liệu kiểm thử**:
  - Cấu hình phần cứng và môi trường phần mềm (Python 3.10+, CPU/RAM).
  - Phân bố tập dữ liệu CSIRO Sentinel-1 SAR: 3,725 ảnh Class 0 và 1,905 ảnh Class 1.
- **4.2. Phương pháp và Các chỉ số đánh giá định lượng**:
  - Định nghĩa True Positive (TP), False Positive (FP), True Negative (TN), False Negative (FN).
  - Công thức tính: Accuracy, Precision, Recall, F1-Score, Tốc độ xử lý (Inference Time).
- **4.3. Kết quả thực nghiệm trên toàn bộ tập dữ liệu**:
  - Bảng tổng hợp số liệu đo đạc chi tiết trên Class 0 và Class 1.
  - Ma trận nhầm lẫn (Confusion Matrix) dạng biểu đồ nhiệt Heatmap trực quan.
  - Biểu đồ phân tích độ nhạy của các tham số (ảnh hưởng của ngưỡng diện tích và ngưỡng tương phản).
- **4.4. Đánh giá định tính: Phân tích các trường hợp điển hình**:
  - Minh họa các trường hợp phát hiện xuất sắc vết dầu có hình dạng phức tạp.
  - Minh họa các trường hợp lọc thành công vùng gió lặng không gây báo động giả.
  - Phân tích chi tiết các ca phát hiện sai (False Positives / False Negatives) và giải thích nguyên nhân vật lý.

---

### CHƯƠNG 5: KẾT LUẬN VÀ HƯỚNG PHÁT TRIỂN (4 trang — Do TV1 viết chính)
- **5.1. Kết luận và Mức độ hoàn thành mục tiêu**:
  - Tóm tắt các kết quả đạt được so với yêu cầu đề bài của giảng viên.
  - Đánh giá mức độ đáp ứng các chuẩn đầu ra CDIO của môn học.
- **5.2. Đánh giá ưu điểm và Hạn chế của hệ thống**:
  - Ưu điểm: Tốc độ xử lý nhanh, thuật toán toán học minh bạch 100% không black-box, giao diện trực quan dễ sử dụng.
  - Hạn chế: Khó khăn với các vệt dầu quá mỏng hoặc ảnh có độ nhiễu bờ biển phức tạp.
- **5.3. Hướng phát triển và Ứng dụng thực tiễn**:
  - Mô phỏng quỹ đạo trôi dầu Lagrangian kết hợp gió ERA5 và mô hình dòng chảy đại dương để cảnh báo sớm vùng bờ biển miền Trung chịu ảnh hưởng.
  - Đối soát tọa độ vết dầu với dữ liệu định danh tàu biển AIS (Automatic Identification System) nhằm truy vết chính xác tàu thuyền xả trộm dầu ngoài khơi.

---

### PHẦN CUỐI (4 trang)
- **Tài liệu tham khảo**: Trích dẫn tối thiểu 8-10 tài liệu khoa học chuẩn IEEE (Giáo trình TS. Phan Thanh Toàn, bài báo CSIRO, tài liệu NASA Sentinel-1 SAR).
- **Phụ lục mã nguồn**: Trích dẫn các đoạn code lõi NumPy tiêu biểu.

---

## 3. QUY CÁCH ĐỊNH DẠNG BÁO CÁO (FORMATTING GUIDELINE)

1. **Khổ giấy & Căn lề**:
   - Khổ giấy: A4 (210 x 297 mm).
   - Căn lề chuẩn Luận văn kỹ thuật UTC:
     - Lề trên (Top): 2.0 cm.
     - Lề dưới (Bottom): 2.0 cm.
     - Lề trái (Left): 3.0 cm (để đóng gáy sách).
     - Lề phải (Right): 2.0 cm.
2. **Kiểu chữ & Cỡ chữ**:
   - Font: **Times New Roman**.
   - Cỡ chữ nội dung: **13 pt**. Dãn dòng (Line spacing): **1.25 đến 1.3 lines**. Dãn đoạn: Before 0 pt, After 6 pt.
   - Tiêu đề cấp 1 (Chương): 16 pt, In hoa, Đậm, Căn giữa.
   - Tiêu đề cấp 2 (1.1, 1.2): 14 pt, Đậm, Căn trái.
   - Tiêu đề cấp 3 (1.1.1): 13 pt, Đậm nghiêng, Căn trái.
3. **Quy chuẩn Đánh số Hình vẽ, Bảng biểu và Công thức**:
   - Hình vẽ: Đánh số theo số chương, ví dụ `Hình 2.3: Mô hình lọc trung vị qua cửa sổ 3x3` (đặt dưới hình, căn giữa).
   - Bảng biểu: Đánh số theo chương, ví dụ `Bảng 4.2: Kết quả đo đạc Precision, Recall trên tập kiểm thử` (đặt trên bảng, căn giữa).
   - Công thức: Đánh số căn lề sát mép phải theo định dạng `(2.5)`, `(3.2)`.
