# Đánh giá dự án và đối chiếu Đề 18

**Ngày kiểm tra:** 17/11/2026. **Kết luận: chưa đủ căn cứ xác nhận đáp ứng 100% Đề 18.**

Phần mềm và các thực nghiệm đã hoàn thành trong phạm vi dữ liệu hiện có. Điều đó không đồng nghĩa đã kiểm chứng đầy đủ bài toán phát hiện dầu ngoài khơi miền Trung. Không tự quy đổi thành 75%, 90% hay điểm môn học khi chưa có rubric của giảng viên.

## 1. Căn cứ đối chiếu

Đã đọc trực tiếp Đề 18 trong DOCX gốc của môn học. [Bản trích nguyên văn và SHA-256](management/de18_original_requirements.json) chứa đúng chín đoạn của đề, gồm dữ liệu, ba chức năng bắt buộc, hướng phát triển và đánh giá. Các yêu cầu bổ sung của nhóm là NumPy tự cài, so sánh thư viện, số liệu thật, notebook và Streamlit.

Thông báo trước đây về “hoàn thiện dự án” chỉ xác nhận luồng triển khai/kiểm thử của phiên bản hiện có. Tài liệu này đính chính: **không phải xác nhận đạt toàn bộ yêu cầu đề hoặc đủ tin cậy để cảnh báo thực địa**.

## 2. Ma trận yêu cầu và bằng chứng

| Yêu cầu | Trạng thái có thể khẳng định | Bằng chứng | Phần chưa đủ |
|---|---|---|---|
| Sentinel-1 ngoài khơi và dữ liệu SAR công khai có nhãn | Có dữ liệu và thực nghiệm | [Manifest SOS](../data/manifest.json); [manifest Cantarell](management/cantarell_eligible_manifest.json) gồm 154 mẫu hợp lệ, 94/35/25 theo train/val/test | SOS thiếu metadata cảnh; không chứng minh split SOS độc lập theo cảnh. Cantarell gộp dầu tràn và dầu thấm tự nhiên |
| Gió bề mặt tái phân tích | Có ghép gió ERA5 theo không gian/thời gian ở nhánh vật lý | [Audit gió](management/cantarell_wind_audit.json), 172/173 tile ban đầu; các mẫu hợp lệ vượt chốt độ phủ gió | Gió chỉ là bối cảnh; chưa đo đóng góp của gió trong classifier. Đề không nói rõ bắt buộc đưa gió vào classifier, nên không tự coi việc này là vi phạm |
| **1. Lọc speckle + góc tới + ngưỡng thích nghi** | Đã triển khai và chạy cùng một pipeline Cantarell | [Lựa chọn có lọc](../results/cantarell/requirements_selection.json): gamma0 từ dữ liệu vật lý → Lee 7×7 L4 → Niblack 31 k0,5 → SVM; [pipeline](../scripts/cantarell/cantarell_pipeline.py), [notebook 12](../notebooks/external/12_cantarell_models_and_angle.ipynb) | Trình tự vật lý thực tế là hiệu chuẩn/gamma0 trước lọc trên công suất tuyến tính, rồi log/percentile và ngưỡng. Gamma0 là hiệu chỉnh diện tích hình học, chưa loại mọi phụ thuộc góc tới; chưa xử lý thermal noise. Chưa chứng minh tăng F1 |
| **2. Bốn nhóm đặc trưng bắt buộc** | Đã triển khai và đối chứng | [core.py](../src/sar_oil/core.py), tám đặc trưng gồm elongation, complexity, boundary gradient và local background contrast; [đối chứng Cantarell](../results/cantarell/feature_verification.json) | Kết luận đúng trong quy ước chu vi, vành nền, độ phân giải và các ca kiểm tra; không gọi là đúng tuyệt đối với mọi ảnh |
| **3. Phân lớp dầu/tương tự dầu bằng SVM hoặc cây** | Có minh chứng nhị phân trên QPOSD | [QPOSD evaluation](../results/qposd/evaluation.json), [pipeline](../scripts/qposd/qposd_pipeline.py), [notebook 10](../notebooks/external/10_qposd_classification_detection.ipynb) | QPOSD là UAVSAR, không phải Sentinel-1; nhãn look-alike chung. SOS/Cantarell dầu/nền không chứng minh rằng nền là look-alike có nhãn |
| Các hiện tượng gió yếu, màng sinh học, mưa | Chưa có bằng chứng bao phủ từng nguyên nhân | QPOSD chỉ có lớp look-alike chung | Ngoặc trong đề nêu ví dụ của look-alike, **không mặc nhiên bắt buộc classifier nhiều lớp**. Tuy nhiên chưa có hồ sơ nhãn để chứng minh tập kiểm tra đại diện đủ các hiện tượng này |
| Precision/Recall/F1 mức đối tượng trên test | Đã có, tái tính được | [SOS](../results/sos/evaluation.json), [Cantarell](../results/cantarell/evaluation.json), [xác minh 175 mask](management/cantarell_results_verification.json) | Điểm thấp; không suy thành hệ thống cảnh báo hiệu quả. Đề không nêu F1 tối thiểu nên không tự kết luận trượt chỉ vì F1 thấp |
| Tỷ lệ nhầm dầu/look-alike | Có trên QPOSD | Confusion và lớp bỏ sót/báo thừa trong [evaluation QPOSD](../results/qposd/evaluation.json) | Phân lớp khi có sẵn vùng và phát hiện end-to-end là hai bài toán khác nhau. Chưa có cùng phép đánh giá look-alike cho nhánh Sentinel-1 vật lý |
| Bối cảnh miền Trung, phát hiện sớm ngoài khơi | Mới là bối cảnh ứng dụng | Các dữ liệu hiện tại là benchmark và nhánh ngoài Việt Nam | Chưa có tập miền Trung với nhãn độc lập, đánh giá chuyển miền, độ trễ hay vận hành chuỗi ảnh theo thời gian |
| Mô phỏng trôi dầu và AIS | Hướng phát triển, không thuộc ba chức năng bắt buộc | Có mã **minh họa** trôi dầu trong [study_guide](../study_guide/tu_code_du_an/07_mo_phong_troi_dat_dau/drift_simulation.py) | Chưa tích hợp/kiểm chứng quỹ đạo hoặc bãi biển bị ảnh hưởng; chưa có AIS. Không cộng điểm hoàn thiện chỉ vì có file demo |

