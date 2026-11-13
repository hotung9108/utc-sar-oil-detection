# Tổng hợp công việc đã thực hiện trong dự án SAR phát hiện dầu tràn

**Ngày tổng hợp:** 13/11/2026.  
**Phạm vi:** các thay đổi, mã nguồn, thực nghiệm và tài liệu đang có trong workspace.  
**Trạng thái:** đã triển khai và chạy thực nghiệm phần xử lý ảnh trên SOS; **chưa hoàn thành toàn bộ Đề 18 và bộ sản phẩm nộp**. Mục tiêu hoàn thiện dự án đang tạm dừng theo yêu cầu người dùng.

Tài liệu này tổng hợp phần công việc có sự hỗ trợ của Codex. Nó không xác nhận rằng từng thành viên đã tự thực hiện, hiểu mã nguồn hoặc hoàn thành phần được phân công. Đóng góp cá nhân cần được thành viên kiểm tra và xác nhận riêng.

## 1. Rà soát yêu cầu và xác định lại mục tiêu

Đã đọc tài liệu hướng dẫn BTL, danh mục đề tài liên quan NASA và mẫu báo cáo người dùng cung cấp. Giữ lựa chọn **Đề 18 — Phát hiện vết dầu tràn trên biển từ ảnh SAR**.

Đã tổ chức lại hướng thực hiện thành:

1. Kiểm tra dữ liệu có nhãn và ý nghĩa nhãn tham chiếu.
2. Cố định train, validation, test và giao thức đánh giá.
3. Chạy so sánh thuật toán, lưu số liệu từng cấu hình và từng ảnh.
4. Lựa chọn cấu hình bằng validation, công bố quy tắc và giới hạn lựa chọn.
5. Tự cài thuật toán bằng NumPy, đối chiếu với bản dùng thư viện.
6. Ghép pipeline, chạy đánh giá cuối và trình bày bằng notebook.

Đã lưu mục tiêu và giao thức tại:

- [Mục tiêu dự án](MUC_TIEU_DU_AN.md).
- [Giao thức thực nghiệm](GIAO_THUC_THUC_NGHIEM.md).
- [Nguồn dữ liệu và bối cảnh NASA](NGUON_DU_LIEU_SAR_DAU_TRAN.md).

Đã tìm hiểu và lưu nguồn về ứng dụng radar của NASA–NOAA trong ứng phó dầu tràn. Tuy nhiên, tài liệu về hoạt động này không đồng nghĩa với đặc tả chính thức của thử thách “NASA #6”. Việc đối chiếu đầy đủ mục tiêu thử thách đó vẫn cần hoàn thiện; không coi SOS là bộ nhãn được NASA xác nhận.

## 2. Kiểm kê và chuẩn bị dữ liệu SOS

Dữ liệu sử dụng là **Refined Deep-SAR Oil Spill — SOS**, đã được người dùng tải vào `data/Refined-Deep-SAR/`.

Đã viết mã kiểm kê ảnh–mask, kiểm tra lỗi đọc/kích thước, cặp thiếu, mask không nhị phân và trùng ảnh theo nội dung pixel. Đã tạo manifest để cố định danh sách ảnh, split và hash.

| Tập dữ liệu | Số cặp ảnh–mask | Cách sử dụng |
|---|---:|---|
| Sentinel train | 2.683 | Huấn luyện classifier và fit chuẩn hóa đặc trưng |
| Sentinel validation | 671 | So sánh thuật toán, chọn tham số |
| Sentinel test | 839 | Đánh giá cấu hình đã khóa |
| PALSAR train | 3.101 | Chưa dùng để huấn luyện |
| PALSAR external test | 776 | Đánh giá chuyển miền |
| **Tổng** | **8.070** | |

Sentinel train/validation của dự án được tách từ tập train của nhà công bố với seed 2026. Tập `val` Sentinel của nhà công bố được dùng làm test của dự án; tên thư mục `val` không có nghĩa ảnh đó vẫn là validation nội bộ.

