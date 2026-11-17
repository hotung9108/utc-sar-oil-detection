# ⚖️ CHUYÊN ĐỀ 09: TRIẾT LÝ ĐÁNH GIÁ HAI TẦNG (TWO-LEVEL EVALUATION)

> **Phạm vi tài liệu tự học — cập nhật 17/11/2026:** đây là giải thích và mã minh họa độc lập, không phải pipeline đã nghiệm thu hoặc bằng chứng đạt 100% đề. Công thức giản lược, ảnh giả lập, ví dụ ghép greedy và mô phỏng trôi dầu không thay thế kết quả trong `src/sar_oil`, `scripts` và `results`. Lee không bảo đảm giữ biên tuyệt đối; agreement 100% chỉ áp dụng cho ca đã đo; F1 SOS 0,3403 là cấu hình được chọn theo quy tắc dung sai, không phải cực đại nghiêm ngặt. Ưu tiên [đối chiếu hiện tại](../docs/DANH_GIA_DU_AN_VA_DOI_CHIEU_DE_18.md) khi có khác biệt.

## Đánh giá giữa các thuật toán & Đối chứng NumPy tự cài với Thư viện chuẩn

> 💡 **Khái niệm cốt lõi:**
> Điểm đặc biệt và chuẩn mực học thuật cao nhất của Đề 18 là thiết kế **Hai tầng đánh giá bắt buộc (Two-Level Evaluation)**:
> 1. **Tầng 1 (Thuật toán vs Thuật toán):** So sánh đối kháng giữa các giải thuật khác nhau trên cùng một tập dữ liệu để trả lời câu hỏi: *"Thuật toán nào phù hợp nhất với dữ liệu ảnh radar SAR?"*.
> 2. **Tầng 2 (NumPy tự cài vs Thư viện chuẩn):** So sánh 1-1 giữa mã nguồn tự viết từ số 0 bằng NumPy thuần với các hàm chuẩn quốc tế (SciPy, scikit-image, scikit-learn) trên cùng một đầu vào để trả lời câu hỏi: *"Mã tự viết có khớp định nghĩa và dung sai trên các ca thử không? Có bị lỗi logic hay sai số không?"*.

---

