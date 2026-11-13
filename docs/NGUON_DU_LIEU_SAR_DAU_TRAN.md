# Nguồn dữ liệu SAR và nhãn dầu tràn cho Đề 18

Ngày tổng hợp: **12/11/2026**.

Tài liệu tập hợp các nguồn đã tìm được để nhóm xem xét trước khi refactor dự án. Ưu tiên nguồn NASA, dữ liệu có nhãn dầu/tương tự dầu (look-alike), và khả năng truy về cảnh SAR gốc. Đây là danh mục khảo sát, **chưa phải quyết định chọn dataset**. Chưa tải và kiểm tra toàn bộ dữ liệu; các số lượng và dung lượng dưới đây là thông tin nhà phát hành công bố.

Mục tiêu của nhóm: tự cài CART và SVM, so sánh giữa các thuật toán và giữa bản tự cài với thư viện; cải tiến tập trung giảm báo nhầm look-alike. Việc chọn thuật toán sẽ dựa trên thực nghiệm sau khi chốt dữ liệu và cách đánh giá.

## 1. Đọc nhanh và thứ tự ưu tiên

| Nguồn | Có liên quan NASA? | Nhãn được mô tả | Vai trò đáng xem xét | Trạng thái |
| --- | --- | --- | --- | --- |
| QPOSD | Ảnh UAVSAR NASA/JPL; nhãn do nhóm nghiên cứu tạo | Mask dầu, look-alike, biển, đất | Ưu tiên nếu muốn ảnh NASA có nhãn | Đọc được bài mô tả; chưa mở được Zenodo |
| Trujillo-Acatitla, Parts I–III | Sentinel-1, không phải cảm biến NASA | Mask đi kèm các nhóm dầu/look-alike/không dầu | Ưu tiên thẩm định cho Đề 18 | Đọc được ba bản ghi dữ liệu |
| DARTIS / PANGAEA | Sentinel-1 | Bounding box dầu; tập ảnh không dầu | Đánh giá đối tượng, truy cảnh gốc, thử báo nhầm | Đọc được bản ghi và bài báo |
| MKLab / OSDD | Sentinel-1 | Mask năm lớp | Benchmark dầu và look-alike | Có điều kiện xin quyền truy cập |
| Refined SOS | Dữ liệu SAR từ SOS | Mask phân đoạn được hiệu chỉnh | Benchmark bổ sung | Đọc được bản ghi Zenodo |
| Cantarell / Garcia-INPE | Sentinel-1 | Mask nhị phân slick/biển, vector | Kiểm tra chéo trên vùng khác | Đọc được repository |
| GlobalOSD-SAR | Sentinel-1 | Mô tả có mẫu dầu và look-alike | Khảo sát nguồn quy mô lớn | Chưa kiểm chứng tệp nguồn |
| OSLM | Chưa xác minh chi tiết | Cần kiểm tra dataset card | Nguồn cần khảo sát tiếp | Mở được repository |
| CSIRO | Sentinel-1 | Nhãn cấp ảnh 0/1 | Kiểm tra phụ ở cấp ảnh | Có metadata trong dự án |

**Đề xuất thẩm định trước:** QPOSD, Trujillo-Acatitla và DARTIS. Chưa có đủ bằng chứng để khẳng định một bộ duy nhất đáp ứng đồng thời mask dầu/look-alike, góc tới, gió, mã cảnh và xác nhận tại hiện trường.

## 2. NASA và dữ liệu sử dụng ảnh NASA

### 2.1. NASA/JPL UAVSAR Data Search

- Đơn vị: NASA/JPL.
- Cổng dữ liệu: <https://uavsar.jpl.nasa.gov/cgi-bin/data.pl>
- Cảm biến: radar SAR hàng không UAVSAR; cổng có nhiều loại sản phẩm và bộ lọc phân cực/băng tần.
- Nội dung: tìm cảnh theo khu vực, ngày bay, flight line và product ID; có sản phẩm PolSAR và metadata.
- Nhãn: **chưa xác nhận có mask dầu chuẩn đi kèm** từng sản phẩm.
- Dung lượng, quyền sử dụng và điều kiện tải: cần kiểm tra trên sản phẩm cụ thể.
- Phù hợp: lấy ảnh gốc để nghiên cứu cơ chế SAR, góc tới và dầu tràn; phải có nguồn nhãn đối chiếu riêng.

