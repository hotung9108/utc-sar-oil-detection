"""Exact publisher RGB mapping; unknown colors stay ignored, never background."""
import numpy as np

CLASS_NAMES = ('sea', 'oil', 'look_alike', 'land')
CLASS_COLORS = ((0, 0, 255), (255, 0, 0), (0, 255, 0), (0, 0, 0))
IGNORE_LABEL = 255


def decode_mask(rgb):
    rgb = np.asarray(rgb)
    if rgb.ndim != 3 or rgb.shape[-1] != 3 or rgb.dtype != np.uint8:
        raise ValueError('Expected H x W x 3 uint8 RGB mask; no implicit rescaling')
    labels = np.full(rgb.shape[:2], IGNORE_LABEL, dtype=np.uint8)
    for index, color in enumerate(CLASS_COLORS):
        labels[np.all(rgb == color, axis=-1)] = index
    return labels
