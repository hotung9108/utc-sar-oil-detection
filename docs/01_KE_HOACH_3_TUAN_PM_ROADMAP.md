# KẾ HOẠCH TÁC CHIẾN 3 TUẦN (21 NGÀY) — MASTER PM ROADMAP
## BÀI TẬP LỚN XỬ LÝ ẢNH — ĐỀ TÀI 18 (SAR OIL SPILL DETECTION)
**Project Manager:** TV1 — Trưởng nhóm & Tích hợp hệ thống  
**Thời lượng:** 3 tuần (21 ngày) | **Phương pháp quản lý:** Agile Scrum rút gọn (Sprint 1 tuần)

---

## 1. TỔNG QUAN TIẾN ĐỘ 3 TUẦN (SPRINT TIMELINE)

```mermaid
gantt
    title LỘ TRÌNH 3 TUẦN BÀI TẬP LỚN XỬ LÝ ẢNH (UTC)
    dateFormat  YYYY-MM-DD
    section TUẦN 1: NỀN TẢNG
    Kick-off & Phân công & Khởi tạo Git        :2026-10-17, 1d
    Chuẩn bị dữ liệu & EDA (TV5)              :2026-10-18, 2d
    Dẫn xuất công thức & Toy Example (TV2)     :2026-10-18, 3d
    Code NumPy: Median, Mean, Otsu (TV3)       :2026-10-19, 4d
    Code NumPy: Morphology & Features (TV4)    :2026-10-20, 4d
    Sprint Review 1 & Rà soát PR               :2026-10-23, 1d
    section TUẦN 2: TÍCH HỢP & THỰC NGHIỆM
    Tích hợp Pipeline tổng thể (TV1)           :2026-10-24, 2d
    Code kiểm chứng NumPy vs OpenCV (TV2)      :2026-10-25, 2d
    Batch Benchmark 5,630 ảnh SAR (TV5)        :2026-10-26, 3d
    Tinh chỉnh Heuristic & Giảm FP (TV4)       :2026-10-27, 2d
    Sprint Review 2 & Bảng số liệu P/R/F1      :2026-10-30, 1d
    section TUẦN 3: ĐÓNG GÓI & BẢO VỆ
    Xây dựng Web App Streamlit (TV1)           :2026-10-31, 3d
    Viết và ráp Báo cáo 40-55 trang (Toàn nhóm):2026-10-31, 4d
    Làm Slide thuyết trình 18 slide            :2026-11-03, 2d
    Quay Video Demo 5-7 phút                   :2026-11-04, 2d
    Diễn tập Vấn đáp Chéo (Mock Defense)       :2026-11-05, 1d
    Đóng gói sản phẩm nộp & Bảo vệ             :2026-11-06, 1d
```

---

## 2. KẾ HOẠCH CHI TIẾT THEO TỪNG NGÀY (DAY-BY-DAY)

### 🚀 TUẦN 1 (NGÀY 1 – NGÀY 7): NỀN TẢNG TOÁN HỌC & CÀI ĐẶT MÃ LÕI NUMPY
**Mục tiêu tuần 1:** Xây dựng đầy đủ lý thuyết, tính tay số liệu mẫu, và tự code 100% thuật toán bằng NumPy mà không phụ thuộc hàm đen OpenCV.

#### Ngày 1 (Thứ 2): Khởi động dự án & Phân công
- **TV1 (PM)**:
  - Tổ chức họp Kick-off qua Google Meet / Trực tiếp (30-45 phút).
  - Phổ biến 5 vai trò, quy chế điểm môn học, và chuẩn đầu ra CDIO.
  - Khởi tạo GitHub repository, thiết lập branch `main`, `develop`, cấu hình `.gitignore`, tạo thư mục dự án theo cấu trúc chuẩn.
- **Cả nhóm**: Clone repository về máy tính cá nhân, kiểm tra môi trường Python 3.10+, cài đặt thư viện cơ bản (`numpy`, `opencv-python`, `scipy`, `matplotlib`, `streamlit`).

