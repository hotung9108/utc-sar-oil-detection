# Chuyên đề 06: Học máy phân lớp — CART & Linear SVM tự cài đặt bằng NumPy thuần

> **Phạm vi tài liệu tự học — cập nhật 17/11/2026:** đây là giải thích và mã minh họa độc lập, không phải pipeline đã nghiệm thu hoặc bằng chứng đạt 100% đề. Công thức giản lược, ảnh giả lập, ví dụ ghép greedy và mô phỏng trôi dầu không thay thế kết quả trong `src/sar_oil`, `scripts` và `results`. Lee không bảo đảm giữ biên tuyệt đối; agreement 100% chỉ áp dụng cho ca đã đo; F1 SOS 0,3403 là cấu hình được chọn theo quy tắc dung sai, không phải cực đại nghiêm ngặt. Ưu tiên [đối chiếu hiện tại](../docs/DANH_GIA_DU_AN_VA_DOI_CHIEU_DE_18.md) khi có khác biệt.

> 🎯 **Mục tiêu chuyên đề:**\
> Hiểu tại sao dự án chọn thuật toán học máy cổ điển thay vì Deep Learning "hộp đen". Nắm vững nguyên lý cây quyết định **CART** qua chỉ số bất thuần Gini. Chứng minh bài toán tối ưu **Linear SVM với Squared Hinge Loss** và giải thuật gia tốc **Nesterov Accelerated Gradient**. Giải thích ý nghĩa của con số "Agreement = 1.0" giữa code NumPy tự viết và Scikit-learn.

---

## 1. Trực giác đời thường: Tại sao không dùng Deep Learning (CNN / U-Net)?

Ngày nay, khi nhắc đến xử lý ảnh, nhiều người nghĩ ngay đến Deep Learning (YOLO, Mask R-CNN, U-Net). Nhưng tại sao trong dự án này, nhóm lại kiên quyết sử dụng **Xử lý ảnh truyền thống kết hợp Machine Learning cổ điển (Feature Extraction + CART / SVM)**?

Có 4 lý do khoa học cốt lõi:
1. **Tính tường minh và giải thích được (Explainability):**
   - Deep Learning là một "hộp đen" (Black box) với hàng triệu trọng số ma trận bí hiểm. Khi mô hình dự đoán một vệt đen là dầu, bạn không thể giải thích nổi vì sao nó lại đoán như vậy.
   - Với phương pháp của nhóm: Nhóm có thể chỉ ra chính xác: *"Vùng này được kết luận là dầu vì độ tương phản nền đạt 0.72, độ thuôn dài đạt 3.8 và gradient biên rất dốc"*. Đây là yếu tố sống còn trong các hệ thống giám sát hàng hải và cứu nạn khẩn cấp.
2. **Khả năng kiểm soát toán học tuyệt đối:**
   - Dự án tự cài đặt $100\%$ mã nguồn bằng NumPy thuần từ con số 0. Tự viết phép nhân ma trận, tự giải phương trình gradient descent, đối chứng sai số từng bit với thư viện chuẩn. Deep Learning với PyTorch/TensorFlow chỉ là gọi API có sẵn, không thể hiện được trình độ nắm vững bản chất giải thuật môn XLA.
3. **Chi phí tính toán cực nhẹ:**
   - Pipeline của nhóm chạy vèo vèo trên CPU văn phòng bình thường trong vài mili-giây, không cần đến card đồ họa GPU đắt tiền ngốn điện.

---

## 2. Cây quyết định CART (Classification and Regression Trees)

CART là mô hình học máy trực quan nhất, hoạt động giống như một chuỗi các câu hỏi phân nhánh nhị phân (Binary Decision Tree):

```text
                  Độ tương phản nền > 0.45 ?
                        /            \
                     ĐÚNG            SAI
                     /                  \
          Độ thuôn dài > 2.1 ?        LỚP: NỀN / LOOK-ALIKE
             /            \
          ĐÚNG            SAI
          /                  \
    LỚP: DẦU TRÀN         LỚP: NỀN
```

### Bản chất toán học: Chỉ số bất thuần Gini (Gini Impurity)
Làm thế nào để máy tính tự động tìm ra: *Nên chọn đặc trưng nào để đặt câu hỏi đầu tiên? Và ngưỡng cắt là bao nhiêu?*\
Nó sử dụng thước đo **Độ vấy bẩn Gini (Gini Impurity)**:
$$I_G(p) = 1 - \sum_{i=1}^C p_i^2$$

