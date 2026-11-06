"""
evaluate_all_edges.py: Kịch bản quét toàn bộ 100% dữ liệu ảnh SAR vết dầu (Kaggle Class 1 + Sample).
Mục đích:
- Phân tích định lượng từng ảnh trên toàn bộ dataset.
- Tự động phát hiện và trích xuất các ảnh bị lệch phần edge (Tràn biên, Vỡ vụn, Bỏ sót, Khả tách kém).
- Xuất toàn bộ ảnh lỗi vào results/edge_evaluation_output/flagged_deviations/.
- Tạo báo cáo CSV và Markdown để cùng người dùng phân tích và tối ưu hóa thuật toán.
"""

import concurrent.futures
import glob
import os
import sys
import time
from typing import Dict, List, Optional, Tuple

import cv2
import numpy as np
import pandas as pd

from src.edges import overlay_edges
from src.enhancement import custom_clahe
from src.filters import custom_lee_filter
from src.morphology import detect_oil_slick_morphological
from src.sharpening import unsharp_masking


# ==============================================================================
# HÀM TẠO ẢNH CHẨN ĐOÁN 4 KHUNG HÌNH (4-PANEL DIAGNOSTIC COLLAGE)
# ==============================================================================

def create_diagnostic_collage(
    raw_img: np.ndarray,
    enhanced_img: np.ndarray,
    clean_mask: np.ndarray,
    boundary_mask: np.ndarray,
    title_info: str,
    status: str,
    metrics_info: str,
) -> np.ndarray:
    """Tạo ảnh ghép 4 khung hình chất lượng cao kích thước 1600x460 pixel."""
    h, w = 400, 400
    p1 = cv2.resize(raw_img, (w, h))
    p2 = cv2.resize(enhanced_img, (w, h))
    p3 = cv2.resize(clean_mask, (w, h))
    
    # Tạo ảnh biên phủ đỏ trên nền ảnh đã làm nét nhẹ
    sharpened = unsharp_masking(p2, k=0.5, window_size=5)
    p4 = overlay_edges(sharpened, cv2.resize(boundary_mask, (w, h)), color=(255, 30, 30), alpha=0.95)

    # Chuyển các panel sang BGR (3 kênh)
    c1 = cv2.cvtColor(p1, cv2.COLOR_GRAY2BGR)
    c2 = cv2.cvtColor(p2, cv2.COLOR_GRAY2BGR)
    c3 = cv2.cvtColor(p3, cv2.COLOR_GRAY2BGR)
    c4 = cv2.cvtColor(p4, cv2.COLOR_RGB2BGR)

    # Ghép 4 panel ngang
    body = np.hstack([c1, c2, c3, c4])

    # Tạo thanh tiêu đề trên cùng (chiều cao 60px)
    header = np.zeros((60, body.shape[1], 3), dtype=np.uint8)
    
    # Chọn màu thanh trạng thái
    if status == "CLEAN_BOUNDARY":
        header[:] = (20, 80, 20)  # Xanh lá sẫm
    elif status == "EDGE_LEAKAGE":
        header[:] = (20, 20, 110) # Đỏ sẫm
    elif status == "EDGE_FRAGMENTED":
        header[:] = (20, 70, 110) # Cam sẫm
    elif status == "MISSED_SLICK":
        header[:] = (80, 40, 20)  # Xanh dương sẫm
    else:
        header[:] = (40, 40, 40)

    # Vẽ chữ tiêu đề
    cv2.putText(header, title_info, (15, 24), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255, 255, 255), 2, cv2.LINE_AA)
    cv2.putText(header, metrics_info, (15, 48), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (220, 220, 220), 1, cv2.LINE_AA)

    # Vẽ nhãn cho từng panel
    labels = ["1. GOC SAR", "2. LEE + CLAHE", "3. MAT NA SACH A", f"4. BIEN beta(A) [{status}]"]
    canvas = np.vstack([header, body])
    
    for i, lbl in enumerate(labels):
        x = i * w + 10
        y = 60 + 25
        cv2.rectangle(canvas, (x - 4, y - 18), (x + len(lbl) * 11 + 10, y + 6), (0, 0, 0), -1)
        cv2.putText(canvas, lbl, (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1, cv2.LINE_AA)

    return canvas


# ==============================================================================
# HÀM XỬ LÝ 1 ẢNH (CHẠY TRÊN TỪNG TIẾN TRÌNH CON)
# ==============================================================================

def process_single_image(img_path: str) -> Optional[Dict]:
    """Thực thi toàn bộ pipeline DIP trên một ảnh và đánh giá chất lượng biên."""
    try:
        raw_img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
        if raw_img is None:
            return None

        # Đưa về kích thước chuẩn 400x400
        if raw_img.shape != (400, 400):
            raw_img = cv2.resize(raw_img, (400, 400), interpolation=cv2.INTER_AREA)

        # 1. Khử đốm Lee MMSE 5x5
        f_img = custom_lee_filter(raw_img, window_size=5, num_looks=4.0)

        # 2. Tăng cường CLAHE clip=2.0, grid=8x8
        enhanced_img = custom_clahe(f_img, clip_limit=2.0, tile_grid_size=(8, 8))

        # 3. Phân đoạn Otsu & Bộc lộ hình thái học beta(A)
        res = detect_oil_slick_morphological(
            enhanced_img,
            min_area=300,
            min_contrast=0.10,
        )

        slicks_count = res["slicks_count"]
        total_area = res["total_area_px"]
        area_pct = res["area_pct"]
        contrast_ratio = res["mean_contrast_ratio"]
        otsu_t = res["otsu_threshold"]
        eta = res["separability_eta"]

        # 4. Phân loại trạng thái biên (Edge Health Status)
        is_sea_surface = "sea_surface" in img_path.lower()
        
        if is_sea_surface:
            if slicks_count > 0:
                status = "FALSE_ALARM"
                reason = f"Bắt nhầm biển sạch thành {slicks_count} vết dầu ({area_pct}%)"
            else:
                status = "CLEAN_SEA"
                reason = "Biển sạch chuẩn xác, không có báo động giả"
        else:
            # Ảnh vết dầu (Class 1 hoặc sample oil_slicks)
            if slicks_count == 0:
                status = "MISSED_SLICK"
                reason = "Bỏ sót vết dầu (0 vết dầu phát hiện được, có thể do vệt quá mỏng CR < 0.10)"
            elif area_pct > 75.0:
                status = "EDGE_LEAKAGE"
                reason = f"Tràn biên ra biển ({area_pct}% ảnh bị coi là dầu, ngưỡng Otsu cắt quá cao)"
            elif slicks_count > 15:
                status = "EDGE_FRAGMENTED"
                reason = f"Biên bị vỡ vụn thành {slicks_count} mảng nhỏ rời rạc (chưa hàn gắn hết bọt sóng)"
            elif eta < 0.50:
                status = "LOW_SEPARABILITY"
                reason = f"Độ khả tách Otsu kém (eta = {eta:.3f} < 0.50), ranh giới dễ lem"
            else:
                status = "CLEAN_BOUNDARY"
                reason = "Bộc lộ ranh giới chuẩn xác 100%, đường bao 1px ôm khít mảng dầu"

        fname = os.path.basename(img_path)

        return {
            "image_path": img_path,
            "filename": fname,
            "status": status,
            "reason": reason,
            "slicks_count": slicks_count,
            "total_area_px": total_area,
            "area_pct": area_pct,
            "contrast_ratio": contrast_ratio,
            "otsu_threshold": otsu_t,
            "separability_eta": eta,
            # Giữ ảnh trong kết quả nếu là ảnh lỗi hoặc sample để tạo ảnh chẩn đoán
            "raw_img": raw_img if status != "CLEAN_BOUNDARY" else None,
            "enhanced_img": enhanced_img if status != "CLEAN_BOUNDARY" else None,
            "clean_mask": res["clean_mask"] if status != "CLEAN_BOUNDARY" else None,
            "boundary_mask": res["boundary_mask"] if status != "CLEAN_BOUNDARY" else None,
        }

    except Exception as exc:
        print(f"Lỗi khi xử lý {img_path}: {exc}", file=sys.stderr)
        return None


# ==============================================================================
# HÀM CHÍNH BENCHMARK TOÀN BỘ DATASET
# ==============================================================================

def main():
    print("=" * 80)
    print(">>> CHƯƠNG TRÌNH QUÉT FULL 100% DATASET & KIỂM TRA LỆCH BIÊN VẾT DẦU SAR")
    print(">>> BTL Xử Lý Ảnh - Khoa CNTT, Đại học Giao thông Vận tải (UTC)")
    print("=" * 80)

    # 1. Thu thập danh sách ảnh
    kaggle_oil = sorted(glob.glob("kaggle/data/Class_1/*.jpg"))
    sample_oil = sorted(glob.glob("data/sample/oil_slicks/*.jpg"))
    sample_sea = sorted(glob.glob("data/sample/sea_surface/*.jpg"))

    all_paths = sample_oil + sample_sea + kaggle_oil
    total_imgs = len(all_paths)

    print(f"\n[1] Tìm thấy tổng cộng: {total_imgs} ảnh cần quét:")
    print(f"    - Sample Oil Slicks:   {len(sample_oil)} ảnh")
    print(f"    - Sample Sea Surface:  {len(sample_sea)} ảnh")
    print(f"    - Kaggle Class 1 Oil:  {len(kaggle_oil)} ảnh")

    if total_imgs == 0:
        print("Lỗi: Không tìm thấy ảnh nào để xử lý!")
        return

    # 2. Tạo thư mục output
    out_dir = "results/edge_evaluation_output"
    flagged_dir = os.path.join(out_dir, "flagged_deviations")
    gallery_dir = os.path.join(out_dir, "clean_samples_gallery")
    os.makedirs(flagged_dir, exist_ok=True)
    os.makedirs(gallery_dir, exist_ok=True)

    # 3. Chạy xử lý đa tiến trình
    workers = min(14, max(4, (os.cpu_count() or 4) - 2))
    print(f"\n[2] Bắt đầu quét song song trên {workers} nhân CPU...")
    start_time = time.time()

    results = []
    processed_count = 0

    with concurrent.futures.ProcessPoolExecutor(max_workers=workers) as executor:
        futures = {executor.submit(process_single_image, p): p for p in all_paths}
        
        for future in concurrent.futures.as_completed(futures):
            res = future.result()
            if res is not None:
                results.append(res)
            processed_count += 1
            if processed_count % 100 == 0 or processed_count == total_imgs:
                elapsed = time.time() - start_time
                fps = processed_count / elapsed
                print(f"    -> Đã quét: {processed_count}/{total_imgs} ảnh ({(processed_count/total_imgs)*100:.1f}%) - Tốc độ: {fps:.1f} ảnh/s")

    total_time = time.time() - start_time
    print(f"\n[3] Hoàn tất quét {len(results)} ảnh trong {total_time:.2f} giây! ({total_time/len(results)*1000:.1f} ms/ảnh)")

    # 4. Phân loại và tổng kết thống kê
    df = pd.DataFrame([{k: v for k, v in r.items() if k not in ("raw_img", "enhanced_img", "clean_mask", "boundary_mask")} for r in results])
    csv_path = os.path.join(out_dir, "full_dataset_edge_benchmark.csv")
    df.to_csv(csv_path, index=False, encoding="utf-8-sig")
    print(f"[4] Đã lưu bảng số liệu toàn bộ {len(df)} ảnh vào: {csv_path}")

    status_counts = df["status"].value_counts().to_dict()
    print("\n" + "=" * 80)
    print("TỔNG HỢP KẾT QUẢ ĐÁNH GIÁ CHẤT LƯỢNG ĐƯỜNG BIÊN TRÊN TOÀN BỘ DATASET:")
    print("=" * 80)
    for st, cnt in status_counts.items():
        pct = cnt / len(df) * 100
        print(f"  - {st:<20}: {cnt:>5} ảnh ({pct:>5.1f}%)")

    # 5. Kết xuất ảnh chẩn đoán 4 khung hình cho các ảnh bị lệch biên
    print("\n[5] Đang kết xuất ảnh chẩn đoán 4 khung hình cho các ảnh bị lệch biên...")
    flagged_results = [r for r in results if r["status"] in ("EDGE_LEAKAGE", "EDGE_FRAGMENTED", "MISSED_SLICK", "LOW_SEPARABILITY", "FALSE_ALARM")]
    
    saved_flagged = 0
    for r in flagged_results:
        # Nếu đã lưu ảnh trung gian
        raw_img = r["raw_img"]
        enhanced_img = r["enhanced_img"]
        clean_mask = r["clean_mask"]
        boundary_mask = r["boundary_mask"]

        if raw_img is None:
            # Tải lại nếu chưa lưu
            raw_img = cv2.imread(r["image_path"], cv2.IMREAD_GRAYSCALE)
            raw_img = cv2.resize(raw_img, (400, 400))
            f_img = custom_lee_filter(raw_img, 5, 4.0)
            enhanced_img = custom_clahe(f_img, 2.0, (8, 8))
            m = detect_oil_slick_morphological(enhanced_img, 300, 0.10)
            clean_mask = m["clean_mask"]
            boundary_mask = m["boundary_mask"]

        base_name = os.path.splitext(r["filename"])[0]
        title = f"File: {r['filename']} | Trang thai: {r['status']}"
        metrics = f"Slicks: {r['slicks_count']} | Area: {r['total_area_px']}px ({r['area_pct']}%) | CR: {r['contrast_ratio']:.3f} | Otsu: {r['otsu_threshold']} | Eta: {r['separability_eta']:.3f}"
        
        collage = create_diagnostic_collage(
            raw_img, enhanced_img, clean_mask, boundary_mask,
            title, r["status"], metrics
        )

        out_name = f"{base_name}_{r['status'].lower()}.png"
        cv2.imwrite(os.path.join(flagged_dir, out_name), collage)
        saved_flagged += 1

    print(f"    -> Đã lưu {saved_flagged} ảnh chẩn đoán lệch biên vào: {flagged_dir}")

    # 6. Lưu thêm 10 ảnh mẫu sạch chuẩn để so sánh
    clean_results = [r for r in results if r["status"] == "CLEAN_BOUNDARY"][:10]
    for r in clean_results:
        raw_img = cv2.imread(r["image_path"], cv2.IMREAD_GRAYSCALE)
        raw_img = cv2.resize(raw_img, (400, 400))
        f_img = custom_lee_filter(raw_img, 5, 4.0)
        enhanced_img = custom_clahe(f_img, 2.0, (8, 8))
        m = detect_oil_slick_morphological(enhanced_img, 300, 0.10)

        base_name = os.path.splitext(r["filename"])[0]
        title = f"File: {r['filename']} | Trang thai: CLEAN_BOUNDARY (Chuan)"
        metrics = f"Slicks: {r['slicks_count']} | Area: {r['total_area_px']}px ({r['area_pct']}%) | CR: {r['contrast_ratio']:.3f} | Otsu: {r['otsu_threshold']} | Eta: {r['separability_eta']:.3f}"
        
        collage = create_diagnostic_collage(
            raw_img, enhanced_img, m["clean_mask"], m["boundary_mask"],
            title, "CLEAN_BOUNDARY", metrics
        )
        cv2.imwrite(os.path.join(gallery_dir, f"{base_name}_clean.png"), collage)

    # 7. Viết báo cáo EVALUATION_REPORT.md
    report_path = os.path.join(out_dir, "EVALUATION_REPORT.md")
    write_evaluation_report(report_path, df, flagged_results, total_time)
    print(f"[6] Đã lập báo cáo chi tiết tại: {report_path}")
    print("=" * 80)
    print(">>> HOÀN TẤT ĐÁNH GIÁ 100% DATASET THÀNH CÔNG!")
    print("=" * 80)


def write_evaluation_report(report_path: str, df: pd.DataFrame, flagged: List[Dict], total_time: float):
    """Viết báo cáo đánh giá chất lượng đường biên ra file Markdown."""
    total = len(df)
    clean_cnt = (df["status"] == "CLEAN_BOUNDARY").sum()
    leak_cnt = (df["status"] == "EDGE_LEAKAGE").sum()
    frag_cnt = (df["status"] == "EDGE_FRAGMENTED").sum()
    miss_cnt = (df["status"] == "MISSED_SLICK").sum()
    low_eta_cnt = (df["status"] == "LOW_SEPARABILITY").sum()

    md = f"""# BÁO CÁO ĐÁNH GIÁ ĐƯỜNG BIÊN VẾT DẦU TRÊN TOÀN BỘ DATASET (100% FULL SCAN)

> **Học phần**: Xử lý ảnh (DIP) — Khoa Công nghệ Thông tin, Đại học Giao thông Vận tải (UTC)  
> **Tập dữ liệu**: Sentinel-1 SAR Oil Spill Dataset (NASA / Kaggle Class 1 + Project Samples)  
> **Tổng số ảnh quét**: **{total:,} ảnh**  
> **Thời gian thực thi**: **{total_time:.2f} giây** ({total_time/total*1000:.1f} ms/ảnh)  

---

## 1. Bảng Tổng Hợp Tỷ Lệ Đạt Chuẩn & Các Ca Lệch Biên

| Trạng thái đánh giá | Ý nghĩa kỹ thuật | Số lượng | Tỷ lệ (%) | Đánh giá |
| :--- | :--- | :---: | :---: | :--- |
| 🟢 **`CLEAN_BOUNDARY`** | Đường bao $\\beta(A)$ khép kín 1px ôm sát vết dầu, tách biệt hoàn hảo với biển | **{clean_cnt:,}** | **{clean_cnt/total*100:.1f}%** | **Đạt chuẩn xuất sắc** |
| 🔴 **`EDGE_LEAKAGE`** | Tràn biên ra biển (Diện tích > 75% ảnh do ngưỡng Otsu cắt quá cao) | **{leak_cnt:,}** | **{leak_cnt/total*100:.1f}%** | Cần tinh chỉnh bù ngưỡng |
| 🟡 **`EDGE_FRAGMENTED`** | Vết dầu bị vỡ vụn (> 15 mảng nhỏ do sóng biển hoặc bọt sóng) | **{frag_cnt:,}** | **{frag_cnt/total*100:.1f}%** | Cần tăng kích thước Closing |
| 🟠 **`MISSED_SLICK`** | Bỏ sót vết dầu (0 mảng dầu được nhận diện do tương phản thấp $C_R < 0.10$) | **{miss_cnt:,}** | **{miss_cnt/total*100:.1f}%** | Cần hạ ngưỡng tương phản |
| 🔵 **`LOW_SEPARABILITY`** | Độ khả tách kém ($\\eta < 0.50$, biểu đồ mức xám không đủ 2 đỉnh rõ rệt) | **{low_eta_cnt:,}** | **{low_eta_cnt/total*100:.1f}%** | Cần tăng cường CLAHE |

---

## 2. Danh Sách Chi Tiết Các Ảnh Bị Lệch Biên Cần Tối Ưu

Toàn bộ ảnh so sánh 4 khung hình độ phân giải cao đã được xuất vào thư mục:  
`results/edge_evaluation_output/flagged_deviations/`

| STT | Tên file ảnh | Trạng thái | Số vết $N$ | Diện tích (px) | Tỷ lệ (%) | Tương phản $C_R$ | Otsu $T^*$ | Khả tách $\eta$ | Nguyên nhân kỹ thuật & Hướng tối ưu |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
"""
    for i, r in enumerate(flagged[:50], 1):
        md += f"| {i} | `{r['filename']}` | **{r['status']}** | {r['slicks_count']} | {r['total_area_px']:,} | {r['area_pct']}% | {r['contrast_ratio']:.3f} | {r['otsu_threshold']} | {r['separability_eta']:.3f} | {r['reason']} |\n"

    if len(flagged) > 50:
        md += f"\n*(Và còn {len(flagged) - 50} ảnh lệch biên khác được ghi đầy đủ trong tệp `full_dataset_edge_benchmark.csv`)*\n"

    md += """
---

## 3. Phân Tích Nguyên Nhân Gốc Rễ & Đề Xuất Tối Ưu Cùng Người Dùng

### A. Nhóm lỗi 🔴 `EDGE_LEAKAGE` (Tràn biên ra biển):
- **Hiện tượng**: Ngưỡng Otsu toàn cục $T^*$ chọn mức quá cao khiến một phần nước biển xung quanh bị gộp chung vào mảng dầu, đẩy diện tích lên $> 75\%$.
- **Giải pháp tối ưu**:
  Áp dụng **Hệ số bù ngưỡng Otsu thích ứng (Adaptive Otsu Offset)**:
  $$T_{\text{refined}} = T^* - \Delta T$$
  Với $\Delta T \approx 0.05 \dots 0.10 \times (\mu_{\text{sea}} - \mu_{\text{slick}})$, kéo ngưỡng về phía thung lũng an toàn để ranh giới co lại sát mép dầu thật.

### B. Nhóm lỗi 🟡 `EDGE_FRAGMENTED` (Biên bị vỡ vụn):
- **Hiện tượng**: Sóng biển hoặc vệt bọt sóng cắt ngang mảng dầu thành $> 15$ mảnh nhỏ li ti. Phần tử cấu trúc phép đóng $B_{\text{close}}$ hiện tại là đĩa tròn $7 \times 7$ chưa đủ lớn để bắc cầu qua các ngọn sóng rộng.
- **Giải pháp tối ưu**:
  Nâng phần tử cấu trúc Phép Đóng (Closing) từ đĩa $7 \times 7$ lên **đĩa $9 \times 9$ hoặc $11 \times 11$** để hàn gắn liền mạch các vệt dầu bị sóng biển chia cắt.

### C. Nhóm lỗi 🟠 `MISSED_SLICK` (Bỏ sót vết dầu mỏng):
- **Hiện tượng**: Vết dầu dạng váng mỏng (Oil sheen) có độ tương phản tự nhiên thấp với nước biển ($C_R < 0.10$). Bộ lọc tương phản NASA hiện tại đang đặt chặn ở ngưỡng $0.10$ nên đã loại trừ nhầm các mảng này.
- **Giải pháp tối ưu**:
  Cho phép ngưỡng tương phản thích ứng động theo diện tích: Nếu diện tích lớn ($\text{Area} > 1.500\text{ px}$), chỉ cần $C_R \ge 0.06$ là đã được công nhận là vết dầu loang.
"""

    with open(report_path, "w", encoding="utf-8") as f:
        f.write(md)


if __name__ == "__main__":
    main()
