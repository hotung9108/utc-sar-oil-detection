"""TV5: reproducible measurements, parameter survey and failure analysis.

Dataset labels are used only for image-level presence evaluation. No mask-level
accuracy is reported without pixel ground truth. All tables retain per-image rows.
"""

import hashlib
import json
import os
import platform
import subprocess
import time
from concurrent.futures import ProcessPoolExecutor
from dataclasses import asdict
from pathlib import Path

import cv2
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from src.metrics import calculate_all_enhancement_metrics
from src.pipeline import EDGE_NAMES, FILTER_NAMES, PipelineConfig, process_image
from src.utils import load_sar_image

OUT = Path("results/reproducible")
SEED = 2026


def code_digest():
    """Return SHA-256 of source, reproduction entry point and locked environment for evidence provenance."""
    h = hashlib.sha256()
    paths = list(Path("src").rglob("*.py")) + [
        Path(n) for n in ["reproduce.py", "pyproject.toml", "uv.lock"]
    ]
    for p in sorted(paths):
        h.update(p.as_posix().encode())
        h.update(p.read_bytes())
    return h.hexdigest()


def save_table(records, name, group_columns):
    """Write per-image records and mean/std/count CSVs grouped by the named columns; return the DataFrame."""
    df = pd.DataFrame(records)
    df.to_csv(OUT / (name + "_per_image.csv"), index=False, encoding="utf-8-sig")
    values = [c for c in df.select_dtypes(include="number").columns if c not in group_columns]
    grouped = df.groupby(group_columns, sort=False)[values].agg(["mean", "std", "count"])
    grouped.columns = ["_".join(c) for c in grouped.columns]
    grouped.reset_index().to_csv(OUT / (name + "_summary.csv"), index=False, encoding="utf-8-sig")
    return df


def collage(image, result, destination, title):
    """Write an equal-scale PNG of input, filtered, enhanced and boundary-overlay images to destination."""
    fig, axes = plt.subplots(1, 4, figsize=(14, 4))
    for ax, a, label in zip(
        axes,
        [image, result["filtered"], result["enhanced"], result["overlay"]],
        ["Input", "Filtered", "Enhanced", "Candidate boundary"],
    ):
        ax.imshow(a, cmap="gray", vmin=0, vmax=255)
        ax.set_title(label)
        ax.axis("off")
    fig.suptitle(title)
    fig.tight_layout()
    fig.savefig(destination, dpi=140)
    plt.close(fig)


def run_sample_experiments():
    """Run method, parameter, noise and failure experiments; write per-image and summary evidence for Chapter 4."""
    OUT.mkdir(parents=True, exist_ok=True)
    paths = sorted(Path("data/sample").rglob("*.jpg"))
    if len(paths) != 10:
        raise ValueError("Expected the documented 10 sample images")
    raw = {p.as_posix(): load_sar_image(str(p)) for p in paths}
    records = []
    for name, image in raw.items():
        for method in FILTER_NAMES:
            start = time.perf_counter()
            result = process_image(
                image, PipelineConfig(filter_name=method, enhancement_name="none")
            )
            elapsed = (time.perf_counter() - start) * 1000
            records.append(
                dict(image=name, method=method, pipeline_ms=elapsed, **result["metrics"])
            )
    save_table(records, "filters", ["method"])
    records = []
    for name, image in raw.items():
        for clip in [1.0, 2.0, 3.0, 4.0, 5.0]:
            for grid in [4, 8, 16]:
                start = time.perf_counter()
                result = process_image(image, PipelineConfig(clip_limit=clip, tile_grid=grid))
                records.append(
                    dict(
                        image=name,
                        clip=clip,
                        grid=grid,
                        pipeline_ms=(time.perf_counter() - start) * 1000,
                        candidate_area_pct=result["stats"]["area_pct"],
                        **result["metrics"],
                    )
                )
    save_table(records, "clahe", ["clip", "grid"])
    records = []
    rng = np.random.default_rng(SEED)
    for name, image in raw.items():
        for sigma in [0.0, 10.0, 20.0, 30.0]:
            noisy = np.clip(
                np.rint(image.astype(float) + rng.normal(0, sigma, image.shape)), 0, 255
            ).astype(np.uint8)
            for method in EDGE_NAMES:
                start = time.perf_counter()
                result = process_image(noisy, PipelineConfig(edge_name=method))
                records.append(
                    dict(
                        image=name,
                        method=method,
                        noise_sigma=sigma,
                        pipeline_ms=(time.perf_counter() - start) * 1000,
                        edge_density_pct=float(np.mean(result["boundary"] > 0) * 100),
                        **calculate_all_enhancement_metrics(image, result["displayed"]),
                    )
                )
    save_table(records, "edge_noise", ["method", "noise_sigma"])
    # Deliberate failure analysis: image 00013 + all known sea samples; no cherry-picked success label.
    failures = [Path("kaggle/data/Class_1/class_1_00013.jpg")] + sorted(
        Path("data/sample/sea_surface").glob("*.jpg")
    )
    records = []
    for p in failures:
        image = load_sar_image(str(p))
        for method in ["none", "clahe"]:
            result = process_image(image, PipelineConfig(enhancement_name=method))
            records.append(
                dict(
                    image=p.as_posix(),
                    enhancement=method,
                    candidates=result["stats"]["slicks_count"],
                    area_pct=result["stats"]["area_pct"],
                    contrast=result["stats"]["mean_contrast_ratio"],
                )
            )
            collage(
                image,
                result,
                OUT / (p.stem + "_" + method + ".png"),
                f"{p.stem}: {method}, area={result['stats']['area_pct']}%",
            )
    save_table(records, "failure_cases", ["enhancement"])
    # One equal-scale ROI comparison for the representative dark streak.
    image = load_sar_image(str(failures[0]))
    result = process_image(image)
    fig, axes = plt.subplots(1, 3, figsize=(10, 4))
    for ax, key in zip(axes, ["raw", "filtered", "enhanced"]):
        ax.imshow(result[key][270:400, 260:400], cmap="gray", vmin=0, vmax=255)
        ax.set_title(key + " ROI")
        ax.axis("off")
    fig.tight_layout()
    fig.savefig(OUT / "roi_00013.png", dpi=160)
    plt.close(fig)
    print(
        "Sample experiments: filters, CLAHE grid, 3 noise levels + clean, failure cases saved.",
        flush=True,
    )


