# Thử nghiệm bổ sung QPOSD

SOS vẫn là tập chính. QPOSD cung cấp nhãn dầu/tương tự dầu chung trên UAVSAR
L-band, không có nhãn nguyên nhân gió yếu, màng sinh học và mưa. Hiện đã cố
định giao thức và trích một phần đặc trưng; **chưa có điểm phân lớp hoặc
phát hiện QPOSD**.

## Giao thức trước huấn luyện

`protocol.json` được tạo bởi `scripts/prepare_qposd_protocol.py`, không đọc
bất kỳ dự đoán nào. Lệnh từ chối ghi đè nếu giao thức thay đổi.

| Tập | ID ảnh nguồn |
|---|---|
| Train | 4, 8, 10, 17, 19, 20, 22, 26, 28, 33, 34, 35, 36, 41 |
| Validation | 13, 15, 16, 32, 39 |
| Test | 14, 18, 21, 24, 25 |

Chia theo ảnh trước khi lấy vùng, seed 2026, phân tầng theo lớp chiếm nhiều
pixel hơn trong mỗi ảnh. Có 16 ảnh chủ yếu dầu và 8 ảnh chủ yếu tương tự dầu;
train lấy 10+4, validation 3+2, test 3+2. Ba pixel dầu trong ảnh 32 vẫn giữ
nhãn dầu. Tỉ lệ này là lựa chọn thiết kế cho tập nhỏ, không phải tỉ lệ tối
ưu được chứng minh bằng định lý. Chưa có ID cảnh để chứng minh độc lập cảnh.

Giao thức quy định 10 cấu hình SVM/CART, chọn bằng macro-F1 phân lớp trên
validation; sau đó chọn trong 10 cấu hình tạo vùng bằng trung bình F1 mức
đối tượng của hai lớp trên validation. Test chỉ chấm sau khi lưu mô hình và
cấu hình thắng. Khi hòa điểm, dùng thứ tự danh sách cấu hình cố định, không
dùng thời gian chạy một lần hoặc kết quả test để phá hòa.

Hai phép đo khác nhau:

- Phân lớp có sẵn vùng: dùng hình học vùng nhãn để đánh giá bộ phân lớp.
- Phát hiện đầu-cuối: sinh ứng viên từ ảnh, trích đặc trưng, phân lớp rồi
  ghép đối tượng với nhãn tại IoU ≥ 0,5. Không cấp mask cho bước suy luận.

Không bỏ nhãn nhỏ hơn 64 pixel khỏi ground truth. Biển và đất liền không
bị loại khỏi dự đoán bằng mask thật; phát hiện sai tại đó vẫn tính FP.

## Đặc trưng và đối chiếu đã chạy

```powershell
.\.venv\Scripts\python.exe scripts/prepare_qposd_protocol.py
.\.venv\Scripts\python.exe scripts/extract_qposd_regions.py --numbers 4 8 35 41
```

Lệnh trích đặc trưng chỉ nhận ảnh train/validation và từ chối ghi đè kết quả
đã có. Các tệp `regions/image*.json` lưu SHA-256 của ảnh, mask, giao thức,
mã NumPy và mã tham chiếu, cùng đặc trưng hai cách tính cho từng đối tượng.
Muốn tái tạo cần dùng bản sao thư mục kết quả, không xóa bằng chứng gốc.

Đã chạy 4 ảnh trên và ảnh train số 10, gồm 94 vùng. Sai số lớn nhất trên tất cả đặc trưng:
`1.8349904928882665e-11`; trên ảnh chuẩn hóa:
`1.2308238472868993e-7`. Số liệu chỉ thuộc bốn ảnh này. Thời gian trong JSON
là một lần chạy và nhánh NumPy gồm cả gán nhãn; không phải phép so tốc độ
công bằng của hai pipeline hoàn chỉnh. Thêm ảnh 10 bằng lệnh
`scripts/extract_qposd_regions.py --numbers 10` trong cùng môi trường Python.

## Bộ chấm điểm đã kiểm tra

`scripts/qposd_metrics.py` thực hiện ghép một-một, ưu tiên số cặp hợp lệ rồi
tổng IoU. Có hai lần ghép riêng: cùng lớp để tính F1, không xét lớp để ghi
nhầm dầu/tương tự dầu. Hai phép ghép có thể khác nhau, không dùng ma trận
nhầm lẫn có điều kiện để thay cho F1 đầu-cuối. Tỉ lệ nhầm lớp trong ma trận
không xét lớp chỉ tính trong những đối tượng đã ghép được về không gian;
các đối tượng không ghép được được báo cáo riêng.

Pixel nhãn 255 được xóa khỏi hai raster trước khi gán vùng để chấm điểm,
nên có thể làm tách vùng. Đây là quy ước đánh giá, không phải bước suy luận.
Tổng TP/FP/FN được cộng qua các ảnh trước khi tính F1 từng lớp và macro-F1.
Trường hợp mẫu số bằng 0 lưu `null`, không tự biến thành điểm 1.

Đã chạy 7 kiểm tra tính tay: đảo lớp, gộp/tách vùng, đất và pixel bỏ qua,
ưu tiên số cặp ghép, ảnh rỗng, biên IoU 0,5, tỉ lệ nhầm lớp và tổng hợp
toàn tập. Bằng chứng tại `docs/management/qposd_metrics_test_audit.json`.
Đây là kiểm tra bộ chấm, chưa phải số liệu chất lượng mô hình.

Đầu vào là T11 tuyến tính, không chia 255 và không gọi là Sentinel VV.
Lọc Lee 7×7, L=4 chuyển từ cấu hình SOS đã cố định, rồi đổi log và chuẩn hóa
phân vị 1–99% riêng từng ảnh không dùng nhãn. Chưa chứng minh cấu hình này
tối ưu cho QPOSD. Các hằng số, phép chuẩn hóa và giới hạn đều nằm trong giao
thức; không điều chỉnh theo test. Mã tham chiếu Lee ghép các phép toán SciPy
theo cùng công thức, không phải so với một bộ xử lý SAR độc lập như SNAP.

## Điều kiện còn thiếu trước huấn luyện

Tiến trình tải và kiểm tra toàn bộ 24 MAT còn chạy. Trước khi fit cần đủ
kiểm tra toàn mảng, hash/CRC, giá trị hữu hạn và xem các cặp ảnh/nhãn. Nếu
phát hiện lỗi cấu trúc làm thay đổi tập đủ điều kiện, phải dừng và tạo phiên
bản giao thức mới, không âm thầm bỏ mẫu. Kiểm tra trực quan chỉ cho thấy
tương ứng hình ảnh, không chứng minh đường biên chính xác hoặc nguồn nhãn
được xác nhận bằng đo đạc tại hiện trường.
