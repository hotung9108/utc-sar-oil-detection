# Notebook bổ sung ngoài bộ SOS chính

## Hiệu chuẩn Sentinel-1 gốc

`07_sentinel_calibration.ipynb` gồm phần hiệu chuẩn và ghép gió ERA5 tại tâm tile.
Notebook hiện mã nội suy NumPy, chạy lại hiệu chuẩn sigma/gamma trên tile SAR
gốc và đối chiếu SciPy; bảng ghi lần chạy đã xác minh nằm tại
`docs/management/physical_notebook_audit.json`.
Đây là kiểm chứng phép tính trên một tile chưa có nhãn, không phải kiểm chứng
độ chính xác phát hiện dầu.

```text
python scripts/run_notebooks.py --notebook notebooks/external/07_sentinel_calibration.ipynb
```

## Báo nhầm DARTIS

`06_dartis_false_alarms.ipynb` trình bày phép kiểm tra báo nhầm trên toàn bộ
2.290 ảnh no-oil của DARTIS bằng mô hình SOS cố định.

Hiện notebook mới được tạo và kiểm tra cấu trúc/cú pháp, **chưa chạy với kết quả
thực nghiệm đầy đủ**. Tải dữ liệu và chạy `scripts/evaluate_dartis.py` xong mới
Run All notebook. Ô đầu sẽ dừng nếu thiếu kết quả, sai hash hoặc thiếu ảnh.

Notebook này nằm riêng để năm notebook SOS vẫn tái tạo được khi máy chưa tải
DARTIS. `scripts/run_notebooks.py` hiện chỉ chạy năm notebook SOS ở cấp trên.
Mở notebook bổ sung bằng Jupyter và chọn môi trường `.venv` của dự án, hoặc chạy:

```text
python scripts/run_notebooks.py --notebook notebooks/external/06_dartis_false_alarms.ipynb
```

Mã tạo notebook: `scripts/build_dartis_notebook.py`.
Mã kiểm tra kết quả trước khi hiển thị: `scripts/dartis_results.py`.
Kiểm thử mẫu số và chặn kết quả chưa đủ: `tests/test_dartis_reporting.py`.
