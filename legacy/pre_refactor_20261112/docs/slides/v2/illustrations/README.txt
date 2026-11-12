ẢNH MINH HỌA CHO BỘ SLIDE V2

Các PNG là ảnh đầu vào, kết quả xử lý hoặc phần cắt của ảnh thật trong
dự án. Không dùng ảnh SAR do AI sinh. Màu xanh/cam ở contrast_ring.png
là màu đánh dấu mask và vành nền, không phải màu đo được từ vệ tinh.
Ảnh được nhúng trong PowerPoint, không cần giữ thư mục này cạnh PPTX để mở.

NGUỒN VÀ CÁCH TẠO
- kaggle/data/Class_1/class_1_00013.jpg
- data/sample/sea_surface/sea_surface_01.jpg
- src/tv1/pipeline.py, src/tv4/edges.py, src/tv4/morphology.py
- scripts/illustrate_defense_deck_v2.py: xuất ảnh từ lần chạy thực tế.
manifest.json ghi cấu hình, nguồn, vùng cắt và ý nghĩa từng ảnh.
Các ảnh ở nhiều slide dùng cùng một mẫu để theo dõi liên tục tác động
của từng thuật toán. Không xem chúng là các mẫu thực nghiệm độc lập.

HƯỚNG DẪN CHỈ VÀO HÌNH KHI THUYẾT TRÌNH
Slide 2: so ảnh xám, nét viền và vùng trắng. Nét viền biểu diễn ranh giới;
mask tô phần được chọn để có thể đếm diện tích, nhưng vẫn có thể có lỗ.
Slide 4: hai mẫu đầu vào cho thấy hình dạng vùng tối rất đa dạng; nhãn
cả ảnh chưa xác định chính xác đường bao của vùng dầu.
Slide 5: cùng một vùng nền trước và sau xử lý. Những chấm tối dễ thấy
hơn sau CLAHE là lý do không được coi mọi chi tiết mới nổi rõ là dầu.
Slide 7: so độ lốm đốm và độ mềm của cạnh trước/sau Lee, cùng thang xám.
Slide 8: so ảnh sau Lee với sau CLAHE; cả vệt chính và nền đều nổi rõ.
Slide 9: ảnh làm nét còn mức xám, Canny chỉ giữ các điểm biên.
Slide 10: gradient có các dải đáp ứng; NMS làm mảnh; ngưỡng kép và liên
kết loại bớt điểm yếu. Hai ảnh trung gian dùng cùng thang hiển thị.
Slide 11: ảnh nguồn phân đoạn và mask tối ban đầu với ngưỡng thực tế 46.
Vùng trắng của mask biểu thị pixel tối được chọn ở ảnh nguồn.
Slide 12: theo dõi cùng vị trí qua mở, đóng rồi lọc vùng. Ở mẫu này,
phép đóng lấp một số khe/lỗ nhỏ; mask sau lọc có thể giống mask sau đóng
trong vùng cắt, vì vùng chính vẫn được giữ lại.
Slide 13: xanh là vùng ứng viên; cam là vành đo nền. Vành có cả phần
nằm trong lỗ của mask, theo đúng phép giãn rồi trừ vùng đang xét.
Số đo 27,8; 57,9 và tỷ số khoảng 0,52 là của mẫu thật, khác ví dụ minh
họa 100 và 80 trong speaker notes. Cả hai dùng cùng công thức.
Slide 14: ma trận số có thể sửa trực tiếp trong PowerPoint. Ô giữa 200
được nhấn màu để dễ tính trung bình của tám số 100 và một số 200.
Slide 16: bốn hình phóng to cùng vùng vệt chính, không phải toàn ảnh.
Diện tích 3.328 pixel và 2,08% vẫn được tính trên toàn ảnh 400 × 400.
Slide 17: ảnh nền biển vẫn tạo 2 vùng ứng viên, 19,31% diện tích ảnh.
Đây là minh họa điều kiện bất lợi, không phải một mask chuẩn.

DỰNG LẠI
Từ thư mục gốc dự án:
  .venv\Scripts\python.exe -X utf8 scripts/build_defense_deck_v2.py
  powershell -NoProfile -File scripts/export_slides_v2.ps1 -Preview
Sau khi thay thuật toán hoặc dữ liệu cần rà lại nhãn, số liệu và hình.
