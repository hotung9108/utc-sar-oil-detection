> **Tài liệu lịch sử:** nội dung dưới đây được giữ để tham khảo quá trình phát triển. Thuật toán, số liệu và demo hiện tại được mô tả trong [báo cáo chính](report/BAO_CAO_BTL_XLA.pdf), [README](../README.md) và [đối chiếu hiện tại](management/KIEM_TRA_HIEN_TAI.md). Không dùng các kết luận cũ để xác nhận phiên bản mới.

# CHƯƠNG 5: HƯỚNG DẪN CÀI ĐẶT & VẬN HÀNH HỆ THỐNG

> **Học phần**: Xử lý ảnh (Digital Image Processing - DIP) — Khoa CNTT, Đại học Giao thông Vận tải (UTC)  
> **Ứng dụng**: Web Studio Xử Lý Ảnh SAR Vi Ba Phát Hiện Vết Dầu Tràn & Bộ Công Cụ Kiểm Chuẩn

---

## 5.1. YÊU CẦU MÔI TRƯỜNG HỆ THỐNG

- **Hệ điều hành**: Windows 10/11, macOS, hoặc Ubuntu Linux 20.04+.
- **Ngôn ngữ lập trình**: Python 3.10, 3.11 hoặc 3.12 (khuyến nghị 3.11+).
- **Phần cứng đề xuất**:
  * CPU: Tối thiểu 4 nhân (Khuyến nghị 8–16 nhân để chạy benchmark song song nhanh chóng).
  * RAM: Tối thiểu 4 GB (Khuyến nghị 8 GB).
  * Ổ cứng trống: Tối thiểu 1.5 GB.

---

## 5.2. HƯỚNG DẪN CÀI ĐẶT

### Bước 1: Mở Terminal / PowerShell tại thư mục dự án
```powershell
cd D:\Codin\utc-code\HK4_1\XLA\BTL
```

### Bước 2: Tạo và kích hoạt môi trường ảo (Khuyên dùng)
```powershell
# Tạo môi trường ảo
python -m venv venv

# Kích hoạt môi trường ảo trên Windows PowerShell
.\venv\Scripts\Activate.ps1

# (Nếu trên Linux/macOS: source venv/bin/activate)
```

### Bước 3: Cài đặt các gói phụ thuộc tối thiểu
```powershell
pip install -r requirements.txt
```

> **Danh mục thư viện trong `requirements.txt`**:
> - `numpy`: Lõi ma trận xử lý ảnh số 100% tự lập trình.
> - `scipy`: Hỗ trợ dán nhãn thành phần liên thông nhanh `ndimage.label`.
> - `fastapi`, `uvicorn`: Web framework API hiệu năng cao.
> - `opencv-python`: Đọc/ghi ảnh (`cv2.imread`, `cv2.imwrite`) và kiểm chuẩn đối chứng.
> - `pandas`, `matplotlib`: Thống kê số liệu và vẽ biểu đồ khoa học.

---

## 5.3. HƯỚNG DẪN KHỞI CHẠY ỨNG DỤNG WEB STUDIO

### Cách 1: Sử dụng phím tắt tự động (Dành cho Windows)
Nhấp đúp chuột vào tệp:
```
run_app.bat
```
Tệp sẽ tự động kích hoạt môi trường Python, khởi chạy server FastAPI và tự động mở trình duyệt web tại địa chỉ `http://127.0.0.1:8000`.

### Cách 2: Chạy thủ công bằng dòng lệnh Terminal
```powershell
python app.py
```
Sau đó mở trình duyệt (Chrome, Edge, Firefox) và truy cập:
```
http://127.0.0.1:8000
```

---

## 5.4. HƯỚNG DẪN SỬ DỤNG GIAO DIỆN WEB STUDIO

Giao diện được thiết kế trực quan theo phong cách **Tối giản (Minimalism) với Canvas 2x2 lớn**:

1. **Chọn ảnh đầu vào**:
   - Nhấp vào thanh chọn ảnh (hoặc ảnh thumbnail trong gallery) để chọn một trong các ảnh SAR có vệt dầu thực tế (`oil_slick_01.jpg` đến `oil_slick_05.jpg`) hoặc ảnh biển sạch (`sea_surface_01.jpg` đến `sea_surface_05.jpg`).
