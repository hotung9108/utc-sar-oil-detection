# Mã cũ có thể tái sử dụng

| Nhóm | Vị trí trong legacy | Điều kiện kiểm chứng lại |
| --- | --- | --- |
| Lọc | src/tv3/filters.py | Công thức Lee/Frost/Kuan, miền tuyến tính/dB, dtype, padding, ảnh hằng; không coi JPEG là sigma0 |
| Phân đoạn | src/tv4/morphology.py | Otsu, hình thái và liên thông; ngưỡng thích nghi cần thẩm định lại trên dữ liệu mới |
| Gradient | src/tv4/edges.py | Giữ chỉnh sửa chưa commit; kiểm đạo hàm và đặc trưng biên, không dùng mọi cạnh làm vùng dầu |
| Đối chiếu | src/tv2/ | Phân biệt API trực tiếp, ghép công thức và biến thể |
| Chỉ số | src/tv5/metrics.py | ENL cần ROI đồng nhất; bổ sung giao thức mức đối tượng sau khi chốt nhãn |

Đây là kiểm kê khả năng tái sử dụng, chưa xác nhận đúng hay chọn thuật toán. HE/CLAHE/làm nét không mặc định thuộc pipeline mới. CART/SVM và đặc trưng vùng chưa có trong phiên bản lưu trữ.
