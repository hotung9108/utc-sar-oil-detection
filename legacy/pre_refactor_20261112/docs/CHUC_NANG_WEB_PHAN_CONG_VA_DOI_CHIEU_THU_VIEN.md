# Chức năng web, phần việc thành viên và đối chiếu thư viện

Tài liệu dùng để trình bày hệ thống hiện tại. Các chức năng dưới đây được đối chiếu trực tiếp với mã nguồn và kết quả trong dự án. Phần việc cá nhân được ghi theo bảng phân công hiện tại; đây không phải xác nhận lịch sử ai đã tự viết từng dòng mã hoặc đã hoàn thành việc học.

## 1. Giới thiệu hệ thống trong khoảng một phút

“Nhóm xây dựng ứng dụng Streamlit để khảo sát khử nhiễu, tăng tương phản và xử lý biên trên ảnh SAR. Người dùng có thể tải ảnh hoặc chọn ảnh sẵn có, thay các thuật toán và tham số, rồi xem ảnh ở từng công đoạn. Phần lõi được tự cài đặt bằng NumPy. Ngoài bản đồ biên, hệ thống có nhánh phân đoạn và lọc vùng tối ứng viên bằng Otsu, hình thái học, diện tích và tương phản với nền. Nhóm còn xây dựng bộ kiểm chứng so với OpenCV và SciPy, cùng các thí nghiệm trên dữ liệu. Hệ thống không dùng mô hình học máy hay học sâu. Kết quả được gọi là vùng ứng viên vì một vùng tối trên ảnh radar chưa đủ để xác nhận dầu.”

## 2. Chạy ứng dụng ở đâu?

Từ thư mục gốc dự án:

```powershell
.venv\Scripts\python.exe -m streamlit run streamlit_app.py
```

Mở địa chỉ mà terminal hiển thị, mặc định là `http://localhost:8501`. Đây là ứng dụng web chạy cục bộ; tài liệu này không xác nhận ứng dụng đã được triển khai lên một website công khai.

Mã giao diện chính: [streamlit_app.py](../streamlit_app.py).

## 3. Các chức năng đã có trên web

### 3.1. Chọn và chuẩn bị ảnh đầu vào

| Chức năng | Hành vi hiện tại | Vị trí mã |
| --- | --- | --- |
| Tải ảnh từ máy | Nhận PNG, JPG/JPEG, BMP, TIF/TIFF qua hộp tải ảnh | `streamlit_app.py`, khối `st.file_uploader` |
| Chọn ảnh mẫu | Đọc ảnh trong `data/sample/`, thêm ảnh `class_1_00013.jpg` nếu có | `streamlit_app.py`, nhánh `Ảnh mẫu` |
| Chọn ảnh trong dataset | Chọn `Class_0` hoặc `Class_1`, tìm tên ảnh trong danh sách cục bộ `kaggle/data/` | `streamlit_app.py`, nhánh `Dataset Kaggle` |
| Chuẩn hóa đầu vào | Giải mã thành ảnh xám, đổi kích thước về 400 × 400 | `cv2.imdecode`, `cv2.resize` trong `streamlit_app.py` |
| Báo lỗi đầu vào | Thông báo nếu không giải mã được ảnh hoặc dữ liệu không hợp lệ | Khối `try/except` trong `streamlit_app.py` |

“Dataset Kaggle” là tên lựa chọn dữ liệu đã tải về máy, không phải chức năng tải ảnh trực tiếp từ Kaggle qua mạng. Định dạng TIFF được tiếp nhận như một ảnh để giải mã; hệ thống chưa có quy trình đọc/hiệu chuẩn dữ liệu Sentinel-1 SAFE, xử lý tọa độ địa lý hoặc khôi phục đơn vị tán xạ ngược.

### 3.2. Khử nhiễu

Các lựa chọn: `none`, `box`, `gaussian`, `median`, `bilateral`, `lee`, `frost`, `kuan`. Có 7 bộ lọc và một lựa chọn bỏ qua lọc, không phải 8 thuật toán khử nhiễu.

