"""Verify every archived file against its original SHA-256, without modifying it."""

import sys as _sys
from pathlib import Path as _Path
_project_root = _Path(__file__).resolve().parents[2]
_sys.path.insert(0, str(_project_root))
_sys.path.insert(0, str(_project_root / "scripts"))


import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ARCHIVE = ROOT / "legacy/pre_refactor_20261112"


def verify():
    records = json.loads((ARCHIVE / "manifest.json").read_text(encoding="utf-8"))
    failures = []
    for record in records:
        path = (ROOT / record["destination"]).resolve()
        if not path.is_relative_to(ARCHIVE.resolve()) or not path.is_file():
            failures.append(record["destination"])
            continue
        with path.open("rb") as stream:
            actual = hashlib.file_digest(stream, "sha256").hexdigest()
        if actual != record["sha256"] or path.stat().st_size != record["bytes"]:
            failures.append(record["destination"])
    if failures:
        raise RuntimeError(f"Archive mismatch: {failures}")
    return len(records)


if __name__ == "__main__":
    print(f"PASS: {verify()} archived files match original checksums")
