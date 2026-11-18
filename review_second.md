
## 3. Lỗi số liệu còn lại (cần sửa)

| Vị trí | Văn bản | Giá trị đúng theo bảng |
|---|---|---|
| Kết luận, ý 2 | Precision "từ 0,0768 … gấp 3,3 lần" | Bảng 6: 0,0753 (= 1018/13513), gấp ≈ 3,37 lần |
| Kết luận, ý 1 | R0 "từ 23,47 xuống 0,19 FP/ảnh" | Mục 5.4 ghi 24,32 (754/31 = 24,32 khớp số nguyên, còn 23,47 thì không) |
| Kết luận, phát hiện 1 | ΔF1 (Lee vs Mean) = 0,0003 | Bảng 4: +0,0014 [−0,0003; +0,0033]. 0,0003 là cận CI |
| Kết luận, đầu | "không gian **9** đặc trưng **bất biến**" | Có 8 đặc trưng (9 là chiều của w kèm bias). "Bất biến" mâu thuẫn với chú thích về `area_fraction` ở 5.4 |
| Kết luận, ý 2 | "Pixel IoU trung bình của các vết dầu **ghép cặp** Hungarian đạt 0,6614" | Pixel IoU (Eq. 19) gộp toàn bộ pixel, không phụ thuộc ghép cặp. Trung bình theo ảnh là 0,577 |
| Abstract, mục 1, Kết luận | "bảo toàn 97,8% vết dầu thật" / "996/1.018 vùng dầu thật" | 1.018 là TP của Giai đoạn 1, không phải toàn bộ dầu thật (3.182). Tỷ lệ dầu thật được phát hiện là 31,3%. Cần đổi thành "giữ lại 97,8% TP của giai đoạn 1" |
| Bảng 3 | "ALOS PALSAR **Val**" | Bảng 2 và 4.1 gọi là Test |
| Bảng 4 vs Bảng 6 | Lee 7×7 + Otsu: F1 = 0,0855 (A_min = 16, validation) và 0,1220 (A_min = 64, test) | Hai giá trị cùng tên cấu hình, không được đối chiếu hay giải thích |
| Toàn bài | "1.049" (nghìn) cạnh "0,0481" (thập phân) | Dấu chấm vừa là phân cách nghìn vừa là thập phân, dễ hiểu nhầm. Nên chọn một quy ước |

Hình 2 còn thiếu chú thích về nguồn ảnh. Các ảnh minh họa và ảnh phân tích lỗi (sentinel_25, 440, 591…) có thuộc tập test không? Nếu có, hãy ghi rõ đó là phân tích hậu nghiệm.

---

## 4. Các vấn đề khoa học chính

### 4.1. Nhãn huấn luyện không khớp thước đo đánh giá (quan trọng nhất)

Bộ phân loại được huấn luyện với nhãn dương = purity ≥ 0,5 (pixel-level). Thước đo cuối là IoU ≥ 0,5 giữa vùng dự đoán và đối tượng GT nguyên khối. Hai thứ này khác nhau cơ bản, và số liệu của bài cho thấy sự lệch này rất lớn:

- Tập train có 11.092/39.530 ≈ **28%** ứng viên được gán dương (4,13 ứng viên dương/ảnh).
- Ở tập test, chỉ 1.018/13.513 ≈ **7,5%** ứng viên là TP theo IoU ≥ 0,5 (1,21/ảnh). Đây là so sánh thô giữa hai tập, nhưng bậc độ lớn đủ rõ.
- Mô hình dự đoán dương 3.919/839 = **4,67 vùng/ảnh**, xấp xỉ tỷ lệ dương của nhãn huấn luyện.

Nghĩa là bộ phân loại học cách giữ lại các mảnh nằm trong dầu (đúng với nhãn purity), còn đánh giá lại tính các mảnh đó là FP khi chúng không đạt IoU ≥ 0,5. Trường hợp sentinel_440 (35 mảnh nằm trọn trong dầu, bị tính 35 FP) là minh họa cực đoan của cùng hiện tượng.

Hệ quả là "FP/ảnh = 3,48" lẫn lộn hai loại lỗi rất khác nhau: **báo nhầm thật** (vùng tối ngoài dầu) và **phân mảnh/hợp nhất** (vùng nằm trong dầu nhưng IoU thấp). Với nội dung của bài (loại vùng tối giả), chỉ loại thứ nhất đáng gọi là false alarm. Đề nghị:

