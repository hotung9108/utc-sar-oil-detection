# Kiểm tra báo nhầm trên DARTIS no-oil

Mô hình SOS được giữ nguyên; không huấn luyện lại hoặc chọn tham số theo kết quả DARTIS.
Giao thức đã cố định trước suy luận: `protocol.json`. Đầu vào giữ nguyên kích thước,
PIL grayscale chia 255; một ảnh báo nhầm nếu có ít nhất một vùng được giữ là dầu.

| Tập | Ảnh | Ảnh báo nhầm | Tỷ lệ báo nhầm | Vùng/ảnh | Pixel dự đoán dầu |
|---|---:|---:|---:|---:|---:|
| Toàn bộ | 2290 | 1449 | 63.2751% | 1.2393 | 28.4354% |
| Bờ (nc) | 351 | 337 | 96.0114% | 2.4217 | 58.6933% |
| Biển (nw) | 1939 | 1112 | 57.3491% | 1.0253 | 22.9581% |

## Theo cụm do nhà phát hành cung cấp

Các mã cụm là nhóm K-means; không phải nhãn gió yếu, màng sinh học hay mưa.

| Cụm | Ảnh | Ảnh báo nhầm | Tỷ lệ |
|---|---:|---:|---:|
| nc-00 | 76 | 73 | 96.0526% |
| nc-01 | 84 | 82 | 97.6190% |
| nc-02 | 75 | 66 | 88.0000% |
| nc-03 | 44 | 44 | 100.0000% |
| nc-04 | 72 | 72 | 100.0000% |
| nw-00 | 172 | 118 | 68.6047% |
| nw-01 | 171 | 19 | 11.1111% |
| nw-02 | 160 | 135 | 84.3750% |
| nw-03 | 162 | 119 | 73.4568% |
| nw-04 | 81 | 24 | 29.6296% |
| nw-05 | 166 | 11 | 6.6265% |
| nw-06 | 166 | 61 | 36.7470% |
| nw-07 | 171 | 112 | 65.4971% |
| nw-08 | 175 | 155 | 88.5714% |
| nw-09 | 168 | 87 | 51.7857% |
| nw-10 | 174 | 157 | 90.2299% |
| nw-11 | 173 | 114 | 65.8960% |

## Giới hạn diễn giải

- Tập này chỉ có nhãn no-oil: không ước lượng Recall dầu hoặc F1 toàn bài.
- Báo nhầm mức ảnh không cùng đại lượng với Precision/Recall/F1 đối tượng SOS.
- Có patch chung cảnh; không giả định các patch độc lập để tính khoảng tin cậy.
- JPEG, độ phân giải và tiền xử lý DARTIS khác SOS. Không quy toàn bộ sai lệch cho một yếu tố.
- Nhãn tham chiếu do nhà phát hành cung cấp; không phải xác nhận hiện trường của nhóm.
- Chưa phải kiểm chứng theo từng loại look-alike vật lý hoặc vùng biển Việt Nam.

## Bằng chứng và tái tạo

Nguồn: [DARTIS, PANGAEA](https://doi.pangaea.de/10.1594/PANGAEA.980773).
Kết quả từng ảnh, hash, số vùng và pixel: `evaluation.json`.
Notebook: `notebooks/external/06_dartis_false_alarms.ipynb`.

```text
python scripts/download_dartis.py --workers 1
python scripts/evaluate_dartis.py --workers 4
python scripts/report_dartis.py
python scripts/run_notebooks.py --notebook notebooks/external/06_dartis_false_alarms.ipynb
```
