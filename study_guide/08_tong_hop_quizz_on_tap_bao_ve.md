# Chuyên đề 08: Bộ 25 câu trắc nghiệm tổng ôn & Bẫy thi cử bảo vệ BTL

> **Phạm vi tài liệu tự học — cập nhật 17/11/2026:** đây là giải thích và mã minh họa độc lập, không phải pipeline đã nghiệm thu hoặc bằng chứng đạt 100% đề. Công thức giản lược, ảnh giả lập, ví dụ ghép greedy và mô phỏng trôi dầu không thay thế kết quả trong `src/sar_oil`, `scripts` và `results`. Lee không bảo đảm giữ biên tuyệt đối; agreement 100% chỉ áp dụng cho ca đã đo; F1 SOS 0,3403 là cấu hình được chọn theo quy tắc dung sai, không phải cực đại nghiêm ngặt. Ưu tiên [đối chiếu hiện tại](../docs/DANH_GIA_DU_AN_VA_DOI_CHIEU_DE_18.md) khi có khác biệt.

> 🎯 **Mục tiêu chuyên đề:**\
> Bộ câu hỏi trắc nghiệm toàn diện ôn tập các kiến thức chính của dự án: Từ bản chất vật lý viễn thám SAR, bộ lọc thích nghi Lee, phân ngưỡng Otsu/Niblack, hình thái học, 8 đặc trưng toán học, học máy CART/SVM cho đến đánh giá độ đo khoa học.\
> *Mỗi câu hỏi đều có phân tích chi tiết "Bẫy thi cử" giúp bạn tránh các lỗi ngộ nhận thường gặp.*

---

## Phần 1: Vật lý Viễn thám SAR & Cơ chế vết dầu (Câu 1 - 5)

### Câu 1: Tại sao ảnh vệ tinh radar SAR lại được lựa chọn để phát hiện dầu tràn thay vì ảnh quang học (như Landsat, Sentinel-2)?
* A. Vì ảnh SAR có màu sắc sinh động hơn.
* B. Vì ảnh SAR có khả năng tự phát sóng vi ba xuyên qua mây mù, sương đêm và hoạt động bất kể ngày đêm.
* C. Vì ảnh SAR có giá thành rẻ hơn miễn phí hoàn toàn.
* D. Vì ảnh SAR không có nhiễu.
> **Đáp án:** **B**\
> ⚠️ **Bẫy thi cử:** Nhiều bạn trả lời "ảnh SAR nét hơn". Thực tế độ phân giải của SAR không nhất thiết nét hơn ảnh quang học tầm thấp, nhưng ưu thế tuyệt đối của SAR là **xuyên mây và chụp đêm** — thời điểm tai nạn dầu tràn và xả thải trộm hay xảy ra nhất.

### Câu 2: Cơ chế vật lý nào khiến vết dầu loang hiển thị thành màu tối đen trên ảnh SAR?
* A. Dầu thô có màu đen hấp thụ ánh sáng.
* B. Dầu làm tăng nhiệt độ bề mặt nước biển.
* C. Dầu làm dập tắt các sóng mao dẫn ngắn, biến mặt biển thành mặt phẳng phản xạ gương làm sóng radar trượt đi hướng khác, không dội về ăng-ten vệ tinh.
* D. Dầu phản xạ 100% sóng radar dội thẳng về vệ tinh.
> **Đáp án:** **C**\
> ⚠️ **Bẫy thi cử:** Tránh nhầm lẫn với cơ chế quang học (màu sắc đen/trắng). Radar đo độ tán xạ ngược (Backscatter). Biển nhám tán xạ Bragg (sáng), dầu dập sóng phản xạ gương (tối).

### Câu 3: Hiện tượng "Look-alike" (tương tự dầu) trên ảnh SAR là gì?
* A. Là các vết dầu nhân tạo do con người cố tình đổ ra để thử nghiệm.
* B. Là các hiện tượng tự nhiên làm mặt nước phẳng lặng (như gió yếu, màng sinh học do tảo phân hủy, vệt mưa, bóng đảo) tạo ra vệt tối giống hệt dầu tràn.
* C. Là lỗi cảm biến của vệ tinh bị hỏng điểm ảnh.
* D. Là vết dầu đã bị chìm xuống đáy đại dương.
> **Đáp án:** **B**

