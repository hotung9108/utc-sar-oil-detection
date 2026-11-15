# Cẩm nang tự học chuyên sâu & Phản biện BTL Xử lý ảnh — Đề 18

> **Phạm vi tài liệu tự học — cập nhật 17/11/2026:** đây là giải thích và mã minh họa độc lập, không phải pipeline đã nghiệm thu hoặc bằng chứng đạt 100% đề. Công thức giản lược, ảnh giả lập, ví dụ ghép greedy và mô phỏng trôi dầu không thay thế kết quả trong `src/sar_oil`, `scripts` và `results`. Lee không bảo đảm giữ biên tuyệt đối; agreement 100% chỉ áp dụng cho ca đã đo; F1 SOS 0,3403 là cấu hình được chọn theo quy tắc dung sai, không phải cực đại nghiêm ngặt. Ưu tiên [đối chiếu hiện tại](../docs/DANH_GIA_DU_AN_VA_DOI_CHIEU_DE_18.md) khi có khác biệt.

## Chủ đề: Phát hiện vết dầu tràn trên biển từ ảnh SAR (NASA #6)

> 💡 **Mục đích của tài liệu:**\
> Tài liệu này được biên soạn độc lập, cách ly khỏi mã nguồn dự án, phục vụ mục tiêu giúp bạn **nắm vững bản chất từ con số 0**, hiểu tường tận **tại sao lại chọn từng công thức toán học**, có khả năng **tự tính tay trên số liệu nhỏ** và **tự tin phản biện mọi câu hỏi vặn vẹo của Hội đồng chấm BTL**.

---

## 🗺️ Bản đồ lộ trình học tập (7 Chuyên đề + 1 Cẩm nang ELI5 + 1 Bộ Quiz tổng ôn)

