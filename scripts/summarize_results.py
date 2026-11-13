"""Build the report directly from executed JSON evidence, without hand-entered metrics."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results/sos"
load = lambda name: json.loads((OUT / name).read_text(encoding="utf-8"))
screen = load("screen.json")
validation = load("validation.json")
selected = load("selected.json")
comparison = load("model_comparison.json")
evaluation = load("evaluation.json")
fmt = lambda value: "N/A" if value is None else f"{value:.4f}"
text = """# Kết quả SOS từ lần chạy thực tế

Số liệu được tạo bởi `scripts/summarize_results.py` từ JSON thực nghiệm, không nhập tay. Đây là đánh giá mask dầu/nền trên PNG, không phải xác nhận khả năng cảnh báo biển Việt Nam hoặc phân biệt riêng gió yếu/màng sinh học/mưa.

## Dữ liệu và lựa chọn

Sentinel train 2683, validation 671, test 839; PALSAR val 776 đánh giá ngoài miền. Seed 2026, mask >=128. Mọi lựa chọn dùng validation, test chỉ báo cáo cuối. Thiếu metadata cảnh nên không chứng minh độc lập theo cảnh.

"""
text += f"Đã chạy **{len(screen)} cấu hình lọc/ngưỡng** và **{len(validation)} cấu hình vùng/đặc trưng/classifier**. Cấu hình cuối: `{json.dumps(selected['config'], ensure_ascii=False)}`; `{selected['kind']}`, tham số `{selected['params']}`, nhóm đặc trưng `{selected['group']}`.\n\n"
text += "## Đánh giá cuối — NumPy end-to-end\n\n| Thí nghiệm | Ảnh | Precision | Recall | F1 | Pixel IoU | FP/ảnh |\n|---|---:|---:|---:|---:|---:|---:|\n"
for key, value in evaluation.items():
    if key == "provenance":
        continue
    m = value["metrics"]
    text += (
        f"| {key} | {m['images']} | "
        + " | ".join(fmt(m[c]) for c in ("precision", "recall", "f1", "pixel_iou", "fp_per_image"))
        + " |\n"
    )
final = evaluation["test_final"]["metrics"]
baseline = evaluation["test_baseline"]["metrics"]
ablation = evaluation["test_no_classifier"]["metrics"]
text += f"\nSo với baseline, ΔF1 = {final['f1'] - baseline['f1']:+.4f}; ΔRecall = {final['recall'] - baseline['recall']:+.4f}; ΔFP/ảnh = {final['fp_per_image'] - baseline['fp_per_image']:+.4f}. So với cấu hình bỏ classifier, ΔF1 = {final['f1'] - ablation['f1']:+.4f}; ΔRecall = {final['recall'] - ablation['recall']:+.4f}; ΔFP/ảnh = {final['fp_per_image'] - ablation['fp_per_image']:+.4f}.\n"
text += "\nĐây là thay đổi đo được trên split SOS này, không là bằng chứng cải tiến tổng quát hoặc kiểm định ý nghĩa thống kê. Đối tượng suy ra từ semantic mask, ghép một-một IoU>=0.5; F1 tính micro từ tổng số đếm. Không bỏ GT nhỏ.\n"
text += "\n## Lọc/ngưỡng: kết quả tốt nhất mỗi họ ngưỡng theo F1\n\n| Ngưỡng | Lọc | Precision | Recall | F1 |\n|---|---|---:|---:|---:|\n"
for family in ("otsu", "niblack"):
    r = max(
        (r for r in screen if r["config"]["threshold"]["name"] == family),
        key=lambda r: r["metrics"]["f1"] or 0,
    )
    text += (
        f"| {r['config']['threshold']} | {r['config']['filter']} | "
        + " | ".join(fmt(r["metrics"][c]) for c in ("precision", "recall", "f1"))
        + " |\n"
    )
text += "\n## NumPy so với thư viện\n\n| Mô hình | Nhóm | Agreement | F1 NumPy | F1 sklearn | Hội tụ | Fit NumPy (s) | Fit thư viện (s) |\n|---|---|---:|---:|---:|---|---:|---:|\n"
for r in comparison:
    text += f"| {r['kind']} | {r['group']} | {fmt(r['agreement'])} | {fmt(r['metrics']['f1'])} | {fmt(r['reference_metrics']['f1'])} | {r['converged']} | {r['timings']['numpy_fit_seconds']:.4f} | {r['timings']['reference_fit_seconds']:.4f} |\n"
svm = next(r for r in comparison if r["kind"] == "svm")
text += f"\nSVM objective NumPy = {svm['objective']:.10f}; reference = {svm['reference_objective']:.10f}; max |gradient| = {svm['gradient_max']:.3g}; {svm['iterations']} vòng lặp. Bảng classifier dùng cùng đặc trưng reference để tách sai khác huấn luyện; bảng cuối phía trên chạy toàn pipeline NumPy.\n"
checks = load("verification.json")
real = load("verification_real.json")
text += f"\nKiểm chứng ca biên: {len(checks['checks'])} phép, đạt={checks['passed']}. Ảnh SOS thật: {len(real['checks'])} phép trên {real['samples']} ảnh validation, đạt={real['passed']}. Lee reference ghép công thức bằng SciPy, không phải API Lee độc lập. Số liệu thời gian phụ thuộc máy và tải song song, không suy ra latency triển khai.\n"
text += "\n## Giới hạn và việc còn thiếu\n\nThiếu góc tới/gió và lớp look-alike, chưa hoàn tất mọi yêu cầu Đề 18. PNG /255 không phải chuẩn hóa góc tới. Chưa có dữ liệu biển miền Trung để đánh giá chuyển miền địa lý. PALSAR chỉ là kiểm tra ngoài sensor với cấu hình đóng băng. Cần bổ sung metadata và nhãn phù hợp trước các kết luận vật lý.\n\nProvenance: `run_manifest.json`, `data/manifest.json`, `evaluation.json`; bảng đầy đủ: `screen.json`, `validation.json`, `model_comparison.json`. Minh họa ca lỗi nhiều/trung vị/ít lỗi ở notebook 05.\n"
text += f"\n## Đối tượng chạm biên và nội vùng trên test\n\nGT chạm biên: {final['edge_gt']}, TP {final['edge_tp']}, recall {fmt(final['edge_recall'])}. GT không chạm biên: {final['interior_gt']}, TP {final['interior_tp']}, recall {fmt(final['interior_recall'])}. Pixel IoU và F1 đối tượng trả lời hai câu hỏi khác nhau; IoU cao hơn không xóa được các lỗi bỏ sót/báo nhầm đối tượng.\n"
text += "\nThời gian fit đo toàn bộ lời gọi wrapper, có thể bao gồm import thư viện lần đầu. Không dùng các con số này để kết luận tốc độ tuyệt đối giữa hai triển khai.\n"
text += "\n## Vì sao chọn Lee và cấu hình cuối?\n\nXem [bằng chứng lựa chọn](selection_evidence/REPORT.md): 11 cấu hình lọc gốc và 2 đối chứng bổ sung cùng cửa sổ 7×7 trên 671 ảnh validation, số đếm từng ảnh, bảng đối chiếu có kiểm soát, bootstrap thăm dò và phân tích quy tắc F1-band/Recall/thời gian. Không có định lý bảo đảm cấu hình đã chọn tối ưu.\n"
text += "\n## Sai số phép toán trên ảnh validation\n\nMỗi dòng tổng hợp cùng phép toán trên 8 ảnh đã chọn bằng seed 2026. MSE là trung bình bình phương sai khác đầu ra; bảng báo MSE lớn nhất trong 8 ảnh, không phải MSE toàn bộ dataset. Với vùng/đặc trưng, MSE tính trên ma trận đặc trưng khi ID vùng khớp.\n\n| Phép toán | Cấu hình | Max absolute error lớn nhất | MSE lớn nhất |\n|---|---|---:|---:|\n"
groups = {}
for check in real["checks"]:
    key = (check["operation"], json.dumps(check["config"], sort_keys=True))
    groups.setdefault(key, []).append(check)
for (operation, config), values in groups.items():
    errors = [v.get("max_abs_error", float(v.get("disagreement", 0) > 0)) for v in values]
    mse = [v.get("mse", v.get("feature_mse")) for v in values]
    if any(v is None for v in errors + mse):
        raise ValueError("Run scripts/verify_real_data.py to populate numerical MSE evidence")
    text += f"| {operation} | `{config}` | {max(errors):.3e} | {max(mse):.3e} |\n"
text += "\nVí dụ tính tay có kiểm chứng: [Lee 5×5](worked_example/REPORT.md). Phân tích thất bại và mean ± SD từng ảnh: [diagnostics](diagnostics/REPORT.md).\n"
if (OUT / "adaptive/REPORT.md").exists():
    text += "\nNhánh ngưỡng thích nghi được khảo sát riêng sau lựa chọn: [Niblack + classifier](adaptive/REPORT.md). Không thay mô hình Otsu đã khóa và không gán số liệu test cũ cho nhánh mới.\n"
(OUT / "REPORT.md").write_text(text, encoding="utf-8")
print("Generated results/sos/REPORT.md from executed evidence")