### Câu 4: Phép chia giá trị pixel ảnh PNG cho 255 trong code có ý nghĩa gì?
* A. Là phép chuẩn hóa góc tới vật lý (Incidence Angle Normalization).
* B. Là phép chuẩn hóa mức xám số học đưa giá trị về khoảng $[0, 1]$ để tính toán số thực, không phải chuẩn hóa góc tới vật lý.
* C. Là phép khử nhiễu đốm speckle.
* D. Là phép chuyển đổi ảnh từ ảnh xám sang ảnh màu.
> **Đáp án:** **B**\
> ⚠️ **Bẫy thi cử:** Thầy cô rất hay hỏi câu này để xem sinh viên có hiểu bản chất không. Đừng bao giờ nhận vơ chia 255 là chuẩn hóa góc tới!

### Câu 5: Dữ liệu tái phân tích trường gió ERA5 được tích hợp vào dự án nhằm mục đích gì?
* A. Để dự báo thời tiết cho trạm điều khiển vệ tinh.
* B. Để xác định tốc độ gió tại thời điểm chụp ảnh SAR, hỗ trợ loại trừ các vệt tối do gió yếu ($< 2-3\text{ m/s}$) gây ra.
* C. Để làm mát bộ vi xử lý máy tính.
* D. Để tính toán độ dày của màng dầu.
> **Đáp án:** **B**

---

## Phần 2: Nhiễu đốm & Bộ lọc Lee Filter (Câu 6 - 9)

### Câu 6: Bản chất toán học của nhiễu đốm (Speckle noise) trong ảnh SAR là:
* A. Nhiễu cộng độc lập: $y = x + n$
* B. Nhiễu nhân: $y = x \cdot v$ (với kỳ vọng $\mathbb{E}[v]=1$ và phương sai $\sigma_v^2 = 1/L$)
* C. Nhiễu hạt lượng tử Poisson
* D. Nhiễu xung muối tiêu đơn thuần
> **Đáp án:** **B**

### Câu 7: Trong công thức của bộ lọc Lee Filter $\hat{x} = \bar{y} + W(y - \bar{y})$, khi xét một pixel nằm sâu trong vùng biển phẳng đồng nhất, trọng số $W$ có giá trị xấp xỉ bao nhiêu?
* A. $W \approx 1$
* B. $W \approx 0$, khi đó $\hat{x} \approx \bar{y}$ (bộ lọc hoạt động như bộ lọc Mean làm mịn hoàn hảo)
* C. $W \approx 0.5$
* D. $W \to \infty$
> **Đáp án:** **B**

### Câu 8: Tại sao bộ lọc thích nghi Lee Filter lại vượt trội hơn bộ lọc trung bình Box Mean trong phát hiện dầu tràn?
* A. Vì Lee Filter chạy nhanh hơn Box Mean.
* B. Vì Box Mean làm mờ nhòe (blur) đường biên vết dầu, làm biến dạng hình thái; trong khi Lee Filter có thể hạn chế làm mờ ở đường biên, tùy tương quan tín hiệu và nhiễu ($W \to 1$).
* C. Vì Lee Filter không cần tham số nào.
* D. Vì Box Mean chỉ dùng được cho ảnh 1 chiều.
> **Đáp án:** **B**

### Câu 9: Kỹ thuật Bảng diện tích tích phân (Summed-Area Table) được nhóm cài đặt trong hàm `mean_filter` mang lại lợi ích gì?
* A. Giảm độ phân giải của bức ảnh xuống 4 lần.
* B. Tính trung bình vùng lân cận với độ phức tạp cố định $O(W \cdot H)$, tốc độ tính toán độc lập hoàn toàn với kích thước cửa sổ lọc.
* C. Tự động xoay bức ảnh theo hướng gió.
* D. Chuyển đổi dữ liệu sang dạng số nguyên.
> **Đáp án:** **B**

---

## Phần 3: Phân ngưỡng tách vùng tối (Câu 10 - 13)

### Câu 10: Mục tiêu toán học của thuật toán phân ngưỡng Otsu là gì?
* A. Tối đa hóa phương sai giữa hai lớp ($\sigma_b^2$), tương đương tối thiểu hóa phương sai nội lớp ($\sigma_w^2$).
* B. Tìm giá trị trung bình cộng của pixel sáng nhất và tối nhất.
* C. Đếm số lượng pixel có giá trị bằng 128.
* D. Cực tiểu hóa diện tích của vết dầu.
> **Đáp án:** **A**

### Câu 11: Thuật toán phân ngưỡng thích nghi cục bộ Niblack tính ngưỡng động theo công thức nào?
* A. $T(x,y) = m(x,y) + k \cdot s(x,y)$
* B. $T(x,y) = m(x,y) - k \cdot s(x,y)$ (với $m$ là trung bình cục bộ, $s$ là độ lệch chuẩn cục bộ)
* C. $T(x,y) = k \cdot m(x,y) / s(x,y)$
* D. $T(x,y) = s(x,y) - k \cdot m(x,y)$
> **Đáp án:** **B**

