# Chuyên đề 01: Bản chất vật lý viễn thám SAR & Cơ chế vết dầu tràn

> **Phạm vi tài liệu tự học — cập nhật 17/11/2026:** đây là giải thích và mã minh họa độc lập, không phải pipeline đã nghiệm thu hoặc bằng chứng đạt 100% đề. Công thức giản lược, ảnh giả lập, ví dụ ghép greedy và mô phỏng trôi dầu không thay thế kết quả trong `src/sar_oil`, `scripts` và `results`. Lee không bảo đảm giữ biên tuyệt đối; agreement 100% chỉ áp dụng cho ca đã đo; F1 SOS 0,3403 là cấu hình được chọn theo quy tắc dung sai, không phải cực đại nghiêm ngặt. Ưu tiên [đối chiếu hiện tại](../docs/DANH_GIA_DU_AN_VA_DOI_CHIEU_DE_18.md) khi có khác biệt.

> 🎯 **Mục tiêu chuyên đề:**\
> Giúp bạn hiểu từ trực giác đời thường nhất: SAR là gì? Tại sao chụp ảnh không cần ánh sáng mặt trời mà vẫn xuyên qua mây mù? Tại sao mặt biển lại sáng còn vết dầu lại tối đen? Và tại sao các vùng không có dầu đôi khi cũng đen (hiện tượng tương tự dầu - look-alike)?

---

## 1. Trực giác đời thường: Ảnh quang học vs. Ảnh Radar SAR

Hãy tưởng tượng bạn đang tìm một vết dầu tràn trên biển miền Trung vào một đêm bão gió mịt mù:
* **Ảnh quang học (như camera điện thoại, vệ tinh Google Maps, Landsat, Sentinel-2):**
  - Giống như mắt người: Nó phụ thuộc vào **ánh sáng mặt trời** chiếu xuống rồi phản xạ lại.
  - *Hạn chế chí mạng:* Trời tối $\to$ mù tịt. Trời có mây mù, mưa bão $\to$ chỉ chụp được đỉnh mây trắng xóa, không thể nhìn thấy mặt biển bên dưới. Trong khi đó, các vụ xả trộm dầu và tai nạn tràn dầu lại hay xảy ra vào ban đêm hoặc trong thời tiết xấu!
* **Ảnh Radar SAR (Synthetic Aperture Radar — Radar khẩu độ tổng hợp, như Sentinel-1):**
  - Hoạt động giống như **con dơi phát sóng siêu âm**: Vệ tinh mang theo một máy phát sóng vi ba (microwave, thường là băng C bước sóng cỡ $5.6\text{ cm}$). Nó tự phát xung sóng xuống trái đất rồi "lắng nghe" tín hiệu dội ngược trở lại (gọi là **tán xạ ngược — Backscatter**).
  - *Ưu điểm tuyệt đối:*
    1. **Bất chấp ngày đêm:** Tự phát sóng nên chụp đêm cũng sáng rõ như ngày.
    2. **Xuyên mây, xuyên sương mù:** Bước sóng vi ba cỡ vài centimet dễ dàng đi xuyên qua các giọt nước li ti của mây mù mà không bị tán xạ hay cản trở.

---

## 2. Tại sao mặt biển lại sáng mà vết dầu lại tối đen?

Đây là câu hỏi kinh điển nhất của mọi giảng viên khi chấm đề tài dầu tràn SAR. Hãy nắm chắc cơ chế 2 bước sau:

### Bước 1: Mặt biển bình thường trông như thế nào dưới mắt Radar? (Tán xạ Bragg)
* Trên mặt biển luôn có gió thổi. Gió tạo ra những con sóng lăn tăn rất nhỏ, có bước sóng vài centimet (gọi là **sóng mao dẫn — capillary waves** hoặc sóng trọng lực ngắn).
* Khi bước sóng của radar ($\lambda$) và bước sóng của sóng biển ($\Lambda$) thỏa mãn điều kiện cộng hưởng Bragg:
  $$\Lambda = \frac{\lambda}{2 \sin \theta}$$
  *(trong đó $\theta$ là góc tới — incidence angle của tia radar)*
* Hiện tượng **tán xạ Bragg** xảy ra: Hàng triệu con sóng lăn tăn này hoạt động như những gương phản xạ nhỏ, làm sóng radar bị tán xạ tứ phía, và một lượng lớn năng lượng dội ngược thẳng về vệ tinh.
* $\implies$ **Kết quả:** Mặt biển bình thường hiển thị thành một vùng có **mức xám sáng (độ phản xạ cao)** trên ảnh SAR.

```text
       Vệ tinh phát sóng
            \     ^  (Sóng dội ngược về ăng-ten mạnh)
             \   /
              \ /
   ~~~~/\_/\_/\_/\_/\_/\~~~~   (Mặt biển có sóng lăn tăn - Tán xạ Bragg)
```

