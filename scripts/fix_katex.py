"""Fix all KaTeX parse errors and markdown formatting in 06_algorithm_research_review.ipynb."""

import nbformat

NB_PATH = "notebooks/06_algorithm_research_review.ipynb"
nb = nbformat.read(NB_PATH, as_version=4)

# Define clean Markdown for all markdown cells

md_cell_0 = r"""# 06 · Nghiên cứu & Đánh giá Thuật toán Phát hiện Vết Dầu Loang SAR
### Báo cáo Nghiên cứu Thực nghiệm Độc lập & Chẩn đoán Vi mô (Independent Academic Review & Diagnostics)

> [!IMPORTANT]
> **Tuyên bố Tính Độc Lập Thực Nghiệm (Self-Contained & Fully Reproducible):**
> Notebook này được xây dựng độc lập hoàn toàn với các file kết quả chạy trước trong `results/sos/` (như `selected.json`, `svm_model.json`, `evaluation.json`) và không phụ thuộc trạng thái bộ nhớ của các notebook khác.
> - **Nguồn dữ liệu:** Nạp trực tiếp từ dataset ảnh thực tế `D:\Coding\Oil_Spill_Detection\Dataset\SOS` (gồm cả Sentinel-1 C-band và ALOS PALSAR L-band).
> - **Khảo sát & Tối ưu:** Tự đối sánh các bộ lọc/thuật toán phân ngưỡng, tự trích xuất 8 đặc trưng vùng, tự huấn luyện mới từ đầu (from scratch) mô hình `CART` và `LinearSVM` bằng NumPy.
> - **Chẩn đoán vi mô:** Giải phẫu chi tiết nguyên nhân thuật toán đạt Pixel IoU cao (~0.66) nhưng Object F1 khiêm tốn (~0.28), giải thích bộ trọng số SVM học được, chứng minh trực quan các bẫy thuật toán (bẫy Otsu trên ảnh lệch lớp, bẫy vành đai nền 5 pixel, bẫy phạt phân mảnh đối tượng), và thử nghiệm giải pháp cải tiến (Proof-of-Concept) ngay trên các mẫu lỗi.
"""

