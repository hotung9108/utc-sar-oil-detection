"""Extract reference-region features; this is not detection or test scoring."""

import sys as _sys
from pathlib import Path as _Path
_project_root = _Path(__file__).resolve().parents[2]
_sys.path.insert(0, str(_project_root))
_sys.path.insert(0, str(_project_root / "src"))

import argparse
import hashlib
import json
from pathlib import Path
import sys
import time

import numpy as np
from PIL import Image
from scipy.io import loadmat

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'src'))
from sar_oil import core, reference

from scripts._provenance import source_matches
from scripts._paths import resolve_path
from scripts.qposd.qposd_labels import decode_mask


def digest(path):
    return hashlib.sha256(resolve_path(path).read_bytes()).hexdigest()


def display_normalize(linear):
    """Protocol transform for model input (also used by candidate extraction)."""
    log = 10*np.log10(np.maximum(linear, 1e-12))
    low, high = np.percentile(log, [1, 99])
    if high - low < 1e-12:
        return np.zeros(log.shape), [float(low), float(high)]
    return np.clip((log-low)/(high-low), 0, 1), [float(low), float(high)]


def load_pair(number):
    shape_audit = json.loads((ROOT/'docs/management/qposd_shape_audit.json').read_text(encoding='utf-8'))
    mask_audit = json.loads((ROOT/'docs/management/qposd_mask_audit.json').read_text(encoding='utf-8'))
    row = next(p for p in shape_audit['pairs'] if p['number'] == number)
    if not row['spatial_shape_matches']:
        raise ValueError('Dimension-mismatched pair is ineligible')
    path = ROOT/f'data/lookalike_sources/qposd_features/image{number}.mat'
    raw = path.read_bytes()
    if hashlib.sha256(raw[:row['prefix_bytes']]).hexdigest() != row['prefix_sha256']:
        raise ValueError('MAT prefix mismatch')
    T = loadmat(path, variable_names=['T'])['T']
    if list(T.shape) != row['T_shape'] or not np.isfinite(T).all():
        raise ValueError('Unexpected MAT shape/nonfinite data')
    if np.any(T[:, :, 0] < 0):
        raise ValueError('Negative T11 violates the fixed linear-intensity protocol')
    maskrow = next(m for m in mask_audit['masks'] if m['member'] == f'train_masks/mask{number}.png')
    mask_path = ROOT/maskrow['local_path']
    if (not source_matches(mask_path, row['mask_sha256'], digest(mask_path))):
        raise ValueError('Mask hash mismatch')
    with Image.open(mask_path) as image:
        labels = decode_mask(np.asarray(image.convert('RGB')))
    return T[:, :, 0].copy(), labels, {
        'mat_sha256': hashlib.sha256(raw).hexdigest(),
        'mask_sha256': row['mask_sha256'], 'published_prefix_matches': True}


def extract(number, protocol_hash):
    raw, truth, source = load_pair(number)
    started = time.perf_counter()
    filtered = core.filter_image(raw, 'lee', size=7, looks=4)
    a, bounds = display_normalize(filtered)
    labels = np.zeros(truth.shape, dtype=np.int32)
    targets = [0]
    for value, target in ((1, 1), (2, 0)):
        part = core.label(truth == value)
        count = int(part.max())
        nonzero = part > 0
        labels[nonzero] = part[nonzero] + len(targets) - 1
        targets.extend([target]*count)
    X, ids = core.features(a, labels)
    numpy_seconds = time.perf_counter() - started
    started = time.perf_counter()
    ref_filtered = reference.filter_image(raw, 'lee', size=7, looks=4)
    ref_a, ref_bounds = display_normalize(ref_filtered)
    ref_X, ref_ids = reference.features(ref_a, labels)
    reference_seconds = time.perf_counter() - started
    if ids != ref_ids or not np.isfinite(X).all() or not np.isfinite(ref_X).all():
        raise ValueError('Feature row IDs or finite-value check failed')
    areas = np.bincount(labels.ravel())
    return {
        'number': number, 'protocol_sha256': protocol_hash, **source,
        'extraction_script_sha256': digest(Path(__file__)),
        'core_sha256': digest(ROOT/'src/sar_oil/core.py'),
        'reference_sha256': digest(ROOT/'src/sar_oil/reference.py'),
        'shape': list(raw.shape), 'normalization_log_bounds': bounds,
        'reference_normalization_log_bounds': ref_bounds,
        'feature_names': core.FEATURES,
        'rows': [{'object_id': i, 'label': targets[i], 'area': int(areas[i]),
                  'features': X[j].tolist(), 'reference_features': ref_X[j].tolist()}
                 for j, i in enumerate(ids)],
        'comparison': {
            'lee_linear_max_abs_error': float(np.max(np.abs(filtered-ref_filtered))),
            'normalized_max_abs_error': float(np.max(np.abs(a-ref_a))),
            'features_max_abs_error_by_column': np.max(np.abs(X-ref_X), axis=0).tolist() if len(X) else [0.]*8,
            'features_mse_by_column': np.mean((X-ref_X)**2, axis=0).tolist() if len(X) else [0.]*8,
            'numpy_seconds_single_run': numpy_seconds,
            'reference_seconds_single_run': reference_seconds},
        'scope': 'Reference-region features with GT geometry supplied; no classifier fit or detection scores. Full MAT audit and visual eligibility gates still required before fitting. Timings are single-run, with NumPy labeling included only in NumPy path; not a fair end-to-end speed comparison.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--numbers', type=int, nargs='+', required=True)
    args = parser.parse_args()
    path = ROOT/'results/qposd/protocol.json'
    protocol = json.loads(path.read_text(encoding='utf-8'))
    # Keep test imagery out of this development command until a frozen model
    # and candidate choice exist. Test extraction will be an evaluation step.
    allowed = protocol['splits']['train'] + protocol['splits']['validation']
    if any(n not in allowed for n in args.numbers):
        parser.error('Only train/validation feature extraction is permitted here')
    output = ROOT/'results/qposd/regions'
    output.mkdir(parents=True, exist_ok=True)
    for number in args.numbers:
        target = output/f'image{number}.json'
        if target.exists():
            raise SystemExit(f'Refuse to overwrite existing evidence: {target}')
        result = extract(number, digest(path))
        temporary = target.with_suffix('.tmp')
        temporary.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
        temporary.replace(target)
        print(json.dumps({'number': number, 'objects': len(result['rows']),
                          'comparison': result['comparison']}), flush=True)


if __name__ == '__main__':
    main()
