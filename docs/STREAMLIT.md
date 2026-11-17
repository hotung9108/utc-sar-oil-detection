# Chạy và kiểm tra ứng dụng Streamlit

Trạng thái triển khai không đồng nghĩa đạt 100% đề: xem [đối chiếu Đề 18](DANH_GIA_DU_AN_VA_DOI_CHIEU_DE_18.md). QPOSD và Cantarell là hai nhánh dữ liệu/cảm biến khác nhau; không ghép các điểm số thành một chứng nhận toàn hệ thống.

## Khởi động

Từ thư mục gốc dự án, chạy:

```powershell
uv run --frozen --extra web streamlit run streamlit_app.py
```

Mở `http://127.0.0.1:8501`. Cấu hình mặc định chỉ lắng nghe trên máy cục bộ.
Nếu đã cài đủ dependency trong `.venv`, có thể dùng:

```powershell
.venv/Scripts/python.exe -m streamlit run streamlit_app.py
```

## Luồng sử dụng

### Cải tiến trải nghiệm ngày 17/11/2026

- Mỗi màn hình giải thích mục đích và bước tiếp theo. Cấu hình nâng cao thu gọn mặc định; người mới có thể chạy ngay mẫu SOS.
- Có xem trước ảnh, kiểm tra định dạng/kích thước trước khi chạy, báo lỗi rõ và vô hiệu hóa nút chạy với ảnh không hợp lệ.
- Kết quả có kết luận bằng lời, chú giải màu, giải thích tám đặc trưng và ý nghĩa score.
- Tab đối chiếu SOS hiển thị nhãn thật và ảnh so sánh pixel: xanh ngọc = trùng, cam = chỉ dự đoán, tím = chỉ nhãn. Đây không phải bản đồ ghép đối tượng; TP/FP/FN vẫn dùng evaluator hiện có.
- Precision/Recall/F1 đi kèm số vùng đúng, báo nhầm, bỏ sót và hướng dẫn đọc. Không coi không phát hiện dầu là xác nhận ảnh sạch.
- QPOSD/Cantarell có thêm xem ứng viên; chi tiết đặc trưng thu gọn. Góc tới/gió hiển thị kèm đơn vị.
- Trang bằng chứng có bảng tổng quan trước các đối chứng chi tiết; QPOSD tách điểm phân lớp có sẵn vùng khỏi điểm phát hiện đầu-cuối. Trang hướng dẫn có bảng chọn luồng, chuẩn bị mask, giải thích ZIP và câu hỏi thường gặp.

Mô hình, ngưỡng, tập kiểm tra và số liệu thực nghiệm không thay đổi trong lần cải tiến giao diện này.

1. Chọn ảnh mẫu có nhãn hoặc tải PNG/JPEG SAR hiển thị 8-bit, tối đa 16 MB và 1.048.576 pixel. Không tự resize ảnh.
2. Chọn cấu hình SOS Otsu/SVM hoặc nhánh bổ sung Niblack/CART rồi bấm Phân tích ảnh.
3. Xem ảnh gốc, ảnh lọc, ứng viên, mask và overlay; xem tám đặc trưng và decision score.
4. Mask tham chiếu là ảnh 8-bit cùng kích thước, dầu ≥128. Mask chỉ được dùng sau suy luận để tính metric.
5. Tải ZIP gồm năm ảnh và JSON chứa cấu hình, hash nguồn/model, vùng và kết quả đánh giá nếu có.

Đổi nội dung ảnh hoặc model sẽ xóa kết quả cũ khỏi màn hình. Tệp tải lên được xử lý qua thư mục tạm riêng và dọn sau khi suy luận; ứng dụng không ghi đè dữ liệu/kết quả thực nghiệm đã khóa.

Trang Bằng chứng thực nghiệm đọc JSON/Markdown đã lưu trong repository. Điểm một ảnh và điểm toàn tập là các kết quả khác nhau. Score không phải xác suất.

## Phạm vi

Trang Phân tích ảnh dùng hai pipeline SOS đã lưu. Trang Dầu và look-alike chạy mô hình QPOSD riêng trên các mẫu test T11 cục bộ đã xác minh, hiển thị dầu màu đỏ và look-alike màu xanh. ZIP QPOSD giữ mã pixel 0=nền, 1=dầu, 2=look-alike; không chuyển sang mask dầu/nền rồi mất lớp tương tự dầu. Mask tham chiếu chỉ được đọc để đánh giá sau suy luận.

Trang Sentinel-1 vật lý chạy các mẫu Cantarell đã hiệu chuẩn và xác minh, dùng nhánh có đủ Lee + gamma0 + Niblack + SVM. Giao diện chỉ mở khi kết quả test và bản xác minh độc lập khớp hash. Có góc tới, gió ERA5, đặc trưng và ZIP kết quả. Dầu thấm tự nhiên vẫn thuộc foreground dầu.

Trang Bằng chứng có bảng 50 cấu hình, 84 cặp mô hình, kết quả test, CI góc tới và số đối tượng nhỏ bị bỏ sót. Winner ban đầu không lọc có F1 test 0,05891; nhánh đủ bước lọc đạt 0,03825. Giao thức bổ sung có lọc được công bố sau khi xem một phần validation và trước test; không tuyên bố nó tốt hơn winner ban đầu. PNG SOS không hỗ trợ hiệu chỉnh góc tới; không dùng model khác miền rồi tuyên bố đã kiểm chứng.

Không cần PyQt để chạy Streamlit. Giữ ứng dụng desktop cũ để tham chiếu, không import giao diện Qt vào ứng dụng web.

## Kiểm thử

```powershell
.venv/Scripts/python.exe -m unittest discover -s tests -p test_streamlit_app.py -v
```

Toàn bộ kiểm thử web, gồm đầu vào hỏng và giải thích kết quả:

```powershell
.venv/Scripts/python.exe -m unittest discover -s tests -p 'test_streamlit_*.py' -v
```

Kiểm tra trình duyệt tùy chọn (cần Streamlit đang chạy ở cổng 8501 và Microsoft Edge đã cài):

```powershell
uv run --no-project --with playwright python scripts/web/verify_streamlit_browser.py
```

Script chạy ảnh mẫu thật, mở đối chiếu, bằng chứng, trợ giúp, QPOSD và Cantarell; lưu ảnh chụp desktop và màn hình hẹp tại `.cache/streamlit_ux/`. Playwright dùng môi trường tạm của uv, không thay dependency/lock của ứng dụng.

Kết quả kiểm tra bản cải tiến: **13/13 kiểm thử web đạt**, không skip. Script trình duyệt chạy thành công trên Edge headless với mẫu thật của cả ba nhánh; đã xem ảnh chụp kết quả/đối chiếu, bảng bằng chứng và bố cục trang đầu ở chiều rộng 390 px. Đây là kiểm tra chức năng và bố cục cục bộ, chưa phải nghiên cứu usability với người dùng thực tế hay kiểm tra mọi thiết bị.

Kiểm tra adapter với mô hình thật, upload, mask sai kích thước, kết quả ZIP, đổi cấu hình và điều hướng bằng [Streamlit AppTest](https://docs.streamlit.io/develop/api-reference/app-testing/st.testing.v1.apptest). AppTest kiểm chứng luồng ứng dụng; không thay thế kiểm tra bố cục trong trình duyệt.
