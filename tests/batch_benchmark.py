"""
KỊCH BẢN BENCHMARK THỰC NGHIỆM ĐỊNH LƯỢNG HÀNG LOẠT (CDIO BENCHMARK RUNNER)
Đề tài 18: Phát hiện vết dầu tràn trên biển từ ảnh SAR Sentinel-1 (NASA #6)
Bộ môn Kỹ thuật Máy tính — Khoa CNTT — Trường ĐH Giao thông Vận tải (UTC)
Giảng viên hướng dẫn: TS. Phan Thanh Toàn

Thành viên thực hiện: TV5 — Dữ liệu, Thực nghiệm định lượng & Đánh giá kết quả

Mục tiêu kỹ thuật:
- Đánh giá toàn diện pipeline xử lý ảnh dựa trên toán tử thuần NumPy của TV3 & TV4.
- Hỗ trợ các chế độ chạy:
    + sample: 10 ảnh trong data/sample/ (kiểm thử nhanh).
    + fast: 200 ảnh đại diện.
    + representative: 500 ảnh kiểm thử ngẫu nhiên có kiểm soát.
    + full: Toàn bộ tập dữ liệu CSIRO Sentinel-1 SAR (5,538+ ảnh).
- Thu thập ma trận nhầm lẫn (TP, FP, TN, FN), tính toán các chỉ số CDIO:
  Accuracy, Precision, Recall, Specificity, F1-Score, Inference Latency (ms), FPS.
- Xuất file kết quả chi tiết: outputs/benchmark_results.csv
"""

import os
import sys
import time
import glob
import csv
import argparse
import random
from typing import Dict, Any, List, Tuple
from concurrent.futures import ProcessPoolExecutor

import cv2
import numpy as np

# Thêm thư mục gốc vào sys.path để import các module của dự án
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.preprocessing.numpy_otsu import custom_otsu_threshold
from src.morphology.numpy_morphology import (
    custom_open,
    custom_close,
    custom_extract_boundary,
    get_structuring_element
)
from src.features.numpy_features import (
    custom_sobel_gradient,
    extract_blob_features,
    classify_candidate
)