- Phân rã FP theo purity (≤ 0,05 / trung gian / ≥ 0,5) và báo cáo tỷ lệ.
- Thử huấn luyện bằng nhãn IoU với đối tượng GT thay vì purity.
- Thêm bước gộp các mảnh được chấp nhận liền kề (closing hoặc hợp theo khoảng cách d) trước khi đánh giá.
- Báo cáo thêm thước đo nới lỏng (IoU ≥ 0,1/0,3, hoặc phát hiện nếu phủ ≥ x% GT).

### 4.4. Lee MMSE: "suy biến" nhiều khả năng do L cấu hình sai

Bài tìm thấy Lee 7×7 ≈ Mean 7×7 (ΔF1 CI chứa 0) và L = 1 ≈ L = 4 ở mọi kích thước cửa sổ (ví dụ 3×3: 0,0329 vs 0,0326; 5×5: 0,0535 vs 0,0534). Bài giải thích rằng ảnh đã bị lọc đốm trong tiền xử lý nên v ≤ m²/L. Giải thích này hợp lý, nhưng kết luận "Lee thoái hóa về Mean" là hệ quả của việc chọn L quá nhỏ. W = 0 khi hệ số biến thiên cục bộ C² ≤ 1/L. Nếu ảnh đã được lọc thì ENL thực lớn hơn 4 nhiều. Cả L = 1 và L = 4 đều nằm dưới ENL thực nên W ≈ 0 là đương nhiên. Thí nghiệm hợp lý là tăng L (8, 16, 32…) hoặc **ước lượng ENL** từ vùng biển đồng nhất (ENL ≈ (m/σ)² trên các cửa sổ ở ảnh R0). Khi đó Lee mới thực sự bảo toàn biên. Hiện kết luận "Lee không hơn Mean" chưa được kiểm chứng đúng chỗ.

Các điểm liên quan:

- Lọc tốt nhất vẫn là cửa sổ lớn nhất trong lưới (7×7), và ΔF1 giảm đều theo kích thước cửa sổ. Nên mở rộng lưới (9, 11, 15, Gaussian σ lớn hơn). Nếu tối ưu nằm ở biên lưới thì chưa thể nói cấu hình 7×7 là tối ưu.
- Thiếu đối chứng Mean 3×3/5×5 để tách "kích thước cửa sổ" khỏi "loại bộ lọc".
- Chưa nêu miền giá trị của ảnh. PNG 8-bit có thể là amplitude, intensity hoặc dB/log. Nếu là log hay đã kéo dãn phi tuyến thì mô hình I = R·u và ngưỡng m²/L không còn đúng trong miền pixel. Cần nêu rõ hoặc thử lọc trong miền log.
- Vì vậy phần nhấn mạnh "tối ưu hóa bộ lọc Lee bằng bảng tích phân" ở Abstract và Kết luận không còn phù hợp với chính kết quả của bài. Về thực chất đó là bộ lọc hộp (box blur) cài bằng bảng tích phân. Việc này đúng và hữu ích nhưng không phải là phát hiện về "Lee MMSE".

### 4.5. So sánh chưa kiểm soát đủ biến

- Baseline thô dùng A_min = 16, pipeline dùng A_min = 64. Phần giảm FP 58,62 → 14,89 gồm cả hiệu ứng lọc và hiệu ứng A_min. Cần baseline **thô + Otsu + A_min = 64** để tách hai yếu tố.
- Mục 5.1 chọn bộ lọc ở A_min = 16, rồi pipeline cuối dùng 64 mà không có bảng quét A_min.
- "110 cấu hình lọc/ngưỡng" và "729 cấu hình mô hình vùng" xuất hiện trong Abstract nhưng không được liệt kê ở đâu: không có danh sách tham số, 6 siêu tham số nào có 3 giá trị, và C = 10, depth = 3, leaf = 20, A_min = 64 được chọn ra sao. Mục 5.1 chỉ trình bày 13 + 9 cấu hình. Cần một bảng hoặc phụ lục. Việc chọn trong 729 tổ hợp trên 671 ảnh cũng cần được nêu như một nguồn lạc quan (selection bias) của các số liệu validation (Bảng 5).
- Niblack chỉ có 9 cấu hình, chưa có k < 0,2, cửa sổ > 51 hay Sauvola. Cấu hình tốt nhất (51×51, k = 0,2) nằm ở biên lưới. Phần kết quả Niblack chỉ có văn bản, không có bảng.

