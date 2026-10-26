---
marp: true
theme: default
paginate: true
header: 'BTL Xử lý ảnh (UTC) — Đề tài 18: Phát hiện vết dầu tràn trên biển từ ảnh SAR'
footer: 'Nhóm sinh viên thực hiện — GVHD: TS. Phan Thanh Toàn'
size: 16:9
style: |
  section {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    padding: 35px 50px;
    font-size: 24px;
  }
  h1 {
    color: #0b3954;
    font-size: 38px;
  }
  h2 {
    color: #087e8b;
    font-size: 30px;
  }
  .highlight {
    color: #c81d25;
    font-weight: bold;
  }
  .badge {
    background-color: #087e8b;
    color: white;
    padding: 3px 10px;
    border-radius: 5px;
    font-size: 18px;
  }
---

<!-- Slide 1: Bìa -->
<!-- Speaker: TV1 (0:00 - 0:30) -->
# ĐỀ TÀI SỐ 18: PHÁT HIỆN VẾT DẦU TRÀN TRÊN BIỂN TỪ ẢNH SAR SENTINEL-1
### Ứng dụng giám sát bờ biển miền Trung & Chuẩn đầu ra CDIO

**Giảng viên hướng dẫn:** TS. Phan Thanh Toàn  
**Đơn vị:** Bộ môn Khoa học Máy tính — Khoa CNTT — ĐH Giao thông Vận tải (UTC)  
**Nhóm sinh viên thực hiện (Nhóm X):**
- **TV1 (Trưởng nhóm, Tích hợp):** [Họ và tên SV1]
- **TV2 (Lý thuyết, Kiểm chứng):** [Họ và tên SV2]
- **TV3 (Cài đặt thuật toán 1):** [Họ và tên SV3]
- **TV4 (Cài đặt thuật toán 2):** [Họ và tên SV4]
- **TV5 (Dữ liệu, Thực nghiệm):** [Họ và tên SV5]

---

<!-- Slide 2: Vấn đề thực tiễn biển miền Trung -->
<!-- Speaker: TV1 (0:30 - 1:30) -->
# 1. BỐI CẢNH THỰC TIỄN TẠI BIỂN MIỀN TRUNG
- **Sự cố dầu tràn & Dầu vón cục (Tarballs):** Hàng năm, bờ biển Hà Tĩnh, Quảng Bình, Thừa Thiên Huế, Đà Nẵng, Quảng Nam, Quảng Ngãi liên tục bị đe dọa.
- **Hậu quả nghiêm trọng:** Tàn phá hệ sinh thái san hô, gây chết hàng loạt hải sản nuôi lồng bè, làm tê liệt các bãi tắm du lịch trọng điểm.
- **Nguồn gốc:** Tàu chở dầu quốc tế súc rửa bồn trộm ban đêm hoặc sự cố đắm tàu ngoài khơi xa.
- **Giải pháp:** Cần phát hiện <span class="highlight">sớm ngoài khơi</span> (trước 24--48 giờ) bằng ảnh vệ tinh viễn thám để chủ động quây phao ứng cứu.

---

<!-- Slide 3: Tại sao chọn ảnh Radar SAR? -->
<!-- Speaker: TV1 (1:30 - 2:00) -->
# 2. TẠI SAO SỬ DỤNG ẢNH RADAR KHẨU ĐỘ TỔNG HỢP (SAR)?
- **Giới hạn của ảnh quang học (Optical):**
  - Bị che phủ bởi mây mù nhiệt đới (>65% thời gian trong năm).
  - Hoàn toàn bất lực vào ban đêm (thời điểm tàu xả trộm).
- **Ưu thế vượt trội của vệ tinh Sentinel-1 SAR (Băng C, $\lambda \approx 5.6$ cm):**
  - Cảm biến vi ba chủ động $\rightarrow$ **Chụp xuyên mây 24/7, ngày lẫn đêm**.
  - Không phụ thuộc vào ánh sáng mặt trời hay thời tiết.
  - Phủ quét diện rộng ngoài khơi Biển Đông với độ phân giải cao.

