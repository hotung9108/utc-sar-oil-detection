"""Deterministic, resumable experiments. Validation selects; final test reports only."""

import hashlib
import itertools
import json
import pickle
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np

from . import reference
from .data import MANIFEST, ROOT, read_pair, records
from .evaluation import counts, region_counts, region_geometry, summarize
from .models import RegionModel
from .pipeline import candidates, predict

OUT = ROOT / "results/sos"
CACHE = ROOT / ".cache/sos"
FILTERS = (
    [{"name": "none"}]
    + [{"name": "median", "size": n} for n in (3, 5)]
    + [{"name": "gaussian", "sigma": s} for s in (0.8, 1.2)]
    + [{"name": "lee", "size": n, "looks": l} for n, l in itertools.product((3, 5, 7), (1, 4))]
)
THRESHOLDS = [{"name": "otsu"}] + [
    {"name": "niblack", "size": n, "k": k}
    for n, k in itertools.product((15, 31, 51), (0.2, 0.5, 0.8))
]
MODELS = [
    ("cart", {"max_depth": d, "min_leaf": n}) for d, n in itertools.product((3, 5, 8), (5, 20))
] + [("svm", {"C": c}) for c in (0.1, 1, 10)]
GROUPS = {"shape": list(range(4)), "intensity": list(range(4, 8)), "all": list(range(8))}


def write_json(path, obj):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(obj, indent=2, ensure_ascii=False, allow_nan=False), encoding="utf-8"
    )


def digest(config):
    return hashlib.sha256(json.dumps(config, sort_keys=True).encode()).hexdigest()[:16]


def pool_map(fn, items, workers):
    with ProcessPoolExecutor(max_workers=workers) as pool:
        return list(pool.map(fn, items, chunksize=4))


def _screen(row):
    image, truth = read_pair(row)
    output = []
    for f in FILTERS:
        start = time.perf_counter()
        filtered = reference.filter_image(image, **f)
        filter_time = time.perf_counter() - start
        for t in THRESHOLDS:
            start = time.perf_counter()
            mask = reference.postprocess(reference.threshold(filtered, **t))
            elapsed = time.perf_counter() - start + filter_time
            output.append((counts(mask, truth), elapsed))
    return output


def rank(rows):
    """Within .005 of best F1, prioritize recall then runtime; repeat for top k."""
    remaining = list(rows)
    result = []
    while remaining:
        best = max((r["metrics"]["f1"] or 0) for r in remaining)
        tied = [r for r in remaining if (r["metrics"]["f1"] or 0) >= best - 0.005]
        chosen = min(
            tied, key=lambda r: (-(r["metrics"]["recall"] or 0), r.get("seconds", 0), r["id"])
        )
        result.append(chosen)
        remaining.remove(chosen)
    return result


def screen(workers=4):
    OUT.mkdir(parents=True, exist_ok=True)
    raw = pool_map(_screen, records("validation"), workers)
    rows = []
    for i, (f, t) in enumerate(itertools.product(FILTERS, THRESHOLDS)):
        config = {"filter": f, "threshold": t, "morphology": {"operation": "none", "min_area": 16}}
        rows.append(
            {
                "id": digest(config),
                "config": config,
                "metrics": summarize([r[i][0] for r in raw]),
                "seconds": sum(r[i][1] for r in raw),
            }
        )
    rows = rank(rows)
    write_json(OUT / "screen.json", rows)
    return rows


def _regions(args):
    row, config = args
    image, truth = read_pair(row)
    filtered, labels = candidates(image, config, "reference")
    X, ids = reference.features(filtered, labels)
    areas = np.bincount(labels.ravel())
    oil = np.bincount(labels.ravel(), weights=truth.ravel(), minlength=len(areas))
    purity = oil[ids] / areas[ids] if ids else np.empty(0)
    y = np.where(purity >= 0.5, 1, np.where(purity <= 0.05, 0, -1))
    return {
        "id": row["id"],
        "X": X,
        "y": y,
        "labels": labels.astype(np.uint16),
        "truth": np.packbits(truth),
        "shape": truth.shape,
    }


def region_data(config, split, workers):
    # Invalidate cache whenever data manifest or extraction code changes.
    identity = hashlib.sha256(
        MANIFEST.read_bytes()
        + Path(__file__).read_bytes()
        + (ROOT / "src/sar_oil/reference.py").read_bytes()
    ).hexdigest()[:16]
    path = CACHE / f"{identity}_{digest(config)}_{split}.pkl"
    if path.exists():
        with path.open("rb") as handle:
            return pickle.load(handle)
    data = pool_map(_regions, [(r, config) for r in records(split)], workers)
    CACHE.mkdir(parents=True, exist_ok=True)
    with path.open("wb") as handle:
        pickle.dump(data, handle, protocol=5)
    return data


