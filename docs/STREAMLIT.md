# Chạy và kiểm tra ứng dụng Streamlit

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

1. Chọn ảnh mẫu có nhãn hoặc tải PNG/JPEG SAR hiển thị 8-bit, tối đa 16 MB và 1.048.576 pixel. Không tự resize ảnh.
2. Chọn cấu hình SOS Otsu/SVM hoặc nhánh bổ sung Niblack/CART rồi bấm Phân tích ảnh.
3. Xem ảnh gốc, ảnh lọc, ứng viên, mask và overlay; xem tám đặc trưng và decision score.
4. Mask tham chiếu là ảnh 8-bit cùng kích thước, dầu ≥128. Mask chỉ được dùng sau suy luận để tính metric.
5. Tải ZIP gồm năm ảnh và JSON chứa cấu hình, hash nguồn/model, vùng và kết quả đánh giá nếu có.

Đổi nội dung ảnh hoặc model sẽ xóa kết quả cũ khỏi màn hình. Tệp tải lên được xử lý qua thư mục tạm riêng và dọn sau khi suy luận; ứng dụng không ghi đè dữ liệu/kết quả thực nghiệm đã khóa.

Trang Bằng chứng thực nghiệm đọc JSON/Markdown đã lưu trong repository. Điểm một ảnh và điểm toàn tập là các kết quả khác nhau. Score không phải xác suất.

## Phạm vi

Trang Phân tích ảnh dùng hai pipeline SOS đã lưu. Trang Dầu và look-alike chạy mô hình QPOSD riêng trên các mẫu test T11 cục bộ đã xác minh, hiển thị dầu màu đỏ và look-alike màu xanh. ZIP QPOSD giữ mã pixel 0=nền, 1=dầu, 2=look-alike; không chuyển sang mask dầu/nền rồi mất lớp tương tự dầu. Mask tham chiếu chỉ được đọc để đánh giá sau suy luận.

Cantarell cần hoàn tất mô hình và đánh giá trước khi tích hợp suy luận; trang Bằng chứng đã có bảng 50 cấu hình ứng viên trên validation. PNG SOS không hỗ trợ hiệu chỉnh góc tới; không dùng model khác miền rồi tuyên bố đã kiểm chứng.

Không cần PyQt để chạy Streamlit. Giữ ứng dụng desktop cũ để tham chiếu, không import giao diện Qt vào ứng dụng web.

## Kiểm thử

```powershell
.venv/Scripts/python.exe -m unittest discover -s tests -p test_streamlit_app.py -v
```

Kiểm tra adapter với mô hình thật, upload, mask sai kích thước, kết quả ZIP, đổi cấu hình và điều hướng bằng [Streamlit AppTest](https://docs.streamlit.io/develop/api-reference/app-testing/st.testing.v1.apptest). AppTest kiểm chứng luồng ứng dụng; không thay thế kiểm tra bố cục trong trình duyệt.