Đã cố định ngưỡng mask 128 và khảo sát độ nhạy với ngưỡng 64/192. Ảnh PNG được đổi sang số thực bằng chia 255; **đây không phải chuẩn hóa theo góc tới**.

Giới hạn đã xác định:

- Bộ dữ liệu cục bộ không có metadata cần thiết về góc tới, thời gian, tọa độ và mã cảnh.
- Chưa thể ghép gió tái phân tích đúng từng ảnh hoặc xác nhận split độc lập theo cảnh.
- Nhãn hiện dùng là dầu/nền; chưa có nhãn riêng gió yếu, màng sinh học và mưa.
- Không có ảnh SAR sạch tương ứng để dùng PSNR làm bằng chứng chất lượng khử nhiễu.
- Giấy phép sử dụng cần được xác minh đầy đủ trước khi phân phối lại dữ liệu.

Bằng chứng: [manifest](../data/manifest.json), [kiểm kê SOS](management/KIEM_TRA_REFINED_SOS.md), [audit dữ liệu](management/refined_sos_audit.json), [mã kiểm kê](../scripts/audit_refined_sos.py).

## 3. Refactor mã nguồn và tách bản cũ

Đã tổ chức mã mới theo chức năng tại `src/sar_oil/`:

| File | Phần đã triển khai |
|---|---|
| `data.py` | Đọc ảnh–mask, manifest và split |
| `core.py` | Phép toán xử lý ảnh tự cài bằng NumPy |
| `reference.py` | Bản đối chứng bằng SciPy/scikit-image với quy ước tương ứng |
| `models.py` | CART, SVM NumPy và đối chứng scikit-learn; lưu/đọc model |
| `pipeline.py` | Ghép suy luận từ ảnh tới mask và danh sách vùng, không nhận ground truth |
| `evaluation.py` | Ghép đối tượng, tính số đếm và các độ đo |
| `experiments.py` | Sàng lọc cấu hình, benchmark, lựa chọn và đánh giá |
| `provenance.py` | Kiểm tra nguồn, dữ liệu và môi trường trước khi dùng checkpoint |
| `verification.py` | Kiểm tra tính tương đồng của các triển khai |

Đã tách mã/tài liệu cũ vào `legacy/pre_refactor_20261112/`, tránh import vào pipeline mới hoặc dùng số liệu cũ làm kết quả mới. Có script kiểm tra bảo toàn archive; bản cũ không bị coi là đã hoàn thành các yêu cầu của phiên bản mới.

Đã cập nhật README, tài liệu dữ liệu/cấu hình/kết quả, dependency và lockfile. Dữ liệu thô và cache không được đưa vào Git như mã nguồn.

## 4. Các thuật toán đã tự cài và đối chiếu

| Bước | Thuật toán hoặc thao tác |
|---|---|
| Lọc | Mean bằng tổng tích phân; median; Gaussian; biến thể Lee |
| Phân ngưỡng | Otsu với 256 bin cố định; Niblack thích nghi |
| Hình thái | Giãn, co, đóng, mở rồi đóng; loại vùng nhỏ |
| Gán vùng | Liên thông 8 bằng run-length và union-find |
| Đặc trưng | Tỷ lệ diện tích, độ thuôn dài, extent, độ phức tạp biên, mean, std, gradient biên, tương phản nền |
| Phân lớp | CART với Gini; SVM tuyến tính với squared hinge loss |
| Đánh giá | Ghép một–một đối tượng ở IoU ≥ 0,5; Precision, Recall, F1, IoU/Dice pixel, FP/ảnh |

Đã làm rõ quy ước padding, kiểu số thực, tránh tràn uint8, xử lý ảnh hằng, mask rỗng, nền rỗng và mẫu số bằng 0. Đặc trưng được chuẩn hóa bằng thống kê train; không fit lại trên test.

