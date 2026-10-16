"""
Kịch bản Kiểm thử Toàn diện cho Module Hình thái học & Trích xuất Đặc trưng thuần NumPy.
Tác giả: TV4 - Đồ án Xử lý ảnh TS. Phan Thanh Toàn (UTC).
"""

import os
import sys

try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

import numpy as np
import cv2

# Thêm thư mục gốc vào PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src.morphology.numpy_morphology import (
    get_structuring_element,
    custom_erode,
    custom_dilate,
    custom_open,
    custom_close,
    custom_fill_holes,
    custom_extract_boundary,
    custom_connected_components,
)
from src.features.numpy_features import (
    custom_sobel_gradient,
    extract_blob_features,
    classify_candidate,
)

def test_morphology_mathematical_precision():
    print("=" * 60)
    print("1. KIỂM THỬ TÍNH ĐÚNG ĐẮN TOÁN HỌC CỦA TOÁN TỬ HÌNH THÁI HỌC")
    print("=" * 60)
    
    np.random.seed(123)
    dummy_mask = (np.random.rand(200, 200) > 0.65).astype(np.uint8) * 255
    se_rect3 = np.ones((3, 3), dtype=np.uint8)
    
    # 1.1 Kiểm tra custom_erode vs cv2.erode
    my_erode = custom_erode(dummy_mask, ksize=3)
    cv_erode = cv2.erode(dummy_mask, se_rect3, borderType=cv2.BORDER_CONSTANT, borderValue=255)
    max_err_erode = np.max(np.abs(my_erode.astype(int) - cv_erode.astype(int)))
    mse_erode = np.mean((my_erode.astype(float) - cv_erode.astype(float)) ** 2)
    print(f"[Erosion 3x3] Max Error: {max_err_erode:.2f} | MSE: {mse_erode:.4f} => {'PASSED' if max_err_erode == 0 else 'FAILED'}")
    
    # 1.2 Kiểm tra custom_dilate vs cv2.dilate
    my_dilate = custom_dilate(dummy_mask, ksize=3)
    cv_dilate = cv2.dilate(dummy_mask, se_rect3, borderType=cv2.BORDER_CONSTANT, borderValue=0)
    max_err_dilate = np.max(np.abs(my_dilate.astype(int) - cv_dilate.astype(int)))
    mse_dilate = np.mean((my_dilate.astype(float) - cv_dilate.astype(float)) ** 2)
    print(f"[Dilation 3x3] Max Error: {max_err_dilate:.2f} | MSE: {mse_dilate:.4f} => {'PASSED' if max_err_dilate == 0 else 'FAILED'}")
    
    # 1.3 Kiểm tra custom_open vs cv2.morphologyEx(MORPH_OPEN)
    my_open = custom_open(dummy_mask, ksize=3)
    cv_open = cv2.morphologyEx(dummy_mask, cv2.MORPH_OPEN, se_rect3)
    max_err_open = np.max(np.abs(my_open.astype(int) - cv_open.astype(int)))
    print(f"[Opening 3x3] Max Error: {max_err_open:.2f} => {'PASSED' if max_err_open == 0 else 'FAILED'}")
    
    # 1.4 Kiểm tra custom_close vs cv2.morphologyEx(MORPH_CLOSE)
    se_rect5 = np.ones((5, 5), dtype=np.uint8)
    my_close = custom_close(dummy_mask, ksize=5)
    cv_close = cv2.morphologyEx(dummy_mask, cv2.MORPH_CLOSE, se_rect5)
    max_err_close = np.max(np.abs(my_close.astype(int) - cv_close.astype(int)))
    print(f"[Closing 5x5] Max Error: {max_err_close:.2f} => {'PASSED' if max_err_close == 0 else 'FAILED'}")
    
    # 1.5 Kiểm tra custom_extract_boundary theo beta(A) = A - (A (-) B)
    my_boundary = custom_extract_boundary(dummy_mask, ksize=3)
    cv_boundary = cv2.subtract(dummy_mask, cv_erode)
    max_err_bnd = np.max(np.abs(my_boundary.astype(int) - cv_boundary.astype(int)))
    print(f"[Boundary beta(A)] Max Error: {max_err_bnd:.2f} => {'PASSED' if max_err_bnd == 0 else 'FAILED'}")
    
    # 1.6 Kiểm tra custom_fill_holes
    donut = np.zeros((100, 100), dtype=np.uint8)
    donut[20:80, 20:80] = 255
    donut[40:60, 40:60] = 0 # Lỗ thủng ở giữa
    filled = custom_fill_holes(donut)
    hole_filled = np.all(filled[40:60, 40:60] == 255)
    bg_preserved = np.all(filled[:20, :] == 0) and np.all(filled[80:, :] == 0)
    print(f"[Fill Holes] Hole is filled: {hole_filled} | Background preserved: {bg_preserved} => {'PASSED' if hole_filled and bg_preserved else 'FAILED'}")


