# Prompt vẽ sơ đồ thuật toán (IEEE style)

Dán nguyên khối dưới đây vào công cụ sinh ảnh/vẽ (hoặc LLM sinh TikZ/draw.io/Mermaid/SVG).

```text
Create a publication-quality algorithm flowchart for an IEEE journal/conference paper (IEEE Transactions style, double-column width ≈ 7.16 in, vector-like, white background, grayscale-friendly with one accent color for the oil-slick branch, sans-serif Times/Helvetica labels 8–9 pt, thin 0.75 pt black arrows, rounded rectangles for processing blocks, parallelograms for I/O, diamonds for decisions, dashed boxes to group stages, no 3D, no shadows, no clipart). Figure caption: "Fig. 1. Proposed classical (non-learning) pipeline for oil-slick candidate detection in Sentinel-1 SAR imagery."

TITLE: Training-free SAR oil-spill detection: speckle filtering → contrast enhancement → adaptive Otsu → morphology → contrast-ratio validation.

Flow (top to bottom, 5 dashed stage groups, labelled with Roman numerals):

INPUT (parallelogram): "SAR image I (8-bit grayscale, 400×400, Sentinel-1)".

STAGE I – Speckle reduction (block): "Lee MMSE filter, window 5×5, L = 4 looks".
  Equations beside block: 
  σ_v² = 1/L;  Ī = box_5×5(I);  Var(I) = box(I²) − Ī²;
  K = clip(1 − Ī²σ_v² / Var(I), 0, 1);  R̂ = Ī + K (I − Ī).
  Output label: "I_f (filtered, reference image)".

STAGE II – Contrast enhancement (block): "CLAHE, 8×8 tiles, clip limit 2.0, 256-bin histograms, clipped excess redistributed uniformly, tile CDF → LUT, bilinear interpolation between 4 neighbouring tile LUTs".
  Output label: "I_e (enhanced)".
  Draw a dashed side branch from I_e labelled "optional display only: unsharp masking (not used for segmentation — decoupled)".

STAGE III – Adaptive threshold selection (block group):
  (a) Two parallel blocks: "Otsu(I_e) → (t_e, η_e)" and "Otsu(I_f) → (t_f, η_f)", with
      t* = argmax_t w0(t) w1(t) [μ0(t) − μ1(t)]²,  η = σ_B²(t*) / σ_T².
  (b) Diamond: "dark fraction of I_e > 30 % and of I_f ≤ 30 %, OR η_f > η_e + 0.05 ?"
        Yes → select segmentation image S = I_f, t = t_f.
        No  → select S = I_e, t = t_e.
  (c) Diamond: "mean(S ≤ t) > 35 % ?"  Yes → block "t ← max(1, t − max(round(0.10(μ_sea − μ_dark)), 3))"; No → keep t.
  Note: "If a manual threshold is given it overrides Otsu."
  (d) Block: "Dark-spot mask D = [S ≤ t]" with the remark "oil → low backscatter (capillary-wave damping)".
  Measurement image for later stages: calc = I_f.

STAGE IV – Morphological regularization (3 sequential blocks, show structuring-element icons):
  "Opening: D ∘ B_disk(r=2)  (5×5 disk)  – remove sea-clutter specks"
  → "Closing: • B_disk(r=4)  (9×9 disk)  – bridge wave-foam gaps"
  → "8-connected component labelling (run-length union-find); discard area < A_min = 300 px".

STAGE V – Candidate validation (loop box "for each component Ω_i"):
  "Ring buffer: R_i = (Ω_i ⊕ B_15×15) \ Ω_i"
  → "μ_slick = mean_{Ω_i}(I_f),  μ_sea = mean_{R_i}(I_f)"
  → "C_R = (μ_sea − μ_slick) / μ_sea"
  → Diamond "C_R ≥ C_min = 0.10 ?"  Yes → add Ω_i to clean mask M;  No → reject (arrow to a small "discard" terminal).
  (Also: no ring pixels → reject.)

BOUNDARY EXTRACTION (block): "β(M) = M \ (M ⊖ B_3×3)  (1-px morphological boundary)".

OUTPUT (parallelogram, 3 items): "Candidate mask M", "Boundary overlay (red) on image", "Statistics: N slicks, area %, mean C_R, Otsu t*, separability η".

Layout rules: single main vertical spine, the two Otsu blocks placed side by side then merged by the decision diamond; label every arrow with the variable it carries (I, I_f, I_e, S, D, M, β(M)); use consistent notation (italic variables, upright operators ⊖ ⊕ ∘ •); equal block widths; thin dashed frames titled "I. Speckle Filtering", "II. Enhancement", "III. Adaptive Thresholding", "IV. Morphology", "V. Validation". Add a small legend (block = operation, diamond = decision, dashed = stage). Do NOT include any machine-learning / CNN elements: the method is purely classical image processing implemented in NumPy. Output as SVG/PDF vector, 300 dpi if raster.
```

## Phiên bản để viết phần Method trong bài (tùy chọn)

```text
Write the "Proposed Method" section in IEEE style (formal, third-person, numbered equations) describing exactly: (1) Lee MMSE speckle filter (5×5, L=4); (2) CLAHE (8×8, clip 2.0, bilinear LUT interpolation); (3) Otsu thresholding with separability η = σ_B²/σ_T², dual-image selection rule (dark fraction > 30 % or η_f > η_e + 0.05 → use Lee-filtered image) and adaptive offset (dark fraction > 35 % → t ← t − max(0.10(μ_sea − μ_dark), 3)); (4) opening with 5×5 disk then closing with 9×9 disk; (5) 8-connected labelling with A_min = 300 px; (6) contrast ratio C_R = (μ_sea − μ_slick)/μ_sea over a 15×15 dilated ring, threshold 0.10; (7) boundary β(A) = A \ (A ⊖ B_3×3). State that the output is a dark-spot candidate mask, not confirmed oil (look-alikes are not discriminated), and that no learning is used.
```