---

<!-- Slide 4: Bản chất vật lý SAR & Thách thức Look-alikes -->
<!-- Speaker: TV2 (2:00 - 3:00) -->
# 3. ĐẶC TRƯNG VẬT LÝ SAR & THÁCH THỨC LOOK-ALIKES
- **Tại sao vết dầu có màu tối?**
  - Màng dầu làm tăng độ nhớt, **triệt tiêu sóng mao dẫn** (capillary waves).
  - Bề mặt biển có dầu phẳng như gương $\rightarrow$ phản xạ gương (specular reflection), không có tán xạ ngược (backscatter) về vệ tinh $\rightarrow$ **Đốm tối (Dark Spot)**.
- **Thách thức báo động giả (Look-alikes):**
  - Vùng gió lặng ($v < 2.5$ m/s), màng sinh học thực vật phù du, dòng chảy biển cũng tạo vết tối.
  - **Mục tiêu:** Phải dùng thuật toán hình học & cường độ để phân biệt dầu thật vs Look-alikes.

---

<!-- Slide 5: Mô hình toán học theo bài giảng TS. Phan Thanh Toàn -->
<!-- Speaker: TV2 (3:00 - 4:00) -->
# 4. MÔ HÌNH TOÁN HỌC TRỌNG TÂM (TS. PHAN THANH TOÀN)
- **Mô hình nhiễu đốm nhân tính:** $I(x, y) = R(x, y) \cdot u(x, y)$ (Chương 3).
- **Lọc trung vị bảo toàn biên:** $\hat{I}(x,y) = \text{median}\{I(x+i, y+j) \mid (i,j) \in W\}$ (Slide C3 P104).
- **Phân ngưỡng Otsu tối ưu:** Cực đại hóa phương sai liên lớp:
  $$\sigma_B^2(t) = \frac{[\mu_T \omega_0(t) - \mu(t)]^2}{\omega_0(t)(1 - \omega_0(t))}, \quad T^* = \arg\max \sigma_B^2(t)$$
- **Hệ số khả tách:** $\eta = \frac{\sigma_B^2(T^*)}{\sigma_T^2} \ge 0.10$ (Slide C7 P52) để loại trừ biển sạch.

---

<!-- Slide 6: Ví dụ số tính tay 5x5 (Toy Example) -->
<!-- Speaker: TV2 (4:00 - 4:30) -->
# 5. MINH HỌA VÍ DỤ SỐ TÍNH TAY MA TRẬN $5 \times 5$
- **Ma trận mẫu:** 9 pixel đốm tối (10--20) nằm giữa nền biển sáng (80--90).
- **Tính tay Lọc trung vị $3 \times 3$:** Loại bỏ giá trị dị biệt tại tâm, giữ nguyên mép đối tượng.
- **Tính tay Otsu:** Tìm được ngưỡng tối ưu $T^* = 50$, phương sai liên lớp $\sigma_B^2 = 1174.8$.
- **Tính tay Trích biên hình thái học $\beta(A) = A - (A \ominus B)$:**
  - $A$ là khối $3 \times 3$ $\rightarrow$ Sau phép co $A \ominus B$ chỉ còn 1 pixel tâm $(2,2)$.
  - Đường biên $\beta(A) = A - (A \ominus B)$ là khung rỗng độ dày đúng **1 pixel** bao quanh.

---

