"""
Module Xử lý Hình thái học (Mathematical Morphology) thuần NumPy 100%.
Phục vụ Đồ án Xử lý ảnh: Phát hiện vết dầu tràn trên ảnh SAR Sentinel-1 (CSIRO Dataset).
Bộ môn Kỹ thuật Máy tính - Trường Đại học Giao thông Vận tải (UTC).
Giảng viên hướng dẫn: TS. Phan Thanh Toàn.

Tác giả: TV4 - Thành viên phụ trách Thuật toán Hình thái học & Trích xuất đặc trưng vật lý.
Yêu cầu kỹ thuật: Tự lập trình 100% bằng NumPy thuần, không phụ thuộc hàm hình thái của OpenCV/scipy.
"""

import numpy as np
from collections import deque


def get_structuring_element(ksize: int = 3, se_type: str = "rect") -> np.ndarray:
    """
    Tạo phần tử cấu trúc (Structuring Element - SE) B bằng NumPy thuần.

    Tham số:
    ---------
    ksize : int
        Kích thước cạnh của lân cận (thường là số lẻ: 3, 5, 7, ...).
    se_type : str
        Loại hình học của phần tử cấu trúc:
        - 'rect' hoặc 'square': Ma trận toàn số 1 kích thước ksize x ksize.
        - 'disk' hoặc 'ellipse': Hình đĩa tròn bán kính r = ksize // 2.
        - 'cross': Hình dấu cộng (chữ thập) tâm tại (ksize // 2, ksize // 2).

    Trả về:
    -------
    se : np.ndarray
        Ma trận nhị phân 2D uint8 (chỉ gồm các giá trị 0 và 1).
    """
    if ksize % 2 == 0:
        raise ValueError(f"Kích thước kernel ksize phải là số lẻ, nhận được: {ksize}")

    r = ksize // 2
    if se_type.lower() in ("rect", "square"):
        return np.ones((ksize, ksize), dtype=np.uint8)

    elif se_type.lower() in ("disk", "ellipse"):
        y, x = np.ogrid[-r : r + 1, -r : r + 1]
        # Bán kính Euclid chuẩn: x^2 + y^2 <= r^2
        disk = ((x * x + y * y) <= (r * r)).astype(np.uint8)
        return disk

    elif se_type.lower() == "cross":
        cross = np.zeros((ksize, ksize), dtype=np.uint8)
        cross[r, :] = 1
        cross[:, r] = 1
        return cross

    else:
        raise ValueError(
            f"se_type không hợp lệ: '{se_type}'. Chọn trong ['rect', 'disk', 'cross']."
        )


def custom_erode(
    mask: np.ndarray, ksize: int = 3, se: np.ndarray = None
) -> np.ndarray:
    """
    Phép co nhị phân (Binary Erosion): A ⊖ B.

    Cơ sở lý thuyết (Slide Chương 6 - Xử lý hình thái, TS. Phan Thanh Toàn, P10):
        (A ⊖ B)(x, y) = 1 nếu và chỉ nếu B dịch chuyển đến (x, y) nằm hoàn toàn trong A.
        Biểu diễn logic: (A ⊖ B)(x, y) = ⋂_{(i,j) ∈ B, B[i,j]=1} A(x + i - r, y + j - c)

    Tối ưu hóa NumPy:
        Sử dụng phép dịch mảng (array shifting/slicing) kết hợp phép toán bitwise AND (np.bitwise_and).
        Xử lý biên: Sử dụng padding hằng số 255 (Max Border Value) để ngăn ngừa hiện tượng
        co mép giả tạo tại 4 đường biên của khung ảnh.

    Tham số:
    ---------
    mask : np.ndarray
        Ảnh nhị phân đầu vào (mức 0 và 255).
    ksize : int
        Kích thước kernel nếu phần tử cấu trúc se không được cung cấp trực tiếp.
    se : np.ndarray, optional
        Phần tử cấu trúc B (ma trận 0 và 1). Nếu None, mặc định là kernel vuông ksize x ksize.

    Trả về:
    -------
    eroded : np.ndarray
        Ảnh nhị phân sau phép co (cùng kiểu uint8 với mask).
    """
    if se is None:
        se = get_structuring_element(ksize, se_type="rect")

    kh, kw = se.shape
    pad_h = kh // 2
    pad_w = kw // 2
    h, w = mask.shape

    # Đệm biên bằng 255 để điểm biên không bị co giả tạo
    padded = np.pad(mask, ((pad_h, pad_h), (pad_w, pad_w)), mode="constant", constant_values=255)

    eroded = np.full((h, w), 255, dtype=mask.dtype)

    # Vector hóa: duyệt qua các điểm tích cực trong structuring element B
    for i in range(kh):
        for j in range(kw):
            if se[i, j] == 1:
                eroded = np.bitwise_and(eroded, padded[i : i + h, j : j + w])

    return eroded


