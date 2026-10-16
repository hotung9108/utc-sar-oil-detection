# ==============================================================================
# AGENT INSTRUCTION & PROJECT DIRECTIVE (AGENTS.md)
# Project: Đề 18. Phát hiện vết dầu tràn trên biển từ ảnh SAR (★★★) — NASA #6
# Course: Xử lý ảnh / Computer Vision — UTC (Đại học Giao thông vận tải)
# Target Application: Giám sát vùng biển Việt Nam & Bờ biển miền Trung
# ==============================================================================

> [!IMPORTANT]
> ### 🚨 CHỈ THỊ ĐẶC BIỆT DÀNH CHO AGENT (HIỆN TẠI - CURRENT PHASE):
> 1. **CHỈ SỬ DỤNG THUẬT TOÁN COMPUTER VISION THUẦN TÚY (PURE COMPUTER VISION)**:
>    - Trọng tâm tuyệt đối ở giai đoạn này là nghiên cứu và lập trình các thuật toán xử lý ảnh truyền thống: Lọc nhiễu đốm (Speckle filtering), chuẩn hóa dải động, phân ngưỡng thích nghi (Adaptive thresholding), hình thái học (Morphology), phân đoạn và trích xuất vùng ứng viên (Candidate detection & Segmentation).
> 2. **CHƯA ĐỘNG ĐẾN HUẤN LUYỆN MODEL HAY MACHINE LEARNING**:
>    - **TUYỆT ĐỐI KHÔNG** nhảy vào train model (SVM, Decision Tree, Random Forest, Deep Learning...) hay chạy pipeline Machine Learning ở bước này khi chưa có yêu cầu cụ thể từ người dùng.
> 3. **HỖ TRỢ SONG SONG MATLAB VÀ PYTHON**:
>    - Hỗ trợ xây dựng thuật toán trên cả **MATLAB** (sử dụng *Image Processing Toolbox*: `medfilt2`, `wiener2`, `adapthisteq`, `adaptthresh`, `imbinarize`, `bwareaopen`, `imclose`, `imfill`, `regionprops`...) và/hoặc **Python** (`cv2`, `scikit-image`, `scipy.ndimage`, `numpy`).
> 4. **PHÁT HIỆN VẾT DẦU DỰA TRÊN TRI THỨC HÌNH THÁI (HEURISTIC / RULE-BASED CV)**:
>    - Phân biệt bước đầu giữa vệt dầu và các vùng nhiễu/nền dựa trực tiếp vào các ngưỡng hình học & cường độ (Elongation, Compactness/Complexity, Border Gradient, Contrast với nền lân cận) bằng các quy tắc xử lý ảnh toán học.

---

## 1. TỔNG QUAN DỰ ÁN & MỤC TIÊU BÀI TOÁN

### 1.1. Bối cảnh thực tiễn tại Việt Nam
- **Vấn đề**: Hàng năm, các tỉnh ven biển miền Trung (Hà Tĩnh, Quảng Bình, Quảng Trị, Thừa Thiên Huế, Đà Nẵng, Quảng Nam, Quảng Ngãi, Bình Định...) thường xuyên hứng chịu hiện tượng dầu vón cục và các vệt dầu trôi dạt vào bờ biển. Hiện tượng này đe dọa nghiêm trọng hệ sinh thái biển, hủy hoại tài nguyên thủy hải sản và tàn phá ngành du lịch địa phương.
- **Thách thức**: Việc giám sát quang học truyền thống bị giới hạn bởi mây mù và bóng tối. Ảnh radar khẩu độ tổng hợp (**SAR - Synthetic Aperture Radar**) từ vệ tinh Sentinel-1 có khả năng chụp xuyên mây, hoạt động cả ngày lẫn đêm, là công cụ tối ưu để phát hiện sớm các vệt dầu loang ngoài khơi trước khi chúng dạt vào bờ.
- **Đặc trưng vật lý SAR**: Vết dầu làm phẳng các sóng mao dẫn bề mặt đại dương (capillary waves), làm giảm tán xạ ngược (backscatter) của tín hiệu radar trở về máy thu, dẫn đến các vệt màu tối (dark spots) trên ảnh SAR. Tuy nhiên, các hiện tượng tự nhiên như vùng gió lặng (low wind zones), màng sinh học (biogenic slicks), vùng mưa (rain cells) cũng tạo ra vết tối tương tự (**Look-alikes**), gây ra tỉ lệ báo động giả cao.

