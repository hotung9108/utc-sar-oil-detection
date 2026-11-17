"""Audit executed notebooks and metric aggregation; save local preview images."""

import base64
import json
import sys
from pathlib import Path

import nbformat

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from sar_oil.evaluation import summarize
from sar_oil.provenance import ensure_run

ensure_run()
preview = ROOT / ".cache/notebook_previews"
preview.mkdir(parents=True, exist_ok=True)
evidence = []
paths = sorted((ROOT / "notebooks").glob("*.ipynb"))
assert len(paths) >= 5
for path in paths:
    nb = nbformat.read(path, as_version=4)
    nbformat.validate(nb)
    code = [c for c in nb.cells if c.cell_type == "code"]
    assert all(c.execution_count is not None for c in code), path
    assert not any(o.output_type == "error" for c in code for o in c.outputs), path
    images = [
        o.data["image/png"] for c in code for o in c.outputs if "image/png" in o.get("data", {})
    ]
    assert images, path
    (preview / (path.stem + ".png")).write_bytes(base64.b64decode(images[-1]))
    evidence.append({"notebook": path.name, "executed_cells": len(code), "figures": len(images)})
evaluation = json.loads((ROOT / "results/sos/evaluation.json").read_text())
for name, value in evaluation.items():
    if name != "provenance":
        assert summarize([r["counts"] for r in value["per_image"]]) == value["metrics"], name
selected = json.loads((ROOT / "results/sos/selected.json").read_text())
assert selected["metrics"] == evaluation["validation_label128"]["metrics"]
audit = {
    "notebooks": evidence,
    "all_executed": True,
    "no_cell_errors": True,
    "aggregated_metrics_verified": True,
    "numpy_full_pipeline_matches_validation": True,
}
(ROOT / "docs/management/notebook_execution_audit.json").write_text(
    json.dumps(audit, indent=2), encoding="utf-8"
)
print(json.dumps(audit, indent=2))