---

### Bước 2: Khi có dầu tràn, chuyện gì xảy ra? (Hiệu ứng dập sóng - Damping Effect)
* Dầu thô có độ nhớt (viscosity) cao hơn nước biển rất nhiều và có lực căng bề mặt đặc biệt.
* Khi dầu nổi trên mặt nước, màng dầu triệt tiêu năng lượng của gió, **dập tắt hoàn toàn các sóng mao dẫn lăn tăn**. Mặt biển nơi có màng dầu trở nên phẳng lặng như một tấm gương.
* Khi sóng radar chiếu vào mặt dầu phẳng: Thay vì tán xạ tứ phía dội ngược về vệ tinh, sóng radar bị **phản xạ gương (Specular reflection)** trượt thẳng đi hướng khác (văng ra xa vào không gian).
* Ăn-ten vệ tinh hầu như không nhận được tín hiệu dội ngược về (Backscatter cực thấp).
* $\implies$ **Kết quả:** Vùng có dầu hiển thị thành một **vệt tối đen (Dark Spot)** nổi bật trên nền biển sáng!

```text
       Vệ tinh phát sóng
            \
             \
              \       ---> Sóng trượt đi mất (Phản xạ gương)
   _______________________   (Màng dầu dập sóng, phẳng như gương)
```

---

## 3. Cạm bẫy lớn nhất: Hiện tượng tương tự dầu (Look-alikes)

Nếu bài toán chỉ đơn giản là: *"Cứ thấy vùng đen trên biển là dầu tràn"*, thì chỉ cần một lệnh IF đơn giản là xong, không cần đến xử lý ảnh hay học máy!\
Nhưng trên thực tế, biển có rất nhiều hiện tượng tự nhiên làm mặt nước bị phẳng và tạo ra vệt đen giống hệt dầu tràn. Những hiện tượng này gọi là **Look-alikes (Kẻ giả mạo)**:

1. **Vùng gió yếu (Low wind areas):** Khi tốc độ gió $< 2-3\text{ m/s}$, không đủ sức tạo sóng mao dẫn, mặt biển tự nhiên cũng phẳng như gương $\to$ Tạo thành các mảng tối khổng lồ.
2. **Màng sinh học tự nhiên (Biogenic slicks):** Do tảo biển hoặc sinh vật phù du chết phân hủy tiết ra chất nhờn hữu cơ, cũng dập tắt sóng mao dẫn giống hệt dầu khoáng.
3. **Mưa rào trên biển (Rain cells):** Những hạt mưa lớn rơi xuống biển làm phẳng mặt nước tạm thời và giọt mưa trong không khí làm suy hao tín hiệu vi ba $\to$ Tạo vệt tối.
4. **Bóng địa hình ven bờ (Wind shadow):** Các hòn đảo hoặc dãy núi ven biển chắn gió, tạo ra vùng biển phẳng lặng khuất gió phía sau $\to$ Vệt tối kéo dài từ bờ.

> ⚠️ **Nhiệm vụ cốt lõi của đề tài:**\
> Không chỉ là tìm ra các vùng tối (bằng cách phân ngưỡng), mà quan trọng hơn là **phải dùng đặc trưng hình học, độ tương phản và mô hình học máy (SVM/CART) để loại bỏ các look-alikes này**, chỉ giữ lại dầu tràn thực sự!

---

## 4. Hệ thống câu hỏi truy vấn bản chất (Socratic Q&A)

### Câu hỏi 1 (Mức cơ bản):
* **Hỏi:** *Một pixel trên ảnh SAR có giá trị mức xám từ 0 đến 255. Giá trị này thực chất đại diện cho đại lượng vật lý gì? Có phải là màu sắc của nước biển không?*
* **Trả lời:** Không phải màu sắc! Ảnh SAR là ảnh đơn sắc (grayscale). Giá trị pixel thể hiện **cường độ tán xạ ngược (Radar Backscatter Intensity)**, tức là đo xem bao nhiêu năng lượng vi ba dội ngược về ăng-ten vệ tinh. Pixel càng sáng nghĩa là sóng dội về càng mạnh (mặt biển gồ ghề nhám), pixel càng tối nghĩa là sóng dội về càng yếu (mặt biển phẳng lặng hoặc dập sóng).

### Câu hỏi 2 (Mức đào sâu):
* **Hỏi:** *Tại sao đề bài lại yêu cầu "Chuẩn hóa theo góc tới (Incidence angle)"? Góc tới ảnh hưởng thế nào đến độ sáng của ảnh?*
* **Trả lời:** Vệ tinh radar nhìn nghiêng xuống mặt đất. Những vùng biển ở cự ly gần (Near range, góc tới nhỏ $\approx 20^\circ-30^\circ$) nhận được sóng dội về rất mạnh nên nền biển rất sáng. Càng ra xa (Far range, góc tới lớn $\approx 40^\circ-45^\circ$), năng lượng dội về càng yếu nên nền biển tự nhiên bị tối dần đi. Nếu không chuẩn hóa góc tới, một thuật toán phân ngưỡng toàn cục sẽ bị nhầm lẫn: vùng biển ở xa dù không có dầu cũng bị coi là vết tối, còn vết dầu ở gần do nền quá sáng nên bị bỏ sót!