Đã lưu sai số tuyệt đối lớn nhất, MSE và thời gian phép toán trên **8 ảnh validation thật**. Đối chiếu classifier có agreement, objective, trạng thái hội tụ và thời gian fit. Hai finalist CART/SVM có agreement 1,0 trên các ứng viên validation được kiểm tra.

**Giới hạn:** Lee reference được ghép từ thống kê SciPy và cùng công thức, không phải API Lee độc lập. Sai số nhỏ chứng minh sự tương đồng trong các ca đã kiểm tra, không chứng minh thuật toán phát hiện dầu tốt hoặc tương đương trên mọi đầu vào.

Bằng chứng: [kiểm chứng phép toán](../results/sos/verification_real.json), [đối chiếu mô hình](../results/sos/model_comparison.json), [tests](../tests/test_algorithms.py).

## 5. Thực nghiệm so sánh và lựa chọn cấu hình

### 5.1. Thực nghiệm ban đầu

Đã chạy và lưu:

- **110 cấu hình** tạo vùng ứng viên: 11 cấu hình lọc × 10 cấu hình ngưỡng, trên 671 ảnh validation.
- Giữ 3 cấu hình để khảo sát tiếp **729 tổ hợp** hình thái, diện tích tối thiểu, nhóm đặc trưng và classifier.
- Đối chiếu finalist NumPy với thư viện, rồi kiểm tra toàn pipeline NumPy.

Đây là tìm kiếm theo giai đoạn, **không phải thử mọi tổ hợp có thể có**.

Cấu hình đã khóa: **Lee 7×7, L=4 → Otsu → không morphology → diện tích tối thiểu 64 → tám đặc trưng → SVM C=10**.

Quy tắc lựa chọn có F1-band 0,005 rồi ưu tiên Recall. Đây là quy ước thiết kế, không phải định lý hoặc khoảng tương đương thống kê. Nếu chỉ tối đa F1, cấu hình Lee L=1 có F1 validation khoảng 0,34345, cao hơn F1 0,34031 của cấu hình đã chọn. C=10 và C=1 có cùng F1/Recall ở cấu hình được chọn; thời gian một lượt đã phá hòa, chưa đủ chứng minh C=10 tốt hơn C=1.

Bằng chứng: [110 cấu hình](../results/sos/screen.json), [729 tổ hợp](../results/sos/validation.json), [cấu hình đã khóa](../results/sos/selected.json).

### 5.2. Kiểm chứng lý do khảo sát và chọn Lee

Đã viết và chạy [explain_selection.py](../scripts/explain_selection.py) để so sánh **13 cấu hình lọc trên toàn bộ 671 ảnh validation**, giữ Otsu, không morphology và min_area=16. Mean7 và median7 là đối chứng bổ sung sau lựa chọn.

| Bộ lọc | F1 đối tượng của vùng ứng viên |
|---|---:|
| Không lọc | 0,02435 |
| Median 7×7 | 0,07513 |
| Mean 7×7 | 0,08412 |
| Lee 7×7, L=1 | 0,08426 |
| Lee 7×7, L=4 | 0,08552 |

Đã lưu TP/FP/FN từng ảnh, biểu đồ, tổng hợp và bootstrap cặp 2.000 lần. Khoảng bootstrap của chênh lệch Lee7,L4 với mean7 hoặc Lee7,L1 chứa 0: **chưa đủ bằng chứng kết luận Lee vượt hai đối chứng này**. Đây là phân tích thăm dò trên patch, chưa bảo đảm độc lập theo cảnh hoặc hiệu chỉnh nhiều so sánh.

Đã viết [worked_example.py](../scripts/worked_example.py): ví dụ Lee trên ma trận 5×5, tính bằng phân số chính xác, đối chiếu NumPy/SciPy và giải thích dẫn xuất trọng số tuyến tính. Ví dụ tổng hợp này dùng kiểm tra công thức, không thay cho đánh giá trên SOS.