md_cell_2 = r"""## 1. Cơ sở Lý thuyết & Mô hình Toán học của Pipeline

Thuật toán phát hiện vết dầu loang SAR đang khảo sát thuộc lớp phương pháp kết hợp **Xử lý ảnh hình thái học & Bức xạ cổ điển** với **Học máy nhẹ theo vùng (Region-based Machine Learning)**:

```
Ảnh SAR thô I(x, y) ──> [1. Khử nhiễu Lee] ──> I_f ──> [2. Ngưỡng Otsu] ──> Mặt nạ nhị phân
                              │
  [4. Trích 8 Đặc trưng] <────┴────────────── [3. Lọc diện tích & CCL] <──┘
           │
           ▼
     Vector X ∈ R^8  ──> [5. Phân loại LinearSVM / CART] ──> Mặt nạ dầu cuối cùng (score > 0)
```

### 1.1. Bộ lọc khử nhiễu đốm Lee MMSE (Minimum Mean Square Error)
Nhiễu đốm (speckle noise) trong ảnh SAR hình thành do sự giao thoa tán xạ kết hợp, được mô hình hóa theo dạng nhân: $I(x, y) = R(x, y) \cdot u(x, y)$, với $u \sim \Gamma(L, 1/L)$. Bộ lọc Lee xấp xỉ tuyến tính hóa cục bộ:
$$\hat{R}(x, y) = m(x, y) + W(x, y) \cdot [I(x, y) - m(x, y)]$$
trong đó $m(x,y)$ là trung bình cục bộ, $v(x,y)$ là phương sai cục bộ, $\sigma_u^2 = 1/L$ là phương sai nhiễu, và trọng số thích nghi $W(x, y)$ xác định bởi:
$$W(x, y) = \max\left(0, \frac{v(x, y) - \frac{m(x, y)^2}{L}}{\max(v(x, y), 10^{-12})}\right)$$

- Ở vùng mặt biển bằng phẳng ($v \approx m^2/L \implies W \to 0$): đầu ra được làm trơn về trung bình $m$.
- Ở vùng có biên chuyển tiếp hoặc cạnh vết dầu ($v \gg m^2/L \implies W \to 1$): đầu ra giữ lại chi tiết cạnh gốc.
- **Tối ưu hóa độ phức tạp:** Triển khai bằng Bảng tổng tích lũy (Summed-Area Table / Integral Image), tính $m$ và $v$ với chi phí cố định $\mathcal{O}(HW)$ không phụ thuộc kích thước cửa sổ.

### 1.2. Phân ngưỡng toàn cục Otsu & Chỉ số phân tách $\eta$
Otsu phân tách histogram 256 bin thành 2 lớp (dầu loang $\omega_0$ và nền biển $\omega_1$) bằng cách cực đại hóa phương sai giữa hai lớp:
$$t^* = \arg\max_{t} \sigma_B^2(t), \quad \sigma_B^2(t) = \omega_0(t) \omega_1(t) [\mu_0(t) - \mu_1(t)]^2$$
Chỉ số phân tách hai đỉnh $\eta \in [0, 1]$ đo lường độ rõ nét của hai cụm:
$$\eta = \frac{\sigma_B^2(t^*)}{\sigma_T^2}$$
*Giới hạn lý thuyết quan trọng:* Otsu giả định histogram có hai đỉnh rõ rệt. Khi diện tích dầu quá nhỏ ($< 5\%$) hoặc patch ngập trọn trong dầu ($100\%$), giả định này sụp đổ.

### 1.3. Không gian 8 đặc trưng vùng
Thay vì phân lớp từng pixel, thuật toán gom nhóm các thành phần liên thông 8 hướng (Run-Length Union-Find) và trích xuất 8 đặc trưng:
1. $f_0$ (`area_fraction`): Tỷ lệ diện tích vùng so với toàn ảnh $A / (HW)$.
2. $f_1$ (`elongation`): Độ thuôn dài từ hai trị riêng hiệp phương sai tọa độ $\sqrt{(\lambda_2 + \epsilon)/(\lambda_1 + \epsilon)}$.
3. $f_2$ (`extent`): Độ đặc so với bounding box $A / (\Delta x \cdot \Delta y)$.
4. $f_3$ (`complexity`): Tỷ số chu vi-diện tích $P^2 / (4\pi A)$ (chu vi đếm theo cạnh lưới).
5. $f_4$ (`mean`): Cường độ trung bình $\mu_{\mathrm{slick}}$ bên trong vùng trên ảnh đã lọc.
6. $f_5$ (`std`): Độ lệch chuẩn cường độ nội vùng.
7. $f_6$ (`boundary_gradient`): Độ dốc biên trung bình từ toán tử Sobel chuẩn hóa.
8. $f_7$ (`background_contrast`): Độ tương phản so với vành đai nền 5 pixel ngoài biên:
$$C_{\mathrm{contrast}} = \frac{\mu_{\mathrm{bg}} - \mu_{\mathrm{slick}}}{|\mu_{\mathrm{bg}}| + \epsilon}$$

### 1.4. Bộ phân loại Linear Squared-Hinge SVM
Tối ưu hóa hàm mục tiêu lồi khả vi cấp một:
$$\min_{\mathbf{w}} J(\mathbf{w}) = \frac{1}{2n}\|\mathbf{w}\|_2^2 + \frac{C}{n}\sum_{i=1}^n \max\left(0, 1 - y_i (\mathbf{x}_i^T \mathbf{w})\right)^2, \quad y_i \in \{-1, +1\}$$
Giải bằng thuật toán **Nesterov Accelerated Gradient** với cơ chế *adaptive restart* và *backtracking line search*.
"""

md_cell_5 = r"""## 2. Thực nghiệm Đối sánh Bộ lọc & Phân ngưỡng Trực tiếp (Live Benchmarking)

Để kiểm chứng xem sự kết hợp giữa **Bộ lọc khử đốm** và **Thuật toán phân ngưỡng** ảnh hưởng thế nào đến chất lượng phát hiện vùng ứng viên ban đầu (Candidate Generation), ta chạy trực tiếp một lưới thử nghiệm đối sánh gồm 6 cấu hình lọc:
- `none` (Không lọc — ảnh gốc)
- `median 5×5` (Lọc trung vị phi tuyến)
- `gaussian σ=1.2` (Lọc Gauss tuyến tính)
- `lee 5×5 (L=4)` (Lọc thích nghi MMSE kích thước 5)
- `lee 7×7 (L=4)` (Lọc thích nghi MMSE kích thước 7 — cấu hình mặc định của pipeline)
- `mean 7×7` (Lọc trung bình hộp cùng kích thước cửa sổ 7×7)

kết hợp với 2 họ phân ngưỡng:
- **Ngưỡng toàn cục Otsu** (`otsu`)
- **Ngưỡng thích nghi cục bộ Niblack** (`niblack`, cửa sổ trượt $51\times 51$, hệ số $k=0.2$).

*Mục tiêu đo lường:* Khảo sát sự đánh đổi cốt lõi trong xử lý ảnh viễn thám:
1. Bộ lọc làm trơn càng mạnh $\implies$ giảm nhiễu hạt mặt biển $\implies$ giảm số lượng ứng viên giả (`FP`).
2. Nhưng cửa sổ lọc quá lớn $\implies$ nhòe biên và đứt gãy các vệt dầu mảnh $\implies$ tăng số lượng bỏ sót (`FN`).
"""

