"""Production core may use NumPy, Python and project modules, not reference APIs."""

import ast
from pathlib import Path


def test_core_does_not_import_reference_libraries():
    paths = (
        list(Path("src/tv3").glob("*.py"))
        + list(Path("src/tv4").glob("*.py"))
        + [Path("src/tv5/metrics.py")]
    )
    forbidden = {"cv2", "scipy", "skimage", "torch", "tensorflow", "sklearn"}
    for p in paths:
        for node in ast.walk(ast.parse(p.read_text(encoding="utf-8"))):
            if isinstance(node, ast.Import):
                names = [n.name for n in node.names]
            elif isinstance(node, ast.ImportFrom):
                names = [node.module or ""]
            else:
                continue
            assert not any(n.split(".")[0] in forbidden for n in names), (p, names)
