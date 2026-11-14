"""Run from repository root: python scripts/sos.py --help."""

import argparse
import json
import os
import sys
from pathlib import Path

for name in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(name, "1")
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))


def main():
    parser = argparse.ArgumentParser(description="SOS oil/background coursework experiments")
    parser.add_argument(
        "command",
        choices=[
            "prepare",
            "screen",
            "benchmark",
            "verify",
            "select",
            "evaluate",
            "predict",
            "reproduce",
        ],
    )
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--image", type=Path)
    parser.add_argument(
        "--selection",
        type=Path,
        default=Path("results/sos/selected.json"),
        help="Saved selection JSON for predict, including the supplementary adaptive branch",
    )
    parser.add_argument("--output", type=Path, default=Path("results/prediction"))
    args = parser.parse_args()
    from sar_oil import data, experiments

    if args.command in ("prepare", "reproduce"):
        data.prepare()
        print("Manifest prepared", flush=True)
    if args.command != "prepare":
        from sar_oil.provenance import ensure_run

        ensure_run()
    if args.command in ("verify", "reproduce"):
        from sar_oil.verification import verify

        result = verify()
        print(
            f"Verification: {len(result['checks'])} checks; passed={result['passed']}", flush=True
        )
        if not result["passed"]:
            print([check for check in result["checks"] if not check["passed"]])
            raise SystemExit(1)
        import runpy

        runpy.run_path(str(data.ROOT / "scripts/sos_experiments/verify_real_data.py"), run_name="__main__")
    if args.command == "screen":
        experiments.screen(args.workers)
    if args.command in ("benchmark", "reproduce"):
        experiments.benchmark(args.workers)
    if args.command in ("select", "reproduce"):
        experiments.select(args.workers)
    if args.command in ("evaluate", "reproduce"):
        experiments.evaluate(args.workers)
    if args.command == "predict":
        if args.image is None:
            parser.error("--image required")
        import numpy as np
        from PIL import Image

        from sar_oil.models import RegionModel
        from sar_oil.pipeline import predict

        selected = json.loads(args.selection.read_text(encoding="utf-8"))
        image = np.asarray(Image.open(args.image).convert("L"), float) / 255
        mask, regions = predict(
            image,
            selected["config"],
            RegionModel.load(args.selection.parent / selected["model_file"]),
        )
        args.output.mkdir(parents=True, exist_ok=True)
        Image.fromarray((mask * 255).astype("uint8")).save(args.output / "mask.png")
        rgb = np.repeat(image[..., None], 3, axis=2)
        rgb[mask] = 0.5 * rgb[mask] + 0.5 * np.array([1, 0, 0])
        Image.fromarray((rgb * 255).astype("uint8")).save(args.output / "overlay.png")
        experiments.write_json(
            args.output / "regions.json",
            {
                "regions": regions,
                "score_semantics": "decision score, not probability",
                "config": selected["config"],
            },
        )


if __name__ == "__main__":
    main()