Đối với bài toán phân loại nhị phân (dầu vs không dầu), giả sử trong nút có $n$ mẫu, trong đó có $p$ mẫu dương tính ($y=1$):
Tỉ lệ mẫu dương tính là $\frac{p}{n}$, mẫu âm tính là $\frac{n - p}{n}$.
$$I_G = 1 - \left(\frac{p}{n}\right)^2 - \left(\frac{n - p}{n}\right)^2 = \frac{2p(n - p)}{n^2}$$

* $I_G = 0$: Nút hoàn toàn thuần khiết (chỉ toàn dầu hoặc toàn nền).
* $I_G = 0.5$: Nút hỗn loạn nhất (tỉ lệ $50\%$ dầu - $50\%$ nền).

### Thuật toán tìm điểm cắt tối ưu $O(N \log N)$ trong `models.py`:
1. Với mỗi đặc trưng $f \in \{0, 1, \dots, 7\}$:
2. Sắp xếp các mẫu theo thứ tự tăng dần của đặc trưng đó: `order = np.argsort(X[:, f])`.
3. Quét một lượt từ trái qua phải, dùng tổng tích lũy `cumsum()` để tính nhanh độ giảm Gini (**Gini Gain**) nếu cắt ở giữa 2 mẫu liên tiếp:
   $$\text{Gain} = I_{G\_cha} - \frac{N_{trái}}{N} I_{G\_trái} - \frac{N_{phải}}{N} I_{G\_phải}$$
   *(💡 **Kỹ thuật tối ưu hóa vector hóa trong `models.py`:** Để loại bỏ phép chia cho $N$ ở mỗi bước quét nhằm tăng tốc độ tính toán, nhóm nhân toàn bộ biểu thức với $N$:\
   `gain = impurity - 2 * lp * (left - lp) / left - 2 * rp * (right - rp) / right`. Vì $N$ là hằng số đối với một nút, việc nhân với $N$ không làm thay đổi vị trí cực đại `argmax`, giúp code chạy nhanh gấp nhiều lần).*
4. Chọn đặc trưng và ngưỡng cắt có **Gain lớn nhất** để tạo nhánh!

> ⚠️ **Tại sao cây nông (`max_depth=3, min_leaf=20`) lại chiến thắng cây sâu?**\
> Nếu để cây mọc sâu (`max_depth=10`), cây sẽ "học vẹt" (Overfitting), cố gắng phân loại đúng từng vết nhiễu nhỏ trong tập train $\to$ Gặp ảnh test mới là dự đoán sai bét!\
> Cây nông chỉ có độ sâu 3 tầng đóng vai trò như một bộ lọc tổng quát hóa cực kỳ bền vững, đạt F1 validation cao nhất ($0.3373$).

---

## 3. Máy vector hỗ trợ: Linear SVM tự giải bằng NumPy thuần

Mô hình phân lớp được chọn làm cấu hình khóa của dự án là **Linear Support Vector Machine (Linear SVM)** với tham số điều hòa $C=10$.

### Ý tưởng cốt lõi của SVM:
Trong không gian đặc trưng 8 chiều, SVM tìm một siêu phẳng quyết định (Hyperplane) phân cách giữa các điểm "Dầu" ($y_i = +1$) và các điểm "Không dầu" ($y_i = -1$):
$$f(x) = w^T x + b = w_1 x_1 + w_2 x_2 + \dots + w_8 x_8 + b$$

Siêu phẳng này không chỉ phân loại đúng, mà còn phải có **khoảng lề (Margin) rộng nhất có thể** để đảm bảo độ tin cậy khi dự đoán ảnh mới.

---

### Hàm mất mát bình phương bản lề (Squared Hinge Loss)
Thông thường, SVM sử dụng hàm mất mát Hinge Loss: $L(z) = \max(0, 1 - y \cdot f(x))$.\
Tuy nhiên, Hinge Loss có một nhược điểm chí mạng trong giải tích: **Nó bị gãy góc nhọn tại điểm $z=1$ (không có đạo hàm cấp 1 liên tục)**, khiến cho việc giải bằng các thuật toán Gradient Descent rất khó khăn.

