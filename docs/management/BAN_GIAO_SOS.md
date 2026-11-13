# Bàn giao triển khai SOS và notebook

Mục tiêu hiện hành: `../MUC_TIEU_DU_AN.md`. Phân công: `KE_HOACH_SOS_NOTEBOOK.md` và 15 dòng S01–S03 trong workbook. Các dòng W/R và minh chứng lịch sử được giữ nguyên; trạng thái công việc cá nhân mới cần chủ việc/reviewer xác nhận.

## Điểm vào

- Mã xử lý: `src/sar_oil/core.py`; đối chứng: `reference.py`.
- Dữ liệu/đánh giá: `data.py`, `evaluation.py`; huấn luyện: `models.py`.
- Pipeline/benchmark: `pipeline.py`, `experiments.py`; bảo vệ tái sử dụng kết quả: `provenance.py`.
- Chạy: `python scripts/sos.py reproduce --workers 6`.
- Notebook 01–05: dữ liệu, lọc/ngưỡng, vùng/đặc trưng, classifier, pipeline cuối. `python scripts/run_notebooks.py` chạy lại toàn bộ bằng đúng Python hiện hành.
- Báo cáo từ số liệu thật: `python scripts/summarize_results.py`, đầu ra `results/sos/REPORT.md`.

`results/sos/run_manifest.json` khóa mã thuật toán, phiên bản thư viện và manifest. Nếu đổi thuật toán/giao thức/dữ liệu, chuyển toàn bộ thư mục kết quả sang một tên lưu trữ riêng trước khi chạy thí nghiệm mới; CLI sẽ từ chối trộn kết quả cũ. `selected.json` khóa cấu hình trước test; cache test còn kiểm tra hash model/cấu hình. Không sửa số liệu bằng tay.

## Phạm vi xác nhận

Kiểm chứng gồm ca biên, đối chiếu ảnh SOS thật, matching đối tượng và tương đương giữa tính metric trực tiếp với tính từ thống kê vùng đã cache. Lint và kiểm tra cấu trúc nằm trong `tests/`. `scripts/verify_archive.py` kiểm tra bảo toàn 5938 file lịch sử. Workbook có `sos_workbook_audit.json` ghi kiểm tra công thức và giữ nguyên nội dung/style cũ.

Pipeline cuối suy luận bằng thuật toán NumPy; quá trình so sánh classifier dùng cùng bộ đặc trưng reference để cô lập khác biệt mô hình. Nhãn GT chỉ dùng ở train/evaluation, không đi vào `predict`. Notebook hiển thị output của benchmark đã chạy và chạy trực tiếp các ví dụ minh họa.

## Giới hạn còn lại

SOS không có góc tới, gió và nhãn từng loại look-alike. Vì vậy chưa thể tuyên bố hoàn thành toàn bộ yêu cầu Đề 18 hoặc triển khai cảnh báo tại miền Trung. Chuẩn hóa /255 chỉ là xử lý PNG. Chia theo patch chưa chứng minh độc lập theo cảnh. Mọi nhận xét về chất lượng và cải tiến phải đọc kết quả test/ablation tại `results/sos/REPORT.md`, kể cả kết quả thấp.

Không thêm Streamlit, AIS hoặc mô phỏng trôi dầu vào phạm vi triển khai này. Chúng vẫn là hướng phát triển tiếp sau khi dữ liệu nền đủ điều kiện.