def run_pipeline_on_image(
    image_path: str,
    true_label: int,
    ksize_median: int = 5,
    min_area: int = 80,
    max_area: int = 40000,
    min_contrast: float = 10.0,
    min_damping: float = 1.20,
    min_border_grad: float = 5.5,
    min_elongation: float = 1.7,
    min_complexity: float = 1.5,
) -> Dict[str, Any]:
    """
    Thực thi toàn bộ pipeline 4 bước tuần tự trên 1 ảnh SAR:
    Bước 1: Tiền xử lý lọc trung vị khử nhiễu đốm speckle (Chương 3)
    Bước 2: Phân đoạn ngưỡng Otsu tối ưu & Hệ số khả tách eta (Chương 7)
    Bước 3: Hình thái học Opening, Closing, Fill holes, trích biên beta(A) (Chương 6)
    Bước 4: Đạo hàm Gradient Sobel vi phân, tương phản vành đai và Moment quán tính (Chương 5)
    """
    filename = os.path.basename(image_path)
    start_total = time.perf_counter()

    # 0. Đọc ảnh mức xám
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        return {
            "filename": filename,
            "path": image_path,
            "true_label": true_label,
            "pred_label": 0,
            "is_correct": False,
            "error": "Cannot open image",
            "latency_ms": 0.0,
        }

    h, w = img.shape
    total_pixels = h * w

    # -------------------------------------------------------------
    # BƯỚC 1: Lọc trung vị khử nhiễu Speckle (Chương 3)
    # -------------------------------------------------------------
    t0 = time.perf_counter()
    filtered = cv2.medianBlur(img, ksize_median)
    t_median = (time.perf_counter() - t0) * 1000.0

    scene_mean = float(np.mean(filtered))
    scene_std = float(np.std(filtered))

    # SAR Physics Check: Mặt biển lặng gió toàn cảnh (Low Wind Specular Mirror)
    if scene_mean < 35.0:
        latency_ms = (time.perf_counter() - start_total) * 1000.0
        return {
            "filename": filename,
            "path": image_path,
            "true_label": true_label,
            "pred_label": 0,
            "is_correct": (true_label == 0),
            "num_blobs": 0,
            "oil_detected_count": 0,
            "max_area": 0.0,
            "max_contrast": 0.0,
            "max_damping": 1.0,
            "max_border_grad": 0.0,
            "max_elongation": 1.0,
            "max_complexity": 1.0,
            "otsu_thresh": 0,
            "otsu_separability": 0.0,
            "scene_mean": round(scene_mean, 2),
            "latency_ms": round(latency_ms, 2),
            "error": None,
        }

    # -------------------------------------------------------------
    # BƯỚC 2: Phân ngưỡng Otsu tối ưu & Hệ số khả tách eta (Chương 7)
    # -------------------------------------------------------------
    t0 = time.perf_counter()
    optimal_t, separability, dark_mask = custom_otsu_threshold(filtered)
    t_otsu = (time.perf_counter() - t0) * 1000.0

    # Nếu hệ số khả tách eta quá thấp (< 0.05) và độ lệch chuẩn nhỏ: biển sạch đồng nhất
    if separability < 0.05 and scene_std < 6.0:
        latency_ms = (time.perf_counter() - start_total) * 1000.0
        return {
            "filename": filename,
            "path": image_path,
            "true_label": true_label,
            "pred_label": 0,
            "is_correct": (true_label == 0),
            "num_blobs": 0,
            "oil_detected_count": 0,
            "max_area": 0.0,
            "max_contrast": 0.0,
            "max_damping": 1.0,
            "max_border_grad": 0.0,
            "max_elongation": 1.0,
            "max_complexity": 1.0,
            "otsu_thresh": optimal_t,
            "otsu_separability": round(separability, 4),
            "scene_mean": round(scene_mean, 2),
            "latency_ms": round(latency_ms, 2),
            "error": None,
        }

    # -------------------------------------------------------------
    # BƯỚC 3: Xử lý Hình thái học & Trích biên (Chương 6)
    # -------------------------------------------------------------
    t0 = time.perf_counter()
    # 3.1 Mở (Opening) loại bỏ bọt sóng và nhiễu speckle li ti
    opened = custom_open(dark_mask, ksize=3)

    # 3.2 Đóng (Closing) hàn gắn các đứt gãy thân vệt dầu
    closed = custom_close(opened, ksize=7)

    # 3.3 Lấp lỗ thủng (Hole Filling) để làm đặc ruột vệt dầu
    padded = cv2.copyMakeBorder(closed, 1, 1, 1, 1, cv2.BORDER_CONSTANT, value=0)
    mask_ff = np.zeros((h + 4, w + 4), np.uint8)
    cv2.floodFill(padded, mask_ff, (0, 0), 255)
    filled = closed | cv2.bitwise_not(padded[1:-1, 1:-1])

    # 3.4 Phân tích thành phần liên thông
    num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(
        filled, connectivity=8
    )
    t_morph = (time.perf_counter() - t0) * 1000.0

    # Lọc danh sách đốm tối ứng viên có diện tích hợp lệ
    candidate_labels = [
        l for l in range(1, num_labels)
        if min_area <= stats[l, cv2.CC_STAT_AREA] <= max_area
    ]
    num_candidates = len(candidate_labels)

    # Heuristic viễn thám: Nếu có quá 14 đốm tối rải rác -> bọt sóng biển xao động vỡ vụn
    if num_candidates > 14 or num_candidates == 0:
        latency_ms = (time.perf_counter() - start_total) * 1000.0
        return {
            "filename": filename,
            "path": image_path,
            "true_label": true_label,
            "pred_label": 0,
            "is_correct": (true_label == 0),
            "num_blobs": num_candidates,
            "oil_detected_count": 0,
            "max_area": 0.0,
            "max_contrast": 0.0,
            "max_damping": 1.0,
            "max_border_grad": 0.0,
            "max_elongation": 1.0,
            "max_complexity": 1.0,
            "otsu_thresh": optimal_t,
            "otsu_separability": round(separability, 4),
            "scene_mean": round(scene_mean, 2),
            "latency_ms": round(latency_ms, 2),
            "error": None,
        }

    # -------------------------------------------------------------
    # BƯỚC 4: Đạo hàm Sobel, Tương phản vành đai & Hình học (Chương 5)
    # -------------------------------------------------------------
    t0 = time.perf_counter()
    # 4.1 Gradient vi phân Sobel bằng NumPy vector hóa
    _, _, grad_mag = custom_sobel_gradient(filtered)

    se_annulus = get_structuring_element(ksize=11, se_type="ellipse")
    oil_detected_count = 0

    max_area_val = 0.0
    max_contrast_val = 0.0
    max_damping_val = 1.0
    max_border_grad_val = 0.0
    max_elongation_val = 1.0
    max_complexity_val = 1.0

    for l in candidate_labels:
        area = int(stats[l, cv2.CC_STAT_AREA])
        blob_mask = (labels == l).astype(np.uint8) * 255

        # Trích biên hình thái học chuẩn toán học: beta(A) = A - (A (-) B)
        boundary = custom_extract_boundary(blob_mask, ksize=3)

        # Trích xuất toàn diện 4 nhóm đặc trưng bằng NumPy
        feats = extract_blob_features(
            image=filtered,
            blob_mask=blob_mask,
            boundary_mask=boundary,
            all_dark_mask=filled,
            annulus_ksize=11,
            precomputed_grad_mag=grad_mag,
        )

        area_f = feats["area"]
        contrast_f = feats["contrast_diff"]
        damping_f = feats["damping_ratio"]
        grad_f = feats["border_gradient"]
        elong_f = feats["elongation"]
        comp_f = feats["boundary_complexity"]

        if area_f > max_area_val:
            max_area_val = area_f
        if contrast_f > max_contrast_val:
            max_contrast_val = contrast_f
        if damping_f > max_damping_val:
            max_damping_val = damping_f
        if grad_f > max_border_grad_val:
            max_border_grad_val = grad_f
        if elong_f > max_elongation_val:
            max_elongation_val = elong_f
        if comp_f > max_complexity_val:
            max_complexity_val = comp_f

        # Quy tắc Heuristic CDIO:
        # 1. Tương phản hoặc hệ số tắt sóng mao dẫn
        pass_contrast = (contrast_f >= min_contrast) or (damping_f >= min_damping)
        # 2. Độ dốc biên bước nhảy Marangoni
        pass_grad = (grad_f >= min_border_grad)
        # 3. Hình thái học: Dải dài do tàu chạy hoặc rách răng cưa do sóng
        pass_shape = (elong_f >= min_elongation) or (comp_f >= min_complexity)

        if pass_contrast and pass_grad and pass_shape:
            oil_detected_count += 1

    t_feat = (time.perf_counter() - t0) * 1000.0

    pred_label = 1 if oil_detected_count > 0 else 0
    is_correct = (pred_label == true_label)
    latency_ms = (time.perf_counter() - start_total) * 1000.0

    return {
        "filename": filename,
        "path": image_path,
        "true_label": true_label,
        "pred_label": pred_label,
        "is_correct": is_correct,
        "num_blobs": num_candidates,
        "oil_detected_count": oil_detected_count,
        "max_area": round(max_area_val, 1),
        "max_contrast": round(max_contrast_val, 2),
        "max_damping": round(max_damping_val, 2),
        "max_border_grad": round(max_border_grad_val, 2),
        "max_elongation": round(max_elongation_val, 2),
        "max_complexity": round(max_complexity_val, 2),
        "otsu_thresh": optimal_t,
        "otsu_separability": round(separability, 4),
        "scene_mean": round(scene_mean, 2),
        "latency_ms": round(latency_ms, 2),
        "error": None,
    }


