# Phát hiện dầu tràn trên biển từ ảnh SAR — Đề 18

Dự án đang ở giai đoạn tái tổ chức: **chưa chốt dataset, chưa có pipeline hoặc kết quả thực nghiệm mới**. Phiên bản xử lý ảnh trước đây được lưu riêng trong `legacy/pre_refactor_20261112/`.

- [Mục tiêu và tiêu chí khoa học](docs/MUC_TIEU_DU_AN.md)
- [Danh mục nguồn dữ liệu và link](docs/NGUON_DU_LIEU_SAR_DAU_TRAN.md)
- [Kế hoạch và phân công 13–15/11/2026](docs/management/KE_HOACH_REFACTOR_3_NGAY.md)
- [Workbook kế hoạch nối tiếp](docs/management/KE_HOACH_PHAN_CONG_1008_1111_2026.xlsx)
- [Bàn giao và kết quả kiểm tra](docs/management/BAN_GIAO_REFACTOR.md)
- [Hướng dẫn BTL gốc](docs/00_tai_lieu_goc/huong_dan_btl_docx/)

## Cấu trúc

`src/sar_oil/`: mã mới theo chức năng; `tests/`: kiểm tra hiện hành; `configs/`: cấu hình nghiên cứu sau khi chốt dữ liệu; `data/`: manifest/hướng dẫn dữ liệu; `results/`: đầu ra mới; `docs/`: tài liệu hiện hành; `legacy/`: phiên bản lịch sử.

## Kiểm tra

Python 3.13+. Không cần thư viện ngoài cho bộ kiểm tra cấu trúc hiện tại:

```powershell
python -m unittest discover -s tests -v
python scripts/verify_archive.py
```

Không có lệnh chạy demo mới ở giai đoạn này. Không dùng báo cáo, video hoặc số liệu trong legacy làm kết quả của hướng mới. Môi trường `.venv` hiện có được giữ; không cần đồng bộ/xóa môi trường đó để chạy kiểm tra cấu trúc.