md_cell_7 = r"""## 3. Giải phẫu Từng bước Xử lý & Kiểm toán Mất mát Thông tin (Step-by-Step Dissection)

Mỗi giai đoạn trong pipeline đều có thể làm **biến dạng hoặc thất thoát thông tin** của vết dầu:
1. **Khâu lọc Lee:** Trọng số thích nghi $W(x, y) = \max(0, (v - m^2/L)/v)$ kiểm soát việc làm mờ hay giữ biên. Nếu vết dầu quá hẹp, phương sai cục bộ $v$ không đủ lớn, khiến $W \to 0$ và vết dầu bị "hòa tan" vào nền biển.
2. **Khâu phân ngưỡng Otsu:** Cắt nhị phân toàn cục. Với các vết dầu có gradien biên thoai thoải, Otsu chỉ bắt được phần lõi tối nhất, làm co ngót diện tích dầu thật.
3. **Khâu loại bỏ diện tích nhỏ (`min_area=64`):** Triệt tiêu đốm nhiễu mặt biển nhưng cũng xóa sổ các vệt dầu nhỏ độc lập.
4. **Khâu phân loại vùng SVM:** Chỉ có chức năng gán nhãn loại bỏ (pruning), không thể phục hồi pixel đã mất hoặc hàn gắn vết dầu bị đứt gãy.

Dưới đây là hình ảnh giải phẫu trực tiếp 6 lớp của 4 ca bệnh kinh điển:
- `sentinel_0.png`: Ca thành công điển hình (vết dầu lớn, tương phản mạnh).
- `sentinel_25.png`: Ca dải dầu mảnh, bị phân mảnh thành nhiều mảnh nhỏ.
- `sentinel_1.png`: Ca dầu nhỏ nội vùng (Otsu sụp đổ do tỷ lệ dầu $< 5\%$).
- `sentinel_440.png`: Ca patch 100% ngập dầu (Otsu tự cắt đôi phân phối nội tại của vết dầu).
"""

md_cell_9 = r"""## 4. Trích xuất 8 Đặc trưng Vùng & Huấn luyện Mới `CART` / `LinearSVM` từ đầu

Trong phần này, ta **huấn luyện trực tiếp từ đầu** cả hai mô hình phân loại vùng:
- **`CART`**: Cây quyết định nhị phân tối ưu hóa độ vẩn đục Gini (`max_depth=3`, `min_leaf=5`).
- **`LinearSVM`**: SVM tuyến tính tối ưu hóa Squared-Hinge Loss với điều chuẩn $L_2$ ($C=10.0$) giải bằng Nesterov Accelerated Gradient.

### Giao thức trích xuất & gán nhãn đối tượng (Ground Truth Labeling Protocol)
1. Chạy sinh vùng ứng viên trên tập `train_subset` ($N=100$ ảnh Sentinel-1 lấy trực tiếp từ `SOS/train`).
2. Với mỗi vùng ứng viên $R_i$, tính độ tinh khiết so với nhãn tham chiếu ground truth:
$$\mathrm{Purity}(R_i) = \frac{|R_i \cap \mathrm{GT}|}{|R_i|}$$
   - Nếu $\mathrm{Purity}(R_i) \ge 0.50$: Gán nhãn Dương (Vết dầu, $y_i = 1$).
   - Nếu $\mathrm{Purity}(R_i) \le 0.05$: Gán nhãn Âm (Vùng tối giả / Nền biển, $y_i = 0$).
   - Các vùng trung gian ($0.05 < \mathrm{Purity} < 0.50$): Bỏ qua trong huấn luyện để tránh nhiễu nhãn.
3. Chuẩn hóa Z-score trực tiếp trên các đặc trưng đã trích xuất:
$$z_k = \frac{x_k - \mu_k}{\sigma_k}, \quad k = 0, \dots, 7$$
4. Đánh giá sự hội tụ và vẽ đồ thị hàm mất mát / gradient cũng như phân rã trọng số siêu phẳng phân tách $w_k$.
"""

