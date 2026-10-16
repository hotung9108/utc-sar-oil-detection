"""
Module: pipeline.py
Pipeline phát hiện vết dầu tràn trên ảnh SAR tuân thủ 100% giáo trình Xử lý ảnh:
Giáo trình: TS. Phan Thanh Toàn (Đại học Giao thông vận tải - UTC)

Quy trình 4 bước chuẩn Slide:
1. Tiền xử lý (Chương 3): Lọc trung vị (Median Filter, ksize=5) khử nhiễu đốm speckle.
2. Phân vùng ảnh (Chương 7): Phân ngưỡng Otsu tối ưu (Otsu's Thresholding) tìm vùng tối tiềm năng.
   Đánh giá tính khả tách eta = sigma_B^2 / sigma_T^2 (Slide Chương 7 trang 52).
3. Xử lý hình thái học (Chương 6):
   - Phép Mở (Opening) loại bỏ nhiễu sóng nhỏ.
   - Phép Đóng (Closing) hàn gắn vết dầu đứt khúc.
   - Lấp lỗ trống (Hole filling).
   - Lọc diện tích tối thiểu và tối đa.
   - Trích xuất đường biên hình thái học: beta(A) = A - (A - B) (Slide Chương 6 trang 16).
4. Phân tích đường biên (Chương 5):
   - Toán tử Sobel tính độ dốc gradient ranh giới vết dầu.
   - Đánh giá độ tương phản với nền biển lân cận.
   - Vẽ đường biên MÀU ĐỎ ôm sát vết dầu trên ảnh gốc (không vẽ khung chữ nhật, không vẽ chữ).
"""

import cv2
import numpy as np
from typing import Tuple, List, Dict, Any

from course_cv.step1_filter import apply_median_filter
from course_cv.step2_segmentation import otsu_dark_thresholding
from course_cv.step3_morphology import (
    morphological_clean,
    fill_holes,
    filter_small_blobs,
    extract_morphological_boundary
)
from course_cv.step4_edge_gradient import compute_sobel_gradient, evaluate_candidate_edge_contrast