def training_arrays(data):
    X = np.concatenate([r["X"] for r in data])
    y = np.concatenate([r["y"] for r in data])
    rng = np.random.default_rng(2026)
    selected = []
    for cls in (0, 1):
        idx = np.flatnonzero(y == cls)
        if not len(idx):
            raise ValueError(f"No training candidates in class {cls}")
        selected.extend(rng.choice(idx, min(10000, len(idx)), replace=False))
    return (
        X[selected],
        y[selected],
        {
            "positive": int((y == 1).sum()),
            "negative": int((y == 0).sum()),
            "ambiguous": int((y == -1).sum()),
            "used": len(selected),
        },
    )


def evaluate_regions(data, model):
    result = []
    for r in data:
        if "geometry" not in r:
            truth = (
                np.unpackbits(r["truth"], count=np.prod(r["shape"]))
                .reshape(r["shape"])
                .astype(bool)
            )
            r["geometry"] = region_geometry(r["labels"], truth)
        result.append(region_counts(r["geometry"], model.predict(r["X"]).astype(bool)))
    return summarize(result)


def benchmark(workers=4):
    screen_path = OUT / "screen.json"
    screened = json.loads(screen_path.read_text()) if screen_path.exists() else screen(workers)
    all_rows = []
    for base, operation, area in itertools.product(
        screened[:3], ("none", "close", "open_close"), (4, 16, 64)
    ):
        config = dict(base["config"], morphology={"operation": operation, "min_area": area})
        key = digest(config)
        checkpoint = OUT / "validation" / f"{key}.json"
        if checkpoint.exists():
            all_rows.extend(json.loads(checkpoint.read_text()))
            continue
        print("Extracting", key, operation, area, flush=True)
        train = region_data(config, "train", workers)
        X, y, training = training_arrays(train)
        del train
        val = region_data(config, "validation", workers)
        rows = []
        for group, (kind, params) in itertools.product(GROUPS, MODELS):
            start = time.perf_counter()
            model = RegionModel(kind, GROUPS[group], backend="reference", **params).fit(X, y)
            metrics = evaluate_regions(val, model)
            rows.append(
                {
                    "id": key + "_" + group + "_" + kind + "_" + digest(params),
                    "config": config,
                    "group": group,
                    "kind": kind,
                    "params": params,
                    "metrics": metrics,
                    "training": training,
                    "seconds": time.perf_counter() - start,
                }
            )
        write_json(checkpoint, rows)
        all_rows.extend(rows)
        print("Completed", key, "best F1", max(r["metrics"]["f1"] or 0 for r in rows), flush=True)
    all_rows = rank(all_rows)
    write_json(OUT / "validation.json", all_rows)
    return all_rows


def select(workers=4):
    for name in ("verification.json", "verification_real.json"):
        if not json.loads((OUT / name).read_text())["passed"]:
            raise RuntimeError("NumPy checks must pass before selection")
    rows = json.loads((OUT / "validation.json").read_text())
    comparisons = []
    # Verify the top reference result for each model family; select only a converged NumPy model.
    finalists = [next(r for r in rows if r["kind"] == kind) for kind in ("cart", "svm")]
    eligible = []
    for r in finalists:
        X, y, _training = training_arrays(region_data(r["config"], "train", workers))
        val = region_data(r["config"], "validation", workers)
        models = {}
        timings = {}
        for backend in ("numpy", "reference"):
            start = time.perf_counter()
            models[backend] = RegionModel(
                r["kind"], GROUPS[r["group"]], backend=backend, **r["params"]
            ).fit(X, y)
            timings[backend + "_fit_seconds"] = time.perf_counter() - start
        numpy = models["numpy"]
        ref = models["reference"]
        V = np.concatenate([v["X"] for v in val])
        agreement = float(np.mean(numpy.predict(V) == ref.predict(V)))
        candidate_y = np.concatenate([v["y"] for v in val])
        valid = candidate_y >= 0
        confusion = {}
        for backend, model in models.items():
            predicted = model.predict(V)[valid]
            target = candidate_y[valid]
            confusion[backend] = {
                "tp": int(((predicted == 1) & (target == 1)).sum()),
                "fp": int(((predicted == 1) & (target == 0)).sum()),
                "tn": int(((predicted == 0) & (target == 0)).sum()),
                "fn": int(((predicted == 0) & (target == 1)).sum()),
            }
        row = dict(
            r,
            metrics=evaluate_regions(val, numpy),
            reference_metrics=evaluate_regions(val, ref),
            agreement=agreement,
            converged=bool(numpy.converged),
            timings=timings,
            candidate_confusion=confusion,
            ambiguous_validation_candidates=int((~valid).sum()),
        )
        if r["kind"] == "svm":
            e = numpy.estimator
            xr = numpy.transform(X)
            target = 2 * y - 1
            w = ref.estimator.coef_[0]
            reference_objective = float(
                (
                    0.5 * (w @ w)
                    + r["params"]["C"] * np.square(np.maximum(1 - target * (xr @ w), 0)).sum()
                )
                / len(y)
            )
            row.update(
                objective=e.objective,
                reference_objective=reference_objective,
                gradient_max=e.gradient_max,
                iterations=e.iterations,
                history=e.history,
            )
        numpy.save(OUT / (r["kind"] + "_model.json"))
        comparisons.append(row)
        if numpy.converged:
            eligible.append(row)
    write_json(OUT / "model_comparison.json", comparisons)
    if not eligible:
        raise RuntimeError("No converged model: cannot unlock test")
    selected = rank(eligible)[0]
    selected["manifest_sha256"] = hashlib.sha256(MANIFEST.read_bytes()).hexdigest()
    selected["model_file"] = selected["kind"] + "_model.json"
    write_json(OUT / "selected.json", selected)
    return selected