### 1.2. Lộ trình kỹ thuật bài toán (Focus: Computer Vision)
1. **Giai đoạn 1 (TRỌNG TÂM HIỆN TẠI - Computer Vision thuần túy)**:
   - **Lọc nhiễu đốm (Speckle Filtering)**: Lọc Lee, Frost, Kuan, Wiener hoặc Adaptive Median.
   - **Chuẩn hóa & Tăng cường tương phản**: Chuẩn hóa góc tới, CLAHE (Contrast Limited Adaptive Histogram Equalization).
   - **Phân ngưỡng thích nghi (Adaptive Thresholding)**: Sauvola, Niblack, Otsu cục bộ, phân ngưỡng theo độ lệch chuẩn nền biển.
   - **Xử lý hình thái học (Morphological Operations)**: Opening, Closing, Fill holes, loại bỏ đốm nhiễu nhỏ (`bwareaopen` / diện tích tối thiểu).
   - **Phát hiện & Khoanh vùng đốm tối ứng viên (Candidate Dark Spots)**: Trích xuất đường bao (Contours / Connected Components), bounding box, tính toán tâm và mặt nạ đối tượng.
   - **Trích xuất đặc trưng thị giác (Visual Feature Extraction)**: Độ thuôn dài (Elongation), độ phức tạp biên (Boundary Complexity), gradient biên (Border Gradient), độ tương phản với nền biển lân cận.
   - **Phát hiện rule-based / heuristic CV**: Đặt ngưỡng logic dựa trên các đặc trưng hình thái để khoanh vùng vệt dầu khả nghi trực tiếp từ thuật toán xử lý ảnh.
2. **Giai đoạn 2 (Sau này - Machine Learning)**:
   - Đóng gói vector đặc trưng, phân chia tập Train/Val/Test, huấn luyện SVM / Decision Tree / Random Forest để phân loại chi tiết Dầu vs Look-alikes. *(Tạm thời CHƯA thực hiện)*.
3. **Giai đoạn 3 (Ý tưởng mở rộng)**:
   - Mô phỏng trôi dầu Lagrangian (gió ERA5 + dòng chảy đại dương).
   - Đối soát dữ liệu AIS truy vết tàu xả thải.

---

## 2. KIẾN TRÚC DỮ LIỆU & TỔ CHỨC DỰ ÁN

### 2.1. Cấu trúc dữ liệu hiện có
Dự án sử dụng bộ dữ liệu chuẩn **CSIRO Sentinel-1 SAR Oil/Non-oil Dataset**:
- Kích thước ảnh: Grayscale 1 kênh, độ phân giải $400 \times 400$ pixel (chips JPEG).
- Phân bố dữ liệu:
  * `data/Class_0/`: **3,725 ảnh** — Không chứa dầu (Look-alikes: vùng gió lặng, màng sinh học thực vật phù du, dòng biển, biển sạch).
  * `data/Class_1/`: **1,905 ảnh** — Có chứa vết dầu tràn thực tế (Oil slicks).
  * `data/sample/`: Thư mục ảnh mẫu kiểm thử nhanh cho Class 0 và Class 1.
  * `metadata/`: File `dataset_metadata.xml`, `dataset_readme.md` mô tả bộ dữ liệu.

### 2.2. Cấu trúc tổ chức mã nguồn (Hỗ trợ cả MATLAB và Python)
```
BTL/
├── .agents                         # Directive file cho Agent (file này)
├── AGENTS.md                       # Bản sao đồng bộ của .agents
├── data/                           # Thư mục dữ liệu gốc (Class_0, Class_1, sample)
├── metadata/                       # Thư mục metadata chuẩn từ CSIRO
│
├── matlab/                         # CÁC THUẬT TOÁN COMPUTER VISION TRÊN MATLAB
│   ├── main_detection_demo.m       # Kịch bản chính chạy demo xử lý ảnh & detect
│   ├── lee_filter.m                # Thuật toán lọc nhiễu đốm Lee Filter
│   ├── adaptive_thresholding.m     # Phân ngưỡng thích nghi (Sauvola / Local Otsu)
│   ├── morphological_cleanup.m     # Tinh chỉnh hình thái học (bwareaopen, imclose, imfill)
│   ├── extract_features.m          # Trích xuất độ thuôn dài, tương phản, gradient biên
│   └── visualize_results.m         # Vẽ 4 bước xử lý và hiển thị vệt dầu phát hiện
│
├── src/                            # CÁC THUẬT TOÁN COMPUTER VISION TRÊN PYTHON (nếu dùng)
│   ├── preprocessing/
│   │   ├── speckle_filter.py       # Lọc Lee, Frost, Bilateral, Wiener
│   │   ├── normalization.py        # Chuẩn hóa mức xám, CLAHE
│   │   └── candidate_detector.py   # Phân ngưỡng thích nghi & hình thái học
│   ├── features/
│   │   ├── shape_features.py       # Độ thuôn dài, chu vi, diện tích, độ phức tạp
│   │   └── intensity_features.py   # Gradient biên, độ tương phản vành khuyên
│   └── utils/
│       └── visualization.py        # Hiển thị trực quan các bước phân đoạn ảnh
│
├── outputs/                        # Thư mục lưu ảnh kết quả trực quan (so sánh 4 bước)
└── requirements.txt                # Thư viện Python (nếu chạy kèm Python)
```

