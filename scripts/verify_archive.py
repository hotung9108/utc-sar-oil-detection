"""Verify every archived file against its original SHA-256, without modifying it."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
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
