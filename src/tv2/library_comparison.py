"""TV2: measured library comparisons, including explicitly labelled compositions.

OpenCV/SciPy are reference implementations here, never production algorithms.
Comparing an algorithm with a library composition validates its computation, not
the physical interpretation of SAR pixels. Variant comparisons are descriptive.
"""

import json
import platform
import time
from pathlib import Path

import cv2
import numpy as np
import pandas as pd
import scipy
from scipy import fft, stats
from scipy import ndimage as ndi

from src import edges as b
from src import enhancement as e
from src import filters as f
from src import metrics as q
from src import morphology as m
from src import sharpening as s


def u8(a):
    """Round a numeric array, clip to [0,255], and return uint8; shared output convention in Section 3.7."""
    return np.clip(np.rint(a), 0, 255).astype(np.uint8)


def local_stats(a):
    """Return float image, 5x5 mean and variance via SciPy mirror padding; moments for Eq. 2.4."""
    a = a.astype(float)
    mean = ndi.uniform_filter(a, 5, mode="mirror")
    var = np.maximum(ndi.uniform_filter(a * a, 5, mode="mirror") - mean * mean, 0)
    return a, mean, var


def lee_reference(a):
    """Map grayscale a to uint8 Lee output using SciPy moments, L=4; Eq. 2.4."""
    a, mean, var = local_stats(a)
    return u8(mean + np.clip(1 - mean * mean / 4 / np.maximum(var, 1e-8), 0, 1) * (a - mean))


def kuan_reference(a):
    """Map grayscale a to uint8 Kuan output using SciPy moments and L=4; Section 2.2."""
    a, mean, var = local_stats(a)
    ci = var / np.maximum(mean * mean, 1e-8)
    return u8(mean + np.clip((1 - 0.25 / np.maximum(ci, 1e-8)) / 1.25, 0, 1) * (a - mean))


def frost_reference(a):
    """Return the documented Frost variant with SciPy shifts, 5x5 window and damping 2; Section 2.2."""
    a, mean, var = local_stats(a)
    damp = 2 * np.sqrt(var) / np.maximum(mean, 1e-6)
    numerator, denominator = np.zeros_like(a), np.zeros_like(a)
    for dy in range(-2, 3):
        for dx in range(-2, 3):
            weight = np.exp(-damp * np.hypot(dy, dx))
            numerator += weight * ndi.shift(a, (-dy, -dx), order=0, mode="mirror")
            denominator += weight
    return u8(numerator / denominator)