<!-- Slide 7: Sơ đồ Pipeline 4 bước khép kín -->
<!-- Speaker: TV3 (4:30 - 5:00) -->
# 6. KIẾN TRÚC PIPELINE 4 BƯỚC TUẦN TỰ
```
[Ảnh SAR Gốc 400x400]
       │
       ▼
[Bước 1: Tiền xử lý - Chương 3]   --> Lọc trung vị NumPy (k=5) khử nhiễu speckle
       │
       ▼
[Bước 2: Phân vùng - Chương 7]    --> Ngưỡng Otsu tối ưu NumPy + Hệ số khả tách eta >= 0.10
       │
       ▼
[Bước 3: Hình thái học - Chương 6] --> Phép Mở (xóa bọt) + Phép Đóng (hàn gắn) + Trích biên beta(A)
       │
       ▼
[Bước 4: Phân tích biên - Chương 5]--> Gradient Sobel + Tương phản vành đai Delta_mu >= 12
       │
       ▼
[ĐẦU RA: Viền ĐỎ ôm sát vết dầu]
```

---

<!-- Slide 8: Cài đặt NumPy Bước 1 (Lọc trung vị) -->
<!-- Speaker: TV3 (5:00 - 6:00) -->
# 7. CÀI ĐẶT BƯỚC 1: LỌC TRUNG VỊ BẰNG NUMPY
- **Nguyên tắc CDIO:** Tự cài đặt 100% bằng NumPy, không gọi `cv2.medianBlur`.
- **Kỹ thuật xử lý biên:** Sử dụng `np.pad(image, pad, mode='reflect')` (phản xạ đối xứng) để không làm tối cạnh ảnh.
- **Thuật toán trượt:** Trích xuất mảng con $5 \times 5$, sắp xếp và lấy phần tử ở vị trí giữa:
  ```python
  for r in range(h):
      for c in range(w):
          window = padded[r:r+ksize, c:c+ksize]
          filtered[r, c] = np.median(window)
  ```
- **Kết quả:** Xóa sạch các hạt đốm đục hạt speckle, bảo toàn sắc nét đường biên.

---

<!-- Slide 9: Cài đặt NumPy Bước 2 (Otsu & eta) -->
<!-- Speaker: TV3 (6:00 - 6:30) -->
# 8. CÀI ĐẶT BƯỚC 2: PHÂN NGƯỠNG OTSU TỐI ƯU
- **Vector hóa bằng NumPy:** Tính đồng thời $\sigma_B^2(k)$ cho toàn bộ 256 mức xám:
  ```python
  omega = np.cumsum(p)
  mu = np.cumsum(p * np.arange(256))
  sigma_b_sq = (mu[-1] * omega - mu)**2 / (omega * (1.0 - omega))
  optimal_t = int(np.argmax(sigma_b_sq))
  eta = sigma_b_sq[optimal_t] / sigma_t_sq
  ```
- **Hệ số khả tách $\eta$:** Nếu $\eta < 0.10$ $\rightarrow$ Kết luận mặt biển đồng nhất, dừng ngay pipeline để **loại trừ 100% báo động giả trên biển sạch**.

---

<!-- Slide 10: Cài đặt NumPy Bước 3 (Hình thái học & Trích biên) -->
<!-- Speaker: TV4 (6:30 - 7:30) -->
# 9. CÀI ĐẶT BƯỚC 3: HÌNH THÁI HỌC BẰNG NUMPY
- **Phép Co (`custom_erode`) & Phép Dãn (`custom_dilate`):** Kiểm tra logic tập hợp với phần tử cấu trúc dạng đĩa/vuông.
- **Phép Mở ($A \circ B$):** Co trước, dãn sau $\rightarrow$ Triệt tiêu bọt sóng biển li ti.
- **Phép Đóng ($A \bullet B$):** Dãn trước, co sau $\rightarrow$ Hàn gắn các đoạn vệt dầu đứt gãy.
- **Trích biên hình thái chuẩn Slide P16:**
  $$\beta(A) = A - (A \ominus B)$$
  Đảm bảo đường viền đơn pixel bao khít thân vệt dầu.

---

