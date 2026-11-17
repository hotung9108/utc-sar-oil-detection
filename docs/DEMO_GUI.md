# Demo có giao diện PyQt

Notebook 01–05 vẫn là nơi trình bày thực nghiệm SOS; notebook 07 trình bày
nhánh hiệu chuẩn/gió riêng. Ứng dụng này đáp ứng phần demo có giao diện trong
hướng dẫn BTL, gọi trực tiếp pipeline NumPy đã cố định, không huấn luyện lại.

## Cài và mở

Từ thư mục gốc, sau khi đã chuẩn bị SOS và các model theo README:

```powershell
uv sync --frozen --extra demo
uv run --frozen --extra demo python scripts/demo_qt.py
```

Nếu môi trường đã cài đủ: `.venv/Scripts/python.exe scripts/demo_qt.py`.
PyQt6 là dependency tùy chọn `demo`; không bắt buộc khi chỉ chạy notebook.

## Luồng sử dụng

1. Chọn **Mở ảnh SAR 8-bit** hoặc **Ảnh mẫu SOS**. Menu mẫu gồm ảnh đầu
   danh sách test và hai ca thất bại đã phân tích, không chỉ có ảnh cho kết quả tốt.
2. Chọn Otsu/SVM hoặc nhánh Niblack/CART bổ sung rồi bấm **Chạy phát hiện**.
3. Tab **Ảnh và kết quả** hiển thị đầu vào, ảnh lọc Lee, vùng tối ứng viên và
   overlay đỏ của các vùng được giữ. Tab **Đặc trưng vùng** có 8 đặc trưng
   và điểm quyết định; bảng chỉ đọc, điểm không phải xác suất.
4. Có thể tải mask tham chiếu cùng kích thước, căn chỉnh với ảnh. Giá trị
   >=128 là dầu. Tab **Đối chiếu nhãn** hiển thị GT và sai số pixel; dòng
   kết quả báo TP/FP/FN và Precision/Recall/F1 **đối tượng của ảnh đang xem**.
   Mask được dùng sau suy luận, không truyền vào hàm dự đoán.
5. **Xuất kết quả** tạo thư mục mới chứa `mask.png`, `overlay.png`,
   `regions.json`; JSON có cấu hình, hash input/model, đặc trưng, điểm và
   đánh giá sau suy luận nếu có GT hợp lệ. Không ghi đè thư mục kết quả cũ.

## Phạm vi

Ảnh tối đa 1.048.576 pixel, mỗi chiều >=2; không tự resize. Demo từ chối DN
16-bit để tránh nhầm chia 255 với hiệu chuẩn vật lý. Nhánh DN/góc tới/gió
được minh họa riêng ở notebook 07 và chưa tích hợp thành mô hình dầu có nhãn.
Nhánh Niblack mới được đánh giá trên validation; số test Otsu không áp dụng
cho nhánh đó. Bộ SOS chỉ có dầu/nền, chưa có phân loại từng nguyên nhân
look-alike. Không diễn giải dự đoán thành cảnh báo ngoài thực địa.

## Bằng chứng kiểm tra

```powershell
$env:QT_QPA_PLATFORM='windows'
.venv/Scripts/python.exe scripts/verify_demo_qt.py
```

Kiểm tra Qt event loop, signal/worker, hai nhánh, menu ca lỗi, xuất mask/JSON,
GT không làm đổi dự đoán, từ chối mask sai kích thước/DN 16-bit và vô hiệu
kết quả cũ khi đổi cấu hình. Số đếm Otsu khớp kết quả test đã lưu trên ba ảnh.
Kết quả: `docs/management/gui_audit.json`; ảnh chụp: `.cache/gui/`.
Đây là điều khiển widget tự động trên Qt Windows; chưa kiểm tra bằng thao tác
chuột thủ công đối với hộp thoại chọn tệp/thư mục của hệ điều hành.
