"""TV2: literal hand-calculation fixtures checked against production functions."""

import json
from pathlib import Path

import numpy as np

from src.edges import custom_sobel
from src.enhancement import global_histogram_equalization
from src.filters import custom_lee_filter
from src.library_comparison import run_comparisons
from src.morphology import (
    custom_dilation,
    custom_erosion,
    custom_morphological_boundary,
    custom_otsu_threshold,
)


def run_hand_examples():
    """Five small examples, with expected values independent of production code."""
    records = []

    def record(name, expected, actual, explanation):
        """Append expected/actual arrays, maximum error and derivation to hand-example records; Section 2.6."""
        a, b = np.asarray(expected, dtype=float), np.asarray(actual, dtype=float)
        error = float(np.max(np.abs(a - b)))
        records.append(
            dict(
                example=name,
                expected=a.tolist(),
                actual=b.tolist(),
                max_abs_error=error,
                passed=error < 1e-9,
                derivation=explanation,
            )
        )

    a = np.repeat(np.arange(4, dtype=np.uint8), 4).reshape(4, 4)
    record(
        "HE 4x4 CDF-min",
        [0, 85, 170, 255],
        global_histogram_equalization(a)[1][:4],
        "Counts 4,4,4,4; CDF 4,8,12,16. Subtract first CDF=4: round((CDF-4)/12*255).",
    )
    a = np.full((5, 5), 100, np.uint8)
    a[2, 2] = 200
    record(
        "Lee center 5x5, window 3",
        111,
        int(custom_lee_filter(a, 3, 4)[2, 2]),
        "Local sum=1000, mean=1000/9; variance=80000/81 < mean^2/4, K=0; rounded mean=111.",
    )
    a = np.array([[0, 0, 0], [0, 100, 100], [0, 100, 100]], np.uint8)
    gx, gy, _, _ = custom_sobel(a)
    record(
        "Sobel center 3x3",
        [300, 300],
        [gx[1, 1], gy[1, 1]],
        "Gx=(0+2*100+100)-0=300; Gy=(0+2*100+100)-0=300. Use floating gradients.",
    )
    a = np.zeros((8, 8), np.uint8)
    a[2:6, 2:6] = 255
    k = np.ones((3, 3), np.uint8)
    record(
        "Morphology 8x8",
        [4, 36, 12],
        [
            np.count_nonzero(custom_erosion(a, k)),
            np.count_nonzero(custom_dilation(a, k)),
            np.count_nonzero(custom_morphological_boundary(a)),
        ],
        "4x4 square: erosion 2x2=4; dilation 6x6=36; inner boundary 16-4=12.",
    )
    a = np.full((8, 8), 50, np.uint8)
    a[:, 4:] = 200
    record(
        "Otsu 8x8",
        [50, 1],
        custom_otsu_threshold(a),
        "Two equal masses at 50 and 200. Between variance=0.25*150^2=5625=total variance. First maximizing t=50; dark class I<=t.",
    )
    out = Path("results/verification")
    out.mkdir(parents=True, exist_ok=True)
    (out / "hand_examples.json").write_text(
        json.dumps(records, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    assert all(r["passed"] for r in records), records
    print("5 hand-calculation examples match production functions.")
    return records


def main():
    """Run the five hand examples and full comparison registry; exit nonzero on a numerical failure."""
    run_hand_examples()
    measured = run_comparisons()
    if (measured.verdict == "FAIL").any():
        raise SystemExit(1)


if __name__ == "__main__":
    main()