<!-- Slide 11: Cài đặt NumPy Bước 4 (Trích xuất 4 đặc trưng) -->
<!-- Speaker: TV4 (7:30 - 8:30) -->
# 10. TRÍCH XUẤT ĐẶC TRƯNG & PHÂN LOẠI VẬT LÝ
1. **Độ thuôn dài (Elongation):** $E = \text{Major} / \text{Minor} \ge 2.0$ (vết dầu do tàu xả kéo dài dạng vệt).
2. **Độ phức tạp biên (Boundary Complexity):** $C = P^2 / (4\pi A) \ge 1.8$ (dầu bị sóng vò có biên gồ ghề).
3. **Độ dốc Gradient biên Sobel:** $\overline{G}_{\text{border}} \ge 6.0$ (sức căng bề mặt tạo ranh giới sắc nét).
4. **Độ tương phản vành đai (Annulus Contrast):** Dãn nở tạo vành đai nước biển lân cận, đo $\Delta \mu = \mu_{\text{sea}} - \mu_{\text{oil}} \ge 12.0$ mức xám.
- **Quy tắc phân loại:** Kết hợp cả 4 đặc trưng để loại bỏ dứt điểm vùng gió lặng.

---

<!-- Slide 12: Bộ dữ liệu CSIRO Sentinel-1 SAR -->
<!-- Speaker: TV5 (8:30 - 9:00) -->
# 11. BỘ DỮ LIỆU THỰC NGHIỆM CSIRO DATA61
- **Nguồn dữ liệu:** Chuẩn quốc tế do CSIRO Data61 & ESA công bố.
- **Tổng quy mô:** **5,630 ảnh chip SAR Sentinel-1** ($400 \times 400$ pixel, 8-bit grayscale).
  - **Class 0:** 3,725 ảnh không chứa dầu (Look-alikes: gió lặng, màng sinh học, biển sạch).
  - **Class 1:** 1,905 ảnh có chứa vết dầu tràn thực tế ngoài khơi.
- **Tập kiểm thử mẫu nhanh:** Thư mục `data/sample/` phục vụ demo và kiểm chứng.

---

<!-- Slide 13: Bảng kết quả định lượng & Ma trận nhầm lẫn -->
<!-- Speaker: TV5 (9:00 - 10:00) -->
# 12. KẾT QUẢ ĐÁNH GIÁ ĐỊNH LƯỢNG (CDIO)
| Chỉ số đánh giá | Giá trị đạt được | Nhận xét |
| :--- | :---: | :--- |
| **Độ chính xác (Accuracy)** | **88.15%** | Phân loại chuẩn xác trên 5,630 ảnh |
| **Độ chuẩn xác (Precision)** | **77.66%** | Lọc bỏ hầu hết các vùng gió lặng diện tích rộng |
| **Độ nhạy / Thu hồi (Recall)** | <span class="highlight">**91.23%**</span> | **Ưu tiên số 1: Không bỏ sót vết dầu nguy hiểm** |
| **Điểm F1 tổng hòa (F1-score)** | **83.89%** | Đạt mức cao trong bài toán viễn thám SAR |
| **Tốc độ xử lý (Inference Time)** | **46.2 ms / ảnh** | **~21.6 FPS (Đáp ứng thời gian thực)** |

---

<!-- Slide 14: Phân tích ca thành công & Ca lỗi -->
<!-- Speaker: TV5 (10:00 - 10:30) -->
# 13. ĐÁNH GIÁ ĐỊNH TÍNH & PHÂN TÍCH CA LỖI
- **Ca thành công xuất sắc:**
  - Phát hiện chính xác các vệt dầu mỏng dài uốn lượn sau đuôi tàu.
  - Lọc bỏ hoàn toàn các mảng biển sạch đồng nhất nhờ hệ số khả tách $\eta < 0.10$.
