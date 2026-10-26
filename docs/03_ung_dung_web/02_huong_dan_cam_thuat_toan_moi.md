# HƯỚNG DẪN CẮM THUẬT TOÁN TÙY CHỈNH VÀO GIAO DIỆN WEB
## Plugin System — Lập Trình Thuật Toán Mới Mà Không Cần Sửa Code Giao Diện
**Học phần:** Xử lý ảnh / Computer Vision — UTC

---

## 1. TỔNG QUAN KIẾN TRÚC PLUGIN

Hệ thống được thiết kế theo mô hình tách biệt hoàn toàn giữa **Giao diện người dùng (`web/app.py`)** và **Thuật toán xử lý (`src/`)**.

Tất cả các điểm cắm (hooks) để bạn tự viết code được tập trung tại một tệp duy nhất:  
👉 **`src/custom_algorithms.py`**

---

## 2. BA ĐIỂM CẮM CHÍNH (HOOKS)

### 2.1. Điểm cắm 1: Bộ lọc không gian mới (Custom Filter)
Mở file `src/custom_algorithms.py` và chỉnh sửa hàm `custom_filter_template`:
```python
def custom_filter_template(image: np.ndarray, param1: float = 1.0, param2: int = 5) -> np.ndarray:
    """
    image: Mảng numpy 2D mức xám uint8 [H, W]
    param1: Hệ số điều khiển thực (ví dụ: sigmaColor)
    param2: Kích thước cửa sổ lọc ksize (số lẻ)
    """
    # Viết giải thuật lọc của bạn ở đây:
    # Ví dụ: Lọc song phương Bilateral, lọc Kuan, lọc Wiener...
    filtered = cv2.bilateralFilter(image, d=param2, sigmaColor=param1 * 25.0, sigmaSpace=param2)
    return filtered
```
👉 **Cách kích hoạt:** Trên thanh bên trái của Web, tại mục **Bộ lọc speckle**, chọn `Custom Filter (src/custom_algorithms.py)`.

---

### 2.2. Điểm cắm 2: Thuật toán phân đoạn ngưỡng mới (Custom Thresholding)
Chỉnh sửa hàm `custom_threshold_template`:
```python
def custom_threshold_template(image: np.ndarray, k: float = -0.2, window_size: int = 31) -> np.ndarray:
    """
    Đầu vào: Ảnh xám sau lọc (uint8)
    Đầu ra: Mặt nạ nhị phân uint8 (255 cho đốm tối ứng viên, 0 cho nền biển)
    """
    # Ví dụ: Thuật toán Niblack thích nghi cục bộ
    # T(x,y) = mean(x,y) + k * std(x,y)
    img_f = image.astype(np.float64)
    kernel = np.ones((window_size, window_size)) / (window_size ** 2)
    local_mean = cv2.filter2D(img_f, -1, kernel)
    local_sq_mean = cv2.filter2D(img_f ** 2, -1, kernel)
    local_std = np.sqrt(np.maximum(0.0, local_sq_mean - local_mean ** 2))
    
    threshold = local_mean + k * local_std
    dark_mask = (img_f < threshold).astype(np.uint8) * 255
    return dark_mask
```
👉 **Cách kích hoạt:** Tại mục **Phân đoạn đốm tối**, chọn `Niblack thích nghi (Custom)`.

---

### 2.3. Điểm cắm 3: Quy tắc phân loại Heuristic mới (Custom Classifier)
Chỉnh sửa hàm `custom_heuristic_classifier`:
```python
def custom_heuristic_classifier(features: dict, user_weights: dict = None) -> tuple[bool, str]:
    """
    features nhận vào:
      - 'area': Diện tích pixel
      - 'elongation': Độ thuôn dài
      - 'boundary_complexity': Độ phức tạp biên
      - 'contrast_diff': Chênh lệch mức xám Delta mu
      - 'damping_ratio': Tỉ số suy giảm tán xạ
      - 'border_gradient': Gradient biên Sobel
    """
    area = features.get('area', 0)
    contrast = features.get('contrast_diff', 0.0)
    grad = features.get('border_gradient', 0.0)
    elongation = features.get('elongation', 1.0)
    
    # Định nghĩa quy tắc logic của bạn:
    if area >= 100 and contrast >= 12.0 and grad >= 5.0 and elongation >= 1.8:
        return True, "Thỏa mãn tiêu chuẩn vệt dầu theo quy tắc mới"
    return False, "Loại trừ hiện tượng tự nhiên look-alike"
```
👉 **Cách kích hoạt:** Mở mục **Hình thái học & Đặc trưng** $\rightarrow$ chọn `Tùy chỉnh (src/custom_algorithms.py)`.