### 4.6. Khái quát hóa đa cảm biến

Văn bản ở 5.4 đã thận trọng (giải thích bằng mật độ đối tượng 5,15 so với 3,79 và `area_fraction` chưa bất biến). Nhưng Kết luận vẫn viết "chứng minh tính ổn định của các đặc trưng". Cần thêm:

- Huấn luyện trên PALSAR rồi kiểm thử trên Sentinel. Bảng 2 cho thấy đã có sẵn 3.101 ảnh PALSAR train chưa dùng.
- Mô hình trong miền (PALSAR → PALSAR).
- Dòng Lee + Otsu không classifier trên PALSAR, để biết mức tăng thực do bộ phân loại.
- Phân bố chế độ diện tích khác hẳn nhau: PALSAR có 585/776 (75%) ảnh R2 và chỉ 33 ảnh R3+R4, trong khi Sentinel có 252/839. Vì vậy so F1 giữa hai tập chưa công bằng. Cần báo cáo F1 theo từng chế độ cho cả hai cảm biến.
- Chuyển miền thay đổi đồng thời băng tần, phân cực, góc tới, độ phân giải, địa điểm và loại dầu, nên không quy được cho riêng bước sóng.

### 4.7. Diễn giải trọng số SVM mâu thuẫn với Hình 5

Mục 5.2 giải thích w₆ (boundary_gradient) âm là vì "mảnh nhiễu do Otsu cắt có gradient biên rất gắt". Nhưng trong Hình 5, lớp vùng tối giả có gradient chuẩn hóa **thấp hơn** lớp dầu (trung vị ≈ −0,8 so với ≈ −0,3). Quan hệ biên chỉ là chiều dương, còn trọng số âm là hệ quả của đa cộng tuyến: f₇ = (µ_bg − µ)/µ_bg tương quan mạnh với f₄ và f₆, nên w₆ âm là hiệu ứng "suppressor" khi đã có w₇ rất lớn. Giải thích vật lý này là hậu nghiệm và bị chính biểu đồ của bài phản bác. Nên bỏ, hoặc báo cáo ma trận tương quan, VIF và hệ số khi huấn luyện từng nhóm riêng. Tương tự, "thuôn dài theo chiều gió" chưa được kiểm chứng (không có dữ liệu gió).

Ablation (Bảng 5) cũng cho thấy kết quả đáng chú ý nhưng chưa được khai thác: nhóm 4 đặc trưng bức xạ/biên cho F1 = 0,3379, còn thêm 4 đặc trưng hình học chỉ nâng lên 0,3403 (+0,0024) và SVM hơn CART đúng 0,003 (0,3403 vs 0,3373). Không có CI, những chênh lệch này không thể coi là có ý nghĩa. Câu "kết hợp 8 đặc trưng cho hiệu năng cao nhất" cần kèm CI hoặc đổi thành "tương đương". Ngoài ra CART đã bị bỏ khỏi Bảng 6, nên so sánh SVM–CART chỉ còn trên validation.

### 4.8. Đặc trưng nền và ca biên

- Vành nền được định nghĩa là (Ωᵢ ⊕ B₅) ∩ {labels = 0}. Pixel có nhãn 0 gồm các pixel nằm trên ngưỡng Otsu (và các vùng tối nhỏ đã bị lọc diện tích). Vì vậy µ_bg bị thiên lệch sáng một cách cấu trúc và f₇ phụ thuộc phần nào vào chính ngưỡng Otsu (đặc trưng "tự tham chiếu").
- Với R3/R4, khi vành rỗng thì µ_bg lấy trung bình nền còn lại hoặc trung bình toàn ảnh, nên f₇ ≈ 0 hoặc suy biến. Phân tích lỗi (sentinel_591) cho thấy đây là nguyên nhân bộ phân loại loại bỏ vùng dầu thật. Với R4 (56 ảnh, TP = 44, FP = 227), đây là một thiên lệch có hệ thống, không chỉ một trường hợp. Nên báo cáo tỷ lệ ứng viên rơi vào nhánh fallback theo chế độ và tác động đến F1.