### Câu hỏi 3 (Mức nâng cao - Đối phó câu hỏi khó của Hội đồng):
* **Hỏi:** *Bộ dữ liệu SOS của nhóm dùng ảnh PNG. Ảnh PNG này có chuẩn hóa góc tới vật lý được không? Nhóm đã xử lý vấn đề này như thế nào?*
* **Trả lời sắc bén:** Thưa thầy/cô, ảnh PNG trong bộ SOS là ảnh 8-bit đã bị cắt thành các patch nhỏ $256\times 256$ hoặc $512\times 512$ và bị loại bỏ siêu dữ liệu (metadata) góc tới. Vì vậy, **về mặt vật lý, không thể chuẩn hóa góc tới trên ảnh PNG**. Phép chia cho 255 trong code chỉ là đưa mức xám về khoảng $[0, 1]$ để tính toán số học, không phải chuẩn hóa góc tới. Nhóm nhận thức rất rõ điều này, không ngụy biện, và đã chủ động xây dựng thêm nhánh **Cantarell trên ảnh Sentinel-1 gốc (định dạng float32 kèm file LUT góc tới)** để chứng minh nhóm nắm vững bản chất chuẩn hóa bức xạ $\sigma^0$ và $\gamma^0$.

---

## 5. Trắc nghiệm ôn tập nhanh (Quiz 01)

**Câu 1:** Cơ chế vật lý nào khiến mặt biển bình thường xuất hiện sáng trên ảnh radar SAR?\
A. Phản xạ gương của ánh sáng mặt trời.\
B. Tán xạ Bragg trên các sóng mao dẫn ngắn.\
C. Nước biển phát xạ nhiệt hồng ngoại.\
D. Khúc xạ của sóng vô tuyến trong lòng đại dương.\
*(Đáp án: **B** — Tán xạ Bragg dội năng lượng về ăng-ten)*

**Câu 2:** Tại sao màng dầu trên mặt biển lại hiển thị thành vùng tối đen trên ảnh SAR?\
A. Vì dầu thô có màu đen hấp thụ toàn bộ sóng ánh sáng.\
B. Vì dầu làm tăng nhiệt độ nước biển.\
C. Vì dầu dập tắt sóng mao dẫn, biến mặt biển thành mặt phẳng phản xạ gương làm sóng radar văng đi hướng khác.\
D. Vì dầu phản xạ toàn phần sóng radar dội ngược thẳng về vệ tinh.\
*(Đáp án: **C** — Phản xạ gương hướng đi nơi khác khiến ăng-ten không nhận được tín hiệu)*

**Câu 3:** Hiện tượng nào sau đây **KHÔNG PHẢI** là hiện tượng tương tự dầu (Look-alike) trên ảnh SAR?\
A. Vùng biển lặng gió có tốc độ gió dưới 2 m/s.\
B. Vùng biển có màng sinh học do tảo phân hủy.\
C. Vùng có vết dầu do tàu thuyền xả thải trộm.\
D. Vùng biển khuất gió sau một hòn đảo cao.\
*(Đáp án: **C** — Vết dầu xả thải là dầu thật, không phải look-alike)*

**Câu 4:** Nếu không chuẩn hóa góc tới (Incidence Angle) trên ảnh SAR diện rộng, điều gì sẽ xảy ra?\
A. Ảnh bị đảo ngược màu trắng thành đen.\
B. Vùng cự ly xa (Far range) tự nhiên bị tối hơn cự ly gần (Near range), gây báo động giả khi phân ngưỡng.\
C. Ảnh bị mất toàn bộ độ phân giải không gian.\
D. Vết dầu tự động biến mất khỏi ảnh.\
*(Đáp án: **B** — Góc tới lớn làm tán xạ ngược giảm tự nhiên)*

**Câu 5:** Lấy giá trị pixel ảnh PNG chia cho 255 có phải là chuẩn hóa góc tới không?\
A. Phải, vì nó đưa giá trị về $[0, 1]$.\
B. Phải, vì đó là công thức chuẩn trong thư viện OpenCV.\
C. Không, đó chỉ là chuẩn hóa giá trị mức xám số học, chuẩn hóa góc tới đòi hỏi bảng tra cứu góc tới vật lý (LUT) từ metadata vệ tinh.\
D. Cả A và B đều đúng.\
*(Đáp án: **C** — Cần phân biệt rạch ròi chuẩn hóa số học và hiệu chỉnh vật lý)*
