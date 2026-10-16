"""
Pipeline Phát hiện Vết dầu tràn SAR thuần 100% bằng NumPy
Tuân thủ 100% Bài giảng Xử lý ảnh - TS. Phan Thanh Toàn (ĐH Giao thông Vận tải)
Chủ trì tích hợp: TV1 — Trưởng nhóm & Tích hợp hệ thống
Phối hợp thuật toán: TV3 (Lọc & Otsu) và TV4 (Hình thái học & Đặc trưng)

Quy trình 4 bước tuần tự:
1. Tiền xử lý (Chương 3): Lọc trung vị thuần NumPy khử nhiễu speckle.
2. Phân vùng (Chương 7): Ngưỡng Otsu tối ưu thuần NumPy + Hệ số khả tách eta >= 0.10.
3. Hình thái học (Chương 6): Opening, Closing, Fill holes, CCL và trích biên beta(A) = A - (A (-) B).
4. Phân tích biên & Phân loại vật lý (Chương 5): Sobel Gradient, Tương phản vành đai và bộ lọc Heuristic.
"""

import time
from typing import Tuple, List, Dict, Any
import numpy as np
import cv2

from src.preprocessing.numpy_filters import custom_median_filter
from src.preprocessing.numpy_otsu import custom_otsu_threshold
from src.morphology.numpy_morphology import (
    get_structuring_element,
    custom_open,
    custom_close,
    custom_fill_holes,
    custom_extract_boundary,
    custom_connected_components,
    custom_dilate
)
from src.features.numpy_features import (
    custom_sobel_gradient,
    extract_blob_features,
    classify_candidate
)


