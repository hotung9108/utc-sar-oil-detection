# Kiểm tra Refined Deep-SAR Oil Spill — SOS

Ngày kiểm tra: 13/11/2026. Nhóm đã chọn Refined SOS; kết luận hiện tại: dùng được làm benchmark phân đoạn dầu/nền, nhưng chưa đủ dữ liệu để đáp ứng độc lập toàn bộ Đề 18. Không thay đổi hoặc di chuyển dữ liệu gốc.

## Nguồn và nhãn

Nguồn chính thức: https://zenodo.org/records/15298010 — DOI 10.5281/zenodo.15298010, Zuenko và Khaidarova. Tác giả công bố đã hiệu chỉnh thủ công khoảng 38% mask train và 50% mask validation bằng kiểm tra trực quan. Đây là nhãn tham chiếu được cải thiện, không phải xác nhận thành phần dầu tại hiện trường.

Bài SOS gốc: https://doi.org/10.1109/TGRS.2021.3115492. SOS gồm ảnh từ PALSAR và Sentinel-1; không phải bộ ảnh NASA. Bộ dữ liệu là ảnh đã xử lý, không được mặc định là sigma0 đã hiệu chuẩn.

## Kiểm kê bản cục bộ

Đường dẫn: `data/Refined-Deep-SAR/`. Loader phải dùng `images/images/{train,val}` và `masks/masks/{train,val}`, ghép theo tên file. Bỏ qua `__MACOSX`, `._*` và `.DS_Store`.

| Split | Nhóm tên | Cặp ảnh–mask | Mask rỗng | Mask toàn foreground | Tỷ lệ foreground |
| --- | --- | ---: | ---: | ---: | ---: |
| train | palsar | 3101 | 95 | 4 | 20.70% |
| train | sentinel | 3354 | 154 | 32 | 30.30% |
| val | palsar | 776 | 45 | 1 | 17.92% |
| val | sentinel | 839 | 31 | 20 | 35.49% |

- Lỗi đọc/kích thước: 0.
- Thiếu mask: 0; mask không có ảnh: 0.
- Nhóm ảnh trùng pixel hoàn toàn: 0; nhóm trùng xuyên train/val: 0; nhóm trùng ảnh nhưng khác mask: 0.
- Chi tiết shape, mode, giá trị nhãn và metadata được ghi trong `refined_sos_audit.json`. Histogram mask trong JSON đếm giá trị trên tất cả kênh; tỷ lệ foreground trong bảng dùng kênh đầu, không nhân ba theo RGB.
- Đã xem trực tiếp hai cặp sentinel_0 và palsar_0: vùng mask trắng đánh dấu các vùng tối. Đây chỉ là kiểm tra mẫu, không chứng minh mọi nhãn đúng.

## Các giới hạn quyết định cách làm bài

### Phát hiện bổ sung quan trọng: mask train chưa thuần nhị phân

- 1.847/6.455 mask train có giá trị trung gian 1–254: 994 PALSAR và 853 Sentinel. Tất cả 1.615 mask val chỉ có 0/255.
- Tổng 6.105.247 pixel mức trung gian ở train (đếm một kênh). Ảnh và mask RGB được kiểm tra có các kênh bằng nhau; mask còn lại ở mode L.
- Ví dụ đã xem: `train/palsar_1260.png`. Chưa kết luận nguyên nhân do resize, augmentation hay thao tác hiệu chỉnh chỉ từ giá trị pixel.
- Bảng tỷ lệ phía trên là thống kê `mask > 0`, **chưa phải tỷ lệ diện tích dầu chuẩn để huấn luyện**. Với ngưỡng 128, tổng pixel foreground train giảm 3.152.878 pixel so với `> 0`.
- Trước khi huấn luyện phải xác minh quy tắc nhãn từ mã/tác giả. Có thể khảo sát nhị phân hóa ở 128 như một giả định được công bố, nhưng không coi đây là quy tắc nhà phát hành đã xác nhận. Không ghi đè mask gốc; khi resize mask nhị phân dùng nearest-neighbor.

1. **Nhãn nhị phân:** dầu/nền không cung cấp nhãn riêng gió yếu, màng sinh học và mưa. Được huấn luyện dầu/nền hoặc dầu/ứng viên không dầu; không gọi mọi pixel nền là look-alike đã xác nhận.
2. **Góc tới và gió:** không tìm thấy sidecar metadata trong bản cục bộ. Không có căn cứ thực hiện chuẩn hóa góc tới hay ghép gió theo vị trí/thời gian chỉ từ PNG này. Muốn hoàn thành phần vật lý phải bổ sung cảnh gốc/metadata hoặc dữ liệu kiểm chứng riêng.
3. **Độc lập chia tập:** chỉ có train và val. So trùng pixel không phát hiện patch chồng lấn, ảnh xoay hoặc thêm nhiễu. Chưa có ánh xạ patch–cảnh nên chưa chứng minh train/val độc lập theo cảnh.
4. **Mức đối tượng:** mask semantic không có ID từng vết dầu. Có thể suy đối tượng bằng liên thông, nhưng phải công bố quy tắc và các ca chia/cắt tại mép patch; đây không phải nhãn instance chuẩn.
5. **Nguồn tải:** bản cục bộ không có ZIP nên chưa đối chiếu MD5 của images.zip và masks.zip do Zenodo công bố. Chưa xác minh giấy phép cụ thể vì nội dung trang đọc được không hiển thị thông tin giấy phép và API/export không truy cập được. Không mặc định là CC BY.

## Cách sử dụng đề xuất

- Ưu tiên nhóm Sentinel cho bài chính phù hợp Đề 18; báo riêng PALSAR để khảo sát khác cảm biến, không trộn kết quả mà không phân tầng.
- Dùng mask để đo phân đoạn và đối tượng suy ra. So sánh lọc/ngưỡng/đặc trưng/CART/SVM trên cùng split; dùng bản tự cài và thư viện đối chứng.
- Chọn giao thức split trước thí nghiệm: nếu giữ val của nhà phát hành làm holdout cuối, không dùng nó chọn tham số; tách validation nội bộ từ train theo nhóm cảnh nếu khôi phục được. Nếu chưa có scene ID phải công bố giới hạn, không tuyên bố kiểm tra trên cảnh độc lập.
- Chưa chọn Lee/Frost/ngưỡng hay mô hình cuối. Chưa chạy huấn luyện hoặc tạo Precision/Recall/F1 trong đợt kiểm tra này.
- Để đánh giá đúng nhầm dầu/look-alike và góc tới/gió, cần nguồn bổ sung; Refined SOS vẫn có thể là benchmark chính cho phần ảnh–mask.

## Tái lập

Chạy `.venv/Scripts/python.exe scripts/audit_refined_sos.py` trong môi trường có Pillow và NumPy. Script chỉ đọc dataset và ghi JSON kiểm kê. Không kiểm tra near-duplicate hoặc xác nhận nhãn bằng hiện trường.
