"""Image-only registration diagnostics; never reads labels or selects a classifier."""

import sys as _sys
from pathlib import Path as _Path
_project_root = _Path(__file__).resolve().parents[2]
_sys.path.insert(0, str(_project_root))
_sys.path.insert(0, str(_project_root / "src"))

import hashlib
import json
from pathlib import Path

import numpy as np
import tifffile
from scipy.ndimage import shift as shift_image
from skimage.registration import phase_cross_correlation


from scripts._provenance import source_matches
from scripts._paths import resolve_path
from scripts.cantarell.audit_cantarell_source import ROOT, REVISION


def sha(path):
    return hashlib.sha256(resolve_path(path).read_bytes()).hexdigest()


def prepare(image):
    if not np.all(np.isfinite(image)):
        raise ValueError('Nonfinite registration image')
    window = np.outer(np.hanning(image.shape[0]), np.hanning(image.shape[1]))
    return (image-image.mean())*window


def integer_phase_numpy(reference, moving):
    spectrum = np.fft.fftn(reference)*np.fft.fftn(moving).conj()
    spectrum /= np.maximum(np.abs(spectrum), 100*np.finfo(float).eps)
    peak = np.array(np.unravel_index(np.argmax(np.abs(np.fft.ifftn(spectrum))), reference.shape), dtype=float)
    shape = np.array(reference.shape)
    peak[peak > np.trunc(shape/2)] -= shape[peak > np.trunc(shape/2)]
    return peak


def stats(reference, moving):
    valid = np.isfinite(reference) & np.isfinite(moving)
    a, b = reference[valid], moving[valid]
    return {'pixels': int(valid.sum()), 'pearson_correlation': float(np.corrcoef(a, b)[0, 1]),
            'rmse_under_db_assumption': float(np.sqrt(np.mean((a-b)**2))),
            'median_moving_minus_reference': float(np.median(b-a))}


def register(reference, moving):
    a, b = prepare(reference), prepare(moving)
    ours = integer_phase_numpy(a, b)
    theirs = phase_cross_correlation(a, b, upsample_factor=1, normalization='phase')[0]
    if not np.array_equal(ours, theirs):
        raise ValueError('Integer phase-correlation mismatch')
    fine = phase_cross_correlation(a, b, upsample_factor=100, normalization='phase')[0]
    moved = shift_image(moving, fine, order=1, mode='constant', cval=np.nan, prefilter=False)
    interior = (slice(8, -8), slice(8, -8))
    return {'numpy_integer_shift': ours.tolist(), 'skimage_integer_shift': theirs.tolist(),
            'skimage_subpixel_shift': fine.tolist(),
            'before_on_interior': stats(reference[interior], moving[interior]),
            'after_on_interior': stats(reference[interior], moved[interior])}


def main():
    cache = ROOT / '.cache/cantarell_source' / REVISION
    native_path = ROOT / 'docs/management/cantarell_native_audit.json'
    native = json.loads(native_path.read_text())
    sampled_path = cache / 'native_vv_sampled.npz'
    if (not source_matches(sampled_path, native['sampled_sha256'], sha(sampled_path))):
        raise ValueError('Native sampled image hash mismatch')
    source = json.loads((ROOT / 'docs/management/cantarell_source_audit.json').read_text())
    image_path = 'RASTER/IMG-TIFF/16-BIT/IMG_01_TILE_001.tiff'
    exported_path = cache / (image_path + '.lfs-object')
    receipt = next(r for r in source['receipts'] if r['path'] == image_path and r.get('verified_against_lfs_pointer'))
    if (not source_matches(exported_path, receipt['sha256'], sha(exported_path))):
        raise ValueError('Exported image hash mismatch')
    exported = tifffile.imread(exported_path).astype(float)
    with np.load(sampled_path) as data:
        moving = data['sigma0_db']
    global_result = register(exported, moving)
    local = []
    row_edges = np.linspace(0, exported.shape[0], 4, dtype=int)
    col_edges = np.linspace(0, exported.shape[1], 4, dtype=int)
    for r in range(3):
        for c in range(3):
            crop = (slice(row_edges[r], row_edges[r+1]), slice(col_edges[c], col_edges[c+1]))
            local.append({'grid_row_col': [r, c], **register(exported[crop], moving[crop])})
    # Check sign convention on a known cyclic translation before interpreting shifts.
    synthetic = np.random.default_rng(2026).normal(size=(64, 80))
    recovered = integer_phase_numpy(synthetic, np.roll(synthetic, (5, -7), axis=(0, 1)))
    if not np.array_equal(recovered, [-5, 7]):
        raise ValueError('Known translation check failed')
    result = {'sample': 'IMG_01_TILE_001', 'native_audit_sha256': sha(native_path),
              'script_sha256': sha(Path(__file__)), 'mask_read': False,
              'method': 'Mean subtraction + Hann window; phase-only FFT correlation; all nine fixed disjoint blocks reported.',
              'shift_convention': 'Row/column shift applied to native resampled image to align with publisher export.',
              'global': global_result, 'local_3x3': local,
              'known_translation_check': recovered.tolist(),
              'limits': ['One development sample; no source-scene generalization.',
                         'Subpixel solution is from skimage; only integer peak is independently implemented in NumPy.',
                         'Shift estimation and residual statistics use the same image; descriptive, not held-out validation.',
                         'Image correlation does not verify absolute geolocation, annotation correctness, physical units or polarization.',
                         'No image, label or frozen model is modified. No detection or calibration-benefit claim.']}
    (ROOT / 'docs/management/cantarell_registration_audit.json').write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({'global': global_result, 'local_shifts': [r['skimage_subpixel_shift'] for r in local]}, indent=2))


if __name__ == '__main__':
    main()
