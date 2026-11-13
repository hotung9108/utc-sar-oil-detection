# Slide bảo vệ — bản xem xét v1

`SAR_SOS_review_v1.pptx` gồm 18 slide, sử dụng số liệu đã lưu trong `results/sos/`.
Đã kiểm tra trực quan từng slide và kiểm tra cấu trúc PPTX, kích thước, font,
8 bảng chỉnh sửa được và khả năng nhập lại bằng Artifact Tool.
Bằng chứng và SHA-256: `docs/management/slides_audit.json`.

Đây là bản trình bày kết quả hiện có, chưa phải xác nhận dự án đủ điều kiện nộp.
Slide ghi rõ giới hạn metadata góc tới/gió, nhãn look-alike và phép thử DARTIS
chưa hoàn thành. Cần cập nhật slide 17 khi có kết quả DARTIS. Chưa kiểm tra
trong ứng dụng Microsoft PowerPoint; chưa có video demo và chữ ký đóng góp thật.

Tạo lại từ thư mục gốc dự án bằng Node của môi trường Artifact Tool:

```text
node scripts/build_slides.mjs
node scripts/finalize_slides.mjs
```

Hai script dùng đường dẫn runtime hiện tại làm mặc định. Trên máy khác, đặt
`ARTIFACT_RUNTIME` đến thư mục dependencies có Node, Python và Artifact Tool;
đặt `PRESENTATIONS_SKILL` đến thư mục skill chứa các công cụ kiểm tra.
Sau khi tạo lại phải xem lại các slide và cập nhật bản ghi kiểm tra cùng hash.
