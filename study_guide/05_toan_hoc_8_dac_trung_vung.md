# Chuyên đề 05: Chứng minh toán học & Ý nghĩa vật lý của 8 đặc trưng vùng

> **Phạm vi tài liệu tự học — cập nhật 17/11/2026:** đây là giải thích và mã minh họa độc lập, không phải pipeline đã nghiệm thu hoặc bằng chứng đạt 100% đề. Công thức giản lược, ảnh giả lập, ví dụ ghép greedy và mô phỏng trôi dầu không thay thế kết quả trong `src/sar_oil`, `scripts` và `results`. Lee không bảo đảm giữ biên tuyệt đối; agreement 100% chỉ áp dụng cho ca đã đo; F1 SOS 0,3403 là cấu hình được chọn theo quy tắc dung sai, không phải cực đại nghiêm ngặt. Ưu tiên [đối chiếu hiện tại](../docs/DANH_GIA_DU_AN_VA_DOI_CHIEU_DE_18.md) khi có khác biệt.

> 🎯 **Mục tiêu chuyên đề:**\
> Hiểu tại sao phân ngưỡng thôi là chưa đủ mà bắt buộc phải trích xuất đặc trưng. Nắm vững bản chất toán học từ con số 0 của cả **8 đặc trưng** trong file [src/sar_oil/core.py](file:///D:/Codin/utc-code/HK4_1/XLA/BTL/src/sar_oil/core.py): Ma trận hiệp phương sai ra trị riêng cho độ thuôn dài, bất đẳng thức đẳng chu cho độ phức tạp biên, và tại sao **vành nền cục bộ 5 pixel** lại là "chìa khóa vàng" để nhận dạng vết dầu.

---

## 1. Trực giác đời thường: Tại sao cần trích xuất đặc trưng?

Sau Bước 4, ta có danh sách các vùng tối ứng viên. Nhưng trong số đó:
* Có những vùng là **vết dầu thật** (loang lổ từ tàu xả thải hoặc dàn khoan).
* Có những vùng là **vệt gió yếu** (biển lặng gió tự nhiên).
* Có những vùng là **vệt nước mưa** hoặc **bóng đảo ven bờ**.

Tất cả chúng đều là những mảng màu đen trên ảnh SAR!\
Nếu chỉ nhìn vào màu đen, máy tính không thể phân biệt được. Nhưng nếu nhìn vào **hình dáng học (Geometry)** và **tính chất vật lý vi mô (Radiometry & Contrast)**, vết dầu tràn có những "dấu vân tay" cực kỳ đặc thù:
1. **Dầu loang thường bị gió và sóng kéo dài ra thành vệt hẹp uốn lượn** (thuôn dài cao).
2. **Đường biên của vết dầu rất nham nhở, rách rưới** (độ phức tạp biên cao).
3. **Mặt dầu rất phẳng và đồng nhất** (độ lệch chuẩn nội vùng thấp).
4. **Vết dầu tạo độ tương phản bức xạ rất gắt ngay tại ranh giới với nước biển xung quanh**.

Để máy tính "học" được những dấu vân tay này, ta số hóa chúng thành **vector đặc trưng 8 chiều**:
$$X = [x_1, x_2, x_3, x_4, x_5, x_6, x_7, x_8] \in \mathbb{R}^8$$

---

## 2. Đi sâu vào bản chất toán học của từng đặc trưng

Dưới đây là phần giải phẫu toán học chi tiết 8 đặc trưng được lập trình trong hàm `core.features(a, labels)`:

```python
FEATURES = [
    "area_fraction",      # 1. Tỷ lệ diện tích
    "elongation",         # 2. Độ thuôn dài (Eigenvalues)
    "extent",             # 3. Độ lấp đầy hộp bao
    "complexity",         # 4. Độ phức tạp đường biên (Isoperimetric Quotient)
    "mean",               # 5. Cường độ sáng trung bình nội vùng
    "std",                # 6. Độ lệch chuẩn cường độ sáng nội vùng
    "boundary_gradient",  # 7. Độ dốc bức xạ dọc đường biên (Sobel)
    "background_contrast" # 8. Độ tương phản với vành nền lân cận
]
```

---

### Đặc trưng 1: Tỷ lệ diện tích (`area_fraction`)
* **Công thức:**
  $$\text{area\_fraction} = \frac{A}{A_{image}} = \frac{\text{Số lượng pixel của vùng}}{\text{Chiều rộng} \times \text{Chiều cao ảnh}}$$
* **Ý nghĩa vật lý:**
  - Vết dầu tràn do tàu xả thải thường có kích thước vừa phải (từ vài trăm đến vài ngàn pixel).
  - Vùng gió yếu tự nhiên thường là những mảng khổng lồ bao phủ $30\% - 50\%$ toàn bộ khung cảnh. Đặc trưng này giúp phân loại ngay các mảng gió yếu quy mô lớn.

---

### Đặc trưng 2: Độ thuôn dài (`elongation`) — Trị riêng của Ma trận hiệp phương sai
* **Sai lầm thường gặp:** Rất nhiều người lấy Chiều dài chia Chiều rộng của hộp bao chữ nhật (Bounding Box): $\frac{W_{bbox}}{H_{bbox}}$.
  - *Tại sao sai:* Nếu vết dầu là một dải hẹp dài nằm chéo góc $45^\circ$, hộp bao chữ nhật của nó sẽ là một hình vuông ($W \approx H \implies \text{Tỉ số} \approx 1$). Máy tính sẽ tưởng nhầm vệt dầu dài ngoẵng này là một hình tròn tròn!
* **Giải pháp toán học mẫu mực của nhóm:** Sử dụng **Elip tương đương quán tính (Equivalent Inertia Ellipse)**:
  1. Tọa độ của các pixel trong vùng: $(x_i, y_i)$ với $i = 1, \dots, A$.
  2. Dịch tâm về trọng tâm của vùng: $\tilde{x}_i = x_i - \bar{x}$, $\tilde{y}_i = y_i - \bar{y}$.
  3. Lập ma trận hiệp phương sai tọa độ $2\times 2$:
     $$C = \frac{1}{A} \begin{bmatrix} \sum \tilde{x}_i^2 & \sum \tilde{x}_i \tilde{y}_i \\ \sum \tilde{x}_i \tilde{y}_i & \sum \tilde{y}_i^2 \end{bmatrix}$$
  4. Tính 2 trị riêng của ma trận $C$ bằng hàm `np.linalg.eigvalsh(C)`:
     $$0 \le \lambda_2 \le \lambda_1$$
     - $\lambda_1$ đại diện cho phương sai dọc theo trục dài nhất của vết dầu.
     - $\lambda_2$ đại diện cho phương sai dọc theo trục ngắn nhất vuông góc với trục dài.
  5. **Công thức độ thuôn dài:**
     $$\boxed{\text{elongation} = \sqrt{\frac{\lambda_1 + \epsilon}{\lambda_2 + \epsilon}}}$$
     *(Lưu ý về cài đặt trong code NumPy: Hàm `np.linalg.eigvalsh(C)` luôn trả về các trị riêng theo thứ tự tăng dần $\lambda_2 \le \lambda_1$, tức là `eigen[0]` $\le$ `eigen[1]`. Do đó trong code `core.py`, biểu thức được viết chính xác là `np.sqrt((eigen[1] + 1e-6) / (eigen[0] + 1e-6))` — lấy trị riêng lớn chia trị riêng bé).*
* **Ý nghĩa vật lý:**
  - Nếu vùng có hình tròn hoặc hình vuông: $\lambda_1 \approx \lambda_2 \implies \text{elongation} \approx 1.0$.
  - Nếu vết dầu bị gió kéo thành dải dài ngoằn ngoèo: $\lambda_1 \gg \lambda_2 \implies \text{elongation} \ge 3.0 - 10.0$.
  - Trị riêng tự động xoay theo góc nghiêng thực tế của vết dầu, bất chấp vết dầu nằm ngang, nằm dọc hay nằm chéo!

---

### Đặc trưng 3: Độ lấp đầy hộp bao (`extent`)
* **Công thức:**
  $$\text{extent} = \frac{A}{(x_{max} - x_{min} + 1) \cdot (y_{max} - y_{min} + 1)}$$
* **Ý nghĩa vật lý:**
  - Tỉ số giữa diện tích thực của vết dầu so với diện tích của chiếc hộp chữ nhật nhỏ nhất bao quanh nó.
  - Hình chữ nhật đặc có $\text{extent} = 1.0$.
  - Vết dầu uốn lượn hình chữ S hoặc chữ C có $\text{extent}$ rất nhỏ ($< 0.2$), vì nó rỗng ở giữa.

---

### Đặc trưng 4: Độ phức tạp đường biên (`complexity`) — Bất đẳng thức đẳng chu
* **Nguồn gốc toán học:**
  - Theo **Bất đẳng thức đẳng chu (Isoperimetric Inequality)** trong hình học phẳng: Trong tất cả các hình khép kín có cùng diện tích $A$, hình tròn là hình có chu vi $P$ ngắn nhất:
    $$P^2 \ge 4\pi A$$
    Dấu bằng ($P^2 = 4\pi A$) xảy ra khi và chỉ khi đối tượng là **hình tròn hoàn hảo**!
* **Công thức tính:**
  $$\boxed{\text{complexity} = \frac{P^2}{4\pi A}}$$
  *(Trong đó chu vi $P$ được tính chính xác bằng tổng các cạnh lưới pixel tiếp giáp với bên ngoài).*
* **Ý nghĩa vật lý:**
  - Hình tròn: $\text{complexity} = 1.0$ (độ phức tạp thấp nhất, viền trơn láng nhất).
  - Vệt mưa hoặc vũng gió yếu thường có đường viền khá trơn, bầu bĩnh $\implies \text{complexity}$ thấp ($1.5 - 3.0$).
  - Vết dầu loang chịu tác động xé rách của dòng hải lưu và sóng biển nên đường biên bị gấp khúc, lởm chởm, rách rưới $\implies \text{complexity}$ rất cao ($5.0 - 20.0+$).

---

### Đặc trưng 5 & 6: Cường độ sáng trung bình (`mean`) và Độ lệch chuẩn (`std`)
* **Công thức:**
  $$\text{mean} = \frac{1}{A} \sum_{(x,y) \in \text{vùng}} I(x, y)$$
  $$\text{std} = \sqrt{\frac{1}{A} \sum_{(x,y) \in \text{vùng}} (I(x, y) - \text{mean})^2}$$
* **Ý nghĩa vật lý:**
  - Đo xem vùng tối này tối đến mức nào (mức độ dập sóng).
  - Đo độ đồng nhất của vệt dầu: Vết dầu thô dày thường rất mịn và đồng nhất bên trong ($\text{std}$ nhỏ), trong khi các vùng biển xáo trộn do bão gió có $\text{std}$ rất lớn.

---

### Đặc trưng 7: Độ dốc bức xạ dọc đường biên (`boundary_gradient`)
* **Cách tính trong code:**
  1. Áp dụng toán tử đạo hàm Sobel theo 2 trục $X$ và $Y$ trên ảnh mức xám đã lọc: $G_x = I * S_x$, $G_y = I * S_y$.
  2. Độ lớn gradient tại mỗi pixel: $G = \sqrt{G_x^2 + G_y^2}$ (`np.hypot`).
  3. Tìm đường biên mỏng 1 pixel của vết dầu: $\text{boundary} = \text{region} \land \neg(\text{erode}(\text{region}))$.
  4. Lấy trung bình độ lớn gradient trên tập các pixel đường biên này:
     $$\text{boundary\_gradient} = \frac{1}{|\text{boundary}|} \sum_{p \in \text{boundary}} G(p)$$
* **Ý nghĩa vật lý:**
  - Ranh giới giữa màng dầu và nước biển là một bước nhảy mức xám rất đột ngột $\to$ Gradient biên lớn.
  - Ranh giới của vùng gió yếu hoặc vệt mưa thường biến thiên thoai thoải, mờ dần ra biển $\to$ Gradient biên nhỏ.

---

### Đặc trưng 8: Độ tương phản với vành nền lân cận (`background_contrast`)
* **Tại sao không lấy trung bình vết dầu so với trung bình của toàn bức ảnh?**
  - Vì độ sáng của ảnh SAR bị biến thiên theo góc tới và trường gió diện rộng: Nửa ảnh bên trái có thể sáng hơn nửa ảnh bên phải!
  - Lấy trung bình toàn ảnh sẽ khiến các vết dầu ở vùng tối bị tính sai tương phản.
* **Giải pháp đột phá: Tạo Vành đai nền cục bộ (Local Background Ring 5px):**
  1. Giãn nở vùng dầu ra ngoài thêm $5$ pixel bằng phép Dilate: $\text{dilate}(\text{region}, 5)$.
  2. Lấy phần vành giãn nở này và **loại trừ bản thân vết dầu cùng các vết dầu khác lân cận**:
     $$\text{ring} = \text{dilate}(\text{region}, 5) \land (\text{labels} == 0)$$
  3. Giá trị trung bình của vành nước biển sát nách vết dầu: $\bar{I}_{bg}$.
  4. **Công thức độ tương phản:**
     $$\boxed{\text{background\_contrast} = \frac{\bar{I}_{bg} - \text{mean}_{region}}{|\bar{I}_{bg}| + \epsilon}}$$
* **Ý nghĩa vật lý:**
  - Đây là đặc trưng mạnh nhất để phát hiện dầu: Cho biết vết dầu này tối hơn bao nhiêu phần trăm so với chính vùng nước biển ngay sát cạnh nó!

```text
       [ . . . . . . . . . . . . . . . ]
       [ . . . /-----------------\ . . ]  <- Vành nền biển cục bộ (Ring 5px)
       [ . . /   *************     \ . ]
       [ .  |   *** VẾT DẦU ***     |  ]
       [ . . \   *************     / . ]
       [ . . . \-----------------/ . . ]
       [ . . . . . . . . . . . . . . . ]
```

---

## 3. Bảng tổng hợp 8 đặc trưng vùng

| STT | Tên đặc trưng | Nhóm | Công thức tóm tắt | Giá trị vết dầu thật | Giá trị Look-alike |
|:---:|---|:---:|---|:---:|:---:|
| 1 | `area_fraction` | Hình học | $A / A_{img}$ | Nhỏ đến vừa ($< 0.05$) | Thường rất lớn ($> 0.2$) |
| 2 | `elongation` | Hình học | $\sqrt{\lambda_1 / \lambda_2}$ (Eigenvalues) | **Cao** ($> 2.5$) | Thấp ($1.0 - 1.8$) |
| 3 | `extent` | Hình học | $A / (W_{bb} \cdot H_{bb})$ | Thấp đến trung bình | Cao (hình khối) |
| 4 | `complexity` | Hình học | $P^2 / (4\pi A)$ | **Rất cao** ($> 4.0$) | Thấp ($1.2 - 2.5$) |
| 5 | `mean` | Cường độ | $\bar{I}_{region}$ | Thấp (tối đen) | Thấp vừa |
| 6 | `std` | Cường độ | $\sigma_{region}$ | Rất thấp (đồng nhất) | Cao (xáo trộn) |
| 7 | `boundary_gradient` | Biên | Mean Sobel trên biên 1px | **Cao** (bước nhảy gắt) | Thấp (chuyển tiếp thoai thoải) |
| 8 | `background_contrast`| Bức xạ | $(\bar{I}_{ring} - \bar{I}_{reg}) / \bar{I}_{ring}$ | **Rất cao** ($> 0.5$) | Thấp ($0.1 - 0.3$) |

---

## 4. Hệ thống câu hỏi truy vấn bản chất (Socratic Q&A)

### Câu hỏi 1:
* **Hỏi:** *Tại sao trong ma trận hiệp phương sai tính độ thuôn dài, ta lại dùng hàm `np.linalg.eigvalsh` mà không dùng `eig` thông thường?*
* **Trả lời:** Ma trận hiệp phương sai $C$ là một ma trận đối xứng thực ($C = C^T$) và nửa xác định dương. Hàm `eigvalsh` của NumPy được thiết kế chuyên biệt cho ma trận đối xứng (Symmetric/Hermitian). Nó sử dụng giải thuật nhanh hơn gấp nhiều lần và đảm bảo $100\%$ các trị riêng tìm được luôn là số thực, triệt tiêu hoàn toàn nguy cơ sinh ra phần ảo do sai số làm tròn dấu phẩy động!

### Câu hỏi 2:
* **Hỏi:** *Nếu một vết dầu nằm sát sạt góc mép ảnh thì phép Dilate lấy vành nền 5px có bị văng lỗi vượt chỉ số mảng (IndexError) không?*
* **Trả lời:** Trong mã nguồn `src/sar_oil/core.py`, nhóm đã chủ động dùng kỹ thuật cắt lát an toàn:
  ```python
  y0, y1 = max(0, y.min() - 5), min(a.shape[0], y.max() + 6)
  x0, x1 = max(0, x.min() - 5), min(a.shape[1], x.max() + 6)
  ```
  Hàm `max(0, ...)` và `min(shape, ...)` kẹp chặt chỉ số luôn nằm trong biên giới hợp lệ của bức ảnh. Nếu vành nền bị chạm viền ảnh hoặc rỗng, thuật toán có cơ chế dự phòng an toàn (fallback) tự động chuyển sang lấy trung bình nền toàn ảnh: `bg = background.mean() if len(background) else a.mean()`.

---

## 5. Trắc nghiệm ôn tập nhanh (Quiz 05)

**Câu 1:** Tại sao không nên dùng tỷ số $W_{bbox} / H_{bbox}$ để tính độ thuôn dài của vết dầu?\
A. Vì phép chia máy tính chạy rất chậm.\
B. Vì nếu vết dầu dài hẹp nằm nghiêng một góc $45^\circ$, hộp bao chữ nhật là hình vuông ($W \approx H$) dẫn đến tính sai độ thuôn dài.\
C. Vì Bounding box không thể vẽ được trên ma trận 2D.\
D. Vì Bounding box chỉ dùng cho ảnh màu.\
*(Đáp án: **B**)*

**Câu 2:** Độ phức tạp đường biên `complexity` được tính theo công thức nào dựa trên Bất đẳng thức đẳng chu?\
A. $P / A$\
B. $4\pi A / P^2$\
C. $P^2 / (4\pi A)$\
D. $\sqrt{P \cdot A}$\
*(Đáp án: **C** — Hình tròn có giá trị nhỏ nhất = 1, hình càng rách rưới nham nhở thì giá trị càng lớn)*

**Câu 3:** Việc tạo một vành nền cục bộ (Local Background Ring) bán kính 5 pixel quanh vết dầu nhằm giải quyết vấn đề gì?\
A. Tăng độ phân giải không gian của ảnh.\
B. Loại bỏ ảnh hưởng của sự biến thiên độ sáng nền biển diện rộng (do góc tới và gió), giúp tính độ tương phản cục bộ chính xác.\
C. Làm mịn biên vết dầu.\
D. Thay thế cho bước khử nhiễu Lee Filter.\
*(Đáp án: **B**)*

**Câu 4:** Một vùng tối trên biển có đặc trưng: `area_fraction` = 0.45, `elongation` = 1.2, `complexity` = 1.4, `boundary_gradient` = thấp. Vùng này nhiều khả năng là:\
A. Vết dầu tràn do tàu xả thải trộm.\
B. Vùng biển lặng gió tự nhiên quy mô lớn (Look-alike).\
C. Dàn khoan dầu khí ngoài khơi.\
D. Đảo đá vôi ven bờ.\
*(Đáp án: **B** — Diện tích khổng lồ, hình dáng bầu bĩnh, biên mờ)*

**Câu 5:** Sau khi trích xuất được 8 đặc trưng cho mỗi vùng, bước tiếp theo bắt buộc phải làm trước khi đưa vào mô hình Machine Learning là gì?\
A. Nhân tất cả các giá trị với 255.\
B. Chuẩn hóa thang đo (StandardScaler / z-score) để các đặc trưng có mean=0, std=1, tránh việc đặc trưng có số lớn lấn át đặc trưng có số bé.\
C. Làm tròn tất cả các đặc trưng thành số nguyên.\
D. Đảo ngược dấu của tất cả các đặc trưng.\
*(Đáp án: **B**)*