def detect_oil_spill_numpy(
    image: np.ndarray,
    ksize_filter: int = 5,
    min_area: int = 150,
    max_area: int = 120000,
    min_contrast: float = 12.0,
    min_boundary_grad: float = 6.0,
    min_otsu_separability: float = 0.10,
    border_thickness: int = 2
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, List[Dict[str, Any]], Dict[str, Any]]:
    """
    Thực thi toàn bộ pipeline 4 bước bằng 100% thuật toán NumPy thuần túy.
    
    Tham số:
        image: Ảnh xám hoặc ảnh màu BGR (np.ndarray)
        ksize_filter: Kích thước cửa sổ lọc trung vị (3, 5, 7)
        min_area: Diện tích tối thiểu của vệt dầu (px)
        max_area: Diện tích tối đa tránh chọn toàn bộ ảnh
        min_contrast: Độ chênh lệch mức xám tối thiểu giữa nền biển và vết dầu
        min_boundary_grad: Độ lớn gradient Sobel tối thiểu tại đường biên
        min_otsu_separability: Hệ số khả tách eta tối thiểu của Otsu
        border_thickness: Độ dày đường viền đỏ kết quả
        
    Trả về:
        vis_bgr: Ảnh trực quan với viền ĐỎ ôm sát vết dầu
        filtered_gray: Ảnh sau khi lọc trung vị
        final_oil_mask: Mặt nạ nhị phân vết dầu
        detections: Danh sách các đặc trưng vết dầu phát hiện được
        meta: Thống kê chi tiết (eta, optimal_t, thời gian xử lý ms)
    """
    t_start = time.time()
    
    # 0. Chuẩn bị ảnh xám
    if image.ndim == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        vis_bgr = image.copy()
    else:
        gray = image.copy()
        vis_bgr = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)

    # -------------------------------------------------------------
    # BƯỚC 1: LỌC TRUNG VỊ BẢO TOÀN BIÊN KHỬ NHIỄU SPECKLE (CHƯƠNG 3)
    # -------------------------------------------------------------
    t1_s = time.time()
    filtered = custom_median_filter(gray, ksize=ksize_filter, mode='reflect')
    t1_time = (time.time() - t1_s) * 1000

    # -------------------------------------------------------------
    # BƯỚC 2: PHÂN VÙNG BẰNG NGƯỠNG OTSU TỐI ƯU & TÍNH ETA (CHƯƠNG 7)
    # -------------------------------------------------------------
    t2_s = time.time()
    optimal_t, eta, dark_mask = custom_otsu_threshold(filtered)
    t2_time = (time.time() - t2_s) * 1000

    # Nếu hệ số khả tách eta < min_otsu_separability -> Biển đồng nhất / biển sạch
    if eta < min_otsu_separability:
        total_time = (time.time() - t_start) * 1000
        meta = {
            "optimal_t": optimal_t,
            "eta": round(eta, 4),
            "step1_ms": round(t1_time, 2),
            "step2_ms": round(t2_time, 2),
            "step3_ms": 0.0,
            "step4_ms": 0.0,
            "total_ms": round(total_time, 2),
            "status": "CLEAN_SEA_EARLY_STOP"
        }
        return vis_bgr, filtered, np.zeros_like(gray), [], meta

    # -------------------------------------------------------------
    # BƯỚC 3: HÌNH THÁI HỌC LÀM SẠCH VÀ LẤP LỖ TRỐNG (CHƯƠNG 6)
    # -------------------------------------------------------------
    t3_s = time.time()
    # 3.1 Opening xóa bọt sóng nhỏ (kernel 3x3)
    se3 = get_structuring_element(3, se_type="disk")
    se7 = get_structuring_element(7, se_type="disk")
    opened = custom_open(dark_mask, se=se3)
    # 3.2 Closing hàn gắn vết dầu đứt khúc (kernel 7x7)
    closed = custom_close(opened, se=se7)
    # 3.3 Lấp lỗ thủng bên trong thân vệt dầu
    filled = custom_fill_holes(closed)
    # 3.4 Phân tách liên thông (Connected Component Labeling)
    num_blobs, labeled_img, blobs = custom_connected_components(filled, connectivity=8, min_area=min_area)
    t3_time = (time.time() - t3_s) * 1000

    # -------------------------------------------------------------
    # BƯỚC 4: TÍNH ĐẶC TRƯNG & PHÂN LOẠI VẬT LÝ (CHƯƠNG 5)
    # -------------------------------------------------------------
    t4_s = time.time()
    # Đạo hàm Sobel toàn ảnh thuần NumPy
    gx, gy, grad_mag = custom_sobel_gradient(filtered)
    scene_mean = float(np.mean(filtered))
    scene_dark_ratio = float(np.sum(dark_mask > 0) / dark_mask.size)
    
    final_oil_mask = np.zeros_like(gray)
    detections = []
    
    for blob in blobs:
        area = blob["area"]
        if area > max_area:
            continue
            
        b_mask = (labeled_img == blob["label"]).astype(np.uint8) * 255
        
        # Trích biên hình thái học đơn pixel: beta(A) = A - (A (-) B) (Slide Chương 6 P16)
        b_boundary = custom_extract_boundary(b_mask, ksize=3)
        
        # Trích 4 đặc trưng phân biệt
        feats = extract_blob_features(filtered, b_mask, b_boundary, precomputed_grad_mag=grad_mag)
        
        # Phân loại ứng viên
        is_oil, label_name, details = classify_candidate(
            feats,
            min_area=min_area,
            max_area=max_area,
            min_contrast=min_contrast,
            min_gradient=min_boundary_grad,
            min_damping=1.25,
            scene_mean=scene_mean,
            scene_dark_ratio=scene_dark_ratio,
            total_scene_blobs=len(blobs)
        )
        
        if is_oil:
            final_oil_mask[b_mask == 255] = 255
            detections.append({
                "id": len(detections) + 1,
                "label": blob["label"],
                "area": area,
                "elongation": round(feats["elongation"], 2),
                "complexity": round(feats["boundary_complexity"], 2),
                "contrast": round(feats["contrast_diff"], 2),
                "damping_ratio": round(feats["damping_ratio"], 2),
                "mean_gradient": round(feats["border_gradient"], 2),
                "centroid": feats["centroid"]
            })
            
    # Vẽ viền ĐỎ ôm sát vết dầu
    if np.sum(final_oil_mask) > 0:
        total_boundary = custom_extract_boundary(final_oil_mask, ksize=3)
        if border_thickness > 1:
            se_thick = get_structuring_element(border_thickness * 2 - 1, "disk")
            total_boundary = custom_dilate(total_boundary, se=se_thick)
            
        # Không vẽ ở 2 pixel mép ngoài
        total_boundary[0:2, :] = 0
        total_boundary[-2:, :] = 0
        total_boundary[:, 0:2] = 0
        total_boundary[:, -2:] = 0
        
        vis_bgr[total_boundary > 0] = [0, 0, 255] # BGR Red

    t4_time = (time.time() - t4_s) * 1000
    total_time = (time.time() - t_start) * 1000

    meta = {
        "optimal_t": optimal_t,
        "eta": round(eta, 4),
        "step1_ms": round(t1_time, 2),
        "step2_ms": round(t2_time, 2),
        "step3_ms": round(t3_time, 2),
        "step4_ms": round(t4_time, 2),
        "total_ms": round(total_time, 2),
        "status": "OIL_DETECTED" if detections else "NO_OIL_CONFIRMED"
    }

    return vis_bgr, filtered, final_oil_mask, detections, meta