#### Ngày 2 (Thứ 3): Khảo sát dữ liệu & Thiết lập kiến trúc
- **TV5**: Khảo sát thư mục `data/Class_0` (3,725 ảnh không dầu) và `data/Class_1` (1,905 ảnh có dầu), đọc `metadata/dataset_metadata.xml`. Viết script nhỏ `inspect_dataset.py` kiểm tra phân bố kích thước ($400 \times 400$), giá trị min, max, mean mức xám.
- **TV2**: Đọc các slide bài giảng (Chương 3, 5, 6, 7) của TS. Phan Thanh Toàn. Liệt kê toàn bộ công thức toán cần dùng vào file nháp: Median filter, Otsu inter-class variance $\sigma_B^2(t)$, hệ số khả tách $\eta$, công thức toán tử hình thái học ($A \ominus B, A \oplus B, A \circ B, A \bullet B$), trích biên $\beta(A)$, độ lớn Gradient Sobel $M(x,y)$.
- **TV1**: Thiết kế sơ đồ kiến trúc Pipeline tổng thể (Flowchart) cho Mục 3.1 của báo cáo.

#### Ngày 3 (Thứ 4): Dẫn xuất công thức & Tính tay ma trận mẫu
- **TV2**:
  - Dẫn xuất chi tiết công thức Otsu và hệ số khả tách $\eta = \sigma_B^2 / \sigma_T^2$.
  - Xây dựng **Ví dụ số tính tay (Toy Example)** trên ma trận $5 \times 5$:
    1. Lọc trung vị với cửa sổ $3 \times 3$.
    2. Tính Histogram, tính $\mu_T$, $\sigma_B^2(t)$ và tìm ngưỡng $T^*$ bằng tay.
    3. Áp dụng phần tử cấu trúc $3 \times 3$ tính phép co và trích biên $\beta(A)$.
- **TV3**: Bắt đầu viết hàm lọc trung vị `custom_median_filter(image, ksize)` và lọc trung bình `custom_mean_filter(image, ksize)` thuần NumPy (dùng phép trượt sliding window / slicing).

#### Ngày 4 (Thứ 5): Cài đặt thuật toán phân đoạn NumPy
- **TV3**:
  - Cài đặt thuật toán Otsu bằng NumPy: `custom_otsu_threshold(image)`.
  - Tính chính xác $\sigma_B^2(t)$ cho $t \in [0, 255]$ và hệ số $\eta$.
  - Trả về ngưỡng tối ưu $T^*$ và mặt nạ nhị phân đốm tối ($I(x,y) \le T^*$).
- **TV4**: Bắt đầu lập trình thư viện hình thái học cơ bản bằng NumPy:
  - Phép co `custom_erode(mask, se)` và phép dãn `custom_dilate(mask, se)`.
  - Phép mở `custom_open` và phép đóng `custom_close`.

#### Ngày 5 (Thứ 6): Cài đặt trích biên & trích xuất đặc trưng
- **TV4**:
  - Cài đặt trích biên hình thái học theo đúng công thức slide P16: $\beta(A) = A - (A \ominus B)$ bằng NumPy.
  - Cài đặt toán tử Sobel tính gradient biên: $G_x, G_y$ bằng nhân chập NumPy với ma trận $3 \times 3$.
  - Cài đặt tính độ tương phản với nền lân cận (vành đai biên Annulus Dilation).
- **TV3**: Tối ưu hóa tốc độ các hàm NumPy (sử dụng vectorization thay vì loop lồng nhau quá sâu).

#### Ngày 6 (Thứ 7): Hoàn thiện các hàm lõi độc lập
- **TV3 & TV4**: Viết unit test nhỏ cho từng hàm, đảm bảo chạy đúng trên ảnh mẫu `data/sample`.
- **TV2**: Viết bản nháp Chương 2 báo cáo (Cơ sở lý thuyết & Mô hình toán học) và bảng số liệu ví dụ tính tay $5 \times 5$.
- **TV5**: Chuẩn bị bộ dữ liệu test đại diện (gồm 100 ảnh Class 0 và 100 ảnh Class 1) để chuẩn bị cho giai đoạn benchmark tuần 2.