Người dùng chọn cửa sổ 3, 5, 7 hoặc 9; tham số L từ 1 đến 16 được truyền cho Lee/Kuan trong pipeline. Mặc định là Lee, cửa sổ 5 × 5, L = 4. Không phải mọi bộ lọc đều dùng mọi tham số trên thanh bên.

Mã cài đặt: [src/tv3/filters.py](../src/tv3/filters.py). Mã chọn và gọi bộ lọc: [src/tv1/pipeline.py](../src/tv1/pipeline.py), hàm `process_image()`.

### 3.3. Tăng tương phản

Các lựa chọn: `none`, `log`, `he`, `clahe`, `homomorphic`. Có 4 phương pháp và một lựa chọn bỏ qua. CLAHE cho thay clip limit từ 0,5 đến 5 và lưới 1, 2, 4, 8 hoặc 16 ô mỗi chiều; mặc định clip = 2, grid = 8 × 8.

Mã cài đặt: [src/tv3/enhancement.py](../src/tv3/enhancement.py). Các hàm cần đọc: `log_transform()`, `global_histogram_equalization()`, `custom_clahe()`, `homomorphic_filter()`.

### 3.4. Làm nét để quan sát

Các lựa chọn: `none`, `unsharp`, `laplacian`, `sobel`; hệ số làm nét trên giao diện từ 0 đến 3. Trong mã hiện tại, hệ số này được dùng cho unsharp và Laplacian; nhánh làm nét Sobel gọi cấu hình của chính hàm đó.

Làm nét tạo ảnh hiển thị. Nhánh biên và mask sử dụng ảnh trước làm nét, nên thay hệ số làm nét không phải cách trực tiếp thay mask ứng viên.

Mã: [src/tv4/sharpening.py](../src/tv4/sharpening.py), cùng đoạn tạo `displayed` trong `process_image()`.

### 3.5. Phát hiện biên và tạo mask vùng tối

| Chế độ | Đầu ra và cách hiểu |
| --- | --- |
| `canny` | Bản đồ biên sau Gaussian, gradient, NMS, ngưỡng kép và liên kết biên |
| `sobel`, `prewitt`, `roberts` | Bản đồ biên từ đáp ứng biến thiên mức xám, được chọn theo ngưỡng trong pipeline |
| `log` | Biên từ đổi dấu đáp ứng Laplacian of Gaussian |
| `morphology` | Mask vùng tối ứng viên và đường biên trích từ mask sau phân ngưỡng, hình thái và lọc vùng |

Trong nhánh morphology, hệ thống có Otsu toàn cục kèm quy tắc chọn ảnh nguồn/điều chỉnh ngưỡng; mở hình thái; đóng hình thái; gán nhãn liên thông 8 hướng; lọc diện tích; lọc tỷ số tương phản vùng/nền; trích biên và phủ lên ảnh gốc.

Tham số có thể đổi: diện tích tối thiểu, tương phản tối thiểu, bán kính closing, bật/tắt điều chỉnh Otsu và dùng ngưỡng mức xám thủ công. Bán kính opening hiện cố định bằng 2 trong mã. Kernel vành nền là hình vuông 15 × 15, không phải một nút chỉnh riêng trên web.

Ngưỡng Canny thấp/cao mặc định 35/90. Ngưỡng cao trên web có thể tới 1.020 ở chế độ Canny. Các phương pháp khác không nhất thiết sử dụng cả ngưỡng thấp lẫn cao theo cùng cách.

Mã: [src/tv4/edges.py](../src/tv4/edges.py), [src/tv4/morphology.py](../src/tv4/morphology.py). Hàm kết nối toàn bộ nhánh mask là `detect_oil_slick_morphological()`.

### 3.6. Bốn tab trên giao diện

