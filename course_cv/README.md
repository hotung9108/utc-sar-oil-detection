# HỆ THỐNG PHÁT HIỆN VẾT DẦU TRÀN TỪ ẢNH SAR (SENTINEL-1)
## TUÂN THỦ 100% BÀI GIẢNG MÔN XỬ LÝ ẢNH — ĐẠI HỌC GIAO THÔNG VẬN TẢI (UTC)
**Giảng viên:** TS. Phan Thanh Toàn  
**Đề tài số 18:** Phát hiện vết dầu tràn trên biển từ ảnh SAR (★★★) — NASA #6  
**Thư mục làm việc độc lập:** `course_cv/`

---

## 1. NGUYÊN TẮC THIẾT KẾ ĐỘC LẬP & TÁCH BIỆT
Chương trình trong thư mục này được xây dựng **hoàn toàn độc lập** với tất cả các mã nguồn trước đây, tuân thủ nghiêm ngặt các tiêu chí học thuật của môn học:
1. **100% Computer Vision truyền thống**: Không sử dụng mô hình học máy (Machine Learning / Deep Learning).
2. **100% Nội dung trong giáo trình & slide của TS. Phan Thanh Toàn**:
   - Không dùng các bộ lọc ngoài giáo trình (không dùng Lee Filter, Kuan, Frost...).
   - Chỉ sử dụng các thuật toán được dạy trực tiếp trong các slide bài giảng Chương 3, Chương 5, Chương 6 và Chương 7.
3. **Trực quan hóa chuẩn mực**:
   - Chỉ hiển thị **đường viền ĐỎ** ôm sát vệt dầu phát hiện được theo đúng công thức trích biên hình thái học $\beta(A) = A - (A \ominus B)$.
   - Tuyệt đối **không vẽ khung chữ nhật, không vẽ bounding box, không gắn nhãn chữ/badge**.

---

## 2. BẢNG ÁNH XẠ THUẬT TOÁN VỚI SLIDE BÀI GIẢNG

| Bước thực hiện | File mã nguồn | Chương trong giáo trình | Thuật toán & Trang slide | Mục đích & Ý nghĩa trong xử lý ảnh SAR |
| :--- | :--- | :--- | :--- | :--- |
| **Bước 1: Tiền xử lý** | [`step1_filter.py`](file:///D:/Codin/utc-code/HK4_1/XLA/BTL/course_cv/step1_filter.py) | **Chương 3**: Cải thiện và phục hồi ảnh | - Lọc trung vị (*Median Filter*), Slide P104-106<br>- Lọc trung bình (*Mean/Box Filter*), Slide P94-99<br>- Cân bằng Histogram (*Hist Eq*), Slide P54-65 | Khử nhiễu đốm đục hạt (*speckle noise*) đặc trưng của radar SAR mà vẫn giữ nguyên độ sắc nét của đường biên vệt dầu |
| **Bước 2: Phân vùng** | [`step2_segmentation.py`](file:///D:/Codin/utc-code/HK4_1/XLA/BTL/course_cv/step2_segmentation.py) | **Chương 7**: Phân vùng ảnh | - Ngưỡng tối ưu Otsu (*Otsu's Thresholding*), Slide P48-55<br>- Hệ số khả tách $\eta = \frac{\sigma_B^2}{\sigma_T^2}$, Slide P52<br>- Ngưỡng thích nghi cục bộ (*Mean Adaptive*), Slide P29-36 | Phân tách tự động vệt dầu tối màu (pixel có độ phản xạ thấp) khỏi nền biển sáng hơn mà không cần gán ngưỡng thủ công |
| **Bước 3: Hình thái học** | [`step3_morphology.py`](file:///D:/Codin/utc-code/HK4_1/XLA/BTL/course_cv/step3_morphology.py) | **Chương 6**: Xử lý hình thái học | - Phần tử cấu trúc (*Structuring Element* $B$), Slide P7<br>- Phép mở (*Opening* $A \circ B$), Slide P18<br>- Phép đóng (*Closing* $A \bullet B$), Slide P20<br>- Phép co (*Erosion* $A \ominus B$), Slide P8<br>- Trích biên hình thái: $\beta(A) = A - (A \ominus B)$, Slide P16 | - Mở để xóa bọt sóng li ti.<br>- Đóng để nối liền thân dầu bị đứt.<br>- Lấp lỗ thủng (*Fill holes*).<br>- Trích đường biên chuẩn toán học đơn pixel. |
| **Bước 4: Đạo hàm biên** | [`step4_edge_gradient.py`](file:///D:/Codin/utc-code/HK4_1/XLA/BTL/course_cv/step4_edge_gradient.py) | **Chương 5**: Phân tích ảnh & Xử lý đường biên | - Toán tử Sobel ($G_x, G_y$), Slide P36-40<br>- Toán tử Prewitt ($P_x, P_y$), Slide P30-34<br>- Độ lớn Gradient $M(x,y) = \sqrt{G_x^2 + G_y^2}$ | Đo độ sắc nét của ranh giới giữa vết dầu và nền nước biển; đánh giá độ tương phản vành khuyên ngoại vi |
| **Tích hợp Pipeline** | [`pipeline.py`](file:///D:/Codin/utc-code/HK4_1/XLA/BTL/course_cv/pipeline.py) | Cả 4 chương | Kết nối 4 bước tuần tự thành quy trình khép kín | Đầu vào là ảnh gốc $\rightarrow$ Đầu ra là ảnh với viền đỏ chuẩn ôm sát vệt dầu |

---

## 3. HƯỚNG DẪN THỰC THI

### 3.1. Chạy trên Python
1. **Chạy thử nghiệm trên tập ảnh mẫu (`data/sample`):**
   ```bash
   python course_cv/main.py --input_dir data/sample --output_dir outputs_slide
   ```
2. **Chạy trên toàn bộ dữ liệu đầy đủ (`data/`):**
   ```bash
   python course_cv/main.py --input_dir data --output_dir outputs_slide_full
   ```
3. **Tùy chỉnh các tham số theo nhu cầu:**
   - `--min_area`: Diện tích tối thiểu của vùng dầu (mặc định 150 pixel).
   - `--min_contrast`: Độ tương phản tối thiểu giữa vết dầu và nền biển lân cận (mặc định 12 mức xám).
   - `--min_boundary_grad`: Ngưỡng gradient Sobel tối thiểu tại đường biên (mặc định 6.0).

### 3.2. Chạy trên MATLAB
Chương trình cung cấp script MATLAB hoàn chỉnh [`matlab_slide_pipeline.m`](file:///D:/Codin/utc-code/HK4_1/XLA/BTL/course_cv/matlab_slide_pipeline.m) sử dụng các hàm chuẩn của **Image Processing Toolbox**:
- `medfilt2(I, [5 5])`: Lọc trung vị (Chương 3).
- `[T, separability] = graythresh(I)`: Ngưỡng Otsu (Chương 7).
- `strel('disk', r)`, `imopen`, `imclose`, `imfill`, `bwareaopen`: Hình thái học (Chương 6).
- `imerode(A, B)` & `imsubtract(A, eroded)`: Trích biên hình thái $\beta(A)$ (Chương 6).
- `imgradientxy(I, 'sobel')`: Gradient Sobel (Chương 5).

Chạy trong cửa sổ lệnh MATLAB:
```matlab
cd course_cv
matlab_slide_pipeline('../data/sample', '../outputs_slide_matlab')
```
