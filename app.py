"""
HỆ THỐNG PHÁT HIỆN VẾT DẦU TRÀN TRÊN BIỂN TỪ ẢNH SAR SENTINEL-1
Giao diện Web tương tác Streamlit (Demo chuẩn CDIO - Đại học Giao thông Vận tải)
Giảng viên hướng dẫn: TS. Phan Thanh Toàn
Đề tài 18: Phát hiện vết dầu tràn trên biển từ ảnh SAR (NASA #6)
Chủ trì phát triển: TV1 — Trưởng nhóm & Tích hợp hệ thống
"""

import time
import os
import glob
import cv2
import numpy as np
import streamlit as st
import matplotlib.pyplot as plt

# Thiết lập cấu hình trang Streamlit
st.set_page_config(
    page_title="Phát hiện dầu tràn SAR - UTC",
    page_icon="🌊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Tùy biến CSS giao diện
st.markdown("""
<style>
    .main-title {
        font-size: 28px;
        color: #0b3954;
        font-weight: 700;
        text-align: center;
        margin-bottom: 5px;
    }
    .sub-title {
        font-size: 16px;
        color: #415a77;
        text-align: center;
        margin-bottom: 25px;
    }
    .metric-card {
        background-color: #f8f9fa;
        border-radius: 8px;
        padding: 15px;
        border-left: 5px solid #0077b6;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .alert-oil {
        background-color: #ffe5d9;
        color: #9d0208;
        padding: 12px;
        border-radius: 6px;
        font-weight: 600;
        border-left: 5px solid #d00000;
    }
    .alert-clean {
        background-color: #d8f3dc;
        color: #1b4332;
        padding: 12px;
        border-radius: 6px;
        font-weight: 600;
        border-left: 5px solid #2d6a4f;
    }
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------------------
# THUẬT TOÁN XỬ LÝ ẢNH CHUẨN GIÁO TRÌNH TS. PHAN THANH TOÀN
# -------------------------------------------------------------

def run_pipeline(
    image: np.ndarray,
    ksize: int = 5,
    min_area: int = 150,
    max_area: int = 120000,
    min_contrast: float = 12.0,
    min_boundary_grad: float = 6.0,
    min_otsu_separability: float = 0.10,
    border_thickness: int = 2
):
    """
    Pipeline 4 bước tuần tự:
    Bước 1: Lọc trung vị khử nhiễu speckle (Chương 3)
    Bước 2: Phân ngưỡng Otsu tối ưu & tính eta (Chương 7)
    Bước 3: Hình thái học Opening, Closing, Fill holes, trích biên beta(A) (Chương 6)
    Bước 4: Đạo hàm Sobel & tương phản vành đai (Chương 5)
    """
    start_time = time.time()
    
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        vis_img = image.copy()
    else:
        gray = image.copy()
        vis_img = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)

    # BƯỚC 1: Lọc trung vị
    filtered = cv2.medianBlur(gray, ksize)

    # BƯỚC 2: Phân ngưỡng Otsu tối ưu & hệ số khả tách eta
    hist = cv2.calcHist([filtered], [0], None, [256], [0, 256]).ravel()
    total_pixels = filtered.size
    p = hist / total_pixels
    
    omega = np.cumsum(p)
    mu = np.cumsum(p * np.arange(256))
    mu_t = mu[-1]
    sigma_t_sq = np.sum(((np.arange(256) - mu_t) ** 2) * p)
    
    denominator = omega * (1.0 - omega)
    numerator = (mu_t * omega - mu) ** 2
    sigma_b_sq = np.zeros(256)
    valid_idx = denominator > 1e-9
    sigma_b_sq[valid_idx] = numerator[valid_idx] / denominator[valid_idx]
    
    optimal_t = int(np.argmax(sigma_b_sq))
    separability = float(sigma_b_sq[optimal_t] / sigma_t_sq) if sigma_t_sq > 1e-6 else 0.0

    # Nếu tính khả tách quá kém -> biển sạch
    if separability < min_otsu_separability:
        latency = (time.time() - start_time) * 1000
        return vis_img, filtered, np.zeros_like(gray), [], separability, optimal_t, latency

    # Mặt nạ đốm tối nhị phân (pixel <= optimal_t)
    _, initial_mask = cv2.threshold(filtered, optimal_t, 255, cv2.THRESH_BINARY_INV)

    # BƯỚC 3: Hình thái học
    se_open = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    se_close = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
    opened = cv2.morphologyEx(initial_mask, cv2.MORPH_OPEN, se_open)
    closed = cv2.morphologyEx(opened, cv2.MORPH_CLOSE, se_close)
    
    # Fill holes
    h, w = closed.shape
    padded = cv2.copyMakeBorder(closed, 1, 1, 1, 1, cv2.BORDER_CONSTANT, value=0)
    mask_ff = np.zeros((h + 4, w + 4), np.uint8)
    cv2.floodFill(padded, mask_ff, (0, 0), 255)
    filled = closed | cv2.bitwise_not(padded[1:-1, 1:-1])

    # BƯỚC 4: Đánh giá đặc trưng & Vẽ viền đỏ
    num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(filled, connectivity=8)
    
    # Sobel Gradient (Chương 5)
    gx = cv2.Sobel(filtered, cv2.CV_32F, 1, 0, ksize=3)
    gy = cv2.Sobel(filtered, cv2.CV_32F, 0, 1, ksize=3)
    grad_mag = cv2.magnitude(gx, gy)
    
    final_oil_mask = np.zeros_like(gray)
    detections = []
    se_annulus = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
    se_boundary = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))

    for l in range(1, num_labels):
        area = int(stats[l, cv2.CC_STAT_AREA])
        if area < min_area or area > max_area:
            continue
            
        blob_mask = np.zeros_like(gray)
        blob_mask[labels == l] = 255
        
        # Trích biên hình thái học: beta(A) = A - (A (-) B)
        eroded = cv2.erode(blob_mask, se_boundary)
        blob_boundary = cv2.subtract(blob_mask, eroded)
        
        # Tương phản vành đai
        dilated = cv2.dilate(blob_mask, se_annulus)
        annulus = cv2.subtract(dilated, blob_mask)
        
        sea_pixels = filtered[annulus > 0]
        oil_pixels = filtered[blob_mask > 0]
        
        mean_sea = float(np.mean(sea_pixels)) if len(sea_pixels) > 0 else 0.0
        mean_oil = float(np.mean(oil_pixels)) if len(oil_pixels) > 0 else 0.0
        contrast = mean_sea - mean_oil
        
        # Gradient biên
        border_grad_pixels = grad_mag[blob_boundary > 0]
        mean_grad = float(np.mean(border_grad_pixels)) if len(border_grad_pixels) > 0 else 0.0
        
        # Tiêu chuẩn vết dầu vật lý
        if contrast >= min_contrast and mean_grad >= min_boundary_grad:
            final_oil_mask[blob_mask == 255] = 255
            detections.append({
                "id": len(detections) + 1,
                "area": area,
                "contrast": round(contrast, 2),
                "mean_gradient": round(mean_grad, 2),
                "centroid": (int(centroids[l][0]), int(centroids[l][1]))
            })

    # Vẽ viền ĐỎ ôm sát vết dầu
    if np.sum(final_oil_mask) > 0:
        eroded_total = cv2.erode(final_oil_mask, se_boundary)
        total_boundary = cv2.subtract(final_oil_mask, eroded_total)
        if border_thickness > 1:
            k_thick = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (border_thickness, border_thickness))
            total_boundary = cv2.dilate(total_boundary, k_thick)
        
        # Tránh mép ảnh
        total_boundary[0:2, :] = 0
        total_boundary[-2:, :] = 0
        total_boundary[:, 0:2] = 0
        total_boundary[:, -2:] = 0
        
        vis_img[total_boundary > 0] = [0, 0, 255] # BGR Red

    latency = (time.time() - start_time) * 1000
    return vis_img, filtered, final_oil_mask, detections, separability, optimal_t, latency


# -------------------------------------------------------------
# GIAO DIỆN CHÍNH
# -------------------------------------------------------------

st.markdown('<div class="main-title">🌊 HỆ THỐNG PHÁT HIỆN VẾT DẦU TRÀN TỪ ẢNH SAR SENTINEL-1</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Bộ môn Khoa học Máy tính — Khoa CNTT — Đại học Giao thông Vận tải (UTC) | GVHD: TS. Phan Thanh Toàn</div>', unsafe_allow_html=True)

# SIDEBAR: Điều khiển
st.sidebar.header("⚙️ BẢNG ĐIỀU KHIỂN THAM SỐ")

input_mode = st.sidebar.radio("Nguồn ảnh đầu vào:", ["Chọn từ thư viện mẫu (Sample)", "Tải ảnh từ máy tính (Upload)"])

input_image = None
image_name = ""

if input_mode == "Chọn từ thư viện mẫu (Sample)":
    sample_options = []
    # Quét ảnh mẫu trong data/sample hoặc outputs_slide
    sample_files = glob.glob("data/sample/**/*.jpg", recursive=True) + glob.glob("outputs_slide/**/*.jpg", recursive=True)
    if not sample_files:
        sample_files = glob.glob("data/**/*.jpg", recursive=True)[:20]
    
    if sample_files:
        selected_file = st.sidebar.selectbox("Chọn ảnh kiểm thử:", sample_files)
        input_image = cv2.imread(selected_file)
        image_name = os.path.basename(selected_file)
    else:
        st.sidebar.warning("Không tìm thấy ảnh mẫu trong thư mục data/")
else:
    uploaded_file = st.sidebar.file_uploader("Tải lên ảnh SAR (.jpg, .png, .tif):", type=["jpg", "jpeg", "png", "tif"])
    if uploaded_file is not None:
        file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
        input_image = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
        image_name = uploaded_file.name

st.sidebar.markdown("---")
st.sidebar.subheader("⚙️ Động cơ Thuật toán")
engine_choice = st.sidebar.radio(
    "Lựa chọn động cơ xử lý:",
    ["100% Thuần NumPy (Tự code chuẩn CDIO BTL)", "OpenCV (Đối chiếu thư viện)"]
)

st.sidebar.markdown("---")
st.sidebar.subheader("Tham số thuật toán CV")
ksize = st.sidebar.select_slider("Kernel lọc trung vị (px):", options=[3, 5, 7], value=5)
min_area = st.sidebar.slider("Diện tích tối thiểu (px):", min_value=50, max_value=3000, value=150, step=50)
min_contrast = st.sidebar.slider("Độ tương phản tối thiểu (Δμ):", min_value=5.0, max_value=35.0, value=12.0, step=1.0)
min_boundary_grad = st.sidebar.slider("Gradient biên tối thiểu (Sobel):", min_value=2.0, max_value=20.0, value=6.0, step=0.5)
min_otsu_eta = st.sidebar.slider("Hệ số khả tách Otsu tối thiểu (η):", min_value=0.05, max_value=0.40, value=0.10, step=0.01)
border_thickness = st.sidebar.slider("Độ dày đường viền đỏ (px):", min_value=1, max_value=4, value=2)

# Tabs hiển thị
tab1, tab2, tab3 = st.tabs(["🔍 Trực quan hóa 4 bước", "📐 Cơ sở toán học", "👥 Thông tin nhóm & CDIO"])

with tab1:
    if input_image is not None:
        # Chạy pipeline theo động cơ đã chọn
        from src.pipeline_numpy import detect_oil_spill_numpy
        
        if "NumPy" in engine_choice:
            vis_bgr, filtered_gray, oil_mask, detections, meta = detect_oil_spill_numpy(
                input_image,
                ksize_filter=ksize,
                min_area=min_area,
                min_contrast=min_contrast,
                min_boundary_grad=min_boundary_grad,
                min_otsu_separability=min_otsu_eta,
                border_thickness=border_thickness
            )
            latency = meta["total_ms"]
            optimal_t = meta["optimal_t"]
            eta = meta["eta"]
            engine_badge = "🔥 100% NumPy Thuần túy (Không hộp đen)"
        else:
            vis_bgr, filtered_gray, oil_mask, detections, eta, optimal_t, latency = run_pipeline(
                input_image,
                ksize=ksize,
                min_area=min_area,
                min_contrast=min_contrast,
                min_boundary_grad=min_boundary_grad,
                min_otsu_separability=min_otsu_eta,
                border_thickness=border_thickness
            )
            engine_badge = "⚡ OpenCV Thư viện đối chiếu"
        
        vis_rgb = cv2.cvtColor(vis_bgr, cv2.COLOR_BGR2RGB)
        orig_rgb = cv2.cvtColor(input_image, cv2.COLOR_BGR2RGB)

        # Trạng thái kết luận
        st.markdown("### 1. Trạng thái kết luận phân loại")
        col_status, col_time = st.columns([3, 1])
        with col_status:
            if len(detections) > 0:
                st.markdown(f'<div class="alert-oil">🚨 CẢNH BÁO: PHÁT HIỆN {len(detections)} VẾT DẦU TRÀN NGUY HIỂM NGOÀI KHƠI!</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="alert-clean">✅ AN TOÀN: KHÔNG PHÁT HIỆN VẾT DẦU (Mặt biển sạch hoặc vùng gió lặng đã được loại trừ thành công)</div>', unsafe_allow_html=True)
        with col_time:
            st.metric("Thời gian xử lý", f"{latency:.1f} ms", f"{1000/latency:.1f} FPS")

        st.markdown("---")
        st.markdown("### 2. Trực quan hóa quy trình 4 bước tuần tự")
        
        col1, col2 = st.columns(2)
        with col1:
            st.image(orig_rgb, caption="Bước 0: Ảnh Radar SAR Sentinel-1 gốc (400x400)", use_container_width=True)
            st.image(oil_mask, caption="Bước 3: Mặt nạ nhị phân sau Otsu & Hình thái học", use_container_width=True, clamp=True)
        with col2:
            st.image(filtered_gray, caption=f"Bước 1: Ảnh sau lọc trung vị (k={ksize}px) khử nhiễu speckle", use_container_width=True, clamp=True)
            st.image(vis_rgb, caption="Bước 4: Kết quả phát hiện ôm sát vết dầu bằng viền ĐỎ", use_container_width=True)

        if detections:
            st.markdown("---")
            st.markdown("### 3. Bảng đo đạc định lượng các vết dầu phát hiện được")
            st.dataframe(detections, use_container_width=True)
            
    else:
        st.info("Vui lòng chọn hoặc tải lên một ảnh radar SAR từ thanh bên trái để bắt đầu phân tích!")

with tab2:
    st.markdown("""
    ### TỔNG HỢP CÔNG THỨC TOÁN HỌC TRỌNG TÂM (TS. PHAN THANH TOÀN)
    
    1. **Khử nhiễu đốm đục hạt (Speckle Noise - Chương 3, Trang 104-106):**
       - Lọc trung vị 2D bảo toàn đường biên:
         $$\\hat{I}(x,y) = \\text{median}\\{I(x+i, y+j) \\mid (i,j) \\in W\\}$$
    2. **Phân ngưỡng Otsu tối ưu & Hệ số khả tách (Chương 7, Trang 48-55):**
       - Tối đa hóa phương sai liên lớp:
         $$\\sigma_B^2(t) = \\frac{[\\mu_T \\omega_0(t) - \\mu(t)]^2}{\\omega_0(t)(1 - \\omega_0(t))}, \\quad T^* = \\arg\\max \\sigma_B^2(t)$$
       - Hệ số khả tách: $\\eta = \\frac{\\sigma_B^2(T^*)}{\\sigma_T^2} \\ge 0.10$
    3. **Toán tử trích biên hình thái học (Chương 6, Trang 16):**
       $$\\beta(A) = A - (A \\ominus B)$$
    4. **Độ dốc Gradient biên Sobel (Chương 5, Trang 36-40):**
       $$M(x,y) = \\sqrt{G_x^2 + G_y^2} \\ge 6.0$$
    5. **Độ tương phản vành đai lân cận (Annulus Contrast):**
       $$\\Delta \\mu = \\mu_{\\text{sea}} - \\mu_{\\text{oil}} \\ge 12.0$$
    """)

with tab3:
    st.markdown("""
    ### THÔNG TIN NHÓM THỰC HIỆN ĐỀ TÀI (ĐẠI HỌC GIAO THÔNG VẬN TẢI)
    
    - **Học phần:** Xử lý ảnh (Computer Vision)
    - **Giảng viên hướng dẫn:** TS. Phan Thanh Toàn
    - **Đề tài số 18:** Phát hiện vết dầu tràn trên biển từ ảnh SAR (★★★) — NASA #6
    
    | Vai trò | Phụ trách chính | Nhiệm vụ kỹ thuật |
    | :---: | :--- | :--- |
    | **TV1** | *Trưởng nhóm, Tích hợp* | Quản lý dự án, Repo Git, Kiến trúc mã, Streamlit Web App, Chương 1 & 5 |
    | **TV2** | *Lý thuyết, Kiểm chứng* | Dẫn xuất công thức, Ví dụ tính tay 5x5, Kiểm chứng so với OpenCV, Chương 2 |
    | **TV3** | *Cài đặt thuật toán 1* | Tự code thuần NumPy: Lọc trung vị, Box filter, Otsu tối ưu, Mục 3.2 |
    | **TV4** | *Cài đặt thuật toán 2* | Tự code thuần NumPy: Hình thái học, Trích biên β(A), 4 đặc trưng, Mục 3.3 |
    | **TV5** | *Dữ liệu, Thực nghiệm* | Benchmark 5,630 ảnh CSIRO Sentinel-1, Tính Precision/Recall/F1, Chương 4 |
    """)
