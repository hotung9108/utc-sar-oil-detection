"""Shape and geometric feature extraction for candidate blobs."""
import numpy as np
import cv2

def compute_shape_features(contour: np.ndarray) -> dict:
    """
    Computes geometric shape features for a candidate slick contour:
    - Area
    - Perimeter
    - Elongation (Aspect ratio of fitted ellipse)
    - Boundary Complexity (Perimeter^2 / (4 * pi * Area))
    - Solidity (Area / ConvexHullArea)
    """
    area = cv2.contourArea(contour)
    perimeter = cv2.arcLength(contour, closed=True)
    
    # Elongation via minimum area bounding rectangle or fitted ellipse
    elongation = 1.0
    if len(contour) >= 5:
        try:
            ellipse = cv2.fitEllipse(contour)
            (center, (axis_a, axis_b), angle) = ellipse
            major_axis = max(axis_a, axis_b)
            minor_axis = min(axis_a, axis_b)
            elongation = major_axis / (minor_axis + 1e-6)
        except Exception:
            rect = cv2.minAreaRect(contour)
            w, h = rect[1]
            elongation = max(w, h) / (min(w, h) + 1e-6)
    else:
        rect = cv2.minAreaRect(contour)
        w, h = rect[1]
        elongation = max(w, h) / (min(w, h) + 1e-6) if min(w, h) > 0 else 1.0
        
    # Complexity
    complexity = (perimeter ** 2) / (4.0 * np.pi * area + 1e-6) if area > 0 else 1.0
    
    # Solidity
    hull = cv2.convexHull(contour)
    hull_area = cv2.contourArea(hull)
    solidity = area / (hull_area + 1e-6) if hull_area > 0 else 1.0
    
    return {
        "area": float(area),
        "perimeter": float(perimeter),
        "elongation": float(elongation),
        "complexity": float(complexity),
        "solidity": float(solidity)
    }
