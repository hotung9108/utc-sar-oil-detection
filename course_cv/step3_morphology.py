"""
Module: step3_morphology.py
Chuẩn theo: CHƯƠNG 6: XỬ LÝ HÌNH THÁI HỌC (Morphological Image Processing)
Giáo trình: Xử lý ảnh - TS. Phan Thanh Toàn (Đại học Giao thông vận tải - UTC)

Các thuật toán sử dụng theo Slide:
- Thành phần cấu trúc (Structuring Element B) - Slide P7
- Phép co (Erosion): A - B - Slide P8
- Phép giãn (Dilation): A + B - Slide P12
- Phép mở (Opening): A o B = (A - B) + B - Slide P18 (loại bỏ các đốm nhiễu sóng nhỏ)
- Phép đóng (Closing): A * B = (A + B) - B - Slide P20 (nối liền các đoạn vết dầu bị đứt khúc)
- Trích xuất đường biên hình thái học (Morphological Boundary Extraction) - Slide P16:
  beta(A) = A - (A - B) (Lấy tập A trừ đi ảnh sau phép co A - B để thu được đường biên hoàn hảo).
"""

import cv2
import numpy as np

def morphological_clean(binary_mask: np.ndarray, open_ksize: int = 3, close_ksize: int = 7) -> np.ndarray:
    """
    Làm sạch mặt nạ nhị phân bằng phép Mở (Opening) và phép Đóng (Closing)
    theo Slide Chương 6 (trang 18, 20).
    
    1. Opening (Mở): Xóa bỏ các đốm nhiễu li ti do sóng biển gây ra.
    2. Closing (Đóng): Hàn gắn các khoảng đứt gãy trên thân vết dầu do nhiễu đốm radar.
    """
    # 1. Phần tử cấu trúc (Structuring Element / Kernel) - Slide P7
    se_open = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (open_ksize, open_ksize))
    se_close = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (close_ksize, close_ksize))
    
    # Phép mở (A o B) - Slide P18
    opened = cv2.morphologyEx(binary_mask, cv2.MORPH_OPEN, se_open)
    
    # Phép đóng (A * B) - Slide P20
    closed = cv2.morphologyEx(opened, cv2.MORPH_CLOSE, se_close)
    
    return closed

def fill_holes(binary_mask: np.ndarray) -> np.ndarray:
    """
    Lấp lỗ trống bên trong vùng nhị phân (Hole Filling) bằng kỹ thuật bù ảnh
    và lan truyền nền (an toàn với biên ảnh có viền padding).
    """
    h, w = binary_mask.shape
    padded = cv2.copyMakeBorder(binary_mask, 1, 1, 1, 1, cv2.BORDER_CONSTANT, value=0)
    mask_ff = np.zeros((h + 4, w + 4), np.uint8)
    cv2.floodFill(padded, mask_ff, (0, 0), 255)
    padded_crop = padded[1:-1, 1:-1]
    filled = binary_mask | cv2.bitwise_not(padded_crop)
    return filled

def filter_small_blobs(binary_mask: np.ndarray, min_area: int = 120) -> np.ndarray:
    """
    Lọc bỏ các thành phần liên thông có diện tích nhỏ hơn ngưỡng tối thiểu.
    """
    num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(binary_mask, connectivity=8)
    output_mask = np.zeros_like(binary_mask)
    for l in range(1, num_labels):
        if stats[l, cv2.CC_STAT_AREA] >= min_area:
            output_mask[labels == l] = 255
    return output_mask

def extract_morphological_boundary(binary_mask: np.ndarray, ksize: int = 3) -> np.ndarray:
    """
    Trích xuất đường biên hình thái học theo đúng công thức Slide Chương 6 (trang 16):
        beta(A) = A - (A - B)
    Đường biên của tập A là hiệu của tập A trừ đi ảnh sau phép co (Erosion) của A.
    
    Tham số:
        binary_mask: Mặt nạ nhị phân của vết dầu (tập A)
        ksize: Kích thước phần tử cấu trúc B (mặc định 3x3)
    Trả về:
        boundary_mask: Mặt nạ đường biên đơn pixel ôm sát đối tượng.
    """
    se = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (ksize, ksize))
    
    # Phép co: A - B (Erosion) - Slide P8
    eroded = cv2.erode(binary_mask, se)
    
    # Đường biên: beta(A) = A - (A - B) - Slide P16
    boundary = cv2.subtract(binary_mask, eroded)
    
    # Khử 2 pixel mép ngoài ảnh để không vẽ khung viền chữ nhật bao quanh toàn ảnh
    boundary[0:2, :] = 0
    boundary[-2:, :] = 0
    boundary[:, 0:2] = 0
    boundary[:, -2:] = 0
    
    return boundary