| Tab | Chức năng đã có |
| --- | --- |
| Kết quả ảnh | Hiện ảnh gốc, ảnh sau lọc, sau tăng tương phản, sau làm nét, mask/bản đồ biên và ảnh chồng đường biên |
| Chỉ số và phân tích | Hiện ENL, SSI, RMS contrast, entropy, AMBE, EPI; vẽ histogram và lát cắt mức xám theo hàng do người dùng chọn |
| Đối chiếu thư viện | Hiện bảng CSV tổng hợp đã lưu và cho tải bảng; không chạy đối chiếu mới trên ảnh người dùng đang chọn |
| Phân công TV1–TV5 | Hiện họ tên, tài khoản GitHub và phần phụ trách từ `docs/management/thanh_vien.json` |

Ở nhánh morphology, tab kết quả còn hiện số vùng, phần trăm diện tích, ngưỡng phân đoạn và bảng từng vùng gồm diện tích, hộp bao, tâm hình học, mức xám trung bình vùng/nền, tỷ số tương phản. Nhánh chỉ tìm biên trả `mask=None`, không báo số pixel biên thành diện tích dầu.

### 3.7. Tải kết quả

- `enhanced.png`: ảnh tăng tương phản.
- `boundary.png`: bản đồ biên.
- `mask.png`: chỉ có khi nhánh xử lý trả mask.
- `sar_result.json`: cấu hình, chỉ số ảnh và thống kê vùng của lần chạy.
- `comparison_summary.csv`: bảng đối chiếu thư viện đã lưu.

Trình duyệt quyết định thư mục tải xuống. Web không tự lưu mọi lần đổi tham số vào `results/`, và hiện chưa có nút chạy toàn bộ dataset trong giao diện.

## 4. Phần việc của năm thành viên đã được hiện thực trong dự án

Bảng này nối trách nhiệm với sản phẩm đang có. Khi trình bày nên nói “phần được phân công phụ trách đã có các chức năng…”; mức đóng góp và việc tự viết mã cần nhóm xác nhận thực tế.

| Thành viên | Phần được phân công | Những phần đã có trong mã/sản phẩm | File nên mở khi bảo vệ |
| --- | --- | --- | --- |
| TV1 - Tiến Sơn Trần | Tích hợp, giao diện, cấu hình, báo cáo chung | Giao diện 4 tab; nhận ảnh; chọn tham số; gọi pipeline; giữ reference trước CLAHE; trả ảnh/mask/chỉ số; tải PNG/JSON; kiểm tra dữ liệu đầu vào | `streamlit_app.py`, `src/tv1/pipeline.py`, `src/tv1/validation.py`, `src/tv1/utils.py` |
| TV2 - Lương Tiến Dũng | Cơ sở lý thuyết, tính tay và kiểm chứng | Danh sách 33 phép toán/cấu hình đối chiếu; 18 ảnh kiểm tra; sai số từng ca; phân loại direct/composition/variant; 5 ví dụ số chung đã kiểm chứng | `src/tv2/library_comparison.py`, `src/tv2/verification.py` |
| TV3 - Hồ Việt Tùng | Lọc và tăng tương phản | Box, Gaussian, Median, Bilateral, Lee, Frost, Kuan; log, HE, CLAHE, homomorphic; xử lý kiểu số, padding, histogram, CDF và nội suy | `src/tv3/filters.py`, `src/tv3/enhancement.py` |
| TV4 - Nguyễn Hải Hiếu | Làm nét, biên, Otsu, hình thái | Unsharp/Laplacian/Sobel; Roberts/Prewitt/Sobel/LoG/Canny; Otsu; co/giãn/mở/đóng; liên thông; lọc diện tích và tương phản; vẽ biên | `src/tv4/sharpening.py`, `src/tv4/edges.py`, `src/tv4/morphology.py` |
| TV5 - Phạm Minh Tuấn | Dữ liệu, chỉ số, thí nghiệm và tái lập | ENL/SSI/RMS/entropy/AMBE/EPI; khảo sát phương pháp và tham số; điều kiện bất lợi; đánh giá cấp ảnh trên 5.538 ảnh; xuất CSV/JSON/PNG và manifest | `src/tv5/metrics.py`, `src/tv5/experiments.py`, `reproduce.py` |

