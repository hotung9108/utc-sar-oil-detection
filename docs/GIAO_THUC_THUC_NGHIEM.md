# Giao thức SOS — chốt trước khi mở test

## Dữ liệu và phạm vi

Nguồn: Refined Deep-SAR Oil Spill v1, https://zenodo.org/records/15298010. Dùng mask semantic làm nhãn tham chiếu; không gọi đó là xác nhận dầu tại hiện trường. Bộ tải về không có metadata cảnh, tọa độ, thời gian, góc tới, gió hoặc các lớp look-alike. PALSAR và Sentinel được tách riêng, không trộn khi huấn luyện.

Sentinel publisher train gồm 3354 ảnh: chia 2683 train và 671 validation nội bộ, seed 2026, phân tầng mask rỗng/không rỗng. 839 ảnh publisher val là test cuối. PALSAR publisher val (776 ảnh) là đánh giá ngoài miền, không huấn luyện hoặc chọn tham số trên PALSAR. 3101 PALSAR train được lưu manifest nhưng không sử dụng cho kết quả chính. Chia ở cấp patch: thiếu scene ID nên không thể chứng minh độc lập theo cảnh, dù kiểm kê không thấy ảnh trùng pixel chính xác.

PNG được đổi grayscale và chia 255, không resize. Mask >=128; nhãn trung gian được lưu nguyên trên đĩa. Khảo sát ngưỡng mask 64/192 trên validation với cấu hình đóng băng; không chọn ngưỡng GT theo điểm số tốt nhất. GT không lọc đối tượng nhỏ. Hash ảnh/mask và split nằm trong `data/manifest.json`.

## Không gian thuật toán

| Bước | Các cấu hình khảo sát | Tự cài / đối chứng |
|---|---|---|
| Lọc | none; median 3/5; Gaussian sigma 0.8/1.2, kernel 5; Lee cửa sổ 3/5/7, looks 1/4 | NumPy / SciPy ndimage; Lee đối chứng ghép công thức |
| Ngưỡng | Otsu 256 bins [0,1]; Niblack cửa sổ 15/31/51, k 0.2/0.5/0.8 | NumPy / scikit-image |
| Hình thái | none, closing, opening+closing; đĩa r=1; diện tích tối thiểu 4/16/64 | NumPy / SciPy |
| Liên thông | 8-neighbor | NumPy run-length union-find / SciPy label |
| Đặc trưng | shape (4), intensity (4), all (8) | NumPy / regionprops và ndimage |
| CART | max_depth 3/5/8; min_leaf 5/20 | NumPy Gini / sklearn DecisionTreeClassifier |
| SVM tuyến tính | squared hinge, L2, C=0.1/1/10 | NumPy accelerated gradient / sklearn LinearSVC |

Lọc và tính thống kê dùng reflect không lặp pixel mép, tương ứng `mirror` trong SciPy. Hình thái dùng nền false bên ngoài ảnh, bao gồm erosion. Lee trên PNG chỉ là phép thử công thức, không bảo đảm mô hình nhiễu vật lý đúng. Không dùng PSNR/SSIM trên SAR thật vì không có ảnh sạch.

Giai đoạn 1 chạy 110 tổ hợp lọc/ngưỡng trên validation, morphology none/min_area16. Giữ 3 cấu hình đầu: nếu F1 cách mức tốt nhất <=0.005 thì ưu tiên Recall, sau đó thời gian, cuối cùng ID để có tie-break xác định. Giai đoạn 2 chạy 3 × 3 morphology × 3 diện tích × 3 nhóm đặc trưng × 9 classifier = 729 cấu hình thư viện. Chọn kết quả đầu mỗi họ CART/SVM, huấn luyện bản NumPy tương ứng, đối chiếu trên validation. Chỉ mô hình NumPy hội tụ và kiểm chứng thuật toán đạt mới được dùng cho test; chọn giữa hai bản NumPy theo cùng quy tắc. Đây là tìm kiếm theo giai đoạn, không đảm bảo tối ưu toàn cục trên mọi tổ hợp bị loại sớm.

## Đặc trưng và huấn luyện

8 đặc trưng theo thứ tự: area/image_area; sqrt((lambda_max+1e-6)/(lambda_min+1e-6)); area/bbox_area; perimeter_grid²/(4πarea); mean; std; mean Sobel magnitude trên biên trong; (mean_background−mean_region)/(|mean_background|+1e-6). Gradient Sobel chia 8. Chu vi đếm cạnh lưới, tránh so sánh các định nghĩa chu vi khác nhau. Vành nền là dilation đĩa r=5 trừ toàn bộ ứng viên; nếu rỗng dùng nền toàn ảnh, nếu vẫn rỗng dùng toàn ảnh.

