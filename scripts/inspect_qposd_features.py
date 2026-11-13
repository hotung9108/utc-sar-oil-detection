"""Inspect three small QPOSD image/mask pairs; this is not a benchmark split."""
import hashlib
import io
import json
from pathlib import Path
import zipfile

import numpy as np
from PIL import Image
from scipy.io import loadmat

from audit_qposd import ROOT, RangeReader


def main():
    audit = json.loads((ROOT / 'docs/management/qposd_mask_audit.json').read_text())
    entry = audit['archive']
    folder = ROOT / 'data/lookalike_sources/qposd_features'
    folder.mkdir(parents=True, exist_ok=True)
    stream = RangeReader(entry['links']['self'], entry['size'], budget=80 * 1024**2)
    rows = []
    with zipfile.ZipFile(stream) as archive:
        for number in [7, 35, 40]:
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
    output = {'record': audit['record'], 'selection': [7, 35, 40],
              'selection_reason': 'Small archive members for structural inspection: sea/land, oil, look-alike; not a random or held-out evaluation set',
              'http_bytes': stream.transferred, 'pairs': rows,
              'scope': 'Shape/key/numeric checks do not establish geospatial alignment, physical calibration, or independent source scenes.'}
    (ROOT / 'docs/management/qposd_feature_audit.json').write_text(json.dumps(output, indent=2) + '\n', encoding='utf-8')


if __name__ == '__main__':
    main()
