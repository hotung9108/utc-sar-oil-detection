# Nguồn bộ dữ liệu SAR

Theo [metadata XML đi kèm](metadata/dataset_metadata.xml), nguồn là **CSIRO Sentinel-1 SAR image dataset of oil- and non-oil features for machine learning (Deep Learning)**, David Blondeau-Patissier, CSIRO, ngày 15/12/2022; DOI **10.25919/4v55-dn16**. Tên bộ dữ liệu không thay đổi phạm vi BTL: dự án này chỉ dùng xử lý ảnh truyền thống.

[Tệp giấy phép gốc](metadata/license.html) ghi **Creative Commons Attribution-ShareAlike 4.0 International**. Giữ attribution này cùng dữ liệu và các hình SAR dẫn xuất trong báo cáo/slide. Metadata được đọc từ dự án; không tuyên bố đã đối chiếu từng ảnh với máy chủ nguồn.

| Phần dữ liệu | Metadata công bố | Repo hiện tại | Chênh lệch |
| --- | ---: | ---: | ---: |
| Class_0: không có dầu (biển sạch hoặc look-alike) | 3.725 | 3.695 | 30 |
| Class_1: có dầu | 1.905 | 1.843 | 62 |
| Tổng | 5.630 | 5.538 | 92 |

Tất cả ảnh cục bộ là JPEG 400×400, lưu ở chế độ RGB; ứng dụng đọc thành một kênh xám. Không có tệp trùng SHA-256 trong 5.538 ảnh. Cả 10 ảnh demo khớp byte với tệp trong dataset: demo là tập con, không phải tập độc lập. Hash khác nhau không chứng minh ảnh thuộc các cảnh chụp độc lập.

Không có mask pixel, bảng ánh xạ chip–cảnh hoặc checksum bộ gốc. Không suy ra nguyên nhân thiếu 92 ảnh từ tên tệp. Kết quả báo cáo áp dụng cho toàn bộ **bản cục bộ**; không tuyên bố đã đo toàn bộ bộ sưu tập công bố.

Kiểm kê lại: `uv run --extra docs python scripts/audit_dataset.py`. Kết quả ở `results/reproducible/data_inventory.json`; bản dùng trong báo cáo ở `docs/report/evidence/reproducible_data_inventory.json`.
