# Đánh giá bổ sung trên 3.101 patch PALSAR

Quần thể: toàn bộ `external_train` của manifest SOS. Đây là tập tác giả gọi
`train`, nhưng không dùng để fit hoặc chọn cấu hình trong pipeline hiện tại.
Hai mô hình được khóa trước suy luận; không chọn mô hình thắng hoặc chỉnh lại
tham số từ phép thử này. Giao thức: `protocol.json`.

| Nhánh NumPy | Ảnh | TP | FP | FN | Precision | Recall | F1 | IoU pixel |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| otsu | 3101 | 6170 | 11014 | 12978 | 0.359055 | 0.322227 | 0.339645 | 0.641096 |
| niblack | 3101 | 5180 | 17199 | 13968 | 0.231467 | 0.270524 | 0.249476 | 0.494529 |

## Giới hạn

- Đây là phép thử bổ sung chuyển sensor, không phải tập Sentinel mới ngoài khơi Việt Nam.
- Kiểm tra hash và pixel trùng hoàn toàn không chứng minh độc lập theo cảnh hoặc loại trừ patch chồng lấn.
- Chưa xác minh lịch sử mọi lần xem thủ công dữ liệu; chỉ kiểm tra luồng fit/search và kết quả pipeline hiện tại.
- Hai pipeline khác cả bộ lọc/tham số lẫn classifier; không quy chênh lệch riêng cho Otsu hoặc Niblack.
- Nguồn nhãn SOS là dầu/nền, không phân biệt từng nguyên nhân look-alike.
- Kết quả không thay thế các test SOS trước đó; không gộp các tập có khả năng chung cảnh.

## Tái tạo

```text
python scripts/audit_palsar_holdout.py
python scripts/evaluate_palsar_holdout.py --prepare
python scripts/evaluate_palsar_holdout.py --run --workers 4
python scripts/report_palsar_holdout.py
```
