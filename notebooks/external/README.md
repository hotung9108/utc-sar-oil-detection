# Notebook bổ sung ngoài bộ SOS chính

## Hai pipeline cố định trên PALSAR

`09_palsar_frozen_pipelines.ipynb` đã chạy ba ô mã, hai hình đã được xem trực
tiếp. Toàn bộ 3.101 ảnh `external_train` được chấm cho cả Otsu và Niblack đã
khóa; không fit lại hoặc thay tham số. F1 đối tượng lần lượt 0,339645 và
0,249476. Notebook kiểm tra hash và tổng hợp lại số đếm, sau đó chạy lại hai
mô hình trên ảnh có ID nhỏ nhất để đối chiếu với kết quả đã lưu.

Đây là phép thử bổ sung chuyển sensor; không chứng minh độc lập theo cảnh
hoặc tác dụng riêng của thuật toán ngưỡng. Chi tiết và giao thức nằm tại
`results/sos/external_palsar_train/`; audit notebook tại
`docs/management/palsar_notebook_audit.json`. Kết quả này đã được đưa vào DOCX
v10 và PPTX v4; các bản DOCX v9, PPTX v3 và ZIP v2 không chứa cập nhật này.

```text
python scripts/run_notebooks.py --notebook notebooks/external/09_palsar_frozen_pipelines.ipynb
```

## Thẩm định nguồn nhãn QPOSD

`08_qposd_audit.ipynb` đã chạy đủ bốn ô mã, không có lỗi, có hai hình đã
kiểm tra trực quan. Notebook đọc lại 41 mask gốc, đối chiếu hash, đếm màu nhãn,
kiểm tra kích thước từ 41 phần đầu MAT và hiển thị ba cặp MAT–mask tải đầy đủ.
Bằng chứng lần chạy: `docs/management/qposd_notebook_audit.json`.

Kết quả: 24 cặp khớp kích thước, 17 cặp lệch; khớp kích thước chưa chứng minh
căn chỉnh từng pixel. Đây là kiểm tra dữ liệu bổ sung, chưa phải đánh giá
classifier và không thay thế SOS. Dữ liệu nguồn không được đóng gói trong Git;
các lệnh tải và giới hạn kiểm tra nằm trong `docs/management/QPOSD_THAM_DINH.md`.

```text
python scripts/run_notebooks.py --notebook notebooks/external/08_qposd_audit.ipynb
```

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

Đã có kết quả thực nghiệm đủ 2.290 ảnh và notebook đã thực thi bốn ô mã:
bảng tổng hợp, biểu đồ nhóm/cụm và ba ảnh có tỷ lệ pixel báo nhầm cao nhất.
Ô minh họa chạy lại mô hình và đối chiếu số pixel/vùng với kết quả đã lưu.
Ô đầu sẽ dừng nếu thiếu kết quả, sai hash hoặc thiếu ảnh. Tỷ lệ báo nhầm
toàn tập là 1.449/2.290 (63,2751%); không diễn giải thành Recall hoặc F1 dầu.

Notebook này nằm riêng để năm notebook SOS vẫn tái tạo được khi máy chưa tải
DARTIS. `scripts/run_notebooks.py` hiện chỉ chạy năm notebook SOS ở cấp trên.
Mở notebook bổ sung bằng Jupyter và chọn môi trường `.venv` của dự án, hoặc chạy:

```text
python scripts/run_notebooks.py --notebook notebooks/external/06_dartis_false_alarms.ipynb
```

Mã tạo notebook: `scripts/build_dartis_notebook.py`.
Mã kiểm tra kết quả trước khi hiển thị: `scripts/dartis_results.py`.
Kiểm thử mẫu số và chặn kết quả chưa đủ: `tests/test_dartis_reporting.py`.