### 2.2. NASA Gulf Oil Spill Airborne Data

- Đơn vị: NASA/JPL; dữ liệu chiến dịch Deepwater Horizon.
- Tìm dữ liệu: <https://gulfoilspill.jpl.nasa.gov/cgi-bin/search.pl>
- Hướng dẫn tìm và tải: <https://gulfoilspill.jpl.nasa.gov/help.html>
- Nội dung: dữ liệu UAVSAR và AVIRIS theo đường bay, thời gian thu nhận.
- Phân biệt: UAVSAR là SAR; AVIRIS là cảm biến quang phổ, không phải SAR.
- Nhãn: sự kiện dầu tràn có thật không có nghĩa mọi pixel trong ảnh đều có nhãn được xác nhận. Chưa xác minh bộ mask sẵn dùng.
- Phù hợp: xây dựng ca nghiên cứu có hồ sơ sự kiện và quan trắc bổ trợ; phải kiểm tra độ lệch thời gian, vị trí và độ phân giải giữa các nguồn.
- Hạn chế: cổng lịch sử; khả năng tải từng sản phẩm, dung lượng và điều kiện sử dụng chưa được kiểm tra toàn bộ.

### 2.3. QPOSD — Quad-polarization Oil Spill Detection Dataset

**Cập nhật 13/11/2026:** đã truy cập API chính thức bản 19258036, xác nhận CC BY 4.0 và đọc đủ 41 mask từ ZIP bằng HTTP Range. Đếm được 4.780.381 pixel look-alike và 2.117 pixel ngoài bảng màu. Đã tải ba mảng đặc trưng: mẫu 7 và 40 có ảnh 521×521 nhưng mask 521×520; mẫu 35 khớp 771×771. Chưa chạy mô hình vì cần xác minh căn chỉnh. Xem [thẩm định thực tế](management/QPOSD_THAM_DINH.md), `management/qposd_mask_audit.json` và `management/qposd_feature_audit.json`. Các ghi chú chưa truy cập dưới đây là trạng thái khảo sát cũ.

- Bài báo: <https://www.sciencedirect.com/science/article/pii/S2352340926003264>
- Bản bài báo trên PMC: <https://pmc.ncbi.nlm.nih.gov/articles/PMC13112480/>
- DOI dữ liệu: <https://doi.org/10.5281/zenodo.19258036>
- Nguồn ảnh: UAVSAR NASA/JPL, băng L, đa phân cực, Vịnh Mexico, giai đoạn 2010–2022.
- Theo bài mô tả: 41 cảnh SAR; độ phân giải khoảng 6 × 4 m; góc tới 27–67°; biểu diễn ma trận coherence phân cực thành chín kênh thực.
- Nhãn: bốn lớp biển, dầu, look-alike và đất; hơn 80 triệu pixel được gán nhãn.
- Cách tạo nhãn: gán nhãn thủ công, lan truyền nhãn bằng Random Forest và hiệu chỉnh thủ công. Vì vậy cần xem xét tính độc lập của nhãn khi đánh giá mô hình phân lớp.
- **Nguồn ảnh là NASA; bộ nhãn do nhóm nghiên cứu phát hành. Không gọi đây là nhãn được NASA xác nhận từng pixel.**
- Trạng thái: đọc được mô tả bài báo; công cụ chưa mở được bản ghi Zenodo. Chưa xác minh dung lượng, giấy phép dataset, split, tệp góc tới và cách tải thực tế.
- Phù hợp: ứng viên ưu tiên nếu nhóm muốn dữ liệu NASA có mask dầu/look-alike. Cần giải thích khác biệt cảm biến nếu sử dụng thay cho Sentinel-1 trong đề.

### 2.4. NASA UAVSAR Oil Slicks — tư liệu sự kiện

- Nguồn: <https://science.nasa.gov/photojournal/uavsar-oil-slicks/>
- Nội dung: quan sát dầu tràn bằng UAVSAR để hỗ trợ NOAA, minh họa khả năng xác định hiện diện và vị trí vệt dầu.
- Vai trò: dẫn chứng bối cảnh ứng dụng, hình minh họa và đầu mối truy dữ liệu.
- **Không dùng ảnh minh họa trên trang làm benchmark có ground truth.**

## 3. Các bộ dữ liệu có nhãn ngoài NASA

### 3.1. Trujillo-Acatitla — Sentinel-1 SAR Oil Spill, Parts I–III

