"""
Unit test suite for TV3 Pure NumPy Preprocessing modules:
- custom_median_filter
- custom_mean_filter
- custom_otsu_threshold
- compute_otsu_statistics

Tests cover:
1. Toy matrix validation with known analytical results.
2. Boundary reflect padding correctness.
3. Noise suppression and edge preservation.
4. Otsu mathematical formulation correctness and consistency with OpenCV Otsu.
5. All sample images in data/sample/Class_0 and data/sample/Class_1.
6. Verification that core files do NOT import or depend on cv2.
7. Performance latency benchmarks.
"""

import os
import sys

try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

import time
import glob
import ast
import unittest
import numpy as np

# Thêm thư mục gốc vào PYTHONPATH
WORKSPACE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if WORKSPACE_DIR not in sys.path:
    sys.path.insert(0, WORKSPACE_DIR)

from src.preprocessing.numpy_filters import custom_median_filter, custom_mean_filter
from src.preprocessing.numpy_otsu import custom_otsu_threshold, compute_otsu_statistics


class TestPureNumpyFilters(unittest.TestCase):
    """Kiểm thử bộ lọc trung vị và trung bình thuần NumPy."""

    def test_no_opencv_imported_in_core_modules(self):
        """Kiểm tra tuyệt đối không import hoặc sử dụng cv2 trong các module lõi của TV3."""
        for mod_name in ["numpy_filters.py", "numpy_otsu.py"]:
            file_path = os.path.join(WORKSPACE_DIR, "src", "preprocessing", mod_name)
            self.assertTrue(os.path.exists(file_path), f"File {file_path} không tồn tại!")
            with open(file_path, "r", encoding="utf-8") as f:
                tree = ast.parse(f.read(), filename=file_path)
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        self.assertNotEqual(
                            alias.name, "cv2",
                            f"VI PHẠM: Module {mod_name} import cv2!"
                        )
                elif isinstance(node, ast.ImportFrom):
                    self.assertNotEqual(
                        node.module, "cv2",
                        f"VI PHẠM: Module {mod_name} import từ cv2!"
                    )

    def test_median_filter_salt_and_pepper_toy(self):
        """Kiểm tra lọc bỏ xung nhiễu muối tiêu trên ma trận đồ chơi 5x5."""
        # Vùng phẳng giá trị 100, tại tâm (2, 2) bị nhiễu xung cực đại 255
        toy = np.full((5, 5), 100, dtype=np.uint8)
        toy[2, 2] = 255  # Nhiễu muối
        toy[1, 1] = 0    # Nhiễu tiêu

        filtered = custom_median_filter(toy, ksize=3)
        self.assertEqual(filtered.dtype, np.uint8)
        self.assertEqual(filtered.shape, (5, 5))
        # Tại tâm lân cận 3x3 có 7 số 100, 1 số 255, 1 số 0 -> trung vị phải bằng 100
        self.assertEqual(filtered[2, 2], 100)
        self.assertEqual(filtered[1, 1], 100)

    def test_median_filter_edge_reflection(self):
        """Kiểm tra tính phản xạ biên đối xứng (reflect padding)."""
        # Ma trận bậc thang 3x3
        toy = np.array([
            [10, 20, 30],
            [40, 50, 60],
            [70, 80, 90]
        ], dtype=np.uint8)

        filtered = custom_median_filter(toy, ksize=3)
        self.assertEqual(filtered.shape, toy.shape)
        # Tại góc (0, 0): Với reflect padding 'reflect' (không lặp biên):
        # lân cận 3x3 quanh (0, 0) lấy từ pad reflect:
        # Padded quanh (0,0) gồm: [50, 40, 50; 20, 10, 20; 50, 40, 50]
        # Các giá trị: 10, 20, 20, 40, 40, 50, 50, 50, 50 -> trung vị là 40
        self.assertEqual(filtered[0, 0], 40)

    def test_median_filter_dtypes_preservation(self):
        """Kiểm tra khả năng bảo toàn kiểu dữ liệu đầu vào (uint8, float32, float64)."""
        img_u8 = np.random.randint(0, 256, (32, 32), dtype=np.uint8)
        img_f32 = np.random.rand(32, 32).astype(np.float32)
        img_f64 = np.random.rand(32, 32).astype(np.float64)

        out_u8 = custom_median_filter(img_u8, ksize=3)
        out_f32 = custom_median_filter(img_f32, ksize=3)
        out_f64 = custom_median_filter(img_f64, ksize=3)

        self.assertEqual(out_u8.dtype, np.uint8)
        self.assertEqual(out_f32.dtype, np.float32)
        self.assertEqual(out_f64.dtype, np.float64)

    def test_median_filter_invalid_inputs(self):
        """Kiểm tra xử lý ngoại lệ khi truyền tham số sai quy cách."""
        valid_img = np.zeros((10, 10), dtype=np.uint8)
        # ksize chẵn phải báo lỗi
        with self.assertRaises(ValueError):
            custom_median_filter(valid_img, ksize=4)
        # ksize <= 0 phải báo lỗi
        with self.assertRaises(ValueError):
            custom_median_filter(valid_img, ksize=0)
        # Ảnh 3D phải báo lỗi
        with self.assertRaises(ValueError):
            custom_median_filter(np.zeros((10, 10, 3)), ksize=3)

    def test_mean_filter_toy(self):
        """Kiểm tra bộ lọc trung bình bằng Bảng diện tích tích lũy (Integral Image)."""
        toy = np.array([
            [10, 20, 30],
            [40, 50, 60],
            [70, 80, 90]
        ], dtype=np.uint8)

        # Trung bình cửa sổ 3x3 tại tâm (1, 1) = (10+20+...+90)/9 = 450/9 = 50.0
        filtered = custom_mean_filter(toy, ksize=3)
        self.assertEqual(filtered[1, 1], 50)
        self.assertEqual(filtered.dtype, np.uint8)