Thư mục `src/tv1` đến `src/tv5` chứa triển khai theo phân công. Những file ngắn như `src/pipeline.py`, `src/filters.py`, `src/library_comparison.py` chủ yếu là lớp tái xuất để giữ đường dẫn import; nếu muốn đọc thuật toán thật, mở file bên trong `src/tvN/`.

### Câu nói mẫu cho từng người

- **TV1:** “Phần em phụ trách ghép các thuật toán thành quy trình thống nhất, cho người dùng đổi cấu hình và theo dõi ảnh ở từng công đoạn. Em phân biệt rõ ảnh hiển thị, bản đồ biên và mask để giao diện không báo nhầm diện tích.”
- **TV2:** “Phần em phụ trách kiểm tra cách tính. Với cùng dữ liệu và tham số, em đối chiếu đầu ra tự cài với hàm thư viện hoặc phép ghép đối chứng, rồi báo sai số và những trường hợp khác biến thể.”
- **TV3:** “Phần em phụ trách giảm dao động ảnh và làm rõ tương phản. Em cần giải thích tác dụng của cửa sổ Lee, tham số L, histogram và clip limit, đồng thời chỉ ra nguy cơ làm mờ vệt hoặc làm nổi nhiễu.”
- **TV4:** “Phần em phụ trách tìm biên và vùng ứng viên. Biên từ gradient khác biên từ mask; các phép hình thái và tiêu chí vùng giúp lọc kết quả nhưng chưa xác nhận được nguyên nhân vật lý là dầu.”
- **TV5:** “Phần em phụ trách dữ liệu và đánh giá. Em tách kiểm chứng số học khỏi đánh giá chất lượng ảnh và khỏi quyết định có ứng viên ở cấp ảnh; các chỉ số không được dùng vượt phạm vi mà nhãn dữ liệu cho phép.”

## 5. Muốn xem so sánh với thư viện thì mở file nào trước?

**File quan trọng nhất: [src/tv2/library_comparison.py](../src/tv2/library_comparison.py).**

Đọc theo thứ tự sau; số dòng theo trạng thái hiện tại, tên hàm là mốc ổn định hơn khi mã thay đổi:

| Thứ tự | Hàm / vị trí | Nội dung cần xem |
| --- | --- | --- |
| 1 | `registry()`, khoảng dòng 153 | Ghép thuật toán tự cài với hàm thư viện; tham số; kiểu đối chiếu; giới hạn sai số |
| 2 | `cases()`, khoảng dòng 466 | Tạo 8 ảnh tổng hợp và đọc 10 ảnh mẫu, tổng 18 đầu vào |
| 3 | `run_comparisons()`, khoảng dòng 486 | Chạy hai hàm trên cùng ảnh, so kích thước, tính sai số, ghi PASS/FAIL/DESCRIPTIVE |
| 4 | Đoạn xuất CSV, khoảng dòng 527 | Lưu từng ca vào `per_case.csv`, tổng hợp vào `summary.csv` |
| 5 | `lee_reference()`, khoảng dòng 41 | Ví dụ phép ghép đối chứng Lee bằng moment từ SciPy |

Để xem thuật toán tự cài tương ứng, quay sang `src/tv3/filters.py`, `src/tv3/enhancement.py` hoặc `src/tv4/edges.py`, `src/tv4/morphology.py`.

Ví dụ đối chiếu CLAHE trong `registry()` có thể đọc ngắn gọn như sau:

```python
custom = e.custom_clahe
reference = lambda a: cv2.createCLAHE(2, (8, 8)).apply(a)
kind = "direct"
max_error_limit = 1
```

Đoạn trên là cách diễn giải mục cấu hình, không phải sửa hàm CLAHE để ép kết quả đẹp hơn. Hai bên cần cùng đầu vào, clip limit, lưới, quy ước biên và làm tròn. Nếu khác quy ước thì phải giải thích trước khi kết luận sai cài đặt.

## 6. Kết quả so sánh đã nằm ở đâu?

