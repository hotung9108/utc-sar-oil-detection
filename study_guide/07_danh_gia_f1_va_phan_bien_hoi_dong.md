# Chuyên đề 07: Đánh giá độ đo khoa học & Bộ câu hỏi phản biện Hội đồng BTL

> **Phạm vi tài liệu tự học — cập nhật 17/11/2026:** đây là giải thích và mã minh họa độc lập, không phải pipeline đã nghiệm thu hoặc bằng chứng đạt 100% đề. Công thức giản lược, ảnh giả lập, ví dụ ghép greedy và mô phỏng trôi dầu không thay thế kết quả trong `src/sar_oil`, `scripts` và `results`. Lee không bảo đảm giữ biên tuyệt đối; agreement 100% chỉ áp dụng cho ca đã đo; F1 SOS 0,3403 là cấu hình được chọn theo quy tắc dung sai, không phải cực đại nghiêm ngặt. Ưu tiên [đối chiếu hiện tại](../docs/DANH_GIA_DU_AN_VA_DOI_CHIEU_DE_18.md) khi có khác biệt.

> 🎯 **Mục tiêu chuyên đề:**\
> Nắm vững sự khác biệt bản chất giữa **Pixel IoU** và **Object F1** (tránh cạm bẫy "ngộ nhận số liệu"). Hiểu sâu sắc thuật toán ghép cặp đối tượng 1-1 ($IoU \ge 0.5$). Phân tích **3 ca thất bại điển hình**. Trang bị trọn bộ **20 câu hỏi vặn vẹo của Giảng viên** cùng câu trả lời mẫu sắc bén giúp bạn đạt điểm tối đa khi bảo vệ BTL.

---

## 1. Cạm bẫy số liệu: Tại sao Pixel IoU đạt 0.66 mà Object F1 chỉ đạt 0.28?