#### Ngày 7 (Chủ nhật): Sprint Review 1 & Rà soát Git PR
- **TV1 (PM)**:
  - Tổ chức họp Sprint Review 1 (45 phút).
  - Rà soát Pull Request (PR) của TV2, TV3, TV4, TV5 vào nhánh `develop`.
  - Kiểm tra lịch sử `git log` đảm bảo mỗi thành viên đều có commit độc lập đúng với phần mã mình phụ trách.
  - **Tiêu chí nghiệm thu (DoD - Tuần 1)**: Đã có đủ các file NumPy tự viết chạy được trên ảnh mẫu đơn lẻ mà không báo lỗi cú pháp.

---

### ⚙️ TUẦN 2 (NGÀY 8 – NGÀY 14): TÍCH HỢP HỆ THỐNG & ĐÁNH GIÁ ĐỊNH LƯỢNG
**Mục tiêu tuần 2:** Tích hợp pipeline hoàn chỉnh, chứng minh tính đúng so với OpenCV, chạy thực nghiệm toàn diện trên 5,630 ảnh và lập bảng chỉ số.

#### Ngày 8 (Thứ 2): Tích hợp Pipeline tổng thể
- **TV1 (PM)**:
  - Viết file `pipeline.py` kết nối các hàm của TV3 và TV4 theo luồng 4 bước tuần tự:
    `Ảnh gốc -> Lọc trung vị NumPy -> Phân ngưỡng Otsu NumPy -> Hình thái học & Trích biên NumPy -> Lọc đặc trưng & Viền đỏ`.
  - Đảm bảo đầu vào là ảnh bất kỳ và đầu ra là ảnh viền đỏ, mặt nạ nhị phân và danh sách các vết dầu phát hiện.

#### Ngày 9 (Thứ 3): Kiểm chứng tính đúng (NumPy vs OpenCV)
- **TV2**:
  - Viết script `tests/verify_correctness.py`.
  - So sánh kết quả từng bước:
    1. `custom_median_filter` vs `cv2.medianBlur`: Tính sai số tuyệt đối lớn nhất ($\max |I_{np} - I_{cv}|$) và Mean Squared Error (MSE).
    2. `custom_otsu_threshold` vs `cv2.threshold(..., cv2.THRESH_OTSU)`: So sánh giá trị ngưỡng $T^*$ tìm được.
    3. `custom_erode` & `custom_dilate` vs `cv2.erode` & `cv2.dilate`.
    4. `custom_sobel` vs `cv2.Sobel`.
  - Xuất bảng so sánh sai số và thời gian chạy (tính bằng milli-giây) để đưa vào Mục 3.5 báo cáo.

#### Ngày 10 (Thứ 4): Tinh chỉnh Heuristic & Phân loại Dầu vs Vết tương tự (Look-alikes)
- **TV4**:
  - Tinh chỉnh bộ tiêu chí lọc đốm tối (Heuristic rules) để loại trừ các ca báo động giả:
    - Vùng gió lặng (Low wind): diện tích quá lớn nhưng gradient biên mờ nhạt ($\overline{G}_{border} < 6.0$).
    - Bọt biển / Nhiễu đốm: diện tích nhỏ ($Area < 150$ px).
    - Vết dầu thực tế: Độ tương phản $\Delta \mu \ge 12.0$, gradient biên sắc nét, độ thuôn dài $Elongation \ge 2.0$.
  - (Tùy chọn mở rộng): Huấn luyện thử nghiệm mô hình phân loại SVM / Decision Tree trên vector đặc trưng nếu cần đối chiếu.

#### Ngày 11 (Thứ 5): Batch Benchmark toàn bộ dữ liệu (5,630 ảnh)
- **TV5**:
  - Viết script chạy tự động `batch_evaluation.py` duyệt qua toàn bộ:
    - 3,725 ảnh trong `data/Class_0` (Look-alikes / Biển sạch).
    - 1,905 ảnh trong `data/Class_1` (Vết dầu thực tế).
  - Thu thập kết quả: True Positive (TP), False Positive (FP), True Negative (TN), False Negative (FN).
  - Đo thời gian xử lý trung bình mỗi ảnh (Inference Time).

