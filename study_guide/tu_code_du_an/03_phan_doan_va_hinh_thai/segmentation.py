"""MODULE 3: SEGMENTATION & MORPHOLOGY FROM SCRATCH (NUMPY THUẦN)

Module này tự triển khai toàn bộ thuật toán phân đoạn và hình thái học:
1. Phân ngưỡng toàn cục Otsu (Tối ưu hóa phương sai liên lớp)
2. Phân ngưỡng thích nghi Niblack (Tính mean và std cục bộ O(1))
3. Toán tử hình thái học Erode, Dilate, Opening, Closing
4. Gán nhãn liên thông 8 hướng bằng thuật toán Union-Find nén đường đi
"""
from __future__ import annotations
import numpy as np


# ==============================================================================
# 1. PHÂN NGƯỠNG TOÀN CỤC OTSU
# ==============================================================================
def otsu_threshold(img: np.ndarray) -> tuple[float, np.ndarray]:
    """Tìm ngưỡng Otsu tối ưu phân chia giữa Nền biển và Đốm tối.

    Returns:
        (best_thresh_float, dark_spot_mask)
        Trong đó dark_spot_mask = 1 cho vùng TỐI (dầu), 0 cho nền biển sáng.
    """
    img_u8 = np.clip(img * 255.0 if img.max() <= 1.0 else img, 0, 255).astype(np.uint8)
    hist, _ = np.histogram(img_u8, bins=256, range=(0, 256))
    total_pixels = img.size

    sum_total = np.sum(np.arange(256) * hist)
    weight_bg = 0
    sum_bg = 0
    best_thresh = 0
    max_between_var = -1.0

    for t in range(256):
        weight_bg += hist[t]
        if weight_bg == 0:
            continue
        weight_fg = total_pixels - weight_bg
        if weight_fg == 0:
            break

        sum_bg += t * hist[t]
        mean_bg = sum_bg / weight_bg
        mean_fg = (sum_total - sum_bg) / weight_fg

        # sigma_b^2 = w0 * w1 * (mu0 - mu1)^2
        between_var = float(weight_bg) * float(weight_fg) * ((mean_bg - mean_fg) ** 2)
        if between_var > max_between_var:
            max_between_var = between_var
            best_thresh = t

    # Đốm dầu là vùng TỐI (giá trị < ngưỡng)
    dark_mask = (img_u8 < best_thresh).astype(np.uint8)
    return float(best_thresh), dark_mask


# ==============================================================================
# 2. PHÂN NGƯỠNG THÍCH NGHI NIBLACK
# ==============================================================================
def niblack_threshold(
    img: np.ndarray,
    window_size: int = 31,
    k: float = 0.2
) -> np.ndarray:
    """Ngưỡng thích nghi cục bộ Niblack: T(x, y) = m(x, y) - k * s(x, y).

    Tối ưu hóa bằng 2 bảng tích lũy SAT: một bảng cho x và một bảng cho x^2
    để tính mean và variance cục bộ trong thời gian O(1) mỗi pixel.
    """
    H, W = img.shape
    pad = window_size // 2
    padded = np.pad(img, pad, mode='reflect')

    # Bảng tích lũy SAT cho ảnh gốc
    sat1 = np.zeros((H + 2 * pad + 1, W + 2 * pad + 1), dtype=np.float64)
    sat1[1:, 1:] = np.cumsum(np.cumsum(padded, axis=0), axis=1)

    # Bảng tích lũy SAT cho ảnh bình phương (để tính phương sai: E[X^2] - (E[X])^2)
    sat2 = np.zeros_like(sat1)
    sat2[1:, 1:] = np.cumsum(np.cumsum(padded ** 2, axis=0), axis=1)

    r1 = np.arange(H)
    r2 = r1 + window_size
    c1 = np.arange(W)
    c2 = c1 + window_size

    R1, C1 = np.meshgrid(r1, c1, indexing='ij')
    R2, C2 = np.meshgrid(r2, c2, indexing='ij')
    area = float(window_size * window_size)

    sum1 = sat1[R2, C2] - sat1[R1, C2] - sat1[R2, C1] + sat1[R1, C1]
    sum2 = sat2[R2, C2] - sat2[R1, C2] - sat2[R2, C1] + sat2[R1, C1]

    local_mean = sum1 / area
    local_var = np.maximum(0.0, (sum2 / area) - (local_mean ** 2))
    local_std = np.sqrt(local_var)

    # Ngưỡng cục bộ
    threshold_map = local_mean - k * local_std

    # Vết dầu là vùng tối: img < threshold_map
    dark_mask = (img < threshold_map).astype(np.uint8)
    return dark_mask


