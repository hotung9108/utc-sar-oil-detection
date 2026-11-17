# Tối ưu trích đặc trưng QPOSD

Ngày 14/11/2026, lượt so sánh validation đầu tiên chưa hoàn tất được dừng
để thay cách tìm tọa độ từng vùng bằng gom tọa độ một lần. Không có kết quả
chọn cấu hình phát hiện hoặc điểm test được tạo từ lượt dừng này. Giữ nguyên
10 cấu hình ứng viên, bộ phân lớp đã chọn, cách chia dữ liệu và công thức
8 đặc trưng. Mã SOS gốc không thay đổi.

`qposd_fast_features.py` dùng NumPy, sắp xếp ổn định để giữ thứ tự pixel
trong mỗi vùng. Nhánh thư viện vẫn dùng triển khai tham chiếu cũ.
`qposd_grouped_feature_benchmark.json` ghi phép đo đầu trên ảnh validation 13:
1.474 vùng, ID và cả 8 đặc trưng bằng nhau chính xác; thời gian một lượt
18,8348 giây so với 1,3107 giây. Máy có tải đồng thời; không suy rộng hệ số
tăng tốc này cho toàn bộ pipeline hoặc mọi ảnh.

Chạy lại bằng script đã lưu cho kết quả 20,0804 giây và 1,4159 giây,
vẫn 1.474 vùng và sai số bằng 0 ở cả 8 cột. Bằng chứng kèm hash script:
`qposd_grouped_feature_benchmark_repeat.json`.

Chạy lại phép đo với tên đầu ra mới, không ghi đè bằng chứng cũ:

```powershell
.venv\Scripts\python.exe scripts/benchmark_qposd_features.py --output .cache/qposd/feature_benchmark_repeat.json
.venv\Scripts\python.exe -m unittest discover -s tests -p 'test_qposd*.py'
```

24 kiểm thử QPOSD đã qua sau tích hợp, gồm so sánh chính xác đặc trưng
trên vùng rỗng, một pixel, sát biên, ID không liên tục, vùng có lỗ và toàn ảnh;
kiểm thử pipeline và điều kiện khóa lựa chọn trước khi chạy test.
Kết quả lựa chọn phát hiện, đánh giá test và notebook kiểm tra SHA-256
của helper mới. Lượt validation tiếp theo phải chạy đủ 10 cấu hình × 5 ảnh;
không dùng kết quả thời gian để chọn cấu hình phân lớp hoặc phát hiện.

Theo yêu cầu người dùng, thông tin lớp, số nhóm, giảng viên, mã sinh viên,
đóng góp và biên bản chưa được xác nhận tiếp tục để trống, không tự điền.