#### Ngày 12 (Thứ 6): Tính toán các chỉ số CDIO và vẽ biểu đồ
- **TV5**:
  - Tính toán các chỉ số đánh giá theo yêu cầu đề bài:
    $$\text{Precision} = \frac{\text{TP}}{\text{TP} + \text{FP}}, \quad \text{Recall} = \frac{\text{TP}}{\text{TP} + \text{FN}}, \quad \text{F1-score} = 2 \cdot \frac{P \cdot R}{P + R}, \quad \text{Accuracy} = \frac{\text{TP} + \text{TN}}{\text{Total}}$$
  - Lập Ma trận nhầm lẫn (Confusion Matrix).
  - Viết script `plot_results.py` dùng `matplotlib` vẽ:
    - Biểu đồ Confusion Matrix dạng Heatmap.
    - Biểu đồ phân bố các đặc trưng (Histogram của diện tích, độ tương phản, gradient biên giữa Class 0 và Class 1).
    - Đồ thị so sánh thời gian thực thi NumPy vs OpenCV.

#### Ngày 13 (Thứ 7): So sánh và phân tích ca lỗi (Failure Analysis)
- **Cả nhóm**:
  - Họp rà soát các trường hợp hệ thống dự đoán sai (False Positives và False Negatives).
  - TV5 chọn ra 3-5 ảnh tiêu biểu dự đoán đúng và 2-3 ảnh dự đoán sai để phân tích nguyên nhân vật lý SAR (do vệt tối quá mờ, nhiễu bờ biển, hoặc hiện tượng màng sinh học trải rộng).
  - TV5 hoàn thiện bản nháp Chương 4 báo cáo (Thực nghiệm và Đánh giá).

#### Ngày 14 (Chủ nhật): Sprint Review 2 & Khóa luồng thuật toán
- **TV1 (PM)**:
  - Tổ chức họp Sprint Review 2.
  - Khóa toàn bộ mã nguồn lõi (Code Freeze cho thuật toán chính), merge vào nhánh `develop`.
  - **Tiêu chí nghiệm thu (DoD - Tuần 2)**: Toàn bộ pipeline chạy mượt mà, có đầy đủ bảng kiểm chứng tính đúng (TV2) và bảng số liệu thực nghiệm đầy đủ trên toàn bộ dữ liệu (TV5).

---

### 🏆 TUẦN 3 (NGÀY 15 – NGÀY 21): ĐÓNG GÓI SẢN PHẨM, VIẾT BÁO CÁO & BẢO VỆ
**Mục tiêu tuần 3:** Xây dựng Web App Demo có GUI, hoàn thiện Báo cáo PDF 40-55 trang, thiết kế Slide 18 trang, quay Video 5-7 phút và diễn tập vấn đáp đạt điểm 10.

#### Ngày 15 (Thứ 2): Xây dựng Giao diện Demo trực quan (Streamlit App)
- **TV1 (PM)**:
  - Lập trình ứng dụng giao diện web bằng Streamlit: `app.py`.
  - Các tính năng bắt buộc:
    1. Tải ảnh tùy chọn từ máy tính hoặc chọn ảnh mẫu từ thư viện (Class 0 / Class 1).
    2. Thanh trượt (Sliders) điều chỉnh tham số thời gian thực: Kích thước kernel lọc trung vị, Ngưỡng diện tích tối thiểu ($A_{min}$), Độ tương phản tối thiểu ($\Delta \mu$), Gradient biên tối thiểu.
    3. Hiển thị song song 4 ảnh trực quan: Ảnh gốc $\rightarrow$ Ảnh sau lọc $\rightarrow$ Mặt nạ nhị phân Otsu & Morphology $\rightarrow$ Ảnh kết quả viền đỏ ôm sát vết dầu.
    4. Bảng thông số đo đạc thời gian thực (Diện tích, Tương phản, Gradient biên, Kết luận: "Phát hiện vết dầu" hoặc "Biển bình thường / Look-alike").

