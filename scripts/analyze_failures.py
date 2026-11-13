"""Post-selection diagnostics; never trains, tunes, or changes the frozen model."""

import hashlib
import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from sar_oil.data import read_pair, records
from sar_oil.evaluation import counts, summarize
from sar_oil.models import RegionModel
from sar_oil.pipeline import candidates, predict
from sar_oil.provenance import ensure_run


def distribution(values):
    """Population SD across defined per-image values; undefined values are counted."""
    valid = np.asarray([v for v in values if v is not None], dtype=float)
    return {
        "defined": len(valid),
        "undefined": len(values) - len(valid),
        "mean": float(valid.mean()) if len(valid) else None,
        "std_population": float(valid.std(ddof=0)) if len(valid) else None,
        "min": float(valid.min()) if len(valid) else None,
        "max": float(valid.max()) if len(valid) else None,
    }


def main():
    ensure_run()
    source = ROOT / "results/sos"
    dest = source / "diagnostics"
    dest.mkdir(exist_ok=True)
    evaluation = json.loads((source / "evaluation.json").read_text())
    selected = json.loads((source / "selected.json").read_text())
    model = RegionModel.load(source / selected["model_file"])
    report = {"scope": "Post-selection descriptive analysis; no model changes", "experiments": {}}
    keys = ("precision", "recall", "f1", "pixel_iou", "dice", "fp_per_image")
    for name, experiment in evaluation.items():
        if name == "provenance":
            continue
        rows = experiment["per_image"]
        assert summarize([r["counts"] for r in rows]) == experiment["metrics"]
        per = [summarize([r["counts"]]) for r in rows]
        report["experiments"][name] = {
            "micro": experiment["metrics"],
            "per_image": {k: distribution([r[k] for r in per]) for k in keys},
            "recorded_worker_seconds": distribution([r["seconds"] for r in rows]),
        }
    rows = evaluation["test_final"]["per_image"]
    by_id = {r["id"]: r for r in records("test")}
    chosen = []
    for criterion, score in (
        ("largest_false_positive_count", lambda r: r["counts"]["fp"]),
        ("largest_false_negative_count", lambda r: r["counts"]["fn"]),
        ("largest_pixel_error", lambda r: r["counts"]["union"] - r["counts"]["intersection"]),
    ):
        row = max(
            (r for r in rows if r["id"] not in [x[1]["id"] for x in chosen]),
            key=lambda r: (score(r), r["id"]),
        )
        chosen.append((criterion, row))
    cases = []
    for index, (criterion, row) in enumerate(chosen, 1):
        image, truth = read_pair(by_id[row["id"]])
        filtered, labels = candidates(image, selected["config"])
        prediction, _ = predict(image, selected["config"], model)
        actual = counts(prediction, truth)
        assert actual == row["counts"], row["id"]
        proposal = counts(labels > 0, truth)
        errors = np.zeros((*truth.shape, 3))
        errors[prediction & truth] = [0, 1, 0]
        errors[prediction & ~truth] = [1, 0, 0]
        errors[~prediction & truth] = [0, 0, 1]
        fig, axes = plt.subplots(2, 3, figsize=(10, 7))
        for ax, img, title in zip(
            axes.flat,
            [image, filtered, truth, labels > 0, prediction, errors],
            [
                row["id"],
                "Lee filtered",
                "Ground truth",
                "Proposals",
                "Frozen prediction",
                "Pixel TP green / FP red / FN blue",
            ],
        ):
            ax.imshow(img, cmap="gray", vmin=0, vmax=1)
            ax.set_title(title, fontsize=9)
            ax.axis("off")
        fig.suptitle(f"{criterion}: TP={actual['tp']}, FP={actual['fp']}, FN={actual['fn']}")
        fig.tight_layout()
        filename = f"failure_{index}.png"
        fig.savefig(dest / filename, dpi=160)
        plt.close(fig)
        cases.append(
            {
                "id": row["id"],
                "selection_rule": criterion,
                "figure": filename,
                "proposal_counts": proposal,
                "final_counts": actual,
                "truth_pixels_missing_from_proposals": int((truth & (labels == 0)).sum()),
                "truth_pixels_removed_by_classifier": int(
                    (truth & (labels > 0) & ~prediction).sum()
                ),
            }
        )
    report["failure_cases"] = cases
    report["sha256"] = {
        p.name: hashlib.sha256(p.read_bytes()).hexdigest()
        for p in [
            source / "evaluation.json",
            source / "selected.json",
            source / selected["model_file"],
            Path(__file__),
        ]
    }
    (dest / "diagnostics.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    lines = [
        "# Thống kê và ba trường hợp thất bại",
        "",
        "Phân tích mô tả sau lựa chọn, không dùng để đổi cấu hình. Tái tạo: `python scripts/analyze_failures.py`.",
        "",
        "Micro cộng TP/FP/FN trước khi chia. Macro là trung bình từng ảnh có mẫu số xác định; báo rõ số ảnh bị loại do chỉ số không xác định. Độ lệch chuẩn là độ phân tán giữa các patch (ddof=0), không phải sai số giữa các lần huấn luyện hay khoảng tin cậy theo cảnh.",
        "",
        "| Thí nghiệm | F1 micro | F1 từng ảnh: mean ± SD | Số ảnh xác định / không xác định |",
        "|---|---:|---:|---:|",
    ]
    for name, result in report["experiments"].items():
        stat = result["per_image"]["f1"]
        lines.append(
            f"| {name} | {result['micro']['f1']:.5f} | {stat['mean']:.5f} ± {stat['std_population']:.5f} | {stat['defined']} / {stat['undefined']} |"
        )
    lines += [
        "",
        "Thời gian trong JSON là số đo từng worker từ lần chạy đã lưu, có thể chịu tranh chấp CPU; không coi là benchmark độ trễ tuần tự.",
    ]
    for case in cases:
        a, b = case["proposal_counts"], case["final_counts"]
        lines += [
            "",
            f"## {case['id']} — {case['selection_rule']}",
            "",
            f"![Các bước xử lý]({case['figure']})",
            "",
            f"Trước classifier: TP/FP/FN={a['tp']}/{a['fp']}/{a['fn']}; sau classifier: {b['tp']}/{b['fp']}/{b['fn']}.",
            f"Có {case['truth_pixels_missing_from_proposals']} pixel dầu GT không có trong ứng viên; classifier loại thêm {case['truth_pixels_removed_by_classifier']} pixel dầu GT.",
            "Đây là bằng chứng vị trí mất thông tin theo từng bước. Classifier chỉ loại vùng, không thể khôi phục pixel thiếu hoặc sửa đường biên. FP mức đối tượng là vùng không ghép được với GT ở IoU≥0,5: có thể do phân mảnh một vùng dầu thật, không nhất thiết là pixel nền bị gọi nhầm dầu. Không thể quy lỗi cụ thể cho mưa, gió yếu hay màng sinh học vì SOS không có nhãn phụ này.",
        ]
    lines += [
        "",
        "Hướng kiểm tra tiếp: khảo sát ngưỡng thích nghi để cải thiện vùng ứng viên và recall đối tượng nhỏ; kiểm tra phân tách vùng dính; bổ sung nhãn look-alike độc lập. Các thay đổi cần validation và tập kiểm tra mới, không tối ưu theo ba ảnh này.",
    ]
    (dest / "REPORT.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Saved descriptive statistics and {len(cases)} verified failures to {dest}")


if __name__ == "__main__":
    main()
