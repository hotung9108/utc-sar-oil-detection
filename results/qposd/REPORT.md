# QPOSD: phân lớp và phát hiện dầu/tương tự dầu

Dữ liệu bổ sung UAVSAR L-band; SOS vẫn là tập chính. Nguồn:
[QPOSD, CC BY 4.0](https://zenodo.org/records/19258036).

## Dữ liệu và cách chọn

24/41 cặp có kích thước ảnh–nhãn phù hợp; loại 17 cặp không khớp, không resize nhãn.
Đã kiểm tra đủ MAT, CRC/hash, giá trị hữu hạn và xem 24 cặp ảnh/nhãn.
Giao thức v2 giữ nguyên nhóm giao trùng chính xác {19,20} và {21,22,33,35}.
Không có điểm test từ v1. Kiểm tra giao trùng không chứng minh độc lập cảnh.

- train: [4, 8, 10, 19, 20, 21, 22, 26, 28, 33, 34, 35, 36, 41]
- validation: [13, 15, 16, 32, 39]
- test: [14, 17, 18, 24, 25]

Chọn mô hình bằng macro-F1 phân lớp trên vùng tham chiếu validation, sau đó
chọn cấu hình tìm vùng bằng macro-F1 đối tượng validation. Cố định IoU ≥ 0,5,
ghép một-một; hòa điểm dùng thứ tự cấu hình. Không chọn theo test.

## Mười bộ phân lớp (cùng đặc trưng NumPy)

| ID | Cấu hình | Macro-F1 NumPy | Macro-F1 thư viện | Đồng thuận |
|---:|---|---:|---:|---:|
| 0 | {'kind': 'svm', 'params': {'C': 0.01}} | 0.455587 | 0.455587 | 1.000000 |
| 1 | {'kind': 'svm', 'params': {'C': 0.1}} | 0.457919 | 0.457919 | 1.000000 |
| 2 | {'kind': 'svm', 'params': {'C': 1.0}} | 0.457919 | 0.457919 | 1.000000 |
| 3 | {'kind': 'svm', 'params': {'C': 10.0}} | 0.468160 | 0.468160 | 1.000000 |
| 4 | {'kind': 'cart', 'params': {'max_depth': 2, 'min_leaf': 1}} | 0.393300 | 0.393300 | 1.000000 |
| 5 | {'kind': 'cart', 'params': {'max_depth': 2, 'min_leaf': 5}} | 0.393300 | 0.393300 | 1.000000 |
| 6 | {'kind': 'cart', 'params': {'max_depth': 3, 'min_leaf': 1}} | 0.606895 | 0.606895 | 1.000000 |
| 7 | {'kind': 'cart', 'params': {'max_depth': 3, 'min_leaf': 5}} | 0.606895 | 0.606895 | 1.000000 |
| 8 | {'kind': 'cart', 'params': {'max_depth': 5, 'min_leaf': 1}} | 0.623805 | 0.623805 | 1.000000 |
| 9 | {'kind': 'cart', 'params': {'max_depth': 5, 'min_leaf': 5}} | 0.549626 | 0.583005 | 0.965347 |

Được chọn: ID 8. Đây là phân lớp có sẵn vùng, không phải phát hiện.

## Mười cấu hình tìm vùng (cùng mô hình NumPy đã khóa)

| ID | Cấu hình | Macro-F1 NumPy | Macro-F1 thư viện |
|---:|---|---:|---:|
| 0 | {'filter': 'none', 'size': 7, 'looks': 4, 'threshold': {'name': 'otsu'}, 'min_area': 64, 'morphology': 'none'} | 0.056338 | 0.056338 |
| 1 | {'filter': 'none', 'size': 7, 'looks': 4, 'threshold': {'name': 'niblack', 'size': 31, 'k': 0.2}, 'min_area': 64, 'morphology': 'none'} | 0.018973 | 0.018973 |
| 2 | {'filter': 'none', 'size': 7, 'looks': 4, 'threshold': {'name': 'niblack', 'size': 31, 'k': 0.5}, 'min_area': 64, 'morphology': 'none'} | 0.022043 | 0.022043 |
| 3 | {'filter': 'none', 'size': 7, 'looks': 4, 'threshold': {'name': 'niblack', 'size': 51, 'k': 0.2}, 'min_area': 64, 'morphology': 'none'} | 0.024731 | 0.024731 |
| 4 | {'filter': 'none', 'size': 7, 'looks': 4, 'threshold': {'name': 'niblack', 'size': 51, 'k': 0.5}, 'min_area': 64, 'morphology': 'none'} | 0.041882 | 0.041882 |
| 5 | {'filter': 'lee', 'size': 7, 'looks': 4, 'threshold': {'name': 'otsu'}, 'min_area': 64, 'morphology': 'none'} | 0.037500 | 0.037500 |
| 6 | {'filter': 'lee', 'size': 7, 'looks': 4, 'threshold': {'name': 'niblack', 'size': 31, 'k': 0.2}, 'min_area': 64, 'morphology': 'none'} | 0.013249 | 0.013250 |
| 7 | {'filter': 'lee', 'size': 7, 'looks': 4, 'threshold': {'name': 'niblack', 'size': 31, 'k': 0.5}, 'min_area': 64, 'morphology': 'none'} | 0.008025 | 0.008025 |
| 8 | {'filter': 'lee', 'size': 7, 'looks': 4, 'threshold': {'name': 'niblack', 'size': 51, 'k': 0.2}, 'min_area': 64, 'morphology': 'none'} | 0.010360 | 0.010361 |
| 9 | {'filter': 'lee', 'size': 7, 'looks': 4, 'threshold': {'name': 'niblack', 'size': 51, 'k': 0.5}, 'min_area': 64, 'morphology': 'none'} | 0.014396 | 0.014397 |

Được chọn: ID 0.

## Toàn bộ năm ảnh test

| Phép đo | Lớp | TP | FP | FN | Precision | Recall | F1 |
|---|---|---:|---:|---:|---:|---:|---:|
| Phân lớp có sẵn vùng | oil | 9 | 53 | 6 | 0.145161 | 0.600000 | 0.233766 |
| Phân lớp có sẵn vùng | look_alike | 125 | 6 | 53 | 0.954198 | 0.702247 | 0.809061 |
| Phát hiện NumPy | oil | 3 | 35 | 12 | 0.078947 | 0.200000 | 0.113208 |
| Phát hiện NumPy | look_alike | 6 | 658 | 172 | 0.009036 | 0.033708 | 0.014252 |
| Phát hiện thư viện | oil | 3 | 35 | 12 | 0.078947 | 0.200000 | 0.113208 |
| Phát hiện thư viện | look_alike | 6 | 658 | 172 | 0.009036 | 0.033708 | 0.014252 |

## Nhầm lẫn và đối tượng nhỏ

Phân lớp có sẵn vùng: dầu → tương tự dầu = 0.400000; tương tự dầu → dầu = 0.297753.
Tỷ lệ là phân số từ 0 đến 1. Ma trận có hàng thật, cột dự đoán.
Ma trận phân lớp [tương tự dầu, dầu]: `[[125, 53], [6, 9]]`.
Ma trận ghép không gian [dầu, tương tự dầu]: `[[3, 0], [6, 6]]`.
GT không ghép: `[12, 166]`; dự đoán không ghép: `[29, 658]`.
Ma trận ghép không gian chỉ mô tả đối tượng ghép được, không thay thế Recall.

| Lớp | Kích thước GT | GT | TP | Recall |
|---|---|---:|---:|---:|
| oil | below_64 | 5 | 0 | 0.000000 |
| oil | at_least_64 | 10 | 3 | 0.300000 |
| look_alike | below_64 | 74 | 1 | 0.013514 |
| look_alike | at_least_64 | 104 | 5 | 0.048077 |

## Giới hạn và tái tạo

- Nhãn tương tự dầu là lớp chung; không có nhãn nguyên nhân gió yếu/màng sinh học/mưa.
- Năm ảnh test đã được xem để kiểm tra ảnh–nhãn; không gọi đây là đánh giá mù.
- Phân đoạn liên thông từ mask không tương đương số sự kiện dầu độc lập.
- Diện tích tối thiểu 64 chỉ áp dụng ứng viên; giữ cả GT nhỏ khi đánh giá.
- Không suy góc tới hoặc gió từ T11. Chưa kiểm chứng trên vùng biển Việt Nam.
- Nhánh thư viện dùng cùng classifier NumPy để tách khác biệt phép xử lý ảnh.
- Thời gian từng lượt không phải benchmark kiểm soát tải máy.

Chạy `python scripts/report_qposd.py` sau khi có đủ kết quả. Script xác minh hash,
lựa chọn đã khóa, số ảnh, mask đã lưu và tổng hợp lại các số đếm trước khi viết bảng.
Notebook 10 chạy lại suy luận hai backend, đối chiếu mask từng pixel và hiển thị năm ảnh test.