### 4.9. Chế độ R0 và ngoại suy vận hành

- R0 chỉ có 31 ảnh (3,7% tập test) và 6 FP. Con số "0,19 FP/ảnh, giảm 99,2%" cần khoảng tin cậy (ví dụ Poisson hoặc bootstrap) vì mẫu rất nhỏ.
- SOS đã được sàng lọc và có tới ~96% ảnh chứa dầu, nên không thể ngoại suy FP/ảnh sang giám sát thực tế, nơi biển sạch chiếm đa số. Nên có thử nghiệm trên cảnh đầy đủ hoặc ít nhất trên một tập có tỷ lệ biển sạch cao hơn.
- Bài chưa dùng đặc trưng kết cấu (GLCM…) dù các công trình nền tảng đã trích dẫn ([14], [15]) chủ yếu dựa vào chúng. Nên giải thích lý do loại trừ, hoặc thêm vào để so sánh.

### 4.10. Thống kê và giao thức

- Chỉ phép so sánh bộ lọc có CI. Bảng 6 (kết quả chính) và so sánh SVM–CART không có CI. Bootstrap theo patch sẽ cho khoảng quá hẹp nếu các patch cùng cảnh tương quan. Cần ghi chú hoặc dùng bootstrap theo cụm.
- Bộ phân loại chỉ được đánh giá ở ngưỡng cố định 0 và sau khi lấy mẫu giảm cân bằng (bỏ ~61% mẫu âm, trong khi tỷ lệ dương/âm của test rất lệch). Cần đường cong Precision–Recall (hoặc FP/ảnh theo Recall), ROC-AUC/PR-AUC ở cấp vùng trên validation, và chọn điểm vận hành trên validation. Có thể so sánh với trọng số lớp thay vì lấy mẫu giảm.
- Chỉ một seed (2026). Cần báo cáo độ biến thiên theo seed lấy mẫu.
- Macro-average được tính "trên các ảnh có mẫu số xác định" nên n khác nhau giữa các cột. Cần ghi n cho mỗi cột.
- Điều kiện dừng ‖∇J‖∞ ≤ 10⁻⁶ áp dụng cho J đã chia n = 20.000, tương đương dung sai khoảng 0,02 trên mục tiêu chưa chuẩn hóa, lỏng hơn vẻ ngoài. Hình 6 chỉ có vài điểm nối thẳng nên không minh họa được hội tụ. Nên vẽ J − J* theo từng vòng lặp (thang log) và so với L-BFGS/liblinear. Với bài toán 9 tham số, NAG chỉ có giá trị minh họa, không nên là điểm nhấn.
- Về thời gian chạy, 50,2 ms/ảnh cần nêu CPU cụ thể và so với một baseline học sâu nhỏ hoặc cài đặt SciPy. "Nhanh hơn baseline thô" (42,11 s so với 90,46 s) phản ánh việc cài đặt thuần NumPy xử lý hàng chục nghìn thành phần liên thông, không phải ưu thế của phương pháp.

---

## 5. Còn thiếu so với bản trước (chưa được giải quyết)

- Bằng chứng về look-alike vẫn thiếu. Kết luận vẫn nói "phân biệt vết dầu và vùng tối nhiễu nền", nhưng nhãn SOS là nhị phân và không có phân tích nào cho thấy FP bị loại là look-alike. Phân rã FP theo purity (mục 4.1) và duyệt thủ công một mẫu sẽ giải quyết việc này.
- Mã nguồn, môi trường và seed vẫn chưa được công bố. Bài tự hào về cài đặt NumPy "đạt sai số < 10⁻¹¹", nên việc phát hành mã là điều tự nhiên.

---

## 6. Trình bày và tài liệu tham khảo

- Hình 1 là sơ đồ nằm ngang một hàng, chữ nhỏ đến mức không đọc được. Hình 3, 5, 6 cũng khá nhỏ.
- Bảng 4 và 6 quá dày (11 cột). Nên bỏ bớt cột hoặc xoay trang.
- Một số ký tự đầu dòng bị lỗi hiển thị trong danh sách (glyph thiếu). Tên Pietikäinen ở [13] bị lỗi mã hóa.

- Abstract quá dài. Nên rút gọn và đưa các con số chi tiết (110/729 cấu hình, 9.572 vùng) xuống thân bài.
