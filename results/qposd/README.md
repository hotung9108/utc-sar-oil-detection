# Thử nghiệm bổ sung QPOSD

SOS vẫn là tập chính. QPOSD cung cấp nhãn dầu/tương tự dầu chung trên UAVSAR
L-band, không có nhãn nguyên nhân gió yếu, màng sinh học và mưa. Đã sửa
cách chia theo nhóm ảnh trùng trước khi fit, lưu giao thức v2 và chạy đủ
10 cấu hình phân lớp. CART độ sâu 5, min_leaf=1 đạt macro-F1 validation
cao nhất 0,6238049911 khi được cung cấp vùng tham chiếu. Đã chạy đủ 10 cấu
hình tìm vùng × 5 ảnh validation. Cấu hình thắng là không lọc trước tìm vùng,
Otsu, diện tích tối thiểu 64, không hình thái: macro-F1 đối tượng 0,0563380.
Ảnh dùng trích đặc trưng vẫn được lọc Lee 7×7, L=4 theo giao thức cố định.
Lựa chọn đã lưu trong `detection_selection.json` và commit trước khi chạy test.
Đánh giá đủ năm ảnh test đã hoàn tất: macro-F1 phát hiện 0,0637297, F1 dầu
0,1132075 và F1 tương tự dầu 0,0142518. NumPy/thư viện có mask bằng nhau
từng pixel trên cả năm ảnh. Phân lớp có sẵn vùng đạt macro-F1 0,5214139;
không dùng số này thay F1 phát hiện. Chi tiết, confusion và số đếm tại
[`REPORT.md`](REPORT.md), được tạo bằng `scripts/report_qposd.py` sau kiểm tra hash.

V1 bị từ chối trước fit vì ảnh 21 (test) trùng 7.601 pixel với ảnh 22
(train). Toàn bộ giao thức và đặc trưng v1 được giữ tại `archive/protocol_v1/`.

## Giao thức trước huấn luyện

`protocol.json` được tạo bởi `scripts/prepare_qposd_protocol.py`, không đọc
bất kỳ dự đoán nào. Lệnh từ chối ghi đè nếu giao thức thay đổi.

| Tập | ID ảnh nguồn |
|---|---|
| Train | 4, 8, 10, 19, 20, 21, 22, 26, 28, 33, 34, 35, 36, 41 |
| Validation | 13, 15, 16, 32, 39 |
| Test | 14, 17, 18, 24, 25 |

Chia theo ảnh trước khi lấy vùng, seed 2026, phân tầng theo lớp chiếm nhiều
pixel hơn trong mỗi ảnh. Có 16 ảnh chủ yếu dầu và 8 ảnh chủ yếu tương tự dầu;
train lấy 10+4, validation 3+2, test 3+2. Ba pixel dầu trong ảnh 32 vẫn giữ
nhãn dầu. Tỉ lệ này là lựa chọn thiết kế cho tập nhỏ, không phải tỉ lệ tối
ưu được chứng minh bằng định lý. Chưa có ID cảnh để chứng minh độc lập cảnh.

V2 xét đủ 5.880 cách gán các nhóm ảnh dầu giữ nguyên quy mô/phân tầng,
chọn cách đổi ít ảnh nhất rồi phá hòa bằng SHA-256 gắn seed 2026. Chỉ ảnh
21 chuyển sang train và 17 chuyển sang test. Không dùng điểm mô hình để
sửa tập. Ảnh 17 từng được trích đặc trưng dưới v1, nhưng chưa có mô hình
hay điểm dự đoán; không gọi test mới là tập chưa từng xem.

Đã kiểm tra trùng lặp chính xác trên 7 ảnh tải trước (4, 8, 10, 13, 14, 35,
41), gồm 21 cặp: lấy ô T11 5×5, bước 64 pixel, tìm giá trị ô giống hệt trong
ảnh thứ hai. Không tìm thấy ô khớp ở lần chạy này. Mã tại
`scripts/audit_qposd_overlap.py`, kết quả thực tại
`docs/management/qposd_overlap_first7.json`. Mã đã qua kiểm tra tìm đúng độ
dịch và toàn bộ vùng giao khi cắt một ảnh giả lập, đồng thời không coi ảnh
hằng là bằng chứng trùng lặp. Đây là kiểm tra lấy mẫu, không phát hiện chắc
chắn ảnh cùng cảnh đã đổi thang, xoay hoặc lấy mẫu lại; không được dùng kết
quả âm tính để khẳng định độc lập cảnh. Lượt mở rộng đủ 24 ảnh đã hoàn tất,
phát hiện bốn cặp giao trùng; chi tiết ở cuối tài liệu.