#### Ngày 16 (Thứ 3): Đồng bộ và biên tập Báo cáo (Chương 1, 2, 3)
- **TV1 (PM)**:
  - Tạo template báo cáo chuẩn (Word hoặc Overleaf/LaTeX) theo quy cách của UTC (Font Times New Roman 13pt, dãn dòng 1.2 - 1.3, lề chuẩn).
  - Viết hoàn thiện **Chương 1** (Tổng quan bài toán tràn dầu biển miền Trung Việt Nam, lý do dùng ảnh SAR Sentinel-1, mục tiêu đồ án).
  - Viết **Mục 3.1** (Kiến trúc pipeline tổng thể) và **Mục 3.4** (Thiết kế ứng dụng giao diện demo).
- **TV2**: Đưa nội dung lý thuyết, công thức LaTeX và ma trận tính tay $5 \times 5$ vào **Chương 2**; đưa bảng so sánh kiểm chứng NumPy vs OpenCV vào **Mục 3.5**.
- **TV3**: Viết **Mục 3.2** (Chi tiết cài đặt Lọc trung vị và Phân ngưỡng Otsu bằng NumPy).
- **TV4**: Viết **Mục 3.3** (Chi tiết cài đặt Hình thái học, trích biên và các đặc trưng).

#### Ngày 17 (Thứ 4): Hoàn thiện Báo cáo (Chương 4, 5) & Rà soát tổng thể
- **TV5**: Đưa toàn bộ bảng số liệu, biểu đồ Confusion Matrix, phân tích định lượng và phân tích ca lỗi vào **Chương 4**.
- **TV1 (PM)**:
  - Viết **Chương 5** (Kết luận, đánh giá mức độ hoàn thành theo chuẩn CDIO, bài học kinh nghiệm và hướng phát triển: mô phỏng trôi dầu Lagrangian, tích hợp dữ liệu AIS truy vết tàu xả thải).
  - Rà soát toàn bộ báo cáo: Căn lề, đánh số thứ tự hình vẽ/bảng biểu, kiểm tra lỗi chính tả, mục lục tự động. Đảm bảo dung lượng nằm trong khoảng **40 – 55 trang**.
  - Xuất file `BaoCao_BTL_XLA_NhomX_De18.pdf`.

#### Ngày 18 (Thứ 5): Thiết kế Slide thuyết trình bảo vệ (15 – 20 slide)
- **TV1 (PM)**: Lên dàn ý chi tiết 18 slide PowerPoint/Canva chuyên nghiệp, phân bổ người thuyết trình:
  - Slide 1–3: Mở đầu & Ý nghĩa thực tiễn biển miền Trung (TV1 trình bày - 2 phút).
  - Slide 4–6: Cơ sở lý thuyết & Mô hình toán học (TV2 trình bày - 2.5 phút).
  - Slide 7–10: Thiết kế & Cài đặt thuật toán thuần NumPy (TV3 & TV4 trình bày - 4 phút).
  - Slide 11–14: Kết quả thực nghiệm, Confusion Matrix & Đánh giá định lượng (TV5 trình bày - 2.5 phút).
  - Slide 15–18: Kiến trúc App Demo, Kết luận & Hướng phát triển AIS (TV1 trình bày - 1 phút).
  - Tổng thời gian thuyết trình: **12 phút**.

#### Ngày 19 (Thứ 6): Quay Video Demo (5 – 7 phút)
- **TV1 (PM)**:
  - Chủ trì quay màn hình video demo bằng OBS Studio hoặc Loom/Clipchamp.
  - Kịch bản video (6 phút):
    - 0:00 - 1:00: Giới thiệu đề tài, bài toán dầu vón cục miền Trung, thành viên nhóm.
    - 1:00 - 2:30: Thuyết minh quy trình 4 bước xử lý ảnh trên slide tóm tắt.
    - 2:30 - 5:00: Demo trực tiếp trên giao diện Streamlit Web App: Thử nghiệm với ảnh có dầu thực tế (Class 1) $\rightarrow$ chỉnh slider $\rightarrow$ thuật toán nhận diện chuẩn viền đỏ; Thử nghiệm với ảnh gió lặng (Class 0) $\rightarrow$ thuật toán tự động lọc bỏ.
    - 5:00 - 6:00: Bảng số liệu kiểm chứng và kết luận.
  - Xuất video chuẩn Full HD 1080p, tải lên Google Drive / YouTube (chế độ Unlisted).

