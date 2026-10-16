"""
Module Trích xuất Đặc trưng Hình học & Vật lý phân biệt Đốm tối SAR thuần NumPy 100%.
Phục vụ Đồ án Xử lý ảnh: Phát hiện vết dầu tràn trên ảnh SAR Sentinel-1 (CSIRO Dataset).
Bộ môn Kỹ thuật Máy tính - Trường Đại học Giao thông Vận tải (UTC).
Giảng viên hướng dẫn: TS. Phan Thanh Toàn.

Tác giả: TV4 - Thành viên phụ trách Thuật toán Hình thái học & Trích xuất đặc trưng vật lý.
Yêu cầu kỹ thuật: Tự lập trình 100% bằng NumPy thuần các toán tử vi phân và đặc trưng phân loại.
"""

import numpy as np
from src.morphology.numpy_morphology import custom_dilate, custom_extract_boundary


def custom_sobel_gradient(
    image: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    r"""
    Tính toán đạo hàm vi phân Sobel Gx, Gy và độ lớn Gradient M(x,y) thuần NumPy.

    Cơ sở lý thuyết (Slide Chương 5 - Tách biên ảnh, TS. Phan Thanh Toàn, P18):
        Toán tử vi phân Sobel xấp xỉ đạo hàm riêng bậc nhất theo 2 phương trực giao:
        - Nhân chập theo phương ngang (Gx):
              S_x = [[-1, 0, 1],
                     [-2, 0, 2],
                     [-1, 0, 1]]
        - Nhân chập theo phương dọc (Gy):
              S_y = [[-1, -2, -1],
                     [ 0,  0,  0],
                     [ 1,  2,  1]]

        Độ lớn Gradient vi phân:
              M(x, y) = \sqrt{G_x^2(x, y) + G_y^2(x, y)}

    Đặc tính kỹ thuật:
        - Sử dụng cơ chế phản xạ đối xứng qua biên (np.pad mode='reflect' tức reflect_101).
        - Đạt độ chính xác tương đương tuyệt đối (Max Error = 0.00, MSE = 0.00) so với hàm
          cv2.Sobel(image, cv2.CV_64F, ..., borderType=cv2.BORDER_DEFAULT).

    Tham số:
    ---------
    image : np.ndarray
        Ảnh mức xám 2D (uint8 hoặc float64).

    Trả về:
    -------
    gx : np.ndarray
        Đạo hàm vi phân theo phương ngang dI/dx (float64).
    gy : np.ndarray
        Đạo hàm vi phân theo phương dọc dI/dy (float64).
    grad_mag : np.ndarray
        Độ lớn vector Gradient M(x, y) (float64).
    """
    img_f = image.astype(np.float64)
    h, w = img_f.shape

    # Padding phản xạ đối xứng (reflect_101)
    padded = np.pad(img_f, 1, mode="reflect")

    # Vector hóa nhân chập Sobel Gx
    gx = (
        -1.0 * padded[0:h, 0:w] + 1.0 * padded[0:h, 2 : w + 2]
        - 2.0 * padded[1 : h + 1, 0:w] + 2.0 * padded[1 : h + 1, 2 : w + 2]
        - 1.0 * padded[2 : h + 2, 0:w] + 1.0 * padded[2 : h + 2, 2 : w + 2]
    )

    # Vector hóa nhân chập Sobel Gy
    gy = (
        -1.0 * padded[0:h, 0:w] - 2.0 * padded[0:h, 1 : w + 1] - 1.0 * padded[0:h, 2 : w + 2]
        + 1.0 * padded[2 : h + 2, 0:w] + 2.0 * padded[2 : h + 2, 1 : w + 1] + 1.0 * padded[2 : h + 2, 2 : w + 2]
    )

    grad_mag = np.sqrt(gx**2 + gy**2)

    return gx, gy, grad_mag


def extract_blob_features(
    image: np.ndarray,
    blob_mask: np.ndarray,
    boundary_mask: np.ndarray = None,
    all_dark_mask: np.ndarray = None,
    annulus_ksize: int = 15,
    precomputed_grad_mag: np.ndarray = None,
) -> dict:
    r"""
    Trích xuất toàn diện 4 nhóm đặc trưng vật lý và hình học của đốm tối SAR:

    1. Diện tích (Area):
       Tổng số pixel thuộc thân đốm: A = \sum \mathbb{I}(blob\_mask > 0).

    2. Chu vi (Perimeter):
       Tổng số pixel trên đường biên hình thái học \beta(A): P = \sum \mathbb{I}(\beta(A) > 0).

    3. Độ thuôn dài (Elongation = MajorAxis / MinorAxis):
       Tính từ ma trận hiệp phương sai của tọa độ các điểm ảnh đốm (Moment quán tính bậc 2):
       - Trục chính: MajorAxis = 4 \sqrt{\lambda_1}
       - Trục phụ: MinorAxis = 4 \sqrt{\lambda_2}
       - Elongation = \sqrt{\lambda_1 / (\lambda_2 + \epsilon)}
       Ý nghĩa vật lý: Vết dầu loang do tàu thuyền xả thải khi hành trình thường kéo dài
       dạng dải mỏng ngoằn ngoèo (Elongation >> 2.0), trong khi vùng gió lặng dạng mảng bè rộng.

    4. Độ phức tạp biên (Boundary Complexity / Circularity):
       C = P^2 / (4 \pi A).
       Ý nghĩa vật lý: Vết dầu thực tế bị tác động cơ học của sóng và dòng hải lưu xé nhỏ,
       gây viền gồ ghề răng cưa phức tạp (C >= 1.5 - 2.5), khác với màng gió mượt mà.

    5. Độ dốc Gradient ranh giới (Border Gradient Sharpness):
       \overline{G}_{border} = (1 / |\beta(A)|) \sum_{(x,y) \in \beta(A)} M(x, y).
       Ý nghĩa vật lý: Sức căng bề mặt của màng dầu (hiệu ứng Marangoni) ngăn cách với
       nước biển tạo bước nhảy tán xạ dốc và sắc nhọn (\overline{G}_{border} >= 6.0),
       trong khi ranh giới vùng gió giảm mờ thoai thoải do tán xạ biến thiên liên tục.

    6. Độ tương phản vành đai lân cận (Annulus Background Contrast) & Hệ số tắt dần (Damping Ratio):
       Tạo vành đai biển bao quanh bằng phép dãn hình thái custom_dilate trừ đi đốm dầu:
       \Delta \mu = \mu_{bg} - \mu_{slick}
       Damping Ratio = \mu_{bg} / (\mu_{slick} + \epsilon)
       Ý nghĩa vật lý: Vết dầu dập tắt sóng mao dẫn cực mạnh, làm tín hiệu tán xạ ngược
       giảm sâu (\Delta \mu >= 12.0 mức xám, Damping Ratio >= 1.35).

    Tham số:
    ---------
    image : np.ndarray
        Ảnh SAR đầu vào (grayscale 2D).
    blob_mask : np.ndarray
        Mặt nạ nhị phân của riêng đốm cần trích xuất (uint8: 0 và 255).
    boundary_mask : np.ndarray, optional
        Mặt nạ biên đơn pixel \beta(A). Nếu None, tự động trích xuất bằng custom_extract_boundary.
    all_dark_mask : np.ndarray, optional
        Mặt nạ toàn bộ các đốm tối trên ảnh để loại trừ khỏi vùng vành đai nước biển sạch.
    annulus_ksize : int
        Kích thước kernel dãn để tạo vành đai bao quanh (mặc định 15 pixel).
    precomputed_grad_mag : np.ndarray, optional
        Ma trận độ lớn gradient Sobel đã tính sẵn để tăng tốc xử lý nhiều đốm.

    Trả về:
    -------
    features : dict
        Bảng từ điển chứa các tham số hình học và vật lý định lượng.
    """
    img_f = image.astype(np.float64)
    h, w = img_f.shape

    # 1. Trích xuất đường biên nếu chưa có
    if boundary_mask is None:
        boundary_mask = custom_extract_boundary(blob_mask, ksize=3)

    # 2. Diện tích và Chu vi
    area = float(np.sum(blob_mask > 0))
    perimeter = float(np.sum(boundary_mask > 0))

    if area == 0:
        return {
            "area": 0.0,
            "perimeter": 0.0,
            "elongation": 1.0,
            "major_axis": 0.0,
            "minor_axis": 0.0,
            "boundary_complexity": 1.0,
            "mean_slick": 0.0,
            "mean_bg": 0.0,
            "contrast_diff": 0.0,
            "damping_ratio": 1.0,
            "border_gradient": 0.0,
            "centroid": (0.0, 0.0),
        }

    # 3. Tính độ thuôn dài từ moment trung tâm bậc 2 của tọa độ các pixel
    rows, cols = np.where(blob_mask > 0)
    cr = float(np.mean(rows))
    cc = float(np.mean(cols))

    dr = rows - cr
    dc = cols - cc

    # Central moments: mu20 (variance X), mu02 (variance Y), mu11 (covariance XY)
    mu20 = float(np.mean(dc**2))
    mu02 = float(np.mean(dr**2))
    mu11 = float(np.mean(dr * dc))

    # Eigenvalues của ma trận hiệp phương sai 2x2
    common_term = np.sqrt((mu20 - mu02) ** 2 + 4.0 * (mu11**2))
    l1 = max(0.0, (mu20 + mu02 + common_term) / 2.0)
    l2 = max(0.0, (mu20 + mu02 - common_term) / 2.0)

    major_axis = 4.0 * np.sqrt(l1)
    minor_axis = 4.0 * np.sqrt(l2)
    elongation = float(np.sqrt(l1 / (l2 + 1e-6)))

    # 4. Độ phức tạp biên (Boundary Complexity)
    complexity = float((perimeter**2) / (4.0 * np.pi * area + 1e-6))

    # 5. Cường độ vệt dầu và Cường độ nền biển lân cận (Annulus Ring)
    mean_slick = float(np.mean(img_f[blob_mask > 0]))

    # Tạo vành đai bằng phép dãn nở
    dilated_blob = custom_dilate(blob_mask, ksize=annulus_ksize, se=None)
    annulus_mask = (dilated_blob > 0) & (blob_mask == 0)

    # Loại trừ các đốm tối khác nếu có
    if all_dark_mask is not None:
        annulus_mask = annulus_mask & (all_dark_mask == 0)

    annulus_pixels = img_f[annulus_mask]
    if len(annulus_pixels) > 0:
        mean_bg = float(np.mean(annulus_pixels))
    else:
        # Nếu không có pixel vành đai (ví dụ chạm viền hoàn toàn), lấy trung bình ngoài đốm
        non_blob = img_f[blob_mask == 0]
        mean_bg = float(np.mean(non_blob)) if len(non_blob) > 0 else float(np.mean(img_f))

    contrast_diff = float(mean_bg - mean_slick)
    damping_ratio = float(mean_bg / (mean_slick + 1e-6))

    # 6. Độ dốc Gradient ranh giới (Border Gradient Sharpness)
    if precomputed_grad_mag is not None:
        grad_mag = precomputed_grad_mag
    else:
        _, _, grad_mag = custom_sobel_gradient(image)

    border_vals = grad_mag[boundary_mask > 0]
    border_grad_sharpness = float(np.mean(border_vals)) if len(border_vals) > 0 else 0.0

    return {
        "area": area,
        "perimeter": perimeter,
        "elongation": elongation,
        "major_axis": float(major_axis),
        "minor_axis": float(minor_axis),
        "boundary_complexity": complexity,
        "mean_slick": mean_slick,
        "mean_bg": mean_bg,
        "contrast_diff": contrast_diff,
        "damping_ratio": damping_ratio,
        "border_gradient": border_grad_sharpness,
        "centroid": (cr, cc),
    }


def classify_candidate(
    features: dict,
    min_area: int = 120,
    max_area: int = 25000,
    min_contrast: float = 10.0,
    min_damping: float = 1.25,
    min_gradient: float = 5.0,
    min_elongation: float = 1.8,
    min_complexity: float = 1.6,
    scene_mean: float = None,
    scene_dark_ratio: float = None,
    max_dark_ratio: float = 0.25,
    total_scene_blobs: int = None,
    max_scene_blobs: int = 10,
) -> tuple[bool, str, dict]:
    """
    Phân loại đốm tối ứng viên: Vết dầu tràn thực tế (True Oil Slick)
    hay Vùng tối tương tự dầu / Hiện tượng thiên nhiên (Look-alike: Gió lặng, màng sinh học...).

    Cơ sở quy tắc Heuristic dựa trên đặc trưng viễn thám SAR:
    -------------------------------------------------------
    1. Tiêu chí Toàn cảnh SAR (Scene-Level Physics Context):
       - Mức xám trung bình toàn ảnh (scene_mean): Nếu scene_mean < 45.0, mặt biển phẳng lặng
         hoàn toàn như một tấm gương phản xạ (Specular reflection), tín hiệu tán xạ ngược
         suy giảm diện rộng không thể có vết dầu cô lập.
       - Tỉ lệ diện tích tối toàn cảnh (scene_dark_ratio): Vết dầu tràn chỉ chiếm một tỉ lệ
         nhỏ trên diện tích đại dương (thường 0.5% - 15%). Nếu scene_dark_ratio > 0.25 (25% khung ảnh),
         đó là hiện tượng gió lặng quy mô vùng rộng (Low Wind Field) hoặc vùng bóng râm địa hình.
       - Mật độ đốm tối (total_scene_blobs): Nếu số lượng đốm tối rải rác vượt quá max_scene_blobs (ví dụ > 10),
         đây là hiện tượng sóng biển xao động / bọt biển vò nát phân tán, không phải vệt dầu tràn tập trung.
    2. Tiêu chí Diện tích (Area):
       - Loại bỏ các chấm nhiễu đốm nhỏ, bọt sóng (Area < min_area).
       - Loại bỏ các mảng gió lặng khí quyển bao trùm diện rộng (Area > max_area).
    3. Tiêu chí Tương phản & Tắt sóng (Contrast & Damping):
       - Vết dầu thực tế làm tắt hẳn sóng mao dẫn, tạo độ tương phản sâu với nền biển lân cận:
         contrast_diff >= min_contrast HOẶC damping_ratio >= min_damping.
    4. Tiêu chí Gradient ranh giới (Border Gradient Sharpness):
       - Sức căng bề mặt của màng dầu tạo ranh giới sắc nét:
         border_gradient >= min_gradient (mức xám/pixel).
    5. Tiêu chí Hình thái học (Elongation & Complexity):
       - Dầu xả từ tàu thuyền có dạng vệt dài ngoằn ngoèo (elongation >= min_elongation)
         HOẶC bị sóng vò tạo mép răng cưa (boundary_complexity >= min_complexity).

    Tham số:
    ---------
    features : dict
        Bảng từ điển đặc trưng do extract_blob_features trả về.
    min_area : int
        Diện tích tối thiểu (pixel). Mặc định 120.
    max_area : int
        Diện tích tối đa (pixel). Mặc định 25000.
    min_contrast : float
        Độ chênh lệch mức xám tối thiểu với nền vành đai. Mặc định 10.0.
    min_damping : float
        Hệ số tắt dần sóng (Damping ratio) tối thiểu. Mặc định 1.25.
    min_gradient : float
        Độ dốc gradient biên tối thiểu. Mặc định 5.0.
    min_elongation : float
        Độ thuôn dài tối thiểu. Mặc định 1.8.
    min_complexity : float
        Độ phức tạp biên tối thiểu. Mặc định 1.6.
    scene_mean : float, optional
        Mức xám trung bình toàn cảnh của ảnh SAR.
    scene_dark_ratio : float, optional
        Tỉ lệ diện tích toàn bộ các đốm tối trên toàn khung ảnh (0.0 đến 1.0).
    max_dark_ratio : float
        Ngưỡng tỉ lệ tối tối đa toàn cảnh (mặc định 0.25 tức 25%).
    total_scene_blobs : int, optional
        Tổng số lượng đốm tối tìm thấy trên toàn khung ảnh.
    max_scene_blobs : int
        Ngưỡng mật độ đốm tối tối đa trên cảnh (mặc định 10).

    Trả về:
    -------
    is_oil : bool
        True nếu đốm là vệt dầu tràn thực tế, False nếu là Look-alike hoặc nhiễu.
    label : str
        Nhãn phân loại chuỗi: 'Oil Slick', 'Look-alike (Wide Low-Wind Field)', 'Ocean Wave Clutter', 'Speckle Noise', hoặc 'Look-alike (Low Wind/Bio)'.
    decision_details : dict
        Chi tiết các tiêu chí kiểm tra logic để phục vụ giải thích kết quả.
    """
    # 1. Kiểm tra ngữ cảnh toàn cảnh
    if scene_mean is not None and scene_mean < 45.0:
        return False, "Look-alike (Wide Low-Wind Field)", {
            "pass_scene_mean": False,
            "scene_mean": scene_mean,
            "reason": "Mặt biển phẳng lặng toàn cảnh (scene_mean < 45.0)"
        }

    if scene_dark_ratio is not None and scene_dark_ratio > max_dark_ratio:
        return False, "Look-alike (Wide Low-Wind Field)", {
            "pass_dark_ratio": False,
            "scene_dark_ratio": scene_dark_ratio,
            "reason": f"Tỉ lệ tối toàn cảnh quá lớn ({scene_dark_ratio*100:.1f}% > {max_dark_ratio*100:.0f}%)"
        }

    if total_scene_blobs is not None and total_scene_blobs > max_scene_blobs:
        return False, "Ocean Wave Clutter", {
            "pass_blob_density": False,
            "total_scene_blobs": total_scene_blobs,
            "reason": f"Mật độ đốm tối quá dày đặc ({total_scene_blobs} > {max_scene_blobs}) do sóng biển xao động"
        }

    area = features.get("area", 0.0)
    contrast = features.get("contrast_diff", 0.0)
    damping = features.get("damping_ratio", 1.0)
    grad = features.get("border_gradient", 0.0)
    elongation = features.get("elongation", 1.0)
    complexity = features.get("boundary_complexity", 1.0)

    pass_area_min = bool(area >= min_area)
    pass_area_max = bool(area <= max_area)
    pass_contrast = bool(contrast >= min_contrast or damping >= min_damping)
    pass_gradient = bool(grad >= min_gradient)
    pass_shape = bool(elongation >= min_elongation or complexity >= min_complexity)

    decision_details = {
        "pass_area_min": pass_area_min,
        "pass_area_max": pass_area_max,
        "pass_contrast": pass_contrast,
        "pass_gradient": pass_gradient,
        "pass_shape": pass_shape,
        "area_val": area,
        "contrast_val": contrast,
        "damping_val": damping,
        "gradient_val": grad,
        "elongation_val": elongation,
        "complexity_val": complexity,
    }

    if not pass_area_min:
        return False, "Speckle Noise", decision_details

    if not pass_area_max:
        return False, "Look-alike (Wide Low-Wind Field)", decision_details

    if pass_contrast and pass_gradient and pass_shape:
        return True, "Oil Slick", decision_details
    else:
        return False, "Look-alike (Low Wind/Bio)", decision_details
