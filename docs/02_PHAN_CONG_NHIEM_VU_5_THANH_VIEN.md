# MA TRẬN PHÂN CÔNG NHIỆM VỤ 5 THÀNH VIÊN & ĐÁNH GIÁ CHÉO
## BÀI TẬP LỚN XỬ LÝ ẢNH — ĐẠI HỌC GIAO THÔNG VẬN TẢI (UTC)
**Đề tài 18:** Phát hiện vết dầu tràn trên biển từ ảnh SAR (★★★) — NASA #6  
**Chuẩn đầu ra áp dụng:** CDIO Toàn diện (Phân tích, Thiết kế, Cài đặt, Vận hành, Làm việc nhóm)

---

## 1. MA TRẬN ÁNH XẠ CHUẨN ĐẦU RA CDIO VÀ 5 VAI TRÒ

| Chuẩn đầu ra CDIO | Thể hiện trong Đồ án | Vai trò chịu trách nhiệm chính | Vai trò phối hợp |
| :--- | :--- | :--- | :--- |
| **1. Phân tích bài toán & Mô hình toán** | Chương 1–2 báo cáo | **TV1** (Bối cảnh biển miền Trung)<br>**TV2** (Mô hình toán học, công thức) | Toàn nhóm |
| **2. Thiết kế thuật toán & Kiến trúc** | Chương 3 báo cáo | **TV1** (Kiến trúc pipeline, GUI)<br>**TV3** (Tiền xử lý & Ngưỡng)<br>**TV4** (Hình thái học & Đặc trưng) | TV2 (Kiểm chứng) |
| **3. Cài đặt & Kiểm thử độc lập** | Mã nguồn Git, Mục 3.5 & Chương 4 | **TV3** (Code lọc & Otsu bằng NumPy)<br>**TV4** (Code Morphology & Features)<br>**TV2** (Code kiểm chứng so với OpenCV) | TV1 (Review PR) |
| **4. Đánh giá định lượng & Cải tiến** | Chương 4–5, Demo tương tác | **TV5** (Benchmark 5,630 ảnh, P/R/F1)<br>**TV1** (Streamlit Demo, hướng mở rộng AIS) | Toàn nhóm |
| **5. Làm việc nhóm & Trình bày kỹ thuật** | Nhật ký nhóm, Git log, Slide, Bảo vệ | **TV1** (Điều phối, Git, Slide, Video)<br>**Cả 5 thành viên** (Bảo vệ 20 phút) | Toàn nhóm |

---

## 2. BẢN MÔ TẢ CÔNG VIỆC CHI TIẾT (JOB DESCRIPTION) TỪNG THÀNH VIÊN

### 👑 THÀNH VIÊN 1 (TV1) — TRƯỞNG NHÓM, TÍCH HỢP HỆ THỐNG (PROJECT MANAGER)
- **Họ và tên:** *[Điền tên của bạn]* | **Mã sinh viên:** *[Điền MSV]*
- **Trách nhiệm kỹ thuật cốt lõi:**
  1. Quản lý dự án tổng thể: phân công, theo dõi tiến độ hằng ngày, quản lý GitHub repository và duyệt Pull Request.
  2. Thiết kế kiến trúc mã nguồn tổng thể (`pipeline.py`), tích hợp các module độc lập của TV3 và TV4 thành luồng xử lý trơn tru.
  3. Xây dựng Ứng dụng Demo có giao diện trực quan hoàn chỉnh (`app.py` bằng Streamlit hoặc PyQt) cho phép người dùng kéo slider tham số và xem kết quả 4 bước trực quan.
- **Phần báo cáo chịu trách nhiệm viết chính:**
  - **Chương 1:** Mở đầu và Tổng quan bài toán (Vấn đề ô nhiễm dầu vón cục biển miền Trung, đặc trưng ảnh radar SAR Sentinel-1, mục tiêu và phạm vi đề tài).
  - **Mục 3.1:** Kiến trúc hệ thống và Sơ đồ khối Pipeline tổng thể.
  - **Mục 3.4:** Thiết kế và Hiện thực hóa ứng dụng giao diện Demo tương tác.
  - **Chương 5:** Kết luận, đánh giá mức độ hoàn thành chuẩn CDIO, bài học kinh nghiệm và hướng phát triển (mô phỏng trôi dầu Lagrangian, tích hợp AIS truy vết tàu xả trộm).
- **Trách nhiệm bảo vệ:** Thuyết trình mở đầu (Slide 1-3), điều phối phần thuyết trình của nhóm, trực tiếp bấm và thao tác demo ứng dụng 3 phút trước hội đồng.

---

