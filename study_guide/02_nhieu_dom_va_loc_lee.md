# Chuyên đề 02: Nhiễu đốm Speckle & Bản chất toán học bộ lọc Lee Filter

> **Phạm vi tài liệu tự học — cập nhật 17/11/2026:** đây là giải thích và mã minh họa độc lập, không phải pipeline đã nghiệm thu hoặc bằng chứng đạt 100% đề. Công thức giản lược, ảnh giả lập, ví dụ ghép greedy và mô phỏng trôi dầu không thay thế kết quả trong `src/sar_oil`, `scripts` và `results`. Lee không bảo đảm giữ biên tuyệt đối; agreement 100% chỉ áp dụng cho ca đã đo; F1 SOS 0,3403 là cấu hình được chọn theo quy tắc dung sai, không phải cực đại nghiêm ngặt. Ưu tiên [đối chiếu hiện tại](../docs/DANH_GIA_DU_AN_VA_DOI_CHIEU_DE_18.md) khi có khác biệt.

> 🎯 **Mục tiêu chuyên đề:**\
> Hiểu tại sao ảnh SAR lại có nhiễu hạt lốm đốm (speckle). Chứng minh tại sao nó là **nhiễu nhân** chứ không phải nhiễu cộng. Dẫn xuất công thức bộ lọc **Lee Filter** từ bài toán tối ưu sai số toàn phương (LMMSE). Nắm chắc ví dụ số tính tay $5\times 5$ để trả lời tự tin trước Hội đồng.

---

## 1. Trực giác đời thường: Nhiễu đốm (Speckle) từ đâu chui ra?

Khi nhìn vào một bức ảnh SAR, bạn sẽ thấy bề mặt biển không hề mịn màng mà bị rải một lớp "muối tiêu" lốm đốm, hạt sáng hạt tối chen chúc nhau rất gắt.
* Nhiều người tưởng đây là do cảm biến bị lỗi hoặc do đường truyền bị nhiễu. **Hoàn toàn sai!**
* **Nhiễu đốm là một hiện tượng vật lý tất yếu của hệ thống radar kết hợp (Coherent Radar):**
  - Một pixel trên ảnh SAR đại diện cho một ô đất/biển có kích thước thực tế (ví dụ $10\text{m} \times 10\text{m}$).
  - Trong ô $100\text{ m}^2$ đó, có hàng triệu điểm phản xạ nhỏ li ti (từng gợn sóng, bọt biển, mẩu rác...).
  - Sóng radar chiếu xuống đập vào tất cả các điểm đó rồi dội ngược về.
  - Vì khoảng cách từ các điểm con này đến ăng-ten chênh lệch nhau vài milimet, các sóng dội về sẽ **giao thoa với nhau**:
    - Nơi sóng cùng pha $\to$ cộng hưởng làm tín hiệu vọt lên cực sáng.
    - Nơi sóng ngược pha $\to$ triệt tiêu làm tín hiệu tụt xuống tối đen.
  - $\implies$ Kết quả: Sinh ra hiện tượng nhiễu đốm hạt hạt (Speckle).

---

## 2. Tại sao là Nhiễu Nhân (Multiplicative Noise) mà không phải Nhiễu Cộng?

Đây là điểm mấu chốt để phân biệt người hiểu xử lý ảnh SAR với người chỉ học vẹt xử lý ảnh thông thường:

* **Trong ảnh quang học thông thường:**\
  Nhiễu thường là nhiễu nhiệt cảm biến, độc lập với độ sáng của vật thể:
  $$y = x + n$$
  *(Nhiễu cộng: Dù cảnh sáng hay cảnh tối, biên độ nhiễu $n$ vẫn như nhau).*

