# 🗺️ LỘ TRÌNH TỰ CODE CHAY TOÀN BỘ DỰ ÁN TỪ SỐ 0 BẰNG NUMPY THUẦN

> **Phạm vi tài liệu tự học — cập nhật 17/11/2026:** đây là giải thích và mã minh họa độc lập, không phải pipeline đã nghiệm thu hoặc bằng chứng đạt 100% đề. Công thức giản lược, ảnh giả lập, ví dụ ghép greedy và mô phỏng trôi dầu không thay thế kết quả trong `src/sar_oil`, `scripts` và `results`. Lee không bảo đảm giữ biên tuyệt đối; agreement 100% chỉ áp dụng cho ca đã đo; F1 SOS 0,3403 là cấu hình được chọn theo quy tắc dung sai, không phải cực đại nghiêm ngặt. Ưu tiên [đối chiếu hiện tại](../../docs/DANH_GIA_DU_AN_VA_DOI_CHIEU_DE_18.md) khi có khác biệt.

## Dự án: Phát hiện vết dầu tràn trên biển từ ảnh SAR (Đề 18 — NASA #6)

> 💡 **Triết lý của bộ tài liệu này:**
> *"Cái gì tôi không thể tự tạo ra từ con số 0, tôi không thực sự hiểu nó."* (Richard Feynman).
>
> Thay vì chỉ gọi `cv2.filter2D()`, `cv2.threshold()`, `scipy.ndimage.label()`, `sklearn.svm.LinearSVC()`, bộ cẩm nang này sẽ hướng dẫn bạn **tự tay viết lại từng dòng code bằng NumPy thuần**, hiểu tường tận từng phép nhân ma trận, từng phép quét cửa sổ và từng bước tối ưu hóa toán học!

---

## 📂 CẤU TRÚC THƯ MỤC HỌC TẬP (`study_guide/tu_code_du_an/`)

Toàn bộ mã nguồn và lý thuyết được chia thành 8 thư mục module chuyên biệt, độc lập và có tính kế thừa:

```
study_guide/tu_code_du_an/
├── README.md                             <-- BẠN ĐANG Ở ĐÂY (Bản đồ hướng dẫn tổng thể)
│
├── 01_tien_xu_ly_va_du_lieu/             <-- MODULE 1: Dữ liệu SAR & Góc tới
│   ├── ly_thuyet_va_huong_dan.md         # Bản chất ảnh SAR, ma trận float32, góc tới LUT
│   └── data_loader.py                    # Code chay đọc ảnh, chuẩn hóa bức xạ, nội suy góc tới
│
├── 02_khu_nhieu_speckle/                 <-- MODULE 2: Lọc đốm thích nghi
│   ├── ly_thuyet_va_huong_dan.md         # Bản chất nhiễu nhân, chứng minh Lee Filter MMSE
│   └── speckle_filters.py                # Code chay 4 bộ lọc: Mean SAT O(1), Median, Gaussian, Lee
│
├── 03_phan_doan_va_hinh_thai/            <-- MODULE 3: Tách đốm tối & Liên thông
│   ├── ly_thuyet_va_huong_dan.md         # Otsu phương sai liên lớp, Niblack thích nghi, Loang 8 hướng
│   └── segmentation.py                   # Code chay Otsu, Niblack O(1), Gán nhãn liên thông, Erode/Dilate
│
├── 04_trich_xuat_8_dac_trung/            <-- MODULE 4: Thẻ căn cước 8 chiều
│   ├── ly_thuyet_va_huong_dan.md         # Chứng minh toán học 8 đặc trưng: Elongation, Complexity, Sobel, Vành 5px
│   └── feature_extraction.py             # Code chay trích xuất chính xác 8 đặc trưng hình học & cường độ
│
├── 05_hoc_may_tu_so_0/                   <-- MODULE 5: Thuật toán Học máy tự viết
│   ├── ly_thuyet_va_huong_dan.md         # Toán học CART (Gini) & Linear SVM (Nesterov Accelerated Gradient)
│   └── machine_learning.py               # Code chay StandardScaler, CART đệ quy, Bộ giải tối ưu SVM
│
├── 06_danh_gia_va_do_luong/              <-- MODULE 6: Thước đo đánh giá khoa học
│   ├── ly_thuyet_va_huong_dan.md         # Tiêu chuẩn ghép cặp đối tượng IoU>=0.5, Precision, Recall, F1
│   └── evaluation.py                     # Code chay ghép cặp đối tượng, ma trận nhầm lẫn, phát hiện sai
│
├── 07_mo_phong_troi_dat_dau/             <-- MODULE 7: Mô phỏng vật lý trôi dạt
│   ├── ly_thuyet_va_huong_dan.md         # Phương trình bình lưu dòng chảy + 3% gió + Monte Carlo khuếch tán
│   └── drift_simulation.py               # Code chay mô phỏng trôi dạt 48h, biến dạng đa giác vết dầu
│
└── 08_pipeline_tong_hop/                 <-- MODULE 8: Ghép nối toàn bộ hệ thống
    ├── ly_thuyet_va_huong_dan.md         # Hợp đồng đầu vào/đầu ra, cấu hình pipeline hoàn chỉnh
    └── full_pipeline.py                  # Kịch bản End-to-End chạy toàn bộ quy trình từ ảnh đến kết quả
```

---

## 🚀 THỨ TỰ BẠN NÊN TỰ CODE VÀ HỌC TẬP

1. **Bước 1 — Hiểu dữ liệu đầu vào**: Đọc `01_tien_xu_ly_va_du_lieu/ly_thuyet_va_huong_dan.md`. Tự gõ `data_loader.py` để hiểu ma trận ảnh SAR khác ảnh RGB thông thường như thế nào.
2. **Bước 2 — Quét sạch hạt tiêu**: Đọc `02_khu_nhieu_speckle/ly_thuyet_va_huong_dan.md`. Tự code `speckle_filters.py`, quan sát tại sao Lee filter giữ được cạnh còn Mean làm nhòe ảnh.
3. **Bước 3 — Cắt bánh tìm đốm đen**: Đọc `03_phan_doan_va_hinh_thai/ly_thuyet_va_huong_dan.md`. Tự code thuật toán Otsu và gán nhãn 8 hướng trong `segmentation.py`.
4. **Bước 4 — Lập hồ sơ vết dầu**: Đọc `04_trich_xuat_8_dac_trung/ly_thuyet_va_huong_dan.md`. Tự tính 8 đặc trưng toán học trong `feature_extraction.py`.
5. **Bước 5 — Trở thành nhà toán học học máy**: Đọc `05_hoc_may_tu_so_0/ly_thuyet_va_huong_dan.md`. Tự code bộ giải Gradient Descent tìm siêu phẳng SVM trong `machine_learning.py`.
6. **Bước 6 — Đánh giá công bằng**: Đọc `06_danh_gia_va_do_luong/ly_thuyet_va_huong_dan.md`. Tự code thuật toán ghép cặp IoU $\ge 0.5$ trong `evaluation.py`.
7. **Bước 7 — Dự báo tương lai**: Đọc `07_mo_phong_troi_dat_dau/ly_thuyet_va_huong_dan.md`. Tự code mô phỏng trôi dạt Lagrangian trong `drift_simulation.py`.
8. **Bước 8 — Về đích rực rỡ**: Mở `08_pipeline_tong_hop/full_pipeline.py`, kết nối toàn bộ các hàm lại với nhau thành một hệ thống xử lý ảnh hoàn chỉnh!

Hãy bắt đầu khám phá từng thư mục bên dưới!
