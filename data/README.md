# Dữ liệu hiện hành

Dữ liệu chính: Refined Deep-SAR Oil Spill — SOS v1, https://zenodo.org/records/15298010. 8070 cặp PNG/mask trong `Refined-Deep-SAR/images/images/{train,val}` và `masks/masks/{train,val}`. Dữ liệu thô được gitignore; không phân phối lại khi chưa làm rõ giấy phép.

`manifest.json` lưu SHA256 ảnh/mask, sensor, split nhà phát hành và split thực nghiệm. Sentinel: train2683, validation671, test839. PALSAR val776 dùng đánh giá ngoài miền; PALSAR train3101 chỉ được kiểm kê. Mask >=128, không sửa ảnh gốc. Chạy `python scripts/sos.py prepare` để tái tạo manifest.

Thiếu scene ID, góc tới, gió, tọa độ/thời gian và nhãn riêng look-alike. Không suy metadata từ ảnh PNG. Xem `docs/management/KIEM_TRA_REFINED_SOS.md` và `docs/GIAO_THUC_THUC_NGHIEM.md`. Dữ liệu CSIRO/mẫu cũ nằm trong legacy.
