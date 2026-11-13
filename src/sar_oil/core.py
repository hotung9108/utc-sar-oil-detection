"""Image algorithms implemented with NumPy only; reflect padding excludes edge pixel."""

import numpy as np
from numpy.lib.stride_tricks import sliding_window_view


def mean_filter(a, size):
    """O(HW) box mean using a summed-area table."""
    p = np.pad(np.asarray(a, dtype=float), size // 2, mode="reflect")
    s = np.pad(p, ((1, 0), (1, 0))).cumsum(0).cumsum(1)
    return (s[size:, size:] - s[:-size, size:] - s[size:, :-size] + s[:-size, :-size]) / size**2


def correlate(a, kernel):
    """2D correlation, preserving floating point gradients."""
    p = np.pad(a, [(n // 2, n // 2) for n in kernel.shape], mode="reflect")
    return np.einsum("ijkl,kl->ij", sliding_window_view(p, kernel.shape), kernel)


def filter_image(a, name="none", size=3, sigma=0.8, looks=1):
    a = np.asarray(a, dtype=float)
    if name == "none":
        return a.copy()
    if name == "median":
        return np.median(
            sliding_window_view(np.pad(a, size // 2, mode="reflect"), (size, size)), axis=(-2, -1)
        )
    if name == "gaussian":
        x = np.arange(-2, 3)
        g = np.exp(-x * x / (2 * sigma * sigma))
        g /= g.sum()
        return correlate(correlate(a, g[None, :]), g[:, None])
    if name == "lee":
        m = mean_filter(a, size)
        v = np.maximum(mean_filter(a * a, size) - m * m, 0)
        noise = m * m / looks
        weight = np.maximum(v - noise, 0) / np.maximum(v, 1e-12)
        return m + weight * (a - m)
    raise ValueError(name)


def otsu(a):
    """256 fixed bins on [0,1], first maximizing split; returns bin center."""
    h, edges = np.histogram(a, bins=256, range=(0, 1))
    centers = (edges[:-1] + edges[1:]) / 2
    w = h.cumsum().astype(float)
    m = (h * centers).cumsum()
    valid = (w > 0) & (w < w[-1])
    score = np.full(256, -np.inf)
    score[valid] = (m[-1] * w[valid] - m[valid] * w[-1]) ** 2 / (w[valid] * (w[-1] - w[valid]))
    return float(centers[np.argmax(score)])


def threshold(a, name="otsu", size=31, k=0.5):
    if np.ptp(a) < 1e-12:
        return np.zeros(a.shape, dtype=bool)
    if name == "otsu":
        return a < otsu(a)
    if name == "niblack":
        m = mean_filter(a, size)
        std = np.sqrt(np.maximum(mean_filter(a * a, size) - m * m, 0))
        return a < m - k * std
    raise ValueError(name)


def morph(mask, operation, radius=1):
    """Binary morphology with an explicit false exterior, including erosion."""
    y, x = np.mgrid[-radius : radius + 1, -radius : radius + 1]
    footprint = x * x + y * y <= radius * radius
    windows = sliding_window_view(np.pad(mask.astype(bool), radius), footprint.shape)[
        ..., footprint
    ]
    return windows.any(-1) if operation == "dilate" else windows.all(-1)


def label(mask):
    """8-connected run-length union-find, adapted and reverified from legacy."""
    parent = [0]
    out = np.zeros(mask.shape, np.int32)
    previous = []

    def root(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    for y, row in enumerate(mask):
        changes = np.diff(np.pad(row.astype(np.int8), (1, 1)))
        starts, ends = np.flatnonzero(changes == 1), np.flatnonzero(changes == -1) - 1
        current = []
        j = 0
        for left, right in zip(starts, ends):
            ident = len(parent)
            parent.append(ident)
            while j < len(previous) and previous[j][1] < left - 1:
                j += 1
            k = j
            while k < len(previous) and previous[k][0] <= right + 1:
                a, b = root(ident), root(previous[k][2])
                parent[max(a, b)] = min(a, b)
                k += 1
            out[y, left : right + 1] = ident
            current.append((left, right, ident))
        previous = current
    roots = np.array([root(i) for i in range(len(parent))])
    unique = np.unique(roots[1:])
    mapping = np.zeros(len(parent), np.int32)
    mapping[unique] = np.arange(1, len(unique) + 1)
    return mapping[roots[out]]


def postprocess(mask, operation="none", min_area=16):
    if operation == "open_close":
        mask = morph(morph(mask, "erode"), "dilate")
    if operation in ("close", "open_close"):
        mask = morph(morph(mask, "dilate"), "erode")
    labels = label(mask)
    area = np.bincount(labels.ravel())
    keep = area >= min_area
    keep[0] = False
    return keep[labels]


FEATURES = [
    "area_fraction",
    "elongation",
    "extent",
    "complexity",
    "mean",
    "std",
    "boundary_gradient",
    "background_contrast",
]


def features(a, labels):
    """Eight interpretable region features; grid-edge perimeter is explicitly defined."""
    sx = np.array([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]], dtype=float) / 8
    gradient = np.hypot(correlate(a, sx), correlate(a, sx.T))
    result = []
    ids = []
    for ident in np.unique(labels):
        if ident == 0:
            continue
        y, x = np.nonzero(labels == ident)
        area = len(x)
        y0, y1 = max(0, y.min() - 5), min(a.shape[0], y.max() + 6)
        x0, x1 = max(0, x.min() - 5), min(a.shape[1], x.max() + 6)
        local_labels = labels[y0:y1, x0:x1]
        local_a = a[y0:y1, x0:x1]
        region = local_labels == ident
        centered = np.stack([x - x.mean(), y - y.mean()])
        eigen = np.linalg.eigvalsh(centered @ centered.T / area)
        elongation = np.sqrt((eigen[1] + 1e-6) / (eigen[0] + 1e-6))
        padded = np.pad(region.astype(np.int8), 1)
        perimeter = np.abs(np.diff(padded, axis=0)).sum() + np.abs(np.diff(padded, axis=1)).sum()
        boundary = region & ~morph(region, "erode")
        ring = morph(region, "dilate", 5) & (local_labels == 0)
        background = local_a[ring] if ring.any() else a[labels == 0]
        bg = background.mean() if len(background) else a.mean()
        result.append(
            [
                area / a.size,
                elongation,
                area / ((x.max() - x.min() + 1) * (y.max() - y.min() + 1)),
                perimeter**2 / (4 * np.pi * area),
                local_a[region].mean(),
                local_a[region].std(),
                gradient[y0:y1, x0:x1][boundary].mean(),
                (bg - local_a[region].mean()) / (abs(bg) + 1e-6),
            ]
        )
        ids.append(int(ident))
    return np.asarray(result, dtype=float).reshape(-1, 8), ids