Đây là ứng viên đáng ưu tiên vì giữ ảnh sigma0 thay vì chỉ cung cấp JPEG hiển thị.

| Phần | Link chính thức | Nội dung công bố | Dung lượng nén công bố |
| --- | --- | --- | --- |
| Part I | <https://zenodo.org/records/8346860> | 1.200 ảnh dầu train/validation và mask tương ứng | Khoảng 40,7 GB |
| Part II | <https://zenodo.org/records/8253899> | Ảnh và mask cho look-alike, không dầu | Khoảng 45,9 GB |
| Part III | <https://zenodo.org/records/13761290> | Test: 150 ảnh dầu, 150 look-alike, 150 không dầu và mask | Khoảng 9,9 GB |

- Bài báo liên quan: <https://doi.org/10.1016/j.marpolbul.2024.116549>
- Tác giả: Rubicel Trujillo-Acatitla, José Tuxpan-Vargas, Cesaré Ovando-Vázquez, Erandi Monterrubio-Martínez.
- Ảnh: Sentinel-1 sigma0 theo dB, hai phân cực VV/VH, TIFF 2048 × 2048 × 2.
- Mask: TIFF 2048 × 2048; Part I mô tả foreground = 1, background = 0.
- Metadata: ảnh có georeference; mask không có georeference riêng. Cần xác nhận ảnh–mask khớp lưới trước khi kế thừa thông tin địa lý của ảnh.
- Tổng khoảng **96,5 GB nén**, chưa tính giải nén và cảnh SAR gốc.
- Bản ghi có checksum MD5 cho các gói, hữu ích kiểm tra tải đầy đủ.
- Chưa xác minh: giấy phép cụ thể, quá trình xác nhận nhãn từ tài liệu gốc, mã cảnh, thời gian chụp, tệp góc tới và tính độc lập giữa các split.
- Đặc biệt cần kiểm tra: mask của nhóm look-alike đánh dấu vùng look-alike hay chỉ đánh dấu dầu và vì vậy có thể là mask rỗng. Tên thư mục không đủ để suy ra nhãn từng đối tượng.
- **GeoTIFF không mặc nhiên chứa góc tới.** Không tuyên bố hoàn thành chuẩn hóa góc tới chỉ từ việc đọc ảnh TIFF.

### 3.2. MKLab Oil Spill Detection Dataset / OSDD

- Trang nhóm phát hành: <https://m4d.iti.gr/oil-spill-detection-dataset/>
- Trang MKLab: <https://mklab.iti.gr/results/oil-spill-detection-dataset/>
- Bài báo: <https://www.mdpi.com/2072-4292/11/15/1762>
- Nguồn ảnh: Sentinel-1; tọa độ và thời gian sự kiện dầu được cung cấp từ hồ sơ EMSA CleanSeaNet.
- Dữ liệu công bố: khoảng 400 MB, khoảng 1.000 ảnh train và 110 ảnh test, ảnh JPEG và mask năm lớp: dầu, look-alike, tàu, đất, biển.
- Điểm mạnh: trực tiếp phục vụ phân biệt dầu/look-alike; có nguồn sự kiện hỗ trợ nhãn.
- Truy cập: phải đọc Terms of Use và gửi đề xuất theo mẫu bằng email tổ chức. Trang nguồn yêu cầu sinh viên nhờ giảng viên hướng dẫn đứng tên và ghi sinh viên là người được hướng dẫn.
- Chưa gửi email hoặc xin quyền truy cập. Không mặc định bản đăng lại trên Kaggle có quyền phân phối hợp lệ.
- Hạn chế: chưa xác nhận bộ phát hành có mã cảnh, sigma0 gốc và góc tới. Không dùng JPEG để khẳng định đánh giá đầy đủ hiệu chỉnh vật lý SAR.

### 3.3. DARTIS — Eastern Mediterranean Sea 2019