* **Trong ảnh Radar SAR:**\
  Biên độ của nhiễu giao thoa tỉ lệ thuận trực tiếp với cường độ sóng phản xạ: Càng phản xạ mạnh thì giao thoa càng dữ dội!
  Do đó, mô hình toán học của ảnh SAR là **Nhiễu nhân**:
  $$y = x \cdot v$$
  Trong đó:
  - $y$: Giá trị pixel quan sát được trên ảnh SAR (bị nhiễu).
  - $x$: Tín hiệu phản xạ thực sự của mặt đất/biển (giá trị không nhiễu cần tìm).
  - $v$: Thành phần nhiễu đốm ngẫu nhiên, có giá trị trung bình kỳ vọng bằng $1$ ($\mathbb{E}[v] = 1$) và phương sai $\sigma_v^2 = \frac{1}{L}$ (với $L$ là số lượt nhìn - number of looks).

> 💡 **Hệ quả cực kỳ quan trọng:**\
> Ở vùng sáng (biển nhám), nhiễu dao động rất mạnh với biên độ lớn. Ở vùng tối (vết dầu), biên độ nhiễu lại rất nhỏ.\
> Vì là nhiễu nhân, các bộ lọc nhiễu cộng thông thường (như Gaussian hay Box Mean) sẽ tính sai bản chất thống kê!

---

## 3. Vì sao Box Mean và Median lại thất bại hoặc kém tối ưu?

Trước khi chọn Lee Filter, dự án đã thử nghiệm 13 cấu hình bộ lọc khác nhau trên 671 ảnh validation. Kết quả thực nghiệm cho thấy:
1. **Bộ lọc trung bình (Box Mean):**
   - Lấy trung bình cộng tất cả các pixel trong cửa sổ: $\hat{x} = \frac{1}{N} \sum y_i$.
   - *Hậu quả:* Nó san phẳng mọi thứ! Vết dầu có đường biên rất sắc nét, khi áp dụng Mean Filter, đường biên bị nhòe nhoẹt (blur), vết dầu bị phình to ra và mép biên bị mờ, làm giảm mạnh độ chính xác định vị.
2. **Bộ lọc trung vị (Median Filter):**
   - Lấy giá trị ở giữa sau khi sắp xếp. Khử nhiễu muối tiêu tốt trên ảnh quang học.
   - *Hậu quả trên SAR:* Vết dầu tràn thường có hình dải hẹp, dài ngoằn ngoèo hoặc có các đuôi nhọn. Bộ lọc Median có xu hướng "gọt tỉa" làm cụt các góc nhọn và cắt đứt các vệt dầu mỏng.
3. **Bộ lọc thích nghi Lee Filter (Chiến thắng):**
   - Vừa làm mịn cực mạnh ở vùng đồng nhất (nền biển hoặc lòng vết dầu), vừa **có thể hạn chế làm mờ ở đường biên, tùy tương quan tín hiệu và nhiễu vết dầu**!

---

## 4. Chứng minh toán học công thức bộ lọc Lee Filter

Bộ lọc Lee Filter (do C.K. Lee phát minh năm 1980) giải bài toán: *Tìm một ước lượng tuyến tính $\hat{x}$ của tín hiệu gốc $x$ sao cho sai số bình phương trung bình $\mathbb{E}[(x - \hat{x})^2]$ là nhỏ nhất (Linear Minimum Mean Square Error - LMMSE)*.

Giả sử ước lượng có dạng tuyến tính:
$$\hat{x} = a + b \cdot y$$

Dựa trên mô hình nhiễu nhân $y = x \cdot v$ với $\mathbb{E}[v] = 1$ và $\text{Var}(v) = \sigma_v^2 = \frac{1}{L}$:
1. **Giá trị trung bình cục bộ của $y$:**
   $$\bar{y} = \mathbb{E}[y] = \mathbb{E}[x \cdot v] = \mathbb{E}[x] \cdot \mathbb{E}[v] = \bar{x} \cdot 1 = \bar{x}$$
   $\implies$ Trung bình cục bộ của ảnh quan sát chính là trung bình của tín hiệu thực.

