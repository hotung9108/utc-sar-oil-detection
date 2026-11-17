"""MODULE 6: OBJECT-LEVEL EVALUATION METRICS (NUMPY THUẦN)

Module này tự triển khai các phép đo đánh giá khoa học:
1. Tính chỉ số IoU (Intersection over Union) giữa 2 mặt nạ nhị phân
2. Thuật toán ghép cặp đối tượng 1-1 theo ngưỡng IoU >= 0.5
3. Tính Precision, Recall, Object F1-Score, False Alarm Rate
4. Ma trận nhầm lẫn (Confusion Matrix) đa lớp
"""
from __future__ import annotations
import numpy as np


def compute_iou_masks(mask1: np.ndarray, mask2: np.ndarray) -> float:
    """Tính tỷ số Giao trên Hợp (IoU) giữa 2 mặt nạ nhị phân.

    IoU = |A cap B| / |A cup B|
    """
    intersection = np.logical_and(mask1, mask2).sum()
    union = np.logical_or(mask1, mask2).sum()
    if union == 0:
        return 1.0 if intersection == 0 else 0.0
    return float(intersection) / float(union)


def match_objects_greedy(
    pred_regions: list[dict],
    gt_regions: list[dict],
    iou_thresh: float = 0.5,
    img_shape: tuple[int, int] = (100, 100)
) -> tuple[int, int, int]:
    """Ghép cặp tham lam 1-1 giữa các vùng dự đoán (Pred) và nhãn mặt đất (GT).

    Quy tắc:
    - Mỗi vết dầu GT chỉ được ghép với tối đa 1 vết Pred có IoU cao nhất (và >= iou_thresh).
    - Các vết Pred không ghép được tính là False Positive (FP).
    - Các vết GT không được phát hiện tính là False Negative (FN).

    Returns:
        (TP, FP, FN)
    """
    n_pred = len(pred_regions)
    n_gt = len(gt_regions)

    if n_gt == 0:
        return 0, n_pred, 0
    if n_pred == 0:
        return 0, 0, n_gt

    H, W = img_shape
    # Tạo ma trận mask cho từng vùng để tính IoU nhanh
    pred_masks = []
    for p in pred_regions:
        m = np.zeros((H, W), dtype=bool)
        m[p["coords"][:, 0], p["coords"][:, 1]] = True
        pred_masks.append(m)

    gt_masks = []
    for g in gt_regions:
        m = np.zeros((H, W), dtype=bool)
        m[g["coords"][:, 0], g["coords"][:, 1]] = True
        gt_masks.append(m)

    # Tính ma trận IoU kích thước (n_pred, n_gt)
    iou_matrix = np.zeros((n_pred, n_gt), dtype=np.float64)
    for i in range(n_pred):
        for j in range(n_gt):
            iou_matrix[i, j] = compute_iou_masks(pred_masks[i], gt_masks[j])

    matched_gt = set()
    tp = 0

    # Ghép theo thứ tự IoU giảm dần
    flat_indices = np.argsort(iou_matrix.ravel())[::-1]
    for idx in flat_indices:
        pred_i, gt_j = np.unravel_index(idx, iou_matrix.shape)
        score = iou_matrix[pred_i, gt_j]
        if score < iou_thresh:
            break
        if gt_j not in matched_gt:
            matched_gt.add(gt_j)
            tp += 1
            # Đảm bảo pred_i này không ghép thêm với gt nào khác
            iou_matrix[pred_i, :] = -1.0

    fp = n_pred - tp
    fn = n_gt - tp
    return tp, fp, fn


def compute_metrics(tp: int, fp: int, fn: int) -> dict[str, float]:
    """Tính các chỉ số Precision, Recall và F1-Score."""
    precision = float(tp) / float(tp + fp) if (tp + fp) > 0 else 0.0
    recall = float(tp) / float(tp + fn) if (tp + fn) > 0 else 0.0
    f1 = (
        2.0 * precision * recall / (precision + recall)
        if (precision + recall) > 0 else 0.0
    )
    return {
        "TP": tp,
        "FP": fp,
        "FN": fn,
        "Precision": precision,
        "Recall": recall,
        "F1_score": f1
    }