md_cell_11 = r"""## 5. Đánh giá Toàn diện Độc lập & Phân tích Nguyên nhân Lỗi

Trong phần này, ta đánh giá mô hình vừa huấn luyện trên tập mẫu kiểm định `val_subset` (gồm cả Sentinel-1 C-band và ALOS PALSAR L-band), so sánh 4 biến thể thuật toán:
1. **`Baseline`**: Otsu thuần túy (không lọc đốm, không phân loại).
2. **`No Classifier`**: Lọc Lee 7×7 + Otsu + Lọc diện tích `min_area=64`.
3. **`Pipeline + CART`**: Thêm bộ phân loại cây quyết định CART vừa huấn luyện.
4. **`Pipeline + LinearSVM`**: Thêm bộ phân loại LinearSVM vừa huấn luyện.

### Ba phát hiện học thuật quan trọng:
1. **Sự lệch pha giữa Pixel IoU và Object F1:**
   Khi phân đoạn đạt mức pixel rất tốt (`Pixel IoU ~ 0.65-0.75`), `Object F1` có thể vẫn rất thấp (`0.25-0.35`). Nguyên nhân: Thang đo Object F1 áp dụng luật ghép cặp Hungarian 1-1 ở ngưỡng khắt khe $\mathrm{IoU} \ge 0.5$. Một vết dầu lớn bị đứt thành 3 mảnh nhỏ (ví dụ mảnh 1 có IoU=0.45, mảnh 2 có IoU=0.35) sẽ bị tính là **0 TP, 3 FP, 1 FN**!
2. **Hiện tượng Otsu sụp đổ ở hai đầu cực trị:**
   - Ở $R_1$ (vết dầu $< 5\%$): Không đủ độ phân tách hai lớp ($\eta < 0.15$), Otsu cắt nhầm vào phân phối nền biển, gây tràn ứng viên giả.
   - Ở $R_4$ (patch ngập trọn 100% dầu): Ảnh chỉ có một phân phối duy nhất, nhưng Otsu vẫn ép chia đôi, tự băm nát vết dầu thành 20–40 mảnh nhỏ.
3. **Bẫy vành đai nền 5 pixel (`5-Pixel Ring Trap`):**
   Đặc trưng quan trọng nhất của SVM là `background_contrast` ($w \approx +1.25$). Cài đặt hiện tại dùng:
   ```python
   ring = morph(region, "dilate", 5) & (local_labels == 0)
   ```
   Nếu vết dầu lớn bị Otsu cắt co ngót hoặc nằm sát cạnh một mảnh dầu khác, vành đai 5 pixel này **vẫn nằm hoàn toàn bên trong vùng tối của dầu** chứ chưa chạm tới mặt biển sạch:
   $$\mu_{\mathrm{bg}} \approx \mu_{\mathrm{slick}} \implies \mathrm{background\_contrast} \to 0$$
   Do đó, SVM hiểu nhầm đây là vùng nền và loại bỏ chính vết dầu thật!
"""

md_cell_13 = r"""## 6. Thử nghiệm Giả thuyết Cải tiến (Live Proof-of-Concept on Failure Cases)

Từ các phân tích định lượng ở Phần 5, ta đề xuất và thử nghiệm trực tiếp 3 cơ chế nâng cấp nhẹ nhằm giải quyết đúng các điểm nghẽn của phương pháp cổ điển:

### 6.1. Cổng kiểm định tính hai đỉnh ($\eta$-Gate):
Trước khi gọi Otsu, tính chỉ số phân tách $\eta = \sigma_B^2(T^*) / \sigma_T^2$ và độ sáng trung bình $\mu_{\mathrm{img}}$:
- Nếu $\eta < 0.15$ và $\mu_{\mathrm{img}} < 0.22$ (như ở `sentinel_440`, `sentinel_591`): Patch là một khối dầu đồng nhất diện rộng $\implies$ gán nhãn toàn bộ patch là dầu, ngăn chặn việc Otsu băm nhỏ patch thành 40 mảnh.
- Nếu $\eta < 0.15$ và $\mu_{\mathrm{img}} > 0.50$: Patch là mặt biển sạch đồng nhất $\implies$ gán nhãn toàn bộ là nền, triệt tiêu báo nhầm.

### 6.2. Đặc trưng tương phản nền toàn cục ($P_{75}$-Referenced Contrast):
Khắc phục bẫy vành đai 5 pixel bằng cách bổ sung độ tương phản tham chiếu so với phân vị thứ 75 của toàn ảnh (đại diện cho mặt biển sáng):
$$C_{\mathrm{global}} = \frac{P_{75}(I_f) - \mu_{\mathrm{slick}}}{P_{75}(I_f) + \epsilon}$$
Đặc trưng này giúp các mảnh dầu lớn vẫn giữ được độ tương phản dương mạnh ngay cả khi vành đai 5 pixel lân cận bị tối.

### 6.3. Hàn gắn hình thái học có điều kiện (Morphological Bridging):
Thực hiện phép đóng hình thái học (`morphological closing` bán kính 5) trên mặt nạ ứng viên trước khi đưa vào gán nhãn liên thông để nối liền các mảnh dầu bị nứt gãy, giúp đạt điều kiện ghép cặp $\mathrm{IoU} \ge 0.5$ với nhãn ground truth.
"""

