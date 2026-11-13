# Trạng thái phép thử DARTIS

Giao thức trước suy luận: `protocol.json`. Đã đánh giá đủ 2.290 ảnh bằng mô hình
SOS cố định và kiểm tra lại hash, quần thể ảnh, số đếm tổng hợp bằng reporter.
Kết quả: 1.449 ảnh báo nhầm (63,2751%); nhóm bờ 337/351 (96,0114%), nhóm biển
1.112/1.939 (57,3491%). Bảng đầy đủ: `REPORT.md`; từng ảnh: `evaluation.json`.
Đây là tỷ lệ báo nhầm mức ảnh trên tập no-oil, không phải F1 đối tượng.
Đã tải đủ 2.290 ảnh, giải mã và lưu SHA-256; `download_audit.json` ghi
`complete: true`, không có lỗi. Năm ảnh từng gặp HTTP 503 đã tải thành công
trong lượt tiếp theo sau khi chờ. `evaluation.json` có `complete: true`;
reporter đã kiểm tra thành công. Kết quả cho thấy mô hình chuyển trực tiếp
từ SOS sang DARTIS báo nhầm nhiều, chưa phù hợp để triển khai thực tế.

Đã quan sát HTTP 429 từ nhà phát hành. `rate_limit.json` lưu thời điểm được
thử lại sớm nhất. Downloader mặc định một worker, giãn cách tối thiểu hai giây
giữa các yêu cầu và ngừng phát yêu cầu mới khi nhận 429. Tôn trọng Retry-After;
nếu không có header hợp lệ, chờ tối thiểu 15 phút. Không khởi chạy lặp trong
thời gian chờ. Ảnh đã tải hợp lệ được tái sử dụng.

Sau thời gian chờ:

```text
python scripts/download_dartis.py --workers 1
python scripts/evaluate_dartis.py --workers 4
python scripts/report_dartis.py
python scripts/run_notebooks.py --notebook notebooks/external/06_dartis_false_alarms.ipynb
```

Chỉ chạy lệnh sau khi lệnh trước thành công. Evaluator yêu cầu đủ ảnh;
reporter và notebook kiểm tra lại hash, quần thể ảnh và số đếm trước khi công bố.
Không dùng tập thiếu ảnh để thay thế tập đã cố định trong giao thức.
