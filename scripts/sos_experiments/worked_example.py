"""Verify a small Lee example with exact rational arithmetic and library output."""

import sys as _sys
from pathlib import Path as _Path
_project_root = _Path(__file__).resolve().parents[2]
_sys.path.insert(0, str(_project_root))
_sys.path.insert(0, str(_project_root / "src"))


import json
import sys
from fractions import Fraction
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
from sar_oil import core, reference


def main():
    # Synthetic pedagogical example, never a substitute for SOS ground truth.
    raw = np.array(
        [[2, 2, 2, 2, 2], [2, 2, 2, 2, 2], [2, 2, 9, 2, 2], [2, 2, 2, 2, 2], [2, 2, 2, 2, 2]]
    )
    image = raw.astype(float) / 10
    local = [Fraction(int(x), 10) for x in raw[1:4, 1:4].flat]
    mean = sum(local) / 9
    variance = sum(x * x for x in local) / 9 - mean * mean
    noise = mean * mean / 4
    weight = max(variance - noise, Fraction(0)) / variance
    center = mean + weight * (Fraction(9, 10) - mean)
    custom = core.filter_image(image, name="lee", size=3, looks=4)
    library = reference.filter_image(image, name="lee", size=3, looks=4)
    assert np.isclose(custom[2, 2], float(center), rtol=0, atol=1e-12)
    assert np.allclose(custom, library, rtol=0, atol=1e-12)
    dest = ROOT / "results/sos/worked_example"
    dest.mkdir(exist_ok=True)
    result = {
        "purpose": "Synthetic teaching example, not detection accuracy",
        "input": image.tolist(),
        "window": 3,
        "looks": 4,
        "exact_center": {
            k: str(v)
            for k, v in {
                "mean": mean,
                "variance": variance,
                "noise": noise,
                "weight": weight,
                "output": center,
            }.items()
        },
        "numpy_output": custom.tolist(),
        "reference_output": library.tolist(),
        "max_abs_error": float(np.max(np.abs(custom - library))),
        "mse": float(np.mean((custom - library) ** 2)),
        "passed": True,
    }
    (dest / "example.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    text = f"""# Ví dụ số kiểm chứng Lee trên ma trận 5×5

Tái tạo: `python scripts/sos_experiments/worked_example.py`. Đây là ma trận tổng hợp phục vụ giải thích, không phải ảnh SAR hoặc chứng cứ về độ chính xác phát hiện dầu.

Ma trận có giá trị 0,2 ở mọi ô, riêng ô giữa là 0,9. Cửa sổ 3×3 ở tâm gồm tám giá trị 0,2 và một giá trị 0,9. Dùng phương sai tổng thể, L=4:

- m = (8×0,2 + 0,9)/9 = {mean}.
- v = (8×0,2² + 0,9²)/9 − m² = {variance}.
- noise = m²/4 = {noise}.
- w = max(v−noise,0)/v = {weight}.
- y = m + w(0,9−m) = {center} ≈ {float(center):.12f}.

Code kiểm tra giá trị tâm bằng `Fraction` (số hữu tỉ chính xác), đối chiếu NumPy với công thức này, rồi đối chiếu cả ma trận với bản dùng thống kê SciPy. Sai số tuyệt đối lớn nhất: {result["max_abs_error"]:.3e}; MSE: {result["mse"]:.3e}. Giá trị các ô còn lại và toàn bộ ma trận đầu ra nằm trong `example.json`.

## Ý nghĩa và giới hạn của công thức

Xét mô hình cục bộ đơn giản Y=X+N, N có trung bình 0 và không tương quan với X. Với ước lượng tuyến tính X̂=m+a(Y−m), sai số bình phương kỳ vọng là (a−1)² Var(X)+a² Var(N). Đạo hàm theo a bằng 0 cho a=Var(X)/(Var(X)+Var(N))=1−Var(N)/Var(Y). Thay các phương sai bằng ước lượng cục bộ và chặn phần âm cho dạng trọng số đang dùng.

Đây là giải thích theo mô hình đơn giản. Nhiễu speckle SAR thường được mô hình hóa dạng nhân; cách thay Var(N) bằng m²/L trong code là một xấp xỉ cục bộ. Dữ liệu PNG không xác minh thang cường độ tuyến tính hoặc số looks vật lý. Vì vậy suy luận trên KHÔNG chứng minh L=4 tối ưu, KHÔNG chứng minh F1 tăng, và KHÔNG chứng minh giữ đúng biên dầu. Các kết luận về SOS phải dựa vào thực nghiệm validation đã lưu.

Ở vùng gần hằng, v≤noise nên w=0: đầu ra là m. Khi v lớn so với noise, w gần 1: đầu ra gần giá trị quan sát. Điểm sáng bất thường cũng có thể làm v tăng; do đó cơ chế này có thể giữ lại cả nhiễu hoặc cấu trúc không phải dầu.

## Liên hệ cài đặt

`core.mean_filter` tính mean và mean bình phương bằng summed-area table; `core.filter_image` tính v=max(E[Y²]−m²,0), noise, w rồi đầu ra. Chuyển sang float trước khi bình phương để tránh tràn uint8; dùng mẫu số max(v,1e−12) để tránh chia 0. Padding reflect không lặp pixel biên. Bản SciPy dùng mode mirror tương ứng; đây là cùng công thức với công cụ tính thống kê khác, không phải một API Lee độc lập.

Với ảnh H×W và cửa sổ k, cách tích phân có thời gian/bộ nhớ O((H+k)(W+k)); khi k nhỏ so với ảnh là O(HW). Cách trượt cửa sổ trực tiếp tính từng trung bình tốn O(HWk²). Khác biệt tối ưu hóa này không làm thay đổi định nghĩa công thức.
"""
    (dest / "REPORT.md").write_text(text, encoding="utf-8")
    print("Exact Lee example and NumPy/reference comparison passed")


if __name__ == "__main__":
    main()
