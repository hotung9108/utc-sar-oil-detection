# Kiểm tra nguồn bổ sung cho nhánh góc tới

Mục đích: tìm ảnh SAR có nhãn và thông tin vật lý để đánh giá tác động chuẩn hóa góc tới. SOS vẫn là tập chính; kiểm tra này chưa tạo thí nghiệm hay thay kết quả đã khóa.

**Cập nhật:** đã kiểm kê đủ 173 TIFF/mask/GeoJSON và xác định đủ 24 cảnh Sentinel. Xem [kiểm kê toàn bộ](CANTARELL_FULL_INVENTORY.md), bao gồm mã polygon lặp qua train/test. Các mục dưới đây giữ quá trình kiểm chứng ban đầu trên một rồi hai tile; chúng không thay thế kiểm tra căn chỉnh toàn bộ tập.

## Giao thức dữ liệu vật lý đã khóa

`cantarell_data_protocol_v1.json` được tạo bằng `scripts/freeze_cantarell_data_protocol.py` và commit **5fd0330**, trước khi tái dựng DN toàn tập hoặc chấm mô hình. Nối các nhóm cảnh dùng chung mã polygon; nếu một nhóm nối chứa test thì giữ cả nhóm trong test. Do đó `IMG_18` chuyển từ train sang test cùng `IMG_17`; không sửa split gốc của nhà phát hành.

| Tập bổ sung mới | Tile | Cảnh |
|---|---:|---:|
| Train | 103 | 15 |
| Validation | 43 | 4 |
| Test | 27 | 5 |

Đây là cách xử lý bảo thủ mã polygon chưa rõ, không phải khẳng định hai polygon là cùng sự kiện. Hai tile phát triển căn chỉnh vẫn ở train. Chưa huấn luyện mô hình hay chọn thuật toán bằng điểm test Cantarell.

Điều kiện chất lượng đã ghi trước: kiểm tra hash/miền nội suy, độ dịch tuyệt đối ≤3 pixel, sai khác độ dịch cục bộ với toàn ảnh ≤0,5 pixel, tương quan sau đăng ký ≥0,70, và ít nhất 3 cảnh hợp lệ mỗi split. Các ngưỡng là tiêu chí kỹ thuật, không phải định lý hoặc bảo đảm chính xác định vị. Ghi mọi mẫu bị loại và lý do; không nới ngưỡng theo điểm test. Nhánh so sánh dự kiến dùng sigma0 và sigma0/cos(góc tới), cùng lưới, cùng phạm vi đánh giá; gamma chỉ hiệu chỉnh hệ số diện tích hình học, không loại hết phụ thuộc góc của mặt biển.

## Metadata vật lý toàn bộ cảnh

```powershell
.venv/Scripts/python.exe scripts/fetch_cantarell_physical_metadata.py
```

Đã tải/kiểm tra đủ **24/24** bộ annotation VV và calibration VV, tổng **67.963.469 byte**, mỗi tệp có URL và SHA-256. Lưới geolocation của 13 cảnh có kích thước 10×21, 11 cảnh có kích thước 11×21; góc tới toàn các cảnh trong **30,79937–46,22010°**. LUT sigma0/gamma đều hữu hạn, dương, tọa độ tăng và có lưới chữ nhật hợp lệ.

Cả 24 annotation ghi `thermalNoiseCorrectionPerformed=false`. Giao thức hiện không trừ nhiễu nhiệt; hai nhánh giữ cùng điều kiện này, không gọi kết quả là hiệu chuẩn đã xử lý đầy đủ tương đương SNAP. Bằng chứng: `cantarell_physical_metadata_audit.json`. Đây mới là metadata; chưa phải 173 tile DN đã căn chỉnh và chưa có kết quả phát hiện cho nhánh vật lý.

## Nhật ký kiểm chứng ban đầu

### Chuẩn bị DN toàn tập và ghép gió

```powershell
.venv/Scripts/python.exe scripts/prepare_cantarell_physical.py --workers 2
.venv/Scripts/python.exe scripts/fetch_cantarell_wind.py
```

Mã chuẩn bị DN tái dùng các byte-range có kiểm tra hash theo từng cảnh; lưu sigma0, gamma0 suy từ góc tới, góc tới và mask trên cùng lưới đã căn chỉnh. Nội suy và phép dịch NumPy đều đối chiếu SciPy; chỉ đọc nhãn sau khi tính đăng ký ảnh và tiêu chí chất lượng. Cắt 8 pixel mỗi cạnh cho mọi nhánh, ghi số đối tượng ngoài crop hoặc chạm biên, không xóa đối tượng nhỏ. Cache kết quả gắn hash giao thức, metadata, mã và phiên bản thư viện; không trộn các phiên bản. `--retry-errors` chỉ thử lại lỗi vận hành, không nới điều kiện chất lượng.

