"""
tests/verify_correctness.py
===========================
Kịch bản Kiểm chứng Tính đúng đắn Toán học (Mathematical Verification Suite).
So sánh đối chiếu toàn diện 100% giữa các hàm tự viết thuần NumPy trong:
  - `src/preprocessing/numpy_filters.py` (custom_median_filter, custom_mean_filter)
  - `src/preprocessing/numpy_otsu.py`    (custom_otsu_threshold)
  - `src/morphology/numpy_morphology.py` (custom_erode, custom_dilate, custom_extract_boundary)
  - `src/features/numpy_features.py`     (custom_sobel_gradient)
với các hàm thư viện chuẩn của OpenCV:
  - `cv2.medianBlur`
  - `cv2.blur` (với cv2.BORDER_REFLECT_101)
  - `cv2.threshold` (với cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
  - `cv2.erode` (với cv2.BORDER_CONSTANT, borderValue=255)
  - `cv2.dilate` (với cv2.BORDER_CONSTANT, borderValue=0)
  - `cv2.subtract(A, cv2.erode(A))` (Toán tử trích biên beta(A) = A - (A (-) B))
  - `cv2.Sobel` (với cv2.BORDER_REFLECT_101)

Dữ liệu kiểm thử:
  1. Dữ liệu giả lập: Ma trận ngẫu nhiên (Uniform, Gaussian, Binary Shapes) kích thước 100x100 và 400x400.
  2. 10 ảnh mẫu SAR thực tế từ CSIRO Dataset:
     - 5 ảnh Class 0 (Không chứa dầu / Look-alike)
     - 5 ảnh Class 1 (Vết dầu loang thực tế)

Chỉ số đo đạc:
  - Max Absolute Error: max |Output_NumPy - Output_OpenCV|
  - Mean Squared Error (MSE): 1/N * sum (Output_NumPy - Output_OpenCV)^2
  - Thời gian thực thi (Runtime in ms) đo bằng time.perf_counter()
  - Trạng thái kiểm thử (PASSED: Max Error = 0.00)

Thành viên thực hiện: TV2 (Lý thuyết toán học & Kiểm chứng tính đúng).
Đối chiếu với Mục 3.5 trong Báo cáo LaTeX (report_latex/chapters/03_methodology.tex).
"""

import os
import sys
import glob
import time
import unittest
from typing import Dict, List, Tuple, Any

# Thêm thư mục gốc vào PYTHONPATH
WORKSPACE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if WORKSPACE_DIR not in sys.path:
    sys.path.insert(0, WORKSPACE_DIR)

# Thiết lập UTF-8 console Windows
try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

import numpy as np
import cv2

from src.preprocessing.numpy_filters import custom_median_filter, custom_mean_filter
from src.preprocessing.numpy_otsu import custom_otsu_threshold, compute_otsu_statistics
from src.morphology.numpy_morphology import (
    get_structuring_element,
    custom_erode,
    custom_dilate,
    custom_open,
    custom_close,
    custom_extract_boundary,
)
from src.features.numpy_features import custom_sobel_gradient


def compute_metrics(
    arr_a: np.ndarray,
    arr_b: np.ndarray
) -> Tuple[float, float]:
    """Tính toán sai số cực đại (Max Absolute Error) và sai số bình phương trung bình (MSE)."""
    diff = arr_a.astype(np.float64) - arr_b.astype(np.float64)
    max_err = float(np.max(np.abs(diff)))
    mse = float(np.mean(diff ** 2))
    return max_err, mse


def benchmark_function(fn, *args, repeat: int = 5, **kwargs) -> Tuple[Any, float]:
    """Chạy lặp hàm nhiều lần và lấy thời gian trung bình ngắn nhất (ms)."""
    # Chạy khởi động (warm-up)
    res = fn(*args, **kwargs)
    times = []
    for _ in range(repeat):
        t0 = time.perf_counter()
        _ = fn(*args, **kwargs)
        times.append((time.perf_counter() - t0) * 1000.0)
    return res, float(np.min(times))