| Chuyên đề | Tên tài liệu | Nội dung cốt lõi |
|:---:|---|---|
| **⭐ ĐẶC BIỆT** | [00_giai_thich_cho_tre_6_tuoi_va_code_chay_tu_dau.md](file:///D:/Codin/utc-code/HK4_1/XLA/BTL/study_guide/00_giai_thich_cho_tre_6_tuoi_va_code_chay_tu_dau.md) | **Cẩm nang vỡ lòng "ELI5":** Giải thích toàn bộ luồng, bài báo chọn thuật toán ra sao, giải mã từng tham số và hướng dẫn tự code chay từ số 0 bằng NumPy. |
| **01** | [01_ban_chat_vat_ly_sar.md](file:///D:/Codin/utc-code/HK4_1/XLA/BTL/study_guide/01_ban_chat_vat_ly_sar.md) | Radar SAR là gì? Tán xạ Bragg, tại sao biển sáng mà vết dầu lại đen sì? Look-alikes từ đâu ra? |
| **02** | [02_nhieu_dom_va_loc_lee.md](file:///D:/Codin/utc-code/HK4_1/XLA/BTL/study_guide/02_nhieu_dom_va_loc_lee.md) | Bản chất nhiễu đốm Speckle (nhiễu nhân). Chứng minh toán học công thức Lee Filter từ bài toán MMSE. Worked Example 5×5. |
| **03** | [03_phan_nguong_otsu_niblack.md](file:///D:/Codin/utc-code/HK4_1/XLA/BTL/study_guide/03_phan_nguong_otsu_niblack.md) | Phân tách vùng tối: Chứng minh phương sai liên lớp Otsu. Giới hạn của Otsu và giải pháp ngưỡng thích nghi cục bộ Niblack. |
| **04** | [04_hinh_thai_hoc_nhan_lien_thong.md](file:///D:/Codin/utc-code/HK4_1/XLA/BTL/study_guide/04_hinh_thai_hoc_nhan_lien_thong.md) | Hình thái học (Erode/Dilate) và thuật toán gán nhãn liên thông 8 hướng (Run-length + Union-Find). Tại sao loại vùng < 64 px? |
| **05** | [05_toan_hoc_8_dac_trung_vung.md](file:///D:/Codin/utc-code/HK4_1/XLA/BTL/study_guide/05_toan_hoc_8_dac_trung_vung.md) | Chứng minh toán học 8 đặc trưng: Elongation (Eigenvalues), Complexity ($P^2/4\pi A$), Gradient biên, Vành tương phản nền 5px. |
| **06** | [06_hoc_may_cart_linear_svm.md](file:///D:/Codin/utc-code/HK4_1/XLA/BTL/study_guide/06_hoc_may_cart_linear_svm.md) | Học máy NumPy: Cây quyết định CART (Gini) và Linear SVM (Squared Hinge Loss + Nesterov Accelerated Gradient). |
| **07** | [07_danh_gia_f1_va_phan_bien_hoi_dong.md](file:///D:/Codin/utc-code/HK4_1/XLA/BTL/study_guide/07_danh_gia_f1_va_phan_bien_hoi_dong.md) | Đánh giá đối tượng IoU $\ge 0.5$ vs Pixel IoU. Phân tích 3 ca thất bại. 20 câu hỏi "xoáy" của Giảng viên và câu trả lời mẫu. |
| **08** | [08_tong_hop_quizz_on_tap_bao_ve.md](file:///D:/Codin/utc-code/HK4_1/XLA/BTL/study_guide/08_tong_hop_quizz_on_tap_bao_ve.md) | 25 câu hỏi trắc nghiệm kèm giải thích bẫy thi cử giúp ôn tập nhanh trước ngày bảo vệ. |
| **09** | [09_hai_tang_danh_gia_va_doi_chung_thu_vien.md](file:///D:/Codin/utc-code/HK4_1/XLA/BTL/study_guide/09_hai_tang_danh_gia_va_doi_chung_thu_vien.md) | **Triết lý Đánh giá Hai Tầng:** So sánh thi đấu giữa các thuật toán và Đối chứng toán học NumPy vs Thư viện chuẩn (SciPy, skimage, sklearn). |

---

## 🧪 Thư mục mã nguồn mini thực nghiệm (`mini_examples/`)
Các script Python cực nhỏ gọn, độc lập hoàn toàn với pipeline, có thể chạy trực tiếp bằng terminal để xem từng bước tính toán số học:
0. `demo_hai_tang_danh_gia.py`: **[ĐÁNH GIÁ 2 TẦNG]** Chạy thi đấu các bộ lọc & mô hình học máy + Đối chứng sai số 1-1 với SciPy, skimage, sklearn.
1. `code_chay_toan_bo_pipeline_tu_dau.py`: **[KHUYÊN DÙNG]** Toàn bộ pipeline 5 bước viết hoàn toàn bằng NumPy thuần trong 1 file, in ma trận trực quan ASCII.
1. `demo_01_lee_step_by_step.py`: Chạy từng bước lọc Lee trên ma trận $5\times 5$, in trọng số $W$, phương sai và kết quả.
2. `demo_02_otsu_variance.py`: Vẽ biểu đồ ASCII và in bảng tính phương sai liên lớp $\sigma_b^2$ qua từng ngưỡng.
3. `demo_03_features_geometry.py`: Tạo ma trận nhị phân vết dầu mẫu, tính và in 8 đặc trưng hình học & cường độ.
4. `demo_04_svm_gradient_step.py`: Chạy các bước lặp cập nhật trọng số SVM Nesterov, in loss và gradient giảm dần.

---

## 📌 Cách học hiệu quả nhất
1. Đọc từng chuyên đề theo thứ tự từ 01 đến 07.
2. Mỗi khi gặp công thức toán, hãy tự hỏi: *"Nếu mình là người phát minh, tại sao mình lại nghĩ ra công thức này?"*.
3. Làm các câu hỏi tự vấn (Self-Check) và bài Quiz ở cuối mỗi chuyên đề.
4. Chạy script mini tương ứng để "nhìn tận mắt" các con số nhảy múa trên màn hình terminal.
