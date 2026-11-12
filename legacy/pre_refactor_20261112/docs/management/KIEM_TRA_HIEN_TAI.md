# Đối chiếu hiện tại với hướng dẫn BTL

Ngày kiểm tra: 11/11/2026. Bản này thay cho kết luận hiện trạng ở snapshot cũ; không sửa minh chứng lịch sử.

**Phần mã và hồ sơ kỹ thuật đã được cập nhật. Chưa thể xác nhận toàn bộ bộ nộp của nhóm hoàn tất:** video đang hoãn, MSSV/chữ ký/đánh giá thật, diễn tập, kiểm tra trùng lặp và lịch sử 8 tuần còn cần nhóm xử lý. Họ tên và GitHub đã cập nhật theo nhóm và collaborators.

Hash mã và môi trường đã đo: `28ecff90ac5cd28b2c2547ee9df86093599e3cf63e120e12cc71a356a8e4aa79`. Báo cáo nguồn `docs/report/`; slide `docs/slides/`; số liệu đóng băng kèm checksum trong `docs/report/evidence/`.

| Hạng mục | Kết luận | Minh chứng / giới hạn |
| --- | --- | --- |
| Python 3.13 và môi trường | Đạt | Python 3.13.5; uv.lock; pyproject.toml |
| TV1 trưởng nhóm, TV2–TV5 | Đạt | src/tv1…tv5; PHAN_CONG_MA_NGUON.md; trách nhiệm hiện tại |
| Lõi NumPy, không ML/DL | Đạt | TV3/TV4/metrics dùng NumPy/Python; test AST; FFT là primitive số |
| Đối chiếu các thuật toán/chỉ số | Đạt trong phạm vi đã nêu | 33 mục ×18 ca: 558 PASS, 36 DESCRIPTIVE, 0 FAIL; phân biệt API/ghép hàm/biến thể |
| Ví dụ số và hồi quy | Đạt | 5 ví dụ gọi hàm thật; 23 tests pass gồm Streamlit |
| PEP 8 và docstring | Đạt phạm vi kiểm tra | Ruff check/format cho code hiện tại; mọi hàm trong src/tv* có docstring; không chứng nhận mọi cách dùng đầu vào |
| Demo Streamlit | Đạt | streamlit_app.py; chọn ảnh, tham số, PNG/JSON; AppTest đổi Canny/morphology/00013 |
| Báo cáo PDF và nguồn | Đạt phần kỹ thuật | 42 trang; 32 trang chính; C3+C4=19 (59.38%); DOCX và LaTeX |
| Cấu trúc 5 chương | Đạt | Mở đầu 5 trang; các chương {'1': 3, '2': 8, '3': 8, '4': 11, '5': 2}; tham khảo 2 trang; phụ lục A/B/C |
| Định dạng và công thức | Đạt | A4; TNR nhúng, thân 13pt, giãn 1.3; lề 3/2/2.5/2.5; 15 công thức vector từ LaTeX và native OMML |
| Lý thuyết, giả mã, độ phức tạp | Đã bổ sung | Chương 2–3: công thức, dẫn xuất Lee, ví dụ HE/Lee, giả mã có số dòng và chi phí thời gian/bộ nhớ |
| Thực nghiệm và tái lập | Đạt | reproduce.py; so sánh lọc, CLAHE, nhiễu, ca lỗi, hai lớp; mean/std/count và seed 2026 |
| Nguồn và nhãn dữ liệu | Đã xác định từ hồ sơ cục bộ | CSIRO DOI 10.25919/4v55-dn16; license CC BY-SA 4.0; 0 không dầu, 1 có dầu |
| Phạm vi dataset | Có giới hạn đã công bố | 5.538 ảnh so với 5.630 công bố; thiếu 92; 10 mẫu là tập con; chưa có checksum gốc/mask/cảnh |
| Đánh giá không làm đẹp số liệu | Đạt | TN810 FP2885 FN204 TP1639; precision36.23%, recall88.93%; chỉ cấp ảnh |
| Tài liệu tham khảo | Đạt số lượng; cần nhóm đọc nguồn | 13 mục IEEE, ít nhất 3 bài DOI; nguồn kế thừa hồ sơ dự án, không tuyên bố đã đọc toàn văn bên ngoài |
| Slide 15–20 trang | Đạt | 18 slide PPTX/PDF, speaker notes; PowerPoint xuất PDF, 0 hộp chữ tràn; Canva MCP bị admin tắt |
| Kịch bản bảo vệ | Đã chuẩn bị | 12 phút nói +3 phút demo +5 phút vấn đáp; nhóm cần diễn tập |
| Sổ tay học theo thành viên | Đã xuất và kiểm nội dung | 5 Markdown + 5 PDF; mỗi sổ tay 10 chương, 20–25 câu hỏi có gợi ý, ví dụ tính tay và thực hành; hash trong pdf_audit.json |
| Bảng đánh giá chéo | Đạt yêu cầu tạo mẫu | 20 cặp TV1–TV5; điểm/nhận xét/chữ ký chưa điền |
| Danh tính và đóng góp thật | Tên/GitHub đã cập nhật; hồ sơ còn thiếu | Tên do nhóm cung cấp, GitHub từ collaborators; MSSV/tỷ lệ/chữ ký chờ nhóm điền |
| Video 5–7 phút | Hoãn theo yêu cầu | Không tạo video trong đợt này |
| Lịch sử Git 8 tuần | Chưa đủ minh chứng | Giữ nguyên lịch sử; không backdate/gán tác giả giả; cần giải trình theo quy định lớp |
| Nhật ký nhóm và kiểm tra trùng lặp | Nhóm cần hoàn tất | Khung 8 tuần là hồi cứu có ô minh chứng; chưa có kiểm tra trùng lặp của trường |
| Khai báo AI | Đã bổ sung | Phụ lục C nêu Codex, các phần hỗ trợ và kiểm tra; sinh viên cần tự đọc và chịu trách nhiệm |

Excel đã cập nhật họ tên/GitHub/module hiện tại ở Thanh_vien; bảng đánh giá chéo có 20 cặp, mọi ô điểm/nhận xét/chữ ký vẫn trống. Sheet Hoi_cuu_1008_1111 có 70 dòng trống để bổ sung minh chứng thật. Các sheet lịch sử và Cap_nhat_20261111 giữ như snapshot trước lần bổ sung thành viên; không tự biến thành minh chứng công việc quá khứ.

Mỗi thành viên có một sổ tay Markdown đầy đủ và một PDF cùng nội dung trong docs/thanh_vien/, thay cho ba đề cương ngắn. Mỗi bản có 10 chương, giải thích từ nền tảng, ví dụ tính tay, 20–25 câu hỏi có gợi ý và bài thực hành. Chương 8 chỉ rõ nơi lưu kết quả. Slide được chia đúng 720 giây cho năm người. Demo cho phép chọn mọi ảnh trong cả Class_0 và Class_1.

Số liệu nguồn trong manifest cũ ghi nguồn/nhãn cần xác nhận tại lúc đo; lần kiểm kê sau đó tìm được metadata CSIRO trong cùng repo. Hồ sơ dữ liệu mới bổ sung nguồn và giới hạn 92 ảnh, không thay đổi kết quả đo thuật toán.

Kiểm tra tự động không thay thế việc nhóm đọc và hiểu mọi dòng mã. Không có phép đo IoU/Dice, kết luận dầu đã xác nhận, hoặc chứng nhận đạt rubric từ giảng viên.
