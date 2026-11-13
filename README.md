# Phát hiện dầu tràn từ ảnh SAR — Đề 18

Dự án xử lý ảnh theo hướng **nhãn tham chiếu → thực nghiệm → chọn thuật toán → pipeline NumPy**, sử dụng Refined Deep-SAR Oil Spill (SOS). Giao diện học tập là 5 Jupyter notebook; chạy hàng loạt bằng CLI.

Demo desktop: `uv run --frozen --extra demo python scripts/demo_qt.py`.
Xem [hướng dẫn GUI](docs/DEMO_GUI.md). Nhánh bổ sung trên Sentinel-1 gốc và
gió ERA5 nằm ở [notebook 07](notebooks/external/07_sentinel_calibration.ipynb),
chưa thay thế đánh giá phát hiện dầu có nhãn của SOS.

SOS hiện có PNG và mask dầu/nền. **Chưa đáp ứng đầy đủ Đề 18** vì thiếu góc tới, thời gian/vị trí để ghép gió, và nhãn riêng các loại tương tự dầu. Không gọi phép chia 255 là chuẩn hóa góc tới hoặc suy kết quả thành khả năng cảnh báo thực tế tại miền Trung.

## Chạy

Tái tạo báo cáo số liệu và chạy lại cả **9 notebook** từ các mô hình/kết quả
đã khóa (cần đủ dữ liệu SOS, DARTIS, Sentinel-1 và QPOSD cục bộ):

```powershell
.venv/Scripts/python.exe scripts/rebuild_evidence.py
```

Lệnh đã chạy đủ 14 bước; output và 19 hình của chín notebook khớp bản đã lưu.
Nhật ký: `docs/management/evidence_rebuild_audit.json` và
`notebook_rebuild_comparison.json`. Đây là tái tạo báo cáo và phép tính notebook,
không huấn luyện lại toàn bộ, tải dữ liệu hoặc dựng Word/PPTX/video.

Một lệnh chạy chuỗi thực nghiệm SOS đã triển khai, phân tích bổ sung và notebook: `.venv/Scripts/python.exe run_experiments.py --workers 6`. Lệnh dùng checkpoint khi có; không tải dữ liệu tự động. Chỉ kiểm tra artifact đã lưu: thêm `--verify-only` (không được gọi đây là chạy lại thực nghiệm). Nhật ký từng bước lưu tại `results/sos/runner_*.json`.

Python 3.13+, cài theo `pyproject.toml` bằng `uv sync`. Dữ liệu từ [Refined SOS v1](https://zenodo.org/records/15298010), đặt tại `data/Refined-Deep-SAR/images/images/{train,val}/*.png` và `masks/masks/{train,val}/*.png`.

```powershell
.venv/Scripts/python.exe scripts/sos.py reproduce --workers 6
.venv/Scripts/python.exe scripts/explain_selection.py --workers 6
.venv/Scripts/python.exe scripts/adaptive_experiment.py --workers 6
.venv/Scripts/python.exe scripts/analyze_failures.py
.venv/Scripts/python.exe scripts/worked_example.py
.venv/Scripts/python.exe scripts/summarize_results.py
.venv/Scripts/python.exe -m unittest discover -s tests -v
.venv/Scripts/python.exe scripts/run_notebooks.py
.venv/Scripts/python.exe scripts/sos.py predict --image <duong-dan-anh.png>
```

Đầu ra suy luận: `results/prediction/mask.png`, `overlay.png`, `regions.json`. Score là điểm quyết định, không phải xác suất. Mở notebook 01–05 trong Jupyter hoặc VS Code và chọn Python `.venv`. Notebook đọc chứng cứ benchmark đã thực thi, đồng thời chạy trực tiếp các ví dụ NumPy; thiếu kết quả sẽ báo lệnh cần chạy.

Suy luận bằng nhánh ngưỡng thích nghi bổ sung: `.venv/Scripts/python.exe scripts/sos.py predict --selection results/sos/adaptive/selected.json --image <anh.png> --output results/prediction_adaptive`. Nhánh này chỉ được đánh giá validation, chưa có kết quả test độc lập mới.

CLI có từng bước `prepare`, `verify`, `screen`, `benchmark`, `select`, `evaluate`, `predict`. Benchmark có checkpoint tại `results/sos/validation/`, cache tại `.cache/sos/`. Toàn bộ grid có thể tốn nhiều thời gian/dung lượng; không dùng sample nhỏ rồi báo là toàn bộ test.

## Tài liệu

- [Hướng dẫn bàn giao](deliverables/README.md), [gói review ZIP](deliverables/packages/SAR_review_v1.zip): 204 tệp kèm manifest, chưa phải bản nộp hoàn chỉnh.
- [Báo cáo DOCX/PDF bản review v8](deliverables/report/README.md): đã kiểm tra bố cục; còn thông tin nhóm và yêu cầu khoa học chưa hoàn tất.
- [Video demo 6 phút và kiểm chứng](deliverables/video/README.md), [slide 20 trang](deliverables/presentation/README.md).
- [Mục tiêu](docs/MUC_TIEU_DU_AN.md), [giao thức](docs/GIAO_THUC_THUC_NGHIEM.md).
- [Phân công mới](docs/management/KE_HOACH_SOS_NOTEBOOK.md), [workbook](docs/management/KE_HOACH_PHAN_CONG_1008_1111_2026.xlsx).
- [Kiểm kê dữ liệu](docs/management/KIEM_TRA_REFINED_SOS.md), [manifest](data/manifest.json).
- [Nguồn dữ liệu và NASA](docs/NGUON_DU_LIEU_SAR_DAU_TRAN.md).
- Kết quả thật: `results/sos/screen.json`, `validation.json`, `model_comparison.json`, `selected.json`, `evaluation.json`.
- [Báo cáo kết quả từ lần chạy thực tế](results/sos/REPORT.md), [bàn giao](docs/management/BAN_GIAO_SOS.md).
- [Vì sao chọn Lee: số liệu có kiểm soát và quy tắc lựa chọn](results/sos/selection_evidence/REPORT.md). Code tái tạo: `scripts/explain_selection.py`; số đếm từng ảnh: `results/sos/selection_evidence/per_image.json`.
- [Thống kê toàn tập và ba ca thất bại](results/sos/diagnostics/REPORT.md): số liệu micro/macro, độ lệch chuẩn giữa các ảnh và hình từng bước; không chọn lại mô hình theo test.
- [Ví dụ Lee 5×5 tính bằng số hữu tỉ](results/sos/worked_example/REPORT.md): giải thích trọng số, đối chiếu NumPy/SciPy và giới hạn của lập luận lý thuyết.
- [Nhánh Niblack đáp ứng thao tác ngưỡng thích nghi](results/sos/adaptive/REPORT.md): thực nghiệm bổ sung trên validation; kết quả test của nhánh Otsu không áp dụng cho nhánh này.
- Nguồn dựng báo cáo theo mẫu: `docs/report/narrative.json`, `bibliography.json`, `source_audit.json`. Đây chưa phải DOCX/PDF hoàn chỉnh. Tái tạo hình báo cáo bằng `python scripts/report_figures.py`; kiểm tra nguồn bằng `python scripts/verify_report_sources.py`.

Mã theo chức năng tại `src/sar_oil/`; notebook không sao chép thuật toán. Bản cũ ở `legacy/pre_refactor_20261112/`, không import vào pipeline mới hoặc dùng số liệu cũ làm bằng chứng. Kiểm tra bảo toàn bằng `python scripts/verify_archive.py`. Dữ liệu thô không đưa lên Git.
