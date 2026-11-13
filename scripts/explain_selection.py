"""Re-run controlled filter comparisons and save auditable selection evidence.

Uses validation only. Does not modify the selected model or evaluate test again.
"""

import argparse
import hashlib
import json
import os
import sys
from pathlib import Path

for name in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(name, "1")
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
import numpy as np
from scipy import ndimage

from sar_oil import core, reference
from sar_oil.data import read_pair, records
from sar_oil.evaluation import counts, summarize
from sar_oil.experiments import FILTERS, OUT, pool_map, rank, write_json
from sar_oil.provenance import ensure_run

DEST = OUT / "selection_evidence"
CONTROL_FILTERS = FILTERS + [{"name": "median", "size": 7}, {"name": "mean", "size": 7}]


def measure(row):
    image, truth = read_pair(row)
    results = []
    verification = []
    for config in CONTROL_FILTERS:
        filtered = (
            ndimage.uniform_filter(image, size=7, mode="mirror")
            if config["name"] == "mean"
            else reference.filter_image(image, **config)
        )
        if config not in FILTERS:
            custom = (
                core.mean_filter(image, 7)
                if config["name"] == "mean"
                else core.filter_image(image, **config)
            )
            error = float(np.max(np.abs(custom - filtered)))
            assert np.allclose(custom, filtered, atol=1e-6, rtol=1e-5), (row["id"], config, error)
            verification.append({"filter": config, "max_abs_error": error, "passed": True})
        prediction = reference.postprocess(
            reference.threshold(filtered, name="otsu"), operation="none", min_area=16
        )
        results.append(counts(prediction, truth))
    return {"image_id": row["id"], "counts": results, "supplementary_numpy_checks": verification}


