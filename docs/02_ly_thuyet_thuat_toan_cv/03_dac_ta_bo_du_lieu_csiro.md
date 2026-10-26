# ĐẶC TẢ BỘ DỮ LIỆU CSIRO SENTINEL-1 SAR OIL SPILL
## Thông Số Kỹ Thuật, Cấu Trúc Phân Bố & Định Dạng Dữ Liệu Thực Nghiệm
**Dự án:** Đề tài 18 — Phát hiện vết dầu tràn trên biển từ ảnh SAR (NASA #6)

---

## 1. THÔNG SỐ VỆ TINH & CẢM BIẾN SAR SENTINEL-1

- **Vệ tinh:** Sentinel-1A / Sentinel-1B (Cơ quan Vũ trụ Châu Âu — ESA, chương trình Copernicus).
- **Cảm biến:** Radar Khẩu độ Tổng hợp C-band (Synthetic Aperture Radar — C-SAR).
- **Tần số hoạt động:** $5.405\text{ GHz}$ (Bước sóng $\lambda \approx 5.54\text{ cm}$).
- **Chế độ chụp:** Chế độ dải quét rộng giao thoa (Interferometric Wide Swath — IW).
- **Phân cực sóng:** VV (Truyền thẳng đứng, nhận thẳng đứng — phân cực tối ưu nhất để quan sát sóng mao dẫn biển).
- **Độ phân giải không gian gốc:** $20\text{ m} \times 22\text{ m}$ trên mặt đất.

---

## 2. QUY CÁCH DỮ LIỆU ĐÓNG GÓI (CHIPS)

Bộ dữ liệu nghiên cứu được cơ quan khoa học quốc gia Australia (**CSIRO**) và NASA cắt nhỏ thành các lát ảnh (chips) phục vụ nghiên cứu thị giác máy tính:
- **Kích thước ảnh:** $400 \times 400$ pixel.
- **Kênh màu:** Ảnh mức xám 1 kênh (Grayscale uint8, dải giá trị $[0, 255]$).
- **Định dạng lưu trữ:** JPEG / TIFF.
- **Tổng số lượng mẫu:** **5,630 ảnh**.

---

## 3. CẤU TRÚC PHÂN PHỐI 2 LỚP DỮ LIỆU

### 3.1. Lớp 1 (`data/Class_1/` — 1,905 ảnh): Vết Dầu Tràn Thực Tế (Oil Slicks)
- Chứa các vết dầu loang thực tế do tàu thuyền xả thải trộm, súc rửa hầm hàng (bilge water discharge), hoặc các sự cố rò rỉ giàn khoan ngoài khơi.
- **Đặc trưng thị giác:**
  - Tạo thành các vệt tối màu kéo dài, uốn lượn ngoằn ngoèo theo hướng di chuyển của tàu hoặc dòng hải lưu.
  - Tỉ số trục chính trên trục phụ cao ($\text{Elongation} \ge 1.8 - 4.0$).
  - Đường ranh giới giữa dầu và nước biển có độ dốc tán xạ rất sắc nét do sức căng bề mặt.

### 3.2. Lớp 0 (`data/Class_0/` — 3,725 ảnh): Không Chứa Dầu / Hiện Tượng Tương Tự (Look-alikes)
- Chứa các bề mặt đại dương không có dầu tràn:
  - **Biển sạch đồng nhất:** Mặt biển có gió ổn định, tán xạ Bragg phân bố đều.
  - **Vùng gió lặng (Low Wind Zones):** Tốc độ gió dưới $2\text{ m/s}$ không đủ tạo sóng mao dẫn, tạo mảng đen rộng bè.
  - **Màng sinh học tảo biển (Biogenic Slicks):** Dịch tiết hữu cơ mỏng của vi sinh vật phù du làm giảm sóng mao dẫn cục bộ nhưng ranh giới chuyển tiếp thoai thoải.
  - **Bóng mây mưa (Rain Cells) & Sóng nội ngầm (Internal Waves).**
