# 🚀 MODULE 8: GHÉP NỐI TOÀN BỘ PIPELINE TỰ ĐỘNG END-TO-END

> **Phạm vi tài liệu tự học — cập nhật 17/11/2026:** đây là giải thích và mã minh họa độc lập, không phải pipeline đã nghiệm thu hoặc bằng chứng đạt 100% đề. Công thức giản lược, ảnh giả lập, ví dụ ghép greedy và mô phỏng trôi dầu không thay thế kết quả trong `src/sar_oil`, `scripts` và `results`. Lee không bảo đảm giữ biên tuyệt đối; agreement 100% chỉ áp dụng cho ca đã đo; F1 SOS 0,3403 là cấu hình được chọn theo quy tắc dung sai, không phải cực đại nghiêm ngặt. Ưu tiên [đối chiếu hiện tại](../../../docs/DANH_GIA_DU_AN_VA_DOI_CHIEU_DE_18.md) khi có khác biệt.

## 1. KIẾN TRÚC ĐIỀU PHỐI (ORCHESTRATION PIPELINE)

Module này là **đích đến cuối cùng** của việc tự code chay dự án. Nó xâu chuỗi toàn bộ 7 module độc lập trước đó thành một quy trình phát hiện dầu tràn khép kín:

```
[Ảnh SAR đầu vào: PNG / NPZ]
       │
       ▼ (Module 1: data_loader.py)
[Ma trận float64 [0, 1] + Chuẩn hóa góc tới gamma0]
       │
       ▼ (Module 2: speckle_filters.py)
[Khử nhiễu đốm thích nghi bằng Lee Filter 7x7 (L=4)]
       │
       ▼ (Module 3: segmentation.py)
[Phân đoạn đốm tối Otsu/Niblack & Gán nhãn liên thông Union-Find]
       │
       ▼ (Module 4: feature_extraction.py)
[Trích xuất Bảng 8 đặc trưng toán học cho từng vết]
       │
       ▼ (Module 5: machine_learning.py)
[Chuẩn hóa StandardScaler + Phán quyết Linear SVM C=10]
       │
       ├──> (Nếu có nhãn GT) ──> [Module 6: evaluation.py: Tính IoU, Precision, Recall, F1]
       │
       └──> (Nếu phát hiện dầu) ──> [Module 7: drift_simulation.py: Dự báo trôi dạt 48h]
       │
       ▼
[KẾT QUẢ CUỐI CÙNG]
- Mặt nạ nhị phân vết dầu (Binary Oil Mask)
- Ảnh Overlay trực quan phủ màu cảnh báo
- Báo cáo số liệu đặc trưng và toạ độ trôi dạt GeoJSON
```

---

## 2. HỢP ĐỒNG ĐẦU VÀO VÀ ĐẦU RA (INPUT/OUTPUT CONTRACT)

- **Đầu vào (Input):**
  - Mảng ảnh 2D `img` (kích thước $H \times W$, giá trị float64).
  - Tùy chọn: Nhãn mặt đất `gt_mask` (nếu muốn chấm điểm đánh giá tự động).
  - Tùy chọn: Tọa độ địa lý tâm ảnh `(center_lat, center_lon)` và vector gió `(u_wind, v_wind)`.

- **Đầu ra (Output):**
  - `clean_img`: Ảnh đã lọc nhiễu Lee Filter.
  - `candidate_mask`: Mặt nạ tất cả các đốm tối ban đầu.
  - `oil_mask`: Mặt nạ chỉ chứa các vết dầu thật đã qua kiểm duyệt SVM.
  - `features_table`: Bảng dữ liệu 8 đặc trưng toán học của từng vết.
  - `drift_forecast`: Quỹ đạo trôi dạt và diện tích mở rộng $T_0 \to +48\text{h}$.

Mở file `full_pipeline.py` để chạy toàn bộ hệ thống!
