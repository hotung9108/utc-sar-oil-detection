# 📊 MODULE 6: ĐÁNH GIÁ THỰC NGHIỆM VÀ ĐỐI CHỨNG KHOA HỌC

> **Phạm vi tài liệu tự học — cập nhật 17/11/2026:** đây là giải thích và mã minh họa độc lập, không phải pipeline đã nghiệm thu hoặc bằng chứng đạt 100% đề. Công thức giản lược, ảnh giả lập, ví dụ ghép greedy và mô phỏng trôi dầu không thay thế kết quả trong `src/sar_oil`, `scripts` và `results`. Lee không bảo đảm giữ biên tuyệt đối; agreement 100% chỉ áp dụng cho ca đã đo; F1 SOS 0,3403 là cấu hình được chọn theo quy tắc dung sai, không phải cực đại nghiêm ngặt. Ưu tiên [đối chiếu hiện tại](../../../docs/DANH_GIA_DU_AN_VA_DOI_CHIEU_DE_18.md) khi có khác biệt.

## 1. TẠI SAO ĐÁNH GIÁ MỨC ĐỐI TƯỢNG (OBJECT-LEVEL) LẠI KHẮC NGHIỆT HƠN PIXEL-LEVEL?

### 1.1. Cái bẫy của Pixel IoU và Độ chính xác Pixel
Trong một lát cắt ảnh SAR kích thước $1000 \times 1000 = 1.000.000$ pixel:
- Mặt biển chiếm $995.000$ pixel ($99.5\%$).
- Vết dầu tràn chỉ chiếm $5.000$ pixel ($0.5\%$).

Nếu một sinh viên viết một thuật toán "lười biếng": **Gán toàn bộ ảnh là biển (tất cả pixel = 0)**:
- Độ chính xác pixel đạt: **$99.5\%$** (Trông rất đẹp nhưng thực tế là đồ phế thải vì không tìm thấy giọt dầu nào!).
- Đó là lý do trong nghiên cứu khoa học chuẩn mực của Đề 18, ta **tuyệt đối không dùng Pixel Accuracy** để báo cáo chất lượng phát hiện!

### 1.2. Chuẩn ghép cặp đối tượng (Object-Level IoU $\ge 0.5$)
Theo tiêu chuẩn quốc tế (PASCAL VOC / COCO):
1. Một vết dầu dự đoán (Prediction) được coi là **Bắt trúng (True Positive - TP)** nếu và chỉ nếu nó đè lên vết dầu thật (Ground Truth - GT) với tỷ lệ diện tích giao trên hợp:
$$\text{IoU} = \frac{|\text{Pred} \cap \text{GT}|}{|\text{Pred} \cup \text{GT}|} \ge 0.5$$
2. Nếu $\text{IoU} < 0.5$ hoặc vết dầu phát hiện ra nằm ở vùng biển sạch $\implies$ Tính là **Báo động giả (False Positive - FP)**.
3. Nếu một vết dầu thật ngoài biển mà thuật toán không tìm ra $\implies$ Tính là **Bỏ sót (False Negative - FN)**.

---

## 2. CÔNG THỨC PRECISION, RECALL, F1 VÀ TỶ LỆ BÁO SAI

$$\text{Precision} = \frac{TP}{TP + FP} \quad (\text{Trong số vết máy báo là dầu, bao nhiêu \% là dầu thật?})$$
$$\text{Recall} = \frac{TP}{TP + FN} \quad (\text{Trong số vết dầu thật ngoài biển, máy bắt được bao nhiêu \%?})$$
$$F_1 = 2 \cdot \frac{\text{Precision} \cdot \text{Recall}}{\text{Precision} + \text{Recall}} \quad (\text{Trung bình điều hòa cân bằng giữa bắt đúng và không bắt nhầm})$$
$$\text{False Alarm Rate} = \frac{\text{Tổng số ca FP}}{\text{Tổng số ảnh kiểm tra}} \quad (\text{Trung bình 1 bức ảnh báo nhầm bao nhiêu lần?})$$

### 2.3. Sự đóng góp của bộ phân lớp học máy trong dự án
Khi đo trên **839 ảnh Test độc lập** của tập chuẩn Refined SOS:
- **Nếu chỉ dùng lọc Lee + Otsu (không có SVM):**
  - Recall = $31.99\%$, Precision = $7.53\%$, F1 = $0.1220$.
  - Số ca báo động giả lên tới: **$14.89$ FP/ảnh** (Cứ 1 ảnh lại báo nhầm 15 chỗ!).
- **Khi kết hợp Linear SVM trên 8 đặc trưng:**
  - Recall = $31.30\%$, Precision tăng vọt lên $25.41\%$, F1 tăng lên **$0.2805$**.
  - Số ca báo động giả giảm từ $14.89$ xuống chỉ còn **$3.48$ FP/ảnh**!
  $\implies$ Học máy đã gạt bỏ được hơn $76\%$ các ca báo động giả do vùng biển lặng gió gây ra!

Mở file `evaluation.py` để tự tay gõ từng dòng thuật toán!