### 📐 THÀNH VIÊN 2 (TV2) — LÝ THUYẾT TOÁN HỌC & KIỂM CHỨNG TÍNH ĐÚNG
- **Họ và tên:** *[Điền tên thành viên 2]* | **Mã sinh viên:** *[Điền MSV]*
- **Trách nhiệm kỹ thuật cốt lõi:**
  1. Dẫn xuất toán học chặt chẽ toàn bộ các thuật toán trong bài giảng của TS. Phan Thanh Toàn (Lọc trung vị, phân ngưỡng Otsu tối ưu, phương sai liên lớp $\sigma_B^2$, hệ số khả tách $\eta$, các phép toán hình thái học co/dãn/mở/đóng, trích biên $\beta(A)$, đạo hàm biên Sobel).
  2. Xây dựng **Ví dụ số tính tay (Toy Example)** trên ma trận nhỏ $5 \times 5$: Thể hiện từng bước biến đổi số học (tính histogram, tính ngưỡng, áp phần tử cấu trúc $3 \times 3$, tính gradient).
  3. Lập trình module kiểm chứng `tests/verify_correctness.py`: Đối chiếu từng hàm tự viết bằng NumPy của TV3 và TV4 với hàm chuẩn của OpenCV (`cv2.medianBlur`, `cv2.threshold`, `cv2.erode`, `cv2.Sobel`) bằng các chỉ số sai số tuyệt đối cực đại ($\max |I_{np} - I_{cv}|$), sai số bình phương trung bình (MSE), và so sánh tốc độ thực thi (ms).
- **Phần báo cáo chịu trách nhiệm viết chính:**
  - **Chương 2:** Cơ sở lý thuyết và Mô hình toán học xử lý ảnh (Toàn bộ các công thức toán, ý nghĩa vật lý SAR, và bảng minh họa ví dụ tính tay $5 \times 5$).
  - **Mục 3.5:** Kiểm chứng tính đúng của các thuật toán tự cài đặt (Bảng số liệu đối chiếu NumPy vs OpenCV, phân tích sai số và kết luận tính tương đương).
- **Trách nhiệm bảo vệ:** Thuyết trình phần Cơ sở lý thuyết (Slide 4-6, 2.5 phút), sẵn sàng giải thích chi tiết mọi công thức toán học và bảng tính tay khi giảng viên chất vấn.

---

### ⚙️ THÀNH VIÊN 3 (TV3) — CÀI ĐẶT THUẬT TOÁN 1: TIỀN XỬ LÝ & PHÂN ĐOẠN ỨNG VIÊN
- **Họ và tên:** *[Điền tên thành viên 3]* | **Mã sinh viên:** *[Điền MSV]*
- **Trách nhiệm kỹ thuật cốt lõi:**
  1. Tự lập trình 100% bằng **NumPy thuần** (không gọi hàm OpenCV thực thi thuật toán chính):
     - Hàm lọc trung vị `custom_median_filter(image, ksize)` khử nhiễu đốm speckle (xử lý padding biên, sắp xếp mảng con và lấy giá trị trung vị).
     - Hàm lọc trung bình / Box filter `custom_mean_filter(image, ksize)`.
     - Hàm cân bằng lược đồ mức xám cục bộ / toàn cục.
  2. Tự lập trình 100% bằng **NumPy thuần** thuật toán Phân ngưỡng Otsu tối ưu:
     - Tính lược đồ tần suất $p_i$, trung bình tích lũy $\mu(k)$, trọng số tích lũy $\omega(k)$, trung bình toàn cục $\mu_T$.
     - Tính phương sai liên lớp $\sigma_B^2(k)$ cho mọi ngưỡng $k \in [0, 255]$.
     - Tìm ngưỡng tối ưu $T^* = \arg\max \sigma_B^2(k)$ và tính hệ số khả tách $\eta = \sigma_B^2 / \sigma_T^2$.
     - Sinh mặt nạ nhị phân đốm tối ($I(x,y) \le T^*$).
- **Phần báo cáo chịu trách nhiệm viết chính:**
  - **Mục 3.2:** Cài đặt thuật toán Tiền xử lý lọc nhiễu speckle và Phân đoạn tự động tìm đốm tối ứng viên (Trình bày cấu trúc hàm NumPy, giải thuật xử lý biên padding, mã nguồn mẫu và phân tích độ phức tạp thuật toán $O(N \cdot K^2)$).
- **Trách nhiệm bảo vệ:** Thuyết trình Mục 3.2 trên Slide (2 phút), sẵn sàng trả lời sâu về cơ chế lọc trung vị và cách tính phương sai liên lớp Otsu.

---