- Dữ liệu PANGAEA: <https://doi.pangaea.de/10.1594/PANGAEA.980773>
- Bài báo: <https://essd.copernicus.org/articles/17/6807/2025/>
- Mã hỗ trợ: <https://github.com/yi-jie-yang/dataset_DARTIS_2019>
- Nguồn: Yang và cộng sự; Sentinel-1 VV ở Đông Địa Trung Hải.
- Bản ghi PANGAEA công bố: 1.365 patch dầu với 3.225 đối tượng dầu và 2.290 patch không dầu.
- Giấy phép bản ghi: **CC BY 4.0**.
- Nhãn: bounding box dầu định dạng Pascal VOC XML; tập không dầu có look-alike nhưng không có nhãn đối tượng cho từng vùng.
- Metadata: mã sản phẩm Sentinel-1, thời gian bắt đầu/kết thúc, tọa độ góc patch và đối tượng. Có khả năng truy ngược cảnh gốc.
- Chất lượng nhãn: hai người diễn giải ảnh đồng thuận; bài báo thừa nhận thiếu xác nhận hiện trường và khả năng có chất ô nhiễm khác dầu.
- Lưu ý kiểm kê: một đoạn bài báo ghi 2.990 patch không dầu, khác 2.290 trên bản ghi PANGAEA. Phải kiểm đếm tệp thực tế, không âm thầm chọn một số để báo cáo.
- Phù hợp: đánh giá phát hiện mức đối tượng và báo nhầm trên tập không dầu; khảo sát khôi phục cảnh vật lý để lấy góc tới/gió.
- Hạn chế: JPEG đã biến đổi cường độ; **bounding box không phải mask ranh giới dầu**. Không dùng diện tích hộp làm diện tích dầu thực.

### 3.4. Refined Deep-SAR Oil Spill — SOS

- Dữ liệu: <https://zenodo.org/records/15298010>
- Nhóm hiệu chỉnh: Denis Zuenko và Ilvira Khaidarova.
- Gói công bố: images.zip khoảng 1,1 GB; masks.zip khoảng 28,3 MB; tổng hiển thị khoảng 1,2 GB.
- Nhãn: mask phân đoạn được hiệu chỉnh bằng kiểm tra trực quan và tính nhất quán.
- Tác giả cho biết đã sửa khoảng **38% mask train và 50% mask validation**. Đây là bằng chứng cần kiểm tra chất lượng nhãn, không phải bằng chứng độ chính xác tuyệt đối của bản sửa.
- Cần kiểm tra: giấy phép, lớp look-alike riêng, cảm biến từng mẫu, mã cảnh và rò rỉ giữa patch của cùng cảnh trong các split.
- Vai trò: benchmark phụ cho phân đoạn; chưa đủ căn cứ chọn làm nguồn duy nhất cho cả ba chức năng Đề 18.

### 3.5. Deep-SAR Oil Spill — SOS gốc

- Link dataset được dẫn trong tài liệu nghiên cứu: <https://aistudio.baidu.com/datasetdetail/145599>
- Bài gốc: *Oil Spill Contextual and Boundary-Supervised Detection Network Based on Marine SAR Images*.
- DOI: <https://doi.org/10.1109/TGRS.2021.3115492>
- Trạng thái: tìm được đầu mối; chưa xác minh trực tiếp tệp tải, tài khoản cần dùng, giấy phép và cấu trúc nhãn.
- Cần kiểm tra cách tách ảnh từ các cảnh SAR và phân biệt nguồn cảm biến; không xem mọi patch là quan sát độc lập.
- Nên xem cùng bản Refined SOS để hiểu lịch sử hiệu chỉnh nhãn.

### 3.6. Cantarell — Garcia-INPE Oil Spill Detection Dataset

- Repository: <https://github.com/Garcia-INPE/oilspill-detection-dataset>
- Nội dung công bố: 173 bộ ảnh/mask 800 × 600, Sentinel-1 tại vùng Cantarell, Vịnh Mexico, tháng 1–9/2020.
- Nhãn nhị phân: SEA và SLICK; SLICK gồm dầu tràn hoặc dầu rò tự nhiên.
- Có bảng đặc trưng, GeoTIFF, vector và các baseline truyền thống/học máy.
- Giấy phép công bố: **CC BY 4.0**.
- Điểm mạnh: có mã và dữ liệu hỗ trợ đối chiếu; thích hợp kiểm tra chéo.
- Hạn chế: chưa có bằng chứng về lớp look-alike riêng; cần kiểm tra nguồn xác nhận nhãn, đơn vị cường độ, split theo cảnh và metadata góc tới.

### 3.7. Global Oil Slick SAR Dataset — GlobalOSD-SAR

