# HƯỚNG DẪN KHỞI ĐỘNG VÀ VẬN HÀNH ỨNG DỤNG WEB
## Hệ Thống Phát Hiện Vết Dầu Tràn từ Ảnh SAR Sentinel-1 (Pure CV)

---

### 1. Khởi động nhanh (Quick Start)

Bạn có thể chạy ứng dụng web bằng **1 trong 3 cách** dưới đây:

#### Cách 1: Chạy file Batch 1-Click (Khuyên dùng trên Windows)
- Nhấp đúp chuột vào file:
  - `run_web.bat` (ở thư mục gốc dự án) **hoặc**
  - `web/run_web.bat` (trong thư mục `web/`)
- Cửa sổ dòng lệnh sẽ tự động khởi động máy chủ và mở trình duyệt tại:  
  👉 **`http://localhost:8501`**

#### Cách 2: Dòng lệnh PowerShell / Command Prompt (Từ thư mục gốc)
Mở terminal tại thư mục dự án và chạy:
```powershell
python -m streamlit run web/app.py
```

#### Cách 3: Chạy từ bên trong thư mục `web/`
```powershell
cd web
python -m streamlit run app.py
```

---

### 2. Cấu trúc thư mục ứng dụng Web (`web/`)

```
BTL/
├── web/
│   ├── app.py              # Mã nguồn giao diện Web chính (Streamlit Minimalist Luxury)
│   ├── run_web.bat         # File kích hoạt nhanh trong thư mục web
│   └── README.md           # Hướng dẫn chi tiết dành riêng cho Web
│
├── src/                    # Toàn bộ thuật toán xử lý ảnh thuần túy (Pure CV)
│   ├── pipeline_modular.py # Pipeline modular liên kết 4 công đoạn
│   ├── custom_algorithms.py# Nơi viết thêm các thuật toán tùy chỉnh
│   ├── preprocessing/      # Lọc Lee, Otsu, Sauvola, CLAHE
│   ├── morphology/         # Opening, Closing, Fill holes, trích biên
│   └── features/           # Đặc trưng hình học & gradient Sobel
│
├── data/                   # Dữ liệu ảnh radar SAR Sentinel-1
│   ├── sample/             # Ảnh mẫu kiểm thử nhanh (Class 0 & Class 1)
│   ├── Class_0/            # Ảnh không dầu / Look-alikes (gió lặng, màng sinh học)
│   └── Class_1/            # Ảnh có vết dầu loang thực tế
│
├── RUN_WEB.md              # File hướng dẫn này
└── run_web.bat             # File kích hoạt nhanh ở thư mục gốc
```

---

### 3. Cài đặt thư viện (Nếu sử dụng máy mới)

Nếu chạy trên máy tính mới hoặc môi trường ảo riêng, hãy đảm bảo đã cài các thư viện:
```powershell
pip install streamlit opencv-python numpy matplotlib pandas
```

---

### 4. Vận hành các tính năng trên giao diện Web

1. **Chọn ảnh kiểm thử:**
   - Tại thanh điều khiển bên trái, chọn **Thư viện mẫu** (chọn `Class 1` để xem vết dầu thực tế, hoặc `Class 0` để kiểm tra khả năng loại trừ đốm giả look-alike).
   - Hoặc chọn **Tải từ máy tính** để tải lên ảnh radar SAR bất kỳ (`.jpg`, `.png`, `.tif`).
2. **Tùy chỉnh thuật toán (Pure Computer Vision):**
   - **Bộ lọc Speckle:** Lựa chọn `Median Filter (Chương 3)`, `Lee Filter (Radar SAR)`, `Frost Filter`, v.v. Kèm tùy chọn bật/tắt CLAHE.
   - **Phân đoạn đốm tối:** Chọn `Otsu tối ưu`, `Sauvola thích nghi`, hoặc `Thống kê nền biển`.
   - **Hình thái học & Đặc trưng:** Điều chỉnh kernel Opening/Closing, ngưỡng diện tích `min_area`, tương phản $\Delta \mu$, gradient Sobel.
3. **Quan sát kết quả trực tiếp:**
   - **Thẻ trạng thái:** Báo động đỏ khi phát hiện dầu loang nguy hiểm hoặc thông báo xanh khi biển sạch.
   - **Chỉ số hiệu năng:** Thời gian xử lý (ms), tốc độ FPS, số lượng vết dầu, giá trị ngưỡng tối ưu $T^*$.
   - **Lưới 4 ảnh tuần tự:** Xem trực quan từ ảnh gốc $\rightarrow$ sau lọc $\rightarrow$ mặt nạ nhị phân $\rightarrow$ ảnh viền đỏ ôm sát vết dầu.
   - **Biểu đồ Histogram:** Phân tích phân bố cường độ tán xạ và vị trí cắt ngưỡng.
   - **Bảng đo đạc định lượng:** Xem diện tích (px), chu vi, độ thuôn dài, tương phản $\Delta \mu$, gradient biên.
   - **Tải xuống kết quả:** Tải file `.csv` số liệu, ảnh `.png` khoanh đỏ, hoặc mặt nạ nhị phân `.png`.

---

### 5. Cách tự thêm thuật toán của bạn vào Web

Để cắm thêm thuật toán mới, bạn mở tệp:  
👉 **`src/custom_algorithms.py`**

- **Thêm bộ lọc mới:** Chỉnh sửa hàm `custom_filter_template(...)`
- **Thêm thuật toán phân đoạn mới:** Chỉnh sửa hàm `custom_threshold_template(...)`
- **Thêm quy tắc phân loại mới:** Chỉnh sửa hàm `custom_heuristic_classifier(...)`

Sau khi lưu tệp, trên giao diện web chọn mục **Custom / Tùy chỉnh**, thuật toán mới sẽ chạy ngay lập tức.

---

### 6. Xử lý sự cố thường gặp (Troubleshooting)

- **Lỗi cổng 8501 bị chiếm (Port 8501 is already in use):**
  Chạy ứng dụng với cổng khác:
  ```powershell
  python -m streamlit run web/app.py --server.port 8502
  ```
- **Lỗi không nhận diện được lệnh `streamlit`:**
  Luôn sử dụng cú pháp tiền tố python:
  ```powershell
  python -m streamlit run web/app.py
  ```
- **Lỗi font chữ tiếng Việt trên console CMD:**
  Chạy lệnh `chcp 65001` trước khi chạy script (các file `.bat` đã tích hợp sẵn).
