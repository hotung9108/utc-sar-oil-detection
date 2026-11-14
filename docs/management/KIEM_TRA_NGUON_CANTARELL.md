# Kiểm tra nguồn bổ sung cho nhánh góc tới

Mục đích: tìm ảnh SAR có nhãn và thông tin vật lý để đánh giá tác động chuẩn hóa góc tới. SOS vẫn là tập chính; kiểm tra này chưa tạo thí nghiệm hay thay kết quả đã khóa.

Nguồn: [Garcia-INPE/oilspill-detection-dataset](https://github.com/Garcia-INPE/oilspill-detection-dataset), revision `1b9a62c30a9da9698eb470562aa976f9bd1e8fc3`. Đã tải tài liệu, giấy phép, bảng CSV, ba split và **một** cặp raster/mask. Script xử lý Git LFS và xác nhận kích thước/SHA-256 theo pointer; từng nguồn có receipt trong `cantarell_source_audit.json`.

Chạy lại từ thư mục gốc:

```powershell
.venv/Scripts/python.exe scripts/audit_cantarell_source.py
```

## Những gì đã đo trực tiếp

- Bảng có 385 polygon: 327 `OIL SPILL`, 58 `SEEPAGE SLICK`. Dầu thấm tự nhiên không được tự đổi thành nhãn tương tự dầu do gió yếu, màng sinh học hoặc mưa.
- Split có 108/43/22 mẫu. Nhóm tiền tố `IMG_XX` không giao nhau giữa ba split; đây chưa chứng minh độc lập cảnh Sentinel gốc.
- `IMG_01_TILE_001.tiff` trong thư mục tên `16-BIT` thực tế có dtype **float32**, kích thước 600×800, giá trị hữu hạn từ −48,88188 đến 17,69975. Không suy đơn vị sigma0-dB chỉ từ khoảng số hoặc tên tệp có `Cal`.
- TIFF có thông tin WGS84/EPSG:4326, pixel scale và tiepoint. Những tag đã đọc không cung cấp góc tới từng pixel hoặc định nghĩa đơn vị bức xạ.
- Mask cùng kích thước có **476.426 pixel giá trị 0 và 3.574 pixel giá trị 2**. Dataset card mô tả nhãn nhị phân 0/1, nhưng mẫu đã đọc không đúng tập giá trị này. Chưa xác định ý nghĩa giá trị 2; không âm thầm remap thành dầu. Cùng kích thước cũng chưa đủ chứng minh căn chỉnh với lưới SAR gốc.

## Quyết định hiện tại

**Chưa đủ điều kiện dùng để tuyên bố chuẩn hóa góc tới cải thiện phát hiện dầu.** Đây là ứng viên có thông tin địa lý đáng khảo sát, chưa phải nguồn đã xác minh đầy đủ. Cần đối chiếu encoding mask với vector/pipeline của tác giả; xác nhận phân cực, đơn vị bức xạ và lịch sử xử lý; xác định đầy đủ SAFE gốc, góc tới và phép ánh xạ nhãn. Sau đó mới khóa protocol, chia tập theo cảnh và chạy đối chứng có/không chuẩn hóa trên cùng nhãn.

Phạm vi kiểm kê chỉ là một cặp ảnh, không phải xác minh toàn bộ 173 cặp. Chưa chạy mô hình trên nguồn này, chưa có Precision/Recall/F1 và chưa thêm nguồn vào gói review v4 bất biến.
