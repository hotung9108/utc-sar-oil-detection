"""Inspect selected QPOSD image/mask pairs; this is not a benchmark split."""

import sys as _sys
from pathlib import Path as _Path
_project_root = _Path(__file__).resolve().parents[2]
_sys.path.insert(0, str(_project_root))
_sys.path.insert(0, str(_project_root / "src"))

import argparse
import hashlib
import io
import json
from pathlib import Path
import zipfile

import numpy as np
from PIL import Image
from scipy.io import loadmat

from scripts.qposd.audit_qposd import ROOT, RangeReader


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--numbers', type=int, nargs='+', default=[7, 35, 40])
    parser.add_argument('--budget-mib', type=int, default=80,
                        help='Maximum HTTP bytes in MiB for this inspection (1..4096)')
    parser.add_argument('--output', type=Path, default=ROOT / 'docs/management/qposd_feature_audit.json')
    parser.add_argument('--selection-reason', default='Small archive members for structural inspection: sea/land, oil, look-alike; not a random or held-out evaluation set')
    args = parser.parse_args()
    if not 1 <= args.budget_mib <= 4096:
        parser.error('--budget-mib must be between 1 and 4096')
    if len(set(args.numbers)) != len(args.numbers) or any(n < 1 or n > 41 for n in args.numbers):
        parser.error('Choose distinct published sample numbers from 1 to 41')
    if args.numbers != [7, 35, 40] and args.output.resolve() == (ROOT / 'docs/management/qposd_feature_audit.json').resolve():
        parser.error('Use a separate --output to preserve the original three-pair audit')
    audit = json.loads((ROOT / 'docs/management/qposd_mask_audit.json').read_text(encoding='utf-8'))
    entry = audit['archive']
    folder = ROOT / 'data/lookalike_sources/qposd_features'
    folder.mkdir(parents=True, exist_ok=True)
    stream = RangeReader(entry['links']['self'], entry['size'], budget=args.budget_mib * 1024**2)
    rows = []
    with zipfile.ZipFile(stream) as archive:
        for number in args.numbers:
            member = f'train_images_9ch/image{number}.mat'
            info = archive.getinfo(member)
            target = folder / f'image{number}.mat'
            if target.exists():
                import zlib
                raw = target.read_bytes()
                assert len(raw) == info.file_size and zlib.crc32(raw) == info.CRC
            else:
                raw = archive.read(info)
                target.write_bytes(raw)
            mat = loadmat(io.BytesIO(raw))
            arrays = {k: v for k, v in mat.items() if not k.startswith('__')}
            mask_row = next(r for r in audit['masks'] if r['member'] == f'train_masks/mask{number}.png')
            with Image.open(ROOT / mask_row['local_path']) as image:
                mask_shape = [image.height, image.width]
            details = {}
            for key, value in arrays.items():
                item = {'shape': list(value.shape), 'dtype': str(value.dtype)}
                if np.issubdtype(value.dtype, np.number):
                    item['all_finite'] = bool(np.isfinite(value).all())
                    if value.ndim == 3:
                        item['channels'] = [{'min': float(np.min(value[:, :, c])),
                                             'max': float(np.max(value[:, :, c])),
                                             'mean': float(np.mean(value[:, :, c])),
                                             'std': float(np.std(value[:, :, c]))}
                                            for c in range(value.shape[2])]
                details[key] = item
            row = {'member': member, 'sha256': hashlib.sha256(raw).hexdigest(),
                   'bytes': len(raw), 'crc32_verified': True, 'variables': details,
                   'mask_member': mask_row['member'], 'mask_shape': mask_shape,
                   'publisher_T_key_present': 'T' in arrays,
                   'matching_spatial_shape': 'T' in arrays and list(arrays['T'].shape[:2]) == mask_shape}
            rows.append(row)
            print(json.dumps(row), flush=True)
    output = {'record': audit['record'], 'selection': args.numbers,
              'selection_reason': args.selection_reason,
              'http_bytes': stream.transferred, 'pairs': rows,
              'scope': 'Shape/key/numeric checks do not establish geospatial alignment, physical calibration, or independent source scenes.'}
    args.output.write_text(json.dumps(output, indent=2) + '\n', encoding='utf-8')


if __name__ == '__main__':
    main()