Bằng chứng: [báo cáo lựa chọn Lee](../results/sos/selection_evidence/REPORT.md), [số đếm từng ảnh](../results/sos/selection_evidence/per_image.json), [ví dụ số](../results/sos/worked_example/REPORT.md).

### 5.3. Nhánh ngưỡng thích nghi bổ sung

Đã khảo sát thêm **27 tổ hợp** trên validation để có một nhánh dùng Niblack theo yêu cầu thao tác ngưỡng thích nghi của đề.

Cấu hình chọn: Lee 7×7, L=1; Niblack cửa sổ 51, k=0,2; min_area=64; tám đặc trưng; CART depth=3/min_leaf=5. Pipeline NumPy đạt **Precision 0,102580; Recall 0,245255; F1 0,144656** trên 671 ảnh validation.

Nhánh này là thực nghiệm bổ sung sau lựa chọn, **chưa có test độc lập mới**. Không dùng kết quả test của Otsu để mô tả chất lượng Niblack.

Bằng chứng: [code thực nghiệm bổ sung](../scripts/adaptive_experiment.py), [báo cáo Niblack](../results/sos/adaptive/REPORT.md).

## 6. Kết quả đánh giá đã lưu

Các số dưới đây là micro Precision/Recall/F1 mức đối tượng. IoU là mức pixel; không được dùng thay F1 đối tượng.

| Phương án / tập đánh giá | Số ảnh | Precision | Recall | F1 | IoU pixel |
|---|---:|---:|---:|---:|---:|
| Pipeline đã khóa — Sentinel test | 839 | 0,25415 | 0,31301 | 0,28052 | 0,66139 |
| Baseline — Sentinel test | 839 | 0,00859 | 0,13388 | 0,01614 | 0,43666 |
| Bỏ classifier — Sentinel test | 839 | 0,07533 | 0,31992 | 0,12195 | 0,58672 |
| Pipeline đã khóa — PALSAR external test | 776 | 0,38468 | 0,36079 | 0,37235 | 0,64232 |

Pipeline cuối trên Sentinel test có **TP=996, FP=2.923, FN=2.186**. Kết quả còn nhiều báo sai và bỏ sót; chưa chứng minh khả năng cảnh báo vận hành ngoài khơi Việt Nam.

Đã khảo sát ngưỡng nhị phân hóa mask 64/128/192 trên validation; F1 tương ứng khoảng 0,34533 / 0,34031 / 0,33706.

Đã bổ sung thống kê từng ảnh, trung bình, độ lệch chuẩn, min/max và số trường hợp không xác định. Đã phân tích ba ca thất bại `sentinel_440`, `sentinel_25`, `sentinel_591`, có ảnh đầu vào, ứng viên, kết quả cuối, GT và bản đồ lỗi. Phân tích tách lỗi tạo ứng viên khỏi lỗi loại vùng của classifier.

Bằng chứng: [kết quả đánh giá](../results/sos/evaluation.json), [báo cáo tổng hợp](../results/sos/REPORT.md), [phân tích thất bại](../results/sos/diagnostics/REPORT.md).

## 7. Notebook, CLI và tái tạo thực nghiệm

Đã tạo và chạy 5 notebook:

| Notebook | Nội dung |
|---|---|
| `01_data_and_ground_truth.ipynb` | Dữ liệu, nhãn, split và giới hạn |
| `02_filter_threshold_benchmark.ipynb` | So sánh lọc/ngưỡng và bằng chứng chọn Lee |
| `03_regions_and_features.ipynb` | Vùng, hình thái và đặc trưng |
| `04_cart_svm_numpy.ipynb` | CART/SVM tự cài và đối chứng |
| `05_final_pipeline.ipynb` | Pipeline cuối, đánh giá và ca thất bại |

Theo audit đã lưu, cả 5 notebook đã thực thi, không có cell lỗi, có hình minh họa; số liệu tổng hợp khớp số đếm từng ảnh và pipeline NumPy khớp validation đã chọn.

