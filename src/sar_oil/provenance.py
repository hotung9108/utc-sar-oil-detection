"""Prevent accidental reuse of experiment results after code/data/environment changes."""

import ast
import hashlib
import importlib.metadata
import json

from .data import MANIFEST, ROOT


def snapshot():
    files = sorted((ROOT / "src/sar_oil").glob("*.py"))
    return {
        "manifest_sha256": hashlib.sha256(MANIFEST.read_bytes()).hexdigest(),
        "code": {
            p.name: hashlib.sha256(
                ast.dump(ast.parse(p.read_text(encoding="utf-8"))).encode()
            ).hexdigest()
            for p in files
        },
        "source_sha256": {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in files},
        "packages": {
            p: importlib.metadata.version(p)
            for p in ("numpy", "scipy", "scikit-image", "scikit-learn", "Pillow", "matplotlib")
        },
    }


def ensure_run():
    current = snapshot()
    path = ROOT / "results/sos/run_manifest.json"
    if path.exists():
        old = json.loads(path.read_text(encoding="utf-8"))
        for key in ("manifest_sha256", "code", "packages"):
            if old[key] != current[key]:
                raise RuntimeError(
                    f"Experiment {key} changed. Archive results/sos under a new name before rerunning; do not mix old and new evidence."
                )
    else:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(current, indent=2), encoding="utf-8")
    return current