Không lấy việc “có góc tới ở Cantarell” cộng với “có look-alike ở QPOSD” để tuyên bố một pipeline Sentinel-1 đã thực hiện và kiểm chứng tất cả. Nếu môn học chấp nhận các nhánh minh họa riêng, bằng chứng kỹ thuật hiện có bao phủ phần lớn thao tác yêu cầu; việc chấp nhận đó thuộc tiêu chí chấm thực tế, không phải kết luận tự cấp của dự án.

## 3. Số liệu thật cần công bố

| Thí nghiệm | Dữ liệu test | Kết quả |
|---|---|---|
| SOS pipeline đã chọn | 839 ảnh Sentinel | Precision 0,25415; Recall 0,31301; F1 0,28052 |
| Cantarell winner gamma0 ban đầu, không lọc | 25 tile / 5 cảnh | Precision 0,14925; Recall 0,03670; F1 0,05891 |
| Cantarell nhánh có đủ Lee + gamma0 + Niblack + SVM | Cùng 25 tile | Precision 0,07487; Recall 0,02569; F1 0,03825 |
| QPOSD phân lớp khi đã có vùng tham chiếu | 5 ảnh | Macro-F1 0,52141 |
| QPOSD phát hiện tự động | Cùng 5 ảnh | Macro-F1 0,06373 |

- Cantarell: đã chạy 50 so sánh ứng viên và 84 cặp classifier NumPy/thư viện. Agreement nhỏ nhất trong 84 cặp khoảng **0,998715**, không phải mọi mô hình đều khớp 100%.
- Nhánh bắt buộc có lọc là bổ sung sau khi đã xem một phần validation, trước mọi điểm test; có [giao thức bổ sung](management/cantarell_required_filter_protocol_v1.json). Giữ nguyên winner ban đầu và công khai chênh lệch F1 validation −0,045855.
- Bootstrap theo cảnh: CI 95% chênh lệch F1 gamma0−sigma0 là [0; 0] ở detector ban đầu; khoảng [−0,00012903; 0,00029304] ở detector có lọc. **Chưa chứng minh tăng F1**. [Bằng chứng gốc](../results/cantarell/angle_bootstrap_filtered.json).
- 358/545 GT nhỏ hơn 32 pixel. Với dự đoán có diện tích tối thiểu 64 pixel, IoU tối đa của GT dưới 32 pixel nhỏ hơn 0,5. Không bỏ các GT này khi chấm điểm. [Phân tích kích thước](../results/cantarell/size_diagnostics.json).
- Min-area 64 được khóa trong thiết kế thí nghiệm; chưa chứng minh tối ưu cho Cantarell. Giữ biên của Lee là cơ chế có điều kiện, không phải định lý “giữ biên 100%” hay “Lee luôn tốt nhất”.