### Câu 12: Trong thực nghiệm dự án, tại sao nhánh Otsu lại đạt F1 cao hơn nhánh Niblack trên bộ dữ liệu SOS?
* A. Vì Otsu là thuật toán mới hơn Niblack.
* B. Vì các ảnh patch SOS có phạm vi hẹp và nền biển tương đối đồng nhất; Niblack bị sinh ra lượng lớn đốm đen giả ở vùng biển phẳng do độ lệch chuẩn cục bộ $s \approx 0$.
* C. Vì Niblack không thể lập trình bằng ngôn ngữ Python.
* D. Vì Niblack làm mất hết các vết dầu lớn.
> **Đáp án:** **B**

### Câu 13: Khi nào thuật toán Otsu toàn cục dễ bị sai sót nhất?
* A. Khi vết dầu chiếm đúng 50% diện tích ảnh.
* B. Khi vết dầu quá nhỏ (chiếm $< 1\%$ diện tích ảnh) khiến đỉnh của dầu bị chìm vào đỉnh của nền biển trên biểu đồ histogram.
* C. Khi ảnh không có nhiễu đốm.
* D. Khi ảnh có kích thước $256\times 256$.
> **Đáp án:** **B**

---

## Phần 4: Hình thái học & Gán nhãn liên thông (Câu 14 - 17)

### Câu 14: Tại sao trong bài toán vết dầu tràn, ta bắt buộc phải sử dụng liên thông 8 hướng (8-connected) thay vì liên thông 4 hướng?
* A. Vì liên thông 8 hướng chạy nhanh hơn.
* B. Vì vết dầu loang thường bị sóng kéo dài thành dải hẹp uốn lượn chéo góc; liên thông 4 hướng sẽ cắt đứt dải dầu thành nhiều mẩu vụn rời rạc.
* C. Vì OpenCV chỉ có liên thông 8 hướng.
* D. Vì liên thông 4 hướng làm mất màu của ảnh.
> **Đáp án:** **B**

### Câu 15: Cấu trúc dữ liệu nào được sử dụng trong thuật toán Connected Component của nhóm để tối ưu việc hợp nhất nhãn?
* A. Rừng tập hợp rời rạc (Disjoint-Set / Union-Find) có nén đường đi (Path compression).
* B. Hàng đợi hai đầu (Deque).
* C. Cây đỏ đen (Red-Black Tree).
* D. Bảng băm mở (Open Hash Table).
> **Đáp án:** **A**

### Câu 16: Phép toán hình thái học Opening (Mở) có tác dụng gì đối với ảnh nhị phân sau phân ngưỡng?
* A. Phình to đối tượng thêm 2 lớp pixel.
* B. Loại bỏ các chấm nhiễu trắng nhỏ li ti ngoài biển mà không làm thay đổi kích thước tổng thể của vết dầu lớn.
* C. Đảo ngược toàn bộ ảnh từ đen thành trắng.
* D. Làm tăng độ sáng của ảnh gốc.
> **Đáp án:** **B**

### Câu 17: Tại sao nhóm lại đặt ngưỡng loại bỏ các vùng có diện tích nhỏ hơn 64 pixel?
* A. Để tiết kiệm dung lượng ổ cứng.
* B. Vì các vùng nhỏ hơn 64 pixel đa phần là tàn dư của nhiễu đốm speckle ngẫu nhiên trên biển; loại bỏ chúng giúp giảm hơn 90% số ca báo động giả (False Positives).
* C. Vì ảnh Sentinel-1 không thể chụp được vật thể nhỏ hơn 64 pixel.
* D. Vì thuật toán SVM chỉ nhận vùng trên 64 pixel.
> **Đáp án:** **B**

---

## Phần 5: 8 Đặc trưng toán học & Học máy phân lớp (Câu 18 - 22)

### Câu 18: Độ thuôn dài (`elongation`) của vết dầu được nhóm tính toán dựa trên cơ sở toán học nào?
* A. Tỉ số giữa chiều rộng và chiều cao của hộp bao Bounding Box ($W/H$).
* B. Tỉ số căn bậc hai của các trị riêng (Eigenvalues $\sqrt{\lambda_1/\lambda_2}$) từ ma trận hiệp phương sai tọa độ của vùng.
* C. Chu vi chia cho diện tích ($P/A$).
* D. Khoảng cách Euclidean giữa hai điểm xa nhất.
> **Đáp án:** **B**\
> ⚠️ **Bẫy thi cử:** Tỉ số Bounding Box $W/H$ sẽ sai nếu vết dầu nằm chéo góc $45^\circ$. Trị riêng ma trận hiệp phương sai bất biến với góc quay!