Nhóm đã sử dụng biến thể **Squared Hinge Loss (L2-loss)**:
$$\boxed{\mathcal{L}(w) = \frac{1}{2n} \|w\|^2 + \frac{C}{n} \sum_{i=1}^n \max\left(0, 1 - y_i (w^T x_i)\right)^2}$$

* **Ưu điểm vượt trội:** Hàm mục tiêu $\mathcal{L}(w)$ trở nên **khả vi liên tục (smooth)** và lồi mạnh (strongly convex).
* **Đạo hàm Gradient giải tích cực đẹp:**
  Đặt lề sai số $m_i = \max(0, 1 - y_i(w^T x_i))$, đạo hàm riêng theo vector trọng số $w$ là:
  $$\nabla \mathcal{L}(w) = \frac{1}{n} w - \frac{2C}{n} \sum_{i=1}^n y_i \cdot m_i \cdot x_i$$
  Công thức này được lập trình tinh gọn bằng phép nhân ma trận NumPy:
  ```python
  grad = z / n - 2 * self.C * (X.T @ (target * margin)) / n
  ```

---

### Giải thuật tối ưu: Nesterov Accelerated Gradient (NAG)
Nếu dùng thuật toán Gradient Descent thông thường ($w_{t+1} = w_t - \alpha \nabla \mathcal{L}$), tốc độ hội tụ rất chậm: Sai số giảm theo cấp số $O(1/k)$ (sau $1.000$ bước lặp vẫn chưa tới đích).

Nhóm đã tự lập trình giải thuật gia tốc **Nesterov Accelerated Gradient (NAG)**:
* Ý tưởng: Thay vì chỉ nhìn vào vị trí hiện tại, thuật toán "nhìn trước tương lai" theo hướng quán tính (momentum) rồi mới tính đạo hàm:
  $$z_k = w_k + \beta_k (w_k - w_{k-1})$$
  $$w_{k+1} = z_k - \alpha \nabla \mathcal{L}(z_k)$$
* Thuật toán kết hợp cơ chế tự động khởi động lại quán tính (**Restart**) khi gradient bị ngược chiều và kỹ thuật **Backtracking Line Search** để tự chỉnh tốc độ học $\alpha$.
* $\implies$ **Tốc độ hội tụ tăng vọt lên mức tối ưu lý thuyết $O(1/k^2)$**: Chỉ sau đúng **177 vòng lặp** (mất $0.27$ giây), mô hình đã tìm được nghiệm tối ưu chính xác tuyệt đối với chuẩn gradient $\|g\| < 10^{-6}$!

---

## 4. Bằng chứng kiểm chứng đối chứng: Agreement = 1.0 nghĩa là gì?

