"""Record local source imports and potential ML indicators for manual review."""

import ast
import hashlib
import json
import subprocess
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FORBIDDEN = {
    "torch",
    "torchvision",
    "tensorflow",
    "keras",
    "sklearn",
    "xgboost",
    "lightgbm",
    "catboost",
    "onnx",
    "onnxruntime",
    "transformers",
    "ultralytics",
    "timm",
    "jax",
}


def main():
    """Inspect project files, write evidence, and fail on indicators needing review."""
    names = (
        subprocess.check_output(
            ["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"], cwd=ROOT
        )
        .decode("utf-8")
        .split("\0")
    )
    files = sorted({name for name in names if name and (ROOT / name).is_file()})
    python_files = [name for name in files if name.endswith(".py")]
    imports, findings, hashes = set(), [], {}
    for name in python_files:
        path = ROOT / name
        hashes[name] = hashlib.sha256(path.read_bytes()).hexdigest()
        tree = ast.parse(path.read_text(encoding="utf-8-sig"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                modules = [alias.name for alias in node.names]
            elif isinstance(node, ast.ImportFrom):
                modules = [node.module or ""]
            else:
                modules = []
            imports.update(m.split(".")[0] for m in modules if m)
            for module in modules:
                if module.split(".")[0] in FORBIDDEN:
                    findings.append(dict(file=name, line=node.lineno, import_name=module))
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
                if node.func.attr in {
                    "fit",
                    "fit_transform",
                    "backward",
                    "load_state_dict",
                    "readNet",
                    "readNetFromONNX",
                }:
                    findings.append(dict(file=name, line=node.lineno, call=ast.unparse(node.func)))
    model_files = [
        n
        for n in files
        if Path(n).suffix.lower()
        in {".pt", ".pth", ".onnx", ".h5", ".keras", ".safetensors", ".pkl", ".joblib"}
    ]
    result = dict(
        checked_at=datetime.now().astimezone().isoformat(timespec="seconds"),
        scope="Tracked and unignored project Python files; no environment or external directory scan",
        python_file_count=len(python_files),
        imported_roots=sorted(imports),
        ml_indicators=findings,
        potential_model_files=model_files,
        source_hashes=hashes,
        limitation="Static indicators do not prove absence of every possible NumPy or dynamically loaded ML implementation; production call chain was also reviewed.",
    )
    destination = ROOT / "docs/management/no_ml_audit.json"
    destination.write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps({k: v for k, v in result.items() if k != "source_hashes"}, ensure_ascii=False))
    if findings or model_files:
        raise SystemExit("Review ML indicators before claiming no ML/DL")


if __name__ == "__main__":
    main()
