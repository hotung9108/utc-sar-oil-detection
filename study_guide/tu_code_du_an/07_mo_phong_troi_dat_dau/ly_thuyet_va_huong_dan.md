# 🌊 MODULE 7: MÔ PHỎNG VẬT LÝ TRÔI DẠT DẦU (LAGRANGIAN DRIFT)

> **Phạm vi tài liệu tự học — cập nhật 17/11/2026:** đây là giải thích và mã minh họa độc lập, không phải pipeline đã nghiệm thu hoặc bằng chứng đạt 100% đề. Công thức giản lược, ảnh giả lập, ví dụ ghép greedy và mô phỏng trôi dầu không thay thế kết quả trong `src/sar_oil`, `scripts` và `results`. Lee không bảo đảm giữ biên tuyệt đối; agreement 100% chỉ áp dụng cho ca đã đo; F1 SOS 0,3403 là cấu hình được chọn theo quy tắc dung sai, không phải cực đại nghiêm ngặt. Ưu tiên [đối chiếu hiện tại](../../../docs/DANH_GIA_DU_AN_VA_DOI_CHIEU_DE_18.md) khi có khác biệt.

## 1. NGUYÊN LÝ VẬT LÝ CỦA SỰ TRÔI DẠT DẦU TRÊN ĐẠI DƯƠNG

Khi dầu đổ ra biển, nó không đứng yên một chỗ mà trôi dạt và biến dạng dưới tác động của 3 lực chính:
1. **Dòng chảy bề mặt đại dương (Ocean Current):** Dòng nước cuốn toàn bộ khối dầu đi theo vận tốc $\mathbf{u}_{\text{current}}$.
2. **Gió khí quyển bề mặt (Surface Wind):** Gió ma sát trực tiếp lên màng dầu nổi.
   - **Giả định minh họa trong code:** hệ số gió đặt bằng 0,03. Đây không phải vận tốc dầu luôn bằng đúng 3% vận tốc gió và chưa được hiệu chỉnh bằng quan sát của dự án:
$$\mathbf{u}_{\text{drift}} = \mathbf{u}_{\text{current}} + 0.03 \cdot \mathbf{u}_{\text{wind}}$$
3. **Khuếch tán rối ngẫu nhiên (Turbulent Diffusion):** Các xoáy nước nhỏ làm màng dầu bị xé vụn và loang rộng ra xung quanh. Ta mô hình hóa bằng chuyển động Brown (Random Walk):
$$d\mathbf{r}_{\text{diff}} = \sqrt{2 \cdot D_h \cdot \Delta t} \cdot \mathcal{N}(0, 1)$$

---

## 2. Giả định loang rộng trong ví dụ

Code dùng hệ số tăng kích thước tuyến tính giả định `1 + 0.08 * sqrt(h)` quanh tâm đa giác. Đây là quy tắc trực quan hóa chưa được xác minh, **không phải triển khai đã được kiểm chứng của mô hình Fay (1971)**. Nếu các tọa độ được nhân cùng hệ số thì diện tích tăng theo bình phương hệ số đó, chưa tính nhiễu khuếch tán. Không dùng ví dụ này để tuyên bố dự báo thực địa hoặc độ chính xác sau 24–48 giờ.

---

## 3. CHUYỂN ĐỔI HỆ TỌA ĐỘ TRẮC ĐỊA (MÉT $\to$ ĐỘ KINH VĨ)

Để vẽ được vệt dầu trôi dạt lên Bản đồ Vệ tinh thế giới, ta phải đổi độ dời tính bằng mét sang kinh độ và vĩ độ:
- $1^\circ$ vĩ độ (Latitude) tương đương:
$$\Delta \text{lat} = \frac{\Delta y}{111.139\text{ mét}}$$
- $1^\circ$ kinh độ (Longitude) co lại theo hàm cosin của vĩ độ:
$$\Delta \text{lon} = \frac{\Delta x}{111.139 \cdot \cos(\text{lat}_0)\text{ mét}}$$

Mở file `drift_simulation.py` để tự tay gõ từng dòng thuật toán!
