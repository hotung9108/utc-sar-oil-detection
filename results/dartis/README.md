# Trạng thái phép thử DARTIS

Giao thức trước suy luận: `protocol.json`. Chưa có kết quả đánh giá đầy đủ.
Lượt tải gần nhất xử lý đủ danh sách 2.290 ảnh nhưng còn 42 ảnh chưa tải được, theo
`download_audit.json`; số xử lý không đồng nghĩa số tải thành công.
Đã có 2.248 ảnh hợp lệ. Lượt này ghi 38 lỗi HTTP 503, một timeout, một HTTP 429
và hai ảnh hoãn sau khi nhận giới hạn tốc độ. Chưa chạy đánh giá trên tập thiếu.

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