### 🔍 THÀNH VIÊN 4 (TV4) — CÀI ĐẶT THUẬT TOÁN 2: HÌNH THÁI HỌC & TRÍCH XUẤT ĐẶC TRƯNG
- **Họ và tên:** *[Điền tên thành viên 4]* | **Mã sinh viên:** *[Điền MSV]*
- **Trách nhiệm kỹ thuật cốt lõi:**
  1. Tự lập trình 100% bằng **NumPy thuần** các toán tử hình thái học:
     - Phép co `custom_erode(mask, se)` và phép dãn `custom_dilate(mask, se)`.
     - Phép mở `custom_open` (xóa bọt sóng biển nhỏ) và phép đóng `custom_close` (hàn gắn vết dầu đứt khúc).
     - Thuật toán lấp lỗ thủng `fill_holes`.
     - Thuật toán trích xuất đường biên hình thái học đơn pixel theo chuẩn Slide P16: $\beta(A) = A - (A \ominus B)$.
  2. Lập trình trích xuất 4 đặc trưng phân biệt đốm tối bằng NumPy:
     - Độ thuôn dài ($Elongation = Major / Minor$).
     - Độ phức tạp biên ($Complexity = Perimeter^2 / (4\pi \cdot Area)$).
     - Độ dốc gradient ranh giới bằng toán tử Sobel NumPy ($M = \sqrt{G_x^2 + G_y^2}$).
     - Độ tương phản với nền biển lân cận (Annulus Background Contrast).
  3. Xây dựng bộ quy tắc lọc heuristic hoặc mô hình phân loại SVM/Decision Tree phân biệt Vết dầu thực tế vs Vết tương tự dầu (Look-alikes: vùng gió lặng, màng sinh học).
- **Phần báo cáo chịu trách nhiệm viết chính:**
  - **Mục 3.3:** Cài đặt các toán tử hình thái học, trích xuất đặc trưng hình học & cường độ, và cơ chế phân loại vết dầu (Trình bày cấu trúc code, ma trận kernel structuring element, công thức 4 đặc trưng).
- **Trách nhiệm bảo vệ:** Thuyết trình Mục 3.3 trên Slide (2 phút), sẵn sàng giải thích cơ chế phân biệt vật lý giữa vệt dầu và vùng gió lặng.

---

### 📊 THÀNH VIÊN 5 (TV5) — DỮ LIỆU, THỰC NGHIỆM ĐỊNH LƯỢNG & ĐÁNH GIÁ KẾT QUẢ
- **Họ và tên:** *[Điền tên thành viên 5]* | **Mã sinh viên:** *[Điền MSV]*
- **Trách nhiệm kỹ thuật cốt lõi:**
  1. Quản lý, kiểm kê và tiền xử lý bộ dữ liệu:
     - 3,725 ảnh `data/Class_0` (Look-alikes: màng sinh học, gió lặng, sóng biển).
     - 1,905 ảnh `data/Class_1` (Vết dầu tràn thực tế).
     - Tạo thư mục `data/sample` phục vụ demo và test nhanh.
  2. Viết script chạy thực nghiệm tự động hàng loạt (`batch_evaluation.py`) trên toàn bộ 5,630 ảnh hoặc tập test chuẩn hóa.
  3. Đo đạc định lượng và thống kê các chỉ số hiệu năng:
     - True Positive (TP), False Positive (FP), True Negative (TN), False Negative (FN).
     - Accuracy, Precision, Recall, F1-score.
     - Tốc độ xử lý trung bình mỗi ảnh (Inference Latency - FPS).
  4. Lập Ma trận nhầm lẫn (Confusion Matrix Heatmap) và vẽ biểu đồ phân bố đặc trưng (Boxplot/Histogram) bằng `matplotlib` / `seaborn`.
  5. Phân tích định tính: Trích xuất các ca phân loại sai (False Positives do vùng gió lặng, False Negatives do vết dầu quá mờ) và giải thích nguyên nhân.
- **Phần báo cáo chịu trách nhiệm viết chính:**
  - **Chương 4:** Thực nghiệm, Đánh giá định lượng và So sánh kết quả (Bảng thống kê tập dữ liệu, bảng số liệu Precision/Recall/F1, hình ảnh Confusion Matrix, đồ thị phân tích và phân tích các trường hợp điển hình).
- **Trách nhiệm bảo vệ:** Thuyết trình Chương 4 trên Slide (2.5 phút), sẵn sàng trả lời về độ tin cậy của tập dữ liệu và ý nghĩa các chỉ số đánh giá.

---

