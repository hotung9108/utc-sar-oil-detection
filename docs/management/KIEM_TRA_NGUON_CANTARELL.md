# Kiểm tra nguồn bổ sung cho nhánh góc tới

Mục đích: tìm ảnh SAR có nhãn và thông tin vật lý để đánh giá tác động chuẩn hóa góc tới. SOS vẫn là tập chính; kiểm tra này chưa tạo thí nghiệm hay thay kết quả đã khóa.

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
