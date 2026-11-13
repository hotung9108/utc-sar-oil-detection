# Slide bảo vệ — bản xem xét v2

[SAR_SOS_review_v2.pptx](SAR_SOS_review_v2.pptx) gồm 20 slide, sử dụng số liệu đã lưu trong `results/sos/` và `results/physical/`.
Đã xem 5 slide mới/thay đổi, đối chiếu 15 slide còn lại giống pixel với bản v1 đã duyệt,
kiểm tra cấu trúc PPTX, kích thước, font,
8 bảng chỉnh sửa được và khả năng nhập lại bằng Artifact Tool.
Bằng chứng và SHA-256: `docs/management/slides_audit.json`.

Đây là bản trình bày kết quả hiện có, chưa phải xác nhận dự án đủ điều kiện nộp.
Slide 17 trình bày nhánh hiệu chuẩn/gió riêng, slide 18 giới thiệu GUI và video,
slide 19 ghi giới hạn QPOSD và phép thử DARTIS chưa hoàn thành. Chưa kiểm tra
trong ứng dụng Microsoft PowerPoint. Video tự động 6 phút đã có ở `deliverables/video/`;
chữ ký và xác nhận đóng góp thật vẫn còn thiếu. Bản v1 được giữ để truy vết.

Tạo lại từ thư mục gốc dự án bằng Node của môi trường Artifact Tool:

```text
node scripts/build_slides.mjs
node scripts/finalize_slides.mjs
```

Hai script dùng đường dẫn runtime hiện tại làm mặc định. Trên máy khác, đặt
`ARTIFACT_RUNTIME` đến thư mục dependencies có Node, Python và Artifact Tool;
đặt `PRESENTATIONS_SKILL` đến thư mục skill chứa các công cụ kiểm tra.
Sau khi tạo lại phải xem lại các slide và cập nhật bản ghi kiểm tra cùng hash.
