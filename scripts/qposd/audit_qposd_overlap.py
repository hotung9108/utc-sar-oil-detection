"""Screen sampled exact T11 patches for translated overlap across source files.

Negative results do not establish independent scenes: resampling, radiometric
changes, rotations and unsampled overlaps are outside this exact-match screen.
"""

import sys as _sys
from pathlib import Path as _Path
_project_root = _Path(__file__).resolve().parents[2]
_sys.path.insert(0, str(_project_root))
_sys.path.insert(0, str(_project_root / "src"))

import argparse
from collections import Counter
import json
from pathlib import Path

import numpy as np

from scripts.qposd.extract_qposd_regions import ROOT, digest, load_pair


def exact_anchors(source, target, stride=64, size=5):
    if stride < 1 or size < 2:
        raise ValueError('Invalid sampling parameters')
    flat = target.ravel()
    order = np.argsort(flat)
    sorted_values = flat[order]
    offsets = Counter()
    tested = 0
    truncated = 0
    for y in range(0, source.shape[0]-size+1, stride):
        for x in range(0, source.shape[1]-size+1, stride):
            patch = source[y:y+size, x:x+size]
            if np.ptp(patch) == 0:
                continue
            tested += 1
            left, right = np.searchsorted(sorted_values, patch[0, 0], side='left'), np.searchsorted(sorted_values, patch[0, 0], side='right')
            # Repeated scalar values can make a flat-image scan quadratic.
            # Record truncation explicitly; this screen is not exhaustive.
            if right-left > 64:
                truncated += 1
                right = left+64
            for pos in order[left:right]:
                ty, tx = divmod(int(pos), target.shape[1])
                if ty+size <= target.shape[0] and tx+size <= target.shape[1] and np.array_equal(patch, target[ty:ty+size, tx:tx+size]):
                    offsets[(ty-y, tx-x)] += 1
    checked = []
    for (dy, dx), count in offsets.most_common():
        sy0, sx0 = max(0, -dy), max(0, -dx)
        sy1, sx1 = min(source.shape[0], target.shape[0]-dy), min(source.shape[1], target.shape[1]-dx)
        a = source[sy0:sy1, sx0:sx1]
        b = target[sy0+dy:sy1+dy, sx0+dx:sx1+dx]
        equal = int(np.count_nonzero(a == b))
        checked.append({'target_minus_source_offset_yx': [dy, dx],
                        'exact_anchor_patches': count,
                        'overlap_shape': list(a.shape), 'overlap_pixels': int(a.size),
                        'equal_pixels': equal, 'equal_fraction': equal/a.size,
                        'entire_overlap_exact': bool(np.array_equal(a, b))})
    return {'sampled_nonconstant_patches': tested, 'scalar_searches_truncated': truncated,
            'translations': checked}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--numbers', type=int, nargs='+', required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if len(set(args.numbers)) != len(args.numbers):
        parser.error('Duplicate source IDs')
    if args.output.exists():
        parser.error('Refuse to overwrite prior overlap evidence')
    protocol = json.loads((ROOT/'results/qposd/protocol.json').read_text(encoding='utf-8'))
    split = {n: k for k, ids in protocol['splits'].items() for n in ids}
    arrays, provenance = {}, {}
    for number in args.numbers:
        arrays[number], _, provenance[number] = load_pair(number)
    pairs = []
    for index, first in enumerate(args.numbers):
        for second in args.numbers[index+1:]:
            result = exact_anchors(arrays[first], arrays[second])
            result.update({'first': first, 'second': second,
                           'splits': [split[first], split[second]],
                           'cross_split': split[first] != split[second]})
            pairs.append(result)
            print(f"{first}/{second}: {len(result['translations'])} exact-patch translations", flush=True)
    audit = {'script_sha256': digest(Path(__file__)), 'selection': args.numbers,
             'protocol_sha256': digest(ROOT/'results/qposd/protocol.json'),
             'stride': 64, 'patch_size': 5, 'inputs': provenance, 'pairs': pairs,
             'scope': 'Exact, unrotated, untranslated-value T11 patch screen with translated overlap verification. No model predictions. Missing matches do not establish independent scenes; non-exact/resampled/unsampled overlap may be missed.'}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(audit, indent=2)+'\n', encoding='utf-8')


if __name__ == '__main__':
    main()
