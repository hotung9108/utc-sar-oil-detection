# HỆ THỐNG PHÁT HIỆN VẾT DẦU TRÀN TRÊN BIỂN TỪ ẢNH SAR SENTINEL-1
## BÀI TẬP LỚN MÔN XỬ LÝ ẢNH / COMPUTER VISION — ĐẠI HỌC GIAO THÔNG VẬN TẢI (UTC)
**Học phần:** Xử lý ảnh | **Chuẩn đầu ra:** CDIO Toàn diện (50% điểm học phần)  
**Giảng viên hướng dẫn:** TS. Phan Thanh Toàn  
**Đề tài số 18:** Phát hiện vết dầu tràn trên biển từ ảnh SAR (★★★) — NASA #6  
**Ứng dụng thực tiễn:** Giám sát môi trường biển, cảnh báo sớm dầu vón cục và tràn dầu trôi dạt bờ biển miền Trung Việt Nam

---

## 1. GIỚI THIỆU BÀI TOÁN & Ý NGHĨA THỰC TIỄN
Hàng năm, vùng biển và dải bờ biển các tỉnh miền Trung (Hà Tĩnh, Quảng Bình, Quảng Trị, Thừa Thiên Huế, Đà Nẵng, Quảng Nam, Quảng Ngãi...) thường xuyên đối mặt với sự cố dầu vón cục và các vệt dầu trôi dạt vào bờ, đe dọa nghiêm trọng hệ sinh thái biển, khu bảo tồn san hô, nghề cá và ngành du lịch ven biển.

Việc giám sát bằng ảnh vệ tinh quang học truyền thống bị giới hạn lớn bởi mây mù và bóng tối. Công nghệ **Radar khẩu độ tổng hợp (SAR)** từ vệ tinh Sentinel-1 có khả năng chụp xuyên mây, hoạt động 24/7 cả ngày lẫn đêm, là giải pháp tối ưu để phát hiện sớm các vệt dầu loang ngoài khơi.

Dự án này nghiên cứu và hiện thực hóa hệ thống phát hiện vết dầu tràn tự động bằng **100% thuật toán Xử lý ảnh (Computer Vision) thuần túy**, tự cài đặt mã nguồn bằng thư viện **NumPy**, tuân thủ nghiêm ngặt giáo trình bài giảng của TS. Phan Thanh Toàn.

---

## 2. BẢNG PHÂN CÔNG 5 VAI TRÒ CHUẨN CDIO

| Vai trò | Thành viên | Trách nhiệm chính trong mã nguồn | Phần viết trong Báo cáo |
| :---: | :--- | :--- | :--- |
| **TV1** | *Trưởng nhóm, Tích hợp (PM)* | Quản lý tiến độ, Git repo, thiết kế kiến trúc mã, làm Web App Demo tương tác (Streamlit). | **Chương 1**, **Mục 3.1 & 3.4**, **Chương 5** |
| **TV2** | *Lý thuyết, Kiểm chứng* | Dẫn xuất công thức toán, ví dụ tính tay $5 \times 5$, code kiểm chứng so sánh NumPy vs OpenCV. | **Chương 2**, **Mục 3.5** |
| **TV3** | *Cài đặt thuật toán 1* | Tự lập trình bằng NumPy: Lọc trung vị khử nhiễu đốm speckle, phân ngưỡng Otsu tối ưu tính hệ số $\eta$. | **Mục 3.2** |
| **TV4** | *Cài đặt thuật toán 2* | Tự lập trình bằng NumPy: Hình thái học (co, dãn, mở, đóng), trích biên $\beta(A)$, trích 4 đặc trưng phân biệt. | **Mục 3.3** |
| **TV5** | *Dữ liệu, Thực nghiệm* | Quản lý 5,630 ảnh SAR, viết script chạy thực nghiệm tự động, đo Precision/Recall/F1, vẽ ma trận nhầm lẫn. | **Chương 4** |

---

## 3. CẨM NANG DÀNH CHO NHÓM TRONG THƯ MỤC `docs/`