def evaluate_one(item):
    """Process one (path,label) pair and return candidate presence, area, contrast and elapsed milliseconds."""
    cv2.setNumThreads(1)
    path, label = item
    start = time.perf_counter()
    image = load_sar_image(path)
    result = process_image(image)
    stats = result["stats"]
    prediction = int(stats["slicks_count"] > 0)
    return dict(
        image=path,
        label=label,
        prediction=prediction,
        candidates=stats["slicks_count"],
        area_pct=stats["area_pct"],
        contrast=stats["mean_contrast_ratio"],
        pipeline_ms=(time.perf_counter() - start) * 1000,
    )


def run_dataset_evaluation(workers=4):
    """Evaluate both directory classes using workers processes; write per-image rows and return image-level confusion metrics."""
    OUT.mkdir(parents=True, exist_ok=True)
    items = [
        (p.as_posix(), label)
        for label in [0, 1]
        for p in sorted(Path(f"kaggle/data/Class_{label}").glob("*.jpg"))
    ]
    if not items:
        raise ValueError("Dataset is missing; cannot claim a full evaluation")
    rows = []
    workers = max(1, min(workers, os.cpu_count() or 1))
    with ProcessPoolExecutor(max_workers=workers) as pool:
        for row in pool.map(evaluate_one, items, chunksize=8):
            rows.append(row)
            if len(rows) % 200 == 0:
                print(f"Dataset {len(rows)}/{len(items)}", flush=True)
    df = save_table(rows, "dataset", ["label"])
    counts = {}
    for label, pred, name in [(0, 0, "TN"), (0, 1, "FP"), (1, 0, "FN"), (1, 1, "TP")]:
        counts[name] = int(((df.label == label) & (df.prediction == pred)).sum())
    tn, fp, fn, tp = (counts[k] for k in ["TN", "FP", "FN", "TP"])
    counts.update(
        n=len(df),
        precision=tp / max(tp + fp, 1),
        recall=tp / max(tp + fn, 1),
        f1=2 * tp / max(2 * tp + fp + fn, 1),
        specificity=tn / max(tn + fp, 1),
        accuracy=(tp + tn) / len(df),
        scope="Image-level presence against directory Class_0/Class_1; not pixel segmentation accuracy; no train/test learning",
    )
    (OUT / "confusion.json").write_text(json.dumps(counts, indent=2), encoding="utf-8")
    print(json.dumps(counts), flush=True)
    return counts


def write_manifest(scope="full", workers=4):
    """Write scope, workers, versions, config and source hash; partial runs cannot certify full-dataset results."""
    OUT.mkdir(parents=True, exist_ok=True)
    meta = dict(
        completed_scope=scope,
        dataset_workers=max(1, min(workers, os.cpu_count() or 1)),
        seed=SEED,
        python=platform.python_version(),
        platform=platform.platform(),
        cpu=platform.processor(),
        logical_cpus=os.cpu_count(),
        numpy=np.__version__,
        opencv=cv2.__version__,
        git_head=subprocess.check_output(["git", "rev-parse", "HEAD"]).decode().strip(),
        git_dirty=bool(subprocess.check_output(["git", "status", "--porcelain"]).strip()),
        source_sha256=code_digest(),
        config=asdict(PipelineConfig()),
        label_assumption="Class_0: no oil; Class_1: oil present, as named in the supplied project; license/source provenance still requires team confirmation",
        executed_at=time.strftime("%Y-%m-%dT%H:%M:%S%z"),
    )
    (OUT / "manifest.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
