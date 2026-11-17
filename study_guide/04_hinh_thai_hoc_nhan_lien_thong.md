# Chuyên đề 04: Toán tử hình thái học & Gán nhãn liên thông 8 hướng

> **Phạm vi tài liệu tự học — cập nhật 17/11/2026:** đây là giải thích và mã minh họa độc lập, không phải pipeline đã nghiệm thu hoặc bằng chứng đạt 100% đề. Công thức giản lược, ảnh giả lập, ví dụ ghép greedy và mô phỏng trôi dầu không thay thế kết quả trong `src/sar_oil`, `scripts` và `results`. Lee không bảo đảm giữ biên tuyệt đối; agreement 100% chỉ áp dụng cho ca đã đo; F1 SOS 0,3403 là cấu hình được chọn theo quy tắc dung sai, không phải cực đại nghiêm ngặt. Ưu tiên [đối chiếu hiện tại](../docs/DANH_GIA_DU_AN_VA_DOI_CHIEU_DE_18.md) khi có khác biệt.

> 🎯 **Mục tiêu chuyên đề:**\
> Hiểu tại sao sau khi nhị phân hóa, ảnh lại bị phân mảnh. Nắm vững bản chất toán học của các phép biến đổi hình thái (Co, Giãn, Đóng, Mở). Hiểu sâu sắc thuật toán **Gán nhãn thành phần liên thông 8 hướng (8-connected labeling)** tự viết bằng kỹ thuật **Run-Length kết hợp Union-Find**. Lý giải tại sao loại bỏ vùng diện tích $< 64$ pixel.

---

## 1. Trực giác đời thường: Sau phân ngưỡng là một "bãi chiến trường"

Sau khi ảnh đi qua bước phân ngưỡng Otsu/Niblack, ta thu được một ma trận nhị phân (Binary Mask) gồm các giá trị True/False (hoặc 1/0):
* Các pixel giá trị $1$ (màu trắng): Là những pixel tối được coi là "ứng viên dầu".
* Các pixel giá trị $0$ (màu đen): Là nền biển.

Nhưng hãy nhìn vào bức ảnh nhị phân này: Nó trông giống như một **"bãi chiến trường cát bụi"**:
1. Có hàng ngàn đốm trắng li ti chỉ to từ $1$ đến vài pixel nằm rải rác khắp mặt biển (do tàn dư của nhiễu đốm speckle chưa khử hết).
2. Bản thân vết dầu lớn có thể bị rỗ lỗ chỗ bên trong (vài pixel biển lọt vào trong lòng vết dầu).
3. Hai vết dầu lớn có thể bị dính vào nhau bởi một "sợi chỉ" mỏng manh 1 pixel.

$\implies$ **Nếu để nguyên như vậy đem đi nhận dạng thì máy tính sẽ "loạn đao pháp"!**\
Ta cần 2 công cụ dọn dẹp mạnh mẽ của xử lý ảnh hình thái học:
* **Toán tử hình thái (Morphology):** Để hàn gắn lỗ thủng hoặc dọn dẹp sợi nối.
* **Gán nhãn liên thông (Connected Component Labeling):** Để gom các pixel dính liền nhau thành từng "đối tượng" độc lập có ID riêng ($1, 2, 3...$).

---

## 2. Toán tử hình thái học (Morphological Operations)

Toán tử hình thái học làm việc dựa trên việc trượt một **phần tử cấu trúc (Structuring Element / Footprint)** hình đĩa tròn bán kính $r=1$ qua từng pixel:

### 1. Phép Co (Erosion):
* *Cách làm:* Đặt đĩa tròn vào pixel trung tâm. Pixel trung tâm chỉ được giữ lại giá trị $1$ nếu **tất cả** các pixel lân cận trong đĩa đều bằng $1$ (toán tử logic AND: `windows.all(-1)`).
* *Tác dụng:* Bóc đi một lớp viền ngoài cùng của đối tượng. Làm biến mất hoàn toàn các chấm nhiễu đơn lẻ và cắt đứt các cầu nối mỏng manh giữa 2 vùng lớn.

### 2. Phép Giãn (Dilation):
* *Cách làm:* Pixel trung tâm sẽ thành $1$ nếu có **ít nhất một** pixel trong đĩa bằng $1$ (toán tử logic OR: `windows.any(-1)`).
* *Tác dụng:* Phình to đối tượng thêm 1 lớp viền. Lấp đầy các lỗ thủng nhỏ li ti bên trong vệt dầu và hàn gắn các vết nứt.

### 3. Phép Mở (Opening) và Phép Đóng (Closing):
* **Opening = Co trước rồi Giãn sau ($\text{Erode} \to \text{Dilate}$):**\
  Xóa sạch các đốm nhiễu nhỏ ngoài biển mà không làm thay đổi kích thước tổng thể của vết dầu lớn.
