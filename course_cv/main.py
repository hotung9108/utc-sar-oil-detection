"""
Chương trình chính: main.py
Dự án: Phát hiện vết dầu tràn trên ảnh SAR - Đề 18
Tuân thủ 100% giáo trình môn Xử lý ảnh - TS. Phan Thanh Toàn (Đại học Giao thông vận tải - UTC)

Chương trình này hoạt động hoàn toàn tách biệt với mã nguồn cũ, CHỈ sử dụng
các kỹ thuật thị giác máy tính cổ điển đã được giảng dạy trong slide:
- Chương 3: Lọc trung vị (Median Filter) khử nhiễu đốm SAR
- Chương 5: Đạo hàm Sobel tính độ dốc gradient và kiểm tra sắc nét đường biên
- Chương 6: Hình thái học (Opening, Closing, Fill holes, Area filtering, Boundary Extraction beta(A))
- Chương 7: Phân vùng ảnh bằng ngưỡng tối ưu Otsu và tính khả tách eta

Kết quả trực quan:
Chỉ vẽ đường viền ĐỎ bao quanh vệt dầu phát hiện được (không vẽ khung chữ nhật, không vẽ chữ).
"""

import os
import sys
import glob
import time
import argparse
import cv2
import numpy as np

# Đảm bảo in tiếng Việt trên console Windows không bị lỗi cp1252
if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Thêm đường dẫn gốc để import module course_cv
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from course_cv.pipeline import detect_oil_spill_pipeline

def process_dataset(
    input_dir: str = "data/sample",
    output_dir: str = "outputs_slide",
    min_area: int = 150,
    max_area: int = 120000,
    min_contrast: float = 12.0,
    min_boundary_grad: float = 6.0,
    min_otsu_separability: float = 0.10,
    max_images_per_class: int = None
):
    print("=" * 70)
    print("CHƯƠNG TRÌNH PHÁT HIỆN VẾT DẦU TRÀN SAR (CHUẨN GIÁO TRÌNH XLA - UTC)")
    print("Giảng viên: TS. Phan Thanh Toàn")
    print(f"Thư mục dữ liệu vào:  {input_dir}")
    print(f"Thư mục kết quả ra:   {output_dir}")
    print("=" * 70)

    # Quét tất cả các file ảnh jpg, png trong input_dir
    valid_exts = ("*.jpg", "*.jpeg", "*.png", "*.bmp")
    all_files = []
    
    # Duyệt đệ quy hoặc theo cấu trúc thư mục con
    for root, dirs, files in os.walk(input_dir):
        for f in files:
            if f.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp')):
                all_files.append(os.path.join(root, f))
                
    if not all_files:
        print(f"[CẢNH BÁO] Không tìm thấy ảnh nào trong {input_dir}")
        return

    print(f"Tìm thấy tổng cộng: {len(all_files)} ảnh.")

    # Phân nhóm theo thư mục con
    classes = {}
    for fpath in all_files:
        rel = os.path.relpath(fpath, input_dir)
        parts = rel.split(os.sep)
        group = parts[0] if len(parts) > 1 else "root"
        classes.setdefault(group, []).append(fpath)

    total_processed = 0
    total_with_oil = 0
    start_time = time.time()

    for group_name, file_list in classes.items():
        if max_images_per_class is not None:
            files_to_run = file_list[:max_images_per_class]
        else:
            files_to_run = file_list

        out_subfolder = os.path.join(output_dir, group_name) if group_name != "root" else output_dir
        os.makedirs(out_subfolder, exist_ok=True)

        print(f"\n[XỬ LÝ NHÓM: {group_name}] ({len(files_to_run)} ảnh)...")
        detected_in_group = 0

        for idx, img_path in enumerate(files_to_run, 1):
            fname = os.path.basename(img_path)
            img = cv2.imread(img_path)
            if img is None:
                continue

            vis_img, oil_mask, detections = detect_oil_spill_pipeline(
                image=img,
                min_area=min_area,
                max_area=max_area,
                min_contrast=min_contrast,
                min_boundary_grad=min_boundary_grad,
                min_otsu_separability=min_otsu_separability,
                border_thickness=2
            )

            # Lưu ảnh kết quả với đường viền đỏ ôm sát vết dầu
            out_file = os.path.join(out_subfolder, fname)
            cv2.imwrite(out_file, vis_img)

            total_processed += 1
            if len(detections) > 0:
                detected_in_group += 1
                total_with_oil += 1

            if idx % 20 == 0 or idx == len(files_to_run):
                print(f"  -> Đã xử lý {idx}/{len(files_to_run)} ảnh | Phát hiện có vệt dầu: {detected_in_group}")

    elapsed = time.time() - start_time
    print("\n" + "=" * 70)
    print(f"HOÀN THÀNH XỬ LÝ TOÀN BỘ!")
    print(f"- Tổng số ảnh đã phân tích: {total_processed}")
    print(f"- Số ảnh phát hiện có vết dầu: {total_with_oil}")
    print(f"- Thời gian thực thi: {elapsed:.2f} giây ({elapsed / max(1, total_processed) * 1000:.1f} ms/ảnh)")
    print(f"- Toàn bộ ảnh kết quả được lưu tại: {os.path.abspath(output_dir)}")
    print("=" * 70)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Chương trình Computer Vision phát hiện dầu tràn chuẩn Slide UTC")
    parser.add_argument("--input_dir", type=str, default="data/sample", help="Thư mục chứa ảnh đầu vào")
    parser.add_argument("--output_dir", type=str, default="outputs_slide", help="Thư mục lưu ảnh kết quả")
    parser.add_argument("--min_area", type=int, default=150, help="Diện tích tối thiểu (px)")
    parser.add_argument("--max_area", type=int, default=120000, help="Diện tích tối đa (px)")
    parser.add_argument("--min_contrast", type=float, default=12.0, help="Độ tương phản tối thiểu")
    parser.add_argument("--min_boundary_grad", type=float, default=6.0, help="Gradient biên Sobel tối thiểu")
    parser.add_argument("--min_separability", type=float, default=0.10, help="Tính khả tách Otsu tối thiểu")
    parser.add_argument("--max_images", type=int, default=None, help="Giới hạn số ảnh mỗi lớp (mặc định chạy hết)")

    args = parser.parse_args()

    process_dataset(
        input_dir=args.input_dir,
        output_dir=args.output_dir,
        min_area=args.min_area,
        max_area=args.max_area,
        min_contrast=args.min_contrast,
        min_boundary_grad=args.min_boundary_grad,
        min_otsu_separability=args.min_separability,
        max_images_per_class=args.max_images
    )
