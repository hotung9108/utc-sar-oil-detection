"""TV1: coursework demo. Launch: python -m streamlit run streamlit_app.py."""

import json
from pathlib import Path

import cv2
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st

from src.pipeline import (
    EDGE_NAMES,
    ENHANCEMENT_NAMES,
    FILTER_NAMES,
    SHARPENING_NAMES,
    PipelineConfig,
    process_image,
)

ROOT = Path(__file__).resolve().parent
TEAM = json.loads((ROOT / "docs/management/thanh_vien.json").read_text(encoding="utf-8"))
st.set_page_config(page_title="Xử lý ảnh SAR · BTL UTC", layout="wide")
st.title("Khử nhiễu, tăng cường và xử lý biên ảnh SAR")
st.caption("BTL Xử lý ảnh · Đề kết hợp đã đăng ký · NumPy · Không ML/DL")

with st.sidebar:
    st.header("Ảnh đầu vào")
    upload = st.file_uploader("Tải ảnh", type=["png", "jpg", "jpeg", "bmp", "tif", "tiff"])
    source = st.radio("Nguồn ảnh có sẵn", ["Ảnh mẫu", "Dataset Kaggle"])
    if source == "Dataset Kaggle":
        dataset_class = st.selectbox("Lớp dữ liệu", ["Class_0", "Class_1"])
        samples = sorted((ROOT / "kaggle/data" / dataset_class).glob("*.jpg"))
        st.caption(f"{dataset_class}: {len(samples):,} ảnh. Gõ tên trong ô chọn để tìm ảnh.")
        selected = st.selectbox("Chọn ảnh Kaggle", samples, format_func=lambda p: p.name)
    else:
        samples = sorted((ROOT / "data/sample").rglob("*.jpg"))
        special = ROOT / "kaggle/data/Class_1/class_1_00013.jpg"
        if special.exists():
            samples.append(special)
        selected = st.selectbox("Hoặc chọn ảnh mẫu", samples, format_func=lambda p: p.name)
    st.header("Tham số xử lý")
    filt = st.selectbox("Bộ lọc", FILTER_NAMES, index=FILTER_NAMES.index("lee"))
    size = st.select_slider("Cửa sổ lọc", options=[3, 5, 7, 9], value=5)
    looks = st.slider("Số look L", 1.0, 16.0, 4.0, 0.5)
    enh = st.selectbox("Tăng tương phản", ENHANCEMENT_NAMES, index=3)
    clip = st.slider("CLAHE clip limit", 0.5, 5.0, 2.0, 0.5)
    grid = st.select_slider("Lưới CLAHE", options=[1, 2, 4, 8, 16], value=8)
    sharp = st.selectbox("Làm nét để quan sát", SHARPENING_NAMES)
    amount = st.slider("Hệ số làm nét", 0.0, 3.0, 1.0, 0.1)
    edge = st.selectbox("Phương pháp biên", EDGE_NAMES)
    area = st.number_input(
        "Diện tích vùng tối tối thiểu (px)", min_value=1, max_value=160000, value=300
    )
    contrast = st.slider("Tương phản vùng/nền tối thiểu", 0.0, 1.0, 0.10, 0.01)
    close = st.slider("Bán kính closing", 0, 8, 4)
    auto = st.checkbox("Điều chỉnh ngưỡng Otsu khi vùng tối lớn", value=True)
    manual = st.checkbox("Dùng ngưỡng mức xám thủ công", value=False)
    threshold = st.slider("Ngưỡng mức xám", 1, 254, 80) if manual else None
    low = st.slider("Ngưỡng biên thấp", 0, 255, 35)
    high = st.slider("Ngưỡng biên cao", low, 1020 if edge == "canny" else 255, max(low, 90))

try:
    if upload is None and selected is None:
        st.info("Thư mục chưa có ảnh. Hãy tải ảnh hoặc bổ sung dataset vào kaggle/data.")
        st.stop()
    data = upload.getvalue() if upload is not None else selected.read_bytes()
    decoded = cv2.imdecode(np.frombuffer(data, np.uint8), cv2.IMREAD_GRAYSCALE)
    if decoded is None:
        raise ValueError("Không giải mã được ảnh.")
    raw = cv2.resize(decoded, (400, 400), interpolation=cv2.INTER_AREA)
    config = PipelineConfig(
        filt,
        size,
        looks,
        enh,
        clip,
        grid,
        sharp,
        amount,
        edge,
        low,
        high,
        area,
        contrast,
        close,
        threshold,
        auto,
    )
    result = process_image(raw, config)
