---
name: sar-oil-cv
description: Workflows and pure computer vision algorithms for Sentinel-1 SAR oil spill candidate detection, speckle filtering, adaptive thresholding, and morphological feature extraction.
---

# SAR Oil Spill Computer Vision Detection Skill

## Overview
This skill provides structured workflows and algorithmic reference implementations in MATLAB and Python for detecting oil spill candidate patches in Sentinel-1 SAR imagery without machine learning.

## Step-by-Step Processing Pipeline
1. **Speckle Filtering (Lọc nhiễu đốm SAR)**:
   - Apply Lee Filter or Wiener Filter ($5 \times 5$ or $7 \times 7$) to suppress multiplicative speckle noise while preserving sharp slick boundaries.
2. **Contrast Enhancement & Radiometric Normalization**:
   - Apply CLAHE (Contrast Limited Adaptive Histogram Equalization) with clip limit 0.02 to heighten contrast between dark slicks and background sea clutter.
3. **Adaptive Thresholding (Phân ngưỡng thích nghi)**:
   - Compute local statistical threshold: $T(x,y) = \mu_{local}(x,y) - k \cdot \sigma_{local}(x,y)$ or Sauvola thresholding.
   - Binarize image where $I(x,y) < T(x,y)$ represents dark candidate spots.
4. **Mathematical Morphology (Hình thái học)**:
   - `Opening` ($3 \times 3$) to remove isolated wave clutter dots.
   - `Closing` ($5 \times 5$ or $7 \times 7$) to connect broken slick segments.
   - `Hole filling` (`imfill` in MATLAB / flood fill in Python).
   - Area filtering (`bwareaopen` in MATLAB / contour area $\ge 50$ px in Python).
5. **Feature Extraction & Rule-based Identification**:
   - Compute Elongation ($MajorAxis / MinorAxis$), Boundary Complexity ($Perimeter^2 / (4\pi Area)$), Annulus background contrast ratio ($Damping \ge 1.35$), and Sobel boundary gradient.
   - Filter false positives (look-alikes) using geometry thresholds.