| File | Khi nào nên xem |
| --- | --- |
| [results/verification/summary.csv](../results/verification/summary.csv) | Xem nhanh mỗi thuật toán có bao nhiêu ca và sai số tổng hợp; đây là bảng chính trên web |
| [results/verification/per_case.csv](../results/verification/per_case.csv) | Xem thuật toán nào trên ảnh nào bị lệch; có tên đối chứng, giới hạn, verdict, thời gian cả hai phía và chỉ số biên ở một số phép |
| [results/verification/environment.json](../results/verification/environment.json) | Xem phiên bản Python, NumPy, OpenCV, SciPy và phạm vi phép kiểm chứng |
| [results/verification/hand_examples.json](../results/verification/hand_examples.json) | Xem expected/actual của 5 ví dụ tính tay chung |
| [docs/report/evidence/verification_summary.csv](report/evidence/verification_summary.csv) | Bản dự phòng mà web đọc nếu chưa có bảng `results/verification/summary.csv` |

Trong `streamlit_app.py`, tìm `with tab_verify:` để xem cách web đọc CSV. Web **hiển thị kết quả đã lưu**, chưa có nút tự chạy OpenCV/SciPy rồi hiển thị hai ảnh đối chứng mới cho ảnh đang chọn.

## 7. Cách đọc các cột và kết luận hiện có

- `max_abs_error`: phần tử lệch lớn nhất giữa đầu ra tự cài và đối chứng. Trong summary là giá trị lớn nhất qua các ca.
- `mse`: trung bình bình phương sai khác của một ca; `mse_mean` là trung bình MSE qua các ca.
- `agreement_pct`: tỷ lệ phần tử bằng nhau tuyệt đối. Với số thực, chênh lệch rất nhỏ có thể làm tỷ lệ này thấp dù sai số gần 0.
- `limit`: giới hạn sai số tối đa của phép kiểm chứng. Mã hiện gán PASS dựa trên `max_abs_error <= limit`, không phải dựa trên MSE.
- `custom_ms`, `reference_ms`: thời gian đo cho từng bên ở một ca. Bảng summary hiện chỉ tổng hợp thời gian phía tự cài; muốn so tốc độ phải đọc per_case và chú ý phép đo một lần.
- `edge_f1_exact`: mức khớp điểm biên của hai cài đặt, không phải F1 phát hiện dầu so với mask nhãn thật.

Ba kiểu đối chiếu:

| Kiểu | Ý nghĩa | Ví dụ |
| --- | --- | --- |
| `direct` | Có hàm thư viện tương ứng để đối chiếu | HE với `cv2.equalizeHist`; CLAHE với `cv2.createCLAHE`; Sobel với `cv2.Sobel` |
| `composition` | Ghép các phép thư viện và công thức để tạo đối chứng | Lee dùng moment SciPy rồi cùng công thức Lee; không có hàm Lee độc lập được gọi trong bộ đối chứng |
| `variant` | Hai biến thể có khác biệt đã biết; báo mô tả, không tính PASS | Bilateral: footprint; Canny: chi tiết làm mảnh, hướng và xử lý biên |

Kết quả hiện lưu gồm **33 phép toán/cấu hình × 18 ảnh = 594 ca: 558 PASS, 36 DESCRIPTIVE, 0 FAIL**. DESCRIPTIVE không có nghĩa là đã đạt hay thất bại; nó không có ngưỡng PASS/FAIL trong cấu hình hiện tại.

| Phép toán | Kiểu | Sai số tuyệt đối lớn nhất | MSE trung bình qua 18 ca | Cách diễn giải |
| --- | --- | --- | --- | --- |
| Lee | composition | 0 | 0 | Khớp đối chứng ghép moment SciPy trong phạm vi thử |
| HE | direct | 0 | 0 | Khớp kết quả OpenCV trên các ca đã thử |
| CLAHE | direct | 1 | 0,0001302083 | Có sai khác nhỏ, nằm trong giới hạn 1 của phép kiểm chứng |
| Sobel | direct | 0 | 0 | Khớp các đại lượng đang được so sánh |
| Otsu | direct | 0 | 0 | Khớp đại lượng trong bộ đối chứng |
| Bilateral | variant | 20 | 2,0078886 | Khác footprint, chỉ báo mô tả |
| Canny | variant | 255 | 32,7775977 | Có điểm biên nhị phân khác nhau, chỉ báo mô tả |