Sau đó, khi ảnh 22 tải xong, kiểm tra cặp 22/35 phát hiện vùng giao
**771×581 = 447.951 pixel T11 giống hệt nhau**, độ dịch ảnh đích so với ảnh
nguồn là (-160, -450), có 108 ô lấy mẫu khớp. Bằng chứng tại
`docs/management/qposd_overlap_22_35.json`. Hai ảnh hiện cùng train, nên cặp
này không gây rò rỉ giữa các tập nhưng chứng minh tên tệp khác nhau không
đảm bảo nội dung độc lập. Bước trước huấn luyện hiện yêu cầu kiểm tra đủ
276 cặp của 24 ảnh và từ chối chạy nếu vùng giao giống hệt nằm khác tập.
Nếu phát hiện trường hợp đó, phải lập lại nhóm trước fit và lưu thay đổi
giao thức; không che giấu bằng cách tiếp tục chấm test theo cách chia cũ.

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

V2 đã trích lại 729 vùng của đủ 19 ảnh train/validation: 527 vùng train
(325 dầu, 202 tương tự dầu), 202 vùng validation (24 dầu, 178 tương tự dầu).
Đặc trưng của 18 ảnh giữ nguyên vai trò khớp hoàn toàn giữa hai lần trích;
đã lưu kiểm chứng tại `docs/management/qposd_protocol_v2_audit.json`.
Sai số lớn nhất trên tất cả đặc trưng:
`6.516835210357286e-9`; trên ảnh chuẩn hóa:
`1.8385559610381574e-6`. Số liệu chỉ thuộc 19 ảnh đã trích đặc trưng này. Thời gian trong JSON
là một lần chạy và nhánh NumPy gồm cả gán nhãn; không phải phép so tốc độ
công bằng của hai pipeline hoàn chỉnh. Thêm ảnh 10 bằng lệnh
`scripts/extract_qposd_regions.py --numbers` kèm ID ảnh chưa xử lý trong cùng
môi trường Python. Chưa chấm mô hình trên test; phần đặc trưng ảnh 17 đã
trích dưới v1 được lưu trong lịch sử, không dùng để fit v2.

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

`scripts/qposd_pipeline.py` là hàm suy luận chỉ nhận T11, cấu hình và mô hình;
không nhận mask thật. `scripts/select_qposd_detection.py` dùng hàm này cho
10 cấu hình trên 5 ảnh validation, sau khi mô hình phân lớp đã được cố định.
Nó lưu vùng, đặc trưng, score, điểm đối tượng, số pixel bất đồng NumPy/thư
viện và chọn theo macro-F1 từ tổng số đếm. Nhánh thư viện dùng cùng mô hình
NumPy đã cố định để tách riêng khác biệt của các phép xử lý ảnh.

Ba kiểm tra suy luận với ảnh giả lập và bộ phân lớp giả lập xác định đã qua;
không suy ra độ chính xác thực tế từ các kiểm tra này. Lần chạy lệnh chọn
cấu hình ban đầu dừng trước chấm validation do thiếu hồ sơ 24 MAT. Sau khi
đủ dữ liệu và sửa nhóm trùng, lượt so sánh 10 cấu hình validation đang chạy.

Sau khi đã lưu đủ hai lựa chọn, chấm test bằng:

```powershell
.\.venv\Scripts\python.exe scripts/evaluate_qposd_test.py --preflight-only
.\.venv\Scripts\python.exe scripts/evaluate_qposd_test.py
```

Lệnh kiểm tra không trích đặc trưng test hoặc chấm điểm. Lệnh chạy thật sẽ
lưu `evaluation.json`, mask lớp 0/1/2 cho NumPy và thư viện, kết quả từng ảnh
và đặc trưng vùng tham chiếu trong `test/`. Mask PNG được đọc lại để xác
minh không đổi pixel. Kết quả phân lớp có sẵn vùng và kết quả phát hiện
đầu-cuối được lưu riêng. Nếu đã có thư mục `test/` hoặc kết quả tổng hợp,
lệnh từ chối ghi đè; nếu lần chạy bị gián đoạn phải kiểm tra bằng chứng dở
dang trước khi quyết định cách phục hồi, không âm thầm chạy lại.

