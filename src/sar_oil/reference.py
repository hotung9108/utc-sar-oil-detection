"""Independent library references; Lee is a composed-formula reference, not an API."""

import numpy as np
from scipy import ndimage as ndi
from skimage.filters import threshold_niblack, threshold_otsu


def filter_image(a, name="none", size=3, sigma=0.8, looks=1):
    if name == "none":
        return a.copy()
    if name == "median":
        return ndi.median_filter(a, size=size, mode="mirror")
    if name == "gaussian":
        return ndi.gaussian_filter(a, sigma=sigma, radius=2, mode="mirror")
    if name == "lee":
        m = ndi.uniform_filter(a, size, mode="mirror")
        v = np.maximum(ndi.uniform_filter(a * a, size, mode="mirror") - m * m, 0)
        return m + np.maximum(v - m * m / looks, 0) / np.maximum(v, 1e-12) * (a - m)
    raise ValueError(name)


def threshold(a, name="otsu", size=31, k=0.5):
    if np.ptp(a) < 1e-12:
        return np.zeros(a.shape, bool)
    if name == "otsu":
        h, edges = np.histogram(a, bins=256, range=(0, 1))
        return a < threshold_otsu(hist=(h, (edges[:-1] + edges[1:]) / 2))
    return a < threshold_niblack(a, window_size=size, k=k)


def label(mask):
    return ndi.label(mask, structure=np.ones((3, 3)))[0]


def postprocess(mask, operation="none", min_area=16):
    footprint = np.array([[0, 1, 0], [1, 1, 1], [0, 1, 0]], bool)
    if operation == "open_close":
        mask = ndi.binary_opening(mask, structure=footprint, border_value=0)
    if operation in ("close", "open_close"):
        mask = ndi.binary_closing(mask, structure=footprint, border_value=0)
    labels = label(mask)
    areas = np.bincount(labels.ravel())
    keep = areas >= min_area
    keep[0] = False
    return keep[labels]


def features(a, labels):
    """Independent regionprops/ndimage reference using the same feature definitions."""
    from skimage.measure import regionprops

    gradient = np.hypot(
        ndi.sobel(a, axis=1, mode="mirror") / 8, ndi.sobel(a, axis=0, mode="mirror") / 8
    )
    cross = ndi.generate_binary_structure(2, 1)
    y, x = np.mgrid[-5:6, -5:6]
    disk = x * x + y * y <= 25
    output = []
    ids = []
    for r in regionprops(labels):
        y0, x0, y1, x1 = r.bbox
        y0, x0 = max(0, y0 - 5), max(0, x0 - 5)
        y1, x1 = min(a.shape[0], y1 + 5), min(a.shape[1], x1 + 5)
        local = labels[y0:y1, x0:x1]
        values = a[y0:y1, x0:x1]
        mask = local == r.label
        ring = ndi.binary_dilation(mask, structure=disk) & (local == 0)
        background = values[ring] if ring.any() else a[labels == 0]
        bg = background.mean() if len(background) else a.mean()
        boundary = mask & ~ndi.binary_erosion(mask, structure=cross, border_value=0)
        # Covariance eigenvalues equal the two inertia eigenvalues in 2D, reversed.
        eigen = sorted(r.inertia_tensor_eigvals)
        perimeter = np.count_nonzero(np.diff(np.pad(mask, 1), axis=0)) + np.count_nonzero(
            np.diff(np.pad(mask, 1), axis=1)
        )
        mu = values[mask].mean()
        output.append(
            [
                r.area / a.size,
                np.sqrt((eigen[1] + 1e-6) / (max(eigen[0], 0) + 1e-6)),
                r.extent,
                perimeter**2 / (4 * np.pi * r.area),
                mu,
                values[mask].std(),
                gradient[y0:y1, x0:x1][boundary].mean(),
                (bg - mu) / (abs(bg) + 1e-6),
            ]
        )
        ids.append(r.label)
    return np.asarray(output, float).reshape(-1, 8), ids