def main(workers):
    ensure_run()
    DEST.mkdir(parents=True, exist_ok=True)
    screen = json.loads((OUT / "screen.json").read_text())
    validation = json.loads((OUT / "validation.json").read_text())
    selected = json.loads((OUT / "selected.json").read_text())
    raw = pool_map(measure, records("validation"), workers)
    write_json(
        DEST / "per_image.json", {"split": "validation", "filters": CONTROL_FILTERS, "records": raw}
    )
    controlled = []
    for i, config in enumerate(CONTROL_FILTERS):
        metric = summarize([r["counts"][i] for r in raw])
        original = next(
            (
                r
                for r in screen
                if r["config"]["filter"] == config and r["config"]["threshold"] == {"name": "otsu"}
            ),
            None,
        )
        if original is not None:
            assert metric == original["metrics"], ("Re-run differs from original evidence", config)
        controlled.append(
            {
                "filter": config,
                "metrics": metric,
                "original_id": original["id"] if original else None,
                "supplementary_after_selection": original is None,
            }
        )
    # Paired resampling of patches; compute micro F1 after summing sampled counts.
    statistics = np.array(
        [
            [[r["counts"][i][k] for k in ("tp", "fp", "fn")] for r in raw]
            for i in range(len(CONTROL_FILTERS))
        ]
    )
    rng = np.random.default_rng(2026)
    bootstrap = []
    for _ in range(2000):
        sample = rng.integers(0, len(raw), len(raw))
        total = statistics[:, sample, :].sum(axis=1)
        bootstrap.append(
            2 * total[:, 0] / np.maximum(2 * total[:, 0] + total[:, 1] + total[:, 2], 1)
        )
    bootstrap = np.array(bootstrap)
    lee = FILTERS.index({"name": "lee", "size": 7, "looks": 4})
    for i, row in enumerate(controlled):
        delta = bootstrap[:, lee] - bootstrap[:, i]
        row["lee_minus_filter_f1"] = controlled[lee]["metrics"]["f1"] - row["metrics"]["f1"]
        row["paired_patch_bootstrap_95_interval"] = np.quantile(delta, [0.025, 0.975]).tolist()
    best_by_family = []
    for family in ("none", "median", "gaussian", "lee"):
        rows = [r for r in screen if r["config"]["filter"]["name"] == family]
        best = max(rows, key=lambda r: r["metrics"]["f1"] or 0)
        best_by_family.append(dict(best, configurations_tried=len(rows)))
    assert [r["id"] for r in rank(screen)] == [r["id"] for r in screen]
    assert [r["id"] for r in rank(validation)] == [r["id"] for r in validation]
    strict = max(validation, key=lambda r: r["metrics"]["f1"] or 0)
    near = [
        r for r in validation if (r["metrics"]["f1"] or 0) >= (strict["metrics"]["f1"] or 0) - 0.005
    ]
    evidence = {
        "split": "validation",
        "images": len(raw),
        "controlled_protocol": {
            "threshold": "otsu",
            "morphology": "none",
            "min_area": 16,
            "classifier": None,
        },
        "controlled_filters": controlled,
        "supplementary_numpy_checks": [
            {
                "filter": config,
                "images": len(raw),
                "max_abs_error": max(
                    check["max_abs_error"]
                    for row in raw
                    for check in row["supplementary_numpy_checks"]
                    if check["filter"] == config
                ),
                "passed": True,
            }
            for config in CONTROL_FILTERS
            if config not in FILTERS
        ],
        "family_best_over_screen": best_by_family,
        "screen_rows": len(screen),
        "validation_rows": len(validation),
        "screen_top3": screen[:3],
        "strict_f1_winner": strict,
        "selected_id": selected["id"],
        "selection_rule": {
            "f1_band": 0.005,
            "priority": ["recall descending", "recorded seconds ascending", "id ascending"],
        },
        "near_best_candidates": near,
        "validation_top10": validation[:10],
        "bootstrap": {
            "seed": 2026,
            "replicates": 2000,
            "unit": "patch",
            "interpretation": "Exploratory percentile intervals; post-selection, not scene-independent, no multiplicity correction",
        },
        "source_sha256": {
            name: hashlib.sha256((OUT / name).read_bytes()).hexdigest()
            for name in ("screen.json", "validation.json", "selected.json")
        },
        "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    }
    write_json(DEST / "evidence.json", evidence)
    render_report(evidence, selected)
    print(
        "Saved controlled comparison for",
        len(CONTROL_FILTERS),
        "filters on",
        len(raw),
        "validation images; original 11 configurations match original run; 2 supplementary controls verified against NumPy.",
    )


def render_report(evidence, selected):
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    rows = evidence["controlled_filters"]
    labels = [json.dumps(r["filter"], sort_keys=True) for r in rows]
    fig, ax = plt.subplots(figsize=(11, 6))
    ax.barh(
        labels,
        [r["metrics"]["f1"] for r in rows],
        color=[
            "#ca6f1e" if r["filter"] == selected["config"]["filter"] else "#3478a8" for r in rows
        ],
    )
    ax.set(
        xlabel="Object micro F1 (IoU >= 0.5)",
        title="671 validation patches: fixed Otsu, min area 16, no classifier",
    )
    ax.invert_yaxis()
    fig.tight_layout()
    fig.savefig(DEST / "filters_fixed_otsu.png", dpi=160)
    plt.close(fig)
    text = """# Bằng chứng lựa chọn thuật toán và bộ lọc Lee

Tái tạo: `python scripts/explain_selection.py --workers 6`. Code chạy **13 cấu hình lọc trên toàn bộ 671 ảnh validation**, giữ Otsu, morphology none và min_area16 giống nhau. 11 cấu hình gốc được assert khớp kết quả trước; mean7 và median7 là hai đối chứng bổ sung sau lựa chọn để kiểm tra ảnh hưởng cửa sổ 7×7. Hai phép lọc bổ sung còn được đối chiếu NumPy/reference trên toàn bộ 671 ảnh. File `per_image.json` lưu TP/FP/FN cùng các số đếm và sai số cho từng ảnh/từng bộ lọc; `evidence.json` lưu tổng hợp, hash nguồn, quy tắc chọn và khoảng bootstrap. Không đọc ảnh test, không thay mô hình đã khóa.

## Vì sao đưa Lee vào khảo sát?

Đây là giả thuyết để thử, không phải kết luận trước thực nghiệm. Trong biến thể đang cài, với trung bình cục bộ m, phương sai v và tham số L:

`noise = m²/L; w = max(v−noise,0)/max(v,1e−12); output = m + w·(input−m)`.

Nếu phương sai cục bộ không vượt mức noise ước lượng, w=0 và đầu ra là trung bình cục bộ. Khi v lớn hơn, đầu ra giữ lại một phần sai lệch so với trung bình. Cơ chế điều chỉnh theo thống kê cục bộ là lý do đáng khảo sát cùng median/Gaussian. Nó **không bảo đảm giữ đúng biên dầu hoặc tăng F1**. Đây là biến thể công thức trong `core.filter_image`, không tuyên bố mọi biến thể Lee giống nhau. PNG SOS chưa được xác nhận là sigma0 tuyến tính, nên L=4 là tham số thử nghiệm, không phải số looks vật lý được xác minh.

## So sánh có kiểm soát: chỉ thay bộ lọc

| Bộ lọc | TP | FP | FN | Precision | Recall | F1 | Pixel IoU | ΔF1 Lee7,L4 − bộ lọc | Khoảng bootstrap 95% của Δ |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
"""
    for r in rows:
        m = r["metrics"]
        low, high = r["paired_patch_bootstrap_95_interval"]
        text += f"| `{r['filter']}` | {m['tp']} | {m['fp']} | {m['fn']} | {m['precision']:.5f} | {m['recall']:.5f} | {m['f1']:.5f} | {m['pixel_iou']:.5f} | {r['lee_minus_filter_f1']:+.5f} | [{low:+.5f}, {high:+.5f}] |\n"
    text += "\n![So sánh bộ lọc cùng Otsu](filters_fixed_otsu.png)\n\nKhoảng trên dùng 2000 lần lấy mẫu lại **cùng chỉ số patch** cho các bộ lọc, tính micro F1 từ tổng TP/FP/FN mỗi lần. Đây là phân tích thăm dò sau khi đã xem validation, chưa hiệu chỉnh nhiều so sánh và không bảo đảm độc lập theo cảnh. Không coi khoảng này là chứng minh ưu thế phổ quát.\n"
    text += "\nĐối chứng bổ sung cùng cửa sổ 7×7 (không thuộc grid chọn mô hình ban đầu):\n\n"
    for r in rows:
        if r["supplementary_after_selection"]:
            text += f"- `{r['filter']}`: F1={r['metrics']['f1']:.6f}, ΔF1 so với Lee7,L4={-r['lee_minus_filter_f1']:+.6f}.\n"
    l1 = next(r for r in rows if r["filter"] == {"name": "lee", "size": 7, "looks": 1})
    low, high = l1["paired_patch_bootstrap_95_interval"]
    text += f"\nLee7,L4 − Lee7,L1 có khoảng bootstrap [{low:+.6f}, {high:+.6f}]. " + (
        "Khoảng chứa 0: chưa có bằng chứng rõ ràng L=4 tốt hơn L=1 trong phân tích này.\n"
        if low <= 0 <= high
        else "Đây vẫn là khoảng thăm dò sau lựa chọn.\n"
    )
    text += "\n## Kết quả tốt nhất mỗi họ trong 110 cấu hình\n\n| Họ | Số cấu hình đã thử | Cấu hình đạt F1 lớn nhất | F1 | Recall |\n|---|---:|---|---:|---:|\n"
    for r in evidence["family_best_over_screen"]:
        text += f"| {r['config']['filter']['name']} | {r['configurations_tried']} | `{r['config']}` | {r['metrics']['f1']:.5f} | {r['metrics']['recall']:.5f} |\n"
    text += "\nLee được thử nhiều cấu hình hơn các họ khác; bảng lấy cực đại này có lợi thế do kích thước grid. Bảng giữ cố định Otsu phía trên giúp tách bớt ảnh hưởng ngưỡng, nhưng vẫn chỉ đánh giá giai đoạn tạo ứng viên. Chưa thử mọi bộ lọc kết hợp mọi classifier, nên không thể kết luận Lee luôn tốt nhất cho pipeline cuối.\n"
    text += "\n## Quy tắc lựa chọn cuối có gì mang tính chủ quan?\n\nĐã chạy 110 cấu hình tạo ứng viên; giữ 3 cấu hình theo F1-band/Recall/runtime, rồi chạy 729 tổ hợp hình thái/diện tích/đặc trưng/classifier. Đây là tìm kiếm theo giai đoạn, không phải exhaustive search toàn bộ không gian. Ngưỡng F1-band **0,005 là quy ước**, không phải định lý hoặc khoảng tương đương thống kê.\n"
    best = evidence["strict_f1_winner"]
    text += f"\nNếu chỉ tối đa F1, cấu hình thắng là `{best['config']}`, `{best['kind']} {best['params']}`, F1={best['metrics']['f1']:.6f}, Recall={best['metrics']['recall']:.6f}. Cấu hình đã chọn có F1={selected['metrics']['f1']:.6f}, Recall={selected['metrics']['recall']:.6f}.\n"
    text += "\n| Thứ tự theo quy tắc đã dùng | Lọc | Nhóm | Classifier | F1 | Recall | Thời gian ghi nhận (s) |\n|---:|---|---|---|---:|---:|---:|\n"
    for i, r in enumerate(evidence["validation_top10"], 1):
        text += f"| {i} | `{r['config']['filter']}` | {r['group']} | `{r['kind']} {r['params']}` | {r['metrics']['f1']:.6f} | {r['metrics']['recall']:.6f} | {r['seconds']:.6f} |\n"
    text += """
C=10 và C=1 ở cấu hình đã chọn có cùng Recall/F1; C=10 đứng trước nhờ thời gian một lần thấp hơn. Thời gian gồm wrapper fit/evaluate và phụ thuộc tải máy; **chưa đủ chứng cứ khẳng định C=10 tốt hơn C=1**. Không thay cấu hình sau khi đã xem test. Nếu đổi tiêu chí lựa chọn hoặc mở rộng grid cần công bố một thực nghiệm mới và không gọi test đã dùng là tập hoàn toàn chưa xem.

## Đối chiếu NumPy không thay cho đánh giá chất lượng

`../verification_real.json` lưu sai số thực tế của từng phép toán trên 8 ảnh validation; `../model_comparison.json` lưu agreement, objective và hội tụ của classifier. Lee reference sử dụng thống kê SciPy ghép cùng công thức, **không phải API Lee độc lập**. Sai số nhỏ chứng minh hai triển khai gần nhau trong ca kiểm tra, không chứng minh phát hiện dầu tốt. Chất lượng phát hiện phải đọc TP/FP/FN so với mask SOS.

## Kết luận được phép đưa vào báo cáo

Trong grid ban đầu và split SOS đã khảo sát, Lee7,L4 + Otsu có F1 tạo ứng viên cao nhất, nên được đưa vào giai đoạn phân lớp. Các đối chứng mean7/median7 là khảo sát bổ sung, không được dùng để thay đổi mô hình sau khi đã xem test. Quy tắc có ưu tiên Recall dẫn đến cấu hình cuối đã công bố. Không có định lý bảo đảm đây là bộ lọc tốt nhất cho mọi ảnh SAR; chưa chứng minh tối ưu toàn cục hoặc khả năng triển khai trên biển Việt Nam. Otsu là ngưỡng toàn cục; Niblack thích nghi đã khảo sát nhưng không được chọn làm mặc định. Các giới hạn góc tới/gió/look-alike vẫn còn.
"""
    (DEST / "REPORT.md").write_text(text, encoding="utf-8")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workers", type=int, default=6)
    main(parser.parse_args().workers)