def custom_dilate(
    mask: np.ndarray, ksize: int = 3, se: np.ndarray = None
) -> np.ndarray:
    """
    Phép dãn nhị phân (Binary Dilation): A ⊕ B.

    Cơ sở lý thuyết (Slide Chương 6 - Xử lý hình thái, TS. Phan Thanh Toàn, P13):
        (A ⊕ B)(x, y) = 1 nếu phần tử cấu trúc B đối xứng qua tâm có ít nhất một điểm giao với A.
        Biểu diễn logic: (A ⊕ B)(x, y) = ⋃_{(i,j) ∈ B, B[i,j]=1} A(x - i + r, y - j + c)

    Tối ưu hóa NumPy:
        Sử dụng phép dịch mảng lát cắt kết hợp phép toán bitwise OR (np.bitwise_or).
        Xử lý biên: Sử dụng padding hằng số 0 (Zero Border Value).

    Tham số:
    ---------
    mask : np.ndarray
        Ảnh nhị phân đầu vào (mức 0 và 255).
    ksize : int
        Kích thước kernel nếu se chưa được cấp.
    se : np.ndarray, optional
        Phần tử cấu trúc B. Mặc định là kernel vuông ksize x ksize.

    Trả về:
    -------
    dilated : np.ndarray
        Ảnh nhị phân sau phép dãn (uint8).
    """
    if se is None:
        se = get_structuring_element(ksize, se_type="rect")

    kh, kw = se.shape
    pad_h = kh // 2
    pad_w = kw // 2
    h, w = mask.shape

    # Đệm biên bằng 0
    padded = np.pad(mask, ((pad_h, pad_h), (pad_w, pad_w)), mode="constant", constant_values=0)

    dilated = np.zeros((h, w), dtype=mask.dtype)

    # Vì structuring element đối xứng qua tâm: B(-i, -j) = B(kh - 1 - i, kw - 1 - j)
    for i in range(kh):
        for j in range(kw):
            if se[i, j] == 1:
                # Dịch đối xứng qua tâm
                si = kh - 1 - i
                sj = kw - 1 - j
                dilated = np.bitwise_or(dilated, padded[si : si + h, sj : sj + w])

    return dilated


def custom_open(
    mask: np.ndarray, ksize: int = 3, se: np.ndarray = None
) -> np.ndarray:
    """
    Phép mở hình thái học (Morphological Opening): A ∘ B = (A ⊖ B) ⊕ B.

    Cơ sở lý thuyết (Slide Chương 6, P18):
        Thực hiện co trước (Erosion) rồi dãn sau (Dilation) với cùng phần tử cấu trúc B.
        Tác dụng trong giám sát dầu tràn:
        - Xóa bỏ các đốm nhiễu li ti (speckle noise dư thừa từ sóng biển).
        - Cắt đứt các eo kết nối giả tạo giữa vệt dầu và các đốm nhiễu nhỏ xung quanh.
        - Giữ nguyên kích thước và hình dáng tổng thể của các đốm vệt dầu lớn.

    Tham số:
    ---------
    mask : np.ndarray
        Ảnh nhị phân đầu vào.
    ksize : int
        Kích thước kernel (mặc định 3).
    se : np.ndarray, optional
        Phần tử cấu trúc.

    Trả về:
    -------
    opened : np.ndarray
        Ảnh nhị phân đã được lọc nhiễu cô lập.
    """
    if se is None:
        se = get_structuring_element(ksize, se_type="rect")
    eroded = custom_erode(mask, se=se)
    opened = custom_dilate(eroded, se=se)
    return opened


def custom_close(
    mask: np.ndarray, ksize: int = 5, se: np.ndarray = None
) -> np.ndarray:
    """
    Phép đóng hình thái học (Morphological Closing): A • B = (A ⊕ B) ⊖ B.

    Cơ sở lý thuyết (Slide Chương 6, P20):
        Thực hiện dãn trước (Dilation) rồi co sau (Erosion) với cùng phần tử cấu trúc B.
        Tác dụng trong giám sát dầu tràn:
        - Hàn gắn các vết rạn nứt, đứt gãy do nhiễu đốm radar gây suy hao tín hiệu không đều.
        - Nối liền các đoạn vệt dầu rời rạc thuộc cùng một dải trôi dạt.
        - Làm trơn tru các hốc khuyết hẹp trên thân vệt dầu.

    Tham số:
    ---------
    mask : np.ndarray
        Ảnh nhị phân đầu vào.
    ksize : int
        Kích thước kernel (mặc định 5).
    se : np.ndarray, optional
        Phần tử cấu trúc.

    Trả về:
    -------
    closed : np.ndarray
        Ảnh nhị phân đã được hàn gắn liên tục.
    """
    if se is None:
        se = get_structuring_element(ksize, se_type="rect")
    dilated = custom_dilate(mask, se=se)
    closed = custom_erode(dilated, se=se)
    return closed


