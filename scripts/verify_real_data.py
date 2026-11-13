"""Compare independently implemented operations on actual validation PNGs."""

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import numpy as np

from sar_oil import core, reference
from sar_oil.data import read_pair, records
from sar_oil.experiments import FILTERS, OUT, THRESHOLDS, write_json

rows = records("validation")
indices = np.random.default_rng(2026).choice(len(rows), 8, replace=False)
checks = []
for index in indices:
    row = rows[index]
    a, _ = read_pair(row)
    for f in FILTERS:
        start = time.perf_counter()
        n = core.filter_image(a, **f)
        nt = time.perf_counter() - start
        start = time.perf_counter()
        r = reference.filter_image(a, **f)
        rt = time.perf_counter() - start
        checks.append(
            {
                "image": row["id"],
                "operation": "filter",
                "config": f,
                "max_abs_error": float(np.max(np.abs(n - r))),
                "mse": float(np.mean((n - r) ** 2)),
                "numpy_seconds": nt,
                "reference_seconds": rt,
                "passed": bool(np.allclose(n, r, atol=1e-6, rtol=1e-5)),
            }
        )
    for t in THRESHOLDS:
        start = time.perf_counter()
        n = core.threshold(a, **t)
        nt = time.perf_counter() - start
        start = time.perf_counter()
        r = reference.threshold(a, **t)
        rt = time.perf_counter() - start
        checks.append(
            {
                "image": row["id"],
                "operation": "threshold",
                "config": t,
                "disagreement": int((n != r).sum()),
                "mse": float(np.mean((n.astype(float) - r.astype(float)) ** 2)),
                "numpy_seconds": nt,
                "reference_seconds": rt,
                "passed": bool(np.array_equal(n, r)),
            }
        )
    for op in ("none", "close", "open_close"):
        mask = reference.threshold(a)
        start = time.perf_counter()
        n = core.postprocess(mask, op, 16)
        nl = core.label(n)
        nf, ids = core.features(a, nl)
        nt = time.perf_counter() - start
        start = time.perf_counter()
        r = reference.postprocess(mask, op, 16)
        rl = reference.label(r)
        rf, _ = reference.features(a, rl)
        rt = time.perf_counter() - start
        same = bool(np.array_equal(nl, rl))
        error = (
            float(np.max(np.abs(nf - rf)))
            if nf.size and same
            else 0
            if not nf.size and not rf.size
            else None
        )
        checks.append(
            {
                "image": row["id"],
                "operation": "regions_features",
                "config": op,
                "regions": len(ids),
                "max_abs_error": error,
                "feature_mse": float(np.mean((nf - rf) ** 2))
                if nf.size and same
                else 0
                if same
                else None,
                "numpy_seconds": nt,
                "reference_seconds": rt,
                "passed": same and bool(np.allclose(nf, rf, atol=1e-6, rtol=1e-5)),
            }
        )
result = {
    "samples": 8,
    "split": "validation",
    "seed": 2026,
    "passed": all(c["passed"] for c in checks),
    "checks": checks,
}
write_json(OUT / "verification_real.json", result)
print("Real-data checks:", len(checks), "passed:", result["passed"])
if not result["passed"]:
    print([c for c in checks if not c["passed"]])
    raise SystemExit(1)
