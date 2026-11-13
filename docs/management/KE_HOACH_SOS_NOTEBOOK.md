# Phân công SOS và notebook — 13–15/11/2026

Deadline: 23:59 ngày 15/11/2026, Asia/Saigon. Các việc S01–S03 nối tiếp lịch sử W và đợt dọn R. Mã do công cụ hỗ trợ tạo không đồng nghĩa thành viên đã hoàn thành: từng người phải chạy, giải thích và gửi minh chứng để người review xác nhận. Trạng thái ban đầu “Chưa bắt đầu”; không tự điền giờ thực tế hoặc ghi nhận đóng góp.

| Thành viên | Trách nhiệm | Module / notebook |
|---|---|---|
| TV1 — Tiến Sơn Trần | Tích hợp pipeline, CLI và kết quả cuối | pipeline.py; scripts/sos.py; 05_final_pipeline.ipynb |
| TV2 — Lương Tiến Dũng | CART/SVM NumPy và đối chứng sklearn | models.py; 04_cart_svm_numpy.ipynb |
| TV3 — Hồ Việt Tùng | Lọc speckle và phân ngưỡng thích nghi | core.py/reference.py: filter_image, threshold; 02_filter_threshold_benchmark.ipynb |
| TV4 — Nguyễn Hải Hiếu | Liên thông, hình thái và đặc trưng vùng | core.py/reference.py: label, postprocess, features; 03_regions_and_features.ipynb |
| TV5 — Phạm Minh Tuấn | Dữ liệu, ground truth và đánh giá đối tượng | data.py; evaluation.py; 01_data_and_ground_truth.ipynb |

## Ngày 13/11

| ID | Nhiệm vụ | Điều kiện nghiệm thu | Reviewer |
|---|---|---|---|
| S01-TV1 | Nối CLI, định nghĩa input/output không truyền GT vào predict | CLI chạy từ root; output mask/overlay/JSON; không dùng nhãn trong suy luận | Lương Tiến Dũng |
| S01-TV2 | Tự cài CART Gini và SVM squared hinge; kiểm chứng objective | Cùng objective với thư viện; single class báo lỗi; model lưu/đọc đúng | Hồ Việt Tùng |
| S01-TV3 | Tự cài median, Gaussian, Lee, Otsu, Niblack; đối chiếu padding | Sai số float atol1e-6/rtol1e-5; xử lý constant/tiny/border | Nguyễn Hải Hiếu |
| S01-TV4 | Tự cài morphology, liên thông 8 và 8 đặc trưng vùng | Định nghĩa chu vi thống nhất; mask rỗng và nền rỗng không NaN | Phạm Minh Tuấn |
| S01-TV5 | Kiểm kê SOS, hash manifest, chia 2683/671/839, khóa test | Không trùng hash chính xác giữa split; công bố thiếu scene metadata | Tiến Sơn Trần |

## Ngày 14/11

| ID | Nhiệm vụ | Điều kiện nghiệm thu | Reviewer |
|---|---|---|---|
| S02-TV1 | Chạy benchmark tích hợp, quản lý checkpoint và lựa chọn validation | 729 cấu hình đủ log; test chưa dùng để lựa chọn | Lương Tiến Dũng |
| S02-TV2 | Chạy 9 cấu hình classifier × 3 nhóm đặc trưng; đối chiếu hai họ NumPy | Báo agreement, object F1, objective và hội tụ thực tế | Hồ Việt Tùng |
| S02-TV3 | Đọc bảng 110 cấu hình, giải thích ảnh hưởng lọc/ngưỡng | 110 cấu hình cùng 671 ảnh; lựa chọn top3 theo quy tắc đã chốt | Nguyễn Hải Hiếu |
| S02-TV4 | So sánh morphology/diện tích và shape/intensity/all | 27 cấu hình trích vùng; không loại đối tượng GT nhỏ | Phạm Minh Tuấn |
| S02-TV5 | Kiểm thử matching IoU, đối tượng chạm biên, tổng TP/FP/FN | Ghép một-một IoU>=0.5; micro PRF; N/A khi thiếu mẫu số | Tiến Sơn Trần |

## Ngày 15/11