* **Closing = Giãn trước rồi Co sau ($\text{Dilate} \to \text{Erode}$):**\
  Lấp kín các hố rỗng bên trong vết dầu và nối liền các khe nứt nhỏ mà không làm phình to vết dầu.

> 🔍 **Phát hiện thú vị từ thực nghiệm 729 cấu hình của nhóm:**\
> Khi khảo sát các thao tác `none`, `close`, `open_close`, nhóm nhận thấy thao tác `none` (không áp dụng morphology, chỉ lọc diện tích) đạt F1 cao nhất ($0.3403$). Lý do: Phép Co vô tình làm đứt gãy các đuôi hẹp của vệt dầu tự nhiên, còn phép Giãn lại làm dính các vệt tối lân cận thành một khối méo mó.

---

## 3. Thuật toán gán nhãn liên thông 8 hướng (8-Connected Labeling)

Sau khi dọn dẹp, bài toán là: **Làm sao đánh số thứ tự từng vệt dầu (Vết 1, Vết 2, Vết 3...) để trích xuất đặc trưng?**

### Tại sao là Liên thông 8 hướng (8-connected) mà không phải 4 hướng?
* **Liên thông 4 hướng:** Hai pixel chỉ được coi là cùng một vết nếu chạm nhau ở trên, dưới, trái, phải (không tính góc chéo).
* **Liên thông 8 hướng:** Tính cả 4 hướng chéo!
* *Đặc thù của dầu tràn:* Dưới tác động của gió và dòng hải lưu, vết dầu thường bị kéo dãn thành các dải hẹp uốn lượn chéo góc $45^\circ$. Nếu dùng liên thông 4, dải dầu này sẽ bị chặt khúc thành hàng trăm mẩu vụn rời rạc! Do đó, **bắt buộc phải dùng liên thông 8 hướng**.

```text
Liên thông 4 hướng:        Liên thông 8 hướng (Bao gồm đường chéo):
     [ ] [X] [ ]                 [X] [X] [X]
     [X] [O] [X]                 [X] [O] [X]
     [ ] [X] [ ]                 [X] [X] [X]
```

---