Với bản đồ biên 0/255, chỉ một pixel khác cũng có thể làm sai số tối đa bằng 255; con số này không tự nói có bao nhiêu điểm khác. Ngược lại, nhiều pixel nền đen giống nhau có thể làm tỷ lệ agreement rất cao dù đường biên chưa khớp tốt.

**Kết luận đúng khi bảo vệ:** kiểm chứng trên đây cho thấy mức khớp tính toán của các cài đặt trong phạm vi thử. Nó không chứng minh nhận diện dầu chính xác, không chứng minh thuật toán tự cài tốt hơn thư viện, và không phải tất cả 594 ca đều trùng tuyệt đối.

## 8. Lệnh chạy lại các phép kiểm chứng

Chạy từ gốc dự án; các lệnh này tạo lại kết quả trong thư mục tương ứng:

```powershell
# Chạy đối chiếu thư viện, xuất results/verification/
.venv\Scripts\python.exe -m src.library_comparison

# Chạy cả 5 ví dụ tính tay chung rồi đối chiếu thư viện
.venv\Scripts\python.exe -m src.verification

# Kiểm chứng và khảo sát ảnh mẫu, không chạy toàn bộ dataset
.venv\Scripts\python.exe reproduce.py --samples-only

# Kiểm chứng, khảo sát ảnh mẫu và đánh giá toàn bộ dataset cục bộ
.venv\Scripts\python.exe reproduce.py --workers 4
```

Không cần chạy toàn bộ dataset chỉ để mở web hoặc xem bảng đã lưu. Lệnh `--samples-only` cập nhật manifest thành phạm vi mẫu; không dùng manifest đó để khẳng định vừa chạy lại toàn tập.

## 9. Tiền xử lý có cần thiết không? Bằng chứng đã bổ sung

Đối với mục tiêu học và khảo sát, cần có khử nhiễu/tăng tương phản để thực hiện đúng nội dung đề tài. Đối với từng ảnh và từng tiêu chí đầu ra, chưa thể khẳng định bắt buộc dùng cả Lee và CLAHE mới có kết quả tốt. Phải có cấu hình không dùng làm mốc đối chiếu.

Đã chạy thí nghiệm ghép cặp bốn cấu hình trên cùng 10 ảnh mẫu, và kiểm tra riêng ảnh 00013; giữ nguyên tham số phía sau. Đây là khảo sát nhỏ, chưa phải so sánh toàn bộ 5.538 ảnh.

| Cấu hình | Mật độ biên Canny (%) TB ± SD | Diện tích mask ứng viên (%) TB ± SD |
| --- | --- | --- |
| Không Lee, không CLAHE | 4,928 ± 7,430 | 22,557 ± 22,625 |
| Chỉ Lee | 0,631 ± 0,717 | 22,226 ± 22,804 |
| Chỉ CLAHE | 13,149 ± 11,948 | 20,046 ± 21,246 |
| Lee + CLAHE | 7,685 ± 7,963 | 20,716 ± 20,756 |

Lee làm giảm nhiều đáp ứng biên ở cấu hình này; CLAHE làm tăng đáp ứng biên, kể cả từ nền. Nhiều hay ít biên đều chưa đủ để kết luận tốt hơn: cần biết biên thật nằm ở đâu. Thí nghiệm giữ ngưỡng Canny 35/90 nên đo tác động của tiền xử lý khi giữ tham số sau cố định, chưa đo hiệu quả tốt nhất của từng phương án sau khi chỉnh ngưỡng riêng.

Riêng ảnh 00013: không tiền xử lý giữ 3.302 pixel (2,06%); Lee giữ 3.328 pixel (2,08%). Thêm CLAHE không đổi mask trong từng cặp tương ứng: A với C bằng nhau từng pixel; B với D cũng bằng nhau từng pixel. Nhưng Canny từ 0 điểm biên ở A/B trở thành khoảng 0,489% ở C và 0,327% ở D. Điều này phù hợp nhánh dùng reference: tăng tương phản có thể giúp bộc lộ biên để quan sát mà không đổi mask cuối của ảnh này. Giữa mask A và B có 104 pixel đổi trạng thái, dù diện tích ròng chỉ tăng 26 pixel.