def homo_reference(a):
    """Return uint8 normalized homomorphic output using scipy.fft and the gain in Eq. 2.5."""
    yy, xx = np.ogrid[: a.shape[0], : a.shape[1]]
    gain = 0.5 + 1 * (
        1 - np.exp(-((yy - a.shape[0] // 2) ** 2 + (xx - a.shape[1] // 2) ** 2) / 30**2)
    )
    z = np.expm1(
        fft.ifft2(fft.ifftshift(fft.fftshift(fft.fft2(np.log1p(a.astype(float)))) * gain))
    ).real
    return u8((z - z.min()) / np.ptp(z) * 255) if np.ptp(z) > 1e-8 else np.zeros_like(a)


def log_reference(a):
    """Return the log-transformed grayscale array through cv2.LUT; Eq. 2.1."""
    x = np.log1p(np.arange(256, dtype=float))
    lut = u8(x * 255 / np.log1p(max(float(a.max()), 1)))
    return cv2.LUT(a, lut)


def gaussian_reference(a):
    """Return rounded OpenCV Gaussian output, 5x5 sigma=1, reflect101; Section 3.2."""
    return u8(cv2.GaussianBlur(a.astype(float), (5, 5), 1, borderType=cv2.BORDER_REFLECT_101))


def log_edges_reference(a):
    """Return a 0/255 LoG zero-crossing map using SciPy correlation and shifts; Section 2.4."""
    sigma = 1.4
    radius = int(np.ceil(3 * sigma))
    y, x = np.mgrid[-radius : radius + 1, -radius : radius + 1]
    kernel = (
        -(x * x + y * y - 2 * sigma * sigma)
        / sigma**4
        * np.exp(-(x * x + y * y) / (2 * sigma * sigma))
    )
    kernel -= kernel.mean()
    response = ndi.correlate(a.astype(float), kernel, mode="mirror")
    response[np.abs(response) < 1e-9] = 0.0
    result = np.zeros(a.shape, bool)
    for dy, dx in [(1, 0), (0, 1), (1, 1), (1, -1)]:
        p = ndi.shift(response, (dy, dx), order=0, mode="mirror")
        n = ndi.shift(response, (-dy, -dx), order=0, mode="mirror")
        result |= (p * n < 0) & (np.abs(p - n) > 4)
    return result.astype(np.uint8) * 255


def components_reference(a):
    # Return area per foreground pixel so IDs/scan order do not affect comparison.
    """Return foreground component area at each pixel via OpenCV 8-connectivity; Section 3.6."""
    _, labels = cv2.connectedComponents((a > 0).astype(np.uint8), connectivity=8)
    areas = np.bincount(labels.ravel())
    areas[0] = 0
    return areas[labels]


def components_custom(a):
    """Return area per foreground pixel from NumPy labels, independent of label ID order; Section 3.6."""
    _, labels, _ = m.find_connected_components(a, min_area=a.size + 1)
    areas = np.bincount(labels.ravel())
    areas[0] = 0
    return areas[labels]


def epi_reference(a, z):
    """Return sum-absolute SciPy Laplacian ratio for images a and z; metric in Section 2.6."""
    denominator = np.abs(ndi.laplace(a.astype(float), mode="reflect")).sum()
    return (
        np.abs(ndi.laplace(z.astype(float), mode="reflect")).sum() / denominator
        if denominator >= 1e-8
        else 1.0
    )


def enl_reference(a):
    """Return mean squared / variance for the fixed ROI via cv2.meanStdDev; Section 2.6."""
    roi = a[20 : min(a.shape[0], 80), 20 : min(a.shape[1], 80)] if min(a.shape) > 20 else a
    mu, sd = cv2.meanStdDev(roi)
    return float(mu[0, 0] ** 2 / sd[0, 0] ** 2) if sd[0, 0] ** 2 >= 1e-8 else 999.0


def ssi_reference(a, z):
    """Return the ratio of scipy.stats variation for images z and a; Section 2.6."""
    if a.mean() < 1e-6 or a.std() < 1e-6 or z.mean() < 1e-6:
        return 1.0
    return float(stats.variation(z, axis=None) / stats.variation(a, axis=None))


def registry():
    """name, custom, reference, reference description, kind, max-error limit.

    None means descriptive comparison of different discretizations, not a pass.
    No direct standard Lee/Frost/Kuan/homomorphic API is assumed to exist.
    """
    k = m.disk_kernel(2)
    lap = np.array([[0, 1, 0], [1, -4, 1], [0, 1, 0]], float)
    pre = np.array([[-1, 0, 1]] * 3, float)

    def sob(a):
        """Return the float OpenCV x/y derivatives of image a (Eq. 2.7)."""
        return cv2.Sobel(a, cv2.CV_64F, 1, 0), cv2.Sobel(a, cv2.CV_64F, 0, 1)

    def grad(a):
        """Return the L2 norm of the reference Sobel derivatives (Eq. 2.7)."""
        return np.hypot(*sob(a))

    def binary(a):
        """Convert grayscale a to the shared 0/255 fixture at threshold 127."""
        return (a > 127).astype(np.uint8) * 255

    def erode(a):
        """Return reference erosion with the same neutral exterior (Section 3.6)."""
        return cv2.erode(binary(a), k, borderType=cv2.BORDER_CONSTANT, borderValue=255)

    def dilate(a):
        """Return reference dilation with zero exterior (Section 3.6)."""
        return cv2.dilate(binary(a), k, borderType=cv2.BORDER_CONSTANT, borderValue=0)

    return [
        (
            "box",
            f.custom_box_filter,
            lambda a: u8(ndi.uniform_filter(a.astype(float), 5, mode="mirror")),
            "scipy.ndimage.uniform_filter; mirror",
            "direct",
            0,
        ),
        (
            "gaussian",
            f.custom_gaussian_filter,
            gaussian_reference,
            "cv2.GaussianBlur float64; reflect101",
            "direct",
            1,
        ),
        (
            "median",
            f.custom_median_filter,
            lambda a: ndi.median_filter(a, size=5, mode="mirror"),
            "scipy.ndimage.median_filter; mirror",
            "direct",
            0,
        ),
        (
            "bilateral",
            f.custom_bilateral_filter,
            lambda a: cv2.bilateralFilter(a, 5, 25, 3, borderType=cv2.BORDER_REFLECT_101),
            "cv2.bilateralFilter; disk footprint vs custom square",
            "variant",
            None,
        ),
        (
            "lee",
            f.custom_lee_filter,
            lee_reference,
            "SciPy uniform moments + stated Lee formula (no direct API)",
            "composition",
            1,
        ),
        (
            "frost",
            f.custom_frost_filter,
            frost_reference,
            "SciPy moments/shift + stated exponential CV weights (variant of Frost)",
            "composition",
            1,
        ),
        (
            "kuan",
            f.custom_kuan_filter,
            kuan_reference,
            "SciPy uniform moments + Kuan weights (no direct API)",
            "composition",
            1,
        ),
        (
            "log",
            e.log_transform,
            log_reference,
            "cv2.LUT with analytic log mapping",
            "composition",
            0,
        ),
        (
            "HE",
            lambda a: e.global_histogram_equalization(a)[0],
            cv2.equalizeHist,
            "cv2.equalizeHist; CDF-min; constant unchanged",
            "direct",
            1,
        ),
        (
            "CLAHE",
            e.custom_clahe,
            lambda a: cv2.createCLAHE(2, (8, 8)).apply(a),
            "cv2.createCLAHE; integer clipping, reflect101, interpolation",
            "direct",
            1,
        ),
        (
            "homomorphic",
            e.homomorphic_filter,
            homo_reference,
            "scipy.fft + same Gaussian frequency gain",
            "composition",
            1,
        ),
        (
            "unsharp",
            s.unsharp_masking,
            lambda a: u8(a.astype(float) * 2 - gaussian_reference(a)),
            "cv2.GaussianBlur + unsharp formula k=1",
            "composition",
            1,
        ),
        (
            "high_boost",
            lambda a: s.unsharp_masking(a, k=2),
            lambda a: u8(a.astype(float) * 3 - 2 * gaussian_reference(a).astype(float)),
            "cv2.GaussianBlur + high-boost formula k=2",
            "composition",
            2,
        ),
        (
            "laplacian_sharpen",
            s.laplacian_sharpening,
            lambda a: u8(a - 0.5 * cv2.filter2D(a.astype(float), -1, lap)),
            "cv2.filter2D Laplacian + sharpening formula",
            "composition",
            0,
        ),
        (
            "sobel_enhance",
            lambda a: s.sobel_edge_enhancement(a)[1],
            lambda a: np.clip(a + 0.5 * grad(a), 0, 255).astype(np.uint8),
            "cv2.Sobel + additive gradient enhancement",
            "composition",
            1,
        ),
        (
            "roberts",
            b.custom_roberts,
            lambda a: u8(
                np.hypot(
                    cv2.filter2D(a.astype(float), -1, np.array([[1, 0], [0, -1]]), anchor=(0, 0)),
                    cv2.filter2D(a.astype(float), -1, np.array([[0, 1], [-1, 0]]), anchor=(0, 0)),
                )
            ),
            "cv2.filter2D; explicit Roberts kernels and anchor",
            "composition",
            0,
        ),
        (
            "prewitt",
            lambda a: np.stack(b.custom_prewitt(a)[:2]),
            lambda a: np.stack(
                [cv2.filter2D(a.astype(float), -1, pre), cv2.filter2D(a.astype(float), -1, pre.T)]
            ),
            "cv2.filter2D; explicit Prewitt kernels",
            "composition",
            0,
        ),
        (
            "sobel",
            lambda a: np.stack(b.custom_sobel(a)[:2]),
            lambda a: np.stack(sob(a)),
            "cv2.Sobel; gradients before uint8 clipping",
            "direct",
            0,
        ),
        (
            "LoG",
            b.custom_log,
            log_edges_reference,
            "scipy.ndimage.correlate/shift; sampled zero-mean LoG sigma=1.4, crossing threshold 4",
            "composition",
            0,
        ),
        (
            "canny",
            lambda a: b.custom_canny(a, 35, 90),
            lambda a: cv2.Canny(f.custom_gaussian_filter(a, 5, 1.2), 35, 90, L2gradient=True),
            "cv2.Canny on same smoothing; NMS sectors/ties/borders differ",
            "variant",
            None,
        ),
        (
            "otsu",
            lambda a: m.custom_otsu_threshold(a)[0],
            lambda a: cv2.threshold(a, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[0],
            "cv2.threshold Otsu; first maximizing threshold",
            "direct",
            0,
        ),
        (
            "erosion",
            lambda a: m.custom_erosion(binary(a), k),
            erode,
            "cv2.erode; constant 255 border",
            "direct",
            0,
        ),
        (
            "dilation",
            lambda a: m.custom_dilation(binary(a), k),
            dilate,
            "cv2.dilate; constant 0 border",
            "direct",
            0,
        ),
        (
            "opening",
            lambda a: m.custom_opening(binary(a), k),
            lambda a: cv2.dilate(erode(a), k, borderType=cv2.BORDER_CONSTANT, borderValue=0),
            "cv2.erode + dilate with explicit borders",
            "composition",
            0,
        ),
        (
            "closing",
            lambda a: m.custom_closing(binary(a), k),
            lambda a: cv2.erode(dilate(a), k, borderType=cv2.BORDER_CONSTANT, borderValue=255),
            "cv2.dilate + erode with explicit borders",
            "composition",
            0,
        ),
        (
            "boundary",
            lambda a: m.custom_morphological_boundary(binary(a)),
            lambda a: (
                binary(a)
                - cv2.erode(
                    binary(a),
                    np.ones((3, 3), np.uint8),
                    borderType=cv2.BORDER_CONSTANT,
                    borderValue=0,
                )
            ),
            "cv2.erode + set difference; includes hole boundaries",
            "composition",
            0,
        ),
        (
            "components",
            lambda a: components_custom(binary(a)),
            lambda a: components_reference(binary(a)),
            "cv2.connectedComponents; compare component area per pixel",
            "direct",
            0,
        ),
        (
            "ENL",
            q.calculate_enl,
            enl_reference,
            "cv2.meanStdDev on same fixed ROI; 999 sentinel on zero variance",
            "composition",
            1e-5,
        ),
        (
            "SSI",
            lambda a: q.calculate_ssi(a, f.custom_lee_filter(a)),
            lambda a: ssi_reference(a, f.custom_lee_filter(a)),
            "scipy.stats.variation; same filtered input",
            "composition",
            1e-8,
        ),
        (
            "RMS",
            q.calculate_rms_contrast,
            lambda a: float(cv2.meanStdDev(a)[1][0, 0]),
            "cv2.meanStdDev",
            "direct",
            1e-8,
        ),
        (
            "entropy",
            q.calculate_entropy,
            lambda a: stats.entropy(cv2.calcHist([a], [0], None, [256], [0, 256]).ravel(), base=2),
            "cv2.calcHist + scipy.stats.entropy",
            "composition",
            1e-6,
        ),
        (
            "AMBE",
            lambda a: q.calculate_ambe(a, f.custom_lee_filter(a)),
            lambda a: abs(cv2.mean(a)[0] - cv2.mean(f.custom_lee_filter(a))[0]),
            "cv2.mean; same filtered input",
            "composition",
            1e-8,
        ),
        (
            "EPI",
            lambda a: q.calculate_epi(a, f.custom_lee_filter(a)),
            lambda a: epi_reference(a, f.custom_lee_filter(a)),
            "scipy.ndimage.laplace; reflect; same filtered input",
            "composition",
            1e-8,
        ),
    ]


def cases():
    """Yield named synthetic and project-sample grayscale inputs for the 18-case verification suite."""
    rng = np.random.default_rng(2026)
    grid = np.indices((64, 64))
    fixtures = {
        "black": np.zeros((64, 64), np.uint8),
        "constant": np.full((64, 64), 127, np.uint8),
        "white": np.full((64, 64), 255, np.uint8),
        "ramp": np.tile(np.arange(64, dtype=np.uint8) * 4, (64, 1)),
        "checker": ((grid.sum(0) % 2) * 255).astype(np.uint8),
        "diagonal": ((grid[0] > grid[1]) * 255).astype(np.uint8),
        "noise": rng.integers(0, 256, (63, 67), dtype=np.uint8),
        "impulse": np.pad(np.array([[255]], np.uint8), ((31, 32), (31, 32))),
    }
    for name, a in fixtures.items():
        yield "synthetic/" + name, a
    for p in sorted(Path("data/sample").rglob("*.jpg")):
        yield p.as_posix(), cv2.imread(str(p), cv2.IMREAD_GRAYSCALE)


def run_comparisons(output="results/verification"):
    """Export every measured case, aggregate errors, and environment metadata."""
    out = Path(output)
    out.mkdir(parents=True, exist_ok=True)
    records = []
    for case, a in cases():
        for name, custom, reference, desc, kind, limit in registry():
            start = time.perf_counter()
            x = np.asarray(custom(a), dtype=float)
            custom_ms = (time.perf_counter() - start) * 1000
            start = time.perf_counter()
            y = np.asarray(reference(a), dtype=float)
            reference_ms = (time.perf_counter() - start) * 1000
            assert x.shape == y.shape, (case, name, x.shape, y.shape)
            delta = x - y
            maxerr = float(np.max(np.abs(delta)))
            assert np.isfinite(delta).all(), (case, name)
            passed = None if limit is None else maxerr <= limit
            rec = dict(
                algorithm=name,
                case=case,
                reference=desc,
                kind=kind,
                max_abs_error=maxerr,
                mse=float(np.mean(delta**2)),
                mae=float(np.mean(np.abs(delta))),
                agreement_pct=float(np.mean(x == y) * 100),
                limit=limit,
                verdict="DESCRIPTIVE" if passed is None else ("PASS" if passed else "FAIL"),
                custom_ms=custom_ms,
                reference_ms=reference_ms,
            )
            if name in ["LoG", "canny", "boundary"]:
                xx, yy = x > 0, y > 0
                rec["edge_f1_exact"] = float(
                    2
                    * np.count_nonzero(xx & yy)
                    / max(np.count_nonzero(xx) + np.count_nonzero(yy), 1)
                )
            records.append(rec)
    df = pd.DataFrame(records)
    df.to_csv(out / "per_case.csv", index=False, encoding="utf-8-sig")
    summary = df.groupby(["algorithm", "kind"], sort=False).agg(
        cases=("case", "count"),
        max_abs_error=("max_abs_error", "max"),
        mse_mean=("mse", "mean"),
        mse_std=("mse", "std"),
        agreement_mean=("agreement_pct", "mean"),
        custom_ms_mean=("custom_ms", "mean"),
        custom_ms_std=("custom_ms", "std"),
    )
    summary.to_csv(out / "summary.csv", encoding="utf-8-sig")
    (out / "environment.json").write_text(
        json.dumps(
            dict(
                python=platform.python_version(),
                numpy=np.__version__,
                opencv=cv2.__version__,
                scipy=scipy.__version__,
                seed=2026,
                scope="8 synthetic fixtures + 10 demo images; not dataset segmentation accuracy",
            ),
            indent=2,
        ),
        encoding="utf-8",
    )
    failed = df[df.verdict == "FAIL"]
    print(
        f"{len(df)} comparisons, {len(failed)} failures; descriptive variants are not counted as passes."
    )
    if len(failed):
        print(failed[["algorithm", "case", "max_abs_error", "limit"]].to_string(index=False))
    return df


if __name__ == "__main__":
    result = run_comparisons()
    raise SystemExit(int((result.verdict == "FAIL").any()))