Đã có CLI `scripts/sos.py` với các bước `prepare`, `verify`, `screen`, `benchmark`, `select`, `evaluate`, `predict`, `reproduce`. Suy luận xuất `mask.png`, `overlay.png`, `regions.json`. Điểm classifier là decision score, không được gọi là xác suất dầu.

```powershell
# Chạy chuỗi thực nghiệm SOS đã triển khai và notebook; có dùng checkpoint hợp lệ
.venv/Scripts/python.exe run_experiments.py --workers 6

# Chỉ kiểm tra kết quả đã lưu và tests, không chạy lại toàn bộ benchmark
.venv/Scripts/python.exe run_experiments.py --verify-only

# Suy luận một ảnh
.venv/Scripts/python.exe scripts/sos.py predict --image <duong-dan-anh.png>
```

Nhật ký lần chạy chuỗi 10 bước ghi `passed=true`; lần kiểm tra gần nhất cũng đạt. Bộ kiểm tra có 6 tests. Đây là bằng chứng trong phạm vi các kiểm tra đã cài, không phải xác nhận toàn bộ yêu cầu đề tài đã hoàn thành.

Bằng chứng: [runner](../run_experiments.py), [nhật ký tái tạo](../results/sos/runner_reproduce.json), [nhật ký kiểm tra](../results/sos/runner_verify.json), [audit notebook](management/notebook_execution_audit.json).

## 8. Phân công lại cho 5 thành viên

| Thành viên | Trách nhiệm theo kế hoạch mới |
|---|---|
| TV1 — Tiến Sơn Trần | Pipeline, CLI, tích hợp và kết quả cuối |
| TV2 — Lương Tiến Dũng | CART/SVM NumPy và đối chứng sklearn |
| TV3 — Hồ Việt Tùng | Lọc và phân ngưỡng, phân tích lựa chọn Lee |
| TV4 — Nguyễn Hải Hiếu | Liên thông, hình thái và đặc trưng vùng |
| TV5 — Phạm Minh Tuấn | Dữ liệu, ground truth và đánh giá đối tượng |

Đã cập nhật kế hoạch theo notebook, danh sách nhiệm vụ S01–S03, người review và điều kiện nghiệm thu, cùng workbook phân công. Các ô giờ thực tế, minh chứng và đánh giá cá nhân cần được điền theo công việc thật; không tự gán phần do AI hỗ trợ thành đóng góp đã xác nhận của sinh viên.

Bằng chứng: [kế hoạch mới](management/KE_HOACH_SOS_NOTEBOOK.md), [nhiệm vụ máy đọc](management/sos_tasks.json), [workbook phân công](management/KE_HOACH_PHAN_CONG_1008_1111_2026.xlsx).

## 9. Báo cáo Word/PDF đang dựng

Đã thực hiện:

- Đọc và render toàn bộ mẫu báo cáo; ghi quy tắc định dạng và kiểm tra hash file gốc.
- Viết nguồn nội dung, 10 tài liệu tham khảo, hình dữ liệu, sơ đồ pipeline và biểu đồ tham số.
- Viết script dựng báo cáo từ mẫu; bảng thực nghiệm đọc trực tiếp từ JSON.
- Bổ sung công thức chỉnh sửa được trong Word, dẫn xuất Lee, ví dụ ma trận 5×5, mã giả, định nghĩa tám đặc trưng và cấu trúc module.
- Bổ sung bảng sai số/MSE, đối chiếu classifier, thống kê từng ảnh, ca thất bại và thông tin CPU/RAM/môi trường ghi nhận thực tế.
- Cập nhật trường mục lục bằng Word trên bản sao; nhập kết quả cập nhật cùng bookmark và style danh mục còn thiếu, giữ nguyên các style gốc.
- Render nhiều vòng và sửa lỗi cột bìa, danh mục hình/bảng, thứ tự bảng và vị trí số công thức.
- Viết kiểm tra tự động đối chiếu mục lục với nội dung PDF và bảo vệ bằng hash.

