"""Inspect a pinned candidate source; does not train or alter SOS experiments."""
import csv
import hashlib
import io
import json
from collections import Counter
from pathlib import Path
from urllib.request import urlopen

import numpy as np
import tifffile
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
REVISION = '1b9a62c30a9da9698eb470562aa976f9bd1e8fc3'
BASE = f'https://raw.githubusercontent.com/Garcia-INPE/oilspill-detection-dataset/{REVISION}/'


def main():
    cache = ROOT / '.cache/cantarell_source' / REVISION
    receipts = []

    def fetch(path):
        target = cache / path
        if not target.exists():
            with urlopen(BASE + path, timeout=45) as response:
                raw = response.read(20_000_001)
            if len(raw) > 20_000_000:
                raise ValueError('Source exceeds inspection download limit')
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(raw)
        raw = target.read_bytes()
        receipts.append(dict(path=path, url=BASE + path, bytes=len(raw),
                             sha256=hashlib.sha256(raw).hexdigest()))
        if raw.startswith(b'version https://git-lfs.github.com/spec/v1'):
            fields = dict(line.split(' ', 1) for line in raw.decode().splitlines())
            expected = fields['oid'].removeprefix('sha256:')
            size = int(fields['size'])
            if size > 20_000_000:
                raise ValueError('LFS object exceeds inspection limit')
            media = f'https://media.githubusercontent.com/media/Garcia-INPE/oilspill-detection-dataset/{REVISION}/{path}'
            obj = target.with_name(target.name + '.lfs-object')
            if not obj.exists():
                with urlopen(media, timeout=45) as response:
                    payload = response.read(20_000_001)
                if len(payload) != size or hashlib.sha256(payload).hexdigest() != expected:
                    raise ValueError('LFS object size/hash mismatch')
                obj.write_bytes(payload)
            raw = obj.read_bytes()
            if len(raw) != size or hashlib.sha256(raw).hexdigest() != expected:
                raise ValueError('Cached LFS object size/hash mismatch')
            receipts.append(dict(path=path, url=media, bytes=len(raw), sha256=expected,
                                 verified_against_lfs_pointer=True))
        return raw

    fetch('DATASET_CARD.md')
    fetch('README.md')
    fetch('LICENSE')
    rows = list(csv.DictReader(io.StringIO(fetch(
        'CSV/Oil_Stats_manual_windows_16bits_800x600.csv').decode('utf-8-sig')), delimiter=';'))
    split_rows = {}
    groups = {}
    sample_mask_path = None
    for split in ('train', 'val', 'test'):
        entries = list(csv.DictReader(io.StringIO(fetch(f'splits/{split}.csv').decode('utf-8-sig'))))
        split_rows[split] = len(entries)
        for entry in entries:
            if entry['sample_id'] == 'IMG_01_TILE_001':
                sample_mask_path = entry['mask_path']
        groups[split] = sorted({r['sample_id'].split('_TILE_')[0] for r in entries})
    raw = fetch('RASTER/IMG-TIFF/16-BIT/IMG_01_TILE_001.tiff')
    with tifffile.TiffFile(io.BytesIO(raw)) as tif:
        page = tif.pages[0]
        pixels = page.asarray()
        tags = {tag.name: str(tag.value) for tag in page.tags.values()
                if tag.name in ('ImageDescription', 'ModelPixelScaleTag', 'ModelTiepointTag',
                                'GeoKeyDirectoryTag', 'GeoAsciiParamsTag', 'GDAL_METADATA', 'GDAL_NODATA')}
    if sample_mask_path is None:
        raise ValueError('Inspection sample missing from split manifests')
    mask = np.asarray(Image.open(io.BytesIO(fetch(sample_mask_path))))
    finite = pixels[np.isfinite(pixels)]
    audit = {
        'repository': 'https://github.com/Garcia-INPE/oilspill-detection-dataset',
        'revision': REVISION, 'scope': 'metadata tables and one raster/mask; not a full dataset audit',
        'receipts': receipts, 'polygon_rows': len(rows), 'csv_columns': list(rows[0]),
        'classes': dict(Counter(r['CLASSE'] for r in rows)),
        'source_images': sorted({r['IMG_FNAME'] for r in rows}),
        'split_counts': split_rows, 'split_source_groups': groups,
        'cross_split_groups': {f'{a}/{b}': sorted(set(groups[a]) & set(groups[b]))
                               for a, b in [('train', 'val'), ('train', 'test'), ('val', 'test')]},
        'sample': {'name': 'IMG_01_TILE_001', 'shape': list(pixels.shape),
                   'dtype': str(pixels.dtype), 'finite_min': float(finite.min()),
                   'finite_max': float(finite.max()), 'tags': tags,
                   'mask_shape': list(mask.shape),
                   'mask_counts': {str(k): int(v) for k, v in zip(*np.unique(mask, return_counts=True))},
                   'same_grid_dimensions': pixels.shape == mask.shape},
        'eligibility': {
            'labelled_georeferenced_candidate': True,
            'physical_units_confirmed': False,
            'per_pixel_incidence_available_in_inspected_assets': False,
            'original_safe_identity_and_alignment_verified': False,
            'eligible_for_calibration_benefit_claim': False,
            'next_gate': 'Resolve full SAFE identity, radiometric units, polarization, processing history and label-to-native-grid alignment before freezing an experiment.'
        },
    }
    output = ROOT / 'docs/management/cantarell_source_audit.json'
    output.write_text(json.dumps(audit, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({k: audit[k] for k in ('polygon_rows', 'classes', 'split_counts', 'cross_split_groups', 'sample', 'eligibility')}, indent=2))


if __name__ == '__main__':
    main()
