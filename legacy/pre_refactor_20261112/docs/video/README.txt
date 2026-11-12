VIDEO DEMO BTL XỬ LÝ ẢNH SAR

Mở DEMO_BTL_XLA_V2_6_PHUT.mp4 để xem video hoàn chỉnh.
Thời lượng: 6 phút. Kích thước: 1600 × 900, 25 fps, H.264.
Video quay thao tác trên ứng dụng Streamlit thật, có phụ đề tiếng Việt
gắn trực tiếp vào hình, không có âm thanh theo lựa chọn của nhóm.

CÁC TỆP ĐI KÈM
- DEMO_BTL_XLA_V2.srt: 41 đoạn phụ đề có mốc thời gian, dùng khi biên tập.
  Không bật thêm SRT khi xem MP4 này vì phụ đề đã nằm trong hình.
- LOI_DAN_VA_MOC_THOI_GIAN.txt: nội dung phụ đề và mốc thời gian để nhóm
  chuẩn bị thu lời dẫn. Đây là lời dẫn ngắn theo video, không phải toàn bộ
  speaker notes dài của 18 slide bảo vệ.
- demo_captions.json: nguồn nội dung phụ đề để dựng lại video.
- demo_exports/class_1_00013_mask.png: mask tải từ ứng dụng trong demo.
- demo_exports/class_1_00013_result.json: cấu hình và chỉ số tải cùng mask.

MỐC NỘI DUNG
00:00 Giới thiệu mục tiêu và phạm vi xử lý ảnh cổ điển.
00:23 Chọn ảnh 00013, so sánh ảnh gốc và bộ lọc Lee.
01:05 Tắt/bật CLAHE, thay clip limit và giải thích ảnh tham chiếu.
01:59 Canny, mask hình thái học và thử ngưỡng tương phản vùng/nền.
02:53 Histogram, lát cắt mức xám và thống kê vùng.
03:29 Tải mask PNG và cấu hình/chỉ số JSON.
03:46 Tải ảnh nền biển để minh họa trường hợp bất lợi.
04:22 Đối chiếu với thư viện và giới thiệu phân công nhóm.
04:58 Trở lại ảnh 00013, tổng kết kết quả và giới hạn.
05:43 Lệnh chạy ứng dụng và kết thúc.

THU GIỌNG SAU
Nhập MP4 vào phần mềm biên tập, giữ nguyên tốc độ và thời lượng hình.
Thu lời theo từng mốc trong tệp TXT, giải thích thêm trong khoảng dừng
nếu cần, rồi ghép giọng vào một đường âm thanh riêng. Xem lại để bảo đảm
lời nói khớp tham số và ảnh đang hiển thị. Video hiện không có nhạc nền.

KIỂM TRA BẢN GIAO
Đã giải mã toàn bộ MP4 không lỗi; xác nhận 360 giây và không có luồng âm
thanh. Đã rà soát 22 khung hình đại diện cho các thao tác, kết quả và
phụ đề. Mask xuất có kích thước 400 × 400, chứa 3.328 pixel tiền cảnh;
JSON ghi 1 vùng và diện tích 2,08%, khớp kết quả trong video.
Vùng tối ứng viên chưa phải xác nhận dầu. Bảng đối chiếu thư viện là
kết quả kiểm chứng đã lưu, không phải phép kiểm chứng chạy lại trong demo.

CHẠY ỨNG DỤNG TỪ THƯ MỤC GỐC DỰ ÁN
  .venv\Scripts\python.exe -m streamlit run streamlit_app.py

DỰNG LẠI VIDEO (dành cho người bảo trì)
Các công cụ quay/dựng nằm riêng trong .cache/video_deps và trình duyệt
trong .cache/video_browsers, không thuộc requirements của ứng dụng.
Nếu cache đã bị xóa, cài lại từ thư mục gốc trong PowerShell:
  uv pip install --python .venv/Scripts/python.exe --target .cache/video_deps playwright imageio-ffmpeg
  $env:PYTHONPATH = (Join-Path (Get-Location) '.cache/video_deps')
  $env:PLAYWRIGHT_BROWSERS_PATH = (Join-Path (Get-Location) '.cache/video_browsers')
  .venv\Scripts\python.exe -m playwright install chromium
Khởi động ứng dụng trên cổng 8501, sau đó chạy lần lượt:
  .venv\Scripts\python.exe -X utf8 scripts/record_demo_video.py
  .venv\Scripts\python.exe -X utf8 scripts/build_demo_video.py
  .venv\Scripts\python.exe -X utf8 scripts/verify_demo_video.py
Quay lại mất khoảng 6 phút. Sau khi dựng lại cần rà soát hình và phụ đề;
kiểm tra tự động không thay thế việc xem nội dung video.