**Lần tái dựng toàn tập đang được thực thi; chưa công bố hoàn tất.** Kết quả tổng hợp cuối được ghi vào `cantarell_physical_preparation_audit.json` khi tiến trình kết thúc. Chỉ dùng audit có hash mã hiện hành và `complete_preparation=true`; audit chạy thử hai tile hoặc cache một phần không chứng minh đủ 173 mẫu. Chưa huấn luyện/chấm mô hình Cantarell.

Xem tiến độ bằng `python scripts/report_cantarell_physical.py --progress`: chỉ đọc receipt của đúng phiên bản mã hiện hành, luôn ghi rõ chưa kiểm tra tệp mảng toàn tập và chưa đạt gate cuối. Khi tiến trình kết thúc, chạy lại **không có `--progress`** để kiểm tra hash từng NPZ, kích thước/crop, nhãn khớp nguồn, miền góc, cường độ hữu hạn và điều kiện chất lượng theo giao thức. Mã cũng đối chiếu số cảnh hợp lệ và độ phủ gió; giao thức mô hình phải được khóa riêng trước khi fit. Đã thử xác nhận chế độ cuối từ chối audit hai tile cũ khác hash mã, thay vì công nhận nhầm đủ dữ liệu.

Ghép gió đã hoàn thành truy vấn: **172/173 tile có dữ liệu**, tile `IMG_19_TILE_019` có tâm ngoài miền geolocation nên không tự tạo thời điểm thu nhận. Thời điểm từng tile còn lại được nội suy từ `azimuthTime` của metadata; gió được nội suy theo thành phần u/v giữa hai giờ UTC. Tốc độ từ **0,292171 đến 10,648501 m/s**; khoảng cách xa nhất giữa tâm tile và tâm ô gió trả về **18,005587 km**; sai số đối chiếu nội suy u/v với SciPy bằng **0** trong dữ liệu đã chạy.

