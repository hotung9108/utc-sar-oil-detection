"""
Module: step1_filter.py
Chuẩn theo: CHƯƠNG 3: CẢI THIỆN VÀ PHỤC HỒI ẢNH (Spatial Domain Filtering & Histogram)
Giáo trình: Xử lý ảnh - TS. Phan Thanh Toàn (Đại học Giao thông vận tải - UTC)

Các thuật toán sử dụng theo Slide:
- Lọc trung vị (Median Filter) - Slide P104-P106: Lọc thống kê thứ tự, khử nhiễu ngẫu nhiên/nhiễu muối tiêu
  và nhiễu đốm cực tốt mà ít làm nhòe biên hơn so với lọc trung bình.
- Lọc trung bình (Average/Mean Filter) - Slide P94-P99: Làm trơn ảnh bằng ma trận trọng số đều 1/(m*n).
- Cân bằng lược đồ mức xám (Histogram Equalization) - Slide P54-P65: Trải rộng lược đồ xám.
"""

import cv2
import numpy as np

def apply_median_filter(image: np.ndarray, ksize: int = 5) -> np.ndarray:
    """
    Lọc trung vị (Median Filtering) theo Slide Chương 3 (trang 104-106).
    Thay thế giá trị tại mỗi pixel bằng giá trị trung vị của các pixel lân cận.
    
    Tham số:
        image: Ảnh xám đầu vào (grayscale)
        ksize: Kích thước mặt nạ lẻ (3, 5, 7, mac dinh 5)
    Trả về:
        Ảnh sau lọc trung vị, giảm nhiễu hạt và giữ sắc nét đường biên.
    """
    return cv2.medianBlur(image, ksize)

def apply_average_filter(image: np.ndarray, ksize: int = 5) -> np.ndarray:
    """
    Lọc trung bình (Averaging / Box Filter) theo Slide Chương 3 (trang 94-99).
    Hệ số mặt nạ: 1 / (ksize * ksize).
    """
    return cv2.blur(image, (ksize, ksize))

def apply_histogram_equalization(image: np.ndarray) -> np.ndarray:
    """
    Cân bằng Histogram theo Slide Chương 3 (trang 54-65).
    Trải rộng phân bố mức xám ra toàn bộ khoảng [0, 255].
    """
    return cv2.equalizeHist(image)