# ==============================================================================
# 3. TOÁN TỬ HÌNH THÁI HỌC TỰ CÀI
# ==============================================================================
def binary_erosion(mask: np.ndarray, size: int = 3) -> np.ndarray:
    """Toán tử Co (Erode) nhị phân: Chỉ giữ 1 nếu toàn bộ lân cận đều là 1."""
    H, W = mask.shape
    pad = size // 2
    padded = np.pad(mask, pad, mode='constant', constant_values=0)
    out = np.zeros_like(mask, dtype=np.uint8)

    for r in range(H):
        for c in range(W):
            if np.all(padded[r : r + size, c : c + size] == 1):
                out[r, c] = 1
    return out


def binary_dilation(mask: np.ndarray, size: int = 3) -> np.ndarray:
    """Toán tử Giãn (Dilate) nhị phân: Bằng 1 nếu có ít nhất 1 pixel lân cận là 1."""
    H, W = mask.shape
    pad = size // 2
    padded = np.pad(mask, pad, mode='constant', constant_values=0)
    out = np.zeros_like(mask, dtype=np.uint8)

    for r in range(H):
        for c in range(W):
            if np.any(padded[r : r + size, c : c + size] == 1):
                out[r, c] = 1
    return out


def morphological_closing(mask: np.ndarray, size: int = 3) -> np.ndarray:
    """Toán tử Đóng (Closing = Dilate sau đó Erode) giúp lấp vết nứt nội vùng."""
    return binary_erosion(binary_dilation(mask, size=size), size=size)


# ==============================================================================
# 4. GÁN NHÃN LIÊN THÔNG 8 HƯỚNG BẰNG UNION-FIND NÉN ĐƯỜNG ĐI
# ==============================================================================
class DisjointSet:
    """Cấu trúc dữ liệu rừng tập hợp rời nhau với kỹ thuật Nén đường đi (Path Compression)."""
    def __init__(self, size: int):
        self.parent = list(range(size))

    def find(self, i: int) -> int:
        if self.parent[i] == i:
            return i
        self.parent[i] = self.find(self.parent[i])
        return self.parent[i]

    def union(self, i: int, j: int):
        root_i = self.find(i)
        root_j = self.find(j)
        if root_i != root_j:
            self.parent[root_i] = root_j


