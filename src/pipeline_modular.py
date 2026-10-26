"""
MODULAR SAR OIL SPILL COMPUTER VISION PIPELINE
==============================================
Pipeline xử lý ảnh modular cho phép linh hoạt cấu hình và hoán đổi các thuật toán
ở từng giai đoạn (Lọc -> Phân ngưỡng -> Hình thái học -> Đặc trưng & Phân loại).
Tích hợp sẵn với cả NumPy thuần túy, OpenCV và các module tùy chỉnh do người dùng viết.
"""

import time
from typing import Dict, Any, Tuple, List
import numpy as np
import cv2

from src.preprocessing.speckle_filter import lee_filter, clahe_enhance
from src.preprocessing.numpy_filters import custom_median_filter, custom_mean_filter
from src.preprocessing.candidate_detector import adaptive_threshold_dark
from src.preprocessing.numpy_otsu import custom_otsu_threshold
from src.features.numpy_features import classify_candidate
from src.custom_algorithms import custom_filter_template, frost_filter_demo, custom_threshold_template, custom_heuristic_classifier


def run_modular_pipeline(
    image: np.ndarray,
    # Bước 1: Tiền xử lý
    filter_type: str = "Median Filter (Chương 3)",
    ksize_filter: int = 5,
    enable_clahe: bool = False,
    clahe_clip: float = 2.0,
    # Bước 2: Phân ngưỡng
    threshold_type: str = "Otsu tối ưu (Chương 7)",
    sauvola_k: float = 0.20,
    sauvola_win: int = 41,
    sea_stat_k: float = 1.8,
    min_otsu_eta: float = 0.08,
    # Bước 3: Hình thái học
    enable_opening: bool = True,
    open_ksize: int = 3,
    enable_closing: bool = True,
    close_ksize: int = 7,
    enable_fill_holes: bool = True,
    min_area: int = 120,
    max_area: int = 120000,
    # Bước 4: Tiêu chuẩn nhận diện
    classifier_mode: str = "Chuẩn Heuristic (Vật lý SAR)",
    min_contrast: float = 12.0,
    min_border_grad: float = 6.0,
    min_elongation: float = 1.8,
    min_damping: float = 1.25,
    border_thickness: int = 2
) -> Dict[str, Any]:
    """
    Thực thi pipeline tuần tự 4 bước và trả về chi tiết toàn bộ trạng thái trung gian.
    """
    t_start = time.time()
    
    # 0. Chuẩn bị ảnh xám
    if image.ndim == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        vis_bgr = image.copy()
    else:
        gray = image.copy()
        vis_bgr = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)

    step_times = {}

    # =========================================================================
    # BƯỚC 1: LỌC NHIỄU ĐỐM & TĂNG CƯỜNG TƯƠNG PHẢN (SPECKLE FILTERING)
    # =========================================================================
    t1_s = time.time()
    k = ksize_filter if ksize_filter % 2 == 1 else ksize_filter + 1
    
    if "Median" in filter_type:
        filtered = cv2.medianBlur(gray, k)
    elif "Lee" in filter_type:
        filtered = lee_filter(gray, window_size=k, cu=0.52)
    elif "Frost" in filter_type:
        filtered = frost_filter_demo(gray, window_size=k, damping_factor=2.0)
    elif "Gauss" in filter_type:
        filtered = cv2.GaussianBlur(gray, (k, k), 0)
    elif "Box" in filter_type:
        filtered = cv2.blur(gray, (k, k))
    elif "Tùy chỉnh" in filter_type or "Custom" in filter_type:
        filtered = custom_filter_template(gray, param1=1.5, param2=k)
    else:
        filtered = gray.copy()
        
    if enable_clahe:
        filtered = clahe_enhance(filtered, clip_limit=clahe_clip, tile_grid=(8, 8))
        
    step_times["filter_ms"] = (time.time() - t1_s) * 1000

    # =========================================================================
    # BƯỚC 2: PHÂN NGƯỠNG ĐỐM TỐI ỨNG VIÊN (THRESHOLDING / SEGMENTATION)
    # =========================================================================
    t2_s = time.time()
    optimal_t = None
    eta = None
    
    if "Otsu" in threshold_type:
        optimal_t, eta, dark_mask = custom_otsu_threshold(filtered)
        # Kiểm tra tính khả tách Otsu
        if eta < min_otsu_eta:
            total_time = (time.time() - t_start) * 1000
            return {
                "vis_bgr": vis_bgr,
                "filtered": filtered,
                "threshold_mask": np.zeros_like(gray),
                "morph_mask": np.zeros_like(gray),
                "final_oil_mask": np.zeros_like(gray),
                "detections": [],
                "step_times": step_times,
                "total_time_ms": total_time,
                "optimal_t": optimal_t,
                "eta": round(eta, 4),
                "status": "CLEAN_SEA_LOW_ETA",
                "status_text": f"Mặt biển đồng nhất / biển sạch (Hệ số khả tách Otsu η={eta:.3f} < {min_otsu_eta})"
            }
    elif "Sauvola" in threshold_type:
        swin = sauvola_win if sauvola_win % 2 == 1 else sauvola_win + 1
        dark_mask = adaptive_threshold_dark(filtered, window_size=swin, k=sauvola_k, min_std=6.0)
    elif "Niblack" in threshold_type or "Tùy chỉnh" in threshold_type or "Custom" in threshold_type:
        swin = sauvola_win if sauvola_win % 2 == 1 else sauvola_win + 1
        dark_mask = custom_threshold_template(filtered, k=-0.25, window_size=swin)
    elif "Thống kê" in threshold_type or "Sea Clutter" in threshold_type:
        mu_sea = float(np.mean(filtered))
        sigma_sea = float(np.std(filtered))
        t_stat = mu_sea - sea_stat_k * sigma_sea
        optimal_t = int(max(0, min(255, t_stat)))
        dark_mask = ((filtered < optimal_t).astype(np.uint8)) * 255
    else:
        # Fallback Otsu
        optimal_t, eta, dark_mask = custom_otsu_threshold(filtered)
        
    step_times["threshold_ms"] = (time.time() - t2_s) * 1000

    # =========================================================================
    # BƯỚC 3: XỬ LÝ HÌNH THÁI HỌC (MORPHOLOGICAL POST-PROCESSING)
    # =========================================================================
    t3_s = time.time()
    morph_mask = dark_mask.copy()
    
    # Opening
    if enable_opening and open_ksize > 1:
        se_open = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (open_ksize, open_ksize))
        morph_mask = cv2.morphologyEx(morph_mask, cv2.MORPH_OPEN, se_open)
        
    # Closing
    if enable_closing and close_ksize > 1:
        se_close = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (close_ksize, close_ksize))
        morph_mask = cv2.morphologyEx(morph_mask, cv2.MORPH_CLOSE, se_close)
        
    # Hole filling
    if enable_fill_holes:
        h, w = morph_mask.shape
        padded = cv2.copyMakeBorder(morph_mask, 1, 1, 1, 1, cv2.BORDER_CONSTANT, value=0)
        mask_ff = np.zeros((h + 4, w + 4), np.uint8)
        cv2.floodFill(padded, mask_ff, (0, 0), 255)
        morph_mask = morph_mask | cv2.bitwise_not(padded[1:-1, 1:-1])
        
    step_times["morphology_ms"] = (time.time() - t3_s) * 1000

    # =========================================================================
    # BƯỚC 4: TRÍCH XUẤT ĐẶC TRƯNG & PHÂN LOẠI HEURISTIC (CHƯƠNG 5 & 6)
    # =========================================================================
    t4_s = time.time()
    num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(morph_mask, connectivity=8)
    
    # Sobel gradient magnitude
    gx = cv2.Sobel(filtered.astype(np.float32), cv2.CV_32F, 1, 0, ksize=3)
    gy = cv2.Sobel(filtered.astype(np.float32), cv2.CV_32F, 0, 1, ksize=3)
    grad_mag = cv2.magnitude(gx, gy)
    
    scene_mean = float(np.mean(filtered))
    scene_dark_ratio = float(np.sum(morph_mask > 0) / morph_mask.size)
    total_scene_blobs = num_labels - 1
    
    se_annulus = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9))
    se_boundary = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    
    final_oil_mask = np.zeros_like(gray)
    detections = []
    
    for l in range(1, num_labels):
        area = int(stats[l, cv2.CC_STAT_AREA])
        if area < min_area or area > max_area:
            continue
            
        b_mask = (labels == l).astype(np.uint8) * 255
        
        # 1. Trích biên hình thái học: beta(A) = A - (A (-) B) (Chương 6)
        eroded = cv2.erode(b_mask, se_boundary)
        b_boundary = cv2.subtract(b_mask, eroded)
        perimeter = float(np.sum(b_boundary > 0))
        
        # 2. Vành đai biển lân cận (Annulus background)
        dilated = cv2.dilate(b_mask, se_annulus)
        annulus = cv2.subtract(dilated, b_mask)
        # Loại trừ các đốm tối khác trong vùng vành đai
        annulus = annulus & (~morph_mask)
        
        sea_pixels = filtered[annulus > 0]
        oil_pixels = filtered[b_mask > 0]
        
        mean_sea = float(np.mean(sea_pixels)) if len(sea_pixels) > 0 else float(np.mean(filtered))
        mean_oil = float(np.mean(oil_pixels)) if len(oil_pixels) > 0 else 0.0
        contrast = mean_sea - mean_oil
        damping_ratio = (mean_sea / (mean_oil + 1e-5)) if mean_oil > 0 else 2.0
        
        # 3. Gradient Sobel đường biên
        border_grad_pixels = grad_mag[b_boundary > 0]
        mean_grad = float(np.mean(border_grad_pixels)) if len(border_grad_pixels) > 0 else 0.0
        
        # 4. Đặc trưng hình học: Elongation & Complexity
        cx, cy = centroids[l]
        contours, _ = cv2.findContours(b_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        elongation = 1.0
        if contours and len(contours[0]) >= 5:
            try:
                ellipse = cv2.fitEllipse(contours[0])
                (ecx, ecy), (d1, d2), angle = ellipse
                major_axis = max(d1, d2)
                minor_axis = min(d1, d2)
                elongation = major_axis / (minor_axis + 1e-5)
            except Exception:
                rect = cv2.minAreaRect(contours[0])
                w_box, h_box = rect[1]
                elongation = max(w_box, h_box) / (min(w_box, h_box) + 1e-5) if min(w_box, h_box) > 0 else 1.0
        elif contours:
            rect = cv2.minAreaRect(contours[0])
            w_box, h_box = rect[1]
            elongation = max(w_box, h_box) / (min(w_box, h_box) + 1e-5) if min(w_box, h_box) > 0 else 1.0
            
        complexity = (perimeter ** 2) / (4.0 * np.pi * area + 1e-5)
        
        feature_dict = {
            "id": len(detections) + 1,
            "area": area,
            "perimeter": int(perimeter),
            "elongation": round(float(elongation), 2),
            "boundary_complexity": round(float(complexity), 2),
            "contrast_diff": round(float(contrast), 2),
            "damping_ratio": round(float(damping_ratio), 2),
            "border_gradient": round(float(mean_grad), 2),
            "centroid": (int(cx), int(cy))
        }
        
        # Đánh giá phân loại
        is_oil = False
        decision_reason = ""
        
        if "Tùy chỉnh" in classifier_mode or "Custom" in classifier_mode:
            is_oil, decision_reason = custom_heuristic_classifier(feature_dict)
        else:
            is_oil, decision_reason, _ = classify_candidate(
                feature_dict,
                min_area=min_area,
                max_area=max_area,
                min_contrast=min_contrast,
                min_damping=min_damping,
                min_gradient=min_border_grad,
                min_elongation=min_elongation,
                min_complexity=1.6,
                scene_mean=scene_mean,
                scene_dark_ratio=scene_dark_ratio,
                total_scene_blobs=total_scene_blobs
            )
                
        if is_oil:
            final_oil_mask[b_mask == 255] = 255
            feature_dict["status"] = "OIL_SLICK"
            feature_dict["reason"] = decision_reason
            detections.append(feature_dict)
            
    # Vẽ đường viền đỏ ôm sát vết dầu
    if np.sum(final_oil_mask) > 0:
        total_boundary = cv2.subtract(final_oil_mask, cv2.erode(final_oil_mask, se_boundary))
        if border_thickness > 1:
            k_thick = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (border_thickness * 2 - 1, border_thickness * 2 - 1))
            total_boundary = cv2.dilate(total_boundary, k_thick)
            
        # Tránh viền sát mép ảnh
        total_boundary[0:2, :] = 0
        total_boundary[-2:, :] = 0
        total_boundary[:, 0:2] = 0
        total_boundary[:, -2:] = 0
        
        vis_bgr[total_boundary > 0] = [0, 0, 255] # BGR Red
        
        # Đánh dấu số thứ tự vết dầu
        for d in detections:
            c_x, c_y = d["centroid"]
            cv2.putText(vis_bgr, f"#{d['id']}", (c_x + 5, c_y + 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1, cv2.LINE_AA)

    step_times["features_ms"] = (time.time() - t4_s) * 1000
    total_time = (time.time() - t_start) * 1000

    status_text = f"Cảnh báo: Phát hiện {len(detections)} vết dầu tràn ngoài khơi!" if detections else "Không phát hiện vệt dầu loang (Biển sạch hoặc đốm look-alike đã được loại trừ)"
    
    return {
        "vis_bgr": vis_bgr,
        "filtered": filtered,
        "threshold_mask": dark_mask,
        "morph_mask": morph_mask,
        "final_oil_mask": final_oil_mask,
        "detections": detections,
        "step_times": step_times,
        "total_time_ms": round(total_time, 2),
        "optimal_t": optimal_t,
        "eta": round(eta, 4) if eta is not None else None,
        "status": "OIL_DETECTED" if detections else "NO_OIL_CONFIRMED",
        "status_text": status_text
    }