md_cell_15 = r"""## 7. Tổng kết Bình duyệt & Khuyến nghị Báo cáo Khoa học

Dựa trên toàn bộ kết quả phân tích lý thuyết, đối sánh định lượng và chẩn đoán vi mô trên bộ dữ liệu ảnh thực tế `SOS`, chúng tôi rút ra các kết luận học thuật sau:

### 7.1. Điểm mạnh nổi bật của Thiết kế Hiện tại
1. **Tính độc lập & Tính toán hiệu năng cao thuần NumPy:** Toàn bộ chuỗi giải thuật từ bộ lọc Lee (dùng Summed-Area Table), phân ngưỡng Otsu, gán nhãn Run-Length Union-Find đến bộ giải Nesterov Accelerated Gradient SVM đều được tự cài đặt bằng NumPy thuần, khớp hoàn hảo nghiệm giải tích số và đạt tốc độ thực thi rất nhanh (~0.03s mỗi ảnh $256\times 256$ trên CPU thông thường).
2. **Khả năng triệt tiêu báo nhầm ấn tượng trên biển sạch:** Trên chế độ $R_0$ (ảnh không có dầu), việc kết hợp bộ lọc Lee và bộ phân loại LinearSVM giúp giảm số lượng báo nhầm từ gần 60 FP/ảnh xuống dưới 0.2 FP/ảnh.
3. **Độ phân đoạn pixel tốt trên vết dầu diện rộng:** Trên các vết dầu vừa và lớn ($R_2, R_3$), thuật toán đạt $\mathrm{Pixel\ IoU} \approx 0.65 - 0.80$, chứng tỏ các đặc trưng hình thái học và bức xạ cổ điển vẫn giữ giá trị cao trong viễn thám SAR khi không dùng mạng nơ-ron sâu.

### 7.2. Các Hạn chế Căn cốt cần lưu ý trong Báo cáo BTL / Bài báo
1. **Sự phụ thuộc vào phân ngưỡng toàn cục Otsu trên ảnh Patch:** Otsu được thiết kế cho ảnh toàn cảnh có phân bố hai đỉnh. Khi áp dụng cho các patch cắt nhỏ $256\times 256$, Otsu sụp đổ hoàn toàn ở hai chế độ biên: bỏ sót vết dầu nhỏ $< 5\%$ và băm nát các patch ngập trọn dầu.
2. **Hiện tượng "Bẫy vành đai nền 5 pixel":** Đặc trưng quan trọng nhất của SVM (`background_contrast`) bị suy giảm nghiêm trọng khi vết dầu lớn bị co ngót hoặc nằm sát nhau, khiến vành đai nền cục bộ bị "chìm" trong dầu.
3. **Đánh giá mức đối tượng khắt khe hơn mức pixel:** Object F1 bị kéo tụt do luật phạt phân mảnh ở ngưỡng $\mathrm{IoU} \ge 0.5$.

### 7.3. Khuyến nghị Hướng Cải tiến & Đóng gói
- Bổ sung **Cổng kiểm định tính hai đỉnh $\eta$-Gate** để phân nhánh xử lý các patch cực trị trước khi chạy Otsu.
- Chuyển đổi đặc trưng `background_contrast` sang dạng **đa tỷ lệ (Multi-scale Annulus)** hoặc tham chiếu với mức nền phân vị toàn cục $P_{75}$.
- Kết hợp **Hàn gắn hình thái học có điều kiện (Morphological Bridging)** trước khi đánh số vùng liên thông để tăng mạnh tỷ lệ ghép trúng đối tượng.
"""

# Map cells
md_map = {
    0: md_cell_0,
    2: md_cell_2,
    5: md_cell_5,
    7: md_cell_7,
    9: md_cell_9,
    11: md_cell_11,
    13: md_cell_13,
    15: md_cell_15,
}

for idx, text in md_map.items():
    nb.cells[idx].source = text.strip()

nbformat.write(nb, NB_PATH)
print("Updated all markdown cells with clean, KaTeX-compliant formatting.")

