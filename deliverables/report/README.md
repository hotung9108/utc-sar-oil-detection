# Bản báo cáo để nhóm rà soát

- [Bản Word v11](Bao_cao_SAR_SOS_review_v11.docx)
- [Bản PDF v11](Bao_cao_SAR_SOS_review_v11.pdf)

Bản v11 có 41 trang tổng cộng, 29 trang nội dung chính, 13 tài liệu tham khảo. Giữ kết quả SOS, DARTIS và 3.101 patch PALSAR; bổ sung đầy đủ so sánh 10 bộ phân lớp, 10 cấu hình tìm vùng và 5 ảnh test QPOSD. Macro-F1 phát hiện QPOSD là 0,06373; macro-F1 phân lớp khi có sẵn vùng là 0,52141. Hai phép đo không thay thế nhau.

Đã kiểm tra mục lục và bố cục theo `docs/report/render_audit.json` và `render_progress.json`. Toàn bộ 41 trang được bao phủ bởi kiểm tra trực quan và chuỗi đối chiếu pixel với bản đã duyệt. Hai tệp v11 giữ nguyên byte của bản được kiểm tra; các bản cũ giữ để đối chiếu lịch sử.

**Đây chưa phải bản nộp hoàn chỉnh.** Theo yêu cầu của người dùng, tạm để trống thông tin lớp, giảng viên, nhóm, mã sinh viên, xác nhận đóng góp và biên bản họp chưa xác nhận. Nội dung ghi rõ: chưa kiểm chứng phát hiện dầu trên tile đã hiệu chuẩn, chưa đánh giá nhầm lẫn theo từng nguyên nhân look-alike; nhánh Niblack đã có thử nghiệm PALSAR bổ sung nhưng chưa có test Sentinel độc lập theo cảnh.

Nguồn dựng: `docs/report/narrative.json`, `bibliography.json`, `scripts/build_report.py`; quy trình dựng và cập nhật trường tại `docs/report/README.md`. Hướng dẫn GUI tại `docs/DEMO_GUI.md`, video tại `deliverables/video/README.md`. Không chỉnh trực tiếp PDF để thay số liệu hoặc mục lục; cần dựng và kiểm tra lại sau sửa.
