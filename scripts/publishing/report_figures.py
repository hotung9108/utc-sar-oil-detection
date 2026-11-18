"""Generate report figures from recorded validation experiments, without model selection."""

import sys as _sys
from pathlib import Path as _Path
_project_root = _Path(__file__).resolve().parents[2]
_sys.path.insert(0, str(_project_root))
_sys.path.insert(0, str(_project_root / "scripts"))


import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
from sar_oil.data import read_pair, records
from sar_oil.provenance import ensure_run


def main():
    ensure_run()
    out = ROOT / "results/sos/report_figures"
    out.mkdir(exist_ok=True)
    rows = records("validation")
    chosen = np.random.default_rng(2026).choice(len(rows), 6, replace=False)
    fig, axes = plt.subplots(3, 4, figsize=(12, 9))
    selected = []
    for i, index in enumerate(chosen):
        row = rows[index]
        a, g = read_pair(row)
        selected.append(row["id"])
        r, c = divmod(i, 2)
        axes[r, c * 2].imshow(a, cmap="gray", vmin=0, vmax=1)
        axes[r, c * 2].set_title(row["id"], fontsize=9)
        axes[r, c * 2 + 1].imshow(g, cmap="gray", vmin=0, vmax=1)
        axes[r, c * 2 + 1].set_title("SOS mask >=128", fontsize=9)
    for ax in axes.flat:
        ax.axis("off")
    fig.tight_layout()
    fig.savefig(out / "dataset_examples.png", dpi=180)
    plt.close(fig)
    screen = json.loads((ROOT / "results/sos/screen.json").read_text())
    fig, axes = plt.subplots(1, 2, figsize=(10, 4))
    for looks in (1, 4):
        items = sorted(
            [
                r
                for r in screen
                if r["config"]["filter"]["name"] == "lee"
                and r["config"]["filter"]["looks"] == looks
                and r["config"]["threshold"]["name"] == "otsu"
            ],
            key=lambda r: r["config"]["filter"]["size"],
        )
        axes[0].plot(
            [r["config"]["filter"]["size"] for r in items],
            [r["metrics"]["f1"] for r in items],
            marker="o",
            label=f"L={looks}",
        )
    axes[0].set(
        xlabel="Lee window side (pixels)",
        ylabel="Proposal object F1 (validation)",
        xticks=[3, 5, 7],
    )
    for size in (15, 31, 51):
        items = sorted(
            [
                r
                for r in screen
                if r["config"]["filter"] == {"name": "lee", "size": 7, "looks": 1}
                and r["config"]["threshold"]["name"] == "niblack"
                and r["config"]["threshold"]["size"] == size
            ],
            key=lambda r: r["config"]["threshold"]["k"],
        )
        axes[1].plot(
            [r["config"]["threshold"]["k"] for r in items],
            [r["metrics"]["f1"] for r in items],
            marker="o",
            label=f"window={size}",
        )
    axes[1].set(
        xlabel="Niblack k (dimensionless)",
        ylabel="Proposal object F1 (validation)",
        xticks=[0.2, 0.5, 0.8],
    )
    for ax in axes:
        ax.grid(alpha=0.25)
        ax.legend()
    fig.suptitle("Parameter study: fixed no morphology, min area 16 pixels")
    fig.tight_layout()
    fig.savefig(out / "parameter_study.png", dpi=180)
    plt.close(fig)
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.set(xlim=(0, 10), ylim=(0, 6))
    ax.axis("off")
    boxes = [
        (1, 5, "PNG image\nuint8"),
        (4, 5, "Float /255\nLee filter"),
        (7, 5, "Otsu OR Niblack\nthreshold"),
        (7, 3, "Morphology + area\n8-connected regions"),
        (4, 3, "8 region features\ntrain-only scaler"),
        (1, 3, "Frozen SVM OR CART\nregion decision"),
        (1, 1, "Final mask\nregion JSON"),
        (5, 1, "Evaluation only\nGT + matching + metrics"),
    ]
    for x, y, label in boxes:
        ax.text(
            x,
            y,
            label,
            ha="center",
            va="center",
            fontsize=10,
            bbox={"boxstyle": "round,pad=0.6", "facecolor": "#edf3f7", "edgecolor": "#34536b"},
        )
    for start, end in [
        ((2, 5), (2.9, 5)),
        ((5.2, 5), (5.8, 5)),
        ((7, 4.5), (7, 3.55)),
        ((5.7, 3), (5.1, 3)),
        ((2.8, 3), (2.2, 3)),
        ((1, 2.45), (1, 1.55)),
        ((2.1, 1), (3.4, 1)),
    ]:
        ax.annotate("", xy=end, xytext=start, arrowprops={"arrowstyle": "->", "lw": 1.5})
    ax.text(9, 2, "Ground truth\nnot an inference input", fontsize=9, ha="center")
    ax.annotate(
        "",
        xy=(6.5, 1),
        xytext=(8.5, 1.7),
        arrowprops={"arrowstyle": "->", "lw": 1.5, "linestyle": "dashed"},
    )
    fig.tight_layout()
    fig.savefig(out / "pipeline.png", dpi=180)
    plt.close(fig)
    (out / "manifest.json").write_text(
        json.dumps(
            {
                "seed": 2026,
                "split": "validation",
                "sample_rule": "uniform sample without replacement, six patches",
                "image_ids": selected,
                "source": "results/sos/screen.json",
                "figures": ["dataset_examples.png", "parameter_study.png", "pipeline.png"],
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    print("Created 3 report figures with sample IDs and data source manifest")


if __name__ == "__main__":
    main()