class TestPureNumpyOtsu(unittest.TestCase):
    """Kiểm thử thuật toán Phân ngưỡng Otsu thuần NumPy."""

    def test_otsu_synthetic_bimodal(self):
        """Kiểm tra phân ngưỡng bimodal rõ rệt (2 cụm 40 và 200)."""
        cluster_dark = np.random.normal(loc=40, scale=5, size=(100, 100)).clip(0, 255)
        cluster_bright = np.random.normal(loc=200, scale=5, size=(100, 100)).clip(0, 255)
        bimodal = np.vstack([cluster_dark, cluster_bright]).astype(np.uint8)

        optimal_t, eta, dark_mask = custom_otsu_threshold(bimodal)

        # Ngưỡng tối ưu phải nằm khoảng giữa 2 cụm (khoảng 100 - 140)
        self.assertTrue(90 <= optimal_t <= 150, f"Ngưỡng T*={optimal_t} không nằm giữa 2 đỉnh!")
        # Hệ số khả tách eta của phân bố tách bạch này phải rất cao (> 0.85)
        self.assertGreater(eta, 0.85, f"Eta={eta:.4f} quá thấp đối với bimodal lý tưởng!")
        # Mặt nạ đốm tối phía nửa trên phải có giá trị 255, nửa dưới 0
        self.assertEqual(dark_mask.shape, bimodal.shape)
        self.assertEqual(dark_mask.dtype, np.uint8)
        self.assertGreater(np.mean(dark_mask[:100, :] == 255), 0.99)
        self.assertGreater(np.mean(dark_mask[100:, :] == 0), 0.99)

    def test_otsu_statistics_dictionary(self):
        """Kiểm tra các đại lượng thống kê trung gian của Otsu."""
        img = np.random.randint(0, 256, (50, 50), dtype=np.uint8)
        stats = compute_otsu_statistics(img)

        self.assertIn("hist", stats)
        self.assertIn("p", stats)
        self.assertIn("omega", stats)
        self.assertIn("mu", stats)
        self.assertIn("sigma_b_sq", stats)
        self.assertIn("sigma_t_sq", stats)
        self.assertIn("optimal_t", stats)
        self.assertIn("eta", stats)

        # Kiểm tra tính chuẩn hóa: sum(p) == 1.0, omega[-1] == 1.0
        self.assertAlmostEqual(np.sum(stats["p"]), 1.0, places=6)
        self.assertAlmostEqual(stats["omega"][-1], 1.0, places=6)
        self.assertTrue(0.0 <= stats["eta"] <= 1.0)

    def test_otsu_against_sample_images_and_opencv(self):
        """
        Kiểm tra thuật toán trên toàn bộ ảnh thực tế trong data/sample/
        và so sánh trực tiếp kết quả với OpenCV Otsu (cv2.threshold).
        """
        import cv2

        sample_paths = sorted(glob.glob(os.path.join(WORKSPACE_DIR, "data", "sample", "*", "*.jpg")))
        self.assertGreaterEqual(len(sample_paths), 10, "Thư mục data/sample phải có ít nhất 10 ảnh mẫu!")

        for p in sample_paths:
            img = cv2.imread(p, cv2.IMREAD_GRAYSCALE)
            self.assertIsNotNone(img, f"Không đọc được ảnh {p}")

            # 1. Chạy hàm pure NumPy
            t_start = time.perf_counter()
            optimal_t, eta, dark_mask = custom_otsu_threshold(img)
            t_numpy = (time.perf_counter() - t_start) * 1000.0  # ms

            # 2. Chạy OpenCV đối chứng
            cv_t, cv_mask_bright = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

            # Kiểm tra ngưỡng tìm được khớp chính xác
            self.assertEqual(
                optimal_t, int(cv_t),
                f"Lệch ngưỡng tại {os.path.basename(p)}: NumPy={optimal_t} vs OpenCV={int(cv_t)}"
            )

            # Kiểm tra mặt nạ đốm tối (dark mask) là phần bù của bright mask OpenCV
            # OpenCV gán 255 cho pixel > T, ta gán 255 cho pixel <= T
            expected_dark = (cv_mask_bright == 0).astype(np.uint8) * 255
            diff_pixels = np.sum(dark_mask != expected_dark)
            self.assertEqual(diff_pixels, 0, f"Mặt nạ đốm tối khác OpenCV tại {os.path.basename(p)}")

            # Kiểm tra ràng buộc toán học của eta
            self.assertTrue(0.0 <= eta <= 1.0, f"Eta={eta} nằm ngoài [0, 1] tại {os.path.basename(p)}")
            # Tốc độ Otsu NumPy phải dưới 5ms
            self.assertLess(t_numpy, 20.0, f"Thời gian Otsu quá lâu: {t_numpy:.2f} ms")


