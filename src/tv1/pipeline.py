"""TV1: shared NumPy pipeline for the Streamlit demo and experiments.

No web framework or library reference implementation is imported here.
"""

from dataclasses import asdict, dataclass

import numpy as np

from src import edges, enhancement, filters, metrics, morphology, sharpening
from src.validation import gray_image, odd_window


@dataclass(frozen=True)
class PipelineConfig:
    filter_name: str = "lee"
    window_size: int = 5
    num_looks: float = 4.0
    enhancement_name: str = "clahe"
    clip_limit: float = 2.0
    tile_grid: int = 8
    sharpening_name: str = "none"
    sharp_k: float = 1.0
    edge_name: str = "morphology"
    low_threshold: float = 35.0
    high_threshold: float = 90.0
    min_area: int = 300
    min_contrast: float = 0.10
    closing_radius: int = 4
    manual_threshold: int | None = None
    adaptive_otsu: bool = True


FILTER_NAMES = ["none", "box", "gaussian", "median", "bilateral", "lee", "frost", "kuan"]
ENHANCEMENT_NAMES = ["none", "log", "he", "clahe", "homomorphic"]
SHARPENING_NAMES = ["none", "unsharp", "laplacian", "sobel"]
EDGE_NAMES = ["morphology", "canny", "sobel", "prewitt", "roberts", "log"]


def process_image(image: np.ndarray, config: PipelineConfig = PipelineConfig()) -> dict:
    """Return raw, filtered, enhanced, displayed, edges, overlay, metrics, stats.

    Segmentation uses pre-sharpening intensities and a pre-CLAHE reference.
    The output mask denotes dark candidates, never confirmed oil identity.
    """
    raw = gray_image(image)
    odd_window(config.window_size)
    for name, allowed in [
        (config.filter_name, FILTER_NAMES),
        (config.enhancement_name, ENHANCEMENT_NAMES),
        (config.sharpening_name, SHARPENING_NAMES),
        (config.edge_name, EDGE_NAMES),
    ]:
        if name not in allowed:
            raise ValueError(f"Unknown method: {name}")
    k = config.window_size
    filter_funcs = {
        "none": lambda a: a.copy(),
        "box": lambda a: filters.custom_box_filter(a, k),
        "gaussian": lambda a: filters.custom_gaussian_filter(a, k),
        "median": lambda a: filters.custom_median_filter(a, k),
        "bilateral": lambda a: filters.custom_bilateral_filter(a, k),
        "lee": lambda a: filters.custom_lee_filter(a, k, config.num_looks),
        "kuan": lambda a: filters.custom_kuan_filter(a, k, config.num_looks),
        "frost": lambda a: filters.custom_frost_filter(a, k),
    }
    filtered = filter_funcs[config.filter_name](raw)
    enhanced = {
        "none": lambda a: a.copy(),
        "log": enhancement.log_transform,
        "he": lambda a: enhancement.global_histogram_equalization(a)[0],
        "clahe": lambda a: enhancement.custom_clahe(
            a, config.clip_limit, (config.tile_grid, config.tile_grid)
        ),
        "homomorphic": enhancement.homomorphic_filter,
    }[config.enhancement_name](filtered)
    displayed = {
        "none": lambda a: a.copy(),
        "unsharp": lambda a: sharpening.unsharp_masking(a, k=config.sharp_k),
        "laplacian": lambda a: sharpening.laplacian_sharpening(a, alpha=config.sharp_k),
        "sobel": lambda a: sharpening.sobel_edge_enhancement(a)[1],
    }[config.sharpening_name](enhanced)
    stats = {}
    if config.edge_name == "morphology":
        result = morphology.detect_oil_slick_morphological(
            enhanced,
            min_area=config.min_area,
            min_contrast=config.min_contrast,
            reference_image=filtered,
            closing_radius=config.closing_radius,
            adaptive_otsu=config.adaptive_otsu,
            manual_threshold=config.manual_threshold,
        )
        boundary = result["boundary_mask"]
        mask = result["clean_mask"]
        stats = {
            key: value
            for key, value in result.items()
            if key not in ["boundary_mask", "clean_mask"]
        }
    else:
        magnitude = {
            "canny": lambda: edges.custom_canny(
                enhanced, config.low_threshold, config.high_threshold
            ),
            "sobel": lambda: edges.custom_sobel(enhanced)[2],
            "prewitt": lambda: edges.custom_prewitt(enhanced)[2],
            "roberts": lambda: edges.custom_roberts(enhanced),
            "log": lambda: edges.custom_log(enhanced),
        }[config.edge_name]()
        boundary = (
            magnitude
            if config.edge_name in ["canny", "log"]
            else ((magnitude > 0) & (magnitude >= config.high_threshold)).astype(np.uint8) * 255
        )
        mask = None  # Edge pixels must not be reported as segmented oil area.
    return dict(
        raw=raw,
        filtered=filtered,
        enhanced=enhanced,
        displayed=displayed,
        boundary=boundary,
        mask=mask,
        overlay=edges.overlay_edges(raw, boundary),
        stats=stats,
        metrics=metrics.calculate_all_enhancement_metrics(raw, displayed),
        config=asdict(config),
    )
