"""
Module: step2_segmentation.py
Chuẩn theo: CHƯƠNG 7: PHÂN VÙNG ẢNH (Image Segmentation by Thresholding)
Giáo trình: Xử lý ảnh - TS. Phan Thanh Toàn (Đại học Giao thông vận tải - UTC)

Các thuật toán sử dụng theo Slide:
- Lấy ngưỡng tối ưu Otsu (Otsu Thresholding) - Slide P48-P55:
  Tối đa hóa phương sai giữa các lớp (between-class variance):
  sigma_B^2(T) = w0 * w1 * (mu0 - mu1)^2
  Trong bài toán ảnh SAR biển: Phân tách tự động giữa vệt tối (dầu/look-alike) và nền biển.
- Lấy ngưỡng thích nghi cục bộ (Mean Adaptive Thresholding) - Slide P29-P36:
  T(x, y) = mean_block(x, y) - C
"""

import cv2
import numpy as np

def otsu_dark_thresholding(image: np.ndarray) -> tuple[int, np.ndarray]:
    """
    Phân ngưỡng tối ưu Otsu theo Slide Chương 7 (trang 48-55).
    Đặc thù SAR: Vết dầu tràn và vệt hấp thụ sóng là vùng tối (pixel có cường độ thấp).
    Áp dụng THRESH_BINARY_INV để các điểm tối được gán giá trị 255 (vùng đối tượng),
    còn nền biển sáng hơn được gán giá trị 0.
    
    Tham số:
        image: Ảnh xám đầu vào sau khi lọc
    Trả về:
        optimal_thresh: Giá trị ngưỡng tối ưu T tìm được
        binary_mask: Mặt nạ nhị phân phân đoạn vùng tối (0 và 255)
    """
    optimal_thresh, binary_mask = cv2.threshold(
        image, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU
    )
    return int(optimal_thresh), binary_mask

def mean_adaptive_dark_thresholding(image: np.ndarray, block_size: int = 45, C: float = 4.0) -> np.ndarray:
    """
    Phân ngưỡng thích nghi trung bình (Mean Adaptive Thresholding) theo Slide Chương 7 (trang 29-36).
    Ngưỡng tại mỗi điểm ảnh được tính bằng trung bình cục bộ trừ đi hằng số C.
    
    Tham số:
        image: Ảnh xám đầu vào
        block_size: Kích thước vùng lân cận (phải là số lẻ, ví dụ 35, 45, 55)
        C: Hằng số điều chỉnh ngưỡng
    Trả về:
        binary_mask: Mặt nạ nhị phân vùng tối
    """
    return cv2.adaptiveThreshold(
        image, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV, block_size, C
    )