## 3. CHIẾN LƯỢC ĐÀO TẠO CHÉO (CROSS-TRAINING STRATEGY)
> [!CAUTION]
> **Quy định của Giảng viên:** *"Giảng viên chỉ định người trả lời; mỗi thành viên phải trả lời được câu hỏi về phần của bạn khác"*. Nếu giảng viên hỏi TV5 về công thức Otsu của TV3 hoặc hỏi TV2 về giao diện của TV1 mà không trả lời được, cả nhóm sẽ bị trừ điểm rất nặng!

### Ma trận kiến thức tối thiểu 5 thành viên bắt buộc phải nắm:
1. **Tại sao ảnh SAR vết dầu lại có màu tối?**
   - *Trả lời:* Dầu làm giảm sức căng bề mặt và làm phẳng sóng mao dẫn (capillary waves), làm bề mặt biển trơn như gương khiến sóng radar phản xạ đi hướng khác (specular reflection), không tán xạ ngược (backscatter) về máy thu vệ tinh $\rightarrow$ tạo đốm tối.
2. **Công thức trích biên hình thái học là gì?**
   - *Trả lời:* $\beta(A) = A - (A \ominus B)$ (Lấy ảnh nhị phân $A$ trừ đi ảnh sau phép co $A \ominus B$ với phần tử cấu trúc $B$).
3. **Hệ số khả tách Otsu $\eta$ có ý nghĩa gì?**
   - *Trả lời:* $\eta = \sigma_B^2 / \sigma_T^2$ nằm trong khoảng $[0, 1]$. Nếu $\eta$ quá nhỏ ($< 0.1$), ảnh không có 2 đỉnh tách biệt (ảnh biển đồng nhất, không có đốm tối rõ rệt).
4. **Tại sao vùng gió lặng (Low wind) lại gây báo động giả và lọc bằng cách nào?**
   - *Trả lời:* Gió lặng cũng làm biển phẳng $\rightarrow$ đốm tối. Nhưng vùng gió lặng thường có diện tích rất rộng, ranh giới chuyển tiếp thoai thoải nên Gradient biên nhỏ ($\overline{G}_{border}$ thấp), không có độ sắc nét như vết dầu thực tế.

---

## 4. BIỂU MẪU ĐÁNH GIÁ CHÉO THÀNH VIÊN (PEER REVIEW RUBRIC)

Bảng này sẽ được nộp kèm báo cáo chính thức và có chữ ký xác nhận của 5 thành viên. Điểm đánh giá theo thang 100 điểm, chia làm 4 tiêu chí:
1. **Tiến độ & Deadline (25%)**: Hoàn thành đúng hạn các mốc Sprint, không để nhắc nhở.
2. **Chất lượng kỹ thuật (35%)**: Code chạy tốt, tự viết bằng NumPy, không lỗi, báo cáo đúng chuẩn.
3. **Đóng góp Git (20%)**: Có commit đều đặn, rõ ràng trên nhánh của mình, tự viết code.
4. **Thái độ & Phối hợp (20%)**: Tham gia đầy đủ các buổi họp, hợp tác tốt, sẵn sàng hỗ trợ đồng đội.

### BẢNG CHẤM ĐIỂM CHÉO NỘI BỘ (MẪU ĐIỀN VÀO TUẦN 3)

| Mã TV | Họ và tên | Trách nhiệm chính | Tiến độ (25đ) | Kỹ thuật (35đ) | Git (20đ) | Thái độ (20đ) | Tổng điểm (100đ) | Xếp loại (A/B/C) | Chữ ký xác nhận |
| :---: | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **TV1** | *[Tên bạn]* | PM, Tích hợp, App Demo, Ch 1, 3.1, 3.4, Ch 5 | ... /25 | ... /35 | ... /20 | ... /20 | ... /100 | ... | *(Ký tên)* |
| **TV2** | *[Tên TV2]* | Lý thuyết, Kiểm chứng, Toy Ex, Ch 2, 3.5 | ... /25 | ... /35 | ... /20 | ... /20 | ... /100 | ... | *(Ký tên)* |
| **TV3** | *[Tên TV3]* | Lọc speckle, Otsu NumPy, Mục 3.2 | ... /25 | ... /35 | ... /20 | ... /20 | ... /100 | ... | *(Ký tên)* |
| **TV4** | *[Tên TV4]* | Hình thái học, Đặc trưng, Mục 3.3 | ... /25 | ... /35 | ... /20 | ... /20 | ... /100 | ... | *(Ký tên)* |
| **TV5** | *[Tên TV5]* | Dữ liệu, Benchmark, Đồ thị, Chương 4 | ... /25 | ... /35 | ... /20 | ... /20 | ... /100 | ... | *(Ký tên)* |

*Xếp loại đề xuất: Loại A (90 - 100 điểm) | Loại B (75 - 89 điểm) | Loại C (50 - 74 điểm) | Loại D (< 50 điểm)*