| ID | Nhiệm vụ | Điều kiện nghiệm thu | Reviewer |
|---|---|---|---|
| S03-TV1 | Chạy test cuối/ablation; hoàn thiện notebook 05, demo CLI | Run All notebook; báo cả kết quả kém, không chọn lại theo test | Lương Tiến Dũng |
| S03-TV2 | Hoàn thiện notebook 04; giải thích convergence và khác biệt sklearn | Chỉ chọn mô hình hội tụ; người phụ trách giải thích được code | Hồ Việt Tùng |
| S03-TV3 | Hoàn thiện notebook 02; bổ sung ví dụ lỗi và bảng sai số thật | Không gọi chia255 là chuẩn hóa góc tới; Lee PNG có giới hạn | Nguyễn Hải Hiếu |
| S03-TV4 | Hoàn thiện notebook 03; giải thích gradient, perimeter, ring | Đặc trưng minh họa khớp code và reference | Phạm Minh Tuấn |
| S03-TV5 | Hoàn thiện notebook 01; xác minh số liệu, độ nhạy mask và giới hạn SOS | Hash, seed, versions, test839 và PALSAR776 đúng; không bịa look-alike | Tiến Sơn Trần |

Mỗi việc ước lượng 4 giờ, không phải giờ đã làm. TV3/TV4 sửa các hàm khác nhau trong core.py và reference.py, cần phối hợp trước khi merge. TV5 khóa split và giao thức trước benchmark; TV1 chỉ mở test sau khi TV2/3/4 kiểm chứng xong. Mỗi notebook phải Restart & Run All được bằng cùng môi trường.

## Phần bổ sung sau benchmark — giao việc kiểm tra lại

Các sản phẩm dưới đây được trợ lý hỗ trợ xây dựng; bảng này giao trách nhiệm
kiểm tra và giải thích, **không xác nhận thành viên đã thực hiện hoặc số giờ đã làm**.
Không tự điền điểm đóng góp hay chữ ký từ các artifact tự động.

| Phụ trách | Việc cần kiểm tra | Bằng chứng/đầu ra | Điều kiện nghiệm thu |
|---|---|---|---|
| TV1 — Tiến Sơn Trần | Demo PyQt, xuất kết quả, video và gói bàn giao | `scripts/demo_qt.py`, `demo_engine.py`, `record_demo_video.py`, `docs/DEMO_GUI.md` | Chạy cả hai nhánh và hai ca lỗi; kiểm tra chọn file/lưu thư mục thủ công; video đủ 5–7 phút, phụ đề đúng kết quả |
| TV2 — Lương Tiến Dũng | Giải thích hiệu chuẩn DN/LUT và giới hạn so sánh thư viện | `scripts/sentinel_calibration_demo.py`, `results/physical/calibration.json` | Tái tạo sai số NumPy–SciPy; phân biệt gamma hình học với loại hết phụ thuộc góc/gió; không gọi đây là đối chứng SNAP |
| TV3 — Hồ Việt Tùng | Kiểm tra góc tới và phép ghép gió | `scripts/fetch_scene_wind.py`, notebook 07, `results/physical/wind.json` | Kiểm tra UTC, đơn vị m/s, khoảng cách ô lưới, quy ước hướng FROM và nội suy u/v; không gán metadata này cho SOS |
| TV4 — Nguyễn Hải Hiếu | Kiểm tra liên hệ vùng ứng viên, đặc trưng và ca thất bại trong GUI | Bảng đặc trưng GUI; `results/sos/diagnostics/` | Đối chiếu số vùng, score và mask với pipeline; giải thích khác biệt TP pixel với TP đối tượng |
| TV5 — Phạm Minh Tuấn | Hoàn tất DARTIS và kiểm tra phạm vi nhãn tham chiếu | `results/dartis/`, notebook 06, `scripts/dartis_results.py` | Tôn trọng giới hạn tải; đủ 2.290 ảnh và hash trước đánh giá; không diễn giải cụm K-means là nhãn mưa/gió yếu/màng sinh học |

Các việc chưa thể xác nhận hoàn thành: đánh giá nhánh vật lý trên mẫu có nhãn
đã căn chỉnh, nhãn nguyên nhân look-alike, thông tin bìa chính thức, biên bản
và đóng góp thật. Theo dõi riêng tại `completion_audit.json`.

Giao thức, thuật toán và tiêu chí lựa chọn: [GIAO_THUC_THUC_NGHIEM.md](../GIAO_THUC_THUC_NGHIEM.md). Phân công máy đọc: sos_tasks.json; workbook giữ các ô minh chứng và giờ thực tế cho người thực hiện.
