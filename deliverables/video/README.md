# Video demo SAR

[SAR_demo_v1.mp4](SAR_demo_v1.mp4) dài **6 phút**, 1280×960, H.264, 2 fps, 720 khung hình. Video ghi tự động ứng dụng PyQt đang chạy mô hình NumPy; có phụ đề tiếng Việt, không có âm thanh. Đây không phải bản ghi thuyết trình hay bằng chứng đóng góp của thành viên.

Nội dung gồm đầu vào, lọc Lee, vùng ứng viên, đặc trưng, điểm SVM, đối chiếu mask, nhánh Niblack/CART, hai ca thất bại và xuất mask/overlay/JSON. Kết quả toàn tập SOS được ghi riêng với chỉ số của ảnh đang mở. Nhánh Niblack chỉ có đánh giá validation; dữ liệu SOS chỉ hỗ trợ dầu/nền.

## Kiểm chứng

- [Biên nhận tạo video](SAR_demo_v1.json): thời gian, kịch bản và hash mã nguồn.
- [Kiểm tra tự động](../../docs/management/video_audit.json): giải mã toàn bộ video, kiểm tra 360 giây, hash nguồn và độ vừa của 24 phụ đề. Trường `visual_review_completed: false` thuộc lần kiểm tra tự động, không đại diện cho bước xem ảnh sau đó.
- [Kiểm tra trực quan riêng](../../docs/management/video_visual_review.json): đã xem 9 khung hình giải mã tại các chương 1, 5, 7, 12, 16, 18, 19, 21, 24; không tuyên bố xem thủ công mọi khung hình.

Chạy lại kiểm tra từ thư mục gốc:

```powershell
uv sync --frozen --extra demo
uv run --frozen --extra demo python scripts/verify_demo_video.py
```

Mở ứng dụng: `uv run --frozen --extra demo python scripts/demo_qt.py`. Cần dữ liệu SOS theo README gốc để suy luận; xem video không cần tải dữ liệu.

Hash SHA-256 video: `010c7ac2c81f0b892124237fbc0b472a5edc0c39343e7cbfef8d523e5dd1da77`.
