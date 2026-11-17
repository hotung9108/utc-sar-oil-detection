"""Inventory all publisher splits, float TIFFs, masks and vectors before modelling."""

import sys as _sys
from pathlib import Path as _Path
_project_root = _Path(__file__).resolve().parents[2]
_sys.path.insert(0, str(_project_root))
_sys.path.insert(0, str(_project_root / "src"))

import csv
import hashlib
import io
import json
import time
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.request import urlopen

import numpy as np
import tifffile
from PIL import Image
from matplotlib.path import Path as PolygonPath

from scripts.cantarell.audit_cantarell_source import BASE, REVISION, ROOT

CACHE = ROOT / '.cache/cantarell_source' / REVISION


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def fetch(path):
    target = CACHE / path
    receipts = []

    def download(url, maximum):
        for attempt in range(3):
            try:
                with urlopen(url, timeout=45) as response:
                    raw = response.read(maximum+1)
                if len(raw) > maximum:
                    raise ValueError('Asset exceeds download limit')
                return raw
            except (OSError, TimeoutError):
                if attempt == 2:
                    raise
                time.sleep(2*(attempt+1))

    if not target.exists():
        raw = download(BASE+path, 20_000_000)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(raw)
    raw = target.read_bytes()
    receipts.append({'url': BASE+path, 'bytes': len(raw), 'sha256': digest(raw)})
    if raw.startswith(b'version https://git-lfs.github.com/spec/v1'):
        fields = dict(line.split(' ', 1) for line in raw.decode().splitlines())
        expected, size = fields['oid'].removeprefix('sha256:'), int(fields['size'])
        if size > 20_000_000:
            raise ValueError('LFS payload exceeds limit')
        obj = target.with_name(target.name+'.lfs-object')
        url = f'https://media.githubusercontent.com/media/Garcia-INPE/oilspill-detection-dataset/{REVISION}/{path}'
        if not obj.exists():
            payload = download(url, size)
            if len(payload) != size or digest(payload) != expected:
                raise ValueError('LFS download hash/size mismatch')
            obj.write_bytes(payload)
        raw = obj.read_bytes()
        if len(raw) != size or digest(raw) != expected:
            raise ValueError('LFS cached hash/size mismatch')
        receipts.append({'url': url, 'bytes': len(raw), 'sha256': expected, 'lfs_verified': True})
    return raw, receipts


def inspect(entry):
    sample = entry['sample_id']
    receipts = []

    def get(path):
        raw, rows = fetch(path)
        receipts.extend(rows)
        return raw

    raw = get(f'RASTER/IMG-TIFF/16-BIT/{sample}.tiff')
    tiff_hash = digest(raw)
    with tifffile.TiffFile(io.BytesIO(raw)) as tif:
        page = tif.pages[0]
        image = page.asarray()
        scale, tie = page.tags['ModelPixelScaleTag'].value, page.tags['ModelTiepointTag'].value
        crs = str(page.tags['GeoAsciiParamsTag'].value)
    mask_raw = get(entry['mask_path'])
    mask = np.asarray(Image.open(io.BytesIO(mask_raw)))
    vector = json.loads(get(f'RASTER/LABELS-VECTOR/GEOJSON/{sample}.geojson'))
    if image.ndim != 2 or image.shape != mask.shape:
        raise ValueError(f'{sample}: incompatible dimensions')
    height, width = image.shape
    bounds = [tie[3]-tie[0]*scale[0], tie[4]-(height-tie[1])*scale[1],
              tie[3]+(width-tie[0])*scale[0], tie[4]+tie[1]*scale[1]]
    # Expected class interpretation is tested, not silently imposed on masks.
    class_regions = {name: np.zeros(image.shape, dtype=bool) for name in ('OIL SPILL', 'SEEPAGE SLICK')}
    classes = Counter()
    properties = []
    for feature in vector['features']:
        props, geom = feature['properties'], feature['geometry']
        classes[props['CLASSE']] += 1
        properties.append({k: props.get(k) for k in ('ID_POLY', 'DATE', 'TIME_ACQ', 'IMG_NUMBER', 'CLASSE')})
        if props['CLASSE'] not in class_regions:
            class_regions[props['CLASSE']] = np.zeros(image.shape, dtype=bool)
        if geom['type'] not in ('Polygon', 'MultiPolygon'):
            raise ValueError('Unsupported vector geometry')
        polygons = [geom['coordinates']] if geom['type'] == 'Polygon' else geom['coordinates']
        for rings in polygons:
            outer = np.asarray(rings[0])
            # Restrict point-in-polygon work to an expanded pixel bounding rectangle.
            cp = (outer[:, 0]-tie[3])/scale[0]+tie[0]-.5
            rp = (tie[4]-outer[:, 1])/scale[1]+tie[1]-.5
            r0, r1 = max(0, int(np.floor(rp.min()))-1), min(height, int(np.ceil(rp.max()))+2)
            c0, c1 = max(0, int(np.floor(cp.min()))-1), min(width, int(np.ceil(cp.max()))+2)
            if r0 >= r1 or c0 >= c1:
                continue
            rr, cc = np.mgrid[r0:r1, c0:c1]
            coords = np.column_stack(((tie[3]+(cc+.5-tie[0])*scale[0]).ravel(),
                                      (tie[4]-(rr+.5-tie[1])*scale[1]).ravel()))
            inside = PolygonPath(outer).contains_points(coords)
            for hole in rings[1:]:
                inside &= ~PolygonPath(np.asarray(hole)).contains_points(coords)
            class_regions[props['CLASSE']][r0:r1, c0:c1] |= inside.reshape(rr.shape)
    foreground = np.logical_or.reduce(list(class_regions.values()))
    finite = image[np.isfinite(image)]
    return {'sample': sample, 'split': entry['split'], 'group': sample.split('_TILE_')[0],
            'shape': list(image.shape), 'dtype': str(image.dtype), 'crs': crs, 'bounds_wsen': bounds,
            'image_sha256': tiff_hash, 'mask_sha256': digest(mask_raw), 'receipts': receipts,
            'nonfinite_pixels': int(image.size-finite.size),
            'finite_min': float(finite.min()), 'finite_max': float(finite.max()),
            'mask_counts': {str(k): int(v) for k, v in zip(*np.unique(mask, return_counts=True))},
            'vector_classes': dict(classes), 'vector_properties': properties,
            'foreground_vector_mask_disagreement': int(np.count_nonzero(foreground != (mask > 0))),
            'hypothesis_oil1_disagreement': int(np.count_nonzero(class_regions['OIL SPILL'] != (mask == 1))),
            'hypothesis_seepage2_disagreement': int(np.count_nonzero(class_regions['SEEPAGE SLICK'] != (mask == 2))),
            'hypothesis_seepage_priority_oil1_disagreement': int(np.count_nonzero((class_regions['OIL SPILL'] & ~class_regions['SEEPAGE SLICK']) != (mask == 1))),
            'oil_seepage_vector_overlap_pixels': int(np.count_nonzero(class_regions['OIL SPILL'] & class_regions['SEEPAGE SLICK']))}


