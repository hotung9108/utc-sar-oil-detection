# BÀI TẬP LỚN XỬ LÝ ẢNH (DIP) — KHOA CNTT, UTC
## ĐỀ TÀI: TĂNG CƯỜNG ĐỘ TƯƠNG PHẢN VÀ KHỬ NHIỄU ẢNH RADAR SAR BỘC LỘ VẾT DẦU TRÀN TRÊN BIỂN
**Chuyên đề**: **Nhóm A — Tăng cường và lọc ảnh (Image Enhancement & Filtering)**  
**Giảng viên hướng dẫn**: TS. Phan Thanh Toàn, TS. Cao Thị Luyên  
**Bộ môn**: Khoa học Máy tính & Công nghệ Phần mềm — Trường Đại học Giao thông Vận tải (UTC)  
**Tập dữ liệu**: Sentinel-1 SAR Oil Spill Dataset (NASA Earth Science / Kaggle)  
**Cam kết học thuật**: **100% Xử lý ảnh số kinh điển (No ML / No DL)**. Không sử dụng mạng nơ-ron, SVM, k-NN hay ma trận nhầm lẫn phân lớp. Toàn bộ thuật toán cốt lõi tự cài đặt bằng Pure NumPy và đối chứng kiểm chuẩn khoa học.

---

## 📌 1. Cấu Trúc Thư Mục Dự Án

```text
BTL/
├── app.py                      # Máy chủ Web App (FastAPI + REST API xử lý mảng Pure NumPy)
├── run_app.bat                 # File thực thi click chạy nhanh ứng dụng Web trên Windows
├── run_experiments.py          # Script chạy 3 thử nghiệm khoa học độc lập (Chương 4)
├── requirements.txt            # Thư viện phụ thuộc (numpy, opencv-python, scipy, matplotlib, fastapi, uvicorn, pandas)
├── README.md                   # Hướng dẫn chi tiết cài đặt và sử dụng
├── static/                     # Giao diện Web SPA hiện đại (Single Page Application)
│   ├── index.html              # Bộ khung HTML5, Tailwind CSS, FontAwesome, Chart.js
│   └── js/
│       └── app.js              # Logic chọn ảnh, upload drag-drop, gọi API xử lý thời gian thực
├── data/
│   └── sample/                 # Bộ 10 ảnh SAR thử nghiệm chuẩn (5 Oil Slicks, 5 Sea Surface)
│       ├── oil_slicks/
│       └── sea_surface/
├── docs/
│   ├── THUAT_TOAN_SU_DUNG.md   # Tài liệu chi tiết cơ sở toán học & ánh xạ giáo trình UTC
│   └── 00_tai_lieu_goc/        # Slide bài giảng UTC và hướng dẫn BTL gốc
├── results/
│   ├── figures/                # Đồ thị trực quan hóa Thử nghiệm 1, 2, 3, 4, 5 (.png)
│   └── tables/                 # Bảng số liệu định lượng CSV Thử nghiệm 1, 2, 3, 4, 5
└── src/
    ├── edges.py                # Sobel, Prewitt, Roberts, LoG Zero-Crossing, Canny 4 bước, Edge Overlay (Pure NumPy)
    ├── enhancement.py          # Log Transform, Global HE, CLAHE, Homomorphic Filter (Pure NumPy)
    ├── filters.py              # Box, Gaussian, Median, Bilateral, Lee MMSE, Frost, Kuan (Pure NumPy)
    ├── morphology.py           # Phép Co/Giãn/Mở/Đóng, Trích biên beta(A), Phân đoạn Otsu, Lọc NASA CR (Pure NumPy)
    ├── sharpening.py           # Unsharp Masking, Laplacian, Sobel Edge Enhancement (Pure NumPy)
    ├── metrics.py              # ENL, SSI, RMS Contrast, Shannon Entropy, AMBE, EPI
    ├── utils.py                # Nạp ảnh, lưu ảnh, Difference Map, Profile Slice
    └── verification.py         # Kiểm chứng tính đúng: 5 ví dụ tính tay (8x8 HE, 5x5 Lee, 3x3 Sobel/Prewitt, 8x8 Morphology, 8x8 Otsu) & OpenCV
```

---

## 🚀 2. Hướng Dẫn Cài Đặt & Chạy Nhanh

### Bước 1: Kích hoạt môi trường Python (Python 3.10 - 3.13)
```bash
# Cài đặt các thư viện cần thiết
pip install -r requirements.txt
```

### Bước 2: Chạy kiểm chứng tính đúng đắn thuật toán (Verification)
Kiểm tra đối chiếu 5 ví dụ số tính tay (8x8 HE, 5x5 Lee MMSE, 3x3 Sobel/Prewitt, 8x8 Morphology, 8x8 Otsu) và so khớp kết quả với OpenCV:
```bash
python -m src.verification
```
*Kết quả:* Trùng khớp 100% với bài tập tính tay Slide 3.1, Slide Chương 5, Chương 6 và Chương 7 của UTC và đạt chuẩn MSE = 0 so với OpenCV.