**Bản render mới nhất đã kiểm tra tự động:** 35 trang tổng cộng, 24 trang nội dung chính. Mọi mục lục được kiểm tra đều tìm thấy nội dung ở đúng trang. Độ dài này đạt mẫu mới 20–35 trang nhưng chưa đạt ngưỡng 25–40 trang của hướng dẫn gốc. Chưa hoàn tất kiểm tra trực quan mọi trang; **không coi đây là bản nộp cuối**.

File làm việc hiện nằm trong `.cache/report/`; bản render mới nhất ở `render-fields-v5/`. Cache không thay cho thư mục bàn giao cuối và có thể không đi cùng repository khi clone.

Bằng chứng: [hướng dẫn dựng báo cáo](report/README.md), [code dựng](../scripts/build_report.py), [code cập nhật Word](../scripts/update_report_fields.ps1), [code nhập trường](../scripts/import_report_fields.py), [audit render mới nhất](report/render_audit.json).

Lưu ý khi đọc các audit: `completion_audit.json` và `render_progress.json` còn một số thông tin số trang của vòng dựng cũ. Với trạng thái bản render mới nhất, ưu tiên `report/render_audit.json` và hash của file thực tế.

## 10. Những phần chưa hoàn thành

| Phần còn lại | Tình trạng |
|---|---|
| Chuẩn hóa theo góc tới | Thiếu dữ liệu/metadata phù hợp; chưa triển khai và kiểm chứng nhánh vật lý |
| Gió tái phân tích | Chưa ghép đúng thời gian/vị trí ảnh |
| Dầu so với từng loại look-alike | Chưa có nhãn phân biệt gió yếu, màng sinh học, mưa và ma trận nhầm lẫn tương ứng |
| Test độc lập cho nhánh thích nghi | Chưa có; hiện chỉ công bố validation bổ sung |
| Đối chiếu đầy đủ mục tiêu NASA #6 | Cần hoàn thiện bằng nguồn chính thức của thử thách |
| GUI demo theo hướng dẫn môn học | Đã có notebook/CLI; chưa hoàn thiện ứng dụng GUI riêng |
| Báo cáo DOCX/PDF cuối | Còn kiểm tra mọi trang, hoàn thiện độ dài/cấu trúc theo yêu cầu và metadata bìa |
| Slides 15–20 trang | Chưa hoàn thiện bộ mới |
| Video demo 5–7 phút | Chưa hoàn thiện |
| Đóng góp và hồ sơ nhóm | Cần mã sinh viên, chữ ký, điểm đánh giá chéo và biên bản họp thật |
| Mô phỏng trôi dầu và AIS | Chưa thực hiện; là hướng phát triển, không phải kết quả đã có |
| Gói bàn giao và tái tạo toàn bộ tài liệu | Chưa đóng gói hoàn chỉnh; runner thực nghiệm chưa bao gồm toàn bộ quy trình Word/slides/video |

## 11. Trạng thái Git và phạm vi xác nhận

Tại thời điểm tổng hợp, `git status` còn nhiều file sửa và file mới chưa được theo dõi. **Đợt thay đổi hiện tại chưa được commit/push trong phần công việc này.** Không suy ra các thay đổi trong workspace đã có trên GitHub.

Tài liệu này được tạo bằng cách đối chiếu mã nguồn, các JSON kết quả, nhật ký chạy và audit đang có. Khi tạo tài liệu tổng hợp không chạy lại toàn bộ grid 110/729 cấu hình; các kết quả được lấy từ bằng chứng đã lưu và kiểm tra lại số lượng/số liệu. Mục tiêu tổng thể vẫn tạm dừng; việc tạo file tổng hợp không tự động tiếp tục các phần đang dang dở.