def _worker_task(args: Tuple[str, int]) -> Dict[str, Any]:
    """Hàm bọc gọi đa tiến trình cho 1 ảnh."""
    path, label = args
    try:
        return run_pipeline_on_image(path, label)
    except Exception as e:
        return {
            "filename": os.path.basename(path),
            "path": path,
            "true_label": label,
            "pred_label": 0,
            "is_correct": False,
            "error": str(e),
            "latency_ms": 0.0,
        }


def load_dataset_tasks(
    data_dir: str,
    mode: str = "representative",
    num_samples: int = None,
    seed: int = 42,
) -> List[Tuple[str, int]]:
    """Tải và phân bổ danh sách ảnh cần benchmark theo các chế độ yêu cầu."""
    random.seed(seed)
    tasks: List[Tuple[str, int]] = []

    if mode == "sample":
        # Chế độ kiểm thử nhanh trên thư mục sample
        sample_c0 = sorted(glob.glob(os.path.join(data_dir, "sample", "Class_0", "*.jpg")))
        sample_c1 = sorted(glob.glob(os.path.join(data_dir, "sample", "Class_1", "*.jpg")))
        tasks = [(f, 0) for f in sample_c0] + [(f, 1) for f in sample_c1]
        print(f"[*] Chế độ 'sample': Tìm thấy {len(sample_c0)} ảnh Class 0 và {len(sample_c1)} ảnh Class 1.")
        return tasks

    c0_all = sorted(glob.glob(os.path.join(data_dir, "Class_0", "*.jpg")))
    c1_all = sorted(glob.glob(os.path.join(data_dir, "Class_1", "*.jpg")))

    if not c0_all or not c1_all:
        raise FileNotFoundError(f"Không tìm thấy ảnh SAR trong thư mục '{data_dir}/Class_0' hoặc '{data_dir}/Class_1'")

    if mode == "fast":
        n_c0 = min(100, len(c0_all))
        n_c1 = min(100, len(c1_all))
        c0_sel = random.sample(c0_all, n_c0)
        c1_sel = random.sample(c1_all, n_c1)
        tasks = [(f, 0) for f in c0_sel] + [(f, 1) for f in c1_sel]
        print(f"[*] Chế độ 'fast': Lấy ngẫu nhiên {n_c0} ảnh Class 0 và {n_c1} ảnh Class 1 (Tổng: {len(tasks)} ảnh).")

    elif mode == "representative":
        n_c0 = 300 if num_samples is None else int(num_samples * 0.6)
        n_c1 = 200 if num_samples is None else int(num_samples * 0.4)
        n_c0 = min(n_c0, len(c0_all))
        n_c1 = min(n_c1, len(c1_all))
        c0_sel = random.sample(c0_all, n_c0)
        c1_sel = random.sample(c1_all, n_c1)
        tasks = [(f, 0) for f in c0_sel] + [(f, 1) for f in c1_sel]
        print(f"[*] Chế độ 'representative': Lấy ngẫu nhiên {n_c0} ảnh Class 0 và {n_c1} ảnh Class 1 (Tổng: {len(tasks)} ảnh).")

    elif mode == "full":
        tasks = [(f, 0) for f in c0_all] + [(f, 1) for f in c1_all]
        print(f"[*] Chế độ 'full': Chạy toàn bộ dữ liệu CSIRO gồm {len(c0_all)} ảnh Class 0 và {len(c1_all)} ảnh Class 1 (Tổng: {len(tasks)} ảnh).")

    else:
        raise ValueError(f"Chế độ không hợp lệ: '{mode}'. Chọn trong ['sample', 'fast', 'representative', 'full'].")

    random.shuffle(tasks)
    return tasks