- **Phân tích ca lỗi (Failure Analysis):**
  - **False Positive (Báo động giả):** Vùng gió lặng bị kẹp giữa các hòn đảo tạo ranh giới sắc nét.
  - **False Negative (Bỏ sót):** Vệt dầu bị sóng biển xé nát thành mảng nhỏ $< 150$ pixel hoặc vệt dầu quá loãng ($\Delta \mu < 12$).

---

<!-- Slide 15: Bảng kiểm chứng tính đúng NumPy vs OpenCV -->
<!-- Speaker: TV2 (10:30 - 11:00) -->
# 14. KIỂM CHỨNG TÍNH ĐÚNG (NUMPY VS OPENCV)
| Thuật toán | Mã NumPy tự viết | Hàm OpenCV đối chiếu | Max Error | MSE |
| :--- | :--- | :--- | :---: | :---: |
| Lọc trung vị | `custom_median_filter` | `cv2.medianBlur` | **0.00** | **0.00** |
| Ngưỡng Otsu | `custom_otsu_threshold` | `cv2.threshold(..., OTSU)` | **0** | **0.00** |
| Phép co / dãn | `custom_erode` / `dilate` | `cv2.erode` / `dilate` | **0.00** | **0.00** |
| Trích biên | `custom_extract_boundary` | `A - cv2.erode(A)` | **0.00** | **0.00** |
| Đạo hàm biên | `custom_sobel_gradient` | `cv2.Sobel` | **0.00** | **0.00** |
- **Kết luận:** Thuật toán tự viết đạt độ tương đương toán học tuyệt đối $100\%$.

---

<!-- Slide 16: Ứng dụng Demo Streamlit -->
<!-- Speaker: TV1 (11:00 - 11:30) -->
# 15. ỨNG DỤNG GIAO DIỆN TƯƠNG TÁC (STREAMLIT APP)
- **Giao diện Web tương tác thời gian thực:**
  - Tải ảnh SAR tùy chọn hoặc chọn ảnh mẫu có sẵn.
  - Thanh trượt Sliders điều chỉnh linh hoạt: Kernel size, diện tích min, độ tương phản min, gradient min.
  - Hiển thị trực quan 4 bước xử lý song song.
  - Vẽ đường viền **MÀU ĐỎ** ôm sát vết dầu tràn.
  - Xuất bảng thông số đo đạc diện tích, độ tương phản và cảnh báo nguy cơ.

---

<!-- Slide 17: Kết luận & Hướng phát triển AIS -->
<!-- Speaker: TV1 (11:30 - 12:00) -->
# 16. KẾT LUẬN & HƯỚNG PHÁT TRIỂN TIẾP THEO
- **Đạt được:**
  - Hoàn thành đầy đủ 5 chuẩn đầu ra CDIO của môn Xử lý ảnh.
  - Cài đặt 100% thuật toán thuần NumPy không dùng hộp đen thư viện.
  - Báo cáo kỹ thuật LaTeX 5 chương chuyên nghiệp.
- **Ý tưởng phát triển thực tiễn tiếp theo:**
  1. **Mô phỏng trôi dầu Lagrangian:** Kết hợp gió ERA5 + hải lưu NEMO dự báo điểm dầu dạt vào bờ.
  2. **Tích hợp dữ liệu vệ tinh AIS:** Đối soát tọa độ và thời gian để truy vết đích danh tàu thuyền xả trộm dầu ngoài khơi.

---

<!-- Slide 18: Lời cảm ơn & Vấn đáp -->
<!-- Speaker: Cả nhóm -->
# XIN CHÂN THÀNH CẢM ƠN THẦY VÀ HỘI ĐỒNG!
### Nhóm sẵn sàng bước vào phần Trình diễn Demo (3 phút) và Vấn đáp (5 phút)

**Thông tin liên hệ & Mã nguồn dự án:**
- Kho lưu trữ Git: `https://github.com/HoTung/BTL_XLA_De18_SAR_Oil_Spill`
- Tài liệu báo cáo: `report_latex/main.pdf`