- DOI: <https://doi.org/10.5281/zenodo.15286918>
- Bản ghi chỉ mục đã đọc: <https://explore.openaire.eu/search/dataset?pid=10.5281%2Fzenodo.15286918>
- Mô tả chỉ mục: 100.329 mẫu dầu và 100.134 look-alike, Sentinel-1 giai đoạn 2014–2020; có tọa độ, ngày chụp và loại nguồn dầu.
- **Chưa mở được bản ghi Zenodo**, chưa kiểm chứng số lượng tệp, định dạng nhãn, dung lượng, giấy phép cụ thể hoặc khả năng tải.
- Không mặc định “mẫu” là mask hay đối tượng có ranh giới. Chỉ xếp vào nguồn cần thẩm định tiếp.

### 3.8. OSLM

- Repository: <https://github.com/SARDEEP1/OSLM>
- Bài liên quan được dẫn trong tài liệu nghiên cứu: <https://doi.org/10.1016/j.jhazmat.2025.140683>
- Trạng thái: mở được repository; chưa kiểm chứng đầy đủ dataset card, file ảnh/nhãn và đường tải.
- Cần xác minh: cảm biến, số lượng, loại nhãn, giấy phép, nguồn xác nhận dầu, mã cảnh và điều kiện chia tập.
- Chưa xếp hạng chất lượng và chưa đề nghị dùng làm benchmark chính.

### 3.9. CSIRO Sentinel-1 oil/non-oil — nguồn dữ liệu hiện có trong dự án

- DOI: <https://doi.org/10.25919/4v55-dn16>
- Bản ghi mô tả: <https://researchdata.edu.au/csiro-sentinel-1-deep-learning/3374565>
- Dữ liệu: JPEG chip 400 × 400, nhãn cấp ảnh 0 = không dầu, 1 = có dầu; lớp không dầu gồm biển sạch và look-alike.
- Metadata và giấy phép đi kèm trong repo: `kaggle/metadata/dataset_metadata.xml`, `kaggle/metadata/license.html`.
- Theo kiểm kê đã ghi trong README dự án: có 5.538 ảnh cục bộ, ít hơn số công bố 92 ảnh; chưa có mask chuẩn hoặc ánh xạ chip–cảnh.
- **Không đủ để đánh giá Precision/Recall/F1 mức đối tượng.** Chỉ dùng làm bài kiểm tra cấp ảnh hoặc dữ liệu phụ, không chuyển nhãn ảnh thành ground truth vùng dầu.

## 4. Nguồn xác nhận sự kiện và hướng dữ liệu bổ sung

### 4.1. NOAA Deepwater Horizon

- Nguồn chính thức: <https://www.ncei.noaa.gov/products/deepwater-horizon>
- Vai trò: hồ sơ quan trắc và dữ liệu phản ứng sự cố; hỗ trợ tìm bằng chứng độc lập về sự kiện.
- Hạn chế: không phải mọi phép đo đều mô tả dầu trên mặt nước tại thời điểm ảnh SAR chụp. Cần đối chiếu thời gian, vị trí, loại đo và độ bất định trước khi dùng làm ground truth.

### 4.2. SOSeas — Searching for Oil Spills on Sea Surfaces

- Báo cáo dự án: <https://cordis.europa.eu/project/id/101111054/reporting>
- Danh sách kết quả: <https://cordis.europa.eu/project/id/101111054/results>
- Mô tả dự án đề cập SAR đã hiệu chuẩn, Damping Ratio, góc tới, thông tin nhiễu/chất lượng tín hiệu và gió khi có; SOSeas-Bonn sử dụng sự kiện được xác nhận thực địa.
- Đây là hướng rất phù hợp về mặt dữ liệu vật lý, nhưng **chưa xác minh được gói dữ liệu công khai có thể tải**.
- Không đưa vào kế hoạch bắt buộc cho đến khi có link tải, giấy phép và cấu trúc dữ liệu rõ ràng.

## 5. NASA muốn giải quyết vấn đề gì?

### 5.1. Mục đích ứng dụng dầu tràn