## 4. Yêu cầu bổ sung của nhóm

| Nội dung | Kết quả kiểm tra |
|---|---|
| NumPy tự cài và đối chứng thư viện | Có code, sai số, agreement và bảng mô hình. Reference Lee ghép công thức từ toán tử SciPy, không phải thư viện Lee độc lập |
| Chọn theo thực nghiệm trước test | Có giao thức, manifest và commit lựa chọn trước test; công bố rõ bổ sung muộn ở giai đoạn validation |
| Notebook trực quan | 12 notebook đã chạy, 31 hình; [audit triển khai](management/project_streamlit_acceptance.json) |
| Streamlit | Có SOS tải ảnh, QPOSD mẫu, Cantarell mẫu; xuất mask/overlay/đặc trưng; đánh giá GT sau suy luận |
| Kiểm thử | 62 kiểm thử đạt ở đợt nghiệm thu phần mềm; kiểm tra mới trong lần đối chiếu này chỉ xác minh tài liệu/nguồn và bảng số liệu, không gọi là huấn luyện lại |
| Kiểm tra trình duyệt | Bổ sung cùng ngày sau cải tiến UX: 13 kiểm thử web đạt; Edge headless chạy mẫu thật SOS/QPOSD/Cantarell, mở đối chiếu/bằng chứng/trợ giúp; đã xem ảnh chụp desktop và trang đầu rộng 390 px. Xem [cách tái kiểm tra](STREAMLIT.md). Chưa kiểm tra mọi thiết bị hoặc usability với người dùng thực tế |
| NASA #6 | Là mã tham chiếu trong đề môn học. [Khảo sát nguồn NASA](NGUON_DU_LIEU_SAR_DAU_TRAN.md) không đồng nghĩa dự án được NASA chứng nhận hoặc đáp ứng một chuẩn NASA riêng |

## 5. Phần cần làm để có cơ sở tuyên bố đầy đủ hơn

1. Bổ sung dữ liệu/nhãn dầu và look-alike phù hợp Sentinel-1 có metadata, hoặc chứng minh chuyển miền từ QPOSD bằng tập kiểm tra độc lập; kiểm tra toàn bộ chuỗi từ dữ liệu vật lý đến phân lớp dầu/look-alike.
2. Kiểm tra tài liệu nguồn nhãn để xác định các nguyên nhân look-alike được đại diện. Không tự suy nhãn nguyên nhân từ ảnh tối hoặc tốc độ gió.
3. Nếu tuyên bố ứng dụng miền Trung: cần case study có ảnh thực và nhãn độc lập theo sự kiện, cộng phép đo thời gian xử lý/khả năng phát hiện sớm. Ảnh Việt Nam không nhãn chỉ cho minh họa, không cho P/R/F1.
4. Nếu tiếp tục tối ưu diện tích ứng viên hay đặc trưng: dùng train/validation và giao thức phiên bản mới. Test hiện tại đã được xem; muốn tuyên bố cải tiến độc lập cần holdout mới hoặc thiết kế đánh giá phù hợp, không tiếp tục tune theo test cũ.
5. Kiểm tra giao diện cơ bản đã được bổ sung ở lần cải tiến UX cùng ngày: Edge chạy ba nhánh, AppTest kiểm tra upload và dữ liệu lỗi. Muốn tuyên bố trải nghiệm đã được người dùng xác nhận, cần thêm thử nghiệm sử dụng với người dùng thực tế; không suy điều đó từ kiểm thử tự động.

AIS/trôi dầu có thể phát triển sau; không phải lý do đánh trượt ba chức năng bắt buộc. Không có căn cứ để tự chấm điểm tối đa hoặc tự gắn phần trăm đạt đề.