Nguồn gió là ERA5 chọn tường minh qua [Open-Meteo Historical Weather API](https://open-meteo.com/en/docs/historical-weather-api), lưới danh nghĩa 0,25°, theo giờ; dùng ô gần nhất và tắt hiệu chỉnh độ cao. Kiểm tra thứ tự vị trí trả về, đơn vị m/s và UTC. JSON nguồn/URL/hash, tọa độ yêu cầu và ô trả về, hai giờ nội suy và trường hợp thiếu dữ liệu đều nằm trong `cantarell_wind_audit.json`. Gió lưới thô không phải quan trắc từng pixel SAR, không xác nhận vùng tối là do gió yếu, và chưa được dùng để thay nhãn hoặc chọn thuật toán.

Nguồn: [Garcia-INPE/oilspill-detection-dataset](https://github.com/Garcia-INPE/oilspill-detection-dataset), revision `1b9a62c30a9da9698eb470562aa976f9bd1e8fc3`. Đã tải tài liệu, giấy phép, bảng CSV, ba split và **một** cặp raster/mask; kiểm tra tiếp vector của mẫu, mã remap của tác giả, catalog ASF và metadata Sentinel-1. Script xử lý Git LFS và xác nhận kích thước/SHA-256 theo pointer; từng nguồn có receipt trong `cantarell_source_audit.json`.

Chạy lại từ thư mục gốc:

```powershell
.venv/Scripts/python.exe scripts/audit_cantarell_source.py
```

## Những gì đã đo trực tiếp

- Bảng có 385 polygon: 327 `OIL SPILL`, 58 `SEEPAGE SLICK`. Dầu thấm tự nhiên không được tự đổi thành nhãn tương tự dầu do gió yếu, màng sinh học hoặc mưa.
- Split có 108/43/22 mẫu. Nhóm tiền tố `IMG_XX` không giao nhau giữa ba split; đây chưa chứng minh độc lập cảnh Sentinel gốc.
- `IMG_01_TILE_001.tiff` trong thư mục tên `16-BIT` thực tế có dtype **float32**, kích thước 600×800, giá trị hữu hạn từ −48,88188 đến 17,69975. Không suy đơn vị sigma0-dB chỉ từ khoảng số hoặc tên tệp có `Cal`.
- TIFF có thông tin WGS84/EPSG:4326, pixel scale và tiepoint. Những tag đã đọc không cung cấp góc tới từng pixel hoặc định nghĩa đơn vị bức xạ.
- Mask cùng kích thước có **476.426 pixel giá trị 0 và 3.574 pixel giá trị 2**. Dataset card mô tả nhãn nhị phân 0/1, nhưng mẫu đã đọc không đúng tập giá trị này. Kiểm tra tiếp bên dưới xác định cách gộp nhãn và đối chiếu vector; không suy encoding toàn bộ tập từ một mẫu.

## Kết quả kiểm tra tiếp

Vector của mẫu mang nhãn `SEEPAGE SLICK`, mã polygon `OS03000GXS1`. Dùng pixel scale/tiepoint của TIFF để chuyển tâm 480.000 pixel sang kinh/vĩ độ, rồi kiểm tra điểm nằm trong polygon bằng Matplotlib Path (trừ các lỗ nếu có): **3.574 pixel trong polygon; 0 pixel khác với mask > 0**. Đây là bằng chứng căn chỉnh vector–mask trên lưới GeoTIFF của mẫu, chưa phải căn chỉnh với ảnh SAR gốc.

Mã nguồn `pipeline_ml/scripts/common.py` của tác giả thực hiện `(mask_np > 0).astype(np.int64)` và ghi rõ gộp 1/2 thành `SLICK`. Vì vậy sai khác tài liệu 0/1 so với tệp 0/2 có lời giải thích cho phép đánh giá nhị phân của tác giả. Không dùng lớp dầu thấm tự nhiên này làm nhãn look-alike.

Truy vấn catalog ASF theo nền tảng, mức xử lý và thời điểm, lọc đúng giờ bắt đầu, tìm được một cảnh ứng viên:

`S1A_IW_GRDH_1SDV_20200117T001541_20200117T001606_030833_03899B_5AEE`

Đã tải và xác nhận `productInfo.json` có đúng ID, annotation VV gồm **210 điểm geolocation**, góc tới **30,80163–46,21078°**, và **27 vector hiệu chuẩn**. Các giá trị này thuộc metadata cảnh gốc, không phải bản đồ góc đã căn chỉnh cho tile. Cảnh có VV/VH; chưa xác nhận tile được xuất từ phân cực nào, đơn vị cường độ, phép lọc/nội suy hoặc quy trình terrain correction của tác giả.

## Quyết định hiện tại

**Chưa đủ điều kiện dùng để tuyên bố chuẩn hóa góc tới cải thiện phát hiện dầu.** Encoding nhị phân và vector đã được đối chiếu cho một mẫu; đã có cảnh ứng viên và metadata vật lý. Cần xác nhận phân cực, đơn vị bức xạ, lịch sử xử lý và phép ánh xạ với ảnh gốc. Sau đó mới kiểm kê các mẫu còn lại, khóa protocol, chia tập theo cảnh và chạy đối chứng có/không chuẩn hóa trên cùng nhãn.

Phạm vi kiểm kê chỉ là một cặp ảnh, không phải xác minh toàn bộ 173 cặp. Chưa chạy mô hình trên nguồn này, chưa có Precision/Recall/F1 và chưa thêm nguồn vào gói review v4 bất biến.

## Ánh xạ và tải SAR gốc đã thực hiện

```powershell
.venv/Scripts/python.exe scripts/map_cantarell_native_grid.py
.venv/Scripts/python.exe scripts/fetch_cantarell_native.py
```

Script ánh xạ tự cài nội suy song tuyến tính và đạo hàm bằng NumPy, giải nghịch đảo lưới geolocation bằng Newton trên đủ 480.000 tâm pixel. Hội tụ sau 4 vòng; miền tương ứng trên ảnh gốc là dòng 6601,68–8031,87, cột 9618,35–11324,34. Góc tới nội suy trong tile là **37,20443–38,25841°**.

Đối chiếu nội suy với SciPy trên toàn tile: sai số tuyệt đối tối đa kinh độ 4,27×10⁻¹⁴ độ, góc tới 2,14×10⁻¹⁴ độ. Đối chiếu nghiệm nghịch đảo bằng `scipy.optimize.least_squares` tại 9 điểm: sai số lớn nhất 2,04×10⁻¹⁰ pixel. Đây là độ nhất quán số học trên cùng metadata, **không phải sai số định vị thực địa**. Phương pháp song tuyến tính này chưa thay thế range-Doppler terrain correction.

Đã tải các block TIFF VV phủ miền trên bằng HTTP range, **6.533.766 byte**, dựng vùng DN uint16 2048×3072. Mỗi byte-range và tệp có SHA-256. Nội suy LUT sigma0, tính DN²/LUT² trên lưới gốc rồi nội suy cường độ tuyến tính sang lưới tile; đối chiếu bước lấy mẫu với SciPy, sai số tối đa 7,11×10⁻¹⁵. Chưa trừ thermal noise.

Nếu **tạm giả định** giá trị ảnh xuất là VV sigma0-dB, tương quan Pearson với ảnh mới là **0,525317**, chênh trung vị **+0,471058 dB**, RMSE **2,545727 dB**. Các số này kiểm tra giả thuyết, không xác nhận đơn vị hoặc phân cực của ảnh xuất. [Hình đối chiếu](cantarell_native_comparison.png) đã được xem trực tiếp: cấu trúc sáng và vùng polygon tương ứng về bố cục tổng thể, nhưng không đủ chứng minh khớp ở độ chính xác pixel. Cần kiểm tra sai lệch đăng ký ảnh và lịch sử xử lý trước khi dùng để đo lợi ích hiệu chuẩn.

Chi tiết có thể tái kiểm tra: `cantarell_mapping_audit.json`, `cantarell_native_audit.json`. Mã không thay SOS, không chọn thuật toán bằng nhãn mẫu này và chưa công bố điểm phát hiện.

## Chẩn đoán độ lệch bằng nội dung ảnh

```powershell
.venv/Scripts/python.exe scripts/check_cantarell_registration.py
```

Script **không đọc mask**. Trừ trung bình, dùng cửa sổ Hann, tính tương quan pha FFT bằng NumPy và đối chiếu vị trí đỉnh nguyên pixel với `skimage.registration.phase_cross_correlation`. Hai cách cùng cho dịch chuyển **[0, −1] pixel**. Kiểm tra dấu dịch trên ảnh tổng hợp dịch biết trước [5, −7] cho nghiệm đúng [−5, 7]. Phần tinh chỉnh dưới pixel dùng skimage với hệ số 100, không gọi đây là phần tự cài NumPy.

Ước lượng toàn ảnh: dịch ảnh SAR đã lấy mẫu **[+0,04 hàng, −0,88 cột]** để khớp ảnh xuất. Chín block cố định, không chồng nhau, có dịch hàng trong **[0,03; 0,05]**, dịch cột trong **[−0,89; −0,87]**. Không bỏ block có kết quả xấu và không chọn vùng theo nhãn.

Trên miền trong bỏ 8 pixel mỗi cạnh (457.856 pixel), tương quan tăng **0,529939 → 0,894977**, RMSE dưới giả thuyết sigma0-dB giảm **2,545847 → 1,451130**. Chênh trung vị sau dịch vẫn **+0,417032 dB**. Kết quả chỉ ra thành phần sai lệch đăng ký ảnh, nhưng chưa xác định nguyên nhân hoặc xác nhận quy trình bức xạ của ảnh xuất.

Các thống kê trước/sau dùng chính ảnh đã ước lượng dịch: **chẩn đoán mô tả, không phải validation độc lập**. Cần kiểm tra trên mẫu khác trước khi dùng quy tắc căn chỉnh trong thí nghiệm. Mã không ghi đè ảnh hoặc nhãn; số liệu từng block và giới hạn nằm trong `cantarell_registration_audit.json`.

## Kiểm tra chuyển độ dịch sang tile thứ hai

Giao thức `cantarell_registration_protocol.json` đã được commit trong `50f13c2` **trước khi tải ảnh thứ hai**. Chọn `IMG_01_TILE_002`, giữ nguyên dịch `[0,04; −0,88]`, không dùng nhãn. Ngưỡng kiểm tra kỹ thuật 0,25 pixel được ghi trước, không phải định lý hoặc khoảng tin cậy thống kê.

```powershell
.venv/Scripts/python.exe scripts/check_cantarell_transfer.py
```

Đã thực thi xong; bounding box hai tile **không giao nhau** (tỉ lệ chồng bằng 0). Trên cùng 457.856 pixel nội vùng:

| Phép đo | Trước dịch | Sau dịch cố định |
|---|---:|---:|
| Tương quan Pearson | 0,393955 | 0,882135 |
| RMSE dưới giả thuyết sigma0-dB | 2,735976 | 1,589774 |
| Chênh trung vị ảnh gốc đã lấy mẫu − ảnh xuất | +0,594605 | +0,536722 |

Độ dịch ước lượng riêng của tile kiểm tra lệch tối đa **0,02 pixel** so với quy tắc đã khóa. Cả ba điều kiện đạt: sai khác dịch ≤0,25 pixel, tương quan tăng, số pixel hữu hạn giữ nguyên. Không thay độ dịch cố định bằng nghiệm mới khi báo cáo phép thử chuyển.

Đây là kiểm tra trên tile khác **cùng một cảnh**, không phải đánh giá tổng quát sang cảnh Sentinel độc lập. Không chồng bounding box không làm hai tile độc lập về thời tiết, sensor hoặc xử lý nguồn. Kết quả chưa chứng minh đơn vị ảnh xuất, nhãn tuyệt đối, hay lợi ích chuẩn hóa góc tới đối với phát hiện dầu. Bằng chứng đầy đủ gồm hash giao thức, ảnh nguồn, các byte-range DN và số liệu tại `cantarell_transfer_audit.json`.