#### Ngày 20 (Thứ 7): Diễn tập Bảo vệ thử nghiệm (Mock Defense) & Luyện vấn đáp
- **Cả nhóm**:
  - Tổ chức buổi bảo vệ thử nghiệm bấm giờ đúng 20 phút (12 phút thuyết trình + 3 phút demo app + 5 phút hỏi đáp).
  - **TV1 (PM)** đóng vai trò Giảng viên (TS. Phan Thanh Toàn), sử dụng ngân hàng câu hỏi trong tài liệu `05_KE_HOACH_DEMO_SLIDE_VIDEO_VAN_DAP.md` để hỏi bất kỳ thành viên nào:
    - *Hỏi TV5 về công thức trích biên hình thái học $\beta(A)$*.
    - *Hỏi TV3 về ý nghĩa của hệ số khả tách Otsu $\eta$*.
    - *Hỏi TV2 về lý do SAR có đốm tối*.
  - Chỉnh sửa ngay những chỗ ấp úng hoặc trả lời chưa chuẩn xác.

#### Ngày 21 (Chủ nhật): Đóng gói hồ sơ, Đánh giá chéo & Sẵn sàng chiến thắng
- **TV1 (PM)**:
  - Thu thập bảng điểm tự đánh giá và đánh giá chéo của 5 thành viên (theo mẫu trong tài liệu `02`).
  - Kiểm tra lần cuối các sản phẩm nộp:
    1. Báo cáo PDF hoàn chỉnh (30 - 60 trang).
    2. Slide bảo vệ PPTX / PDF (15 - 20 slide).
    3. Đường link Video demo (5 - 7 phút).
    4. Repo Git sạch đẹp, có file `README.md` hướng dẫn chạy và lịch sử commit đầy đủ của 5 người.
    5. Bảng điểm đánh giá chéo thành viên có chữ ký xác nhận.
  - Tự tin cùng nhóm bước vào buổi bảo vệ chính thức!

---

## 3. QUẢN TRỊ RỦI RO DỰ ÁN (RISK MANAGEMENT)

| STT | Rủi ro tiềm ẩn | Mức độ | Biện pháp phòng ngừa & Xử lý của PM |
| :---: | :--- | :---: | :--- |
| 1 | Thành viên code chậm / không hoàn thành thuật toán NumPy | **Cao** | PM quy định deadline nội bộ sớm hơn 2 ngày. Nhóm đã có sẵn mã nguồn tham chiếu trong `course_cv/` để các bạn đối chiếu và học hỏi cú pháp. |
| 2 | Lịch sử commit Git bị dồn vào 1 người | **Nghiêm trọng** | Ngay từ Ngày 1, PM bắt buộc mỗi người tạo nhánh `feature/tvX` riêng, tự commit và tạo PR. PM tuyệt đối không commit hộ. |
| 3 | Tỉ lệ báo động giả (False Positive) cao do vùng gió lặng | **Trung bình** | Tinh chỉnh tham số Heuristic: kết hợp cả 3 điều kiện (Diện tích tối thiểu, Độ tương phản với nền biển lân cận $\ge 12$, Gradient biên Sobel $\ge 6.0$). |
| 4 | Báo cáo bị vụn, không đồng nhất văn phong | **Trung bình** | TV1 là người biên tập cuối cùng (Editor-in-Chief), áp dụng bộ Style Guide chung: font chữ, quy chuẩn gọi tên công thức, chú thích hình ảnh. |
| 5 | Thành viên bị "đứng hình" khi giảng viên hỏi chéo | **Rất cao** | Bắt buộc tham gia buổi Mock Defense vào Ngày 20. Học thuộc lòng 15 câu hỏi phản biện cốt lõi trong cẩm nang `05`. |