Kết quả và hình:

- [Bảng từng ảnh](../results/preprocessing_ablation/per_image.csv), [bảng trung bình và độ lệch chuẩn](../results/preprocessing_ablation/summary.csv).
- [Hình bốn cấu hình trên ảnh 00013](../results/preprocessing_ablation/class_1_00013_comparison.png).
- [Hình bốn cấu hình trên ảnh nền biển](../results/preprocessing_ablation/sea_surface_01_comparison.png).
- Mã chạy: [scripts/compare_preprocessing_ablation.py](../scripts/compare_preprocessing_ablation.py); mã dựng hình: [scripts/plot_preprocessing_ablation.py](../scripts/plot_preprocessing_ablation.py).

Chưa có ảnh sạch chuẩn và mask pixel chuẩn, nên chưa thể kết luận Lee + CLAHE làm nhận diện dầu chính xác hơn. Cần tập mask gán tay độc lập để kiểm tra đường bao và vùng; đồng thời khảo sát tham số riêng trên tập phát triển rồi đánh giá trên tập khác.

## 10. Tên đề tài có khớp hệ thống không?

Tên “Tăng cường độ tương phản, khử nhiễu và xử lý biên bộc lộ vết dầu tràn trên biển từ ảnh radar SAR Sentinel-1” phù hợp về hướng xử lý ảnh. Metadata cục bộ xác nhận dữ liệu là các chip JPEG xám 400 × 400 cắt từ cảnh Sentinel-1 đã xử lý, nên có cơ sở ghi Sentinel-1. Nhóm chưa xây dựng xử lý radar thô hoặc xác nhận dầu ngoài thực địa.

Nếu được phép chỉnh cách diễn đạt, tên sát giới hạn đầu ra hơn là: **“Khử nhiễu, tăng cường tương phản và xử lý biên nhằm làm nổi bật vùng nghi ngờ dầu loang trên ảnh SAR Sentinel-1.”** Nếu giữ tên đã đăng ký, phần phát biểu bài toán cần ghi rõ “bộc lộ vùng nghi ngờ, chưa xác nhận dầu”. Thứ tự khử nhiễu rồi tăng tương phản trong tên gợi đúng pipeline mặc định, nhưng thứ tự liệt kê khác không tự làm đề tài sai.

Nguồn: [kaggle/metadata/dataset_metadata.xml](../kaggle/metadata/dataset_metadata.xml), [kaggle/README.md](../kaggle/README.md).

## 11. Ma trận tính tay riêng của từng thành viên

Mỗi thư mục dưới đây đã có `MA_TRAN_TINH_TAY.md`, `MA_TRAN_TINH_TAY.pdf` và `vi_du_ma_tran.py`. Bài tập cần được chính thành viên chạy, tính lại và giải thích; có file chuẩn bị không đồng nghĩa người đó đã nắm bài.

