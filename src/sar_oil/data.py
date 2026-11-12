"""Reproducible patch split. Publisher validation is reserved for final testing."""

import hashlib
import json
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import numpy as np
from PIL import Image
from sklearn.model_selection import train_test_split

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "data/manifest.json"


def read_pair(row, mask_threshold=128):
    with Image.open(ROOT / row["image"]) as im:
        image = np.asarray(im.convert("L"), dtype=float) / 255
    with Image.open(ROOT / row["mask"]) as im:
        mask = np.asarray(im.convert("L")) >= mask_threshold
    return image, mask


def _record(path):
    mask = ROOT / "data/Refined-Deep-SAR/masks/masks" / path.parent.name / path.name
    with Image.open(mask) as im:
        empty = not (np.asarray(im.convert("L")) >= 128).any()
    return {
        "id": path.parent.name + "/" + path.stem,
        "sensor": path.stem.split("_")[0],
        "publisher_split": path.parent.name,
        "image": path.relative_to(ROOT).as_posix(),
        "mask": mask.relative_to(ROOT).as_posix(),
        "empty": bool(empty),
        "image_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "mask_sha256": hashlib.sha256(mask.read_bytes()).hexdigest(),
    }


def prepare():
    paths = sorted((ROOT / "data/Refined-Deep-SAR/images/images").glob("*/*.png"))
    if not paths:
        raise FileNotFoundError("Place SOS images and masks under data/Refined-Deep-SAR")
    with ThreadPoolExecutor(max_workers=8) as pool:
        rows = list(pool.map(_record, paths))
    expected = {
        ("sentinel", "train"): 3354,
        ("sentinel", "val"): 839,
        ("palsar", "train"): 3101,
        ("palsar", "val"): 776,
    }
    from collections import Counter

    if Counter((r["sensor"], r["publisher_split"]) for r in rows) != expected:
        raise ValueError(
            "SOS file inventory differs from the audited dataset; inspect before splitting"
        )
    indices = [
        i
        for i, r in enumerate(rows)
        if r["sensor"] == "sentinel" and r["publisher_split"] == "train"
    ]
    train, val = train_test_split(
        indices, test_size=671, random_state=2026, stratify=[rows[i]["empty"] for i in indices]
    )
    train, val = set(train), set(val)
    for i, r in enumerate(rows):
        r["split"] = (
            ("train" if i in train else "validation" if i in val else "test")
            if r["sensor"] == "sentinel"
            else "external_" + r["publisher_split"]
        )
    obj = {
        "seed": 2026,
        "mask_threshold": 128,
        "source": "https://zenodo.org/records/15298010",
        "limitations": [
            "No scene IDs: scene-independent split cannot be guaranteed",
            "No incidence angles, wind or separate look-alike labels",
        ],
        "records": rows,
    }
    MANIFEST.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")
    return obj


def records(split):
    if not MANIFEST.exists():
        raise FileNotFoundError("Run prepare first")
    return [
        r
        for r in json.loads(MANIFEST.read_text(encoding="utf-8"))["records"]
        if r["split"] == split
    ]
