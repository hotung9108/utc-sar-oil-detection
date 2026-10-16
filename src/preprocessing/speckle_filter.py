"""Speckle filtering algorithms for SAR images."""
import numpy as np
import cv2

def lee_filter(img: np.ndarray, window_size: int = 5, cu: float = 0.52) -> np.ndarray:
    """
    Applies the Lee filter to suppress multiplicative SAR speckle noise.
    
    Formula:
        R_hat = mu_k + W_k * (I - mu_k)
        W_k = max(0, 1 - (Cu^2 / Ci^2))
        Ci = sigma_k / mu_k
        
    Args:
        img: Grayscale input image (uint8 or float [0, 1]).
        window_size: Moving window size (default: 5).
        cu: Noise variation coefficient (default: 0.52 for Sentinel-1).
        
    Returns:
        Filtered image with speckle suppressed and slick edges preserved.
    """
    is_uint8 = (img.dtype == np.uint8)
    img_float = img.astype(np.float64) / 255.0 if is_uint8 else img.astype(np.float64)
    
    kernel = np.ones((window_size, window_size), dtype=np.float64) / (window_size ** 2)
    
    # Local mean mu_k
    local_mean = cv2.filter2D(img_float, -1, kernel, borderType=cv2.BORDER_REFLECT)
    
    # Local variance sigma_k^2
    local_sq_mean = cv2.filter2D(img_float ** 2, -1, kernel, borderType=cv2.BORDER_REFLECT)
    local_var = np.maximum(0.0, local_sq_mean - local_mean ** 2)
    
    # Signal variation coefficient Ci = sigma_k / mu_k
    eps = 1e-8
    ci = np.sqrt(local_var) / (local_mean + eps)
    
    # Lee weight W_k
    weight = np.maximum(0.0, 1.0 - (cu ** 2) / (ci ** 2 + eps))
    weight = np.clip(weight, 0.0, 1.0)
    
    # Estimated backscatter R_hat
    filtered = local_mean + weight * (img_float - local_mean)
    filtered = np.clip(filtered, 0.0, 1.0)
    
    if is_uint8:
        return (filtered * 255.0).round().astype(np.uint8)
    return filtered

def clahe_enhance(img: np.ndarray, clip_limit: float = 2.0, tile_grid: tuple = (8, 8)) -> np.ndarray:
    """Applies Contrast Limited Adaptive Histogram Equalization."""
    if img.dtype != np.uint8:
        img_u8 = (np.clip(img, 0, 1) * 255).astype(np.uint8)
    else:
        img_u8 = img
    clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=tile_grid)
    return clahe.apply(img_u8)
