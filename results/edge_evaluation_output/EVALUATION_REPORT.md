# BÁO CÁO ĐÁNH GIÁ ĐƯỜNG BIÊN VẾT DẦU TRÊN TOÀN BỘ DATASET (100% FULL SCAN)

> **Học phần**: Xử lý ảnh (DIP) — Khoa Công nghệ Thông tin, Đại học Giao thông Vận tải (UTC)  
> **Tập dữ liệu**: Sentinel-1 SAR Oil Spill Dataset (NASA / Kaggle Class 1 + Project Samples)  
> **Tổng số ảnh quét**: **1,853 ảnh**  
> **Thời gian thực thi**: **58.79 giây** (31.7 ms/ảnh)  

---

## 1. Bảng Tổng Hợp Tỷ Lệ Đạt Chuẩn & Các Ca Lệch Biên

| Trạng thái đánh giá | Ý nghĩa kỹ thuật | Số lượng | Tỷ lệ (%) | Đánh giá |
| :--- | :--- | :---: | :---: | :--- |
| 🟢 **`CLEAN_BOUNDARY`** | Đường bao $\beta(A)$ khép kín 1px ôm sát vết dầu, tách biệt hoàn hảo với biển | **1,121** | **60.5%** | **Đạt chuẩn xuất sắc** |
| 🔴 **`EDGE_LEAKAGE`** | Tràn biên ra biển (Diện tích > 75% ảnh do ngưỡng Otsu cắt quá cao) | **48** | **2.6%** | Cần tinh chỉnh bù ngưỡng |
| 🟡 **`EDGE_FRAGMENTED`** | Vết dầu bị vỡ vụn (> 15 mảng nhỏ do sóng biển hoặc bọt sóng) | **322** | **17.4%** | Cần tăng kích thước Closing |
| 🟠 **`MISSED_SLICK`** | Bỏ sót vết dầu (0 mảng dầu được nhận diện do tương phản thấp $C_R < 0.10$) | **49** | **2.6%** | Cần hạ ngưỡng tương phản |
| 🔵 **`LOW_SEPARABILITY`** | Độ khả tách kém ($\eta < 0.50$, biểu đồ mức xám không đủ 2 đỉnh rõ rệt) | **308** | **16.6%** | Cần tăng cường CLAHE |

---

## 2. Danh Sách Chi Tiết Các Ảnh Bị Lệch Biên Cần Tối Ưu

Toàn bộ ảnh so sánh 4 khung hình độ phân giải cao đã được xuất vào thư mục:  
`results/edge_evaluation_output/flagged_deviations/`