- Nguồn: [NASA–NOAA Tech Will Aid Marine Oil Spill Response](https://www.nasa.gov/centers-and-facilities/jpl/nasa-noaa-tech-will-aid-marine-oil-spill-response/).
- NASA mô tả sử dụng UAVSAR để nghiên cứu độ dày dầu trong vệt dầu, hỗ trợ xác định nơi cần ưu tiên ứng phó. Phát hiện vị trí, phân bố và đặc tính dầu phục vụ quyết định xử lý sự cố.
- Phần phù hợp với nhóm: phát hiện vùng nghi dầu, giảm báo nhầm và giải thích đặc trưng dẫn đến quyết định. Đây là hướng đóng góp cần kiểm chứng bằng thực nghiệm, chưa phải cải tiến đã đạt được.
- Không tuyên bố đo độ dày dầu hoặc dự báo trôi dầu chỉ từ pipeline phân lớp CART/SVM.

### 5.2. Quan hệ với “NASA #6 — Dancing with the SARs”

- Trang chính thức: <https://www.spaceappschallenge.org/2026/challenges/dancing-with-the-sars/>
- Trang sự kiện địa phương có mô tả và liên kết tới trang chính thức: <https://hackathlone.com/challenges/dancing-with-the-sars>
- Mô tả địa phương nói đến ứng dụng tương tác dùng dữ liệu NISAR để theo dõi và trực quan hóa thay đổi bề mặt Trái Đất.
- Trang chính thức trả lỗi 502 khi khảo sát. **Chưa xác minh nguyên văn yêu cầu từ trang NASA Space Apps.**
- Ba chức năng cụ thể của bài dầu tràn hiện được lấy từ tài liệu môn học `docs/00_tai_lieu_goc/huong_dan_btl_docx/ĐỀ TÀI LIÊN QUAN ĐẾN NASA.docx`; không gán nguyên văn các chức năng đó cho NASA khi chưa có bằng chứng.

## 6. Điều kiện để một nguồn trở thành dữ liệu đánh giá chính

1. **Nguồn và quyền sử dụng:** xác định tác giả, phiên bản, DOI/link gốc, giấy phép và quyền dùng trong repo/báo cáo/demo.
2. **Ý nghĩa nhãn:** phân biệt nhãn cấp ảnh, bounding box, mask semantic và nhãn instance. Xác định look-alike có nhãn riêng hay chỉ là tên nhóm ảnh.
3. **Bằng chứng về dầu:** ghi rõ xác nhận hiện trường, hồ sơ cơ quan, diễn giải chuyên gia hay nhãn bán tự động. Không gọi tất cả là sự thật tuyệt đối.
4. **Ảnh–nhãn khớp nhau:** kiểm tra kích thước, tọa độ, hướng ảnh, mã lớp, giá trị nodata và các mẫu rỗng/lỗi.
5. **Dữ liệu SAR vật lý:** biết ảnh là sigma0 tuyến tính, dB hay ảnh hiển thị đã biến đổi; kiểm tra phân cực, góc tới, thời gian và khả năng truy cảnh gốc.
6. **Chia tập độc lập:** ưu tiên theo cảnh/sự kiện; phát hiện patch trùng hoặc chồng lấn. Không để cùng một cảnh xuất hiện ở cả train và test mà không công bố hạn chế.
7. **Đánh giá đúng loại nhãn:** bounding box dùng giao thức box; mask dùng giao thức mask. Nếu chuyển semantic mask thành thành phần liên thông để đánh giá đối tượng, phải công bố đó là đối tượng suy ra từ mask, không phải instance chuẩn sẵn có.
8. **Gió và góc tới:** chỉ ghép dữ liệu đúng vị trí/thời gian; chỉ báo cáo hiệu quả chuẩn hóa khi có đầu vào hợp lệ. Không suy ra góc tới từ mức xám JPEG.

## 7. Kết quả cần có trước khi chọn thuật toán

- Bảng kiểm kê dữ liệu thực tế và danh sách mẫu loại bỏ kèm lý do; checksum và manifest ảnh–nhãn–cảnh.
- Ví dụ trực quan ảnh chồng nhãn cho dầu, look-alike, biển sạch và các ca khó; không chỉ chọn ảnh đẹp.
- Train/validation/test cố định; chỉ dùng train/validation để chọn thuật toán và tham số.
- Giao thức Precision, Recall, F1 mức đối tượng, cách ghép dự đoán–nhãn và tỷ lệ báo nhầm look-alike được chốt trước khi chạy test.
- Hai bảng so sánh tách biệt: **giữa các thuật toán** và **bản tự cài so với thư viện tương ứng**; ghi rõ trường hợp không có API tương đương độc lập.
- Đo cải tiến giảm báo nhầm bằng ablation trên cùng split; báo cả thay đổi recall để tránh giảm báo nhầm bằng cách bỏ sót hầu hết dầu.
- Số liệu trong bài báo bên ngoài chỉ là tham khảo. Số liệu đánh giá của nhóm phải do script chạy tạo ra, có cấu hình và nguồn dữ liệu truy lại được.

## 8. Trạng thái khảo sát cũ (12/11/2026)

- Chưa tải và kiểm chứng toàn bộ dataset hoặc huấn luyện mô hình mới.
- Chưa gửi email xin dữ liệu MKLab.
- Chưa xác nhận dataset nào có đầy đủ góc tới, gió và nhãn dầu/look-alike trên cùng mẫu.
- Chưa chốt nguồn chính, chưa thay đổi pipeline và chưa tạo số liệu thực nghiệm mới.

Danh mục này bao gồm các đầu mối tìm được trong đợt khảo sát, không khẳng định bao quát mọi dataset tồn tại. Các bản sao không rõ nguồn trên Kaggle/Hugging Face không được coi là nguồn gốc độc lập.

## Cập nhật 13/11/2026

Nhóm đã chọn Refined SOS v1 (https://zenodo.org/records/15298010), tải và kiểm kê 8070 cặp PNG/mask. Sentinel dùng huấn luyện/validation/test, PALSAR chỉ đánh giá ngoài miền. Xem `management/KIEM_TRA_REFINED_SOS.md` và `GIAO_THUC_THUC_NGHIEM.md`. Các dòng “chưa chọn/chưa tải” ở mục khảo sát cũ mô tả trạng thái trước quyết định này. Không có metadata để hoàn thành chuẩn hóa góc tới, ghép gió hoặc đánh giá riêng look-alike.

### Kiểm tra bổ sung DARTIS ngày 13/11/2026

SOS vẫn là dữ liệu chính. Đã tải catalog từ
[PANGAEA 980773](https://doi.pangaea.de/10.1594/PANGAEA.980773?format=textfile)
vào `data/dartis/catalog.tsv`. Script `scripts/audit_dartis.py` kiểm tra catalog,
ghi [audit](management/dartis_catalog_audit.json) và manifest cục bộ.
Nguồn công bố CC-BY-4.0; cần ghi tác giả Yang và Singha cùng DOI khi sử dụng.

Kết quả chạy thực tế: 5.515 dòng, 3.655 ảnh duy nhất, 3.225 dòng đối tượng dầu,
1.063 mã cảnh Sentinel-1. Bốn tập có 375 oil/coast, 990 oil/water,
351 no-oil/coast và 1.939 no-oil/water. Có 3.581 ảnh 640×640;
74 ảnh có kích thước khác. Các box trong catalog không vượt biên theo kiểm tra
`0 <= xmin < xmax <= width` và tương tự cho y. Đây chưa phải xác nhận nhãn đúng
về mặt hiện tượng hoặc kiểm tra toàn bộ tệp ảnh.

Đã tải và mở `ow-0001.jpg` cùng XML: ảnh xám 640×640; box
(345, 297, 368, 343) khớp catalog. Trường filename trong XML dùng tên cảnh/patch
gốc, khác tên tải xuống; script đối chiếu qua `patch_name` để tránh ghép sai.
Hash catalog, JPEG và XML được lưu trong audit. Chưa chạy benchmark trên DARTIS.

[README của tác giả](https://download.pangaea.de/reference/132854/attachments/README.pdf)
cho biết nhãn dầu là box VOC; mã nhóm no-oil là cụm K-means. Vì vậy:

- Không biến box thành mask dầu đặc rồi tính IoU pixel như SOS.
- Có thể thiết kế phép đo báo dầu nhầm trên ảnh no-oil, nhưng cần cố định cách
  xử lý kích thước và giao thức trước khi xem kết quả.
- Không gán tên mưa/gió yếu/màng sinh học cho mã cụm khi chưa có nhãn xác nhận.
- Mã cảnh và thời gian hỗ trợ truy dữ liệu gốc; JPEG không cung cấp băng góc tới
  hoặc gió. Chưa đáp ứng chuẩn hóa góc tới và ghép gió chỉ nhờ tải catalog.
- Khi chia tập phải gộp các patch chia sẻ bất kỳ mã cảnh nào; một patch có thể
  được tạo từ nhiều cảnh. Không chỉ nhóm theo mã cảnh đầu tiên.

Chạy lại kiểm tra sau khi đặt catalog và các ảnh/XML cần kiểm tra trong `data/dartis/`:

```powershell
.venv/Scripts/python.exe scripts/audit_dartis.py
```

Ảnh và catalog nằm ngoài Git theo quy tắc thư mục data; audit và script được lưu
trong mã nguồn. Download từng tệp dùng tên trong catalog nối với
`https://download.pangaea.de/dataset/980773/files/`.

### Phép thử no-oil với mô hình SOS đã khóa

Giao thức nằm trong `results/dartis/protocol.json`, được ghi trước khi chạy suy luận.
Phạm vi là toàn bộ 2.290 ảnh no-oil (1.939 water, 351 coast). Kiểm kê xác nhận
riêng tập no-oil đều 640×640; các kích thước khác thuộc tập dầu. Giữ kích thước
gốc, đổi ảnh xám sang float bằng chia 255, không fit lại hoặc chỉnh tham số SOS.
Một ảnh báo nhầm khi giữ ít nhất một vùng có score > 0. Báo tỷ lệ ảnh báo nhầm,
số vùng giữ/ảnh và tỷ lệ pixel dự đoán dầu; tách coast/water và cụm K-means.
Không tính Recall dầu hoặc F1 tổng thể từ một tập chỉ có ảnh âm.

```powershell
.venv/Scripts/python.exe scripts/download_dartis.py --workers 4
.venv/Scripts/python.exe scripts/evaluate_dartis.py --workers 4
```

Downloader kiểm tra giải mã JPEG, kích thước và SHA-256, lưu tiến độ mỗi 25 ảnh
trong `results/dartis/download_audit.json`. Nếu máy chủ trả lỗi, chạy lại downloader
sau khi lượt đang chạy kết thúc; ảnh hợp lệ được dùng lại. Evaluator chỉ chạy khi
đủ toàn bộ ảnh, kiểm tra hash giao thức/model/manifest, lưu từng ảnh và checkpoint.
Các lỗi không bị bỏ qua khỏi mẫu số. `complete=false` luôn là kết quả chưa đầy đủ.
Số liệu ngoài miền này không được gộp với bảng test SOS hoặc coi là nhãn hiện trường.
# Metadata Sentinel-1 gốc bổ sung — chưa phải dữ liệu của SOS

Đã truy ngược patch DARTIS `nc-0001-00-000001.jpg` đến cảnh
`S1B_IW_GRDH_1SDV_20190105T154901_20190105T154926_014361_01AB8D_D7A0`.
Tệp `productInfo.json` xác nhận mã cảnh và thời gian chụp 2019-01-05 15:49:01.
Đã tải XML annotation VV, calibration VV và noise VV bằng GET ẩn danh từ S3.
Các lần thử proxy ban đầu trả 404 cho XML nhưng endpoint S3 trả tệp hợp lệ;
nguồn tải thành công và hash được ghi trong `docs/management/sentinel_metadata_audit.json`.

- Lưới địa định vị: 210 điểm; góc tới từ 30,561276° đến 46,074471°.
- Kích thước ảnh gốc trong annotation: 16.725 dòng × 25.721 mẫu.
- XML hiệu chuẩn: 27 vector.
- Đã đọc một tile cường độ gốc 1.024 × 1.024 ở tâm cảnh bằng byte range;
  chưa chứng minh ánh xạ patch JPEG sang pixel gốc. Đã ghép gió ERA5 tại tâm
  tile theo thời gian chụp, không phải theo từng pixel; `results/physical/wind.json`.
  Không gán lưới góc tới này cho ảnh SOS. Xem `results/physical/README.md`
  và `docs/management/sentinel_window_audit.json` về hiệu chuẩn thử nghiệm.
- Việc có XML chưa chứng minh chuẩn hóa góc tới cải thiện phát hiện dầu.

Tái tạo: `python scripts/fetch_sentinel_metadata.py`.
Nguồn cấu trúc đường dẫn: [tài liệu Sentinel-1 GRD](https://roda.sentinel-hub.com/sentinel-s1-l1c/GRD/readme.html),
[AWS Open Data Registry](https://registry.opendata.aws/sentinel-1/).
Ý nghĩa metadata hiệu chuẩn: [ASF Data Formats](https://asf.alaska.edu/sar-information/data-formats-in-depth/).
