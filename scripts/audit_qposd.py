"""Inspect official QPOSD ZIP and RGB masks through bounded HTTP ranges.

Does not execute publisher code, train a model, or reinterpret look-alike subtypes.
"""
import hashlib
import io
import json
from pathlib import Path
import urllib.request
import zipfile

import numpy as np
from PIL import Image
from qposd_labels import decode_mask

ROOT = Path(__file__).resolve().parents[1]
RECORD = 'https://zenodo.org/api/records/19258036'
COLORS = {'sea': (0, 0, 255), 'oil': (255, 0, 0),
          'look_alike': (0, 255, 0), 'land': (0, 0, 0)}


class RangeReader(io.RawIOBase):
    def __init__(self, url, size, budget=32 * 1024**2):
        self.url, self.size, self.budget = url, size, budget
        self.position = self.transferred = 0

    def seekable(self):
        return True

    def tell(self):
        return self.position

    def seek(self, offset, whence=0):
        target = offset if whence == 0 else (self.position if whence == 1 else self.size) + offset
        if not 0 <= target <= self.size:
            raise ValueError('Seek outside archive')
        self.position = target
        return target

    def read(self, size=-1):
        size = self.size - self.position if size < 0 else min(size, self.size - self.position)
        if not size:
            return b''
        if self.transferred + size > self.budget:
            raise ValueError('HTTP range budget exceeded')
        end = self.position + size - 1
        req = urllib.request.Request(self.url, headers={'Range': f'bytes={self.position}-{end}'})
        with urllib.request.urlopen(req, timeout=45) as response:
            expected = f'bytes {self.position}-{end}/{self.size}'
            if response.status != 206 or response.headers.get('Content-Range') != expected:
                raise ValueError('Server did not honor exact byte range')
            data = response.read(size + 1)
        if len(data) != size:
            raise ValueError('Unexpected range length')
        self.position += size
        self.transferred += size
        return data


def main():
    folder = ROOT / 'data/lookalike_sources'
    folder.mkdir(parents=True, exist_ok=True)
    with urllib.request.urlopen(RECORD, timeout=30) as response:
        raw = response.read()
    metadata = json.loads(raw)
    (folder / '19258036.json').write_bytes(raw)
    entry = next(f for f in metadata['files'] if f['key'] == 'QPOSD.zip')
    stream = RangeReader(entry['links']['self'], entry['size'])
    rows = []
    totals = dict.fromkeys(COLORS, 0)
    with zipfile.ZipFile(stream) as archive:
        index = [{'name': f.filename, 'bytes': f.file_size, 'compressed_bytes': f.compress_size,
                  'crc32': f'{f.CRC:08x}'} for f in archive.infolist()]
        (folder / 'qposd_zip_index.json').write_text(json.dumps(index, indent=2), encoding='utf-8')
        masks = [f for f in archive.infolist() if f.filename.lower().endswith('.png') and 'mask' in f.filename.lower()]
        if not masks:
            raise ValueError('No masks found; inspect archive index')
        for i, info in enumerate(masks):
            if info.file_size > 16 * 1024**2:
                raise ValueError('Unexpected mask size')
            data = archive.read(info)  # zipfile verifies member CRC
            target = folder / 'qposd_masks' / f'{i:03d}.png'
            target.parent.mkdir(exist_ok=True)
            target.write_bytes(data)
            with Image.open(io.BytesIO(data)) as image:
                rgb = np.asarray(image.convert('RGB'))
            counts = {name: int(np.all(rgb == color, axis=-1).sum()) for name, color in COLORS.items()}
            unknown = int(rgb.shape[0] * rgb.shape[1] - sum(counts.values()))
            labels = decode_mask(rgb)
            assert int((labels == 255).sum()) == unknown
            colors, frequencies = np.unique(rgb[labels == 255], axis=0, return_counts=True)
            rows.append({'member': info.filename, 'local_path': target.relative_to(ROOT).as_posix(),
                         'shape': list(rgb.shape), 'sha256': hashlib.sha256(data).hexdigest(),
                         'counts': counts, 'unknown_pixels': unknown,
                         'unknown_colors': [{'rgb': c.tolist(), 'pixels': int(n)}
                                            for c, n in zip(colors, frequencies)]})
            for name, count in counts.items():
                totals[name] += count
            print(f'{i+1}/{len(masks)} {info.filename}: {counts}, unknown={unknown}', flush=True)
    audit = {'record': RECORD, 'license': metadata['metadata'].get('license'),
             'metadata_sha256': hashlib.sha256(raw).hexdigest(), 'archive': entry,
             'archive_full_checksum_verified': False, 'member_crc_verified': True,
             'http_bytes': stream.transferred, 'index': index, 'masks': rows,
             'totals': totals, 'unknown_pixels': sum(r['unknown_pixels'] for r in rows),
             'class_presence_masks': {name: sum(r['counts'][name] > 0 for r in rows) for name in totals},
             'decoder_verified_all_masks': True,
             'scope': 'Mask audit only. No feature arrays downloaded or model evaluated. Generic look-alike is not a physical subtype label.'}
    (ROOT / 'docs/management/qposd_mask_audit.json').write_text(
        json.dumps(audit, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')


if __name__ == '__main__':
    main()