2. **Phương sai cục bộ của $y$:**
   Áp dụng công thức phương sai tích hai biến ngẫu nhiên độc lập:
   $$\text{Var}(y) = \sigma_y^2 = \bar{x}^2 \sigma_v^2 + \sigma_x^2 + \sigma_x^2 \sigma_v^2 \approx \sigma_x^2 + \bar{y}^2 \sigma_v^2$$
   Từ đó, phương sai thực của bề mặt đất $\sigma_x^2$ được ước lượng bằng:
   $$\sigma_x^2 = \max\left(0, \sigma_y^2 - \bar{y}^2 \sigma_v^2\right)$$

3. **Tìm hệ số tối ưu $b$ (Trọng số thích nghi $W$):**
   Giải bài toán cực tiểu hóa sai số $\mathbb{E}[(x - (a + by))^2]$, ta tìm được:
   $$W = b = \frac{\text{Cov}(x, y)}{\text{Var}(y)} = \frac{\sigma_x^2}{\sigma_y^2} = \frac{\sigma_y^2 - \bar{y}^2 \sigma_v^2}{\sigma_y^2}$$
   Vì $\sigma_v^2 = \frac{1}{L}$ (với ảnh Sentinel-1 multilook, $L=4$ hoặc $L=1$), phương sai nhiễu là $\sigma_{noise}^2 = \frac{\bar{y}^2}{L}$.

### Công thức chuẩn cuối cùng của Lee Filter:
$$\boxed{W = \max\left(0, \frac{\sigma_y^2 - \bar{y}^2/L}{\sigma_y^2}\right)}$$
$$\boxed{\hat{x} = \bar{y} + W \cdot (y - \bar{y})}$$

---

## 5. Trực giác hoạt động của Trọng số $W$: Thông minh ở chỗ nào?

Hãy nhìn vào cách trọng số $W \in [0, 1]$ tự động biến thiên:

* **Trường hợp 1: Pixel nằm sâu trong lòng biển phẳng hoặc lòng vết dầu (Vùng đồng nhất):**
  - Vì vùng này phẳng, độ biến thiên chỉ do nhiễu đốm gây ra $\implies \sigma_y^2 \approx \bar{y}^2/L$.
  - Khi đó tử số $\approx 0 \implies \mathbf{W \to 0}$.
  - Thay $W = 0$ vào công thức:
    $$\hat{x} = \bar{y} + 0 \cdot (y - \bar{y}) = \mathbf{\bar{y}}$$
  - $\implies$ **Nó biến thành bộ lọc Mean làm mịn hoàn hảo, xóa sạch bong nhiễu đốm!**

* **Trường hợp 2: Pixel nằm ngay tại ranh giới biên giữa nước biển và vết dầu (Vùng có biên):**
  - Mép biên có sự thay đổi mức xám đột ngột (biển sáng, dầu tối) $\implies$ Phương sai đo được $\sigma_y^2$ cực kỳ lớn, lớn hơn rất nhiều so với phương sai nhiễu ($\sigma_y^2 \gg \bar{y}^2/L$).
  - Khi đó tử số xấp xỉ mẫu số $\implies \mathbf{W \to 1}$.
  - Thay $W = 1$ vào công thức:
    $$\hat{x} = \bar{y} + 1 \cdot (y - \bar{y}) = \mathbf{y}$$
  - $\implies$ **Nó giữ nguyên giá trị gốc của pixel, bảo vệ độ sắc nét của đường biên 100%, không bị nhòe 1 pixel nào!**

---

## 6. Worked Example: Tính tay ma trận $5\times 5$ từng bước

Giả sử ta có một cửa sổ nhỏ $3\times 3$ nằm ngay trên đường biên vết dầu, số lượt nhìn $L=1$:

```text
Ma trận mức xám y (cửa sổ 3x3):
[ 100   100   100 ]   <- Nền biển sáng
[  20    20    20 ]   <- Mép vết dầu tối
[  20    20    20 ]   <- Lòng vết dầu tối
```