Khi nhìn vào bảng kết quả đánh giá cuối cùng trên 839 ảnh test Sentinel-1 ([results/sos/REPORT.md](file:///D:/Codin/utc-code/HK4_1/XLA/BTL/results/sos/REPORT.md)):
* **Pixel IoU:** $0.6614$ ($66.14\%$) — Rất cao!
* **Object F1:** $0.2805$ ($28.05\%$) — Có vẻ khiêm tốn?

Nhiều người sẽ thắc mắc: *"Tại sao hai con số này lại vênh nhau nhiều thế? Có phải mô hình bị lỗi không?"*\
**Câu trả lời:** Đây là hiện tượng kinh điển trong phân đoạn ảnh y tế và viễn thám, thể hiện hai góc nhìn hoàn toàn khác nhau:

### 1. Góc nhìn Pixel IoU (Intersection over Union ở cấp độ điểm ảnh):
$$\text{Pixel IoU} = \frac{\text{Số pixel giao nhau giữa Dự đoán và Ground Truth}}{\text{Số pixel hợp nhau giữa Dự đoán và Ground Truth}}$$
* Giả sử trong ảnh có **1 vết dầu khổng lồ (100.000 pixel)** và **10 vết dầu con li ti (mỗi vết 100 pixel)**.
* Mô hình phát hiện trúng $90\%$ diện tích của vết dầu khổng lồ, nhưng bỏ sót sạch cả 10 vết dầu con.
* Khi tính Pixel IoU: Vết dầu khổng lồ chiếm tới $99\%$ tổng số pixel, nên Pixel IoU vẫn đạt con số cực đẹp: **$> 0.85$**!
* $\implies$ **Pixel IoU dễ bị "đánh lừa" bởi các đối tượng kích thước lớn, che giấu hoàn toàn việc bỏ sót các vết dầu nhỏ!**

---

### 2. Góc nhìn Object-level F1 (Độ đo cấp độ đối tượng độc lập):
Trong thực tế cứu hộ hàng hải, mỗi vết dầu độc lập là một mục tiêu cần cử tàu ứng phó. Dù vết dầu to hay nhỏ, bỏ sót 1 vết dầu vẫn là một sự cố nghiêm trọng!

Nhóm đã sử dụng giao thức đánh giá đối tượng chuẩn mực:
* **Thuật toán ghép cặp một - một (1-to-1 Matching):**
  - Một vết dầu dự đoán $\hat{R}$ chỉ được công nhận là **True Positive (TP)** nếu diện tích giao cắt của nó với một vết dầu thực tế $R_{GT}$ đạt:
    $$\text{IoU}(\hat{R}, R_{GT}) = \frac{|\hat{R} \cap R_{GT}|}{|\hat{R} \cup R_{GT}|} \ge 0.5$$
  - Mỗi vết dầu GT chỉ được ghép với duy nhất 1 vết dự đoán tốt nhất (không được tính ăn gian 1 vết thật cho nhiều vết đoán).
* **Các chỉ số đối tượng:**
  - $\text{TP}$ (True Positive): Số vết dầu thực tế được phát hiện đúng.
  - $\text{FP}$ (False Positive): Số vết dầu "ma" do mô hình báo nhầm (báo động giả).
  - $\text{FN}$ (False Negative): Số vết dầu thực tế bị mô hình bỏ sót.
  $$\text{Precision} = \frac{\text{TP}}{\text{TP} + \text{FP}} = \frac{996}{996 + 2923} \approx 0.2541$$
  $$\text{Recall} = \frac{\text{TP}}{\text{TP} + \text{FN}} = \frac{996}{996 + 2186} \approx 0.3130$$
  $$\mathbf{F_1 = \frac{2 \cdot \text{Precision} \cdot \text{Recall}}{\text{Precision} + \text{Recall}} \approx 0.2805}$$

> 💡 **Khẳng định tính trung thực khoa học:**\
> Nhóm báo cáo rạch ròi cả hai chỉ số, không che giấu lỗi bằng Pixel IoU. Con số $F1 = 0.2805$ trên 839 ảnh test hoàn toàn độc lập phản ánh đúng thực tế phức tạp của bài toán ảnh viễn thám SAR tự nhiên!

---

## 2. Phân tích 3 ca thất bại điển hình (Failure Analysis)

Một báo cáo BTL xuất sắc không phải là báo cáo chỉ toàn khoe ảnh đẹp, mà là báo cáo **dám mổ xẻ những ca mô hình dự đoán sai và giải thích tường tận nguyên nhân**. Nhóm đã lưu trữ chi tiết tại [results/sos/diagnostics/REPORT.md](file:///D:/Codin/utc-code/HK4_1/XLA/BTL/results/sos/diagnostics/REPORT.md):

```text
       Ảnh đầu vào               Ground Truth                 Dự đoán lỗi
   [ ~~~ ******* ~~~ ]       [ ... XXXXXXX ... ]          [ ... ....... ... ]
     Vết dầu hẹp dài           Vết dầu thật                 Bị bỏ sót (FN)
```

1. **Ca 1: Phân mảnh vùng ở khòn ứng viên (`sentinel_440`):**
   - *Hiện tượng:* Vết dầu thực tế là một dải dài liền mạch, nhưng mô hình lại cắt đứt thành 5 mẩu nhỏ.
   - *Nguyên nhân:* Nhiễu đốm speckle cục bộ kết hợp với bước phân ngưỡng Otsu toàn cục đã cắt đứt các "eo hẹp" của vệt dầu. Khi chia thành 5 mẩu nhỏ, 3 mẩu có diện tích $< 64$ px bị bước lọc hình thái học xóa sổ, 2 mẩu còn lại không đủ IoU $\ge 0.5$ với vết dầu lớn gốc $\implies$ Bị tính thành False Negative.
2. **Ca 2: Phân lớp sai do vết dầu quá thuôn mảnh (`sentinel_25`):**
   - *Hiện tượng:* Bước tạo ứng viên phát hiện trọn vẹn vết dầu, nhưng bước phân lớp SVM lại gạt bỏ nó thành nhãn 0 (nền).
   - *Nguyên nhân:* Vết dầu này là vết dầu rất mỏng do tàu di chuyển tốc độ cao để lại. Đường biên của nó quá hẹp khiến cho gradient biên không đủ độ dốc gắt, độ tương phản vành nền 5px bị pha loãng bởi chính nước biển hai bên sườn. Bộ phân lớp SVM đánh giá điểm $\text{score} = -0.12 \le 0 \implies$ Bị loại nhầm.
3. **Ca 3: Lỗi chạm mép khung ảnh (`sentinel_591`):**
   - *Hiện tượng:* Vết dầu bị cắt ngang bởi mép viền của bức ảnh radar.
   - *Nguyên nhân:* Do bị cắt ngang mép ảnh, vết dầu bị cụt một đầu, làm sai lệch toàn bộ ma trận hiệp phương sai tọa độ (độ thuôn dài bị tụt từ $4.5$ xuống còn $1.2$, độ phức tạp biên bị tính sai do cạnh mép ảnh) $\implies$ Mô hình nhầm tưởng đây là một mảng gió yếu hình khối bầu bĩnh!

---

## 3. Trọn bộ 20 câu hỏi "xoáy" của Giảng viên & Câu trả lời mẫu sắc bén

Dưới đây là cẩm nang trả lời phản biện giúp bạn hoàn toàn làm chủ buổi bảo vệ:

### Nhóm 1: Về Bản chất Vật lý SAR & Dữ liệu
* **Câu 1:** *Tại sao dùng ảnh SAR mà không dùng ảnh vệ tinh quang học như Landsat/Sentinel-2?*\
  $\to$ **Đáp:** Vì ảnh quang học bị mù hoàn toàn vào ban đêm và khi trời có mây mù bão gió. Tràn dầu và xả thải trộm thường xảy ra vào ban đêm. Radar SAR tự phát sóng vi ba nên chụp xuyên ngày đêm và xuyên mây mù bão gió.
* **Câu 2:** *Tại sao vết dầu lại có màu đen trên ảnh SAR?*\
  $\to$ **Đáp:** Sóng mao dẫn tạo độ nhám khiến mặt biển tán xạ Bragg dội năng lượng về vệ tinh (biển sáng). Dầu có độ nhớt dập tắt sóng mao dẫn, biến mặt biển phẳng như gương làm sóng phản xạ gương trượt đi hướng khác, không dội về vệ tinh (dầu tối).
* **Câu 3:** *Hiện tượng "Look-alike" là gì? Kể tên 3 nguyên nhân?*\
  $\to$ **Đáp:** Là các hiện tượng tự nhiên làm mặt biển bị phẳng và tạo vệt đen giống hệt dầu tràn. 3 nguyên nhân: Vùng biển lặng gió ($< 2-3\text{ m/s}$), màng sinh học do tảo chết phân hủy, và bóng khuất gió sau các hòn đảo ven bờ.
* **Câu 4:** *Tại sao nhóm nói ảnh PNG của bộ SOS chưa chuẩn hóa góc tới?*\
  $\to$ **Đáp:** Vì ảnh PNG trong SOS đã bị cắt thành các patch 8-bit và mất siêu dữ liệu (metadata) góc tới. Phép chia 255 chỉ là đưa mức xám về $[0, 1]$ về mặt số học. Chuẩn hóa góc tới vật lý đòi hỏi đọc file XML/LUT để tính độ dốc tán xạ $\sigma^0$ và $\gamma^0$. Nhóm nhận thức rõ điều này nên đã làm thêm nhánh Cantarell trên ảnh Sentinel-1 gốc.
* **Câu 5:** *Tập dữ liệu DARTIS nhóm dùng để làm gì?*\
  $\to$ **Đáp:** DARTIS gồm 2.290 ảnh SAR hoàn toàn không có dầu (tập âm tính), dùng để kiểm tra độ tin cậy thực tế và đo lường tỷ lệ báo động giả (False Alarm Rate) của pipeline.

### Nhóm 2: Về Thuật toán Xử lý ảnh & Lập trình NumPy
* **Câu 6:** *Tại sao chọn bộ lọc Lee Filter mà không dùng Gaussian hay Mean Filter?*\
  $\to$ **Đáp:** Nhiễu SAR là nhiễu nhân do giao thoa kết hợp. Mean và Gaussian làm mờ nhòe đường biên vết dầu; Median cắt cụt các đuôi dầu nhọn. Lee Filter thích nghi: làm mịn mạnh trong lòng biển ($W \to 0$) nhưng có thể hạn chế làm mờ ở đường biên, tùy tương quan tín hiệu và nhiễu vết dầu ($W \to 1$).
* **Câu 7:** *Ý nghĩa tham số $L=4$ trong Lee Filter là gì?*\
  $\to$ **Đáp:** $L$ là số lượt nhìn độc lập (Number of looks), đại diện cho phương sai nhiễu $\sigma_{noise}^2 = \bar{y}^2/L$. Giá trị $L=4$ tương thích với định dạng Sentinel-1 GRD thực tế.
* **Câu 8:** *Thuật toán Otsu hoạt động dựa trên nguyên lý nào?*\
  $\to$ **Đáp:** Tối đa hóa phương sai giữa hai lớp ($\sigma_b^2$), tương đương với tối thiểu hóa phương sai nội lớp ($\sigma_w^2$), quét nhanh trên 256 bin của biểu đồ tần số mức xám.
* **Câu 9:** *Khi nào thuật toán Otsu thất bại?*\
  $\to$ **Đáp:** Khi vết dầu quá nhỏ (chiếm $< 1\%$ diện tích ảnh), đỉnh của dầu bị chìm vào đỉnh của biển trên histogram; hoặc khi độ sáng nền biển bị nghiêng lệch mạnh theo góc tới.
* **Câu 10:** *Tại sao lại chọn liên thông 8 hướng mà không dùng liên thông 4 hướng?*\
  $\to$ **Đáp:** Dầu loang thường bị sóng kéo dài thành các dải hẹp uốn lượn chéo góc $45^\circ$. Liên thông 4 hướng sẽ cắt đứt dải dầu này thành hàng chục mảnh vụn rời rạc.
* **Câu 11:** *Kỹ thuật Union-Find trong bước gán nhãn giải quyết bài toán gì?*\
  $\to$ **Đáp:** Giải quyết bài toán hợp nhất các nhãn tạm tương đương khi quét hai dòng liên tiếp bằng cấu trúc rừng cây rời rạc, có nén đường đi giúp thuật toán đạt tốc độ gần như tuyến tính $O(N \cdot \alpha(N))$.

### Nhóm 3: Về 8 Đặc trưng & Học máy
* **Câu 12:** *Tại sao độ thuôn dài (Elongation) lại dùng trị riêng ma trận hiệp phương sai thay vì tỷ lệ Bounding Box?*\
  $\to$ **Đáp:** Nếu vết dầu dài nằm chéo góc $45^\circ$, Bounding box của nó là hình vuông ($W/H \approx 1$) dẫn đến tính sai. Trị riêng ma trận hiệp phương sai $\sqrt{\lambda_1/\lambda_2}$ tự động xoay theo trục quán tính thực của vết dầu bất kể góc nghiêng.
* **Câu 13:** *Độ phức tạp đường biên $P^2 / 4\pi A$ bắt nguồn từ đâu?*\
  $\to$ **Đáp:** Bắt nguồn từ Bất đẳng thức đẳng chu (Isoperimetric Inequality). Hình tròn hoàn hảo có giá trị bằng 1. Vết dầu loang tự nhiên có biên nham nhở, rách rưới nên giá trị rất lớn ($> 4.0$).
* **Câu 14:** *Tại sao độ tương phản nền lại dùng vành đai 5 pixel mà không dùng nền toàn ảnh?*\
  $\to$ **Đáp:** Vì nền biển diện rộng bị biến thiên độ sáng do góc tới và gió. Vành đai 5 pixel lấy chính xác mẫu nước biển lân cận ngay sát vết dầu, phản ánh độ tương phản chân thực nhất.
* **Câu 15:** *Tại sao nhóm dùng Linear SVM với Squared Hinge Loss?*\
  $\to$ **Đáp:** Squared Hinge Loss khả vi liên tục (trơn), có đạo hàm cấp 1 giải tích đẹp, cho phép tối ưu hóa mượt mà bằng giải thuật Gradient Descent.
* **Câu 16:** *Giải thuật Nesterov Accelerated Gradient cải tiến điều gì so với Gradient Descent thông thường?*\
  $\to$ **Đáp:** Nó bổ sung động lượng nhìn trước (Look-ahead momentum), tăng tốc độ hội tụ từ $O(1/k)$ lên mức tối ưu lý thuyết $O(1/k^2)$, chỉ mất 177 vòng lặp là hội tụ.
* **Câu 17:** *Con số Agreement = 1.0 có ý nghĩa gì?*\
  $\to$ **Đáp:** Chứng minh code Linear SVM và CART tự viết bằng NumPy thuần đưa ra kết quả phân loại khớp $100\%$ từng mẫu thử so với thư viện Scikit-learn chuẩn quốc tế.

### Nhóm 4: Về Đánh giá & Hướng phát triển
* **Câu 18:** *Tại sao nhóm dùng ngưỡng IoU $\ge 0.5$ để ghép cặp đối tượng?*\
  $\to$ **Đáp:** Đây là quy chuẩn vàng của cuộc thi quốc tế PASCAL VOC và COCO. Nó đòi hỏi vết dầu dự đoán phải bao phủ ít nhất $50\%$ diện tích vết dầu thật thì mới được công nhận là phát hiện trúng (TP).
* **Câu 19:** *Recall và Precision: Cái nào quan trọng hơn trong bài toán tràn dầu?*\
  $\to$ **Đáp:** Recall quan trọng hơn! Vì bỏ sót một vụ tràn dầu (False Negative) sẽ gây ra thảm họa ô nhiễm môi trường biển không thể khắc phục. Báo nhầm (False Positive) chỉ tốn công cử tàu đi tuần tra xác minh. Cấu hình của nhóm ưu tiên Recall trong F1-band.
* **Câu 20:** *Nếu tiếp tục phát triển đề tài, nhóm sẽ làm gì tiếp theo?*\
  $\to$ **Đáp:** Nhóm sẽ tích hợp dữ liệu hải trình tàu biển AIS để truy vết con tàu nào vừa đi qua tọa độ vết dầu (tìm thủ phạm xả trộm); và áp dụng mô hình thủy văn Lagrange mô phỏng hướng trôi của dầu theo dòng chảy và gió ERA5 để cảnh báo sớm cho ngư dân ven biển miền Trung.

---

## 4. Trắc nghiệm ôn tập nhanh (Quiz 07)

**Câu 1:** Trong đánh giá cấp độ đối tượng (Object-level), một vết dầu dự đoán được coi là phát hiện đúng (True Positive) khi nào?\
A. Khi tâm của nó trùng khớp hoàn toàn với tâm vết dầu thật.\
B. Khi diện tích giao cắt IoU của nó với một vết dầu Ground Truth đạt từ $0.5$ trở lên.\
C. Khi nó có diện tích lớn hơn $1000$ pixel.\
D. Khi Pixel IoU đạt 100%.\
*(Đáp án: **B**)*

**Câu 2:** Hiện tượng một vết dầu thực tế lớn bị mô hình cắt đứt thành nhiều mẩu nhỏ được gọi là:\
A. Phân mảnh vùng (Fragmentation / Under-segmentation)\
B. Quá khớp (Overfitting)\
C. Dập sóng Bragg\
D. Tán xạ ngược\
*(Đáp án: **A**)*

**Câu 3:** Tại sao các vết dầu nằm sát mép viền của bức ảnh radar thường dễ bị mô hình dự đoán sai?\
A. Vì mép ảnh luôn có màu đỏ.\
B. Vì vết dầu bị cắt cụt làm sai lệch độ thuôn dài, độ phức tạp biên và không lấy đủ vành nền cục bộ 5px.\
C. Vì mép ảnh không thể đọc được bằng thư viện Pillow.\
D. Vì sóng radar không quét tới mép ảnh.\
*(Đáp án: **B**)*

**Câu 4:** Khi so sánh giữa Pixel IoU và Object F1, phát biểu nào sau đây là **ĐÚNG**?\
A. Pixel IoU luôn nhỏ hơn Object F1 trong mọi trường hợp.\
B. Pixel IoU dễ bị chi phối bởi các đối tượng có diện tích khổng lồ, che giấu việc mô hình bỏ sót các đối tượng nhỏ.\
C. Object F1 không quan tâm đến vị trí của vết dầu.\
D. Hai độ đo này có giá trị luôn luôn bằng nhau.\
*(Đáp án: **B**)*

**Câu 5:** Hướng phát triển nào sau đây giúp tìm ra danh tính con tàu đã xả trộm vết dầu trên biển?\
A. Tăng kích thước bộ lọc Lee lên $15\times 15$.\
B. Chuyển sang dùng ngưỡng Niblack thay cho Otsu.\
C. Tích hợp dữ liệu định vị hàng hải AIS (Automatic Identification System) theo không gian và thời gian.\
D. Tăng số lượng bin của biểu đồ Otsu lên 1024 bin.\
*(Đáp án: **C**)*