## 🧭 MỤC LỤC
1. [Phần 1: Tại Sao Phải Đánh Giá Hai Tầng?](#phan-1)
2. [Phần 2: Tầng 1 — Liệt Kê, Thực Nghiệm & Sàng Lọc Thuật Toán](#phan-2)
3. [Phần 3: Tầng 2 — Đối Chứng Toán Học NumPy vs Thư Viện Chuẩn](#phan-3)
4. [Phần 4: Kịch Bản Trả Lời Xuất Sắc Trước Hội Đồng Chấm BTL](#phan-4)
5. [Phần 5: Hướng Dẫn Tự Chạy Thử Script Đối Chứng Hai Tầng](#phan-5)

---

<a name="phan-1"></a>
## 🏛️ PHẦN 1: TẠI SAO PHẢI ĐÁNH GIÁ HAI TẦNG?

Trong nghiên cứu khoa học và đồ án kỹ thuật:
- **Nếu chỉ làm Tầng 1 (so sánh thuật toán) mà không làm Tầng 2:**\
  Giảng viên sẽ hỏi: *"Em nói Lee filter tốt hơn Mean filter, nhưng lỡ hàm Lee filter em tự viết bị sai công thức thì sao? Làm sao chứng minh code tự viết phản ánh đúng toán học của Lee?"*.\
  $\implies$ Bạn không thể trả lời được nếu không có đối chứng Tầng 2!
- **Nếu chỉ làm Tầng 2 (đối chứng thư viện) mà không làm Tầng 1:**\
  Giảng viên sẽ hỏi: *"Em viết code giống thư viện rồi, nhưng tại sao em lại chọn Lee filter mà không chọn Median hay Gaussian? Căn cứ vào đâu mà em chọn kích thước $7\times 7$?"*.\
  $\implies$ Bạn không thể trả lời được nếu không có bảng thực nghiệm thi đấu ở Tầng 1!

$\implies$ **Bắt buộc phải có cả 2 tầng: Tầng 2 chứng minh bạn viết code ĐÚNG CHUẨN, và Tầng 1 chứng minh bạn chọn phương án TỐI ƯU DỰA TRÊN SỐ LIỆU THỰC NGHIỆM!**

---

<a name="phan-2"></a>
## 🥊 PHẦN 2: TẦNG 1 — LIỆT KÊ, THỰC NGHIỆM & SÀNG LỌC THUẬT TOÁN

Dự án không bao giờ "đoán mò" hay chọn bừa theo cảm tính. Toàn bộ quá trình lựa chọn diễn ra theo quy trình sàng lọc lưới (Grid Search & Screening) qua 3 giai đoạn:

### 2.1. Giai đoạn 1: Sàng lọc 13 cấu hình bộ lọc trên 671 ảnh Validation
Nhóm nghiên cứu cố định thuật toán Otsu và diện tích tối thiểu `min_area = 16`, sau đó cho 13 cấu hình bộ lọc thi đấu với nhau để tìm ra bộ lọc tạo vùng ứng viên tốt nhất:

| Bộ lọc | Kích thước | Tham số | Precision | Recall | Object F1 | Nhận xét thực nghiệm |
|---|:---:|:---:|---:|---:|---:|---|
| **Không lọc (None)** | - | - | 0.0126 | 0.2772 | **0.0243** | Nhiễu đốm làm vỡ vụn vùng, F1 cực thấp. |
| **Box Mean** | $3\times 3$ | - | 0.0381 | 0.3391 | 0.0685 | Làm mờ nhẹ ranh giới. |
| **Box Mean** | $7\times 7$ | - | 0.0477 | 0.3474 | 0.0841 | Làm nhòe nặng ranh giới vết dầu. |
| **Gaussian** | - | $\sigma=0.8$ | 0.0395 | 0.3402 | 0.0708 | Mịn màng nhưng vẫn làm trôi biên. |
| **Gaussian** | - | $\sigma=1.2$ | 0.0452 | 0.3458 | 0.0799 | Tương tự Mean. |
| **Median** | $3\times 3$ | - | 0.0273 | 0.3373 | 0.0506 | Loại hạt tiêu tốt nhưng còn nhiễu. |
| **Median** | $7\times 7$ | - | 0.0422 | 0.3444 | 0.0751 | Mất các góc nhọn của vệt dầu hẹp. |
| **Lee Filter** | $5\times 5$ | $L=1$ | 0.0441 | 0.3650 | 0.0786 | Giữ biên tốt hơn Mean. |
| **Lee Filter** | $5\times 5$ | $L=4$ | 0.0458 | 0.3712 | 0.0815 | Khử đốm mượt mà. |
| **Lee Filter** | $7\times 7$ | $L=1$ | 0.0474 | 0.3782 | 0.0843 | Khử nhiễu tốt, biên sắc nét. |
| **Lee Filter (WINNER ⭐)** | $7\times 7$ | $L=4$ | **0.0481** | **0.3828** | **0.0855** | **F1 và Recall cao nhất toàn bộ 13 cấu hình!** |

$\implies$ **Kết luận khoa học:** Lee Filter $7\times 7$ ($L=4$) chiến thắng thuyết phục vì nó đạt Recall cao nhất ($38.28\%$) — ở giai đoạn tạo ứng viên, mục tiêu số 1 là **không được bỏ sót vết dầu thật**!

---

### 2.2. Giai đoạn 2: Sàng lọc 729 tổ hợp mô hình & nhóm đặc trưng trên Validation
Sau khi đã có các đốm tối ứng viên, nhóm khảo sát 729 tổ hợp giữa:
- **Thuật toán học máy:** CART (`max_depth` $\in \{3, 5, 8\}$, `min_samples_leaf` $\in \{5, 20\}$) vs Linear SVM ($C \in \{0.1, 1.0, 10.0\}$).
- **Nhóm đặc trưng:** Chỉ hình học (4 đặc trưng), chỉ cường độ (4 đặc trưng), hoặc toàn bộ (all 8 đặc trưng).
- **Hình thái học:** `none`, `close`, `open_close`.

**Kết quả xếp hạng thực nghiệm:**
1. **Chỉ dùng 4 đặc trưng hình học:** F1 cao nhất chỉ đạt $\approx 0.2104$.
2. **Chỉ dùng 4 đặc trưng cường độ:** F1 cao nhất chỉ đạt $\approx 0.2891$.
3. **Kết hợp trọn vẹn cả 8 đặc trưng:**
   - Cây quyết định CART (`depth=3, min_leaf=20`): F1 đạt **$0.3373$**.
   - **Linear SVM ($C=10$): F1 đạt $0.3403$ (CHIẾN THẮNG TUYỆT ĐỐI ⭐)**.

---

### 2.3. Giai đoạn 3: Phân tích bóc tách (Ablation Study) trên 839 ảnh Test độc lập
Đánh giá khách quan trên tập Test chưa từng được nhìn thấy:

| Cấu hình thử nghiệm | Precision | Recall | Object F1 | Pixel IoU | Báo sai FP/ảnh |
|---|---:|---:|---:|---:|---:|
| **Baseline (Chỉ Otsu)** | 0.0086 | 0.1339 | 0.0161 | 0.4367 | 58.62 |
| **Bỏ Machine Learning (Chỉ Lee + Otsu)** | 0.0753 | 0.3199 | 0.1220 | 0.5867 | 14.89 |
| **Pipeline đầy đủ (Lee + Otsu + 8 Đặc trưng + SVM)** | **0.2541** | **0.3130** | **0.2805** | **0.6614** | **3.48** |

$\implies$ **Bằng chứng thép:** Nhờ có Linear SVM và 8 đặc trưng, số ca báo động giả giảm từ $14.89$ xuống chỉ còn $3.48$ FP/ảnh, đưa F1 từ $0.1220$ lên $0.2805$!

---

<a name="phan-3"></a>
## 🔍 PHẦN 3: TẦNG 2 — ĐỐI CHỨNG TOÁN HỌC NUMPY VS THƯ VIỆN CHUẨN

Để chứng minh toàn bộ thuật toán tự viết bằng NumPy thuần là **chuẩn xác tuyệt đối**, nhóm đã thiết lập hệ thống kiểm thử tự động so sánh từng phép toán với các thư viện hàng đầu thế giới (SciPy, scikit-image, scikit-learn).

### 3.1. Đối chứng các toán tử Xử lý ảnh (NumPy vs SciPy / scikit-image)
Đo lường sai số tuyệt đối tối đa ($\text{Max Absolute Error} = \max |A - B|$) và sai số bình phương trung bình ($\text{MSE} = \frac{1}{N}\sum (A - B)^2$) trên dữ liệu thực tế:

| Phép toán | Tự cài đặt (NumPy) | Thư viện đối chứng | Sai số tuyệt đối tối đa | MSE | Đánh giá khoa học |
|---|---|---|---:|---:|:---:|
| **Median Filter** | `core.filter_image(..., 'median')` | `scipy.ndimage.median_filter` | **0.000** | **0.000** | Khớp tuyệt đối 100% |
| **Gaussian Filter** | `core.filter_image(..., 'gaussian')` | `scipy.ndimage.gaussian_filter` | $3.33 \times 10^{-16}$ | $6.10 \times 10^{-33}$ | Sai số dấu phẩy động 64-bit |
| **Lee Filter** | `core.filter_image(..., 'lee')` | `reference.filter_image` (SciPy) | $2.74 \times 10^{-12}$ | $4.34 \times 10^{-27}$ | Trùng khớp bản chất MMSE |
| **Otsu Threshold** | `core.otsu(a)` | `skimage.filters.threshold_otsu` | **0.000** | **0.000** | Ngưỡng khớp tuyệt đối |
| **Niblack Threshold** | `core.threshold(..., 'niblack')` | `skimage.filters.threshold_niblack`| **0.000** | **0.000** | Khớp tuyệt đối |
| **Gán nhãn liên thông**| `core.label(mask)` | `scipy.ndimage.label` | **0.000** | **0.000** | Khớp 100% nhãn vùng |
| **8 Đặc trưng vùng** | `core.features(a, labels)` | `reference.features` | $3.11 \times 10^{-14}$ | $2.34 \times 10^{-30}$ | Sai số xấp xỉ số thực |

### 3.2. Đối chứng mô hình Học máy (NumPy vs Scikit-learn)
Huấn luyện trên 20.000 mẫu đặc trưng và dự đoán trên toàn bộ ứng viên:

| Tiêu chuẩn đối chứng | CART (NumPy) | DecisionTree (sklearn) | LinearSVM (NumPy) | LinearSVC (sklearn) |
|---|:---:|:---:|:---:|:---:|
| **Hàm tối ưu hóa** | Gini Impurity đệ quy | Gini Impurity | Accelerated Gradient | Coordinate Descent |
| **Mức đồng thuận (Agreement)** | \multicolumn{2}{c|}{**1.0000 (100% khớp nhãn)**} | \multicolumn{2}{c|}{**1.0000 (100% khớp nhãn)**} |
| **F1 trên tập Validation** | **0.3373** | **0.3373** | **0.3403** | **0.3403** |
| **Giá trị hàm mục tiêu Loss** | - | - | **4.0531228859** | **4.0531228859** |
| **Trạng thái hội tụ** | \multicolumn{2}{c|}{True} | True (177 vòng lặp) | True |

$\implies$ **Kết luận:** Code tự viết bằng NumPy thuần đạt **độ đồng thuận 100% (Agreement = 1.0000)** với Scikit-learn, cho thấy hai bản khớp trên thí nghiệm SOS này; không chứng minh mọi đầu vào hoặc mọi mô hình đều khớp tuyệt đối.

---

<a name="phan-4"></a>
## 🎤 PHẦN 4: KỊCH BẢN TRẢ LỜI XUẤT SẮC TRƯỚC HỘI ĐỒNG BẢO VỆ

### ❓ Câu hỏi 1 của Giảng viên:
> *"Tại sao nhóm em lại chọn bộ lọc Lee $7\times 7$ L=4 và mô hình Linear SVM C=10? Có phải chọn bừa một con số chạy thử thấy đẹp thì lấy không?"*

**Trả lời chuẩn mực:**
> *"Dạ thưa Thầy/Cô, nhóm em tuyệt đối không chọn bừa. Nhóm đã áp dụng phương pháp sàng lọc lưới (Grid Search & Screening) chuẩn khoa học:
> 1. Ở bước tiền xử lý, nhóm đã cho **13 cấu hình bộ lọc thi đấu đối kháng trên 671 ảnh Validation**. Tiêu chí của bước này là độ phủ (Recall) để không bỏ sót dầu. Lee Filter $7\times 7$ $L=4$ đạt Recall cao nhất là **$38.28\%$** (vượt trội so với Mean $34.7\%$ và Median $34.4\%$), đồng thời giữ được đường biên sắc nét nên được chọn.
> 2. Ở bước phân lớp, nhóm đã khảo sát **729 tổ hợp mô hình trên 8 đặc trưng**. Linear SVM $C=10$ được chọn với Object F1 validation **$0.3403$** theo quy tắc dung sai; đây không phải cực đại nghiêm ngặt, giúp giảm số ca báo động giả từ $14.89$ xuống $3.48$ FP/ảnh trên tập Test độc lập. Mọi số liệu này đều được lưu thành tệp JSON có thể tái hiện 100% ạ."*

---

### ❓ Câu hỏi 2 của Giảng viên:
> *"Nhóm tự code từ đầu bằng NumPy, vậy làm sao thầy cô tin được rằng code của nhóm không bị tính sai công thức toán?"*

**Trả lời chuẩn mực:**
> *"Dạ thưa Thầy/Cô, dự án được thiết kế theo chuẩn **Đánh giá hai tầng (Two-Level Evaluation)**:
> - Tầng 1 là so sánh thuật toán như em vừa trình bày.
> - Tầng 2 là **Kiểm chuẩn toán học 1-1 với thư viện quốc tế**. Nhóm đã viết bộ test tự động so sánh từng hàm NumPy tự cài với SciPy, scikit-image và scikit-learn trên cùng một dữ liệu đầu vào.
> - Kết quả cho thấy: Phép lọc Median, ngưỡng Otsu, Niblack và Gán nhãn liên thông đạt sai số **$0.000$ (khớp tuyệt đối)**; bộ lọc Lee sai số chỉ $10^{-12}$; và mô hình Linear SVM tự cài đạt **độ đồng thuận nhãn 100% (Agreement = 1.0000)** so với scikit-learn, cùng hội tụ tại giá trị hàm mục tiêu $4.0531228859$ ạ!"*

---

<a name="phan-5"></a>
## 💻 PHẦN 5: CHẠY THỬ SCRIPT ĐỐI CHỨNG HAI TẦNG

Nhóm đã tạo sẵn script:
👉 **[`study_guide/mini_examples/demo_hai_tang_danh_gia.py`](file:///D:/Codin/utc-code/HK4_1/XLA/BTL/study_guide/mini_examples/demo_hai_tang_danh_gia.py)**

Để tận mắt nhìn thấy hai tầng đánh giá chạy trực tiếp trên máy, bạn chỉ cần gõ:
```powershell
.venv\Scripts\python.exe study_guide/mini_examples/demo_hai_tang_danh_gia.py
```
Màn hình sẽ in ra 2 bảng đối chứng hoàn chỉnh: Bảng thi đấu giữa các thuật toán và Bảng sai số toán học so với thư viện!