Toàn bộ tài liệu quy chuẩn, cơ sở toán học và hướng dẫn của dự án được phân nhóm gọn gàng tại thư mục [**`docs/`**](file:///D:/Codin/utc-code/HK4_1/XLA/BTL/docs/README.md):

- 📑 [**`docs/01_quan_ly_du_an/`**](file:///D:/Codin/utc-code/HK4_1/XLA/BTL/docs/01_quan_ly_du_an/): Tổng quan chiến lược PM, kế hoạch 3 tuần chi tiết theo ngày, phân công 5 thành viên CDIO và quy chuẩn Git.
- 📐 [**`docs/02_ly_thuyet_thuat_toan_cv/`**](file:///D:/Codin/utc-code/HK4_1/XLA/BTL/docs/02_ly_thuyet_thuat_toan_cv/): Cơ chế phân biệt Class 0 vs Class 1 (chứng minh True Negative không phải lỗi), công thức toán học 4 chương giáo trình UTC, đặc tả bộ dữ liệu CSIRO.
- 🌐 [**`docs/03_ung_dung_web/`**](file:///D:/Codin/utc-code/HK4_1/XLA/BTL/docs/03_ung_dung_web/): Hướng dẫn khởi động Web Workstation (`run_web.bat`) và hướng dẫn cắm thuật toán tùy chỉnh vào hệ thống.
- 📖 [**`docs/04_bao_cao_va_thuyet_trinh/`**](file:///D:/Codin/utc-code/HK4_1/XLA/BTL/docs/04_bao_cao_va_thuyet_trinh/): Khung đề cương báo cáo LaTeX 5 chương, hướng dẫn biên dịch Overleaf XeLaTeX, kịch bản thuyết trình bảo vệ 12 phút và bộ 15 câu hỏi phản biện vấn đáp.

---

## 4. QUY TRÌNH 4 BƯỚC XỬ LÝ ẢNH THEO GIÁO TRÌNH TS. PHAN THANH TOÀN

```mermaid
flowchart TD
    A["Ảnh SAR gốc (Sentinel-1 400x400)"] --> B["BƯỚC 1: Tiền xử lý (Chương 3)<br>Lọc trung vị Median (ksize=5)<br>Khử nhiễu đốm đục hạt speckle"]
    B --> C["BƯỚC 2: Phân vùng (Chương 7)<br>Phân ngưỡng Otsu tối ưu<br>Đánh giá hệ số khả tách eta = sigma_B^2 / sigma_T^2"]
    C --> D["BƯỚC 3: Hình thái học (Chương 6)<br>Phép Mở (xóa bọt biển) + Phép Đóng (hàn gắn)<br>Lấp lỗ thủng & Trích biên: beta(A) = A - (A (-) B)"]
    D --> E["BƯỚC 4: Phân tích biên (Chương 5)<br>Đạo hàm Sobel tính Gradient ranh giới<br>Đo tương phản vành đai biển Annulus"]
    E --> F["KẾT QUẢ ĐẦU RA<br>Vẽ đường viền ĐỎ ôm sát vết dầu<br>Bảng thống kê diện tích & tọa độ"]
```

---

## 5. CẤU TRÚC THƯ MỤC DỰ ÁN

```
BTL/
├── web/                               # GIAO DIỆN WEB WORKSTATION (STREAMLIT)
│   ├── app.py                         # Ứng dụng web chính (Minimalist Luxury, chữ to)
│   ├── run_web.bat                    # Kích hoạt nhanh web app trong thư mục web
│   └── README.md                      # Hướng dẫn nhanh cho phần Web
│
├── docs/                              # TOÀN BỘ TÀI LIỆU DỰ ÁN (ĐÃ PHÂN FOLDER)
│   ├── 01_quan_ly_du_an/              # Kế hoạch PM, phân công 5 người, Git flow
│   ├── 02_ly_thuyet_thuat_toan_cv/    # Lý thuyết toán, cơ chế Class 0 vs 1, dữ liệu CSIRO
│   ├── 03_ung_dung_web/               # Hướng dẫn chạy web, cắm thuật toán mới
│   ├── 04_bao_cao_va_thuyet_trinh/    # Đề cương báo cáo LaTeX, slide, kịch bản vấn đáp
│   └── README.md                      # Bản đồ tra cứu tổng thể tài liệu
│
├── src/                               # THUẬT TOÁN COMPUTER VISION THUẦN TÚY (PURE CV)
│   ├── pipeline_modular.py            # Pipeline tuần tự 4 bước
│   ├── custom_algorithms.py           # Điểm cắm thuật toán tùy chỉnh cho người dùng
│   ├── preprocessing/                 # Lọc speckle, Otsu tối ưu, Sauvola, CLAHE
│   ├── morphology/                    # Opening, Closing, Fill holes, trích biên beta(A)
│   └── features/                      # Đo diện tích, độ thuôn dài, gradient Sobel
│
├── data/                              # DỮ LIỆU SAR SENTINEL-1 GỐC (5,630 ẢNH)
│   ├── Class_0/                       # 3,725 ảnh không chứa dầu / Look-alikes
│   ├── Class_1/                       # 1,905 ảnh có vết dầu tràn thực tế
│   └── sample/                        # Ảnh mẫu kiểm thử nhanh cho Class 0 và Class 1
│
├── report_latex/                      # MÃ NGUỒN BÁO CÁO LATEX (OVERLEAF)
├── slides/                            # MÃ NGUỒN SLIDE THUYẾT TRÌNH BẢO VỆ
├── RUN_WEB.md                         # Hướng dẫn vận hành Web chi tiết
├── run_web.bat                        # File 1-Click khởi động Web ở thư mục gốc
└── run_web.ps1                        # File PowerShell khởi động Web ở thư mục gốc
```
├── docs/                                  # HỆ THỐNG TÀI LIỆU QUẢN TRỊ DỰ ÁN CỦA PM
│   ├── 00_TONG_QUAN_VA_CHI_THI_PM.md
│   ├── 01_KE_HOACH_3_TUAN_PM_ROADMAP.md
│   ├── 02_PHAN_CONG_NHIEM_VU_5_THANH_VIEN.md
│   ├── 03_GIT_WORKFLOW_VA_QUY_CHUAN_CODE.md
│   ├── 04_DE_CUONG_BAO_CAO_30_60_TRANG.md
│   └── 05_KE_HOACH_DEMO_SLIDE_VIDEO_VAN_DAP.md
│
├── course_cv/                             # THUẬT TOÁN CHUẨN GIÁO TRÌNH TS. PHAN THANH TOÀN
│   ├── step1_filter.py                    # Chương 3: Lọc trung vị khử nhiễu speckle
│   ├── step2_segmentation.py              # Chương 7: Phân ngưỡng Otsu tối ưu & tính eta
│   ├── step3_morphology.py                # Chương 6: Hình thái học & Trích biên beta(A)
│   ├── step4_edge_gradient.py             # Chương 5: Đạo hàm biên Sobel & Tương phản
│   ├── pipeline.py                        # Pipeline 4 bước khép kín
│   ├── main.py                            # Thực thi batch trên tập ảnh
│   └── matlab_slide_pipeline.m            # Script MATLAB Image Processing Toolbox
│
├── data/                                  # DỮ LIỆU SAR SENTINEL-1 (CSIRO DATASET)
│   ├── Class_0/                           # 3,725 ảnh không chứa dầu (Look-alikes)
│   ├── Class_1/                           # 1,905 ảnh có chứa vết dầu tràn thực tế
│   └── sample/                            # Ảnh mẫu kiểm thử nhanh
│
├── outputs_slide/                         # ẢNH KẾT QUẢ TRỰC QUAN VIỀN ĐỎ
├── AGENTS.md                              # Chỉ thị dành cho AI Coding Assistant
└── README.md                              # Tài liệu giới thiệu dự án (file này)
```

---

## 6. HƯỚNG DẪN CÀI ĐẶT & THỰC THI NHANH

### 6.1. Cài đặt môi trường
Khuyến nghị sử dụng Python 3.10 trở lên:
```bash
pip install numpy opencv-python scipy scikit-image matplotlib streamlit
```

### 6.2. Chạy pipeline xử lý trên tập ảnh mẫu
```bash
python course_cv/main.py --input_dir data/sample --output_dir outputs_slide
```

### 6.3. Khởi chạy Ứng dụng Giao diện Web Streamlit (Demo tương tác)
```bash
streamlit run app.py
```
*(Nếu chưa có file `app.py`, TV1 sẽ triển khai theo thiết kế trong `docs/05`)*.