| Thành viên | Nội dung ma trận | Tài liệu |
| --- | --- | --- |
| TV1 | 4 × 4: phân ngưỡng, tạo mask, đếm diện tích, tích hợp hiển thị | [MD](thanh_vien/TV1_Tien_Son_Tran/MA_TRAN_TINH_TAY.md) · [PDF](thanh_vien/TV1_Tien_Son_Tran/MA_TRAN_TINH_TAY.pdf) · [Mã](thanh_vien/TV1_Tien_Son_Tran/vi_du_ma_tran.py) |
| TV2 | 4 × 4: histogram, phương sai giữa lớp, ngưỡng Otsu, đối chiếu OpenCV | [MD](thanh_vien/TV2_Luong_Tien_Dung/MA_TRAN_TINH_TAY.md) · [PDF](thanh_vien/TV2_Luong_Tien_Dung/MA_TRAN_TINH_TAY.pdf) · [Mã](thanh_vien/TV2_Luong_Tien_Dung/vi_du_ma_tran.py) |
| TV3 | 5 × 5: Lee; 4 × 4: histogram, CDF-min và HE | [MD](thanh_vien/TV3_Ho_Viet_Tung/MA_TRAN_TINH_TAY.md) · [PDF](thanh_vien/TV3_Ho_Viet_Tung/MA_TRAN_TINH_TAY.pdf) · [Mã](thanh_vien/TV3_Ho_Viet_Tung/vi_du_ma_tran.py) |
| TV4 | 5 × 5: Sobel, co ảnh và trích biên hình thái | [MD](thanh_vien/TV4_Nguyen_Hai_Hieu/MA_TRAN_TINH_TAY.md) · [PDF](thanh_vien/TV4_Nguyen_Hai_Hieu/MA_TRAN_TINH_TAY.pdf) · [Mã](thanh_vien/TV4_Nguyen_Hai_Hieu/vi_du_ma_tran.py) |
| TV5 | Hai ma trận 4 × 4: RMS, AMBE, MSE, entropy và SSI | [MD](thanh_vien/TV5_Pham_Minh_Tuan/MA_TRAN_TINH_TAY.md) · [PDF](thanh_vien/TV5_Pham_Minh_Tuan/MA_TRAN_TINH_TAY.pdf) · [Mã](thanh_vien/TV5_Pham_Minh_Tuan/vi_du_ma_tran.py) |

Mỗi người nên chuẩn bị thêm một ma trận tự chọn: ghi đầu vào, tham số và quy tắc biên; tính tay ít nhất một vị trí hoặc toàn bộ phép đo; cài lõi NumPy; so với đáp án tính tay và hàm thư viện tương ứng khi có; giải thích mọi sai khác. Ví dụ HE không thay thế việc hiểu đầy đủ CLAHE; ví dụ threshold của TV1 không thay thế toàn bộ pipeline.

## 12. Những phần chưa có trên web để tránh trình bày nhầm

- Chưa chạy kiểm chứng thư viện trực tiếp trên ảnh đang chọn, chưa hiển thị cặp ảnh NumPy/thư viện và ảnh sai khác trong tab đối chiếu.
- Chưa có trang chạy bốn cấu hình tiền xử lý cùng lúc; thí nghiệm ở mục 9 được chạy bằng script và lưu ngoài web.
- Chưa có nút batch toàn dataset trên giao diện; batch nằm ở `reproduce.py` và module thí nghiệm.
- Chưa có công cụ gán mask chuẩn, đo IoU/Dice với nhãn pixel hay xác nhận dầu từ thông tin thực địa.
- Chưa có bản đồ địa lý, tính diện tích m², nhận ảnh Sentinel-1 SAFE hoặc hiệu chuẩn radar thô.
- Chưa dùng ML/DL, không có bước huấn luyện hoặc suy luận mạng nơ-ron.

## 13. Trình tự demo ngắn để trình bày rõ phần việc

1. TV1 mở web, chọn ảnh 00013 và giới thiệu đầu vào, đầu ra.
2. TV3 tắt/bật Lee và CLAHE, chỉ vào ảnh trung gian, giải thích lợi ích và nguy cơ nổi nhiễu.
3. TV4 đổi Canny/morphology, giải thích biên khác mask; thử ngưỡng tương phản vùng/nền.
4. TV5 mở histogram, lát cắt và thống kê; nhấn mạnh các chỉ số chưa đo đúng đường bao dầu.
5. TV2 mở tab đối chiếu, sau đó mở `registry()` và một dòng `per_case.csv` để chỉ rõ hàm tự cài, hàm đối chứng, sai số và verdict.
6. Nhóm trình bày một ảnh nền biển có ứng viên để cho thấy giới hạn, rồi tải PNG/JSON làm bằng chứng lần chạy.

Khi cần trả lời nhanh “file nào là quan trọng nhất?”, mở `src/tv2/library_comparison.py` để xem cách so sánh và `results/verification/per_case.csv` để xem bằng chứng từng ca.