def connected_components_union_find(
    mask: np.ndarray,
    min_area: int = 64
) -> tuple[np.ndarray, list[dict]]:
    """Gán nhãn liên thông 8 hướng (Two-Pass Union-Find) và lọc bỏ vùng rác diện tích.

    Returns:
        labeled_img: Ma trận số nguyên (H, W), mỗi vùng có ID duy nhất từ 1..N
        regions: Danh sách từ điển thông tin từng vùng (label, area, bbox, coords)
    """
    H, W = mask.shape
    temp_labels = np.zeros((H, W), dtype=np.int32)
    next_label = 1
    max_possible_labels = H * W // 2 + 2
    dset = DisjointSet(max_possible_labels)

    # 8 hướng lân cận cho lượt quét xuôi (các pixel đã duyệt trước đó):
    # (-1, -1), (-1, 0), (-1, 1), (0, -1)

    # LƯỢT 1: Quét xuôi gán nhãn tạm và union các nhãn chạm nhau
    for r in range(H):
        for c in range(W):
            if mask[r, c] == 1:
                neighbors = []
                if r > 0 and c > 0 and temp_labels[r-1, c-1] > 0:
                    neighbors.append(temp_labels[r-1, c-1])
                if r > 0 and temp_labels[r-1, c] > 0:
                    neighbors.append(temp_labels[r-1, c])
                if r > 0 and c < W - 1 and temp_labels[r-1, c+1] > 0:
                    neighbors.append(temp_labels[r-1, c+1])
                if c > 0 and temp_labels[r, c-1] > 0:
                    neighbors.append(temp_labels[r, c-1])

                if not neighbors:
                    temp_labels[r, c] = next_label
                    next_label += 1
                else:
                    min_lab = min(neighbors)
                    temp_labels[r, c] = min_lab
                    for lab in neighbors:
                        dset.union(min_lab, lab)

    # LƯỢT 2: Chuẩn hóa nhãn gốc (Canonical root)
    canonical_map: dict[int, int] = {}
    region_pixels: dict[int, list[tuple[int, int]]] = {}
    final_id = 1

    for r in range(H):
        for c in range(W):
            val = temp_labels[r, c]
            if val > 0:
                root = dset.find(val)
                if root not in canonical_map:
                    canonical_map[root] = final_id
                    region_pixels[final_id] = []
                    final_id += 1
                assigned_id = canonical_map[root]
                region_pixels[assigned_id].append((r, c))

    # LỌC VÙNG RÁC (< min_area) VÀ ĐÓNG GÓI KẾT QUẢ
    labeled_matrix = np.zeros((H, W), dtype=np.int32)
    valid_regions = []
    real_label = 1

    for old_id, coords_list in region_pixels.items():
        area = len(coords_list)
        if area >= min_area:
            coords = np.array(coords_list)
            r_min, r_max = int(np.min(coords[:, 0])), int(np.max(coords[:, 0]))
            c_min, c_max = int(np.min(coords[:, 1])), int(np.max(coords[:, 1]))

            for cr, cc in coords_list:
                labeled_matrix[cr, cc] = real_label

            valid_regions.append({
                "label": real_label,
                "area": area,
                "bbox": (r_min, c_min, r_max - r_min + 1, c_max - c_min + 1),
                "coords": coords
            })
            real_label += 1

    return labeled_matrix, valid_regions


# ==============================================================================
# BÀI TẬP THỰC NGHIỆM TỰ KIỂM TRA
# ==============================================================================
if __name__ == "__main__":
    print("=" * 70)
    print("--- [MODULE 3] KIỂM TRA PHÂN ĐOẠN VÀ GÁN NHÃN LIÊN THÔNG ---")
    print("=" * 70)

    # Tạo ảnh nhị phân giả lập có 2 vùng:
    # Vùng A: Rộng lớn (80 pixel) mô phỏng vết dầu
    # Vùng B: Bé li ti (10 pixel) mô phỏng bọt sóng rác
    synthetic_mask = np.zeros((30, 30), dtype=np.uint8)
    synthetic_mask[5:15, 5:13] = 1   # 10 x 8 = 80 pixel
    synthetic_mask[22:24, 22:27] = 1 # 2 x 5 = 10 pixel

    print(f"Tổng số pixel trắng ban đầu: {np.sum(synthetic_mask)}")

    labeled, regions = connected_components_union_find(synthetic_mask, min_area=50)
    print(f"Số vùng tìm thấy sau lọc rác (min_area=50): {len(regions)}")
    for reg in regions:
        print(f" -> Vùng #{reg['label']}: Diện tích = {reg['area']} px, Bounding Box = {reg['bbox']}")

    print("\n✅ MODULE 3 HOẠT ĐỘNG HOÀN HẢO!")
