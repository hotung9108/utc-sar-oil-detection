# Thẩm định QPOSD để bổ sung nhãn look-alike

Ngày kiểm tra: 13/11/2026. Refined SOS vẫn là tập dữ liệu chính đã được nhóm chọn. QPOSD là nhánh khảo sát bổ sung, chưa có kết quả mô hình và không thay thế benchmark Sentinel-1.

## Nguồn và quyền sử dụng

Đã đọc metadata từ [API Zenodo của bản 19258036](https://zenodo.org/api/records/19258036). Giấy phép ghi `cc-by-4.0`. ZIP công bố dài 3.871.940.048 byte, MD5 `876771b06f9ae344bdb1843f98b0a7aa`. Hai script ví dụ của nhà phát hành đã tải, kiểm tra MD5 và đọc mã; không thực thi.

`scripts/audit_qposd.py` đọc ZIP bằng HTTP Range, giới hạn tổng tải 32 MiB, từ chối máy chủ trả toàn bộ tệp hoặc sai Content-Range. Mỗi mask được kiểm tra CRC bởi `zipfile`, lưu SHA-256 và đếm pixel theo màu. Chưa tải toàn ZIP nên **chưa xác nhận MD5 toàn ZIP**. Thông tin thực tế nằm trong `qposd_mask_audit.json`; dữ liệu tải về nằm dưới `data/lookalike_sources/`, không đưa vào Git.

## Ý nghĩa nhãn

README trong ZIP và ví dụ đọc dữ liệu của nhà phát hành thống nhất: biển `(0,0,255)`, dầu `(255,0,0)`, look-alike `(0,255,0)`, đất `(0,0,0)`. Look-alike là một lớp chung, không có mã riêng cho gió yếu, màng sinh học và mưa. Không suy ra nguyên nhân từ màu xanh.

Đã quan sát màu ngoài bảng mã, ví dụ `(12,255,14)` và `(198,118,255)`. `scripts/qposd_labels.py` giữ các pixel này ở nhãn bỏ qua `255`; không làm tròn về màu gần nhất, không tự gán thành biển. Khi đánh giá phải áp dụng cùng vùng hợp lệ cho cả dự đoán và tham chiếu, công bố số pixel bỏ qua và cách xử lý đối tượng chạm vùng này trước khi chạy mô hình.

## Điều kiện trước thực nghiệm

Kiểm tra đủ **41 mask** đã hoàn tất, tải 495.238 byte qua Range. Số pixel đọc trực tiếp: biển 61.140.336; dầu 12.490.448; look-alike 4.780.381; đất 1.550.227; ngoài bảng mã 2.117. Có 29 mask chứa dầu, 11 chứa look-alike; các số này không phải split train/test. Bộ giải mã đã được đối chiếu trên toàn bộ 41 mask. Audit lưu cả từng màu lạ và tần suất, không chỉ tổng số.

Số đếm trực tiếp khác một số tổng lớp trong bảng bài báo mô tả; cần dùng số đo từ phiên bản tệp thực tế và nêu khác biệt, không sửa nhãn để ép khớp bảng công bố.

1. Kiểm tra cặp tên, kích thước và nội dung giữa 41 mask với các mảng `.mat`; hiện audit mask chưa chứng minh ảnh và nhãn căn chỉnh.
2. Xác minh ý nghĩa chín kênh, bước chuẩn hóa và khả năng chọn cường độ phù hợp. Không coi kênh T11 mặc nhiên là VV hay đưa trực tiếp vào mô hình SOS với phép chia 255.
3. Xác minh các mẫu chung cảnh/chuyến bay, chia theo nhóm nguồn trước khi cắt patch. Script ví dụ của tác giả chia ngẫu nhiên sau cắt patch; không dùng cách đó để tuyên bố độc lập theo cảnh.
4. Chốt xử lý màu ngoài bảng mã và đối tượng rất nhỏ. Không tự loại các pixel dầu lẻ để khớp số liệu bài báo.
5. Định nghĩa giao thức đánh giá dầu/look-alike chung, tách khỏi bài toán xác định từng nguyên nhân vật lý. Chỉ dùng nhãn để đánh giá hoặc huấn luyện trên phần train, không tạo ảnh đầu vào từ mask.

QPOSD dùng UAVSAR băng L; kết quả của nhánh bổ sung phải ghi riêng, không diễn giải thành độ chính xác của Sentinel-1 ngoài khơi Việt Nam. Các kiểm tra này chưa giải quyết nhãn vật lý cho gió yếu/màng sinh học/mưa trên dữ liệu chính.

## Tái tạo

### Mẫu look-alike khớp kích thước đã đọc đầy đủ

Sau khi sàng lọc header, đã chọn mẫu 41 vì có MAT nén nhỏ nhất trong tám cặp
khớp kích thước chứa look-alike. Đã tải đủ 50.758.204 byte MAT, kiểm tra CRC,
lưu SHA-256 và đọc bằng SciPy: T có kích thước 1031×1031×9, float64, toàn bộ
giá trị hữu hạn; mask 1031×1031. Bằng chứng riêng nằm trong
`qposd_matched_lookalike_audit.json`, không ghi đè audit ba mẫu ban đầu.

Mask chứa 18.671 pixel look-alike, 890.637 biển và 153.653 đất, không có dầu.
Hình đối chiếu riêng ảnh T11 thang log và mask gốc đã được xem: đường bờ có
hình dạng tương ứng, nhãn look-alike tập trung dọc bờ. Đây là quan sát trực
quan, chưa định lượng sai số căn chỉnh và không xác nhận nguyên nhân vật lý
của vùng tối. Mẫu này không đủ để tính Recall dầu hoặc huấn luyện hai lớp
dầu/look-alike. Chưa chạy classifier trên mẫu 41.

```powershell
.venv/Scripts/python.exe scripts/inspect_qposd_features.py --numbers 41 --output docs/management/qposd_matched_lookalike_audit.json --selection-reason "Smallest compressed MAT among dimension-matching pairs with look-alike labels; structural inspection only, not a benchmark split"
```

### Kiểm tra phần đầu MAT trên toàn bộ 41 cặp

`scripts/audit_qposd_shapes.py` đã đọc đủ 41 phần đầu MAT qua HTTP Range, tổng tải 687.432 byte. Có **24 cặp khớp kích thước, 17 cặp lệch**. Các mẫu lệch là 1, 2, 3, 5, 6, 7, 9, 11, 12, 23, 27, 29, 30, 31, 37, 38, 40; một số thiếu cột, một số thiếu cả hàng và cột. Trong 24 cặp khớp, tám mask có pixel look-alike: 15, 24, 25, 26, 32, 34, 36, 41.

Đây là sàng lọc cấu trúc, không phải quyết định tự động loại mẫu rồi báo benchmark trên phần còn lại. Chỉ đọc prefix nên **chưa xác nhận CRC toàn bộ MAT**, chưa đọc toàn bộ giá trị số và chưa chứng minh căn chỉnh pixel. Parser giới hạn ở bố cục little-endian, phần tử nén đầu tiên chứa mảng T ba chiều, đã đối chiếu kích thước với SciPy trên ba tệp đầy đủ. Bằng chứng: `qposd_shape_audit.json`; prefix được lưu cùng SHA-256 để kiểm tra lại.

Notebook `notebooks/external/08_qposd_audit.ipynb` đọc lại mask thật, đếm pixel, kiểm tra prefix và trình bày bảng đủ 41 cặp. Nó không chạy classifier hoặc tạo kết quả F1.

### Kết quả kiểm tra ảnh–mask trên ba mẫu nhỏ

`scripts/inspect_qposd_features.py` đã tải và kiểm tra CRC ba mảng `.mat` (mẫu 7, 35, 40), lưu `qposd_feature_audit.json`. Ba mẫu được chọn vì dung lượng nhỏ và có nhóm nhãn khác nhau; không phải mẫu đánh giá ngẫu nhiên.

| Mẫu | Mảng T | Mask | Khớp kích thước |
|---|---|---|---|
| 7 | 521×521×9 | 521×520 | Không |
| 35 | 771×771×9 | 771×771 | Có |
| 40 | 521×521×9 | 521×520 | Không |

Cả ba mảng T là float64, giá trị hữu hạn. Tệp lưu thêm các biến phụ; `fileNames` ở mẫu 7 là tên các kênh `T11.bin`, `T12_imag.bin`…, không phải mã cảnh UAVSAR. Các giá trị kênh không bị giới hạn trong [0,1]; không được áp dụng quy trình PNG/chia 255 của SOS vào những mảng này. Folder thực tế là `train_images_9ch`, khác tên minh họa `train_images_T9` trong script nhà phát hành.

**Hai trong ba cặp không đạt điều kiện kích thước.** Chưa biết cột nào thiếu hoặc quy trình xuất mask gây ra sai lệch; không tự resize/crop và không báo F1 trên các cặp này. Mẫu 35 khớp kích thước chỉ vượt qua kiểm tra cấu trúc, chưa chứng minh căn chỉnh từng pixel. Hiện QPOSD chưa sẵn sàng làm benchmark bổ sung của dự án; cần xác minh quy trình tạo nhãn/căn chỉnh trước.

```powershell
.venv/Scripts/python.exe scripts/audit_qposd.py
.venv/Scripts/python.exe scripts/inspect_qposd_features.py
.venv/Scripts/python.exe scripts/audit_qposd_shapes.py
.venv/Scripts/python.exe scripts/build_qposd_notebook.py
.venv/Scripts/python.exe scripts/run_notebooks.py --notebook notebooks/external/08_qposd_audit.ipynb
.venv/Scripts/python.exe -m unittest discover -s tests -p "test_qposd*.py" -v
```

Năm kiểm tra bao phủ mã màu/nhãn bỏ qua, từ chối mask sai định dạng, giới hạn tải và phản hồi Range không hợp lệ. Đây là kiểm tra bộ đọc, chưa phải đánh giá mô hình.
