"""Read bounded MAT prefixes to screen all QPOSD image/mask dimensions.

This checks structure only. Partial members cannot be CRC-verified and do not
establish pixel alignment, numeric validity, or independent source scenes.
"""
import hashlib
import json
import struct
import zlib
import zipfile

from audit_qposd import ROOT, RangeReader


def first_array_shape(prefix):
    """Strict parser for the observed little-endian compressed MAT v5 layout."""
    if len(prefix) < 136 or prefix[126:128] != b'IM':
        raise ValueError('Unsupported MAT header')
    outer_type, _ = struct.unpack_from('<II', prefix, 128)
    if outer_type != 15:
        raise ValueError('Expected compressed first element')
    inner = zlib.decompressobj().decompress(prefix[136:], 2048)
    if len(inner) < 8 or struct.unpack_from('<I', inner)[0] != 14:
        raise ValueError('Expected first matrix')

    def element(offset):
        if offset + 8 > len(inner):
            raise ValueError('Insufficient header prefix')
        tag, length = struct.unpack_from('<II', inner, offset)
        if tag >> 16:
            size = tag >> 16
            if size > 4:
                raise ValueError('Invalid compact element')
            return tag & 65535, inner[offset+4:offset+4+size], offset+8
        end = offset + 8 + length
        if end > len(inner):
            raise ValueError('Insufficient element prefix')
        return tag, inner[offset+8:end], offset+8+((length+7)//8)*8

    flag_type, flags, pos = element(8)
    if flag_type != 6 or len(flags) != 8:
        raise ValueError('Unsupported array flags')
    dim_type, dims, pos = element(pos)
    if dim_type != 5 or len(dims) != 12:
        raise ValueError('Expected three dimensions')
    shape = struct.unpack('<iii', dims)
    name_type, name, _ = element(pos)
    if name_type != 1 or name != b'T' or min(shape) <= 0 or shape[2] != 9:
        raise ValueError('Expected positive H x W x 9 array T')
    return list(shape)


def main():
    masks = json.loads((ROOT/'docs/management/qposd_mask_audit.json').read_text(encoding='utf-8'))
    entry = masks['archive']
    stream = RangeReader(entry['links']['self'], entry['size'], budget=4*1024**2)
    prefix_dir = ROOT/'data/lookalike_sources/qposd_prefixes'
    prefix_dir.mkdir(parents=True, exist_ok=True)
    rows = []
    destination = ROOT/'docs/management/qposd_shape_audit.json'

    def save():
        report = {'record': masks['record'], 'archive': entry,
                  'complete': len(rows) == 41, 'expected_pairs': 41, 'checked_pairs': len(rows),
                  'http_bytes': stream.transferred, 'pairs': rows,
                  'matching_pairs': sum(r['spatial_shape_matches'] for r in rows),
                  'mismatching_pairs': sum(not r['spatial_shape_matches'] for r in rows),
                  'full_mat_crc_verified': False, 'pixel_alignment_verified': False,
                  'scope': 'Bounded prefix structure screening, not a benchmark eligibility decision or model evaluation'}
        destination.write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')

    with zipfile.ZipFile(stream) as archive:
        for number in range(1, 42):
            member = f'train_images_9ch/image{number}.mat'
            with archive.open(member) as source:
                prefix = source.read(16384)
            shape = first_array_shape(prefix)
            target = prefix_dir/f'image{number}.prefix'
            target.write_bytes(prefix)
            mask = next(r for r in masks['masks'] if r['member'] == f'train_masks/mask{number}.png')
            rows.append({'number': number, 'member': member, 'T_shape': shape,
                         'mask_shape': mask['shape'][:2],
                         'spatial_shape_matches': shape[:2] == mask['shape'][:2],
                         'prefix_sha256': hashlib.sha256(prefix).hexdigest(),
                         'prefix_bytes': len(prefix), 'mask_sha256': mask['sha256'],
                         'class_counts': mask['counts']})
            save()
            print(f"{number}/41: T={shape}, mask={mask['shape'][:2]}", flush=True)


if __name__ == '__main__':
    main()
