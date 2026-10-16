"""Intensity and contrast feature extraction for candidate blobs."""
import numpy as np
import cv2

def compute_intensity_features(img: np.ndarray, contour: np.ndarray, mask: np.ndarray) -> dict:
    """
    Computes intensity, border gradient, and annulus background contrast:
    - Mean slick intensity
    - Background mean intensity (annulus ring)
    - Damping ratio (Background Mean / Slick Mean)
    - Average Sobel border gradient
    """
    img_f = img.astype(np.float64)
    h, w = img.shape
    
    # 1. Slick blob mask
    blob_mask = np.zeros((h, w), dtype=np.uint8)
    cv2.drawContours(blob_mask, [contour], -1, 255, thickness=-1)
    
    slick_pixels = img_f[blob_mask == 255]
    mean_slick = np.mean(slick_pixels) if len(slick_pixels) > 0 else 0.0
    
    # 2. Annulus ring background
    se_dilate = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (13, 13))
    dilated_mask = cv2.dilate(blob_mask, se_dilate)
    annulus_mask = (dilated_mask == 255) & (mask == 0) # Only non-slick ocean pixels
    
    bg_pixels = img_f[annulus_mask]
    mean_bg = np.mean(bg_pixels) if len(bg_pixels) > 0 else np.mean(img_f)
    
    # Damping ratio (attenuation factor)
    damping_ratio = mean_bg / (mean_slick + 1e-6)
    contrast_diff = mean_bg - mean_slick
    
    # 3. Sobel Border Gradient
    sobel_x = cv2.Sobel(img_f, cv2.CV_64F, 1, 0, ksize=3)
    sobel_y = cv2.Sobel(img_f, cv2.CV_64F, 0, 1, ksize=3)
    grad_mag = np.sqrt(sobel_x ** 2 + sobel_y ** 2)
    
    perimeter_mask = np.zeros((h, w), dtype=np.uint8)
    cv2.drawContours(perimeter_mask, [contour], -1, 255, thickness=1)
    border_pixels = grad_mag[perimeter_mask == 255]
    mean_border_grad = np.mean(border_pixels) if len(border_pixels) > 0 else 0.0
    
    return {
        "mean_slick": float(mean_slick),
        "mean_bg": float(mean_bg),
        "contrast_diff": float(contrast_diff),
        "damping_ratio": float(damping_ratio),
        "border_gradient": float(mean_border_grad)
    }