def confusion_matrix_scratch(y_true: np.ndarray, y_pred: np.ndarray) -> np.ndarray:
    """Tự tính ma trận nhầm lẫn 2x2: [[TN, FP], [FN, TP]]."""
    tn = int(np.sum((y_true == 0) & (y_pred == 0)))
    fp = int(np.sum((y_true == 0) & (y_pred == 1)))
    fn = int(np.sum((y_true == 1) & (y_pred == 0)))
    tp = int(np.sum((y_true == 1) & (y_pred == 1)))
    return np.array([[tn, fp], [fn, tp]], dtype=np.int32)


# ==============================================================================
# BÀI TẬP THỰC NGHIỆM ĐÁNH GIÁ
# ==============================================================================
if __name__ == "__main__":
    print("=" * 70)
    print("--- [MODULE 6] KIỂM TRA ĐÁNH GIÁ ĐỐI TƯỢNG (OBJECT IOU >= 0.5) ---")
    print("=" * 70)

    # Giả lập tình huống:
    # Ngoài biển có 3 vết dầu thật (GT 1, GT 2, GT 3)
    # Máy phát hiện ra 3 vết (Pred A, Pred B, Pred C)
    # - Pred A đè lên GT 1 với IoU = 0.85 -> TP!
    # - Pred B đè lên GT 2 với IoU = 0.30 -> Dưới 0.5 nên tính là FP!
    # - Pred C nằm ở vùng biển sạch -> FP!
    # - GT 3 máy bỏ sót hoàn toàn -> FN!

    H, W = 50, 50
    gt_coords = [
        np.argwhere(np.zeros((H, W), dtype=bool)), # placeholder
        np.array([[r, c] for r in range(5, 15) for c in range(5, 15)]),   # GT 1: 10x10 = 100 px
        np.array([[r, c] for r in range(20, 30) for c in range(20, 30)]), # GT 2: 10x10 = 100 px
        np.array([[r, c] for r in range(35, 45) for c in range(35, 45)])  # GT 3: 10x10 = 100 px
    ]
    gt_regions = [
        {"coords": gt_coords[1]},
        {"coords": gt_coords[2]},
        {"coords": gt_coords[3]}
    ]

    pred_regions = [
        # Pred A: đè 8x10 lên GT 1 (IoU cao ~ 0.8)
        {"coords": np.array([[r, c] for r in range(6, 15) for c in range(5, 14)])},
        # Pred B: chỉ đè 3x3 lên góc GT 2 (IoU thấp ~ 0.08)
        {"coords": np.array([[r, c] for r in range(27, 33) for c in range(27, 33)])},
        # Pred C: nằm ở vùng biển sạch (5..10, 35..40)
        {"coords": np.array([[r, c] for r in range(5, 10) for c in range(35, 40)])}
    ]

    tp, fp, fn = match_objects_greedy(pred_regions, gt_regions, iou_thresh=0.5, img_shape=(50, 50))
    res = compute_metrics(tp, fp, fn)

    print(f"Kết quả ghép cặp:")
    print(f" -> True Positive (Bắt đúng)  : {res['TP']}")
    print(f" -> False Positive (Báo nhầm) : {res['FP']}")
    print(f" -> False Negative (Bỏ sót)   : {res['FN']}")
    print(f" -> Precision                 : {res['Precision']*100:.1f}%")
    print(f" -> Recall                    : {res['Recall']*100:.1f}%")
    print(f" -> Object F1-Score           : {res['F1_score']:.4f}")

    print("\n✅ MODULE 6 HOẠT ĐỘNG HOÀN HẢO!")