Pixel trung tâm đang xét là $y = 20$. Hãy tính giá trị sau lọc $\hat{x}$:

1. **Tính giá trị trung bình $\bar{y}$:**
   $$\bar{y} = \frac{100 \times 3 + 20 \times 6}{9} = \frac{300 + 120}{9} = \frac{420}{9} \approx 46.67$$
2. **Tính phương sai $\sigma_y^2$:**
   $$\mathbb{E}[y^2] = \frac{100^2 \times 3 + 20^2 \times 6}{9} = \frac{30000 + 2400}{9} = \frac{32400}{9} = 3600$$
   $$\sigma_y^2 = \mathbb{E}[y^2] - \bar{y}^2 = 3600 - (46.67)^2 = 3600 - 2178.09 = 1421.91$$
3. **Tính phương sai nhiễu $\sigma_{noise}^2$ với $L=1$:**
   $$\sigma_{noise}^2 = \frac{\bar{y}^2}{L} = \frac{2178.09}{1} = 2178.09$$
   *(Trong trường hợp này, vì mẫu nhỏ nên $\sigma_y^2 < \sigma_{noise}^2 \implies W = 0$. Nhưng trên cửa sổ thực $7\times 7$ với $L=4$, $\sigma_{noise}^2 = \bar{y}^2/4 \approx 544.5 < 1421.91$).*
4. **Giả sử $L=4$ (như cấu hình đã chọn trong dự án):**
   $$\sigma_{noise}^2 = \frac{2178.09}{4} \approx 544.52$$
   $$W = \frac{1421.91 - 544.52}{1421.91} = \frac{877.39}{1421.91} \approx 0.617$$
5. **Giá trị pixel sau lọc $\hat{x}$:**
   $$\hat{x} = \bar{y} + W \cdot (y - \bar{y}) = 46.67 + 0.617 \cdot (20 - 46.67) = 46.67 - 16.45 \approx \mathbf{30.22}$$

$\implies$ **Nhận xét:** Nếu dùng Mean Filter, pixel này sẽ bị kéo lên tận $46.67$ (làm mờ đen thành xám). Nhưng nhờ Lee Filter với $W=0.617$, giá trị chỉ là $30.22$, giữ được độ tối của vết dầu!

