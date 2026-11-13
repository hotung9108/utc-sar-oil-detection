# Kiểm kê đối tượng QPOSD trước khi đánh giá phân lớp

Chạy từ thư mục gốc:

```powershell
.\.venv\Scripts\python.exe scripts/audit_qposd_objects.py
```

Kết quả thực chạy lưu tại `qposd_object_audit.json`, kèm SHA-256 của mã,
hai hồ sơ dữ liệu đầu vào và từng mask. Đây là kiểm kê nhãn, chưa phải điểm
chất lượng của bộ phân lớp.

## Số liệu

Mỗi đối tượng là một thành phần liên thông 8 hướng của đúng màu lớp do tác
giả quy định. Màu không xác định bị bỏ qua; không thay đổi kích thước mask.

| Phạm vi | Lớp | Tổng đối tượng | Nhỏ hơn 64 pixel | Từ 64 pixel |
|---|---|---:|---:|---:|
| Toàn bộ 41 mask | Dầu | 452 | 264 | 188 |
| Toàn bộ 41 mask | Tương tự dầu | 794 | 311 | 483 |
| 24 cặp khớp kích thước | Dầu | 364 | 239 | 125 |
| 24 cặp khớp kích thước | Tương tự dầu | 558 | 205 | 353 |

Trong 24 cặp, các vùng dầu nhỏ chứa 2.847/8.046.626 pixel dầu; các vùng
tương tự dầu nhỏ chứa 6.491/3.248.540 pixel tương tự dầu. Chúng chiếm ít
pixel nhưng nhiều đối tượng, nên lựa chọn bỏ vùng nhỏ ảnh hưởng mạnh đến
mẫu số Recall mức đối tượng. Không được tự động xóa chúng khỏi ground truth
chỉ vì pipeline SOS đang dùng diện tích ứng viên tối thiểu 64 pixel.
Mốc 64 ở đây chỉ dùng để kiểm tra độ nhạy đối với cấu hình SOS đã có,
không phải ngưỡng mới được tối ưu cho QPOSD.

## Đối chiếu NumPy với thư viện

Đã chạy hàm liên thông tự cài `sar_oil.core.label` và
`scipy.ndimage.label` trên cả hai lớp của toàn bộ 41 mask: **82 phép đối
chiếu đều trùng phân hoạch từng pixel**, cho phép tên ID của vùng khác nhau.
Kiểm tra không chỉ so tổng số vùng: ánh xạ ID phải một-một và ảnh nhãn sau
ánh xạ phải bằng nhau trên cả pixel nền. JSON lưu thời gian một lần chạy
của mỗi hàm; chưa dùng số đo đơn lẻ này để kết luận hiệu năng tổng quát.

## Quy tắc cho bước tiếp theo

- Chỉ xét 24 cặp khớp kích thước cho thử nghiệm tiếp theo; vẫn phải kiểm tra
  đầy đủ MAT và xem ảnh/nhãn. Không cắt hoặc kéo giãn 17 mask bị lệch.
- Chia theo ảnh nguồn trước khi lấy patch hoặc vùng. Không để vùng của cùng
  một ảnh xuất hiện ở cả train và test. Chưa có ID cảnh nên chưa thể khẳng
  định các ảnh khác nhau là các cảnh độc lập.
- Giữ nhãn nhỏ trong kiểm kê và công bố cách xử lý trước khi chấm điểm.
  Nếu báo cáo thêm nhóm diện tích từ 64 pixel, phải ghi là phân tích theo
  kích thước, không thay cho kết quả trên toàn bộ đối tượng đủ điều kiện.
- Đặc trưng lấy từ vùng ground truth chỉ đánh giá phân lớp khi đã biết vùng;
  không được gọi đó là Precision/Recall/F1 phát hiện đầu-cuối. Phép đo phát
  hiện cần vùng ứng viên sinh từ ảnh, rồi ghép với nhãn theo quy tắc công bố.
- QPOSD bổ sung lớp tương tự dầu chung trên UAVSAR; không thay SOS và không
  cung cấp nhãn riêng cho gió yếu, màng sinh học hoặc mưa.

Thành phần liên thông của mask không mặc nhiên tương ứng một sự kiện dầu
tràn vật lý. Khớp kích thước không tự chứng minh căn chỉnh địa lý.