def custom_fill_holes(mask: np.ndarray) -> np.ndarray:
    """
    Lấp đầy lỗ thủng (Hole Filling) bên trong thân đối tượng vệt dầu.

    Bản chất vật lý & Xử lý ảnh:
        Trong ảnh SAR, các bọt khí, mảnh sóng phản xạ cục bộ hoặc biến thiên độ nhám
        có thể tạo ra các "lỗ thủng" màu trắng (pixel 0) nằm lọt thỏm trong lòng đốm dầu đen (pixel 255).
        Cần lấp đầy các khoảng rỗng này để tính chính xác diện tích và moment hình học.

    Giải thuật NumPy thuần:
        - Định nghĩa: Lỗ thủng là tập hợp các điểm nền (giá trị 0) KHÔNG thông với 4 cạnh biên của ảnh.
        - Tiến hành duyệt đồ thị loang (BFS Flood-Fill) từ toàn bộ pixel biên (r=0, r=H-1, c=0, c=W-1).
        - Đánh dấu tập hợp các điểm nền liên thông với thế giới bên ngoài (Outer Sea Background).
        - Tất cả các pixel còn lại không thuộc Outer Background được kết luận là đối tượng (đã lấp kín lỗ thủng).

    Tham số:
    ---------
    mask : np.ndarray
        Ảnh nhị phân đầu vào (mức 0 và 255).

    Trả về:
    -------
    filled : np.ndarray
        Ảnh nhị phân với toàn bộ các lỗ thủng bên trong thân vệt dầu đã được lấp đầy.
    """
    h, w = mask.shape
    visited = np.zeros((h, w), dtype=bool)
    q = deque()

    # Bước 1: Khởi tạo hàng đợi BFS từ tất cả các điểm nền tại 4 cạnh biên của ảnh
    # Viền trên và viền dưới
    for c in range(w):
        if mask[0, c] == 0 and not visited[0, c]:
            visited[0, c] = True
            q.append((0, c))
        if mask[h - 1, c] == 0 and not visited[h - 1, c]:
            visited[h - 1, c] = True
            q.append((h - 1, c))

    # Viền trái và viền phải
    for r in range(h):
        if mask[r, 0] == 0 and not visited[r, 0]:
            visited[r, 0] = True
            q.append((r, 0))
        if mask[r, w - 1] == 0 and not visited[r, w - 1]:
            visited[r, w - 1] = True
            q.append((r, w - 1))

    # Bước 2: Loang 4-lân cận để tìm toàn bộ vùng nền nối thông ra biên ngoài
    while q:
        r, c = q.popleft()
        for nr, nc in ((r - 1, c), (r + 1, c), (r, c - 1), (r, c + 1)):
            if 0 <= nr < h and 0 <= nc < w:
                if not visited[nr, nc] and mask[nr, nc] == 0:
                    visited[nr, nc] = True
                    q.append((nr, nc))

    # Bước 3: Pixel nào thuộc visited chính là nền ngoài (Outer Sea -> 0).
    # Mọi pixel khác (gồm cả đối tượng gốc lẫn các lỗ thủng bị cô lập bên trong) trở thành 255.
    filled = np.where(visited, 0, 255).astype(np.uint8)
    return filled


