"""Inventory exact-color reference objects before selecting a QPOSD protocol.

No images, model predictions, training, or benchmark scores are read. Counts
at 64 pixels are a diagnostic inherited from SOS, not an eligibility rule.
"""

import sys as _sys
from pathlib import Path as _Path
_project_root = _Path(__file__).resolve().parents[2]
_sys.path.insert(0, str(_project_root))
_sys.path.insert(0, str(_project_root / "src"))

import hashlib
import json
from pathlib import Path
import sys
import time

import numpy as np
from PIL import Image
from scipy import ndimage

from scripts.qposd.qposd_labels import decode_mask

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'src'))
from sar_oil.core import label as numpy_label


def main():
    shape_path = ROOT / 'docs/management/qposd_shape_audit.json'
    mask_path = ROOT / 'docs/management/qposd_mask_audit.json'
    shapes = json.loads(shape_path.read_text(encoding='utf-8'))
    masks = json.loads(mask_path.read_text(encoding='utf-8'))
    rows = []
    for pair in shapes['pairs']:
        record = next(m for m in masks['masks']
                      if m['member'] == f"train_masks/mask{pair['number']}.png")
        path = ROOT / record['local_path']
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        if digest != record['sha256'] or digest != pair['mask_sha256']:
            raise ValueError(f'Mask changed: {path}')
        with Image.open(path) as image:
            decoded = decode_mask(np.asarray(image.convert('RGB')))
        classes = {}
        for value, name in ((1, 'oil'), (2, 'look_alike')):
            start = time.perf_counter()
            components, count = ndimage.label(decoded == value, np.ones((3, 3)))
            scipy_seconds = time.perf_counter() - start
            start = time.perf_counter()
            own = numpy_label(decoded == value)
            numpy_seconds = time.perf_counter() - start
            # Compare partitions up to permutation of component IDs, including
            # every background pixel. Equal counts alone are insufficient.
            mapping = np.zeros(int(own.max()) + 1, dtype=np.int32)
            mapping[own.ravel()] = components.ravel()
            equivalent = (len(mapping) == count + 1
                          and len(np.unique(mapping)) == count + 1
                          and np.array_equal(mapping[own], components))
            if not equivalent:
                raise ValueError(f'NumPy/SciPy partition mismatch: {path}, {name}')
            areas = np.bincount(components.ravel())[1:]
            assert len(areas) == count and int(areas.sum()) == record['counts'][name]
            classes[name] = {
                'pixels': int(areas.sum()), 'objects': count,
                'areas_sorted': sorted(map(int, areas)),
                'objects_below_64_pixels': int((areas < 64).sum()),
                'pixels_in_objects_below_64': int(areas[areas < 64].sum()),
                'objects_at_least_64_pixels': int((areas >= 64).sum()),
                'numpy_scipy_partitions_equal': bool(equivalent),
                'numpy_seconds_single_run': numpy_seconds,
                'scipy_seconds_single_run': scipy_seconds,
            }
        rows.append({'number': pair['number'], 'mask_sha256': digest,
                     'shape_matches': pair['spatial_shape_matches'],
                     'unknown_pixels': int((decoded == 255).sum()),
                     'classes': classes})
    totals = {}
    for scope, selected in (('all_41', rows),
                            ('shape_matching_24', [r for r in rows if r['shape_matches']])):
        totals[scope] = {
            name: {key: sum(r['classes'][name][key] for r in selected)
                   for key in ('pixels', 'objects', 'objects_below_64_pixels',
                               'pixels_in_objects_below_64', 'objects_at_least_64_pixels')}
            for name in ('oil', 'look_alike')}
    audit = {'script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
             'numpy_core_sha256': hashlib.sha256((ROOT / 'src/sar_oil/core.py').read_bytes()).hexdigest(),
             'inputs_sha256': {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                               for p in (shape_path, mask_path)},
             'connectivity': 8, 'rows': rows, 'totals': totals,
             'scope': 'Reference-mask connected components only. No model scores. '
                      'Unknown colors ignored; no relabeling or resizing. A component '
                      'is a raster object, not necessarily one physical spill. Shape '
                      'matching does not prove alignment or independent scenes. '
                      'The 64-pixel counts are diagnostic, not a chosen filter.'}
    output = ROOT / 'docs/management/qposd_object_audit.json'
    output.write_text(json.dumps(audit, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(totals, indent=2))


if __name__ == '__main__':
    main()