---

## 3. THÔNG SỐ & CÔNG THỨC THUẬT TOÁN COMPUTER VISION CHI TIẾT

### 3.1. Thuật toán Lọc nhiễu đốm SAR (Speckle Filtering)
1. **Bộ lọc Lee (Lee Filter)**:
   - Dựa trên mô hình tán xạ đa hợp (multiplicative noise model): $I(x,y) = R(x,y) \cdot u(x,y)$ với $u$ có trung bình 1, phương sai $\sigma_u^2$.
   - Tính toán trung bình cục bộ $\mu_k$ và phương sai cục bộ $\sigma_k^2$ trong cửa sổ trượt $W \times W$ (thường chọn $5 \times 5$ hoặc $7 \times 7$):
     $$\hat{R}(x,y) = \mu_k + W_k \cdot (I(x,y) - \mu_k)$$
     $$W_k = \max\left(0, 1 - \frac{C_u^2}{C_i^2}\right), \quad C_u = \frac{\sigma_u}{\mu_u}, \quad C_i = \frac{\sigma_k}{\mu_k}$$
   - *Trên MATLAB*: Có thể triển khai hàm tự viết `lee_filter.m` hoặc kết hợp `wiener2(I, [5 5])` / `medfilt2(I, [5 5])`.
   - *Trên Python*: Triển khai vector hóa với `scipy.ndimage.uniform_filter`.

### 3.2. Tăng cường tương phản & Chuẩn hóa
1. **CLAHE (Contrast Limited Adaptive Histogram Equalization)**:
   - Cân bằng lược đồ xám cục bộ có giới hạn độ tương phản nhằm làm rõ sự khác biệt giữa nền biển và vệt dầu mà không khuếch đại nhiễu đốm.
   - *MATLAB*: `adapthisteq(I, 'ClipLimit', 0.02, 'Distribution', 'rayleigh')`
   - *Python*: `cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))`

### 3.3. Phân ngưỡng thích nghi tìm đốm tối (Adaptive Dark Spot Segmentation)
1. **Ngưỡng Sauvola / Niblack**:
   - Thích ứng với biến thiên độ sáng nền biển theo góc chụp:
     $$T(x,y) = \mu_{local}(x,y) \cdot \left[1 + k \cdot \left(\frac{\sigma_{local}(x,y)}{R} - 1\right)\right]$$
     (với $R = 128$, $k \approx 0.2$, kích thước cửa sổ $31 \times 31$ hoặc $41 \times 41$).
2. **Ngưỡng theo độ lệch chuẩn nền biển (Statistical Sea Clutter Thresholding)**:
   - Xác định ngưỡng cắt đốm tối: $T_{dark} = \mu_{sea} - k \cdot \sigma_{sea}$ ($k \in [1.5, 2.5]$).
   - Pixel nào có giá trị $I(x,y) < T_{dark}$ được xem là thuộc vùng tối ứng viên.

### 3.4. Xử lý hình thái học (Morphological Operations)
1. **Lọc nhiễu nhỏ & lấp lỗ trống**:
   - `Opening` ($3 \times 3$ hoặc $5 \times 5$) để loại bỏ đốm nhiễu li ti do sóng biển.
   - `Closing` ($5 \times 5$ hoặc $7 \times 7$) để hàn gắn các đoạn vệt dầu bị đứt quãng do nhiễu đốm.
   - `Hole Filling` để lấp đầy các vùng khuyết bên trong thân vệt dầu.
   - `Area Thresholding` (`bwareaopen` trong MATLAB / `cv2.contourArea` trong Python): Loại bỏ các vùng có diện tích $Area < 50$ px.