def detect_oil_spill_pipeline(
    image: np.ndarray,
    min_area: int = 150,
    max_area: int = 120000,
    min_contrast: float = 12.0,
    min_boundary_grad: float = 6.0,
    min_otsu_separability: float = 0.10,
    border_thickness: int = 2
) -> Tuple[np.ndarray, np.ndarray, List[Dict[str, Any]]]:
    """
    Hàm thực thi pipeline chuẩn Slide xử lý ảnh TS. Phan Thanh Toàn.
    
    Tham số:
        image: Ảnh gốc BGR hoặc Grayscale
        min_area: Diện tích tối thiểu của vệt dầu (px)
        max_area: Diện tích tối đa (px) tránh cắt toàn bộ ảnh
        min_contrast: Độ chênh lệch mức xám tối thiểu giữa nền biển và vệt dầu
        min_boundary_grad: Độ lớn gradient Sobel tối thiểu tại đường biên
        min_otsu_separability: Hệ số khả tách eta tối thiểu của Otsu (Slide C7 P52)
        border_thickness: Độ dày nét vẽ viền đỏ (px)
        
    Trả về:
        visualized_bgr: Ảnh gốc với đường viền MÀU ĐỎ tại vết dầu phát hiện được
        detected_mask: Mặt nạ nhị phân vùng dầu
        detections: Danh sách các đặc trưng vùng dầu phát hiện được
    """
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        vis_img = image.copy()
    else:
        gray = image.copy()
        vis_img = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)

    # -------------------------------------------------------------
    # BƯỚC 1: LỌC TRUNG VỊ KHỬ NHIỄU ĐỐM (CHƯƠNG 3 - Trang 104-106)
    # -------------------------------------------------------------
    filtered = apply_median_filter(gray, ksize=5)

    # -------------------------------------------------------------
    # BƯỚC 2: PHÂN VÙNG BẰNG NGƯỠNG TỐI ƯU OTSU (CHƯƠNG 7 - Trang 48-55)
    # -------------------------------------------------------------
    # Tính hệ số khả tách eta = sigma_B^2 / sigma_T^2 (Slide C7 P52)
    hist = cv2.calcHist([filtered], [0], None, [256], [0, 256]).ravel()
    total_pixels = filtered.size
    p = hist / total_pixels
    
    omega = np.cumsum(p)
    mu = np.cumsum(p * np.arange(256))
    mu_t = mu[-1]
    
    # sigma_T^2
    sigma_t_sq = np.sum(((np.arange(256) - mu_t) ** 2) * p)
    
    # sigma_B^2 cho mọi ngưỡng
    denominator = omega * (1.0 - omega)
    numerator = (mu_t * omega - mu) ** 2
    sigma_b_sq = np.zeros(256)
    valid_idx = denominator > 1e-9
    sigma_b_sq[valid_idx] = numerator[valid_idx] / denominator[valid_idx]
    
    optimal_t = int(np.argmax(sigma_b_sq))
    max_sigma_b = sigma_b_sq[optimal_t]
    separability = float(max_sigma_b / sigma_t_sq) if sigma_t_sq > 1e-6 else 0.0

    # Nếu ảnh có độ biến thiên quá nhỏ hoặc tính khả tách quá kém -> biển đồng nhất / không có vết tối tách biệt
    if separability < min_otsu_separability:
        # Không có đối tượng nào đạt chuẩn khả tách
        return vis_img, np.zeros_like(gray), []

    # Tạo mặt nạ vùng tối (ngưỡng Otsu phân lớp tối: pixel <= optimal_t)
    _, initial_mask = cv2.threshold(filtered, optimal_t, 255, cv2.THRESH_BINARY_INV)

    # -------------------------------------------------------------
    # BƯỚC 3: HÌNH THÁI HỌC LÀM SẠCH VÀ LẤP LỖ (CHƯƠNG 6 - Trang 18, 20)
    # -------------------------------------------------------------
    cleaned = morphological_clean(initial_mask, open_ksize=3, close_ksize=7)
    filled = fill_holes(cleaned)
    area_filtered = filter_small_blobs(filled, min_area=min_area)

    # -------------------------------------------------------------
    # BƯỚC 4: XÁC MINH GRADIENT BIÊN (CHƯƠNG 5) & VẼ VIỀN ĐỎ (CHƯƠNG 6 P16)
    # -------------------------------------------------------------
    num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(area_filtered, connectivity=8)
    
    final_oil_mask = np.zeros_like(gray)
    detections = []
    
    for l in range(1, num_labels):
        area = int(stats[l, cv2.CC_STAT_AREA])
        if area < min_area or area > max_area:
            continue
        
        blob_mask = np.zeros_like(gray)
        blob_mask[labels == l] = 255
        
        # Trích xuất đường biên hình thái học beta(A) = A - (A - B) (Slide Chương 6 P16)
        blob_boundary = extract_morphological_boundary(blob_mask, ksize=3)
        
        # Đánh giá tương phản và gradient biên (Chương 5)
        metrics = evaluate_candidate_edge_contrast(filtered, blob_mask, blob_boundary)
        
        contrast = metrics["contrast"]
        border_grad = metrics["mean_boundary_grad"]
        
        # Tiêu chuẩn vết dầu vật lý:
        # 1. Có độ tương phản rõ rệt với mặt biển xung quanh (dầu triệt tiêu sóng mao dẫn)
        # 2. Gradient ranh giới đủ sắc nét do sức căng bề mặt
        if contrast >= min_contrast and border_grad >= min_boundary_grad:
            final_oil_mask[blob_mask == 255] = 255
            detections.append({
                "label": l,
                "area": area,
                "contrast": round(contrast, 2),
                "mean_boundary_grad": round(border_grad, 2),
                "centroid": (float(centroids[l][0]), float(centroids[l][1]))
            })

    # Nếu có phát hiện dầu, trích toàn bộ biên hình thái và vẽ viền đỏ
    if np.sum(final_oil_mask) > 0:
        total_boundary = extract_morphological_boundary(final_oil_mask, ksize=3)
        
        # Làm nét viền đỏ nếu border_thickness > 1
        if border_thickness > 1:
            kernel_thick = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (border_thickness, border_thickness))
            total_boundary = cv2.dilate(total_boundary, kernel_thick)
            
        # Không vẽ ở 2 pixel mép ngoài ảnh
        total_boundary[0:2, :] = 0
        total_boundary[-2:, :] = 0
        total_boundary[:, 0:2] = 0
        total_boundary[:, -2:] = 0
        
        # Tô màu ĐỎ (BGR: [0, 0, 255]) lên ảnh gốc
        vis_img[total_boundary > 0] = [0, 0, 255]

    return vis_img, final_oil_mask, detections