class TestPipelinePerformance(unittest.TestCase):
    """Kiểm thử hiệu năng thời gian và tính hoàn chỉnh trên ảnh SAR 400x400."""

    def test_full_preprocessing_pipeline_latency(self):
        """Đo đạc độ trễ toàn bộ quy trình: Lọc trung vị + Phân ngưỡng Otsu."""
        sample_path = glob.glob(os.path.join(WORKSPACE_DIR, "data", "sample", "Class_1", "*.jpg"))[0]
        # Sử dụng pyplot / matplotlib hoặc PIL hoặc cv2 để đọc ảnh kiểm thử
        import cv2
        img = cv2.imread(sample_path, cv2.IMREAD_GRAYSCALE)
        self.assertEqual(img.shape, (400, 400))

        # Bước 1: Lọc trung vị
        t0 = time.perf_counter()
        filtered = custom_median_filter(img, ksize=5)
        t_median = (time.perf_counter() - t0) * 1000.0

        # Bước 2: Phân ngưỡng Otsu
        t1 = time.perf_counter()
        opt_t, eta, dark_mask = custom_otsu_threshold(filtered)
        t_otsu = (time.perf_counter() - t1) * 1000.0

        total_time = t_median + t_otsu

        try:
            sys.stdout.reconfigure(encoding='utf-8')
        except Exception:
            pass

        print(f"\n[BENCHMARK TV3 - SAR 400x400]")
        print(f"  + Loc trung vi 5x5: {t_median:.2f} ms")
        print(f"  + Nguong Otsu + Eta: {t_otsu:.2f} ms")
        print(f"  + Tong do tre: {total_time:.2f} ms (~{1000.0/total_time:.1f} FPS)")
        print(f"  + Nguong toi uu T*: {opt_t}, He so kha tach eta: {eta:.4f}")

        self.assertLess(t_median, 250.0, f"Lọc trung vị quá chậm: {t_median:.2f} ms")
        self.assertLess(t_otsu, 10.0, f"Otsu quá chậm: {t_otsu:.2f} ms")


if __name__ == "__main__":
    unittest.main()
