# Kết quả SOS từ lần chạy thực tế

Số liệu được tạo bởi `scripts/summarize_results.py` từ JSON thực nghiệm, không nhập tay. Đây là đánh giá mask dầu/nền trên PNG, không phải xác nhận khả năng cảnh báo biển Việt Nam hoặc phân biệt riêng gió yếu/màng sinh học/mưa.

## Dữ liệu và lựa chọn

Sentinel train 2683, validation 671, test 839; PALSAR val 776 đánh giá ngoài miền. Seed 2026, mask >=128. Mọi lựa chọn dùng validation, test chỉ báo cáo cuối. Thiếu metadata cảnh nên không chứng minh độc lập theo cảnh.

Đã chạy **110 cấu hình lọc/ngưỡng** và **729 cấu hình vùng/đặc trưng/classifier**. Cấu hình cuối: `{"filter": {"name": "lee", "size": 7, "looks": 4}, "threshold": {"name": "otsu"}, "morphology": {"operation": "none", "min_area": 64}}`; `svm`, tham số `{'C': 10}`, nhóm đặc trưng `all`.

## Đánh giá cuối — NumPy end-to-end

| Thí nghiệm | Ảnh | Precision | Recall | F1 | Pixel IoU | FP/ảnh |
|---|---:|---:|---:|---:|---:|---:|
| test_final | 839 | 0.2541 | 0.3130 | 0.2805 | 0.6614 | 3.4839 |
| test_baseline | 839 | 0.0086 | 0.1339 | 0.0161 | 0.4367 | 58.6198 |
| test_no_classifier | 839 | 0.0753 | 0.3199 | 0.1220 | 0.5867 | 14.8927 |
| palsar_val | 776 | 0.3847 | 0.3608 | 0.3724 | 0.6423 | 2.9704 |
| validation_label64 | 671 | 0.3179 | 0.3780 | 0.3453 | 0.6526 | 3.2846 |
| validation_label128 | 671 | 0.3145 | 0.3708 | 0.3403 | 0.6524 | 3.3010 |
| validation_label192 | 671 | 0.3126 | 0.3657 | 0.3371 | 0.6517 | 3.3100 |

So với baseline, ΔF1 = +0.2644; ΔRecall = +0.1791; ΔFP/ảnh = -55.1359. So với cấu hình bỏ classifier, ΔF1 = +0.1586; ΔRecall = -0.0069; ΔFP/ảnh = -11.4088.

Đây là thay đổi đo được trên split SOS này, không là bằng chứng cải tiến tổng quát hoặc kiểm định ý nghĩa thống kê. Đối tượng suy ra từ semantic mask, ghép một-một IoU>=0.5; F1 tính micro từ tổng số đếm. Không bỏ GT nhỏ.

## Lọc/ngưỡng: kết quả tốt nhất mỗi họ ngưỡng theo F1

| Ngưỡng | Lọc | Precision | Recall | F1 |
|---|---|---:|---:|---:|
| {'name': 'otsu'} | {'name': 'lee', 'size': 7, 'looks': 4} | 0.0481 | 0.3828 | 0.0855 |
| {'name': 'niblack', 'size': 51, 'k': 0.2} | {'name': 'lee', 'size': 7, 'looks': 1} | 0.0173 | 0.2562 | 0.0325 |

## NumPy so với thư viện

| Mô hình | Nhóm | Agreement | F1 NumPy | F1 sklearn | Hội tụ | Fit NumPy (s) | Fit thư viện (s) |
|---|---|---:|---:|---:|---|---:|---:|
| cart | all | 1.0000 | 0.3373 | 0.3373 | True | 0.2144 | 0.1159 |
| svm | all | 1.0000 | 0.3403 | 0.3403 | True | 0.2765 | 0.0650 |

SVM objective NumPy = 4.0531228859; reference = 4.0531228859; max |gradient| = 9.94e-07; 177 vòng lặp. Bảng classifier dùng cùng đặc trưng reference để tách sai khác huấn luyện; bảng cuối phía trên chạy toàn pipeline NumPy.

Kiểm chứng ca biên: 118 phép, đạt=True. Ảnh SOS thật: 192 phép trên 8 ảnh validation, đạt=True. Lee reference ghép công thức bằng SciPy, không phải API Lee độc lập. Số liệu thời gian phụ thuộc máy và tải song song, không suy ra latency triển khai.

## Giới hạn và việc còn thiếu

Thiếu góc tới/gió và lớp look-alike, chưa hoàn tất mọi yêu cầu Đề 18. PNG /255 không phải chuẩn hóa góc tới. Chưa có dữ liệu biển miền Trung để đánh giá chuyển miền địa lý. PALSAR chỉ là kiểm tra ngoài sensor với cấu hình đóng băng. Cần bổ sung metadata và nhãn phù hợp trước các kết luận vật lý.

