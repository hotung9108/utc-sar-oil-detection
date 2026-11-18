"""Read-only dataset audit. Requires Pillow and NumPy; does not train or edit data."""

import sys as _sys
from pathlib import Path as _Path
_project_root = _Path(__file__).resolve().parents[2]
_sys.path.insert(0, str(_project_root))
_sys.path.insert(0, str(_project_root / "src"))


import argparse
import hashlib
import json
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import numpy as np
from PIL import Image


def read_pair(paths):
    name, image_path, mask_path = paths
    try:
        with Image.open(image_path) as im:
            a, image_mode, metadata = np.array(im), im.mode, list(im.info)
        with Image.open(mask_path) as im:
            b, mask_mode = np.array(im), im.mode
        return name, (a, b, image_mode, mask_mode, metadata), None
    except (OSError, ValueError) as exc:
        return name, None, str(exc)


def read_batches(images, masks):
    names = sorted(images.keys() & masks.keys())
    with ThreadPoolExecutor(max_workers=8) as pool:
        for start in range(0, len(names), 128):
            batch = names[start : start + 128]
            yield from pool.map(read_pair, [(n, images[n], masks[n]) for n in batch])
            if start % 1024 == 0:
                print(f"  inspected {min(start + 128, len(names))}/{len(names)}", flush=True)


def audit(root):
    image_root = root / "images/images"
    mask_root = root / "masks/masks"
    report = {"root": str(root), "splits": {}, "errors": [], "duplicate_image_pixels": []}
    hashes = defaultdict(list)
    for split in ("train", "val"):
        images = {p.name: p for p in (image_root / split).glob("*.png")}
        masks = {p.name: p for p in (mask_root / split).glob("*.png")}
        groups = defaultdict(Counter)
        shapes, modes, labels, meta = Counter(), Counter(), Counter(), Counter()
        for name, pair, error in read_batches(images, masks):
            try:
                if error:
                    raise ValueError(error)
                a, b, image_mode, mask_mode, metadata = pair
                modes[f"image:{image_mode}"] += 1
                modes[f"mask:{mask_mode}"] += 1
                meta.update(metadata)
                shapes[str((a.shape, b.shape))] += 1
                if a.shape[:2] != b.shape[:2]:
                    report["errors"].append([split, name, "dimension mismatch"])
                values, counts = np.unique(b, return_counts=True)
                labels.update({str(int(v)): int(n) for v, n in zip(values, counts)})
                sensor = name.split("_")[0]
                g = groups[sensor]
                g["pairs"] += 1
                g["pixels"] += b.shape[0] * b.shape[1]
                mask = b if b.ndim == 2 else b[..., 0]
                g["nonbinary_masks"] += int(bool(np.any((mask != 0) & (mask != 255))))
                g["intermediate_pixels"] += int(np.count_nonzero((mask != 0) & (mask != 255)))
                g["foreground_ge128_pixels"] += int(np.count_nonzero(mask >= 128))
                if np.any((mask != 0) & (mask != 255)):
                    report.setdefault("nonbinary_examples", [])
                    if len(report["nonbinary_examples"]) < 10:
                        report["nonbinary_examples"].append([split, name])
                g["foreground_nonzero_pixels"] += int(np.count_nonzero(mask))
                g["empty_masks"] += int(not mask.any())
                g["full_masks"] += int(bool(np.all(mask != 0)))
                if a.ndim == 3:
                    g["rgb_channels_equal"] += int(bool(np.all(a == a[..., :1])))
                if b.ndim == 3:
                    g["mask_channels_equal"] += int(bool(np.all(b == b[..., :1])))
                h = hashlib.sha256(str(a.shape).encode() + a.tobytes()).hexdigest()
                mh = hashlib.sha256(b.tobytes()).hexdigest()
                hashes[h].append({"split": split, "name": name, "mask_hash": mh})
            except (OSError, ValueError, TypeError) as exc:
                report["errors"].append([split, name, str(exc)])
        report["splits"][split] = {
            "images": len(images),
            "masks": len(masks),
            "missing_masks": sorted(images.keys() - masks.keys()),
            "orphan_masks": sorted(masks.keys() - images.keys()),
            "groups": dict(groups),
            "shapes": dict(shapes),
            "modes": dict(modes),
            "mask_value_counts": dict(labels),
            "image_metadata_keys": dict(meta),
        }
        print(f"{split}: {len(images)} images / {len(masks)} masks", flush=True)
    duplicates = [v for v in hashes.values() if len(v) > 1]
    report["duplicate_image_pixels"] = duplicates
    report["cross_split_duplicate_groups"] = sum(
        len({p["split"] for p in g}) > 1 for g in duplicates
    )
    report["conflicting_mask_duplicate_groups"] = sum(
        len({p["mask_hash"] for p in g}) > 1 for g in duplicates
    )
    report["auxiliary_files"] = [
        p.relative_to(root).as_posix()
        for p in root.rglob("*")
        if p.is_file()
        and p.suffix.lower() != ".png"
        and "__MACOSX" not in p.parts
        and p.name != ".DS_Store"
    ]
    report["limitations"] = [
        "Exact decoded pixel duplicates only; no near-duplicate or scene-independence guarantee.",
        "Nonzero mask pixels counted, class semantics must be confirmed from publisher.",
        "No archive ZIP available: publisher MD5 not verified.",
    ]
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("data/Refined-Deep-SAR"))
    parser.add_argument(
        "--output", type=Path, default=Path("docs/management/refined_sos_audit.json")
    )
    args = parser.parse_args()
    result = audit(args.root)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print("Saved audit:", args.output)
