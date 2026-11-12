"""Inventory only this project's supplied JPEG files and local CSIRO metadata."""

import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]


def build_inventory():
    """Return counts, dimensions, exact-duplicate groups and sample overlap."""
    paths = sorted((ROOT / "kaggle/data").glob("Class_*/*.jpg"))
    hashes = defaultdict(list)
    sizes = Counter()
    classes = Counter()
    for path in paths:
        relative = path.relative_to(ROOT).as_posix()
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        hashes[digest].append(relative)
        with Image.open(path) as picture:
            sizes[f"{picture.width}x{picture.height} {picture.mode}"] += 1
        classes[path.parent.name] += 1
    overlap = {}
    for path in sorted((ROOT / "data/sample").rglob("*.jpg")):
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        overlap[path.relative_to(ROOT).as_posix()] = hashes.get(digest, [])
    all_images = sorted(
        p
        for p in (ROOT / "kaggle/data").rglob("*")
        if p.is_file() and p.suffix.lower() in {".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff"}
    )
    canonical_paths = set(paths)
    extra_copies = {}
    for path in all_images:
        if path not in canonical_paths:
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            extra_copies[path.relative_to(ROOT).as_posix()] = hashes.get(digest, [])
    if any(not matches for matches in extra_copies.values()):
        raise ValueError(
            "Found additional nonduplicate dataset images outside evaluated Class_0/Class_1"
        )
    result = dict(
        source_metadata="kaggle/metadata/dataset_metadata.xml",
        source_doi="10.25919/4v55-dn16",
        license_file="kaggle/metadata/license.html",
        license_as_stated="CC BY-SA 4.0",
        published_counts={"Class_0": 3725, "Class_1": 1905},
        local_counts=dict(classes),
        dimensions=dict(sizes),
        exact_duplicate_groups=[v for v in hashes.values() if len(v) > 1],
        sample_exact_matches=overlap,
        local_image_files_including_copies=len(all_images),
        additional_kaggle_copies=extra_copies,
        caution="File hashes show byte identity only, not independence of overlapping source scenes. Original collection checksums are not supplied.",
    )
    target = ROOT / "results/reproducible/data_inventory.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(
        json.dumps(
            {
                k: v
                for k, v in result.items()
                if k not in ["sample_exact_matches", "exact_duplicate_groups"]
            }
        )
    )
    print("Exact duplicate groups:", len(result["exact_duplicate_groups"]))
    print("Samples matching dataset:", sum(bool(x) for x in overlap.values()))
    return result


if __name__ == "__main__":
    build_inventory()