Provenance: `run_manifest.json`, `data/manifest.json`, `evaluation.json`; bảng đầy đủ: `screen.json`, `validation.json`, `model_comparison.json`. Minh họa ca lỗi nhiều/trung vị/ít lỗi ở notebook 05.

## Đối tượng chạm biên và nội vùng trên test

GT chạm biên: 2132, TP 886, recall 0.4156. GT không chạm biên: 1050, TP 110, recall 0.1048. Pixel IoU và F1 đối tượng trả lời hai câu hỏi khác nhau; IoU cao hơn không xóa được các lỗi bỏ sót/báo nhầm đối tượng.

Thời gian fit đo toàn bộ lời gọi wrapper, có thể bao gồm import thư viện lần đầu. Không dùng các con số này để kết luận tốc độ tuyệt đối giữa hai triển khai.

## Vì sao chọn Lee và cấu hình cuối?

Xem [bằng chứng lựa chọn](selection_evidence/REPORT.md): 11 cấu hình lọc gốc và 2 đối chứng bổ sung cùng cửa sổ 7×7 trên 671 ảnh validation, số đếm từng ảnh, bảng đối chiếu có kiểm soát, bootstrap thăm dò và phân tích quy tắc F1-band/Recall/thời gian. Không có định lý bảo đảm cấu hình đã chọn tối ưu.

## Sai số phép toán trên ảnh validation

Mỗi dòng tổng hợp cùng phép toán trên 8 ảnh đã chọn bằng seed 2026. MSE là trung bình bình phương sai khác đầu ra; bảng báo MSE lớn nhất trong 8 ảnh, không phải MSE toàn bộ dataset. Với vùng/đặc trưng, MSE tính trên ma trận đặc trưng khi ID vùng khớp.

| Phép toán | Cấu hình | Max absolute error lớn nhất | MSE lớn nhất |
|---|---|---:|---:|
| filter | `{"name": "none"}` | 0.000e+00 | 0.000e+00 |
| filter | `{"name": "median", "size": 3}` | 0.000e+00 | 0.000e+00 |
| filter | `{"name": "median", "size": 5}` | 0.000e+00 | 0.000e+00 |
| filter | `{"name": "gaussian", "sigma": 0.8}` | 3.331e-16 | 6.102e-33 |
| filter | `{"name": "gaussian", "sigma": 1.2}` | 3.331e-16 | 5.682e-33 |
| filter | `{"looks": 1, "name": "lee", "size": 3}` | 1.006e-11 | 3.098e-26 |
| filter | `{"looks": 4, "name": "lee", "size": 3}` | 1.382e-11 | 5.785e-26 |
| filter | `{"looks": 1, "name": "lee", "size": 5}` | 2.573e-12 | 6.683e-27 |
| filter | `{"looks": 4, "name": "lee", "size": 5}` | 4.338e-12 | 1.087e-26 |
| filter | `{"looks": 1, "name": "lee", "size": 7}` | 6.274e-13 | 2.584e-27 |
| filter | `{"looks": 4, "name": "lee", "size": 7}` | 2.737e-12 | 4.337e-27 |
| threshold | `{"name": "otsu"}` | 0.000e+00 | 0.000e+00 |
| threshold | `{"k": 0.2, "name": "niblack", "size": 15}` | 0.000e+00 | 0.000e+00 |
| threshold | `{"k": 0.5, "name": "niblack", "size": 15}` | 0.000e+00 | 0.000e+00 |
| threshold | `{"k": 0.8, "name": "niblack", "size": 15}` | 0.000e+00 | 0.000e+00 |
| threshold | `{"k": 0.2, "name": "niblack", "size": 31}` | 0.000e+00 | 0.000e+00 |
| threshold | `{"k": 0.5, "name": "niblack", "size": 31}` | 0.000e+00 | 0.000e+00 |
| threshold | `{"k": 0.8, "name": "niblack", "size": 31}` | 0.000e+00 | 0.000e+00 |
| threshold | `{"k": 0.2, "name": "niblack", "size": 51}` | 0.000e+00 | 0.000e+00 |
| threshold | `{"k": 0.5, "name": "niblack", "size": 51}` | 0.000e+00 | 0.000e+00 |
| threshold | `{"k": 0.8, "name": "niblack", "size": 51}` | 0.000e+00 | 0.000e+00 |
| regions_features | `"none"` | 3.109e-14 | 2.338e-30 |
| regions_features | `"close"` | 1.865e-14 | 1.742e-30 |
| regions_features | `"open_close"` | 1.101e-13 | 1.367e-29 |

Ví dụ tính tay có kiểm chứng: [Lee 5×5](worked_example/REPORT.md). Phân tích thất bại và mean ± SD từng ảnh: [diagnostics](diagnostics/REPORT.md).

Nhánh ngưỡng thích nghi được khảo sát riêng sau lựa chọn: [Niblack + classifier](adaptive/REPORT.md). Không thay mô hình Otsu đã khóa và không gán số liệu test cũ cho nhánh mới.
