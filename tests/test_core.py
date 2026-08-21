"""Regression checks for the academic NumPy core and reported bug fixes."""

import cv2
import numpy as np
import pytest

from src.edges import custom_canny
from src.enhancement import custom_clahe, global_histogram_equalization
from src.morphology import (
    custom_otsu_threshold,
    detect_oil_slick_morphological,
    find_connected_components,
)
from src.pipeline import PipelineConfig, process_image


@pytest.mark.parametrize("shape", [(1, 1), (1, 17), (17, 1), (19, 23), (64, 64)])
def test_components_partition_against_opencv(shape):
    a = (np.random.default_rng(31).random(shape) > 0.6).astype(np.uint8)
    count, labels, components = find_connected_components(a)
    n, ref = cv2.connectedComponents(a, connectivity=8)
    assert count == n - 1 == len(components)
    assert np.array_equal(labels > 0, a > 0)
    # A component must map to exactly one reference ID and vice versa.
    seen = []
    for c in components:
        ids = np.unique(ref[c["mask"]])
        assert len(ids) == 1 and ids[0] > 0
        seen.append(ids[0])
        assert c["area"] == int(np.count_nonzero(ref == ids[0]))
    assert len(set(seen)) == count


@pytest.mark.parametrize("value", [0, 127, 255])
def test_constant_images(value):
    a = np.full((32, 32), value, np.uint8)
    assert np.array_equal(global_histogram_equalization(a)[0], cv2.equalizeHist(a))
    assert custom_otsu_threshold(a) == (0, 0.0)
    assert not custom_canny(a, 0, 0).any()
    assert detect_oil_slick_morphological(a)["slicks_count"] == 0


@pytest.mark.parametrize(
    "shape,grid", [((32, 32), (1, 1)), ((33, 32), (4, 4)), ((23, 17), (3, 5)), ((1, 1), (8, 8))]
)
def test_clahe_boundaries_and_nondivisible_tiles(shape, grid):
    a = np.random.default_rng(31).integers(0, 256, shape, dtype=np.uint8)
    x = custom_clahe(a, 2, grid)
    y = cv2.createCLAHE(2, (grid[1], grid[0])).apply(a)
    assert np.max(np.abs(x.astype(float) - y)) <= 1


def test_large_region_obeys_contrast():
    a = np.full((200, 200), 100, np.uint8)
    a[60:140, 60:140] = 92
    assert (
        detect_oil_slick_morphological(a, manual_threshold=96, min_contrast=0.4)["slicks_count"]
        == 0
    )
    assert (
        detect_oil_slick_morphological(a, manual_threshold=96, min_contrast=0.05)["slicks_count"]
        == 1
    )


def test_otsu_includes_dark_class_endpoint():
    a = np.full((80, 80), 200, np.uint8)
    a[20:60, 20:60] = 50
    assert custom_otsu_threshold(a)[0] == 50
    r = detect_oil_slick_morphological(a, adaptive_otsu=False)
    assert r["clean_mask"][40, 40] == 255 and r["slicks_count"] == 1


def test_invalid_reference_and_parameters():
    a = np.zeros((32, 32), np.uint8)
    with pytest.raises(ValueError):
        detect_oil_slick_morphological(a, reference_image=a[:10])
    with pytest.raises(ValueError):
        process_image(a, PipelineConfig(window_size=4))
    with pytest.raises(ValueError):
        process_image(a, PipelineConfig(filter_name="unknown"))
    with pytest.raises(ValueError):
        custom_canny(a, 90, 35)


def test_edge_map_is_not_an_oil_area_mask():
    a = np.zeros((64, 64), np.uint8)
    a[20:40, 20:40] = 200
    r = process_image(a, PipelineConfig(edge_name="canny"))
    assert r["mask"] is None and r["stats"] == {}


def test_sharpening_does_not_change_segmentation():
    a = np.full((80, 80), 120, np.uint8)
    a[20:60, 20:60] = 20
    x = process_image(a, PipelineConfig(sharpening_name="none"))
    y = process_image(a, PipelineConfig(sharpening_name="unsharp", sharp_k=2))
    assert np.array_equal(x["mask"], y["mask"])


def test_metadata_min_area_does_not_change_labels():
    a = np.eye(20, dtype=np.uint8)
    n, x, c = find_connected_components(a)
    m, y, d = find_connected_components(a, min_area=100)
    assert n == m == 1 and np.array_equal(x, y) and len(c) == 1 and d == []


@pytest.mark.parametrize("method", ["sobel", "prewitt", "roberts"])
def test_zero_threshold_does_not_turn_a_constant_image_into_edges(method):
    image = np.full((40, 40), 80, np.uint8)
    result = process_image(
        image,
        PipelineConfig(
            filter_name="none", enhancement_name="none", edge_name=method, high_threshold=0
        ),
    )
    assert not result["boundary"].any()
