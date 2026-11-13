"""Supplementary validation-only search constrained to adaptive thresholding.

Preserves the original selected model and every original test result.
"""

import argparse
import hashlib
import json
import os
import sys
import time
from pathlib import Path

for variable in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(variable, "1")
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
import numpy as np

from sar_oil.data import records
from sar_oil.evaluation import summarize
from sar_oil.experiments import (
    GROUPS,
    MODELS,
    OUT,
    _evaluate_image,
    digest,
    evaluate_regions,
    pool_map,
    region_data,
    training_arrays,
    write_json,
)
from sar_oil.models import RegionModel
from sar_oil.provenance import ensure_run

DEST = OUT / "adaptive"


def order(row):
    """Strict F1, recall, stable ID; no runtime-dependent tie-break."""
    return (-(row["metrics"]["f1"] or 0), -(row["metrics"]["recall"] or 0), row["id"])


def main(workers):
    ensure_run()
    DEST.mkdir(exist_ok=True)
    protected = [
        OUT / n for n in ("selected.json", "svm_model.json", "cart_model.json", "evaluation.json")
    ]
    before = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in protected}
    screen = json.loads((OUT / "screen.json").read_text())
    finalists = sorted(
        [r for r in screen if r["config"]["threshold"]["name"] == "niblack"], key=order
    )[:3]
    protocol = {
        "scope": "Supplementary post-selection validation analysis; no test read or tuning",
        "selection": "Top 3 adaptive proposal configurations by strict F1 then recall then ID",
        "stage2": "Fixed no morphology/min_area64 and all 8 features; 9 classifier settings per configuration",
        "limitations": "Not exhaustive; fixed stage2 choices inherited from previous experiment; same validation reused",
        "finalists": finalists,
        "protected_original_sha256": before,
        "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    }
    write_json(DEST / "protocol.json", protocol)
    rows = []
    for entry in finalists:
        config = dict(entry["config"], morphology={"operation": "none", "min_area": 64})
        X, y, training = training_arrays(region_data(config, "train", workers))
        validation = region_data(config, "validation", workers)
        for kind, params in MODELS:
            start = time.perf_counter()
            model = RegionModel(kind, GROUPS["all"], backend="reference", **params).fit(X, y)
            rows.append(
                {
                    "id": digest({"config": config, "kind": kind, "params": params}),
                    "config": config,
                    "kind": kind,
                    "params": params,
                    "group": "all",
                    "training": training,
                    "metrics": evaluate_regions(validation, model),
                    "seconds": time.perf_counter() - start,
                }
            )
        write_json(DEST / "validation.json", sorted(rows, key=order))
        print("Completed adaptive configuration", config, flush=True)
    comparisons = []
    for kind in ("cart", "svm"):
        entry = min((r for r in rows if r["kind"] == kind), key=order)
        X, y, _ = training_arrays(region_data(entry["config"], "train", workers))
        validation = region_data(entry["config"], "validation", workers)
        models = {}
        timings = {}
        for backend in ("reference", "numpy"):
            start = time.perf_counter()
            models[backend] = RegionModel(
                kind, GROUPS["all"], backend=backend, **entry["params"]
            ).fit(X, y)
            timings[backend] = time.perf_counter() - start
        custom = models["numpy"]
        V = np.concatenate([v["X"] for v in validation])
        compared = dict(
            entry,
            metrics=evaluate_regions(validation, custom),
            reference_metrics=evaluate_regions(validation, models["reference"]),
            agreement=float(np.mean(custom.predict(V) == models["reference"].predict(V))),
            converged=bool(custom.converged),
            fit_seconds=timings,
        )
        custom.save(DEST / f"{kind}_model.json")
        comparisons.append(compared)
    write_json(DEST / "model_comparison.json", comparisons)
    eligible = [r for r in comparisons if r["converged"]]
    if not eligible:
        raise RuntimeError("No converged NumPy finalist")
    winner = min(eligible, key=order)
    model_path = DEST / f"{winner['kind']}_model.json"
    raw = pool_map(
        _evaluate_image,
        [(r, winner["config"], str(model_path), "numpy", 128) for r in records("validation")],
        workers,
    )
    metrics = summarize([r["counts"] for r in raw])
    assert metrics == winner["metrics"], (
        "Full NumPy pipeline differs from cached reference features"
    )
    write_json(DEST / "validation_full_numpy.json", {"metrics": metrics, "per_image": raw})
    write_json(
        DEST / "selected.json", dict(winner, model_file=model_path.name, scope=protocol["scope"])
    )
    assert before == {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in protected}
    text = [
        "# Thực nghiệm bổ sung: ràng buộc ngưỡng thích nghi",
        "",
        "Tái tạo: `python scripts/adaptive_experiment.py --workers 6`. Không đọc tập test hoặc thay kết quả/mô hình cũ. Đây là phân tích bổ sung sau lựa chọn, tái sử dụng validation; không phải kiểm chứng độc lập mới.",
        "",
        "Từ 99 cấu hình Niblack đã khảo sát, lấy 3 cấu hình có F1 ứng viên cao nhất (hòa thì Recall rồi ID). Mỗi cấu hình dùng no morphology/min_area64, 8 đặc trưng và 9 cấu hình classifier: tổng 27 lần fit. Các lựa chọn cố định kế thừa thực nghiệm trước, không chứng minh tối ưu toàn cục. Chọn bằng F1 nghiêm ngặt; không dùng thời gian để phá hòa.",
        "",
        "| Classifier NumPy | Tham số | F1 validation | Recall | Agreement với thư viện | Hội tụ |",
        "|---|---|---:|---:|---:|---|",
    ]
    for row in comparisons:
        text.append(
            f"| {row['kind']} | {row['params']} | {row['metrics']['f1']:.6f} | {row['metrics']['recall']:.6f} | {row['agreement']:.6f} | {row['converged']} |"
        )
    text += [
        "",
        f"Cấu hình bổ sung chọn trên validation: `{winner['config']}`, `{winner['kind']} {winner['params']}`.",
        f"Toàn bộ pipeline NumPy chạy lại trên 671 ảnh validation: F1={metrics['f1']:.6f}, Precision={metrics['precision']:.6f}, Recall={metrics['recall']:.6f}. Số đếm từng ảnh lưu trong `validation_full_numpy.json`.",
        "",
        "Nhánh này đáp ứng thao tác ngưỡng thích nghi, chưa khắc phục thiếu góc tới/gió/nhãn look-alike. Chưa công bố test mới cho nhánh này; muốn kết luận tổng quát hóa phải có tập độc lập chưa sử dụng. Không gán kết quả test của nhánh Otsu cho nhánh Niblack.",
    ]
    (DEST / "REPORT.md").write_text("\n".join(text) + "\n", encoding="utf-8")
    print("Adaptive validation experiment complete", metrics, flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workers", type=int, default=6)
    main(parser.parse_args().workers)