def verify_single_image(
    image: np.ndarray,
    image_name: str = "image"
) -> Dict[str, Dict[str, Any]]:
    """
    Thực hiện kiểm chứng toàn bộ 7 toán tử trên một ảnh cụ thể (hoặc ma trận giả lập).
    Trả về từ điển chứa đầy đủ thông số kiểm thử cho từng toán tử.
    """
    results = {}
    h, w = image.shape
    se_rect3 = np.ones((3, 3), dtype=np.uint8)

    # =========================================================================
    # 1. Lọc trung vị 2D (ksize=5)
    # =========================================================================
    # cv2.medianBlur sử dụng BORDER_REPLICATE. Khi gọi custom_median_filter với mode='edge',
    # kết quả toàn ảnh trùng khớp bit-for-bit (Max Error = 0.00).
    # Với mode='reflect' (mặc định), vùng nội biên [pad:-pad, pad:-pad] trùng khớp 100%.
    res_my_med, t_my_med = benchmark_function(custom_median_filter, image, ksize=5, mode='edge')
    res_cv_med, t_cv_med = benchmark_function(cv2.medianBlur, image, 5)
    max_err_med, mse_med = compute_metrics(res_my_med, res_cv_med)

    results['median_filter_5x5'] = {
        'name': 'Lọc trung vị 2D (5x5)',
        'numpy_func': 'custom_median_filter',
        'opencv_func': 'cv2.medianBlur',
        'max_error': max_err_med,
        'mse': mse_med,
        'time_numpy_ms': t_my_med,
        'time_opencv_ms': t_cv_med,
        'passed': bool(max_err_med == 0.0)
    }

    # =========================================================================
    # 2. Lọc trung bình 2D (ksize=5)
    # =========================================================================
    # cv2.blur với borderType=cv2.BORDER_REFLECT_101 tương ứng chính xác với mode='reflect' của NumPy.
    res_my_mean, t_my_mean = benchmark_function(custom_mean_filter, image, ksize=5, mode='reflect')
    res_cv_mean, t_cv_mean = benchmark_function(cv2.blur, image, (5, 5), borderType=cv2.BORDER_REFLECT_101)
    max_err_mean, mse_mean = compute_metrics(res_my_mean, res_cv_mean)

    results['mean_filter_5x5'] = {
        'name': 'Lọc trung bình 2D (5x5)',
        'numpy_func': 'custom_mean_filter',
        'opencv_func': 'cv2.blur(BORDER_REFLECT_101)',
        'max_error': max_err_mean,
        'mse': mse_mean,
        'time_numpy_ms': t_my_mean,
        'time_opencv_ms': t_cv_mean,
        'passed': bool(max_err_mean == 0.0)
    }

    # =========================================================================
    # 3. Phân ngưỡng Otsu tối ưu T* và Mặt nạ nhị phân đốm tối
    # =========================================================================
    # cv2.threshold(..., THRESH_BINARY_INV + THRESH_OTSU) phân ngưỡng mức tối <= T* gán 255.
    t_my_otsu, eta_my, mask_my_otsu = custom_otsu_threshold(image)
    # Đo thời gian
    _, t_my_otsu_time = benchmark_function(custom_otsu_threshold, image)
    
    t0 = time.perf_counter()
    ret_cv, mask_cv_otsu = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    t_cv_otsu_time = (time.perf_counter() - t0) * 1000.0

    err_t = abs(float(t_my_otsu) - float(ret_cv))
    max_err_mask, mse_mask = compute_metrics(mask_my_otsu, mask_cv_otsu)

    results['otsu_threshold'] = {
        'name': 'Ngưỡng Otsu tối ưu T*',
        'numpy_func': 'custom_otsu_threshold',
        'opencv_func': 'cv2.threshold(THRESH_OTSU)',
        'max_error': float(err_t),
        'mse': mse_mask,
        'time_numpy_ms': t_my_otsu_time,
        'time_opencv_ms': t_cv_otsu_time,
        'passed': bool(err_t == 0.0 and max_err_mask == 0.0),
        'optimal_t': t_my_otsu,
        'eta': eta_my
    }

    # =========================================================================
    # 4. Phép co nhị phân (Binary Erosion)
    # =========================================================================
    binary_input = mask_my_otsu
    res_my_erode, t_my_erode = benchmark_function(custom_erode, binary_input, ksize=3)
    res_cv_erode, t_cv_erode = benchmark_function(
        cv2.erode, binary_input, se_rect3, borderType=cv2.BORDER_CONSTANT, borderValue=255
    )
    max_err_erode, mse_erode = compute_metrics(res_my_erode, res_cv_erode)

    results['binary_erosion_3x3'] = {
        'name': 'Phép co nhị phân A (-) B',
        'numpy_func': 'custom_erode',
        'opencv_func': 'cv2.erode(BORDER_CONSTANT=255)',
        'max_error': max_err_erode,
        'mse': mse_erode,
        'time_numpy_ms': t_my_erode,
        'time_opencv_ms': t_cv_erode,
        'passed': bool(max_err_erode == 0.0)
    }

    # =========================================================================
    # 5. Phép dãn nhị phân (Binary Dilation)
    # =========================================================================
    res_my_dilate, t_my_dilate = benchmark_function(custom_dilate, binary_input, ksize=3)
    res_cv_dilate, t_cv_dilate = benchmark_function(
        cv2.dilate, binary_input, se_rect3, borderType=cv2.BORDER_CONSTANT, borderValue=0
    )
    max_err_dilate, mse_dilate = compute_metrics(res_my_dilate, res_cv_dilate)

    results['binary_dilation_3x3'] = {
        'name': 'Phép dãn nhị phân A (+) B',
        'numpy_func': 'custom_dilate',
        'opencv_func': 'cv2.dilate(BORDER_CONSTANT=0)',
        'max_error': max_err_dilate,
        'mse': mse_dilate,
        'time_numpy_ms': t_my_dilate,
        'time_opencv_ms': t_cv_dilate,
        'passed': bool(max_err_dilate == 0.0)
    }

    # =========================================================================
    # 6. Trích biên hình thái học beta(A) = A - (A (-) B)
    # =========================================================================
    res_my_bnd, t_my_bnd = benchmark_function(custom_extract_boundary, binary_input, ksize=3)
    t0 = time.perf_counter()
    cv_erode_for_bnd = cv2.erode(binary_input, se_rect3, borderType=cv2.BORDER_CONSTANT, borderValue=255)
    res_cv_bnd = cv2.subtract(binary_input, cv_erode_for_bnd)
    t_cv_bnd = (time.perf_counter() - t0) * 1000.0
    max_err_bnd, mse_bnd = compute_metrics(res_my_bnd, res_cv_bnd)

    results['boundary_extraction'] = {
        'name': 'Trích biên hình thái beta(A)',
        'numpy_func': 'custom_extract_boundary',
        'opencv_func': 'A - cv2.erode(A)',
        'max_error': max_err_bnd,
        'mse': mse_bnd,
        'time_numpy_ms': t_my_bnd,
        'time_opencv_ms': t_cv_bnd,
        'passed': bool(max_err_bnd == 0.0)
    }

    # =========================================================================
    # 7. Toán tử đạo hàm vi phân Sobel và Độ lớn Gradient M(x, y)
    # =========================================================================
    (my_gx, my_gy, my_mag), t_my_sobel = benchmark_function(custom_sobel_gradient, image)
    
    t0 = time.perf_counter()
    img_f64 = image.astype(np.float64)
    cv_gx = cv2.Sobel(img_f64, cv2.CV_64F, 1, 0, ksize=3, borderType=cv2.BORDER_REFLECT_101)
    cv_gy = cv2.Sobel(img_f64, cv2.CV_64F, 0, 1, ksize=3, borderType=cv2.BORDER_REFLECT_101)
    cv_mag = np.sqrt(cv_gx ** 2 + cv_gy ** 2)
    t_cv_sobel = (time.perf_counter() - t0) * 1000.0

    max_err_mag, mse_mag = compute_metrics(my_mag, cv_mag)
    # Vì tính toán dấu phẩy động 64-bit, sai số cực đại phải nhỏ hơn 1e-9 (số học thực tế = 0.00)
    passed_sobel = bool(max_err_mag < 1e-9)

    results['sobel_gradient_3x3'] = {
        'name': 'Đạo hàm Sobel & Gradient M(x,y)',
        'numpy_func': 'custom_sobel_gradient',
        'opencv_func': 'cv2.Sobel(BORDER_REFLECT_101)',
        'max_error': max_err_mag,
        'mse': mse_mag,
        'time_numpy_ms': t_my_sobel,
        'time_opencv_ms': t_cv_sobel,
        'passed': passed_sobel
    }

    return results


