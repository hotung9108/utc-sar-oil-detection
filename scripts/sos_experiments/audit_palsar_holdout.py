"""Audit the unused external_train population before any new inference.

Exact pixel hashes cannot prove source-scene independence or rule out overlaps.
"""

import sys as _sys
from pathlib import Path as _Path
_project_root = _Path(__file__).resolve().parents[2]
_sys.path.insert(0, str(_project_root))
_sys.path.insert(0, str(_project_root / "src"))

import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]


def main():
    manifest_path = ROOT / 'data/manifest.json'
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    rows = manifest['records']
    target = [r for r in rows if r['split'] == 'external_train']
    assert len(target) == 3101
    assert all(r['sensor'] == 'palsar' and r['publisher_split'] == 'train' for r in target)
    groups = {}
    for number, row in enumerate(rows, 1):
        image_path, mask_path = ROOT / row['image'], ROOT / row['mask']
        assert hashlib.sha256(image_path.read_bytes()).hexdigest() == row['image_sha256']
        assert hashlib.sha256(mask_path.read_bytes()).hexdigest() == row['mask_sha256']
        with Image.open(image_path) as image:
            pixels = np.asarray(image.convert('L'))
        assert pixels.shape == (256, 256)
        digest = hashlib.sha256(pixels.tobytes()).hexdigest()
        groups.setdefault(digest, []).append({'id': row['id'], 'split': row['split']})
        if number % 1000 == 0:
            print(f'{number}/{len(rows)} verified', flush=True)
    crossing = [g for g in groups.values() if any(r['split'] == 'external_train' for r in g)
                and any(r['split'] != 'external_train' for r in g)]
    within = [g for g in groups.values() if sum(r['split'] == 'external_train' for r in g) > 1]
    audit = {'manifest_sha256': hashlib.sha256(manifest_path.read_bytes()).hexdigest(),
             'all_image_and_mask_file_hashes_verified': len(rows),
             'population': 'external_train', 'images': len(target),
             'cross_population_identical_grayscale_groups': crossing,
             'within_population_identical_grayscale_groups': within,
             'target_ids': sorted(r['id'] for r in target),
             'scope': 'File integrity and identical grayscale pixel audit only. Active training/search uses Sentinel train/validation; original external evaluation uses external_val. Historical manual exposure and source-scene independence are not established.',
             'scene_independence_verified': False,
             'model_inference_performed': False}
    out = ROOT / 'docs/management/palsar_holdout_audit.json'
    out.write_text(json.dumps(audit, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'images': len(target), 'cross_duplicate_groups': len(crossing),
                      'within_duplicate_groups': len(within)}))


if __name__ == '__main__':
    main()