except (ValueError, cv2.error) as exc:
    st.error(str(exc))
    st.stop()

tab_image, tab_metrics, tab_verify, tab_team = st.tabs(
    ["Kết quả ảnh", "Chỉ số và phân tích", "Đối chiếu thư viện", "Phân công TV1–TV5"]
)
with tab_image:
    cols = st.columns(3)
    for col, key, title in zip(
        cols, ["raw", "filtered", "enhanced"], ["Ảnh gốc", "Sau khử nhiễu", "Sau tăng tương phản"]
    ):
        col.image(result[key], caption=title, clamp=True)
    cols = st.columns(3)
    cols[0].image(result["displayed"], caption="Ảnh hiển thị sau bước làm nét")
    cols[1].image(
        result["mask"] if result["mask"] is not None else result["boundary"],
        caption="Vùng tối ứng viên"
        if result["mask"] is not None
        else "Bản đồ biên (không phải mask dầu)",
    )
    cols[2].image(result["overlay"], caption="Biên phủ trên ảnh gốc")
    st.info(
        "Vùng tối là ứng viên, chưa khẳng định là dầu. CLAHE có thể làm rõ cả kết cấu nền và nhiễu; đường biên cũng bao gồm các lỗ bên trong mask."
    )
    if result["stats"]:
        a, b, c = st.columns(3)
        a.metric("Số vùng ứng viên", result["stats"]["slicks_count"])
        b.metric("Tỷ lệ diện tích ảnh", f"{result['stats']['area_pct']}%")
        c.metric("Ngưỡng phân đoạn", result["stats"]["otsu_threshold"])
        st.dataframe(pd.DataFrame(result["stats"]["slicks_detected"]), hide_index=True)
    for key in ["enhanced", "boundary", "mask"]:
        if result[key] is not None:
            ok, buf = cv2.imencode(".png", result[key])
            if ok:
                st.download_button(
                    "Tải " + key + ".png", buf.tobytes(), file_name=key + ".png", mime="image/png"
                )
    st.download_button(
        "Tải cấu hình và chỉ số",
        json.dumps(
            {"config": result["config"], "metrics": result["metrics"], "stats": result["stats"]},
            ensure_ascii=False,
            indent=2,
        ),
        file_name="sar_result.json",
        mime="application/json",
    )
with tab_metrics:
    st.dataframe(pd.DataFrame([result["metrics"]]), hide_index=True)
    st.caption(
        "ENL đo ROI góc trên cố định, không đảm bảo ROI thực sự đồng nhất; EPI không chứng minh đường biên đúng. Ảnh demo được đổi kích thước 400×400."
    )
    row = st.slider("Lát cắt hàng", 0, 399, 200)
    fig, axes = plt.subplots(1, 2, figsize=(12, 3))
    for key, label in [("raw", "Gốc"), ("filtered", "Lọc"), ("enhanced", "Tăng tương phản")]:
        axes[0].plot(np.bincount(result[key].ravel(), minlength=256), label=label)
        axes[1].plot(result[key][row], label=label)
    axes[0].set(xlabel="Mức xám", ylabel="Số pixel")
    axes[1].set(xlabel="Cột (px)", ylabel="Mức xám")
    for ax in axes:
        ax.legend()
    st.pyplot(fig)
    plt.close(fig)
with tab_verify:
    path = ROOT / "results/verification/summary.csv"
    st.write(
        "Đối chiếu trực tiếp và phép ghép hàm thư viện được tách riêng. Sai khác giữa biến thể được báo cáo, không tính là kiểm thử đạt."
    )
    if not path.exists():
        path = ROOT / "docs/report/evidence/verification_summary.csv"
    if path.exists():
        st.dataframe(pd.read_csv(path), hide_index=True)
        st.download_button(
            "Tải bảng đối chiếu", path.read_bytes(), file_name="comparison_summary.csv"
        )
    else:
        st.info("Chưa có bảng. Chạy: python -m src.library_comparison")
with tab_team:
    st.table(
        pd.DataFrame(
            [[m["id"], m["name"], m["github"], m["role"]] for m in TEAM],
            columns=["Thành viên", "Họ tên", "GitHub", "Phần phụ trách"],
        )
    )
    st.caption(
        "Danh sách do nhóm cung cấp, tài khoản đối chiếu với collaborators GitHub. Tài liệu học và trình bày: docs/thanh_vien/. Nhóm tự điền MSSV và đánh giá chéo thực tế."
    )
