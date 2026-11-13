# Kết quả thực nghiệm

Kết quả hiện hành nằm trong `results/reproducible/` và `results/verification/`, tính từ gốc dự án. Trên máy này, gốc là `D:\Codin\utc-code\HK4_1\XLA\BTL`.

| Cần xem | File/thư mục |
| --- | --- |
| Kết quả từng ảnh trong 5.538 ảnh đã chạy | [dataset_per_image.csv](reproducible/dataset_per_image.csv) — đường dẫn, nhãn, quyết định, số vùng, diện tích, tương phản và thời gian |
| Tổng đúng/sai cấp ảnh | [confusion.json](reproducible/confusion.json) |
| Thống kê theo lớp | [dataset_summary.csv](reproducible/dataset_summary.csv) |
| Cấu hình, môi trường, thời điểm, hash và phạm vi lần chạy | [manifest.json](reproducible/manifest.json) |
| Ảnh 00013 sau Lee + CLAHE và phân đoạn | [class_1_00013_clahe.png](reproducible/class_1_00013_clahe.png) |
| Đối chứng 00013 khi tắt CLAHE | [class_1_00013_none.png](reproducible/class_1_00013_none.png) |
| Phóng vùng ảnh 00013 | [roi_00013.png](reproducible/roi_00013.png) |
| Khảo sát lọc, CLAHE, nhiễu và ca lỗi | Các file `*_per_image.csv`, `*_summary.csv` trong `reproducible/` |
| Kiểm chứng với thư viện và ví dụ tính tay | `verification/per_case.csv`, `summary.csv`, `hand_examples.json` |

**Chưa có 5.538 bộ ảnh PNG/mask.** Lượt batch toàn tập lưu số liệu theo từng ảnh. Các PNG tự động là hình minh họa 00013 và các ca biển `sea_surface_01`–`05`, không phải ảnh đầu ra của mọi hàng CSV. Muốn xem một ca cụ thể, chọn ảnh đó trong demo với đúng cấu hình. Chương 8.5 của mỗi [sổ tay thành viên](../docs/thanh_vien/README.md) có đoạn Python để lưu một bộ ảnh và JSON vào `results/manual_00013/`.

Các nút tải của demo cung cấp `enhanced.png`, `boundary.png`, `mask.png` (khi có mask) và `sar_result.json`. Chúng được trình duyệt tải vào thư mục người dùng chọn, thường là Downloads; demo không tự ghi chúng vào `results/`. Overlay hiện được hiển thị trên giao diện.

Git chỉ theo dõi hướng dẫn này trong `results/`; CSV và ảnh sinh ra được bỏ qua. Vì vậy các liên kết đầu ra ở trên chỉ mở được sau khi đã chạy trên máy. **Bản số liệu được commit cùng báo cáo** nằm trong [docs/report/evidence](../docs/report/evidence/) với tiền tố `reproducible_`/`verification_`, kèm `checksums.json`. Các hình được chọn đưa vào báo cáo nằm trong [docs/report/assets](../docs/report/assets/).

Chạy từ thư mục gốc dự án:

```powershell
uv run python reproduce.py --workers 4
```

- `verification/`: 5 ví dụ số và 594 đối chiếu, phân biệt PASS/DESCRIPTIVE/FAIL.
- `reproducible/`: số đo từng ảnh, mean/std/count, khảo sát tham số/nhiễu, ca thất bại và đánh giá cả Class_0/Class_1.
- `reproducible/manifest.json`: seed, cấu hình, môi trường, hash nguồn và phạm vi đã hoàn tất. `--samples-only` không xác nhận kết quả toàn dataset.

Các thư mục tables/, figures/, edge_evaluation_output/ nếu còn trên máy là đầu ra cũ. Chỉ số cấp ảnh không thay thế đánh giá mask pixel. Trình dựng báo cáo yêu cầu manifest đầy đủ và khớp mã nguồn hiện tại.

Các lệnh thực nghiệm có thể ghi đè file cùng tên. `--samples-only` không chạy lại toàn tập và thay phạm vi manifest bằng `samples`; đừng dùng nó để xác nhận lần đo đầy đủ. Chỉ sửa tài liệu MD/PDF không có nghĩa thuật toán đã chạy lại: kiểm thời điểm và cấu hình trong manifest để biết nguồn gốc số liệu.
