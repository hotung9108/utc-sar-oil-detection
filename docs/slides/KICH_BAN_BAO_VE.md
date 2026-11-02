# Kịch bản bảo vệ BTL XLA

18 slide = 12 phút theo phân bổ từng người bên dưới. Demo trực tiếp 3 phút riêng; vấn đáp 5 phút. Điều chỉnh nhịp khi diễn tập.

Canva MCP đã được kiểm tra nhưng bị quản trị viên vô hiệu hóa. Slide được tạo cục bộ bằng python-pptx, text/shape sửa được.

Nguồn số liệu: source SHA256 `28ecff90ac5cd28b2c2547ee9df86093599e3cf63e120e12cc71a356a8e4aa79`. Tên đã cập nhật; MSSV chờ bổ sung; chưa tạo video. Tài liệu cá nhân: [docs/thanh_vien](../thanh_vien/README.md).

## 1. Xử lý ảnh SAR: từ khử nhiễu đến vùng tối ứng viên

TV1 — Tiến Sơn Trần · 20 giây.

Giới thiệu bài toán tăng cường, lọc và biên. Nhấn mạnh đây là thực hành xử lý ảnh có thể giải thích, không huấn luyện mô hình nhận diện dầu.

Nguồn: `BTL Xử lý ảnh · UTC · Đề kết hợp đã đăng ký`

## 2. Mục tiêu có giới hạn rõ ràng

TV1 — Tiến Sơn Trần · 20 giây.

Phân biệt tăng cường khả năng quan sát với kết luận vật lý. Diện tích đo bằng pixel, không đổi sang km² khi thiếu độ phân giải mặt đất.

Nguồn: `README.md; hướng dẫn BTL XLA`

## 3. Mã nguồn được chia theo 5 vai trò

TV1 — Tiến Sơn Trần · 20 giây.

Nêu trách nhiệm được phân công, không gán tác giả của lịch sử commit. Mỗi người phải hiểu cả pipeline để trả lời vấn đáp chéo.

Nguồn: `docs/management/PHAN_CONG_MA_NGUON.md`

## 4. Dữ liệu và phạm vi đánh giá

TV5 — Phạm Minh Tuấn · 50 giây.

Nguồn CSIRO theo metadata cục bộ, DOI 10.25919/4v55-dn16; license.html ghi CC BY-SA 4.0. Bản repo ít hơn bộ công bố 92 ảnh. Nhãn 0 không dầu, 1 có dầu; không có mask pixel để báo IoU/Dice.

Nguồn: `CSIRO · DOI 10.25919/4v55-dn16 · CC BY-SA 4.0 theo metadata cục bộ`

## 5. Vì sao ảnh SAR khó phân đoạn?

TV2 — Lương Tiến Dũng · 40 giây.

Mô hình nhiễu nhân là mô hình làm việc, không chứng minh JPEG đã hiệu chuẩn vật lý. Vùng lặng gió hoặc kết cấu nền cũng có thể tối.

Nguồn: `Cơ sở lý thuyết SAR; src/tv3/filters.py`

## 6. Pipeline tách hiển thị và phân đoạn

TV1 — Tiến Sơn Trần · 40 giây.

Làm nét chỉ tác động ảnh quan sát. Phân đoạn dùng ảnh trước làm nét; ảnh đã lọc trước CLAHE được giữ làm reference.

Nguồn: `src/tv1/pipeline.py`

## 7. Lee: làm mịn có trọng số thích nghi

TV3 — Hồ Việt Tùng · 50 giây.

Giải thích mean, variance và L. Khi variance nhỏ hơn mean²/L, K bằng 0 và kết quả là trung bình cục bộ. Đây không phải loại nhiễu hoàn hảo.

Nguồn: `src/tv3/filters.py; Lee (1980)`

## 8. CLAHE: tăng tương phản có giới hạn

TV3 — Hồ Việt Tùng · 50 giây.

Mô tả bốn bước. Code dùng histogram nguyên, phân phối dư, đệm reflect101 và nội suy; kiểm tra cả kích thước không chia hết và lưới 1×1.

Nguồn: `src/tv3/enhancement.py; cv2.createCLAHE`

## 9. Làm nét và các toán tử biên

