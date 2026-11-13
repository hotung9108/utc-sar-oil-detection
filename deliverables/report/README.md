# Bản báo cáo để nhóm rà soát

- [Bản Word v8](Bao_cao_SAR_SOS_review_v8.docx)
- [Bản PDF v8](Bao_cao_SAR_SOS_review_v8.pdf)

Bản ngày 13/11/2026 có 38 trang tổng cộng, 26 trang nội dung chính, 13 tài liệu tham khảo. Đã cập nhật kết quả hiệu chuẩn Sentinel-1, ghép gió ERA5, GUI/video và thẩm định QPOSD. Các số đo SOS giữ nguyên.

Đã kiểm tra mục lục và bố cục theo `docs/report/render_audit.json` và `render_progress.json`: xem trực tiếp 11 trang thay đổi, 27 trang còn lại giống pixel với bản v7 đã duyệt. Hai tệp ở đây giữ nguyên byte của bản được kiểm tra.

**Đây chưa phải bản nộp hoàn chỉnh.** Cần thông tin lớp, giảng viên, nhóm, mã sinh viên, xác nhận đóng góp và biên bản họp thật. Nội dung cũng ghi rõ: chưa kiểm chứng phát hiện dầu trên tile đã hiệu chuẩn, chưa đánh giá nhầm lẫn theo từng nguyên nhân look-alike, nhánh Niblack chưa có test độc lập mới.

Nguồn dựng: `docs/report/narrative.json`, `bibliography.json`, `scripts/build_report.py`; quy trình dựng và cập nhật trường tại `docs/report/README.md`. Hướng dẫn GUI tại `docs/DEMO_GUI.md`, video tại `deliverables/video/README.md`. Không chỉnh trực tiếp PDF để thay số liệu hoặc mục lục; cần dựng và kiểm tra lại sau sửa.
