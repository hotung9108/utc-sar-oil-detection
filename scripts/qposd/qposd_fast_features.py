"""Same eight NumPy features, grouping coordinates once for large SAR rasters.

The frozen SOS implementation is left intact. Equivalence must be measured
before using this helper in QPOSD inference; this module does not select models.
"""

import sys as _sys
from pathlib import Path as _Path
_project_root = _Path(__file__).resolve().parents[2]
_sys.path.insert(0, str(_project_root))
_sys.path.insert(0, str(_project_root / "src"))

import numpy as np
from sar_oil.core import correlate, morph


def features(a, labels):
    a, labels = np.asarray(a), np.asarray(labels)
    if a.shape != labels.shape or a.ndim != 2 or np.any(labels < 0):
        raise ValueError('Expected aligned 2D image and nonnegative labels')
    sx = np.array([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]], dtype=float)/8
    gradient = np.hypot(correlate(a, sx), correlate(a, sx.T))
    flat = np.flatnonzero(labels)
    if not len(flat):
        return np.empty((0, 8)), []
    values = labels.ravel()[flat]
    order = np.argsort(values, kind='stable')
    flat, values = flat[order], values[order]
    boundaries = np.r_[0, np.flatnonzero(np.diff(values))+1, len(values)]
    background = a[labels == 0]
    fallback = background.mean() if len(background) else a.mean()
    result, ids = [], []
    for start, stop in zip(boundaries[:-1], boundaries[1:]):
        ident = int(values[start])
        y, x = np.divmod(flat[start:stop], a.shape[1])
        area = len(x)
        y0, y1 = max(0, y.min()-5), min(a.shape[0], y.max()+6)
        x0, x1 = max(0, x.min()-5), min(a.shape[1], x.max()+6)
        local_labels = labels[y0:y1, x0:x1]
        local_a = a[y0:y1, x0:x1]
        region = local_labels == ident
        centered = np.stack([x-x.mean(), y-y.mean()])
        eigen = np.linalg.eigvalsh(centered @ centered.T / area)
        elongation = np.sqrt((eigen[1]+1e-6)/(eigen[0]+1e-6))
        padded = np.pad(region.astype(np.int8), 1)
        perimeter = np.abs(np.diff(padded, axis=0)).sum()+np.abs(np.diff(padded, axis=1)).sum()
        boundary = region & ~morph(region, 'erode')
        ring = morph(region, 'dilate', 5) & (local_labels == 0)
        bg = local_a[ring].mean() if ring.any() else fallback
        result.append([
            area/a.size, elongation,
            area/((x.max()-x.min()+1)*(y.max()-y.min()+1)),
            perimeter**2/(4*np.pi*area), local_a[region].mean(), local_a[region].std(),
            gradient[y0:y1, x0:x1][boundary].mean(),
            (bg-local_a[region].mean())/(abs(bg)+1e-6)])
        ids.append(ident)
    return np.asarray(result, dtype=float).reshape(-1, 8), ids