| STT | Tên file ảnh | Trạng thái | Số vết $N$ | Diện tích (px) | Tỷ lệ (%) | Tương phản $C_R$ | Otsu $T^*$ | Khả tách $\eta$ | Nguyên nhân kỹ thuật & Hướng tối ưu |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| 1 | `sea_surface_03.jpg` | **FALSE_ALARM** | 3 | 81,055 | 50.66% | 0.207 | 162 | 0.653 | Bắt nhầm biển sạch thành 3 vết dầu (50.66%) |
| 2 | `class_1_00003.jpg` | **LOW_SEPARABILITY** | 1 | 1,655 | 1.03% | 0.324 | 88 | 0.496 | Độ khả tách Otsu kém (eta = 0.496 < 0.50), ranh giới dễ lem |
| 3 | `sea_surface_02.jpg` | **FALSE_ALARM** | 5 | 37,389 | 23.37% | 0.423 | 134 | 0.670 | Bắt nhầm biển sạch thành 5 vết dầu (23.37%) |
| 4 | `sea_surface_01.jpg` | **FALSE_ALARM** | 10 | 49,039 | 30.65% | 0.375 | 115 | 0.674 | Bắt nhầm biển sạch thành 10 vết dầu (30.65%) |
| 5 | `sea_surface_05.jpg` | **FALSE_ALARM** | 12 | 62,039 | 38.77% | 0.192 | 104 | 0.649 | Bắt nhầm biển sạch thành 12 vết dầu (38.77%) |
| 6 | `class_1_00002.jpg` | **MISSED_SLICK** | 0 | 0 | 0.0% | 0.000 | 107 | 0.644 | Bỏ sót vết dầu (0 vết dầu phát hiện được, có thể do vệt quá mỏng CR < 0.10) |
| 7 | `sea_surface_04.jpg` | **FALSE_ALARM** | 4 | 2,953 | 1.85% | 0.103 | 116 | 0.647 | Bắt nhầm biển sạch thành 4 vết dầu (1.85%) |
| 8 | `oil_slick_04.jpg` | **EDGE_FRAGMENTED** | 23 | 36,470 | 22.79% | 0.215 | 134 | 0.541 | Biên bị vỡ vụn thành 23 mảng nhỏ rời rạc (chưa hàn gắn hết bọt sóng) |
| 9 | `class_1_00014.jpg` | **EDGE_LEAKAGE** | 4 | 124,795 | 78.0% | 0.223 | 107 | 0.462 | Tràn biên ra biển (78.0% ảnh bị coi là dầu, ngưỡng Otsu cắt quá cao) |
| 10 | `class_1_00011.jpg` | **LOW_SEPARABILITY** | 4 | 4,811 | 3.01% | 0.191 | 116 | 0.446 | Độ khả tách Otsu kém (eta = 0.446 < 0.50), ranh giới dễ lem |
| 11 | `class_1_00008.jpg` | **LOW_SEPARABILITY** | 1 | 470 | 0.29% | 0.478 | 93 | 0.460 | Độ khả tách Otsu kém (eta = 0.460 < 0.50), ranh giới dễ lem |
| 12 | `class_1_00016.jpg` | **LOW_SEPARABILITY** | 1 | 3,328 | 2.08% | 0.299 | 97 | 0.476 | Độ khả tách Otsu kém (eta = 0.476 < 0.50), ranh giới dễ lem |
| 13 | `class_1_00023.jpg` | **MISSED_SLICK** | 0 | 0 | 0.0% | 0.000 | 93 | 0.527 | Bỏ sót vết dầu (0 vết dầu phát hiện được, có thể do vệt quá mỏng CR < 0.10) |
| 14 | `class_1_00007.jpg` | **EDGE_FRAGMENTED** | 23 | 36,470 | 22.79% | 0.215 | 134 | 0.541 | Biên bị vỡ vụn thành 23 mảng nhỏ rời rạc (chưa hàn gắn hết bọt sóng) |
| 15 | `class_1_00021.jpg` | **LOW_SEPARABILITY** | 3 | 16,304 | 10.19% | 0.264 | 144 | 0.378 | Độ khả tách Otsu kém (eta = 0.378 < 0.50), ranh giới dễ lem |
| 16 | `class_1_00015.jpg` | **MISSED_SLICK** | 0 | 0 | 0.0% | 0.000 | 92 | 0.643 | Bỏ sót vết dầu (0 vết dầu phát hiện được, có thể do vệt quá mỏng CR < 0.10) |
| 17 | `class_1_00027.jpg` | **LOW_SEPARABILITY** | 1 | 4,542 | 2.84% | 0.346 | 88 | 0.419 | Độ khả tách Otsu kém (eta = 0.419 < 0.50), ranh giới dễ lem |
| 18 | `class_1_00034.jpg` | **LOW_SEPARABILITY** | 1 | 7,472 | 4.67% | 0.324 | 77 | 0.498 | Độ khả tách Otsu kém (eta = 0.498 < 0.50), ranh giới dễ lem |
| 19 | `class_1_00032.jpg` | **LOW_SEPARABILITY** | 4 | 5,030 | 3.14% | 0.258 | 108 | 0.472 | Độ khả tách Otsu kém (eta = 0.472 < 0.50), ranh giới dễ lem |
| 20 | `class_1_00028.jpg` | **LOW_SEPARABILITY** | 2 | 11,470 | 7.17% | 0.151 | 144 | 0.455 | Độ khả tách Otsu kém (eta = 0.455 < 0.50), ranh giới dễ lem |
| 21 | `class_1_00046.jpg` | **LOW_SEPARABILITY** | 1 | 8,138 | 5.09% | 0.282 | 100 | 0.485 | Độ khả tách Otsu kém (eta = 0.485 < 0.50), ranh giới dễ lem |
| 22 | `class_1_00037.jpg` | **EDGE_FRAGMENTED** | 22 | 67,536 | 42.21% | 0.198 | 142 | 0.597 | Biên bị vỡ vụn thành 22 mảng nhỏ rời rạc (chưa hàn gắn hết bọt sóng) |
| 23 | `class_1_00054.jpg` | **LOW_SEPARABILITY** | 2 | 2,478 | 1.55% | 0.418 | 119 | 0.468 | Độ khả tách Otsu kém (eta = 0.468 < 0.50), ranh giới dễ lem |
| 24 | `class_1_00055.jpg` | **LOW_SEPARABILITY** | 2 | 4,758 | 2.97% | 0.332 | 98 | 0.454 | Độ khả tách Otsu kém (eta = 0.454 < 0.50), ranh giới dễ lem |
| 25 | `class_1_00053.jpg` | **LOW_SEPARABILITY** | 3 | 2,770 | 1.73% | 0.287 | 111 | 0.491 | Độ khả tách Otsu kém (eta = 0.491 < 0.50), ranh giới dễ lem |
| 26 | `class_1_00062.jpg` | **LOW_SEPARABILITY** | 1 | 709 | 0.44% | 0.186 | 95 | 0.491 | Độ khả tách Otsu kém (eta = 0.491 < 0.50), ranh giới dễ lem |
| 27 | `class_1_00077.jpg` | **LOW_SEPARABILITY** | 2 | 103,369 | 64.61% | 0.149 | 89 | 0.489 | Độ khả tách Otsu kém (eta = 0.489 < 0.50), ranh giới dễ lem |
| 28 | `class_1_00074.jpg` | **LOW_SEPARABILITY** | 4 | 15,704 | 9.81% | 0.255 | 98 | 0.458 | Độ khả tách Otsu kém (eta = 0.458 < 0.50), ranh giới dễ lem |
| 29 | `class_1_00070.jpg` | **LOW_SEPARABILITY** | 1 | 47,640 | 29.78% | 0.111 | 125 | 0.426 | Độ khả tách Otsu kém (eta = 0.426 < 0.50), ranh giới dễ lem |
| 30 | `class_1_00069.jpg` | **LOW_SEPARABILITY** | 1 | 2,880 | 1.8% | 0.296 | 121 | 0.439 | Độ khả tách Otsu kém (eta = 0.439 < 0.50), ranh giới dễ lem |
| 31 | `class_1_00071.jpg` | **LOW_SEPARABILITY** | 3 | 23,422 | 14.64% | 0.141 | 115 | 0.396 | Độ khả tách Otsu kém (eta = 0.396 < 0.50), ranh giới dễ lem |
| 32 | `class_1_00082.jpg` | **MISSED_SLICK** | 0 | 0 | 0.0% | 0.000 | 116 | 0.593 | Bỏ sót vết dầu (0 vết dầu phát hiện được, có thể do vệt quá mỏng CR < 0.10) |
| 33 | `class_1_00083.jpg` | **MISSED_SLICK** | 0 | 0 | 0.0% | 0.000 | 113 | 0.552 | Bỏ sót vết dầu (0 vết dầu phát hiện được, có thể do vệt quá mỏng CR < 0.10) |
| 34 | `class_1_00086.jpg` | **LOW_SEPARABILITY** | 2 | 5,575 | 3.48% | 0.277 | 110 | 0.449 | Độ khả tách Otsu kém (eta = 0.449 < 0.50), ranh giới dễ lem |
| 35 | `class_1_00084.jpg` | **EDGE_FRAGMENTED** | 18 | 58,449 | 36.53% | 0.204 | 131 | 0.537 | Biên bị vỡ vụn thành 18 mảng nhỏ rời rạc (chưa hàn gắn hết bọt sóng) |
| 36 | `class_1_00102.jpg` | **LOW_SEPARABILITY** | 1 | 3,959 | 2.47% | 0.334 | 86 | 0.437 | Độ khả tách Otsu kém (eta = 0.437 < 0.50), ranh giới dễ lem |
| 37 | `class_1_00111.jpg` | **LOW_SEPARABILITY** | 1 | 5,513 | 3.45% | 0.418 | 74 | 0.465 | Độ khả tách Otsu kém (eta = 0.465 < 0.50), ranh giới dễ lem |
| 38 | `class_1_00106.jpg` | **LOW_SEPARABILITY** | 1 | 7,585 | 4.74% | 0.354 | 98 | 0.497 | Độ khả tách Otsu kém (eta = 0.497 < 0.50), ranh giới dễ lem |
| 39 | `class_1_00104.jpg` | **LOW_SEPARABILITY** | 1 | 3,799 | 2.37% | 0.285 | 105 | 0.475 | Độ khả tách Otsu kém (eta = 0.475 < 0.50), ranh giới dễ lem |
| 40 | `class_1_00117.jpg` | **LOW_SEPARABILITY** | 2 | 3,647 | 2.28% | 0.364 | 102 | 0.445 | Độ khả tách Otsu kém (eta = 0.445 < 0.50), ranh giới dễ lem |
| 41 | `class_1_00116.jpg` | **LOW_SEPARABILITY** | 7 | 10,896 | 6.81% | 0.296 | 124 | 0.494 | Độ khả tách Otsu kém (eta = 0.494 < 0.50), ranh giới dễ lem |
| 42 | `class_1_00101.jpg` | **EDGE_FRAGMENTED** | 26 | 40,999 | 25.62% | 0.253 | 121 | 0.590 | Biên bị vỡ vụn thành 26 mảng nhỏ rời rạc (chưa hàn gắn hết bọt sóng) |
| 43 | `class_1_00134.jpg` | **LOW_SEPARABILITY** | 1 | 4,019 | 2.51% | 0.378 | 104 | 0.498 | Độ khả tách Otsu kém (eta = 0.498 < 0.50), ranh giới dễ lem |
| 44 | `class_1_00124.jpg` | **LOW_SEPARABILITY** | 2 | 10,192 | 6.37% | 0.283 | 101 | 0.473 | Độ khả tách Otsu kém (eta = 0.473 < 0.50), ranh giới dễ lem |
| 45 | `class_1_00137.jpg` | **MISSED_SLICK** | 0 | 0 | 0.0% | 0.000 | 116 | 0.611 | Bỏ sót vết dầu (0 vết dầu phát hiện được, có thể do vệt quá mỏng CR < 0.10) |
| 46 | `class_1_00125.jpg` | **EDGE_FRAGMENTED** | 28 | 47,971 | 29.98% | 0.242 | 127 | 0.549 | Biên bị vỡ vụn thành 28 mảng nhỏ rời rạc (chưa hàn gắn hết bọt sóng) |
| 47 | `class_1_00145.jpg` | **MISSED_SLICK** | 0 | 0 | 0.0% | 0.000 | 95 | 0.513 | Bỏ sót vết dầu (0 vết dầu phát hiện được, có thể do vệt quá mỏng CR < 0.10) |
| 48 | `class_1_00128.jpg` | **EDGE_FRAGMENTED** | 29 | 42,304 | 26.44% | 0.228 | 165 | 0.536 | Biên bị vỡ vụn thành 29 mảng nhỏ rời rạc (chưa hàn gắn hết bọt sóng) |
| 49 | `class_1_00135.jpg` | **LOW_SEPARABILITY** | 4 | 16,102 | 10.06% | 0.173 | 103 | 0.437 | Độ khả tách Otsu kém (eta = 0.437 < 0.50), ranh giới dễ lem |
| 50 | `class_1_00154.jpg` | **EDGE_LEAKAGE** | 3 | 128,234 | 80.15% | 0.384 | 66 | 0.589 | Tràn biên ra biển (80.15% ảnh bị coi là dầu, ngưỡng Otsu cắt quá cao) |