def run_benchmark(
    data_dir: str = "data",
    mode: str = "representative",
    num_samples: int = None,
    output_csv: str = "outputs/benchmark_results.csv",
    num_workers: int = None,
) -> Dict[str, Any]:
    """Thực hiện chạy kiểm thử benchmark và tính toán các chỉ số CDIO."""
    os.makedirs(os.path.dirname(output_csv), exist_ok=True)
    tasks = load_dataset_tasks(data_dir=data_dir, mode=mode, num_samples=num_samples)
    total_imgs = len(tasks)

    if num_workers is None:
        num_workers = min(os.cpu_count() or 4, 12)

    print("\n" + "=" * 70)
    print(" BẮT ĐẦU CHẠY THỰC NGHIỆM ĐỊNH LƯỢNG PIPELINE SENTINEL-1 SAR")
    print("=" * 70)
    print(f" - Tổng số mẫu: {total_imgs} ảnh SAR")
    print(f" - Số luồng xử lý song song (Workers): {num_workers}")
    print(f" - Tệp lưu trữ kết quả: {output_csv}")
    print("=" * 70)

    t_start = time.time()
    results: List[Dict[str, Any]] = []

    with ProcessPoolExecutor(max_workers=num_workers) as executor:
        for idx, res in enumerate(executor.map(_worker_task, tasks, chunksize=20), 1):
            results.append(res)
            if idx % 100 == 0 or idx == total_imgs:
                elapsed = time.time() - t_start
                rate = idx / (elapsed + 1e-6)
                pct = (idx / total_imgs) * 100.0
                print(f"   [{idx:>4}/{total_imgs}] Hoàn thành {pct:5.1f}% | Tốc độ: {rate:5.1f} ảnh/s")

    total_wall_time = time.time() - t_start
    print(f"\n[+] Đã hoàn thành xử lý {total_imgs} ảnh trong {total_wall_time:.2f} giây!")

    # 1. Lưu toàn bộ kết quả ra file CSV
    valid_results = [r for r in results if r.get("error") is None]
    fieldnames = [
        "filename", "true_label", "pred_label", "is_correct",
        "num_blobs", "oil_detected_count", "max_area", "max_contrast",
        "max_damping", "max_border_grad", "max_elongation", "max_complexity",
        "otsu_thresh", "otsu_separability", "scene_mean", "latency_ms"
    ]

    with open(output_csv, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for r in valid_results:
            writer.writerow(r)
    print(f"[+] Đã ghi nhật ký chi tiết vào: {output_csv}")

    # 2. Tính toán ma trận nhầm lẫn và các chỉ số CDIO
    tp = sum(1 for r in valid_results if r["true_label"] == 1 and r["pred_label"] == 1)
    fn = sum(1 for r in valid_results if r["true_label"] == 1 and r["pred_label"] == 0)
    fp = sum(1 for r in valid_results if r["true_label"] == 0 and r["pred_label"] == 1)
    tn = sum(1 for r in valid_results if r["true_label"] == 0 and r["pred_label"] == 0)

    total_eval = len(valid_results)
    accuracy = (tp + tn) / total_eval if total_eval > 0 else 0.0
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    specificity = tn / (tn + fp) if (tn + fp) > 0 else 0.0
    f1_score = 2.0 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0

    latencies = [r["latency_ms"] for r in valid_results if r["latency_ms"] > 0]
    mean_lat = float(np.mean(latencies)) if latencies else 0.0
    std_lat = float(np.std(latencies)) if latencies else 0.0
    fps = 1000.0 / mean_lat if mean_lat > 0 else 0.0

    metrics = {
        "total_samples": total_eval,
        "TP": tp,
        "FN": fn,
        "FP": fp,
        "TN": tn,
        "accuracy": accuracy,
        "precision": precision,
        "recall": recall,
        "specificity": specificity,
        "f1_score": f1_score,
        "mean_latency_ms": mean_lat,
        "std_latency_ms": std_lat,
        "fps": fps,
        "wall_time_sec": total_wall_time,
    }

    # In báo cáo bảng định lượng chuẩn CDIO
    print("\n" + "=" * 70)
    print(" BẢNG TỔNG HỢP KẾT QUẢ ĐÁNH GIÁ ĐỊNH LƯỢNG CHUẨN CDIO (UTC)")
    print("=" * 70)
    print(f" {'Chỉ số đánh giá (Evaluation Metric)':<38} | {'Giá trị đạt được':<25}")
    print("-" * 70)
    print(f" {'Tổng số mẫu kiểm thử':<38} | {total_eval} ảnh SAR")
    print(f" {'True Positives (TP - Dầu đúng)':<38} | {tp} ảnh")
    print(f" {'False Negatives (FN - Bỏ sót dầu)':<38} | {fn} ảnh")
    print(f" {'True Negatives (TN - Biển sạch đúng)':<38} | {tn} ảnh")
    print(f" {'False Positives (FP - Báo động giả)':<38} | {fp} ảnh")
    print("-" * 70)
    print(f" {'Độ chính xác toàn cục (Accuracy)':<38} | {accuracy * 100:6.2f} %")
    print(f" {'Độ chuẩn xác (Precision)':<38} | {precision * 100:6.2f} %")
    print(f" {'Độ nhạy / Thu hồi (Recall)':<38} | {recall * 100:6.2f} %")
    print(f" {'Độ đặc hiệu (Specificity)':<38} | {specificity * 100:6.2f} %")
    print(f" {'Điểm F1 tổng hòa (F1-Score)':<38} | {f1_score * 100:6.2f} %")
    print("-" * 70)
    print(f" {'Thời gian xử lý trung bình mỗi ảnh':<38} | {mean_lat:6.2f} ± {std_lat:.2f} ms")
    print(f" {'Tốc độ xử lý khung hình (Throughput)':<38} | {fps:6.1f} FPS (Khung hình/s)")
    print("=" * 70 + "\n")

    return metrics


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Chạy Benchmark thực nghiệm trên dữ liệu SAR Sentinel-1")
    parser.add_argument("--mode", type=str, default="representative", choices=["sample", "fast", "representative", "full"],
                        help="Chế độ chạy: sample (10 ảnh), fast (200 ảnh), representative (500 ảnh), full (toàn bộ)")
    parser.add_argument("--num-samples", type=int, default=None, help="Số lượng mẫu kiểm thử tùy chỉnh")
    parser.add_argument("--workers", type=int, default=None, help="Số lượng tiến trình song song")
    parser.add_argument("--output-csv", type=str, default="outputs/benchmark_results.csv", help="Đường dẫn file CSV kết quả")
    args = parser.parse_args()

    run_benchmark(
        data_dir="data",
        mode=args.mode,
        num_samples=args.num_samples,
        output_csv=args.output_csv,
        num_workers=args.workers,
    )