### 3.5. Trích xuất đặc trưng hình thái & Cường độ (Pure CV Feature Extraction)
Với mỗi vùng ứng viên (Connected Component / Blob $R_i$):
1. **Độ thuôn dài (Elongation / Aspect Ratio)**:
   - Tính từ trục chính ($MajorAxis$) và trục phụ ($MinorAxis$) của elip tương đương (`regionprops`):
     $$Elongation = \frac{MajorAxisLength}{MinorAxisLength} \ge 1.0$$
   - *Ý nghĩa*: Vệt dầu do tàu thuyền xả thải khi di chuyển thường kéo dài dạng dải mỏng ngoằn ngoèo ($Elongation \gg 3$), trong khi vệt gió lặng thường có hình mảng rộng bè ($Elongation \approx 1 - 2$).
2. **Độ phức tạp biên (Boundary Complexity / Circularity)**:
   - Tỉ lệ chu vi bình phương trên diện tích:
     $$Complexity = \frac{Perimeter^2}{4 \pi \cdot Area}$$
   - *Ý nghĩa*: Vết dầu bị sóng và dòng biển vò nát có biên gấp khúc, phức tạp cao hơn so với màng trơn.
3. **Độ dốc gradient đường biên (Border Gradient Sharpness)**:
   - Tính toán gradient biên bằng toán tử Sobel ($G = \sqrt{G_x^2 + G_y^2}$).
   - Lấy giá trị gradient trung bình dọc theo đường contour $\partial R$:
     $$\overline{G}_{border} = \frac{1}{|\partial R|} \sum_{(x,y) \in \partial R} G(x,y)$$
   - *Ý nghĩa*: Sức căng bề mặt của dầu làm ranh giới giữa dầu và nước biển có độ dốc tán xạ rất sắc nét, trong khi ranh giới vùng gió giảm thường chuyển tiếp thoai thoải.
4. **Độ tương phản với nền biển lân cận (Annulus Background Contrast)**:
   - Tạo vùng vành đai biển $\Omega_{bg}$ bao quanh vết dầu bằng phép giãn nở hình thái (Dilation 7 px) trừ đi chính vết dầu:
     $$\Delta \mu = \mu_{bg} - \mu_{oil}$$
     $$Damping\ Ratio = \frac{\mu_{bg}}{\mu_{oil}}$$
   - *Ý nghĩa*: Vết dầu có độ suy giảm tín hiệu mạnh ($Damping\ Ratio > 1.5 - 2.5$).

### 3.6. Quy tắc phát hiện ứng viên dầu (Heuristic CV Detection Rules)
Khi chưa sử dụng Machine Learning, hệ thống có thể kết luận một đốm tối là "Vết dầu nghi vấn" (Suspected Oil Slick) nếu thỏa mãn bộ tiêu chí:
- Diện tích $Area \ge A_{min}$ (ví dụ $\ge 60$ pixel)
- Độ suy giảm tương phản $Damping\ Ratio \ge 1.35$ (hoặc $\Delta \mu \ge 15$ mức xám)
- Gradient biên $\overline{G}_{border} \ge G_{min}$ (đủ sắc nét)
- Độ thuôn dài $Elongation \ge 2.0$ (dạng vệt dài của dầu) hoặc Độ phức tạp biên $Complexity \ge 2.5$

---

## 4. HƯỚNG DẪN HOẠT ĐỘNG DÀNH CHO AGENT (OPERATING RULES)

1. **Tuân thủ đúng giai đoạn phát triển**:
   - Khi người dùng yêu cầu lập trình hay tối ưu, chỉ tập trung vào **các giải thuật Computer Vision (Xử lý ảnh)**.
   - **KHÔNG tự ý viết code huấn luyện Machine Learning/Deep Learning** khi chưa có chỉ thị mới.
2. **Ưu tiên giải thuật trực quan, có thể triển khai trên MATLAB hoặc Python**:
   - Cung cấp mã nguồn MATLAB (.m) rõ ràng, chuẩn phong cách Image Processing Toolbox nếu người dùng yêu cầu MATLAB.
   - Nếu viết Python, sử dụng thuần túy `numpy`, `scipy`, `cv2`, `matplotlib`, `skimage`.
3. **Luôn chú trọng trực quan hóa (Visual Output)**:
   - Kết quả phân tích ảnh phải luôn xuất ra hình so sánh trực quan 4 bước:
     `[Ảnh SAR gốc] -> [Sau lọc Speckle / CLAHE] -> [Mặt nạ nhị phân sau phân ngưỡng thích nghi & Morphology] -> [Khoanh vùng vết dầu với Contours & Thông số diện tích/độ dài]`.
4. **Gắn liền bài toán thực tế biển miền Trung**:
   - Trong các thông báo, chú thích hoặc tài liệu kỹ thuật, luôn thể hiện mối liên hệ với bài toán giám sát dầu tràn/dầu vón cục ngoài khơi biển miền Trung Việt Nam.