Đã kiểm tra bằng dữ liệu giả lập rằng bước kiểm tra test từ chối phương án
thắng không đúng quy tắc validation, điểm tổng hợp bị sửa và tập validation
thiếu ảnh. Lần kiểm tra ban đầu dừng trước test vì chưa đủ hồ sơ MAT.
Hiện test vẫn chưa chạy vì lựa chọn cấu hình tìm vùng chưa hoàn tất;
**chưa tạo `evaluation.json` hay thư mục `test/`**.

Notebook kết quả được tạo sau khi test hoàn tất:

```powershell
.\.venv\Scripts\python.exe scripts/build_qposd_evaluation_notebook.py
.\.venv\Scripts\python.exe scripts/run_notebooks.py --notebook notebooks/external/10_qposd_classification_detection.ipynb
```

Mã dựng gồm 5 ô code: kiểm tra nguồn, so sánh bộ phân lớp, so sánh cấu hình
tạo vùng, chạy lại và xem cả 5 ảnh test, tổng hợp điểm/nhầm lẫn. Đã kiểm tra
định dạng notebook và biên dịch cú pháp các ô trong thư mục tạm; chưa chạy
trên dữ liệu thật. Mã từ chối tạo notebook trong dự án nếu chưa có test đầy
đủ, và không ghi đè notebook đã có. Sau khi thực thi phải xem các hình trước
khi đưa vào báo cáo. Lệnh tái tạo 9 notebook hiện tại chưa bao gồm notebook
mới này; chỉ cập nhật lệnh đó khi notebook 10 đã thực thi và được kiểm tra.

Mã `scripts/train_qposd_classifiers.py` đã có hai chế độ:

```powershell
.\.venv\Scripts\python.exe scripts/train_qposd_classifiers.py --preflight-only
.\.venv\Scripts\python.exe scripts/train_qposd_classifiers.py
```

Chế độ kiểm tra xác minh đủ 24 MAT và hồ sơ xem ảnh, SHA-256 ảnh/mask,
đúng giao thức và đủ đặc trưng train/validation. Chế độ huấn luyện còn lưu
điểm của từng vùng validation cho cả NumPy và thư viện, cảnh báo hội tụ,
ma trận nhầm lẫn, mô hình JSON và kiểm tra điểm không đổi sau lưu/đọc lại.
Chỉ cấu hình NumPy hội tụ mới đủ điều kiện lựa chọn; không có cấu hình đủ
điều kiện thì dừng. Không ghi đè thư mục mô hình/kết quả đã có.

Kiểm tra tích hợp với dữ liệu giả lập đã qua: hai loại mô hình dùng cùng
train, không lấy thống kê chuẩn hóa từ validation, dự đoán NumPy/thư viện
khớp trong trường hợp kiểm tra và hòa điểm chọn đúng thứ tự. Đây không phải
thí nghiệm độ chính xác QPOSD. Với v2, kiểm tra trước fit đã qua và cả 10
cấu hình đã chạy/hội tụ. `classifier_selection.json` lưu mọi score validation,
ma trận nhầm lẫn và hash mô hình. Cấu hình thắng NumPy và thư viện có score
giống nhau trên validation: dầu P=0,285714, R=0,583333, F1=0,383562;
tương tự dầu F1=0,864048. Đây là phân lớp có sẵn vùng, không phải phát hiện.

Đã tải đủ 24 MAT, kiểm tra CRC/hash, giá trị hữu hạn, khớp kích thước và
xem toàn bộ 24 cặp ảnh/nhãn. `qposd_matched_full_audit.json` lưu bằng chứng.
Kiểm tra đủ 276 cặp (`qposd_overlap_all24.json`) tìm thấy bốn cặp có toàn
bộ vùng giao trùng chính xác: 19/20 (76.351 pixel), 21/22 (7.601 pixel),
22/33 (33.711 pixel), 22/35 (447.951 pixel). Các nhóm liên thông là
{19,20} và {21,22,33,35}; những ảnh còn lại chưa phát hiện giao trùng theo
phép kiểm tra này. Cặp 21/22 vượt ranh giới train/test của v1, nên lệnh
kiểm tra trước huấn luyện đã thực sự dừng với lỗi này. Không có mô hình
hoặc điểm test nào được tạo từ cách chia bị lỗi.

Đã tạo giao thức v2 trước khi fit, không âm thầm bỏ mẫu hoặc
báo cáo kết quả từ cách chia cũ. Kiểm tra trực quan chỉ cho thấy
tương ứng hình ảnh, không chứng minh đường biên chính xác hoặc nguồn nhãn
được xác nhận bằng đo đạc tại hiện trường.
