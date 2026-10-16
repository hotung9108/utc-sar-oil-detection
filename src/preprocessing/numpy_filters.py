"""
numpy_filters.py
================
Cài đặt thuần 100% bằng NumPy các bộ lọc không gian (Spatial Filters) phục vụ
tiền xử lý khử nhiễu đốm (Speckle Noise) trên ảnh Radar SAR Sentinel-1.

Tuân thủ nguyên tắc:
- Không sử dụng các hàm xử lý ảnh cấp cao của OpenCV (cv2.medianBlur, cv2.blur, cv2.filter2D...).
- Sử dụng các kỹ thuật vector hóa hiện đại của NumPy (strides / sliding_window_view).
- Hỗ trợ xử lý biên phản xạ đối xứng (Reflect Padding) chuẩn xác, bảo toàn năng lượng vùng biên.
- Tương thích cấu trúc bài giảng Xử lý ảnh - TS. Phan Thanh Toàn (ĐH Giao thông Vận tải).

Thành viên thực hiện: TV3 (Cài đặt thuật toán 1: Tiền xử lý & Phân đoạn).
"""

from typing import Union
import numpy as np


def custom_median_filter(
    image: np.ndarray,
    ksize: int = 5,
    mode: str = 'reflect'
) -> np.ndarray:
    """
    Bộ lọc trung vị 2D (Median Filter) cài đặt thuần NumPy 100%.

    Nguyên lý hoạt động (Bài giảng TS. Phan Thanh Toàn - Chương 3: Cải thiện ảnh):
    - Đây là bộ lọc phi tuyến (Non-linear filter) thuộc nhóm lọc thống kê thứ tự (Order-statistic filter).
    - Với mỗi vị trí pixel (r, c), trích xuất cửa sổ lân cận kích thước ksize x ksize:
      W(r, c) = { I(r + i, c + j) | -pad <= i, j <= pad }
    - Sắp xếp các phần tử trong cửa sổ theo thứ tự tăng dần và chọn giá trị chính giữa:
      I_filtered(r, c) = median(W(r, c))
    - Đặc tính vượt trội với ảnh SAR: Khử triệt để nhiễu đốm speckle và xung muối tiêu (salt-and-pepper)
      mà không làm mờ hay nhòe đường biên sắc nét của vết dầu (Edge-preserving).

    Kỹ thuật tối ưu hóa:
    - Xử lý biên bằng phản xạ đối xứng (mode='reflect'): d c b | a b c d | c b a,
      không làm méo tín hiệu biên như zero-padding (hạn chế viền đen nhân tạo quanh ảnh).
    - Sử dụng `np.lib.stride_tricks.sliding_window_view` để trích xuất toàn bộ cửa sổ
      trượt 2D dưới dạng strided view (không tốn bộ nhớ nhân bản).
    - Sử dụng `np.partition` trên trục cửa sổ phẳng với vị trí mid_idx = ksize^2 // 2.
      Thuật toán QuickSelect của `np.partition` đạt độ phức tạp trung bình O(K^2) cho mỗi pixel,
      nhanh hơn đáng kể so với việc sắp xếp toàn phần O(K^2 log(K^2)).

    Args:
        image: Mảng NumPy 2D chứa ảnh mức xám (thường là uint8 [0, 255] hoặc float).
        ksize: Kích thước cạnh của cửa sổ lọc vuông (phải là số nguyên dương lẻ: 3, 5, 7...). Mặc định 5.
        mode: Kiểu padding biên trong NumPy ('reflect', 'symmetric', 'edge'). Mặc định 'reflect'.

    Returns:
        np.ndarray: Ảnh sau lọc cùng kích thước và cùng kiểu dữ liệu (dtype) với ảnh đầu vào.

    Raises:
        ValueError: Nếu ảnh không phải 2D hoặc ksize không phải số nguyên dương lẻ.
    """
    if not isinstance(image, np.ndarray):
        raise TypeError("Input 'image' must be a numpy.ndarray.")
    if image.ndim != 2:
        raise ValueError(f"Input 'image' must be a 2D grayscale array, got shape {image.shape}.")
    if not isinstance(ksize, (int, np.integer)):
        raise TypeError("ksize must be an integer.")
    if ksize <= 0 or ksize % 2 == 0:
        raise ValueError(f"ksize must be a positive odd integer (e.g., 3, 5, 7), got {ksize}.")

    pad = ksize // 2
    # 1. Padding phản xạ đối xứng bảo toàn biên
    padded = np.pad(image, pad, mode=mode)

    # 2. Tạo strided view của toàn bộ các cửa sổ kích thước (ksize, ksize)
    # Shape view: (H, W, ksize, ksize) với memory footprint ban đầu = 0 byte cấp phát thêm
    windows = np.lib.stride_tricks.sliding_window_view(padded, (ksize, ksize))

    # 3. Chuyển đổi thành dạng (H, W, ksize*ksize) để trích trung vị
    h, w = image.shape
    num_elements = ksize * ksize
    mid_idx = num_elements // 2
    windows_flat = windows.reshape(h, w, num_elements)

    # 4. Lấy phần tử trung vị bằng thuật toán QuickSelect (np.partition)
    # Bảo toàn kiểu dữ liệu gốc (uint8 hoặc float) một cách tự nhiên
    median_values = np.partition(windows_flat, mid_idx, axis=-1)[..., mid_idx]

    return median_values.astype(image.dtype)