def test_sobel_gradient_precision():
    print("\n" + "=" * 60)
    print("2. KIỂM THỬ TÍNH ĐÚNG ĐẮN CỦA TOÁN TỬ SOBEL GRADIENT")
    print("=" * 60)
    
    np.random.seed(456)
    dummy_img = np.random.randint(0, 256, (400, 400), dtype=np.uint8)
    
    # OpenCV Sobel với BORDER_DEFAULT (tức BORDER_REFLECT_101)
    cv_gx = cv2.Sobel(dummy_img.astype(np.float64), cv2.CV_64F, 1, 0, ksize=3, borderType=cv2.BORDER_REFLECT_101)
    cv_gy = cv2.Sobel(dummy_img.astype(np.float64), cv2.CV_64F, 0, 1, ksize=3, borderType=cv2.BORDER_REFLECT_101)
    cv_mag = np.sqrt(cv_gx**2 + cv_gy**2)
    
    my_gx, my_gy, my_mag = custom_sobel_gradient(dummy_img)
    
    err_gx = np.max(np.abs(my_gx - cv_gx))
    err_gy = np.max(np.abs(my_gy - cv_gy))
    err_mag = np.max(np.abs(my_mag - cv_mag))
    
    print(f"[Sobel Gx] Max Error: {err_gx:.6f} => {'PASSED' if err_gx < 1e-9 else 'FAILED'}")
    print(f"[Sobel Gy] Max Error: {err_gy:.6f} => {'PASSED' if err_gy < 1e-9 else 'FAILED'}")
    print(f"[Gradient Mag M(x,y)] Max Error: {err_mag:.6f} => {'PASSED' if err_mag < 1e-9 else 'FAILED'}")


def test_real_sar_detection():
    print("\n" + "=" * 60)
    print("3. CHẠY THỬ NGHIỆM TRÊN ẢNH MẪU SAR SENTINEL-1 THỰC TẾ")
    print("=" * 60)
    
    sample_files = [
        ("data/sample/Class_1/class_1_00001.jpg", "Vết dầu tràn thực tế (Class 1)"),
        ("data/sample/Class_1/class_1_00002.jpg", "Vết dầu tràn thực tế (Class 1)"),
        ("data/sample/Class_0/class_0_00001.jpg", "Vùng không chứa dầu / Look-alike (Class 0)"),
        ("data/sample/Class_0/class_0_00002.jpg", "Vùng không chứa dầu / Look-alike (Class 0)"),
    ]
    
    for path, desc in sample_files:
        if not os.path.exists(path):
            print(f"File {path} không tồn tại, bỏ qua.")
            continue
            
        print(f"\n--- Phân tích ảnh: {path} ({desc}) ---")
        img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
        h, w = img.shape
        
        # Bước lọc và phân ngưỡng Otsu thích nghi để tìm đốm tối
        # Otsu thuần NumPy:
        hist, _ = np.histogram(img.ravel(), bins=256, range=(0, 256))
        p = hist / img.size
        omega = np.cumsum(p)
        mu = np.cumsum(p * np.arange(256))
        mu_t = mu[-1]
        denom = omega * (1.0 - omega)
        numer = (mu_t * omega - mu) ** 2
        sigma_b_sq = np.zeros(256)
        valid = denom > 1e-9
        sigma_b_sq[valid] = numer[valid] / denom[valid]
        optimal_t = int(np.argmax(sigma_b_sq))
        
        raw_mask = (img <= optimal_t).astype(np.uint8) * 255
        
        # Bước hình thái học: Mở (loại bỏ nhiễu) -> Đóng (hàn gắn) -> Lấp lỗ thủng
        opened = custom_open(raw_mask, ksize=3)
        closed = custom_close(opened, ksize=5)
        filled = custom_fill_holes(closed)
        
        # Tách đốm liên thông
        num_blobs, labeled, blobs = custom_connected_components(filled, connectivity=8, min_area=100)
        print(f"Phát hiện {num_blobs} đốm tối ứng viên (diện tích >= 100 px).")
        
        # Tính trước gradient Sobel cho ảnh
        _, _, grad_mag = custom_sobel_gradient(img)
        
        scene_mean = float(np.mean(img))
        scene_dark_ratio = float(np.sum(filled > 0) / img.size)
        detected_oils = 0
        for i, b in enumerate(blobs):
            b_mask = b["blob_mask"]
            b_boundary = custom_extract_boundary(b_mask, ksize=3)
            
            features = extract_blob_features(
                image=img,
                blob_mask=b_mask,
                boundary_mask=b_boundary,
                all_dark_mask=filled,
                annulus_ksize=15,
                precomputed_grad_mag=grad_mag,
            )
            
            is_oil, label, decision = classify_candidate(
                features,
                min_area=120,
                max_area=25000,
                min_contrast=10.0,
                min_damping=1.25,
                min_gradient=5.0,
                min_elongation=1.8,
                min_complexity=1.6,
                scene_mean=scene_mean,
                scene_dark_ratio=scene_dark_ratio,
                max_dark_ratio=0.25,
                total_scene_blobs=num_blobs,
                max_scene_blobs=10,
            )
            
            print(f"  [Blob #{i+1}] Diện tích: {features['area']:.0f} px | Thuôn dài: {features['elongation']:.2f} | "
                  f"Phức tạp: {features['boundary_complexity']:.2f} | Gradient: {features['border_gradient']:.2f} | "
                  f"Delta_mu: {features['contrast_diff']:.2f} => {label}")
            if is_oil:
                detected_oils += 1
                
        print(f"=> Tổng kết: Phát hiện {detected_oils} vệt dầu tràn thực tế được xác nhận.")

if __name__ == "__main__":
    test_morphology_mathematical_precision()
    test_sobel_gradient_precision()
    test_real_sar_detection()