def run_full_verification_suite() -> Dict[str, Any]:
    """
    Thực hiện kiểm chứng toàn diện trên:
    1. Dữ liệu giả lập (Ma trận Synthetic)
    2. Toàn bộ 10 ảnh mẫu SAR thực tế trong `data/sample/`
    In bảng ASCII định dạng chuẩn và trả về tổng hợp số liệu.
    """
    print("=" * 88)
    print("        HỌC PHẦN XỬ LÝ ẢNH - TRƯỜNG ĐẠI HỌC GIAO THÔNG VẬN TẢI (UTC)")
    print("  KỊCH BẢN KIỂM CHỨNG TÍNH ĐÚNG ĐẮN TOÁN HỌC: MÃ NGUỒN NUMPY VS THƯ VIỆN OPENCV")
    print("   Thành viên thực hiện: TV2 (Lý thuyết toán học & Kiểm chứng tính đúng)")
    print("=" * 88)

    all_image_results = {}
    aggregated_ops = {
        'median_filter_5x5': {'max_errs': [], 'mses': [], 't_np': [], 't_cv': [], 'name': 'Lọc trung vị 2D (5x5)'},
        'mean_filter_5x5': {'max_errs': [], 'mses': [], 't_np': [], 't_cv': [], 'name': 'Lọc trung bình 2D (5x5)'},
        'otsu_threshold': {'max_errs': [], 'mses': [], 't_np': [], 't_cv': [], 'name': 'Ngưỡng Otsu tối ưu T*'},
        'binary_erosion_3x3': {'max_errs': [], 'mses': [], 't_np': [], 't_cv': [], 'name': 'Phép co nhị phân A (-) B'},
        'binary_dilation_3x3': {'max_errs': [], 'mses': [], 't_np': [], 't_cv': [], 'name': 'Phép dãn nhị phân A (+) B'},
        'boundary_extraction': {'max_errs': [], 'mses': [], 't_np': [], 't_cv': [], 'name': 'Trích biên hình thái beta(A)'},
        'sobel_gradient_3x3': {'max_errs': [], 'mses': [], 't_np': [], 't_cv': [], 'name': 'Đạo hàm Sobel M(x,y)'},
    }

    # -------------------------------------------------------------
    # 1. KIỂM THỬ TRÊN DỮ LIỆU GIẢ LẬP (SYNTHETIC MATRIX)
    # -------------------------------------------------------------
    print("\n[PHẦN 1] KIỂM THỬ TRÊN MA TRẬN GIẢ LẬP (SYNTHETIC BENCHMARK 400x400)")
    print("-" * 88)
    np.random.seed(42)
    synth_img = np.random.randint(20, 220, (400, 400), dtype=np.uint8)
    # Thêm 1 đốm tối nhân tạo ở trung tâm
    synth_img[100:300, 100:300] = np.random.randint(10, 40, (200, 200), dtype=np.uint8)

    synth_res = verify_single_image(synth_img, "Synthetic_400x400")
    for op_key, r in synth_res.items():
        status_str = "PASSED (100% Khớp)" if r['passed'] else "FAILED"
        print(f"  {r['name']:<32} | Max Err: {r['max_error']:.4f} | MSE: {r['mse']:.6f} | "
              f"NumPy: {r['time_numpy_ms']:5.2f}ms | CV: {r['time_opencv_ms']:5.2f}ms => {status_str}")

    # -------------------------------------------------------------
    # 2. KIỂM THỬ TRÊN 10 ẢNH MẪU SAR SENTINEL-1 THỰC TẾ
    # -------------------------------------------------------------
    print("\n" + "=" * 88)
    print("[PHẦN 2] KIỂM THỬ TRÊN 10 ẢNH MẪU SAR THỰC TẾ (data/sample/Class_0 & Class_1)")
    print("=" * 88)

    sample_files = sorted(glob.glob(os.path.join(WORKSPACE_DIR, "data", "sample", "*", "*.jpg")))
    if not sample_files:
        raise FileNotFoundError("Không tìm thấy ảnh mẫu trong data/sample/!")

    print(f"Tìm thấy tổng cộng {len(sample_files)} ảnh mẫu thực tế:")
    for f in sample_files:
        rel_path = os.path.relpath(f, WORKSPACE_DIR)
        print(f"  + {rel_path}")

    # Bảng chi tiết từng ảnh
    print("\n" + "-" * 88)
    print(f"{'Tên ảnh mẫu':<22} | {'Toán tử kiểm chứng':<24} | {'Max Error':<10} | {'MSE':<10} | {'Trạng thái'}")
    print("-" * 88)

    for img_path in sample_files:
        img_name = os.path.basename(img_path)
        img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
        if img is None:
            continue

        res = verify_single_image(img, img_name)
        all_image_results[img_name] = res

        for op_key, r in res.items():
            aggregated_ops[op_key]['max_errs'].append(r['max_error'])
            aggregated_ops[op_key]['mses'].append(r['mse'])
            aggregated_ops[op_key]['t_np'].append(r['time_numpy_ms'])
            aggregated_ops[op_key]['t_cv'].append(r['time_opencv_ms'])
            status_str = "PASS" if r['passed'] else "FAIL"
            print(f"{img_name:<22} | {r['name']:<24} | {r['max_error']:<10.4f} | {r['mse']:<10.4e} | {status_str}")

    # -------------------------------------------------------------
    # 3. TỔNG HỢP VÀ ĐỐI CHIẾU SỐ LIỆU ĐO ĐẠC CHO BÁO CÁO LATEX
    # -------------------------------------------------------------
    print("\n" + "=" * 88)
    print("      BẢNG TỔNG HỢP ĐỐI CHIẾU TOÀN DIỆN CHO BÁO CÁO (MỤC 3.5 BÁO CÁO LATEX)")
    print("=" * 88)
    print(f"{'Thuật toán / Toán tử':<28} | {'Hàm NumPy':<23} | {'Max Err':<8} | {'MSE':<8} | {'Time NumPy':<10} | {'Time CV':<9} | {'Kết luận'}")
    print("-" * 88)

    summary_for_report = []
    all_passed = True
    for op_key, data in aggregated_ops.items():
        max_err = float(np.max(data['max_errs']))
        avg_mse = float(np.mean(data['mses']))
        avg_t_np = float(np.mean(data['t_np']))
        avg_t_cv = float(np.mean(data['t_cv']))
        is_op_passed = bool(max_err == 0.0 or (op_key == 'sobel_gradient_3x3' and max_err < 1e-9))
        all_passed = all_passed and is_op_passed
        status_label = "100% Khớp" if is_op_passed else "Khác biệt"

        # Lấy tên hàm tương ứng
        sample_item = list(all_image_results.values())[0][op_key]
        np_func = sample_item['numpy_func']

        print(f"{data['name']:<28} | {np_func:<23} | {max_err:<8.2f} | {avg_mse:<8.2e} | "
              f"{avg_t_np:6.2f} ms | {avg_t_cv:6.2f} ms | {status_label}")

        summary_for_report.append({
            'key': op_key,
            'name': data['name'],
            'numpy_func': np_func,
            'opencv_func': sample_item['opencv_func'],
            'max_error': max_err,
            'mse': avg_mse,
            'time_numpy_ms': avg_t_np,
            'time_opencv_ms': avg_t_cv,
            'passed': is_op_passed
        })

    print("-" * 88)
    if all_passed:
        print("[XÁC NHẬN CHÍNH THỨC]: Toàn bộ 7 toán tử tự cài đặt đạt độ chính xác toán học tuyệt đối")
        print("                        (Max Absolute Error = 0.00, MSE = 0.00) trên 100% ảnh mẫu SAR.")
    else:
        print("[CẢNH BÁO]: Có toán tử không khớp với chuẩn đối chứng!")
    print("=" * 88)

    return {
        'all_passed': all_passed,
        'summary': summary_for_report,
        'per_image_results': all_image_results
    }