def custom_mean_filter(
    image: np.ndarray,
    ksize: int = 5,
    mode: str = 'reflect'
) -> np.ndarray:
    """
    Bộ lọc trung bình 2D (Mean / Box Filter) cài đặt thuần NumPy 100%.

    Nguyên lý hoạt động (Bài giảng TS. Phan Thanh Toàn - Chương 3: Cải thiện ảnh):
    - Là bộ lọc không gian tuyến tính (Linear Spatial Filter) cơ bản nhất.
    - Giá trị của mỗi pixel đầu ra bằng trung bình cộng cường độ của các pixel trong lân cận:
      I_filtered(r, c) = (1 / ksize^2) * sum_{i=-pad}^{pad} sum_{j=-pad}^{pad} I(r+i, c+j)
    - Nhược điểm đối với ảnh SAR: Làm mờ đáng kể các đường viền sắc nét của vệt dầu
      (khác với lọc trung vị bảo toàn biên). Thường được dùng làm đối chứng hiệu năng.

    Kỹ thuật tối ưu hóa O(1) bằng Bảng diện tích tích lũy (Summed Area Table / Integral Image):
    - Tích lũy 2D bằng `cumsum`: SAT(r, c) = sum_{i=0}^r sum_{j=0}^c Padded(i, j).
    - Tính tổng của bất kỳ cửa sổ hình chữ nhật nào chỉ bằng 4 phép truy xuất ma trận:
      Sum = SAT(r2, c2) - SAT(r1-1, c2) - SAT(r2, c1-1) + SAT(r1-1, c1-1).
    - Độ phức tạp thời gian đạt O(1) trên mỗi pixel (O(M*N) toàn ảnh), hoàn toàn độc lập với ksize!

    Args:
        image: Mảng NumPy 2D chứa ảnh mức xám (uint8 hoặc float).
        ksize: Kích thước cạnh của cửa sổ lọc vuông (số nguyên dương lẻ). Mặc định 5.
        mode: Kiểu padding biên trong NumPy ('reflect', 'symmetric', 'edge'). Mặc định 'reflect'.

    Returns:
        np.ndarray: Ảnh sau lọc cùng kích thước và dtype với ảnh đầu vào.

    Raises:
        ValueError: Nếu ảnh không phải 2D hoặc ksize không hợp lệ.
    """
    if not isinstance(image, np.ndarray):
        raise TypeError("Input 'image' must be a numpy.ndarray.")
    if image.ndim != 2:
        raise ValueError(f"Input 'image' must be a 2D grayscale array, got shape {image.shape}.")
    if not isinstance(ksize, (int, np.integer)):
        raise TypeError("ksize must be an integer.")
    if ksize <= 0 or ksize % 2 == 0:
        raise ValueError(f"ksize must be a positive odd integer, got {ksize}.")

    is_uint8 = (image.dtype == np.uint8)
    img_work = image.astype(np.float64)

    pad = ksize // 2
    # 1. Padding phản xạ đối xứng
    padded = np.pad(img_work, pad, mode=mode)

    # 2. Xây dựng Bảng diện tích tích lũy (Integral Image) có viền 0 ở trên và bên trái
    # sat shape: (H + 2*pad + 1, W + 2*pad + 1)
    sat = np.pad(padded.cumsum(axis=0).cumsum(axis=1), ((1, 0), (1, 0)), mode='constant', constant_values=0.0)

    # 3. Tính tổng cửa sổ trượt qua 4 góc với độ phức tạp O(1) per pixel
    # Cửa sổ từ r đến r+ksize (chỉ số SAT tương ứng)
    window_sum = (
        sat[ksize:, ksize:]
        - sat[:-ksize, ksize:]
        - sat[ksize:, :-ksize]
        + sat[:-ksize, :-ksize]
    )

    # 4. Tính giá trị trung bình cộng
    filtered = window_sum / float(ksize * ksize)

    if is_uint8:
        return np.clip(np.round(filtered), 0, 255).astype(np.uint8)
    return filtered.astype(image.dtype)
