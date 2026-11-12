# Bàn giao tái tổ chức dự án — 12/11/2026

## Đã thực hiện

- Lưu 5.938 file trong `legacy/pre_refactor_20261112/`, gồm mã cũ, dữ liệu, báo cáo, video, chỉnh sửa chưa commit và sản phẩm từng bị Git bỏ qua. `manifest.json` ghi đường dẫn gốc/đích, kích thước, SHA-256 và move/copy; `git_status_before.txt` lưu trạng thái trước thay đổi.
- Dựng cấu trúc hiện hành theo chức năng, tách khỏi mã TV1–TV5. Không có app/demo giả hoặc pipeline mới chưa được kiểm chứng.
- Lưu mục tiêu mới, quy tắc kiểm chứng, kiểm kê khả năng tái sử dụng và phân công năm thành viên.
- Nối kế hoạch 13–15/11/2026 vào workbook hiện có: giữ 70 nhiệm vụ lịch sử, thêm 15 nhiệm vụ, cập nhật hướng dẫn, vai trò, lịch, các sheet cá nhân và tiến độ riêng.
- Giữ nguyên môi trường `.venv`, cấu hình cá nhân và lịch sử Git. Cấu hình hiện hành và lockfile không còn phụ thuộc ứng dụng cũ; bản cấu hình cũ được lưu trong legacy.

## Kiểm chứng

| Kiểm tra | Kết quả |
| --- | --- |
| SHA-256 và kích thước của toàn bộ file lưu trữ | 5.938/5.938 khớp |
| Kiểm tra cấu trúc, phụ thuộc lịch, người phụ trách/kiểm tra | 3 kiểm thử đạt |
| Lịch sử workbook | Giá trị, công thức và định dạng các hàng lịch sử được giữ |
| Kế hoạch nối tiếp | 15 ID duy nhất; mỗi người 3 việc; 13–15/11/2026 |
| Tiến độ mới | Mỗi người 3 việc, 12 giờ dự kiến; ban đầu 0 hoàn thành |
| Thử tính lại | Đổi một việc thành Hoàn thành: 1/3 và báo thiếu minh chứng; trả lại Chưa bắt đầu: 0/3 |
| Hiển thị workbook | Đã xem các vùng thay đổi trên cả 10 sheet |
| Bộ lọc Excel | Phục hồi và mở rộng vùng bộ lọc sau khi xuất |

Kiểm tra workbook bằng artifact-tool và đọc lại OOXML/openpyxl; chưa kiểm thử tương tác trực tiếp trong Microsoft Excel. File `workbook_audit.json` ghi kết quả. Không dùng công cụ kiểm chứng này để tự xác nhận đóng góp của thành viên.

Lệnh chạy lại từ gốc repo:

```powershell
python -m unittest discover -s tests -v
python scripts/verify_archive.py
```

## Giữ, chuyển và xóa

- Giữ hiện hành: tài liệu gốc, danh mục nguồn SAR, mục tiêu, workbook nối tiếp, danh tính thành viên và cấu hình dự án mới.
- Chuyển legacy: các đường dẫn cụ thể trong manifest; bao gồm source báo cáo, slide/video, scripts, dataset cũ, kết quả, mã và bài kiểm tra cũ.
- Xóa: cache ở gốc workspace và bytecode sinh lại được. Không xóa dữ liệu hoặc mã không có bản lưu. Cache trong snapshot được giữ nguyên để không phá checksum.
- Không commit, push hoặc viết lại lịch sử Git. Git hiển thị nhiều file xóa ở vị trí cũ và file mới ở legacy là hệ quả của chuyển đường dẫn; có thể đối chiếu manifest trước khi commit.

## Những việc tiếp theo chưa thực hiện

1. Thẩm định ảnh/nhãn/giấy phép/metadata của các nguồn ưu tiên; chốt dataset và tài nguyên.
2. Thiết kế split độc lập, giao thức đối tượng, bộ thuật toán so sánh và thí nghiệm giảm báo nhầm.
3. Triển khai lọc/chuẩn hóa góc tới/ngưỡng thích nghi, đặc trưng, CART/SVM tự cài và đối chứng thư viện.
4. Chạy số liệu mới, lựa chọn phương pháp và xây demo/báo cáo/slide mới.

Deadline 23:59 ngày 15/11/2026 chỉ áp dụng đợt dọn và tổ chức lại. Các nhiệm vụ trong workbook để Chưa bắt đầu nhằm chờ thành viên tự rà soát, cập nhật và nghiệm thu; thay đổi kỹ thuật trong lần bàn giao này không phải bằng chứng tác giả hoặc thời gian làm của từng người.