2. **Cấu hình chuỗi xử lý DIP**:
   - **Lọc đốm**: Chọn `Lee MMSE Filter` (Khuyên dùng cho SAR) với kích thước cửa sổ 5x5 hoặc 7x7.
   - **Tăng cường tương phản**: Chọn `CLAHE` (Clip limit = 2.0, Grid = 8x8).
   - **Làm nét**: Chọn `Unsharp Masking` (k = 0.50).
   - **Xử lý biên**: Chọn **`Bộc Lộ Ranh Giới Vết Dầu Hình Thái Học beta(A) (Chương 6 & 7 - Khuyên dùng)`**.
3. **Quan sát kết quả trên lưới 2x2 Z-Pattern**:
   - **Ô 1 (Hàng 1, Trái)**: `1. Ảnh SAR Gốc` mang nhiễu đốm hạt tiêu.
   - **Ô 2 (Hàng 1, Phải)**: `2. Sau Khử Đốm & Tăng Cường` (Lee + CLAHE) làm phẳng biển và mở rộng tương phản.
   - **Ô 3 (Hàng 2, Trái)**: `3. Bộc Lộ Ranh Giới Vết Dầu` hiển thị đường bao $\beta(A)$ đỏ rực 1px ôm khít mảng dầu thật.
   - **Ô 4 (Hàng 2, Phải)**: `4. Bản Đồ Vi Sai Tác Động` ($|\Delta I| \times 2$) thể hiện rõ nơi thuật toán can thiệp.
4. **Tính năng Phóng to ảnh (Lightbox Zoom Modal)**:
   - Nhấp chuột trực tiếp vào bất kỳ ô ảnh nào trong 4 ô để mở modal xem toàn màn hình ở độ phân giải gốc. Nhấn `ESC` hoặc nhấp nút `X` để đóng.
5. **Theo dõi Bảng Thống Kê Đặc Trưng Vết Dầu Tràn (Chuẩn NASA Đề 18)**:
   - Xem ngay các thông số thời gian thực: Số vết dầu ($N$), Tổng diện tích ($px$ và $\%$), Tỷ số tương phản nền biển ($C_R$), Ngưỡng Otsu ($T^*$) và Hệ số khả tách ($\eta$).

---

## 5.5. HƯỚNG DẪN CHẠY BỘ KIỂM CHUẨN TOÁN HỌC & ĐỐI CHUẨN OPENCV

Để chạy bộ kiểm tra 5 bài toán tính tay mẫu $8 \times 8$ và đối chuẩn với OpenCV phục vụ bảo vệ đồ án:
```powershell
python -m src.verification
```
Hệ thống sẽ in toàn bộ bảng ma trận, các bước tính CDF, hệ số $K$ của Lee, đạo hàm Sobel, các phép co/giãn/trích biên $\beta(A)$ và khẳng định sai số $= 0$.

---

## 5.6. HƯỚNG DẪN CHẠY CHUỖI 5 THỬ NGHIỆM ĐỊNH LƯỢNG KHOA HỌC

Để tự động chạy chuỗi 5 thử nghiệm, sinh lại toàn bộ file số liệu CSV trong `results/tables/` và biểu đồ khoa học trong `results/figures/`:
```powershell
python run_experiments.py
```

---

## 5.7. HƯỚNG DẪN CHẠY BENCHMARK QUÉT TOÀN BỘ DATASET (1.853 ẢNH)

Để kích hoạt quét song song đa tiến trình trên toàn bộ 1.853 ảnh dataset:
```powershell
python evaluate_all_edges.py
```
- Thời gian chạy: Khoảng **~60 giây** trên CPU 8-16 nhân.
- Kết quả xuất ra:
  * File CSV chi tiết 1.853 dòng: `results/edge_evaluation_output/full_dataset_edge_benchmark.csv`.
  * Báo cáo Markdown: `results/edge_evaluation_output/EVALUATION_REPORT.md`.
  * Thư mục ảnh chẩn đoán 4 khung hình: `results/edge_evaluation_output/flagged_deviations/`.