### Bước 3: Chạy toàn bộ chuỗi 5 thử nghiệm khoa học (Experiments)
Thực thi đo lường định lượng và tự động xuất các bảng CSV và biểu đồ đồ thị chất lượng cao:
```bash
python run_experiments.py
```
- **Thử nghiệm 1**: Khảo sát 8 bộ lọc đốm (`experiment1_speckle_filters.csv`, `experiment1_speckle_comparison.png`).
- **Thử nghiệm 2**: Khảo sát siêu tham số CLAHE (`experiment2_clahe_survey.csv`, `experiment2_clahe_curves.png`).
- **Thử nghiệm 3**: Pipeline hoàn chỉnh & Lát cắt ngang Profile Slice (`experiment3_enhancement_summary.csv`, `experiment3_pipeline_showcase.png`, `experiment3_profile_slices.png`).
- **Thử nghiệm 4**: So sánh các bộ phát hiện biên Sobel, Prewitt, Roberts, LoG, Canny 4 bước & Phủ viền bộc lộ vết dầu (`experiment4_edge_comparison.csv`, `experiment4_edge_detection.png`).
- **Thử nghiệm 5**: Đối đầu Canny Gradient vs Ranh giới Hình thái học $\beta(A)$ kết hợp Phân đoạn Otsu & Lọc tỷ số tương phản NASA (`experiment5_morphological_oil_boundary.csv`, `experiment5_oil_boundary_comparison.png`).

### Bước 4: Khởi chạy Ứng dụng Web tương tác (SAR Enhancement Studio)
Bạn có thể khởi động theo 1 trong 2 cách cực kỳ thuận tiện:
- **Cách 1**: Chạy lệnh trực tiếp trong PowerShell / CMD:
  ```bash
  python app.py
  ```
- **Cách 2**: Double-click vào file **`run_app.bat`** trong thư mục dự án.

Ứng dụng sẽ tự động bật trình duyệt web tại địa chỉ: **`http://127.0.0.1:8000`**

Giao diện Web gồm 4 Tab nghiệp vụ:
1. **Phòng Thí Nghiệm Tương Tác (Interactive Studio)**:
   - **Bộ chọn ảnh đa năng**: Chọn ảnh mẫu trực tiếp qua lưới thumbnail (5 ảnh vết dầu, 5 ảnh mặt biển) hoặc bấm **"Tải Ảnh Từ Máy Tính"** (hỗ trợ JPG, PNG) để thử nghiệm ảnh SAR bất kỳ.
   - **Thanh trượt điều khiển thời gian thực**: Lọc đốm thích nghi (Lee, Bilateral, Frost, Kuan), tăng tương phản (CLAHE, HE, Log), làm nét (Unsharp Masking, Laplacian, Sobel) và vị trí lát cắt ngang $y$.
   - **Hiển thị so sánh 3 cột**: Ảnh gốc, Ảnh sau xử lý, Bản đồ sai số vi sai Difference Map.
   - **Đồ thị tương tác Chart.js**: So sánh phân bố Histogram mức xám và Đồ thị lát cắt ngang Profile Slice qua tâm vết dầu.
   - **Thẻ chỉ số định lượng thời gian thực**: ENL, SSI, RMS Contrast, Shannon Entropy, AMBE, EPI.
2. **Báo Cáo Thực Nghiệm (Chương 4)**: Xem toàn bộ số liệu và đồ thị của 3 thử nghiệm định lượng.
3. **Kiểm Chuẩn Toán Học & OpenCV**: Bảng so khớp tính tay $8 \times 8$ và sai số OpenCV.
4. **Cơ Sở Lý Thuyết UTC**: Trích dẫn công thức tán xạ Bragg, mô hình nhiễu nhân SAR và giải tích toán học.

---

## 📊 3. Bảng Tóm Tắt Kết Quả Định Lượng

### Thử nghiệm 1: Khử đốm SAR (Speckle Filtering)
- **Lee MMSE Filter (5x5, looks=4)**: Nâng chỉ số **ENL** từ $1760.82 \to 2321.16$ (làm phẳng mặt biển), hạ **SSI** xuống $0.9168$ ($< 1$ khử đốm tốt), tốc độ xử lý nhanh (**17.55 ms**).
- **Bilateral Filter (5x5)**: ENL đạt $2261.76$, SSI đạt $0.9305$, bảo toàn độ sắc nét của đường biên vết dầu.

### Thử nghiệm 2: Tăng cường tương phản CLAHE
- **CLAHE (clip_limit=2.0, grid=8x8)**: Nâng **RMS Contrast** từ $11.95 \to 19.89$, **Entropy thông tin** tăng từ $4.628 \to 5.828$ bits.
- **AMBE** chỉ ở mức $9.03$, bảo toàn độ sáng nền biển tự nhiên vượt trội so với Cân bằng toàn cục Global HE ($\text{AMBE} = 39.23$) và Biến đổi Log ($\text{AMBE} = 127.63$).

### Thử nghiệm 3: Chuỗi Pipeline Toàn diện (Raw $\to$ Lee Filter $\to$ CLAHE $\to$ Unsharp Masking)
- Đưa vết dầu tràn từ trạng thái mờ nhòe do nhiễu đốm thành vùng tối đen tách biệt hoàn toàn khỏi mặt biển.
- Đồ thị lát cắt ngang (**Profile Slice**) cho thấy đáy lòng vết dầu hạ thấp phẳng, thành biên dựng đứng sắc nhọn, chỉ số **EPI đạt 3.6449**.