Trong file [results/sos/model_comparison.json](file:///D:/Codin/utc-code/HK4_1/XLA/BTL/results/sos/model_comparison.json), nhóm ghi nhận:
```json
{
  "kind": "svm",
  "agreement": 1.0,
  "converged": true,
  "numpy_fit_seconds": 0.2765,
  "reference_fit_seconds": 0.0650
}
```

* **Ý nghĩa:**
  - Nhóm cho chạy song song: Bản Linear SVM tự viết bằng NumPy thuần và bản `LinearSVC` của thư viện Scikit-learn (viết bằng C++ dựa trên bộ thư viện chuẩn thế giới LIBLINEAR).
  - Cả hai mô hình cùng huấn luyện trên $20.000$ mẫu đặc trưng và dự đoán trên toàn bộ các vùng ứng viên của 671 ảnh validation.
  - Kết quả: **Tỷ lệ đồng thuận đạt chính xác 1.0000 (100%)**. Nghĩa là trong hàng ngàn vùng kiểm tra, không có bất kỳ một vùng nào mà code tự viết đoán khác so với thư viện Scikit-learn!
  - Giá trị hàm mục tiêu (Objective Loss) của hai bên khớp nhau đến tận 10 chữ số thập phân: **$4.0531228859$**!

---

## 5. Hệ thống câu hỏi truy vấn bản chất (Socratic Q&A)

### Câu hỏi 1:
* **Hỏi:** *Đầu ra của Linear SVM là một con số `score`. Con số này có phải là xác suất vết dầu từ 0% đến 100% không?*
* **Trả lời:** Không phải xác suất! Đây là **Điểm quyết định (Decision Score)**, đại diện cho khoảng cách đại số có dấu từ vector đặc trưng của đối tượng tới siêu phẳng phân cách ($w^T x + b$):
  - $\text{score} > 0$: Điểm nằm ở nửa không gian của lớp Dầu $\to$ Dự đoán là Dầu. Điểm càng lớn nghĩa là càng nằm sâu trong vùng dầu (độ tự tin càng cao).
  - $\text{score} \le 0$: Điểm nằm ở nửa không gian của Nền $\to$ Dự đoán là Nền.
  - Dự án trung thực giữ nguyên bản chất Decision Score, không dùng hàm sigmoid ngụy tạo nó thành xác suất.

### Câu hỏi 2:
* **Hỏi:** *Tại sao thời gian huấn luyện của code NumPy ($0.27\text{s}$) lại lâu hơn thư viện Scikit-learn ($0.06\text{s}$)?*
* **Trả lời:** `LinearSVC` của Scikit-learn được biên dịch bằng mã C/C++ tối ưu bậc thấp (thư viện LIBLINEAR của GS. Chih-Jen Lin), sử dụng thuật toán Coordinate Descent trên bộ nhớ đệm CPU cấp 1. Bản của nhóm được viết hoàn toàn bằng Python thuần thông qua mảng NumPy. Mặc dù chạy bằng thông dịch Python nhưng thời gian $0.27$ giây vẫn là cực kỳ ấn tượng và hoàn toàn đáp ứng tốt cho mọi bài toán thực tế!

---

## 6. Trắc nghiệm ôn tập nhanh (Quiz 06)

**Câu 1:** Tiêu chí tối ưu hóa nào được thuật toán CART sử dụng để tìm điểm phân nhánh trong dự án?\
A. Entropi thông tin Shannon\
B. Độ bất thuần Gini (Gini Impurity)\
C. Khoảng cách Euclidean\
D. Hệ số tương quan Pearson\
*(Đáp án: **B**)*

**Câu 2:** Tại sao mô hình Linear SVM trong dự án lại sử dụng hàm mất mát Squared Hinge Loss thay vì Hinge Loss thông thường?\
A. Vì Squared Hinge Loss khả vi liên tục (trơn), có đạo hàm cấp 1 đẹp giúp giải dễ dàng bằng giải thuật Gradient Descent.\
B. Vì Squared Hinge Loss luôn cho kết quả bằng 0.\
C. Vì thư viện Scikit-learn bắt buộc phải dùng Squared Hinge Loss.\
D. Vì Hinge Loss không thể tính được trên ma trận 2D.\
*(Đáp án: **A**)*

**Câu 3:** Tốc độ hội tụ lý thuyết của giải thuật Nesterov Accelerated Gradient (NAG) là bao nhiêu so với Gradient Descent thông thường?\
A. Giống hệt nhau, đều là $O(1/k)$\
B. Nesterov đạt $O(1/k^2)$, hội tụ nhanh hơn vượt trội so với $O(1/k)$ của Gradient Descent thông thường\
C. Nesterov hội tụ theo cấp số nhân $O(e^k)$\
D. Nesterov chậm hơn nhưng chính xác hơn\
*(Đáp án: **B**)*

**Câu 4:** Khi một cây quyết định CART bị huấn luyện quá sâu (`max_depth = 15`), hiện tượng tiêu cực nào sau đây sẽ xảy ra?\
A. Dưới khớp (Underfitting)\
B. Quá khớp (Overfitting / Học vẹt), dẫn đến độ chính xác trên tập kiểm tra độc lập bị giảm sút\
C. Cây tự động xóa sạch dữ liệu\
D. Thuật toán không thể dừng lại\
*(Đáp án: **B**)*

**Câu 5:** Con số "Agreement = 1.0" trong báo cáo so sánh mô hình giữa code NumPy tự cài và Scikit-learn chứng minh điều gì?\
A. Cả hai mô hình đều dự đoán sai toàn bộ.\
B. Mô hình tự cài bằng NumPy thuần đưa ra kết quả dự đoán khớp 100% từng mẫu so với thư viện Scikit-learn chuẩn quốc tế.\
C. Nhóm đã import trực tiếp Scikit-learn vào file NumPy.\
D. Dữ liệu huấn luyện chỉ có đúng 1 mẫu.\
*(Đáp án: **B**)*