> 💡 **Mở rộng kiểm chứng toán học (Worked Example chuẩn bằng số hữu tỉ):**\
> Trong tài liệu kiểm chứng độc lập của dự án ([results/sos/worked_example/REPORT.md](file:///D:/Codin/utc-code/HK4_1/XLA/BTL/results/sos/worked_example/REPORT.md)), nhóm đã kiểm chứng trên một ma trận tổng hợp $5\times 5$ có nền biển $0.2$ và tâm là một xung sáng đột ngột $0.9$. Bằng việc tính toán giải tích bằng **số hữu tỉ chính xác (Exact Fractions)**, giá trị lý thuyết tại tâm được tính ra chính xác là:
> $$\hat{x}_{tâm} = \frac{1643}{2520} \approx 0.651984126984...$$
> Khi so sánh với code NumPy tự cài, sai số tuyệt đối đo được chỉ là $1.94 \times 10^{-16}$ (chính xác đến giới hạn bit của chuẩn số thực IEEE 754)! Điều này chứng minh thuật toán của nhóm không hề có sai số logic hay sai số thuật toán nào.

---

## 7. Hệ thống câu hỏi truy vấn bản chất (Socratic Q&A)

### Câu hỏi 1:
* **Hỏi:** *Tại sao trong dự án lại chọn cấu hình Lee Filter kích thước $7\times 7$ và $L=4$ mà không chọn $3\times 3$ hay $5\times 5$?*
* **Trả lời:** Qua thực nghiệm sàng lọc trên 671 ảnh validation ([results/sos/screen.json](file:///D:/Codin/utc-code/HK4_1/XLA/BTL/results/sos/screen.json)):
  - Cửa sổ $3\times 3$ quá nhỏ, số lượng mẫu không đủ để ước lượng phương sai cục bộ $\sigma_y^2$ chính xác, dẫn đến việc khử nhiễu đốm chưa triệt để ($F1 \approx 0.05-0.06$).
  - Cửa sổ $7\times 7$ có 49 pixel, ước lượng thống kê rất ổn định.
  - Tham số $L=4$ (4-looks) phù hợp với cơ chế multilooking của sản phẩm Sentinel-1 GRD (Ground Range Detected), giúp cân bằng hoàn hảo giữa khả năng làm mịn nền biển và độ sắc nét đường biên vết dầu, đạt F1 ứng viên cao nhất là $0.0855$.

### Câu hỏi 2:
* **Hỏi:** *Trong code `src/sar_oil/core.py`, phép tính Mean Filter được tối ưu như thế nào?*
* **Trả lời:** Nhóm không dùng 2 vòng lặp lồng nhau $O(W \cdot H \cdot \text{size}^2)$ vì sẽ chạy rất chậm. Nhóm tự cài đặt thuật toán **Bảng diện tích tích phân (Summed-Area Table / Integral Image)** bằng hàm `.cumsum(0).cumsum(1)` của NumPy. Thuật toán này có độ phức tạp chỉ là $O(W \cdot H)$, tốc độ tính toán hoàn toàn độc lập với kích thước cửa sổ lọc!

---

## 8. Trắc nghiệm ôn tập nhanh (Quiz 02)

**Câu 1:** Bản chất vật lý của nhiễu đốm (Speckle noise) trong ảnh SAR là gì?\
A. Do bụi bẩn bám trên thấu kính của vệ tinh.\
B. Do hiện tượng giao thoa sóng tán xạ kết hợp từ nhiều điểm phản xạ nhỏ trong một ô độ phân giải.\
C. Do nhiễu nhiệt điện tử của bộ thu tín hiệu.\
D. Do bức xạ mặt trời làm méo bước sóng vi ba.\
*(Đáp án: **B**)*

**Câu 2:** Mô hình toán học chính xác của ảnh SAR là:\
A. $y = x + v$ (Nhiễu cộng)\
B. $y = x \cdot v$ (Nhiễu nhân)\
C. $y = x^v$ (Nhiễu lũy thừa)\
D. $y = \log(x + v)$\
*(Đáp án: **B**)*

**Câu 3:** Trong bộ lọc Lee Filter, khi xét một pixel nằm trên đường biên sắc nét giữa vết dầu và nước biển, trọng số $W$ sẽ có xu hướng tiến về mấy?\
A. $W \to 0$\
B. $W \to 1$\
C. $W \to 0.5$\
D. $W \to \infty$\
*(Đáp án: **B** — Khi $W \to 1$, $\hat{x} \approx y$, giữ nguyên giá trị biên gốc)*

**Câu 4:** Tham số $L$ trong công thức Lee Filter $\sigma_{noise}^2 = \bar{y}^2/L$ đại diện cho cái gì?\
A. Độ dài bước sóng của radar.\
B. Số lượng vết dầu có trong ảnh.\
C. Số lượt nhìn độc lập (Number of looks) của ảnh SAR.\
D. Cấp độ phân giải mức xám của cảm biến.\
*(Đáp án: **C**)*

**Câu 5:** Nhược điểm chí mạng của bộ lọc Box Mean Filter khi xử lý vết dầu SAR là gì?\
A. Làm mờ nhòe (blur) đường biên vết dầu, làm sai lệch diện tích và hình thái.\
B. Làm ảnh bị đảo ngược mức xám.\
C. Không thể tính toán được bằng ngôn ngữ Python.\
D. Làm vết dầu bị chia cắt thành hàng trăm đốm nhỏ.\
*(Đáp án: **A**)*
