# Kiểm kê toàn bộ Cantarell trước thí nghiệm

Nguồn được ghim tại revision `1b9a62c30a9da9698eb470562aa976f9bd1e8fc3`. Tái tạo bằng `python scripts/report_cantarell_inventory.py` sau hai script kiểm kê. Không có chỉ số phát hiện hoặc lựa chọn thuật toán trong báo cáo này.

| Tập | Tile | Cảnh Sentinel đầy đủ |
|---|---:|---:|
| train | 108 | 16 |
| val | 43 | 4 |
| test | 22 | 4 |

- Đã đọc 173/173 TIFF, mask và GeoJSON; không có lỗi tải/đọc.
- Kiểu ảnh: {'float32': 173}; tổng pixel không hữu hạn: 0.
- Pixel mask: {'0': 81200523, '1': 612938, '2': 1226539}. 0=nền; 1=dầu tràn; 2=dầu thấm tự nhiên, theo đối chiếu vector bên dưới.
- Sai khác nhị phân giữa mask > 0 và polygon tại tâm pixel: 0 pixel trên toàn bộ tập.
- TIFF trùng nguyên tệp: 0 nhóm. Đây không thay thế phát hiện mọi kiểu crop/biến đổi trùng nhau.
- Cặp bounding box chồng nhau trong cùng cảnh: 26; trong đó khác split: 0.
- Mã cảnh đầy đủ xuất hiện ở nhiều split: {}.
- Mã polygon xuất hiện ở nhiều split: {'OS03029GXS1': ['test', 'train']}.

## Mã lớp và polygon trùng

- `IMG_15_TILE_001`: 48 pixel hai lớp vector chồng nhau.
- `IMG_19_TILE_009`: 808 pixel hai lớp vector chồng nhau.

Khi xét từng lớp riêng, hai mẫu trên có sai khác vì polygon dầu và dầu thấm chồng nhau. Quy tắc thử nghiệm “lớp dầu thấm ưu tiên ở phần chồng” cho số mẫu còn sai khác: **0**. Đây là đối chiếu encoding của tệp; không sửa nhãn và không biến dầu thấm thành look-alike.

Bảng CSV có 385 dòng nhưng 384 mã polygon duy nhất; mã lặp trong CSV: {'OS03029GXS1': 2}. Các GeoJSON chứa 458 lượt polygon, 384 mã duy nhất; 45 mã xuất hiện ở nhiều tile. Không được cộng các lượt này thành số sự kiện dầu độc lập. Tập mã CSV và vector khớp hoàn toàn.

### Mã polygon lặp qua split

- `OS03029GXS1` trong `17 S1B_IW_GRDH_1SDV_20200709T001514_NR_Orb_Cal_TC.tif`: tâm (19.459060207806804, -92.45859186881137), diện tích 0.49563723309854707 km².
- `OS03029GXS1` trong `18 S1B_IW_GRDH_1SDV_20200718T120032_NR_Orb_Cal_TC.tif`: tâm (19.34252575559022, -92.16587509721069), diện tích 17.609401472013417 km².

Hai bản ghi có thời điểm, vị trí và diện tích khác nhau. Mã lặp tự nó chưa chứng minh trùng ảnh hoặc cùng sự kiện, nhưng cũng không được bỏ qua khi chia tập. Trước khi khóa thí nghiệm, phải xử lý nhóm mã chưa rõ này hoặc ghi rõ giới hạn về độc lập sự kiện; chưa tự đổi split của tác giả trong kiểm kê này.

## Giới hạn

24 ID cảnh đã đối chiếu catalog ASF và productInfo công khai; phân tách theo cảnh không chứng minh độc lập sự kiện dầu hoặc thời tiết. Phép kiểm kê hình học đã chạy đủ tập, chưa xem trực quan từng ảnh. Chưa khôi phục ảnh DN/góc tới cho toàn bộ 173 tile; mới hai tile cùng cảnh có kiểm tra căn chỉnh. Chưa xác nhận toàn bộ lịch sử xử lý hoặc đơn vị TIFF xuất. SOS vẫn là bộ dữ liệu chính; gói review v4 không thay đổi.

Chứng cứ chi tiết: `cantarell_full_inventory.json`, `cantarell_scenes_audit.json`; từng tài nguyên có URL, SHA-256 và kiểm tra Git LFS khi áp dụng.
