# Kế hoạch nối tiếp 13–15/11/2026

Deadline: **23:59 15/11/2026 — Asia/Saigon**. Mỗi việc ước lượng 4 giờ, chưa phải giờ thực tế. Trạng thái ban đầu Chưa bắt đầu; không ghi nhận công cụ thực hiện thay cho đóng góp hay nghiệm thu của cá nhân.

Phạm vi: dọn dự án, giữ kho legacy, lưu mục tiêu và cập nhật kế hoạch. Dataset và thuật toán chi tiết lập sau. Không viết lại lịch sử Git.

| ID | Ngày | Phụ trách | Nhiệm vụ | Đầu ra | Phụ thuộc | Người kiểm tra |
| --- | --- | --- | --- | --- | --- | --- |
| R01-TV1 | 2026-11-13 | Tiến Sơn Trần | Chốt cấu trúc và mục tiêu; điều phối danh sách giữ/chuyển/xóa | docs/MUC_TIEU_DU_AN.md; README.md | Không | Lương Tiến Dũng |
| R01-TV2 | 2026-11-13 | Lương Tiến Dũng | Đối chiếu hướng dẫn BTL; ghi các tuyên bố cũ không còn đúng | docs/management/QUY_TAC_KIEM_CHUNG.md | Không | Hồ Việt Tùng |
| R01-TV3 | 2026-11-13 | Hồ Việt Tùng | Kiểm kê bộ lọc và mã số học có thể tái sử dụng | docs/management/KHA_NANG_TAI_SU_DUNG.md | Không | Nguyễn Hải Hiếu |
| R01-TV4 | 2026-11-13 | Nguyễn Hải Hiếu | Kiểm kê phân đoạn, liên thông và mã biên đang sửa | docs/management/KHA_NANG_TAI_SU_DUNG.md | Không | Phạm Minh Tuấn |
| R01-TV5 | 2026-11-13 | Phạm Minh Tuấn | Kiểm kê dữ liệu/kết quả, hash và trạng thái workbook | legacy/pre_refactor_20261112/manifest.json | Không | Tiến Sơn Trần |
| R02-TV1 | 2026-11-14 | Tiến Sơn Trần | Tích hợp cấu trúc, README, cấu hình và đường dẫn mới | README.md; src/sar_oil/ | R01-TV1 | Lương Tiến Dũng |
| R02-TV2 | 2026-11-14 | Lương Tiến Dũng | Viết tiêu chí so sánh tự cài/thư viện và bằng chứng | docs/management/QUY_TAC_KIEM_CHUNG.md | R01-TV2 | Hồ Việt Tùng |
| R02-TV3 | 2026-11-14 | Hồ Việt Tùng | Lập bảng công thức, miền đầu vào và lỗi cần kiểm tra lại | docs/management/KHA_NANG_TAI_SU_DUNG.md | R01-TV3 | Nguyễn Hải Hiếu |
| R02-TV4 | 2026-11-14 | Nguyễn Hải Hiếu | Lưu chỉnh sửa mã vùng/biên; lập bản đồ đặc trưng vùng | legacy/pre_refactor_20261112/src/tv4/ | R01-TV4 | Phạm Minh Tuấn |
| R02-TV5 | 2026-11-14 | Phạm Minh Tuấn | Nối 15 nhiệm vụ, cập nhật phân công và tiến độ riêng | docs/management/KE_HOACH_PHAN_CONG_1008_1111_2026.xlsx | R01-TV5 | Tiến Sơn Trần |
| R03-TV1 | 2026-11-15 | Tiến Sơn Trần | Kiểm tra toàn dự án và bàn giao các việc tiếp theo | docs/management/BAN_GIAO_REFACTOR.md | R02-TV1 | Lương Tiến Dũng |
| R03-TV2 | 2026-11-15 | Lương Tiến Dũng | Rà tài liệu, loại nhầm lẫn nhãn ảnh/box/mask | docs/management/BAN_GIAO_REFACTOR.md | R02-TV2 | Hồ Việt Tùng |
| R03-TV3 | 2026-11-15 | Hồ Việt Tùng | Bàn giao danh sách lọc tái sử dụng, chưa chọn thuật toán thắng | docs/management/BAN_GIAO_REFACTOR.md | R02-TV3 | Nguyễn Hải Hiếu |
| R03-TV4 | 2026-11-15 | Nguyễn Hải Hiếu | Kiểm tra mã lưu trữ; bàn giao đầu việc đặc trưng/phân lớp | docs/management/BAN_GIAO_REFACTOR.md | R02-TV4 | Phạm Minh Tuấn |
| R03-TV5 | 2026-11-15 | Phạm Minh Tuấn | Kiểm tra workbook, manifest và các thông tin dữ liệu còn thiếu | docs/management/BAN_GIAO_REFACTOR.md | R02-TV5 | Tiến Sơn Trần |

## Nghiệm thu

- Ngày 13: kiểm kê nguồn và chỉnh sửa đầy đủ.
- Ngày 14: phần hiện hành không phụ thuộc pipeline cũ; workbook giữ lịch sử.
- Ngày 15: checksum, cấu trúc, workbook và tài liệu đạt; công bố phần còn thiếu.

Workbook là nguồn cập nhật trạng thái, ngày hoàn thành, giờ thực tế và minh chứng. JSON/Markdown là định nghĩa kế hoạch ban đầu; không đồng bộ đè dữ liệu người dùng. Các vai trò không xác nhận tác giả commit cũ.
