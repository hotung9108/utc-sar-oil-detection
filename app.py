"""
app.py: Web Application Server (FastAPI + HTML5/CSS3/JavaScript SPA).
BTL Xử lý ảnh - Đề tài Nhóm A: Tăng cường và lọc ảnh vi ba SAR bộc lộ vết dầu tràn trên biển & Đề 5 Xử lý biên.
Khoa CNTT - Đại học Giao thông Vận tải (UTC).
Cam kết: 100% xử lý ảnh kinh điển thuần NumPy, không sử dụng ML/DL.
"""

import base64
import glob
import os
import threading
import time
from typing import Dict, List, Optional
import cv2
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import numpy as np
import pandas as pd
from pydantic import BaseModel
import uvicorn

from src.edges import (
    custom_canny,
    custom_log,
    custom_prewitt,
    custom_roberts,
    custom_sobel,
    overlay_edges,
)
from src.enhancement import (
    custom_clahe,
    global_histogram_equalization,
    homomorphic_filter,
    log_transform,
)
from src.filters import (
    custom_bilateral_filter,
    custom_box_filter,
    custom_frost_filter,
    custom_gaussian_filter,
    custom_kuan_filter,
    custom_lee_filter,
    custom_median_filter,
)
from src.metrics import calculate_all_enhancement_metrics
from src.morphology import (
    custom_morphological_boundary,
    detect_oil_slick_morphological,
)
from src.sharpening import laplacian_sharpening, sobel_edge_enhancement, unsharp_masking
from src.utils import calculate_difference_map, get_profile_slice, load_sar_image

app = FastAPI(title="SAR Image Enhancement & Edge Studio", version="2.1.0")

# Cấu hình CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount thư mục static và results
os.makedirs("static", exist_ok=True)
os.makedirs("results/figures", exist_ok=True)
os.makedirs("results/tables", exist_ok=True)

app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/results", StaticFiles(directory="results"), name="results")


def numpy_to_base64(img: np.ndarray) -> str:
    """Mã hóa ảnh NumPy (2D grayscale hoặc 3D RGB) thành chuỗi Base64 PNG."""
    if img.ndim == 3:
        # OpenCV imencode nhận BGR
        bgr = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
        success, buffer = cv2.imencode(".png", bgr)
    else:
        success, buffer = cv2.imencode(".png", img)

    if not success:
        return ""
    return base64.b64encode(buffer.tobytes()).decode("utf-8")


