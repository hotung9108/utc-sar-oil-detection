"""
MODULE THUẬT TOÁN TÙY CHỈNH (CUSTOM ALGORITHMS FOR SAR OIL SPILL DETECTION)
=============================================================================
Nơi người dùng có thể tự do lập trình, thử nghiệm và cắm (plug-in) các thuật toán
xử lý ảnh mới vào giao diện Web Streamlit.

Hỗ trợ 3 nhóm hàm chính:
1. Bộ lọc khử nhiễu tùy chỉnh (Custom Filter)
2. Phân ngưỡng / Phân đoạn tùy chỉnh (Custom Thresholding / Segmentation)
3. Quy tắc phân loại vết dầu tùy chỉnh (Custom Heuristic Classifier)
"""

import numpy as np
import cv2


# =============================================================================
# 1. BỘ LỌC KHỬ NHIỄU TÙY CHỈNH (CUSTOM FILTER HOOK)
# =============================================================================
def custom_filter_template(image: np.ndarray, param1: float = 1.0, param2: int = 5) -> np.ndarray:
    """
    Template mẫu để người dùng tự viết bộ lọc mới (ví dụ: Frost Filter, Bilateral, v.v.).
    
    Tham số:
        image: Ảnh mức xám uint8 (2D numpy array [H, W])
        param1: Tham số điều khiển 1 (ví dụ hệ số suy giảm)
        param2: Kích thước cửa sổ (kernel size)
        
    Trả về:
        filtered_image: Ảnh sau khi lọc (uint8 [H, W])
    """
    # [VÍ DỤ MẪU]: Lọc Bilateral bảo toàn biên (Bilateral Filter)
    # Người dùng có thể thay thế đoạn code dưới đây bằng thuật toán của riêng mình:
    d = param2 if param2 % 2 == 1 else param2 + 1
    sigma_color = float(param1 * 25.0)
    sigma_space = float(param2)
    filtered = cv2.bilateralFilter(image, d=d, sigmaColor=sigma_color, sigmaSpace=sigma_space)
    return filtered


def frost_filter_demo(image: np.ndarray, window_size: int = 5, damping_factor: float = 2.0) -> np.ndarray:
    """
    Bộ lọc Frost (Frost Filter) đặc trưng cho ảnh Radar SAR.
    Lọc thích nghi dựa trên khoảng cách mũ đến tâm cửa sổ:
    M(x,y) = exp(-a * D * r), với D = sigma / mu, r là khoảng cách Euclidean tới tâm.
    """
    img_f = image.astype(np.float64)
    pad = window_size // 2
    h, w = img_f.shape
    padded = np.pad(img_f, pad, mode='reflect')
    
    # Ma trận khoảng cách r từ tâm cửa sổ
    y_idx, x_idx = np.mgrid[-pad:pad+1, -pad:pad+1]
    dist_r = np.sqrt(x_idx**2 + y_idx**2)
    
    # Kernel tính mean và mean square
    k_ones = np.ones((window_size, window_size), dtype=np.float64) / (window_size ** 2)
    local_mean = cv2.filter2D(img_f, -1, k_ones, borderType=cv2.BORDER_REFLECT)
    local_sq_mean = cv2.filter2D(img_f ** 2, -1, k_ones, borderType=cv2.BORDER_REFLECT)
    local_var = np.maximum(0.0, local_sq_mean - local_mean ** 2)
    local_ci = np.sqrt(local_var) / (local_mean + 1e-8)
    
    filtered = np.zeros_like(img_f)
    
    # Vectorized / Windowed Frost calculation
    for r in range(h):
        for c in range(w):
            patch = padded[r:r+window_size, c:c+window_size]
            ci_val = local_ci[r, c]
            weight = np.exp(-damping_factor * ci_val * dist_r)
            w_sum = np.sum(weight)
            if w_sum > 1e-8:
                filtered[r, c] = np.sum(patch * weight) / w_sum
            else:
                filtered[r, c] = local_mean[r, c]
                
    return np.clip(filtered, 0, 255).astype(np.uint8)


# =============================================================================
# 2. PHÂN NGƯỠNG TÙY CHỈNH (CUSTOM THRESHOLDING HOOK)
# =============================================================================
def custom_threshold_template(image: np.ndarray, k: float = -0.2, window_size: int = 31) -> np.ndarray:
    """
    Template mẫu phân ngưỡng thích nghi cục bộ Niblack:
    T(x,y) = mu(x,y) + k * sigma(x,y)
    
    Tham số:
        image: Ảnh xám sau lọc (uint8)
        k: Hệ số điều chỉnh (thường là số âm cho vệt tối: -0.1 đến -0.3)
        window_size: Kích thước cửa sổ cục bộ
        
    Trả về:
        dark_mask: Mặt nạ nhị phân (uint8: 255 = vết tối ứng viên, 0 = nền biển)
    """
    img_f = image.astype(np.float64)
    kernel = np.ones((window_size, window_size), dtype=np.float64) / (window_size ** 2)
    local_mean = cv2.filter2D(img_f, -1, kernel, borderType=cv2.BORDER_REFLECT)
    local_sq_mean = cv2.filter2D(img_f ** 2, -1, kernel, borderType=cv2.BORDER_REFLECT)
    local_std = np.sqrt(np.maximum(0.0, local_sq_mean - local_mean ** 2))
    
    threshold = local_mean + k * local_std
    
    # Vết tối ứng viên là các pixel có cường độ nhỏ hơn ngưỡng T(x,y)
    dark_mask = (img_f < threshold).astype(np.uint8) * 255
    return dark_mask


# =============================================================================
# 3. QUY TẮC PHÂN LOẠI VẾT DẦU TÙY CHỈNH (CUSTOM HEURISTIC RULE)
# =============================================================================
def custom_heuristic_classifier(features: dict, user_weights: dict = None) -> tuple[bool, str]:
    """
    Template mẫu bộ quy tắc kiểm tra xem một đốm tối có phải là vết dầu loang hay không.
    
    Các đặc trưng nhận vào trong `features`:
    - 'area': Diện tích (pixel)
    - 'elongation': Độ thuôn dài (MajorAxis / MinorAxis)
    - 'boundary_complexity': Độ phức tạp đường biên (P^2 / 4*pi*A)
    - 'contrast_diff': Độ chênh lệch mức xám trung bình giữa biển và vết dầu
    - 'damping_ratio': Tỉ số suy giảm cường độ (mu_sea / mu_oil)
    - 'border_gradient': Độ dốc gradient Sobel trung bình dọc theo đường biên
    
    Trả về:
        (is_oil: bool, reason: str)
    """
    area = features.get('area', 0)
    elongation = features.get('elongation', 1.0)
    contrast = features.get('contrast_diff', 0.0)
    border_grad = features.get('border_gradient', 0.0)
    
    # Tiêu chí logic:
    if area < 80:
        return False, "Diện tích quá nhỏ (<80 px)"
    if contrast < 10.0:
        return False, "Độ tương phản quá thấp so với nền biển"
    if border_grad < 5.0:
        return False, "Biên mờ (gradient nhỏ, khả năng cao là vùng gió lặng)"
        
    # Vết dầu loang thường có tính thuôn dài (dạng vệt di chuyển từ tàu) hoặc biên gấp khúc
    if elongation >= 1.8 or features.get('boundary_complexity', 1.0) >= 2.0:
        return True, "Thỏa mãn đầy đủ tiêu chuẩn hình thái và độ tương phản vệt dầu"
        
    return False, "Đốm tối dạng mảng tròn/bè đồng nhất (nghi vấn look-alike)"