class TestVerificationSuite(unittest.TestCase):
    """Lớp kiểm thử chuẩn unittest phục vụ kiểm thử hồi quy tự động."""

    @classmethod
    def setUpClass(cls):
        cls.files = sorted(glob.glob(os.path.join(WORKSPACE_DIR, "data", "sample", "*", "*.jpg")))
        assert len(cls.files) == 10, f"Mong đợi 10 ảnh mẫu SAR, tìm thấy: {len(cls.files)}"

    def test_median_filter_matches_opencv(self):
        for f in self.files:
            img = cv2.imread(f, cv2.IMREAD_GRAYSCALE)
            my_med = custom_median_filter(img, 5, mode='edge')
            cv_med = cv2.medianBlur(img, 5)
            max_err, _ = compute_metrics(my_med, cv_med)
            self.assertEqual(max_err, 0.0, f"Lọc trung vị lệch trên file {f}")

    def test_mean_filter_matches_opencv(self):
        for f in self.files:
            img = cv2.imread(f, cv2.IMREAD_GRAYSCALE)
            my_mean = custom_mean_filter(img, 5, mode='reflect')
            cv_mean = cv2.blur(img, (5, 5), borderType=cv2.BORDER_REFLECT_101)
            max_err, _ = compute_metrics(my_mean, cv_mean)
            self.assertEqual(max_err, 0.0, f"Lọc trung bình lệch trên file {f}")

    def test_otsu_threshold_matches_opencv(self):
        for f in self.files:
            img = cv2.imread(f, cv2.IMREAD_GRAYSCALE)
            t_my, eta, mask_my = custom_otsu_threshold(img)
            t_cv, mask_cv = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
            self.assertEqual(t_my, int(t_cv), f"Ngưỡng Otsu lệch trên file {f}")
            max_err, _ = compute_metrics(mask_my, mask_cv)
            self.assertEqual(max_err, 0.0, f"Mặt nạ Otsu lệch trên file {f}")

    def test_morphology_erode_dilate_boundary_matches_opencv(self):
        se = np.ones((3, 3), dtype=np.uint8)
        for f in self.files:
            img = cv2.imread(f, cv2.IMREAD_GRAYSCALE)
            _, _, mask = custom_otsu_threshold(img)

            # Erosion
            my_e = custom_erode(mask, ksize=3)
            cv_e = cv2.erode(mask, se, borderType=cv2.BORDER_CONSTANT, borderValue=255)
            err_e, _ = compute_metrics(my_e, cv_e)
            self.assertEqual(err_e, 0.0, f"Phép co lệch trên file {f}")

            # Dilation
            my_d = custom_dilate(mask, ksize=3)
            cv_d = cv2.dilate(mask, se, borderType=cv2.BORDER_CONSTANT, borderValue=0)
            err_d, _ = compute_metrics(my_d, cv_d)
            self.assertEqual(err_d, 0.0, f"Phép dãn lệch trên file {f}")

            # Boundary
            my_b = custom_extract_boundary(mask, ksize=3)
            cv_b = cv2.subtract(mask, cv_e)
            err_b, _ = compute_metrics(my_b, cv_b)
            self.assertEqual(err_b, 0.0, f"Trích biên lệch trên file {f}")

    def test_sobel_gradient_matches_opencv(self):
        for f in self.files:
            img = cv2.imread(f, cv2.IMREAD_GRAYSCALE)
            gx, gy, mag = custom_sobel_gradient(img)

            img_f64 = img.astype(np.float64)
            cv_gx = cv2.Sobel(img_f64, cv2.CV_64F, 1, 0, ksize=3, borderType=cv2.BORDER_REFLECT_101)
            cv_gy = cv2.Sobel(img_f64, cv2.CV_64F, 0, 1, ksize=3, borderType=cv2.BORDER_REFLECT_101)
            cv_mag = np.sqrt(cv_gx ** 2 + cv_gy ** 2)

            err_gx, _ = compute_metrics(gx, cv_gx)
            err_gy, _ = compute_metrics(gy, cv_gy)
            err_mag, _ = compute_metrics(mag, cv_mag)

            self.assertLess(err_gx, 1e-9, f"Sobel Gx lệch trên file {f}")
            self.assertLess(err_gy, 1e-9, f"Sobel Gy lệch trên file {f}")
            self.assertLess(err_mag, 1e-9, f"Sobel Mag lệch trên file {f}")


if __name__ == "__main__":
    suite_res = run_full_verification_suite()
    # Chạy thêm unittest runner
    print("\n--- CHẠY UNITTEST FORMAL TEST SUITE ---")
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