TV4 — Nguyễn Hải Hiếu · 25 giây.

Unsharp/high-boost tăng thành phần cao tần; gradient hoặc đổi dấu không tự phân loại dầu. Diễn giải LoG cần xét ngưỡng và xử lý gần zero số học.

Nguồn: `src/tv4/sharpening.py; src/tv4/edges.py`

## 10. Canny: giữ đúng thông tin gradient

TV4 — Nguyễn Hải Hiếu · 40 giây.

Nêu sửa lỗi cắt gradient về uint8 trước NMS. Góc trong hệ tọa độ ảnh phải chọn đúng cặp chéo. Khác biệt lượng tử hướng, tie và biên ảnh được báo descriptive.

Nguồn: `src/tv4/edges.py; đối chiếu cv2.Canny`

## 11. Otsu: tối ưu mức xám, không tối ưu nhãn dầu

TV4 — Nguyễn Hải Hiếu · 30 giây.

Hai lớp theo ngưỡng gồm I<=t và I>t. Sửa lỗi loại endpoint tối. Ảnh hằng không đủ bằng chứng tương phản; eta cao không chứng minh đúng đối tượng.

Nguồn: `src/tv4/morphology.py; Otsu (1979)`

## 12. Hình thái và gán nhãn tự cài

TV4 — Nguyễn Hải Hiếu · 35 giây.

Phân biệt opening loại cấu trúc nhỏ với closing nối/lấp. Closing cũng có thể gộp nhầm. Run-length union-find thay lời gọi SciPy trong lõi.

Nguồn: `src/tv4/morphology.py; OpenCV đối chứng`

## 13. C_R là tương phản, không phải độ tròn

TV4 — Nguyễn Hải Hiếu · 30 giây.

Sửa sự không khớp giữa báo cáo cũ và code. Không tự hạ CR xuống 0.07 khi vùng lớn. Nếu không có vòng nền, không đủ dữ liệu đo tương phản.

Nguồn: `src/tv4/morphology.py; tests/test_core.py`

## 14. Kiểm chứng: số đo thật, phạm vi rõ

TV2 — Lương Tiến Dũng · 80 giây.

Phân biệt 558 pass kiểm tra số học với 36 descriptive. Các compositions chỉ kiểm chứng phép tính dựa trên primitive thư viện; không phải 33 API thuật toán độc lập.

Nguồn: `results/verification/per_case.csv; hand_examples.json`

## 15. Thực nghiệm có thể tái tạo

TV5 — Phạm Minh Tuấn · 50 giây.

Một lệnh chạy kiểm chứng, bộ mẫu và cả hai lớp. Mean/std tính trên từng ảnh; thời gian là toàn pipeline. ENL dùng ROI cố định nên không bảo đảm ROI đồng nhất.

Nguồn: `python reproduce.py; results/reproducible/`

## 16. Ca 00013: tăng tương phản không tạo bằng chứng dầu

TV3 — Hồ Việt Tùng · 40 giây.

Hiện tại giữ 1 vùng, 2.08% diện tích. Quan sát vệt chính phù hợp hơn bản cũ nhưng không khẳng định IoU khi thiếu mask chuẩn.

Nguồn: `results/reproducible/class_1_00013_clahe.png`

## 17. Đánh giá toàn tập và demo Streamlit

TV5 — Phạm Minh Tuấn · 70 giây.

Nhấn mạnh chỉ số cấp ảnh và giả định nhãn thư mục. Demo trực tiếp riêng 3 phút: ảnh mẫu, 00013, đổi clip/CR, xem lỗi và tải kết quả. Video chưa làm theo yêu cầu.

Nguồn: `results/reproducible/confusion.json; streamlit_app.py`

## 18. Kết luận và nguồn tham khảo

TV1 — Tiến Sơn Trần · 30 giây.

Kết luận theo bằng chứng: triển khai và đối chiếu, còn giới hạn báo nhầm. Hướng tiếp theo vẫn xử lý ảnh: ROI nền thích nghi, ngưỡng cục bộ, đánh giá mask gán tay. Không hứa dùng ML/DL.

Nguồn: `Hướng dẫn BTL UTC; Lee 1980; Otsu 1979; Canny 1986; OpenCV/SciPy docs`