def base64_to_numpy(b64_str: str) -> np.ndarray:
    """Giải mã chuỗi Base64 tải lên thành ma trận NumPy xám uint8 (400x400)."""
    if "," in b64_str:
        b64_str = b64_str.split(",", 1)[1]
    raw_bytes = base64.b64decode(b64_str)
    nparr = np.frombuffer(raw_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise ValueError("Không thể giải mã dữ liệu ảnh tải lên.")
    return cv2.resize(img, (400, 400), interpolation=cv2.INTER_LINEAR)


# Cache danh sách ảnh mẫu
SAMPLE_CACHE: List[Dict] = []


def init_sample_cache(force: bool = False) -> None:
    global SAMPLE_CACHE
    if SAMPLE_CACHE and not force:
        return

    oil_paths = sorted(glob.glob("data/sample/oil_slicks/*.jpg"))
    sea_paths = sorted(glob.glob("data/sample/sea_surface/*.jpg"))

    items = []
    for p in oil_paths:
        name = os.path.basename(p)
        img = load_sar_image(p, target_size=(400, 400))
        thumb = cv2.resize(img, (96, 96))
        items.append({
            "id": name,
            "category": "oil",
            "path": p,
            "thumb_base64": numpy_to_base64(thumb),
        })

    for p in sea_paths:
        name = os.path.basename(p)
        img = load_sar_image(p, target_size=(400, 400))
        thumb = cv2.resize(img, (96, 96))
        items.append({
            "id": name,
            "category": "sea",
            "path": p,
            "thumb_base64": numpy_to_base64(thumb),
        })

    SAMPLE_CACHE = items


class ProcessRequest(BaseModel):
    image_id: str = "oil_slick_01.jpg"
    custom_image_base64: Optional[str] = None
    filter_type: str = "lee"
    filter_size: int = 5
    num_looks: float = 4.0
    sigma_s: float = 3.0
    sigma_r: float = 25.0
    damping: float = 2.0
    d0: float = 30.0
    enhancement_type: str = "clahe"
    clip_limit: float = 2.0
    tile_grid: int = 8
    sharpening_type: str = "unsharp"
    sharp_k: float = 0.8
    slice_row: int = 200
    # Tham số xử lý biên & hình thái học (Chương 5, 6, 7 UTC & Đề 18 NASA)
    edge_type: str = "morphology"  # Default Option 1: Bộc lộ ranh giới vết dầu hình thái học beta(A)
    edge_low: float = 35.0
    edge_high: float = 90.0
    edge_mode: str = "overlay"
    overlay_color: str = "red"
    min_area: int = 300
    min_contrast: float = 0.10
    manual_threshold: Optional[int] = None


@app.get("/")
def serve_index():
    index_file = "static/index.html"
    if not os.path.exists(index_file):
        raise HTTPException(status_code=404, detail="Không tìm thấy static/index.html")
    return FileResponse(index_file)


@app.get("/api/samples")
def get_samples():
    init_sample_cache()
    return {"samples": SAMPLE_CACHE}


@app.post("/api/process")
def process_pipeline(req: ProcessRequest):
    init_sample_cache()

    # 1. Nạp ảnh SAR nguồn
    if req.custom_image_base64:
        try:
            raw_img = base64_to_numpy(req.custom_image_base64)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Lỗi đọc ảnh tải lên: {str(e)}")
    else:
        matched = next((s for s in SAMPLE_CACHE if s["id"] == req.image_id), None)
        if matched and os.path.exists(matched["path"]):
            raw_img = load_sar_image(matched["path"], target_size=(400, 400))
        elif os.path.exists("data/sample/oil_slicks/oil_slick_01.jpg"):
            raw_img = load_sar_image("data/sample/oil_slicks/oil_slick_01.jpg", target_size=(400, 400))
        else:
            raise HTTPException(status_code=404, detail="Không tìm thấy ảnh SAR yêu cầu.")

    # 2. Bước 1: Khử đốm (Speckle Filtering)
    f_type = req.filter_type.lower()
    k_size = max(3, req.filter_size if req.filter_size % 2 == 1 else req.filter_size + 1)
    proc_img = raw_img.copy()

    if f_type == "lee":
        proc_img = custom_lee_filter(proc_img, window_size=k_size, num_looks=req.num_looks)
    elif f_type == "bilateral":
        proc_img = custom_bilateral_filter(proc_img, window_size=k_size, sigma_s=req.sigma_s, sigma_r=req.sigma_r)
    elif f_type == "frost":
        proc_img = custom_frost_filter(proc_img, window_size=k_size, damping_factor=req.damping)
    elif f_type == "kuan":
        proc_img = custom_kuan_filter(proc_img, window_size=k_size, num_looks=req.num_looks)
    elif f_type == "gaussian":
        proc_img = custom_gaussian_filter(proc_img, window_size=k_size, sigma=1.0)
    elif f_type == "median":
        proc_img = custom_median_filter(proc_img, window_size=k_size)
    elif f_type == "box":
        proc_img = custom_box_filter(proc_img, window_size=k_size)
    elif f_type == "homomorphic":
        proc_img = homomorphic_filter(proc_img, gamma_l=0.5, gamma_h=1.5, d0=req.d0)

    # Lưu bản sao ảnh ngay sau lọc đốm (filtered_img) làm reference_image đo đạc tán xạ vật lý
    filtered_img = proc_img.copy()

    # 3. Bước 2: Tăng cường tương phản (Contrast Enhancement)
    e_type = req.enhancement_type.lower()
    if e_type == "clahe":
        grid_dim = req.tile_grid if req.tile_grid in (4, 8, 16) else 8
        proc_img = custom_clahe(proc_img, clip_limit=req.clip_limit, tile_grid_size=(grid_dim, grid_dim))
    elif e_type == "he":
        proc_img, _ = global_histogram_equalization(proc_img)
    elif e_type == "log":
        proc_img = log_transform(proc_img)

    # Lưu bản sao ảnh sau khử đốm & tăng cường tương phản (enhanced_img)
    # Đây là đầu vào lý tưởng cho phân vùng Otsu & hình thái học vì ảnh đã sạch nhiễu đốm,
    # tương phản biển-dầu tối ưu, nhưng CHƯA bị ảnh hưởng bởi hiện tượng Undershoot Dip của làm nét
    enhanced_img = proc_img.copy()

    # 4. Bước 3: Làm nét & Bộc lộ biên (Sharpening)
    s_type = req.sharpening_type.lower()
    if s_type == "unsharp":
        proc_img = unsharp_masking(proc_img, k=req.sharp_k, window_size=5)
    elif s_type == "laplacian":
        proc_img = laplacian_sharpening(proc_img, alpha=req.sharp_k)
    elif s_type == "sobel":
        _, proc_img = sobel_edge_enhancement(proc_img)

    # 5. Bước 4: Xử lý và bộc lộ biên (Edge Detection & Boundary Highlighting)
    e_mode_type = req.edge_type.lower()
    binary_edges = np.zeros_like(raw_img)
    mag_img = np.zeros_like(raw_img)
    oil_stats = None

    if e_mode_type == "morphology":
        # Tùy chọn 1 (Khuyên dùng): Bộc lộ ranh giới vết dầu hình thái học beta(A) (Chương 6 & 7 UTC + Đề 18 NASA)
        # Thực hiện phân đoạn trên enhanced_img để triệt tiêu mọi sai lệch từ làm nét (Undershoot dip)
        morph_res = detect_oil_slick_morphological(
            enhanced_img,
            min_area=req.min_area,
            min_contrast=req.min_contrast,
            manual_threshold=req.manual_threshold,
            reference_image=filtered_img,
        )
        binary_edges = morph_res["boundary_mask"]
        mag_img = morph_res["clean_mask"]
        oil_stats = {
            "slicks_count": morph_res["slicks_count"],
            "total_area_px": morph_res["total_area_px"],
            "area_pct": morph_res["area_pct"],
            "mean_contrast_ratio": morph_res["mean_contrast_ratio"],
            "otsu_threshold": morph_res["otsu_threshold"],
            "separability_eta": morph_res["separability_eta"],
        }
    elif e_mode_type == "canny":
        binary_edges = custom_canny(proc_img, low_thresh=req.edge_low, high_thresh=req.edge_high)
        _, _, mag_img, _ = custom_sobel(proc_img)
    elif e_mode_type == "sobel":
        _, _, mag_img, _ = custom_sobel(proc_img)
        binary_edges = np.where(mag_img >= req.edge_high, 255, 0).astype(np.uint8)
    elif e_mode_type == "prewitt":
        _, _, mag_img = custom_prewitt(proc_img)
        binary_edges = np.where(mag_img >= req.edge_high, 255, 0).astype(np.uint8)
    elif e_mode_type == "roberts":
        mag_img = custom_roberts(proc_img)
        binary_edges = np.where(mag_img >= req.edge_high, 255, 0).astype(np.uint8)
    elif e_mode_type == "log":
        binary_edges = custom_log(proc_img, sigma=1.4, threshold=3.0)
        mag_img = binary_edges

    # Màu phủ viền
    if req.overlay_color == "cyan":
        color_rgb = (0, 230, 255)
    elif req.overlay_color == "white":
        color_rgb = (255, 255, 255)
    else:
        color_rgb = (255, 30, 30)

    # Tạo ảnh hiển thị biên
    if e_mode_type == "none":
        edge_visual = np.stack([raw_img, raw_img, raw_img], axis=-1)
    elif req.edge_mode == "binary":
        edge_visual = binary_edges
    elif req.edge_mode == "magnitude":
        edge_visual = mag_img
    else:
        edge_visual = overlay_edges(proc_img, binary_edges, color=color_rgb, alpha=0.9)

    # 6. Bản đồ vi sai Difference Map
    diff_img = calculate_difference_map(raw_img, proc_img)

    # 7. Lát cắt ngang Profile Slice (Hàng slice_row)
    slice_y = min(max(0, req.slice_row), 399)
    raw_slice = get_profile_slice(raw_img, row_or_col=slice_y, axis=0).tolist()
    proc_slice = get_profile_slice(proc_img, row_or_col=slice_y, axis=0).tolist()

    # 8. Histogram mức xám [0..255]
    raw_hist = np.bincount(raw_img.ravel(), minlength=256).tolist()
    proc_hist = np.bincount(proc_img.ravel(), minlength=256).tolist()

    # 9. Tính 6 chỉ số định lượng DIP Metrics
    metrics = calculate_all_enhancement_metrics(raw_img, proc_img)

    return {
        "raw_image_base64": numpy_to_base64(raw_img),
        "proc_image_base64": numpy_to_base64(proc_img),
        "edge_image_base64": numpy_to_base64(edge_visual),
        "diff_image_base64": numpy_to_base64(diff_img),
        "raw_slice": raw_slice,
        "proc_slice": proc_slice,
        "raw_hist": raw_hist,
        "proc_hist": proc_hist,
        "metrics": metrics,
        "oil_slick_stats": oil_stats,
    }


@app.get("/api/experiments")
def get_experiments():
    exp1_file = "results/tables/experiment1_speckle_filters.csv"
    exp2_file = "results/tables/experiment2_clahe_survey.csv"
    exp3_file = "results/tables/experiment3_enhancement_summary.csv"
    exp4_file = "results/tables/experiment4_edge_comparison.csv"
    exp5_file = "results/tables/experiment5_morphological_oil_boundary.csv"

    def read_csv_safe(path: str) -> List[Dict]:
        if os.path.exists(path):
            try:
                df = pd.read_csv(path)
                return df.to_dict(orient="records")
            except Exception:
                return []
        return []

    return {
        "exp1": read_csv_safe(exp1_file),
        "exp2": read_csv_safe(exp2_file),
        "exp3": read_csv_safe(exp3_file),
        "exp4": read_csv_safe(exp4_file),
        "exp5": read_csv_safe(exp5_file),
    }


def open_browser_later():
    time.sleep(1.2)
    import webbrowser
    webbrowser.open("http://127.0.0.1:8000")


if __name__ == "__main__":
    print("=" * 70)
    print("KHỞI CHẠY SAR IMAGE ENHANCEMENT & EDGE STUDIO (FASTAPI + WEB SPA)")
    print("BTL Xử lý ảnh - Khoa CNTT, Đại học Giao thông Vận tải (UTC)")
    print("Mở trình duyệt tại: http://127.0.0.1:8000")
    print("=" * 70)

    threading.Thread(target=open_browser_later, daemon=True).start()
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=False)
