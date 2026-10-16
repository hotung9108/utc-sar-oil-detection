"""
Module: step4_edge_gradient.py
Chuẩn theo: CHƯƠNG 5: PHÂN TÍCH ẢNH & XỬ LÝ ĐƯỜNG BIÊN (Edge Detection & Gradient Operators)
Giáo trình: Xử lý ảnh - TS. Phan Thanh Toàn (Đại học Giao thông vận tải - UTC)

Các toán tử theo Slide:
- Toán tử Sobel (Slide P36-40):
  Sx = [[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]]
  Sy = [[-1, -2, -1], [ 0,  0,  0], [ 1,  2,  1]]
  Độ lớn Gradient: G = sqrt(Gx^2 + Gy^2) hoặc |Gx| + |Gy|
- Toán tử Prewitt (Slide P30-34):
  Px = [[-1, 0, 1], [-1, 0, 1], [-1, 0, 1]]
  Py = [[-1, -1, -1], [ 0,  0,  0], [ 1,  1,  1]]
- Đánh giá độ sắc nét đường biên (Border Sharpness) và độ tương phản với nền biển (Contrast).
"""

import cv2
import numpy as np

def compute_sobel_gradient(image: np.ndarray) -> np.ndarray:
    """
    Tính gradient ảnh bằng toán tử Sobel theo Slide Chương 5 (trang 36-40).
    
    Tham số:
        image: Ảnh xám đầu vào
    Trả về:
        gradient_magnitude: Ma trận độ lớn gradient chuẩn hóa kiểu float32
    """
    gx = cv2.Sobel(image, cv2.CV_32F, 1, 0, ksize=3)
    gy = cv2.Sobel(image, cv2.CV_32F, 0, 1, ksize=3)
    mag = cv2.magnitude(gx, gy)
    return mag

def compute_prewitt_gradient(image: np.ndarray) -> np.ndarray:
    """
    Tính gradient ảnh bằng toán tử Prewitt theo Slide Chương 5 (trang 30-34).
    """
    kernel_x = np.array([[-1, 0, 1],
                         [-1, 0, 1],
                         [-1, 0, 1]], dtype=np.float32)
    kernel_y = np.array([[-1, -1, -1],
                         [ 0,  0,  0],
                         [ 1,  1,  1]], dtype=np.float32)
    
    gx = cv2.filter2D(image.astype(np.float32), -1, kernel_x)
    gy = cv2.filter2D(image.astype(np.float32), -1, kernel_y)
    mag = np.sqrt(gx**2 + gy**2)
    return mag

def evaluate_candidate_edge_contrast(
    image: np.ndarray,
    candidate_mask: np.ndarray,
    boundary_mask: np.ndarray
) -> dict:
    """
    Đánh giá độ sắc nét đường biên và tương phản giữa vết tối và nền biển lân cận.
    
    Tham số:
        image: Ảnh xám gốc
        candidate_mask: Mặt nạ vùng tối (255 tại blob)
        boundary_mask: Mặt nạ đường biên beta(A) (255 tại biên)
    Trả về:
        dict chứa:
            - mean_boundary_grad: Gradient trung bình trên đường biên (độ sắc nét)
            - mean_blob: Cường độ sáng trung bình bên trong vết
            - mean_bg: Cường độ sáng trung bình của nền biển vành đai lân cận
            - contrast: Chênh lệch mức xám giữa nền và vết (mean_bg - mean_blob)
    """
    sobel_mag = compute_sobel_gradient(image)
    
    # 1. Gradient trung bình dọc theo đường biên beta(A)
    border_pts = boundary_mask > 0
    if np.sum(border_pts) > 0:
        mean_border_grad = float(np.mean(sobel_mag[border_pts]))
    else:
        mean_border_grad = 0.0

    # 2. Vành đai nền biển lân cận bằng phép giãn nở (Dilation - Slide Chương 6 P12)
    kernel_dilate = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (15, 15))
    dilated = cv2.dilate(candidate_mask, kernel_dilate)
    annulus_bg = cv2.subtract(dilated, candidate_mask)
    
    blob_pts = candidate_mask > 0
    bg_pts = annulus_bg > 0
    
    mean_blob = float(np.mean(image[blob_pts])) if np.sum(blob_pts) > 0 else 0.0
    mean_bg = float(np.mean(image[bg_pts])) if np.sum(bg_pts) > 0 else 0.0
    contrast = mean_bg - mean_blob
    
    return {
        "mean_boundary_grad": mean_border_grad,
        "mean_blob": mean_blob,
        "mean_bg": mean_bg,
        "contrast": contrast
    }