def _evaluate_image(args):
    row, config, model_path, backend, mask_threshold = args
    image, truth = read_pair(row, mask_threshold)
    model = RegionModel.load(model_path) if model_path else None
    start = time.perf_counter()
    prediction, _ = predict(image, config, model, backend)
    return {
        "counts": counts(prediction, truth),
        "seconds": time.perf_counter() - start,
        "id": row["id"],
    }


def evaluate(workers=4):
    selected = json.loads((OUT / "selected.json").read_text())
    verification = json.loads((OUT / "verification.json").read_text())
    if not verification["passed"]:
        raise RuntimeError("NumPy verification must pass before test")
    if not json.loads((OUT / "verification_real.json").read_text())["passed"]:
        raise RuntimeError("Real-data verification must pass before test")
    if selected["manifest_sha256"] != hashlib.sha256(MANIFEST.read_bytes()).hexdigest():
        raise RuntimeError("Dataset changed since selection")
    config = selected["config"]
    model_path = str(OUT / selected["model_file"])
    selection_signature = digest(
        {
            "config": config,
            "manifest": selected["manifest_sha256"],
            "model_sha256": hashlib.sha256(Path(model_path).read_bytes()).hexdigest(),
        }
    )
    output = {}
    baseline = {
        "filter": {"name": "none"},
        "threshold": {"name": "otsu"},
        "morphology": {"operation": "none", "min_area": 16},
    }
    jobs = [
        ("test_final", "test", config, model_path, 128),
        ("test_baseline", "test", baseline, None, 128),
        ("test_no_classifier", "test", config, None, 128),
        ("palsar_val", "external_val", config, model_path, 128),
        ("validation_label64", "validation", config, model_path, 64),
        ("validation_label128", "validation", config, model_path, 128),
        ("validation_label192", "validation", config, model_path, 192),
    ]
    for name, split, c, m, mt in jobs:
        path = OUT / (name + ".json")
        if path.exists():
            output[name] = json.loads(path.read_text())
            if output[name].get("selection_signature") != selection_signature:
                raise RuntimeError(f"Stale evaluation {path}: archive it before rerunning")
            continue
        raw = pool_map(_evaluate_image, [(r, c, m, "numpy", mt) for r in records(split)], workers)
        result = {
            "metrics": summarize([r["counts"] for r in raw]),
            "seconds": sum(r["seconds"] for r in raw),
            "per_image": raw,
            "selection_signature": selection_signature,
        }
        write_json(path, result)
        output[name] = result
        print(name, result["metrics"], flush=True)
    import importlib.metadata
    import platform

    output["provenance"] = {
        "python": platform.python_version(),
        "packages": {
            p: importlib.metadata.version(p)
            for p in ("numpy", "scipy", "scikit-image", "scikit-learn", "Pillow")
        },
        "seed": 2026,
        "manifest_sha256": selected["manifest_sha256"],
        "selected_id": selected["id"],
        "workers": workers,
    }
    write_json(OUT / "evaluation.json", output)
    return output