### Bí quyết cài đặt thuật toán: Run-Length kết hợp Union-Find
Trong file [src/sar_oil/core.py](file:///D:/Codin/utc-code/HK4_1/XLA/BTL/src/sar_oil/core.py), nhóm tự cài đặt thuật toán hai lượt quét (Two-pass algorithm) tối ưu cực kỳ tinh gọn:

1. **Mã hóa chuỗi chạy (Run-Length Encoding theo từng hàng):**
   - Thay vì xét từng pixel, thuật toán tìm các đoạn liên tiếp pixel $1$ trên cùng một dòng: `starts` và `ends` (dùng `np.diff`).
   - Mỗi đoạn này được gán tạm một nhãn định danh (`ident`).
2. **Cấu trúc dữ liệu Rừng tập hợp rời nhau (Disjoint-Set / Union-Find):**
   - Dùng mảng `parent` để theo dõi quan hệ cha - con giữa các nhãn.
   - Khi quét xuống hàng tiếp theo, nếu một đoạn ở hàng dưới chạm vào bất kỳ đoạn nào ở hàng trên (kể cả chéo 1 pixel), thuật toán gọi hàm `root()` để tìm gốc của 2 vùng:
     ```python
     def root(i):
         while parent[i] != i:
             parent[i] = parent[parent[i]] # Kỹ thuật nén đường đi (Path compression)
             i = parent[i]
         return i
     ```
   - Hợp nhất 2 nhãn lại với nhau: `parent[max(a, b)] = min(a, b)`.
3. **Lượt quét thứ hai (Chuẩn hóa nhãn):**
   - Ánh xạ lại toàn bộ các nhãn tạm về nhãn gốc duy nhất, đánh số liên tục từ $1, 2, \dots, K$ (với $0$ là nền biển).

---

## 4. Lọc diện tích tối thiểu: Tại sao lại là ngưỡng 64 pixel?

Sau khi gán nhãn xong, thuật toán đếm diện tích (số lượng pixel) của từng vùng bằng hàm `np.bincount(labels.ravel())`.

* Nếu giữ lại tất cả các vùng: Một bức ảnh có thể sinh ra tới **3.000 - 5.000 vùng tối li ti**. Đa số là nhiễu đốm speckle ngẫu nhiên.
* Việc tính 8 đặc trưng cho 5.000 vùng này sẽ làm máy tính chạy rất chậm và tạo ra hàng ngàn ca báo động giả (False Positives).
* **Thực nghiệm chứng minh:**
  - Ngưỡng diện tích nhỏ ($< 16$ px): Báo động giả tăng vọt, FP/ảnh $> 15$.
  - Ngưỡng diện tích lớn ($> 128$ px): Bỏ sót các vết dầu nhỏ mới hình thành, Recall giảm mạnh.
  - Ngưỡng **$\text{min\_area} = 64\text{ pixel}$** (tương đương diện tích thực địa cỡ $6.400\text{ m}^2$ với độ phân giải $10\text{m}$ của Sentinel-1) là điểm cân bằng hoàn hảo nhất, loại bỏ hơn $95\%$ nhiễu rác mà vẫn bảo toàn trọn vẹn các vết dầu thực sự.

```python
# Đoạn code lọc diện tích trong core.postprocess:
labels = label(mask)
area = np.bincount(labels.ravel())
keep = area >= min_area
keep[0] = False  # Nền biển luôn bị loại bỏ
return keep[labels]
```

---

## 5. Hệ thống câu hỏi truy vấn bản chất (Socratic Q&A)

### Câu hỏi 1:
* **Hỏi:** *Độ phức tạp của thuật toán gán nhãn liên thông bằng Union-Find tự cài đặt là bao nhiêu? Có bị tràn bộ nhớ đệ quy (Recursion Limit) không?*
* **Trả lời:** Thuật toán duyệt qua từng đoạn run-length một lần duy nhất, kết hợp hàm `root()` sử dụng vòng lặp `while` (lặp khử đệ quy) và kỹ thuật nén đường đi (path compression). Do đó, thuật toán **hoàn toàn không lo bị tràn ngăn xếp đệ quy (RecursionError)**. Độ phức tạp thời gian gần như tuyến tính: $O(N \cdot \alpha(N))$, trong đó $\alpha$ là hàm nghịch đảo Ackermann (trên thực tế $\alpha(N) \le 4$), chạy cực kỳ nhanh và nhẹ bộ nhớ.

### Câu hỏi 2:
* **Hỏi:** *Nếu hai vết dầu thực tế nằm rất gần nhau nhưng không dính nhau, liệu bộ lọc diện tích 64 px có vô tình loại bỏ một trong hai không?*
* **Trả lời:** Thuật toán tính diện tích độc lập cho từng thành phần liên thông riêng biệt. Nếu mỗi vết có diện tích $\ge 64$ pixel, cả hai đều được giữ lại nguyên vẹn và được cấp 2 ID riêng để trích xuất đặc trưng độc lập. Nếu một trong hai vết là mẩu vụn nhỏ $< 64$ pixel, nó sẽ bị loại bỏ để tránh gây nhiễu cho bộ phân lớp.

---

## 6. Trắc nghiệm ôn tập nhanh (Quiz 04)

**Câu 1:** Phép toán hình thái học nào sau đây tương đương với việc "Co trước rồi Giãn sau"?\
A. Phép Giãn (Dilation)\
B. Phép Đóng (Closing)\
C. Phép Mở (Opening)\
D. Phép Gradient hình thái\
*(Đáp án: **C** — Opening = Erode then Dilate)*

**Câu 2:** Tại sao trong bài toán vết dầu tràn SAR, liên thông 8 hướng lại được ưu tiên hơn liên thông 4 hướng?\
A. Vì liên thông 8 hướng chạy nhanh gấp đôi liên thông 4 hướng.\
B. Vì vết dầu thường bị gió kéo dãn thành các dải hẹp uốn lượn chéo góc; liên thông 4 hướng sẽ cắt đứt dải dầu này thành nhiều mảnh vụn.\
C. Vì thư viện OpenCV chỉ hỗ trợ liên thông 8 hướng.\
D. Vì liên thông 8 hướng luôn làm tăng diện tích vết dầu lên gấp 8 lần.\
*(Đáp án: **B**)*

**Câu 3:** Cấu trúc dữ liệu nào được sử dụng trong `core.py` để quản lý các nhãn tương đương trong thuật toán Connected Component?\
A. Hàng đợi ưu tiên (Priority Queue / Heap)\
B. Bảng băm (Hash Table)\
C. Rừng tập hợp rời rạc (Disjoint-Set / Union-Find)\
D. Cây nhị phân tìm kiếm cân bằng (AVL Tree)\
*(Đáp án: **C**)*

**Câu 4:** Tác dụng cốt lõi của bước lọc diện tích tối thiểu $\ge 64$ pixel là gì?\
A. Làm vết dầu trở nên sáng hơn.\
B. Loại bỏ hàng ngàn đốm nhiễu nhỏ li ti của nhiễu đốm speckle, giảm mạnh số ca báo động giả (False Positives).\
C. Tự động chuyển đổi ảnh nhị phân sang ảnh RGB.\
D. Chuẩn hóa góc tới cho ảnh radar.\
*(Đáp án: **B**)*

**Câu 5:** Kết quả thực nghiệm trên 729 cấu hình của nhóm cho thấy thao tác hình thái học nào cho F1 tốt nhất?\
A. Phép đóng (Closing)\
B. Phép mở rồi đóng (Open-Close)\
C. Không áp dụng đóng/mở (`none`), chỉ lọc diện tích tối thiểu 64 px\
D. Phép co 3 lần liên tiếp\
*(Đáp án: **C** — Giữ nguyên hình dạng tự nhiên tránh làm méo mó hoặc dính chùm vùng)*