### Câu 19: Đặc trưng độ phức tạp đường biên `complexity` $= P^2 / 4\pi A$ bắt nguồn từ định lý hình học nào?
* A. Định lý Pytago
* B. Bất đẳng thức đẳng chu (Isoperimetric Inequality), trong đó hình tròn có giá trị nhỏ nhất bằng 1, hình càng lởm chởm rách rưới thì giá trị càng lớn.
* C. Định lý Fermat
* D. Định lý giới hạn trung tâm
> **Đáp án:** **B**

### Câu 20: Tại sao đặc trưng độ tương phản nền (`background_contrast`) lại được tính dựa trên vành đai giãn nở 5 pixel (Dilation Ring 5px) bao quanh vết dầu?
* A. Vì lấy nền toàn ảnh sẽ bị sai lệch do sự biến thiên độ sáng tự nhiên của nền biển theo góc tới và trường gió diện rộng.
* B. Vì số 5 là số may mắn trong phong thủy.
* C. Vì thuật toán chỉ chạy được trong phạm vi 5 pixel.
* D. Để làm cho vết dầu trông nổi bật hơn trên màn hình hiển thị.
> **Đáp án:** **A**

### Câu 21: Tại sao mô hình Linear SVM trong dự án lại sử dụng Squared Hinge Loss thay vì Hinge Loss nguyên bản?
* A. Vì Squared Hinge Loss là hàm khả vi liên tục (smooth), có đạo hàm cấp 1 giải tích đẹp, cho phép giải mượt mà bằng giải thuật Gradient Descent.
* B. Vì Hinge Loss nguyên bản không có sẵn trong toán học.
* C. Vì Squared Hinge Loss luôn cho kết quả độ chính xác 100%.
* D. Vì Squared Hinge Loss làm giảm số chiều đặc trưng về 0.
> **Đáp án:** **A**

### Câu 22: Con số "Agreement = 1.0" trong báo cáo đối chứng mô hình chứng minh điều gì?
* A. Nhóm đã copy nguyên xi code của thư viện Scikit-learn.
* B. Cả hai mô hình đều dự đoán sai toàn bộ tập kiểm tra.
* C. Mô hình Linear SVM / CART tự lập trình bằng NumPy thuần đưa ra kết quả phân loại khớp chính xác 100% từng mẫu thử so với thư viện Scikit-learn chuẩn quốc tế.
* D. Dữ liệu thử nghiệm chỉ có 1 mẫu duy nhất.
> **Đáp án:** **C**

---

## Phần 6: Đánh giá độ đo khoa học & Thực tiễn (Câu 23 - 25)

### Câu 23: Trong đánh giá cấp độ đối tượng (Object-level), điều kiện để một vết dầu dự đoán được tính là True Positive (TP) là gì?
* A. Diện tích giao cắt IoU giữa vết dầu dự đoán và vết dầu Ground Truth phải đạt từ $0.5$ trở lên theo quy tắc ghép cặp 1-1.
* B. Vết dầu dự đoán phải bao phủ 100% toàn bộ bức ảnh.
* C. Tâm của vết dầu dự đoán trùng khít với tâm ảnh.
* D. Vết dầu dự đoán có diện tích lớn hơn $10.000$ pixel.
> **Đáp án:** **A**

### Câu 24: Tại sao trong bài toán cứu hộ và cảnh báo tràn dầu, chỉ số Recall lại được ưu tiên hơn Precision?
* A. Vì tính Recall dễ hơn tính Precision.
* B. Vì bỏ sót một vụ tràn dầu (False Negative / lọt lưới) sẽ gây thảm họa ô nhiễm môi trường biển nghiêm trọng; trong khi báo nhầm (False Positive) chỉ tốn chi phí điều tàu đi kiểm tra.
* C. Vì Precision luôn luôn bằng 0.
* D. Vì quy định của Bộ Tài nguyên Môi trường chỉ kiểm tra Recall.
> **Đáp án:** **B**

### Câu 25: Hướng phát triển nào sau đây giúp hệ thống không chỉ phát hiện vết dầu mà còn tìm ra thủ phạm xả thải trộm?
* A. Tăng số vòng lặp huấn luyện SVM từ 177 lên 10.000 vòng.
* B. Chuyển đổi mã nguồn từ Python sang C#.
* C. Tích hợp dữ liệu định vị tàu biển AIS (Automatic Identification System) theo không gian và thời gian để rà soát các tàu vừa di chuyển qua vùng xuất hiện vết dầu.
* D. Giảm kích thước cửa sổ lọc Lee xuống $3\times 3$.
> **Đáp án:** **C**