def custom_extract_boundary(
    mask: np.ndarray, ksize: int = 3, se: np.ndarray = None
) -> np.ndarray:
    r"""
    Trích xuất đường biên hình thái học chuẩn toán học (Morphological Boundary Extraction).

    Cơ sở lý thuyết (Slide Chương 6 - Xử lý hình thái, TS. Phan Thanh Toàn, P16):
        \beta(A) = A - (A ⊖ B)
        Trong đó:
        - A: Tập hợp các điểm ảnh nhị phân thuộc đối tượng (mask == 255).
        - B: Phần tử cấu trúc (ksize x ksize, mặc định 3x3).
        - (A ⊖ B): Ảnh nhị phân sau khi co ngót một lớp vỏ ngoài.
        - Hiệu tập hợp \beta(A) biểu thị chính xác lớp vỏ biên đơn pixel ôm sát rìa đối tượng.

    Biểu diễn logic số:
        \beta(A)(x, y) = 255  nếu  A(x, y) == 255  và  (A ⊖ B)(x, y) == 0
        \beta(A)(x, y) = 0    ngược lại.

    Tham số:
    ---------
    mask : np.ndarray
        Mặt nạ nhị phân đốm dầu (uint8).
    ksize : int
        Kích thước kernel của phép co (mặc định 3 cho đường biên mỏng 1 pixel).
    se : np.ndarray, optional
        Phần tử cấu trúc tùy chọn.

    Trả về:
    -------
    boundary : np.ndarray
        Mặt nạ nhị phân của đường biên hình thái học \beta(A).
    """
    if se is None:
        se = get_structuring_element(ksize, se_type="rect")

    eroded = custom_erode(mask, se=se)

    # Hiệu tập hợp toán học chuẩn: A \ (A ⊖ B)
    boundary = np.zeros_like(mask)
    boundary[(mask == 255) & (eroded == 0)] = 255
    return boundary


def custom_connected_components(
    mask: np.ndarray, connectivity: int = 8, min_area: int = 50
) -> tuple[int, np.ndarray, list[dict]]:
    """
    Phân đoạn và gán nhãn thành phần liên thông (Connected Components) thuần NumPy.

    Thuật toán:
        Duyệt đồ thị loang (BFS) theo lân cận 4 hoặc 8, tách biệt từng đốm tối độc lập.
        Tự động sàng lọc loại bỏ các đốm nhiễu có diện tích nhỏ hơn `min_area`.

    Tham số:
    ---------
    mask : np.ndarray
        Mặt nạ nhị phân 2D (0 và 255).
    connectivity : int
        Số liên thông lân cận (4 hoặc 8, mặc định 8).
    min_area : int
        Ngưỡng diện tích tối thiểu (pixel) để giữ lại đốm ứng viên (mặc định 50).

    Trả về:
    -------
    num_valid_blobs : int
        Số lượng đốm tối hợp lệ được tìm thấy.
    labeled_mask : np.ndarray
        Ma trận gán nhãn int32 cùng kích thước, trong đó mỗi đốm mang nhãn 1, 2, ...
    blobs_info : list[dict]
        Danh sách thông tin của từng đốm:
        - 'label': Nhãn số nguyên của đốm.
        - 'area': Diện tích (số pixel).
        - 'coords': Mảng (N, 2) tọa độ (row, col) của các pixel trong đốm.
        - 'bbox': Hộp bao (min_r, min_c, max_r, max_c).
        - 'blob_mask': Mặt nạ nhị phân đơn lập của riêng đốm này (uint8: 0 và 255).
    """
    h, w = mask.shape
    labeled_mask = np.zeros((h, w), dtype=np.int32)
    visited = np.zeros((h, w), dtype=bool)

    if connectivity == 8:
        neighbors = ((-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1))
    else:
        neighbors = ((-1, 0), (1, 0), (0, -1), (0, 1))

    current_label = 0
    blobs_info = []

    for r in range(h):
        for c in range(w):
            if mask[r, c] > 0 and not visited[r, c]:
                # Khởi tạo loang BFS cho thành phần mới
                q = deque([(r, c)])
                visited[r, c] = True
                coords_list = [(r, c)]

                while q:
                    cr, cc = q.popleft()
                    for dr, dc in neighbors:
                        nr, nc = cr + dr, cc + dc
                        if 0 <= nr < h and 0 <= nc < w:
                            if mask[nr, nc] > 0 and not visited[nr, nc]:
                                visited[nr, nc] = True
                                q.append((nr, nc))
                                coords_list.append((nr, nc))

                # Kiểm tra diện tích đốm
                area = len(coords_list)
                if area >= min_area:
                    current_label += 1
                    coords_arr = np.array(coords_list, dtype=np.int32)
                    rows = coords_arr[:, 0]
                    cols = coords_arr[:, 1]

                    # Gán nhãn vào ma trận
                    labeled_mask[rows, cols] = current_label

                    # Tạo mặt nạ đơn lập cho đốm
                    b_mask = np.zeros((h, w), dtype=np.uint8)
                    b_mask[rows, cols] = 255

                    bbox = (int(np.min(rows)), int(np.min(cols)), int(np.max(rows)), int(np.max(cols)))

                    blobs_info.append({
                        "label": current_label,
                        "area": area,
                        "coords": coords_arr,
                        "bbox": bbox,
                        "blob_mask": b_mask,
                    })

    return current_label, labeled_mask, blobs_info
