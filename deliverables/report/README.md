# Bản báo cáo để nhóm rà soát

- [Bản Word v10](Bao_cao_SAR_SOS_review_v10.docx)
- [Bản PDF v10](Bao_cao_SAR_SOS_review_v10.pdf)

Bản v10 có 39 trang tổng cộng, 27 trang nội dung chính, 13 tài liệu tham khảo. Giữ kết quả DARTIS và QPOSD, bổ sung Bảng 4.5 trên 3.101 patch PALSAR: Otsu–SVM F1=0,33965, Niblack–CART F1=0,24948. Đây là hai pipeline đã khóa; chưa chứng minh độc lập theo cảnh hoặc tác dụng riêng của ngưỡng. Các số đo SOS trước đây giữ nguyên.

Đã kiểm tra mục lục và bố cục theo `docs/report/render_audit.json` và `render_progress.json`: xem trực tiếp 10 trang thay đổi, 29 trang còn lại giống pixel với v9 đã duyệt. Hai tệp v10 giữ nguyên byte của bản được kiểm tra; các bản cũ giữ để đối chiếu lịch sử.

**Đây chưa phải bản nộp hoàn chỉnh.** Cần thông tin lớp, giảng viên, nhóm, mã sinh viên, xác nhận đóng góp và biên bản họp thật. Nội dung cũng ghi rõ: chưa kiểm chứng phát hiện dầu trên tile đã hiệu chuẩn, chưa đánh giá nhầm lẫn theo từng nguyên nhân look-alike, nhánh Niblack chưa có test độc lập mới.

Nguồn dựng: `docs/report/narrative.json`, `bibliography.json`, `scripts/build_report.py`; quy trình dựng và cập nhật trường tại `docs/report/README.md`. Hướng dẫn GUI tại `docs/DEMO_GUI.md`, video tại `deliverables/video/README.md`. Không chỉnh trực tiếp PDF để thay số liệu hoặc mục lục; cần dựng và kiểm tra lại sau sửa.