*(Và còn 682 ảnh lệch biên khác được ghi đầy đủ trong tệp `full_dataset_edge_benchmark.csv`)*

---

## 3. Phân Tích Nguyên Nhân Gốc Rễ & Đề Xuất Tối Ưu Cùng Người Dùng

### A. Nhóm lỗi 🔴 `EDGE_LEAKAGE` (Tràn biên ra biển):
- **Hiện tượng**: Ngưỡng Otsu toàn cục $T^*$ chọn mức quá cao khiến một phần nước biển xung quanh bị gộp chung vào mảng dầu, đẩy diện tích lên $> 75\%$.
- **Giải pháp tối ưu**:
  Áp dụng **Hệ số bù ngưỡng Otsu thích ứng (Adaptive Otsu Offset)**:
  $$T_{	ext{refined}} = T^* - \Delta T$$
  Với $\Delta T pprox 0.05 \dots 0.10 	imes (\mu_{	ext{sea}} - \mu_{	ext{slick}})$, kéo ngưỡng về phía thung lũng an toàn để ranh giới co lại sát mép dầu thật.

### B. Nhóm lỗi 🟡 `EDGE_FRAGMENTED` (Biên bị vỡ vụn):
- **Hiện tượng**: Sóng biển hoặc vệt bọt sóng cắt ngang mảng dầu thành $> 15$ mảnh nhỏ li ti. Phần tử cấu trúc phép đóng $B_{	ext{close}}$ hiện tại là đĩa tròn $7 	imes 7$ chưa đủ lớn để bắc cầu qua các ngọn sóng rộng.
- **Giải pháp tối ưu**:
  Nâng phần tử cấu trúc Phép Đóng (Closing) từ đĩa $7 	imes 7$ lên **đĩa $9 	imes 9$ hoặc $11 	imes 11$** để hàn gắn liền mạch các vệt dầu bị sóng biển chia cắt.

### C. Nhóm lỗi 🟠 `MISSED_SLICK` (Bỏ sót vết dầu mỏng):
- **Hiện tượng**: Vết dầu dạng váng mỏng (Oil sheen) có độ tương phản tự nhiên thấp với nước biển ($C_R < 0.10$). Bộ lọc tương phản NASA hiện tại đang đặt chặn ở ngưỡng $0.10$ nên đã loại trừ nhầm các mảng này.
- **Giải pháp tối ưu**:
  Cho phép ngưỡng tương phản thích ứng động theo diện tích: Nếu diện tích lớn ($	ext{Area} > 1.500	ext{ px}$), chỉ cần $C_R \ge 0.06$ là đã được công nhận là vết dầu loang.
