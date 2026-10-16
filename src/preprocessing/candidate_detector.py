"""Adaptive thresholding and morphological operations for dark spot candidate detection."""
import numpy as np
import cv2

def adaptive_threshold_dark(img: np.ndarray, window_size: int = 55, k: float = 0.20, min_std: float = 8.0) -> np.ndarray:
    """
    Sauvola adaptive thresholding tailored to extract dark spots on ocean background.
    Includes minimum standard deviation condition to prevent segmenting noise in flat calm seas.
    """
    if img.dtype != np.float64:
        img_f = img.astype(np.float64)
    else:
        img_f = img.copy()
        
    kernel = np.ones((window_size, window_size), dtype=np.float64) / (window_size ** 2)
    local_mean = cv2.filter2D(img_f, -1, kernel, borderType=cv2.BORDER_REFLECT)
    local_sq_mean = cv2.filter2D(img_f ** 2, -1, kernel, borderType=cv2.BORDER_REFLECT)
    local_std = np.sqrt(np.maximum(0.0, local_sq_mean - local_mean ** 2))
    
    # Sauvola threshold
    threshold = local_mean * (1.0 + k * (local_std / 128.0 - 1.0))
    
    # Dark spot condition: strictly below threshold AND having sufficient local contrast
    dark_mask = ((img_f < threshold) & (local_std > min_std)).astype(np.uint8) * 255
    return dark_mask

def morphological_cleanup(binary_mask: np.ndarray, min_area: int = 120, max_area: int = 25000, close_radius: int = 4) -> np.ndarray:
    """
    Cleans up candidate binary mask using mathematical morphology:
    - Opening (remove isolated wave clutter)
    - Closing (connect broken slick segments)
    - Hole filling
    - Area filtering
    """
    se_open = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    opened = cv2.morphologyEx(binary_mask, cv2.MORPH_OPEN, se_open)
    
    se_close = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (close_radius * 2 + 1, close_radius * 2 + 1))
    closed = cv2.morphologyEx(opened, cv2.MORPH_CLOSE, se_close)
    
    # Hole filling
    h, w = closed.shape
    filled = closed.copy()
    mask_flood = np.zeros((h + 2, w + 2), np.uint8)
    cv2.floodFill(filled, mask_flood, (0, 0), 255)
    filled_inv = cv2.bitwise_not(filled)
    holes_filled = closed | filled_inv
    
    # Area filtering
    num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(holes_filled, connectivity=8)
    clean_mask = np.zeros_like(binary_mask)
    
    for label in range(1, num_labels):
        area = stats[label, cv2.CC_STAT_AREA]
        if min_area <= area <= max_area:
            clean_mask[labels == label] = 255
            
    return clean_mask