Chỉ train dùng GT để gán nhãn vùng: purity >=0.5 là dầu, <=0.05 là nền; bỏ vùng còn lại khỏi train. Tối đa 10.000 vùng/lớp lấy mẫu seed2026. Validation/test vẫn đánh giá mọi dự đoán và mọi GT. Mean/std scaler chỉ fit trên train. Cột hằng SVM được regularize, `LinearSVC(fit_intercept=False)` trên ma trận đã thêm cột hằng để khớp mục tiêu.

SVM tối ưu `(0.5||w||² + CΣmax(1−yXw,0)²)/n`; báo objective, max absolute gradient, số vòng lặp và convergence. Tolerance gradient 1e-6, tối đa 10000 bước. CART chọn split Gini theo thứ tự đặc trưng/ngưỡng xác định; sklearn có thể khác tie-break và float precision, nên báo agreement/F1 thay vì yêu cầu cây giống hệt.

## Đánh giá và hai lớp so sánh

1. Giữa các thuật toán: precision/recall/F1 object micro, pixel IoU/Dice, FP/ảnh và thời gian. Kết quả thật tại `screen.json`, `validation.json`.
2. NumPy/thư viện: sai số tuyệt đối/tương đối, mask disagreement, model agreement, chênh lệch object F1, objective SVM và runtime. Sai số phép toán float mục tiêu atol=1e-6, rtol=1e-5; ngưỡng rất sát nhau có thể gây khác pixel nên cần báo riêng. `verification.json` gồm constant, tiny image, rỗng, full, lỗ, mép, split/merge, constant feature, single class và serialization. `model_comparison.json` chứa đối chiếu classifier trên toàn validation.

Object GT/pred là thành phần 8 liên thông của semantic mask, không phải instance đã được người gán sẵn. Ghép một-một IoU>=0.5, tối đa số cặp hợp lệ rồi tổng IoU. Tính tổng TP/FP/FN toàn split trước PRF. Không có mẫu số trả `null`/N/A, không tự thay 0. Báo thêm recall GT chạm biên và không chạm biên. Thời gian là tổng wall time xử lý từng ảnh/cấu hình dưới mức song song đã ghi, không phải latency thời gian thực đã kiểm định trên máy khác.

Test cuối gồm baseline none+Otsu, cấu hình đã chọn bỏ classifier, và pipeline NumPy đầy đủ. Khảo sát độ nhạy nhãn không làm thay đổi cấu hình. Phân tích FP/FN có ca lỗi nhiều, trung vị và ít lỗi; không chỉ chọn ảnh đẹp. Không báo confusion matrix dầu/gió yếu/màng sinh học/mưa vì SOS không có nhãn đó.

## Tái lập và đầu ra

`python scripts/sos.py reproduce --workers 6` chạy chuẩn bị manifest, kiểm chứng, benchmark, chọn mô hình và test. Checkpoint chỉ dùng trong cùng dữ liệu/mã đã cố định; khi sửa giao thức phải chuyển kết quả cũ sang thư mục khác trước chạy lại, không trộn hai thí nghiệm. Cache đặc trưng gắn hash manifest và mã trích. Lưu phiên bản thư viện, seed, checksum, cấu hình, model JSON, kết quả từng ảnh. Notebook gọi module chung, đọc chứng cứ đã thực thi và trực quan hóa các bước.

Đầu ra suy luận là mask dầu dự đoán, overlay và JSON đặc trưng/điểm quyết định từng vùng. Không dùng GT trong hàm predict. Muốn hoàn tất toàn bộ Đề 18 cần bổ sung dữ liệu SAR vật lý cùng góc tới và gió, cùng nhãn look-alike phù hợp; không chế metadata cho SOS.

Trong lần chạy này, cấu hình thắng dùng **Otsu toàn cục**, không phải ngưỡng thích nghi. Niblack thích nghi có mã NumPy/reference và đủ kết quả khảo sát; không đổi tên Otsu thành thích nghi để khớp đề. Nếu nghiệm thu yêu cầu ngưỡng thích nghi trong cấu hình mặc định, cần một thí nghiệm ràng buộc Niblack riêng và công bố kết quả của nó, không chọn lại dựa trên test đã xem.
