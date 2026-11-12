"""Executable numerical and edge-case evidence, separate from ground-truth accuracy."""

import time

import numpy as np

from . import core, reference
from .evaluation import counts
from .experiments import FILTERS, OUT, THRESHOLDS, write_json
from .models import RegionModel


def verify():
    rng = np.random.default_rng(2026)
    checks = []
    arrays = [rng.random((33, 35)), np.zeros((7, 9)), np.ones((7, 9)), rng.random((1, 1))]
    for index, a in enumerate(arrays):
        for f in FILTERS:
            start = time.perf_counter()
            n = core.filter_image(a, **f)
            nt = time.perf_counter() - start
            start = time.perf_counter()
            r = reference.filter_image(a, **f)
            rt = time.perf_counter() - start
            error = float(np.max(np.abs(n - r)))
            checks.append(
                {
                    "check": "filter",
                    "case": index,
                    "config": f,
                    "max_abs_error": error,
                    "numpy_seconds": nt,
                    "reference_seconds": rt,
                    "passed": bool(np.allclose(n, r, atol=1e-6, rtol=1e-5)),
                }
            )
        for t in THRESHOLDS:
            n = core.threshold(a, **t)
            r = reference.threshold(a, **t)
            checks.append(
                {
                    "check": "threshold",
                    "case": index,
                    "config": t,
                    "disagreement": int((n != r).sum()),
                    "passed": bool(np.array_equal(n, r)),
                }
            )
    masks = [
        rng.random((31, 29)) > 0.7,
        np.zeros((8, 8), bool),
        np.ones((8, 8), bool),
        np.eye(8, dtype=bool),
    ]
    hole = np.ones((8, 8), bool)
    hole[3:5, 3:5] = False
    masks.append(hole)
    for index, m in enumerate(masks):
        n, r = core.label(m), reference.label(m)
        checks.append({"check": "label8", "case": index, "passed": bool(np.array_equal(n, r))})
        for op in ("none", "close", "open_close"):
            checks.append(
                {
                    "check": "morphology",
                    "case": index,
                    "operation": op,
                    "passed": bool(
                        np.array_equal(core.postprocess(m, op, 1), reference.postprocess(m, op, 1))
                    ),
                }
            )
        a = rng.random(m.shape)
        nf, _ = core.features(a, n)
        rf, _ = reference.features(a, r)
        checks.append(
            {
                "check": "features",
                "case": index,
                "max_abs_error": float(np.max(np.abs(nf - rf))) if nf.size else 0,
                "passed": bool(np.allclose(nf, rf, atol=1e-6, rtol=1e-5)),
            }
        )
    # Split/merge: one GT object can only match one prediction, and vice versa.
    gt = np.zeros((12, 20), bool)
    gt[2:10, 2:18] = True
    split = gt.copy()
    split[:, 9:11] = False
    c = counts(split, gt)
    checks.append(
        {
            "check": "split_matching",
            "counts": c,
            "passed": c["tp"] == 0 and c["fp"] == 2 and c["fn"] == 1,
        }
    )
    c = counts(gt, split)
    checks.append(
        {
            "check": "merge_matching",
            "counts": c,
            "passed": c["tp"] == 0 and c["fp"] == 1 and c["fn"] == 2,
        }
    )
    c = counts(np.zeros((8, 8), bool), np.zeros((8, 8), bool))
    checks.append({"check": "empty_matching", "passed": c["tp"] == c["fp"] == c["fn"] == 0})
    X = rng.normal(size=(240, 8))
    X[:, 7] = 1
    y = (X[:, 0] + 0.5 * X[:, 1] > 0).astype(int)
    for kind, params in [("cart", {"max_depth": 3, "min_leaf": 5}), ("svm", {"C": 1})]:
        n = RegionModel(kind, **params).fit(X, y)
        r = RegionModel(kind, backend="reference", **params).fit(X, y)
        agreement = float(np.mean(n.predict(X) == r.predict(X)))
        passed = n.converged and agreement >= 0.95
        checks.append(
            {
                "check": "model",
                "kind": kind,
                "agreement": agreement,
                "converged": bool(n.converged),
                "passed": bool(passed),
            }
        )
        try:
            RegionModel(kind, **params).fit(X, np.zeros(len(X), int))
        except ValueError:
            rejected = True
        else:
            rejected = False
        checks.append({"check": "single_class_rejected", "kind": kind, "passed": rejected})
        path = OUT / (f"verify_{kind}.json")
        path.parent.mkdir(parents=True, exist_ok=True)
        n.save(path)
        checks.append(
            {
                "check": "serialization",
                "kind": kind,
                "passed": bool(np.array_equal(n.predict(X), RegionModel.load(path).predict(X))),
            }
        )
    result = {"passed": all(c["passed"] for c in checks), "checks": checks}
    write_json(OUT / "verification.json", result)
    return result
