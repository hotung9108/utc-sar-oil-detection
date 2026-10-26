"""
HỆ THỐNG PHÁT HIỆN VẾT DẦU TRÀN TỪ ẢNH SAR SENTINEL-1
Giao diện tối giản cao cấp (Minimalist Luxury) — Tập trung thuần túy vào xử lý và phân tích ảnh
Thư mục: web/app.py
"""

import os
import sys
import glob
import io
from pathlib import Path

# Đảm bảo đường dẫn gốc của project luôn nằm trong sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import cv2
import numpy as np
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

from src.pipeline_modular import run_modular_pipeline


# -----------------------------------------------------------------------------
# 1. CẤU HÌNH TRANG & GIAO DIỆN MINIMALIST LUXURY
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Phát Hiện Vết Dầu Tràn SAR",
    page_icon="🛰️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS: Tối giản tuyệt đối, phông chữ lớn, sắc nét, loại bỏ toàn bộ chi tiết thừa
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@500;600;700&display=swap');

    /* Tông màu nền chính: Obsidian Deep Black */
    html, body, .stApp {
        background-color: #090d16 !important;
        color: #f8fafc !important;
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif !important;
        font-size: 16px !important;
    }

    /* Thanh điều khiển bên trái (Sidebar) */
    [data-testid="stSidebar"] {
        background-color: #0f1523 !important;
        border-right: 1px solid rgba(255, 255, 255, 0.08) !important;
    }

    [data-testid="stSidebar"] .stMarkdown h3 {
        color: #94a3b8 !important;
        font-size: 13px !important;
        letter-spacing: 0.12em !important;
        text-transform: uppercase !important;
        font-weight: 700 !important;
        margin-top: 20px !important;
        margin-bottom: 8px !important;
    }

    /* Nhãn điều khiển chữ lớn, rõ nét */
    .stSelectbox label, .stSlider label, .stRadio label, .stCheckbox label, .stFileUploader label {
        font-size: 15px !important;
        font-weight: 600 !important;
        color: #e2e8f0 !important;
        margin-bottom: 6px !important;
    }

    .stSelectbox div[data-baseweb="select"] > div {
        font-size: 15px !important;
        background-color: #161e31 !important;
        border: 1px solid rgba(255, 255, 255, 0.14) !important;
        border-radius: 8px !important;
        color: #ffffff !important;
        min-height: 46px !important;
    }

    /* Thanh tiêu đề tối giản trên cùng */
    .header-bar {
        display: flex;
        justify-content: space-between;
        align-items: baseline;
        padding: 16px 0 20px 0;
        margin-bottom: 24px;
        border-bottom: 1px solid rgba(255, 255, 255, 0.08);
    }
    .header-title-text {
        font-size: 28px;
        font-weight: 800;
        letter-spacing: -0.02em;
        color: #ffffff;
    }
    .header-badge-text {
        font-family: 'JetBrains Mono', monospace;
        font-size: 13px;
        color: #38bdf8;
        letter-spacing: 0.1em;
        font-weight: 600;
    }

    /* Bảng thông báo trạng thái nhận diện */
    .status-panel {
        border-radius: 8px;
        padding: 20px 24px;
        margin-bottom: 24px;
    }
    .status-panel-alert {
        background: rgba(239, 68, 68, 0.08);
        border: 1px solid rgba(239, 68, 68, 0.35);
        border-left: 5px solid #ef4444;
    }
    .status-panel-clean {
        background: rgba(16, 185, 129, 0.08);
        border: 1px solid rgba(16, 185, 129, 0.35);
        border-left: 5px solid #10b981;
    }
    .status-title {
        font-size: 19px;
        font-weight: 700;
        margin-bottom: 6px;
    }
    .status-title-alert { color: #f87171; }
    .status-title-clean { color: #34d399; }
    .status-desc {
        font-size: 15px;
        color: #cbd5e1;
    }

    /* Lưới chỉ số (Metric Cards) chữ số lớn */
    .metric-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 16px;
        margin-bottom: 28px;
    }
    .metric-box {
        background: #131929;
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 8px;
        padding: 18px 20px;
    }
    .metric-lbl {
        font-size: 12px;
        font-weight: 700;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        color: #94a3b8;
        margin-bottom: 6px;
    }
    .metric-num {
        font-family: 'JetBrains Mono', monospace;
        font-size: 30px;
        font-weight: 700;
        color: #ffffff;
    }
    .metric-unit {
        font-size: 13px;
        color: #64748b;
        margin-left: 4px;
    }

    /* Tiêu đề phân mục */
    .block-heading {
        font-size: 20px;
        font-weight: 700;
        color: #ffffff;
        margin-top: 24px;
        margin-bottom: 16px;
        letter-spacing: -0.01em;
    }

    /* Khung hiển thị ảnh */
    .image-card {
        background: #111726;
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 8px;
        padding: 14px;
        margin-bottom: 20px;
    }
    .image-card-title {
        font-size: 15px;
        font-weight: 600;
        color: #e2e8f0;
        margin-bottom: 10px;
    }

    /* Nút tải xuống */
    .stDownloadButton button {
        background: #172033 !important;
        color: #ffffff !important;
        border: 1px solid rgba(255, 255, 255, 0.16) !important;
        border-radius: 8px !important;
        font-size: 15px !important;
        font-weight: 600 !important;
        padding: 12px 20px !important;
        min-height: 48px !important;
        width: 100% !important;
        transition: all 0.2s ease !important;
    }
    .stDownloadButton button:hover {
        background: #222e47 !important;
        border-color: #38bdf8 !important;
    }
</style>
""", unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# 2. THANH THAM SỐ (SIDEBAR)
# -----------------------------------------------------------------------------
st.sidebar.markdown("### ẢNH ĐẦU VÀO")

input_mode = st.sidebar.radio(
    "Nguồn ảnh:",
    ["Thư viện mẫu", "Tải từ máy tính"],
    label_visibility="collapsed"
)

input_image = None
image_name = ""

data_dir = ROOT_DIR / "data"

if input_mode == "Thư viện mẫu":
    class_choice = st.sidebar.selectbox(
        "Nhóm ảnh kiểm thử:",
        ["Class 1: Mẫu có vết dầu tràn", "Class 0: Biển sạch / Vùng gió lặng"]
    )
    
    if "Class 1" in class_choice:
        sample_files = sorted(glob.glob(str(data_dir / "sample" / "Class_1" / "*.jpg")))
        if not sample_files:
            sample_files = sorted(glob.glob(str(data_dir / "Class_1" / "*.jpg")))[:30]
    else:
        sample_files = sorted(glob.glob(str(data_dir / "sample" / "Class_0" / "*.jpg")))
        if not sample_files:
            sample_files = sorted(glob.glob(str(data_dir / "Class_0" / "*.jpg")))[:30]
            
    if sample_files:
        display_names = [os.path.basename(f) for f in sample_files]
        chosen_idx = st.sidebar.selectbox("Tệp ảnh SAR:", range(len(sample_files)), format_func=lambda i: display_names[i])
        chosen_file = sample_files[chosen_idx]
        input_image = cv2.imread(chosen_file)
        image_name = os.path.basename(chosen_file)
    else:
        st.sidebar.warning("Không tìm thấy tệp ảnh mẫu trong thư mục data.")
else:
    uploaded_file = st.sidebar.file_uploader("Tải tệp ảnh SAR (.jpg, .png, .tif):", type=["jpg", "jpeg", "png", "tif"])
    if uploaded_file is not None:
        file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
        input_image = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
        image_name = uploaded_file.name

st.sidebar.markdown("---")
st.sidebar.markdown("### BỘ LỌC SPECKLE")

filter_choice = st.sidebar.selectbox(
    "Thuật toán lọc:",
    [
        "Median Filter (Chương 3)",
        "Lee Filter (Radar SAR)",
        "Frost Filter (Radar SAR)",
        "Gaussian Filter",
        "Box / Mean Filter",
        "Custom Filter (src/custom_algorithms.py)"
    ],
    index=0
)
ksize_filter = st.sidebar.select_slider("Kernel lọc:", options=[3, 5, 7, 9], value=5)
enable_clahe = st.sidebar.checkbox("Tăng tương phản CLAHE", value=False)
clahe_clip = 2.0
if enable_clahe:
    clahe_clip = st.sidebar.slider("Clip Limit CLAHE:", min_value=1.0, max_value=5.0, value=2.0, step=0.5)

st.sidebar.markdown("---")
st.sidebar.markdown("### PHÂN ĐOẠN ĐỐM TỐI")

threshold_choice = st.sidebar.selectbox(
    "Thuật toán phân đoạn:",
    [
        "Otsu tối ưu (Chương 7)",
        "Sauvola thích nghi cục bộ",
        "Thống kê nền biển",
        "Niblack thích nghi (Custom)"
    ],
    index=0
)
min_otsu_eta = 0.08
sauvola_k = 0.20
sauvola_win = 41
sea_stat_k = 1.8

if "Otsu" in threshold_choice:
    min_otsu_eta = st.sidebar.slider("Hệ số khả tách η tối thiểu:", min_value=0.04, max_value=0.30, value=0.08, step=0.01)
elif "Sauvola" in threshold_choice or "Niblack" in threshold_choice:
    sauvola_k = st.sidebar.slider("Hệ số phân đoạn k:", min_value=0.05, max_value=0.50, value=0.20, step=0.05)
    sauvola_win = st.sidebar.select_slider("Cửa sổ cục bộ (px):", options=[21, 31, 41, 51, 61], value=41)
else:
    sea_stat_k = st.sidebar.slider("Hệ số lệch chuẩn k:", min_value=1.0, max_value=3.0, value=1.8, step=0.1)

st.sidebar.markdown("---")
st.sidebar.markdown("### HÌNH THÁI HỌC & ĐẶC TRƯNG")

with st.sidebar.expander("Tùy chỉnh chi tiết", expanded=False):
    enable_opening = st.checkbox("Opening (xóa bọt sóng)", value=True)
    open_k = 3
    if enable_opening:
        open_k = st.select_slider("Kernel Opening:", options=[3, 5], value=3)
        
    enable_closing = st.checkbox("Closing (nối dải dầu)", value=True)
    close_k = 7
    if enable_closing:
        close_k = st.select_slider("Kernel Closing:", options=[5, 7, 9], value=7)
        
    enable_fill_holes = st.checkbox("Lấp lỗ khuyết (Hole Filling)", value=True)
    min_area = st.slider("Diện tích tối thiểu (px):", min_value=50, max_value=1000, value=120, step=25)
    max_area = st.slider("Diện tích tối đa (px):", min_value=5000, max_value=150000, value=120000, step=5000)

    classifier_mode = st.selectbox(
        "Mô hình phân loại:",
        ["Heuristic Chuẩn (Vật lý SAR)", "Tùy chỉnh (src/custom_algorithms.py)"]
    )
    min_contrast = st.slider("Tương phản tối thiểu (Δμ):", min_value=5.0, max_value=30.0, value=10.0, step=1.0)
    min_border_grad = st.slider("Gradient biên Sobel tối thiểu:", min_value=2.0, max_value=20.0, value=5.0, step=0.5)
    min_elongation = st.slider("Độ thuôn dài tối thiểu (Lmaj/Lmin):", min_value=1.0, max_value=4.0, value=1.8, step=0.1)
    border_thickness = st.slider("Độ dày đường ranh giới đỏ:", min_value=1, max_value=4, value=2)


# -----------------------------------------------------------------------------
# 3. NỘI DUNG CHÍNH (SINGLE-VIEW WORKSTATION)
# -----------------------------------------------------------------------------
st.markdown("""
<div class="header-bar">
    <div class="header-title-text">Phát Hiện Vết Dầu Tràn SAR</div>
    <div class="header-badge-text">SENTINEL-1 &bull; PURE CV PIPELINE</div>
</div>
""", unsafe_allow_html=True)

if input_image is not None:
    # Chạy trực tiếp pipeline xử lý
    res = run_modular_pipeline(
        input_image,
        filter_type=filter_choice,
        ksize_filter=ksize_filter,
        enable_clahe=enable_clahe,
        clahe_clip=clahe_clip,
        threshold_type=threshold_choice,
        sauvola_k=sauvola_k,
        sauvola_win=sauvola_win,
        sea_stat_k=sea_stat_k,
        min_otsu_eta=min_otsu_eta,
        enable_opening=enable_opening,
        open_ksize=open_k,
        enable_closing=enable_closing,
        close_ksize=close_k,
        enable_fill_holes=enable_fill_holes,
        min_area=min_area,
        max_area=max_area,
        classifier_mode=classifier_mode,
        min_contrast=min_contrast,
        min_border_grad=min_border_grad,
        min_elongation=min_elongation,
        min_damping=1.25,
        border_thickness=border_thickness
    )
    
    detections = res["detections"]
    status = res["status"]
    step_times = res["step_times"]
    total_time_ms = res["total_time_ms"]
    
    # 1. Thẻ thông báo trạng thái
    if status == "OIL_DETECTED":
        st.markdown(f"""
        <div class="status-panel status-panel-alert">
            <div class="status-title status-title-alert">CẢNH BÁO: PHÁT HIỆN {len(detections)} KHU VỰC VẾT DẦU TRÀN</div>
            <div class="status-desc">Tệp ảnh: <strong>{image_name}</strong> &bull; Các vùng tối thỏa mãn tiêu chí suy giảm tán xạ, độ tương phản và hình thái dải dầu.</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="status-panel status-panel-clean">
            <div class="status-title status-title-clean">TRẠNG THÁI: KHÔNG PHÁT HIỆN VỆT DẦU LOANG</div>
            <div class="status-desc">Tệp ảnh: <strong>{image_name}</strong> &bull; {res["status_text"]}.</div>
        </div>
        """, unsafe_allow_html=True)

    # 2. Thẻ chỉ số hiệu năng
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f"""
        <div class="metric-box">
            <div class="metric-lbl">Thời gian xử lý</div>
            <div class="metric-num">{total_time_ms:.1f}<span class="metric-unit">ms</span></div>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div class="metric-box">
            <div class="metric-lbl">Tốc độ khung hình</div>
            <div class="metric-num">{1000/max(1, total_time_ms):.1f}<span class="metric-unit">FPS</span></div>
        </div>
        """, unsafe_allow_html=True)
    with c3:
        st.markdown(f"""
        <div class="metric-box">
            <div class="metric-lbl">Vết dầu phát hiện</div>
            <div class="metric-num">{len(detections)}<span class="metric-unit">vùng</span></div>
        </div>
        """, unsafe_allow_html=True)
    with c4:
        opt_str = f"T* = {res['optimal_t']}" if res.get('optimal_t') is not None else "Adaptive"
        st.markdown(f"""
        <div class="metric-box">
            <div class="metric-lbl">Ngưỡng phân đoạn</div>
            <div class="metric-num">{opt_str}</div>
        </div>
        """, unsafe_allow_html=True)

    # 3. Bốn bước trực quan hóa ảnh
    st.markdown('<div class="block-heading">Quy Trình Xử Lý Ảnh 4 Giai Đoạn</div>', unsafe_allow_html=True)

    orig_rgb = cv2.cvtColor(input_image, cv2.COLOR_BGR2RGB)
    vis_rgb = cv2.cvtColor(res["vis_bgr"], cv2.COLOR_BGR2RGB)
    
    col_img1, col_img2 = st.columns(2)
    with col_img1:
        st.markdown(f"""
        <div class="image-card">
            <div class="image-card-title">Giai đoạn 0: Ảnh SAR Sentinel-1 gốc ({image_name})</div>
        """, unsafe_allow_html=True)
        st.image(orig_rgb, width="stretch")
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown(f"""
        <div class="image-card">
            <div class="image-card-title">Giai đoạn 2 & 3: Mặt nạ phân đoạn nhị phân</div>
        """, unsafe_allow_html=True)
        st.image(res["morph_mask"], width="stretch", clamp=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with col_img2:
        st.markdown(f"""
        <div class="image-card">
            <div class="image-card-title">Giai đoạn 1: Sau khử nhiễu speckle ({step_times.get('filter_ms', 0):.1f} ms)</div>
        """, unsafe_allow_html=True)
        st.image(res["filtered"], width="stretch", clamp=True)
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown(f"""
        <div class="image-card">
            <div class="image-card-title">Giai đoạn 4: Ranh giới vệt dầu khoanh đỏ ({step_times.get('features_ms', 0):.1f} ms)</div>
        """, unsafe_allow_html=True)
        st.image(vis_rgb, width="stretch")
        st.markdown("</div>", unsafe_allow_html=True)

    # 4. Biểu đồ Histogram
    st.markdown('<div class="block-heading">Phổ Mức Xám Tán Xạ (Histogram)</div>', unsafe_allow_html=True)

    fig, ax = plt.subplots(figsize=(11, 2.8), facecolor='#090d16')
    ax.set_facecolor('#101625')
    
    hist = cv2.calcHist([res["filtered"]], [0], None, [256], [0, 256]).ravel()
    ax.plot(hist, color='#38bdf8', lw=2.0, label="Mức xám tán xạ (SAR Backscatter)")
    ax.fill_between(range(256), hist, color='#38bdf8', alpha=0.18)
    
    if res.get("optimal_t") is not None:
        opt_t = res["optimal_t"]
        ax.axvline(opt_t, color='#f87171', linestyle='--', lw=2.0, label=f"Ngưỡng T* = {opt_t}")
        ax.axvspan(0, opt_t, color='#ef4444', alpha=0.15, label="Vùng đốm tối")
        
    ax.set_xlim(0, 255)
    ax.tick_params(colors='#94a3b8', labelsize=11)
    for spine in ax.spines.values():
        spine.set_color('#1e293b')
    ax.set_xlabel("Mức xám (0: Dầu tràn — 255: Nền biển)", color='#cbd5e1', fontsize=12, labelpad=8)
    ax.set_ylabel("Số pixel", color='#cbd5e1', fontsize=12, labelpad=8)
    ax.grid(True, linestyle="--", color="#1e293b", alpha=0.6)
    ax.legend(facecolor='#090d16', edgecolor='#1e293b', labelcolor='#e2e8f0', fontsize=11, loc="upper right")
    st.pyplot(fig)
    plt.close(fig)

    # 5. Bảng đo đạc định lượng
    st.markdown('<div class="block-heading">Thông Số Định Lượng Vết Dầu</div>', unsafe_allow_html=True)

    if detections:
        df = pd.DataFrame(detections)
        col_order = ["id", "area", "perimeter", "elongation", "boundary_complexity", "contrast_diff", "damping_ratio", "border_gradient", "centroid", "reason"]
        existing_cols = [c for c in col_order if c in df.columns]
        df_display = df[existing_cols].rename(columns={
            "id": "ID",
            "area": "Diện tích (px)",
            "perimeter": "Chu vi (px)",
            "elongation": "Độ thuôn dài",
            "boundary_complexity": "Độ phức tạp biên",
            "contrast_diff": "Tương phản Δμ",
            "damping_ratio": "Tỉ số Damping",
            "border_gradient": "Gradient biên",
            "centroid": "Tọa độ tâm (X, Y)",
            "reason": "Phân loại"
        })
        st.dataframe(df_display, width="stretch")
        
        # Nút xuất dữ liệu
        st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
        b1, b2, b3 = st.columns(3)
        with b1:
            csv_buffer = io.StringIO()
            df_display.to_csv(csv_buffer, index=False, encoding='utf-8-sig')
            st.download_button(
                label="Tải bảng số liệu (CSV)",
                data=csv_buffer.getvalue(),
                file_name=f"metrics_{image_name}.csv",
                mime="text/csv"
            )
        with b2:
            _, png_buf = cv2.imencode(".png", res["vis_bgr"])
            st.download_button(
                label="Tải ảnh ranh giới viền đỏ (PNG)",
                data=png_buf.tobytes(),
                file_name=f"detected_{image_name}.png",
                mime="image/png"
            )
        with b3:
            _, mask_buf = cv2.imencode(".png", res["final_oil_mask"])
            st.download_button(
                label="Tải mặt nạ nhị phân (PNG)",
                data=mask_buf.tobytes(),
                file_name=f"mask_{image_name}.png",
                mime="image/png"
            )
    else:
        st.info("Không có đốm tối nào đáp ứng tiêu chuẩn nhận dạng vết dầu tràn.")
else:
    st.info("Vui lòng chọn ảnh mẫu từ thanh bên trái hoặc tải ảnh để bắt đầu phân tích.")