def main():
    entries, manifest_receipts = [], []
    for split in ('train', 'val', 'test'):
        raw, receipts = fetch(f'splits/{split}.csv')
        manifest_receipts.extend(receipts)
        entries.extend(dict(r, split=split) for r in csv.DictReader(io.StringIO(raw.decode('utf-8-sig'))))
    if len({r['sample_id'] for r in entries}) != len(entries):
        raise ValueError('Duplicate sample IDs in manifests')
    results, errors = [], []
    with ThreadPoolExecutor(max_workers=4) as pool:
        pending = {pool.submit(inspect, r): r for r in entries}
        for future in as_completed(pending):
            entry = pending[future]
            try:
                results.append(future.result())
            except Exception as exc:
                errors.append({'sample': entry['sample_id'], 'error': f'{type(exc).__name__}: {exc}'})
            completed = len(results)+len(errors)
            if completed % 10 == 0 or completed == len(entries):
                print(f'Checked {completed}/{len(entries)}; errors={len(errors)}', flush=True)
    results.sort(key=lambda r: r['sample'])
    groups, hashes = defaultdict(set), defaultdict(list)
    for r in results:
        groups[r['group']].add(r['split'])
        hashes[r['image_sha256']].append(r['sample'])
    overlapping = []
    for i, a in enumerate(results):
        for b in results[i+1:]:
            if a['group'] != b['group']:
                continue
            aa, bb = a['bounds_wsen'], b['bounds_wsen']
            area = max(0, min(aa[2], bb[2])-max(aa[0], bb[0]))*max(0, min(aa[3], bb[3])-max(aa[1], bb[1]))
            if area > 0:
                overlapping.append({'samples': [a['sample'], b['sample']], 'intersection_area_degrees2': area,
                                    'cross_split': a['split'] != b['split']})
    result = {'revision': REVISION, 'script_sha256': digest(__import__('pathlib').Path(__file__).read_bytes()),
              'expected_samples': len(entries), 'checked_samples': len(results), 'errors': errors,
              'complete_inventory': len(results) == len(entries) and not errors,
              'manifest_receipts': manifest_receipts, 'samples': results,
              'split_counts': dict(Counter(r['split'] for r in results)),
              'cross_split_source_groups': {k: sorted(v) for k, v in groups.items() if len(v) > 1},
              'identical_tiff_groups': [v for v in hashes.values() if len(v) > 1],
              'same_source_overlapping_pairs': overlapping,
              'foreground_disagreement_samples': [r['sample'] for r in results if r['foreground_vector_mask_disagreement']],
              'class_encoding_disagreement_samples': [r['sample'] for r in results if r['hypothesis_oil1_disagreement'] or r['hypothesis_seepage2_disagreement']],
              'seepage_priority_encoding_disagreement_samples': [r['sample'] for r in results if r['hypothesis_seepage_priority_oil1_disagreement'] or r['hypothesis_seepage2_disagreement']],
              'limits': ['File/geometry audit, not a model evaluation or visual review of every image.',
                         'Source groups use publisher acquisition identifiers; full SAFE matching for all groups remains to be checked.',
                         'Similar geography across acquisition dates is not automatically train/test leakage.',
                         'No validation/test scores used to select an algorithm.']}
    output = ROOT / 'docs/management/cantarell_full_inventory.json'
    output.write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({k: result[k] for k in ('expected_samples', 'checked_samples', 'complete_inventory', 'errors', 'cross_split_source_groups', 'identical_tiff_groups', 'foreground_disagreement_samples', 'class_encoding_disagreement_samples')}, indent=2))


if __name__ == '__main__':
    main()
