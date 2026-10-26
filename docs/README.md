# HỆ THỐNG TÀI LIỆU DỰ ÁN (PROJECT DOCUMENTATION INDEX)
## Đề Tài 18: Phát Hiện Vết Dầu Tràn Trên Biển Từ Ảnh SAR Sentinel-1 (★★★) — NASA #6
**Học phần:** Xử lý ảnh / Computer Vision — Khoa Công nghệ Thông tin  
**Trường:** Đại học Giao thông Vận tải (UTC) | **GVHD:** TS. Phan Thanh Toàn  
**Mục tiêu ứng dụng:** Giám sát môi trường biển Việt Nam & Bờ biển miền Trung  

---

## BẢN ĐỒ CẤU TRÚC THƯ MỤC TÀI LIỆU (`docs/`)

Toàn bộ tài liệu kỹ thuật, quản lý dự án, báo cáo LaTeX, slide thuyết trình và hướng dẫn sử dụng phần mềm được phân tách thành 4 nhóm thư mục chuyên biệt:

```
docs/
├── 01_quan_ly_du_an/                  # Quản lý tiến độ, quy chuẩn Git, phân công 5 thành viên
├── 02_ly_thuyet_thuat_toan_cv/        # Cơ sở toán học, viễn thám SAR, phân biệt Class 0 vs 1
├── 03_ung_dung_web/                   # Hướng dẫn chạy Web App, cấu hình plugin thuật toán
├── 04_bao_cao_va_thuyet_trinh/        # Đề cương báo cáo LaTeX, biên dịch Overleaf, Slide & Q&A
└── README.md                          # Bản đồ tra cứu này
```

---

## 1. NHÓM 01: QUẢN LÝ DỰ ÁN & TIẾN ĐỘ CDIO (`docs/01_quan_ly_du_an/`)

| Tên tài liệu | Nội dung trọng tâm |
| :--- | :--- |
| [**`00_tong_quan_va_chi_thi_pm.md`**](01_quan_ly_du_an/00_tong_quan_va_chi_thi_pm.md) | Sứ mệnh cốt lõi của Project Manager (TV1), chiến lược đạt điểm A/A+, quy chế bảo vệ CDIO |
| [**`01_ke_hoach_3_tuan_roadmap.md`**](01_quan_ly_du_an/01_ke_hoach_3_tuan_roadmap.md) | Kế hoạch 21 ngày chi tiết theo từng ngày (Sprint 1: Nền tảng $\rightarrow$ Sprint 2: Tích hợp $\rightarrow$ Sprint 3: Báo cáo) |
| [**`02_phan_cong_5_thanh_vien.md`**](01_quan_ly_du_an/02_phan_cong_5_thanh_vien.md) | Bảng phân công nhiệm vụ cụ thể cho 5 sinh viên (TV1 đến TV5) theo chuẩn vai trò công việc |
| [**`03_git_workflow_va_quy_chuan.md`**](01_quan_ly_du_an/03_git_workflow_va_quy_chuan.md) | Quy tắc chia nhánh Git, quy chuẩn commit message Conventional Commits, kiểm duyệt PR |

---

## 2. NHÓM 02: LÝ THUYẾT & THUẬT TOÁN COMPUTER VISION (`docs/02_ly_thuyet_thuat_toan_cv/`)

| Tên tài liệu | Nội dung trọng tâm |
| :--- | :--- |
| [**`01_co_che_phan_biet_class0_class1.md`**](02_ly_thuyet_thuat_toan_cv/01_co_che_phan_biet_class0_class1.md) | **[QUAN TRỌNG]** Giải thích tại sao Class 1 detect được mà Class 0 không vẽ viền đỏ; chứng minh đây là True Negative chính xác 100%, không phải lỗi; cơ chế triệt tiêu False Alarm |
| [**`02_giao_trinh_thuat_toan_utc.md`**](02_ly_thuyet_thuat_toan_cv/02_giao_trinh_thuat_toan_utc.md) | Chi tiết công thức toán học 4 chương giáo trình TS. Phan Thanh Toàn (Lọc speckle, Otsu $\eta$, Morphology, Sobel) |
| [**`03_dac_ta_bo_du_lieu_csiro.md`**](02_ly_thuyet_thuat_toan_cv/03_dac_ta_bo_du_lieu_csiro.md) | Đặc tả 5,630 ảnh SAR Sentinel-1 (C-band, VV, IW), quy chuẩn 400x400 px, phân bố Class 0 và Class 1 |

---

## 3. NHÓM 03: ỨNG DỤNG WEB & PLUGIN HỆ THỐNG (`docs/03_ung_dung_web/`)

| Tên tài liệu | Nội dung trọng tâm |
| :--- | :--- |
| [**`01_huong_dan_chay_web.md`**](03_ung_dung_web/01_huong_dan_chay_web.md) | Hướng dẫn khởi động Web Workstation bằng 1-Click (`run_web.bat`) hoặc Terminal, các tính năng và xử lý sự cố cổng 8501 |
| [**`02_huong_dan_cam_thuat_toan_moi.md`**](03_ung_dung_web/02_huong_dan_cam_thuat_toan_moi.md) | Hướng dẫn chi tiết cách viết hàm lọc mới, ngưỡng mới, heuristic mới trong `src/custom_algorithms.py` để chạy ngay trên web |

---

## 4. NHÓM 04: BÁO CÁO LATEX & THUYẾT TRÌNH BẢO VỆ (`docs/04_bao_cao_va_thuyet_trinh/`)

| Tên tài liệu | Nội dung trọng tâm |
| :--- | :--- |
| [**`01_de_cuong_bao_cao_latex.md`**](04_bao_cao_va_thuyet_trinh/01_de_cuong_bao_cao_latex.md) | Đề cương cấu trúc báo cáo học thuật đầy đủ 5 chương (30 - 60 trang) chuẩn quy định ĐH Giao thông Vận tải |
| [**`02_kich_ban_thuyet_trinh_va_hoi_dap.md`**](04_bao_cao_va_thuyet_trinh/02_kich_ban_thuyet_trinh_va_hoi_dap.md) | Kịch bản thuyết trình bảo vệ 12 phút cho 5 thành viên, bộ câu hỏi - trả lời phản biện vấn đáp với giảng viên |
| [**`03_huong_dan_bien_dich_overleaf.md`**](04_bao_cao_va_thuyet_trinh/03_huong_dan_bien_dich_overleaf.md) | Hướng dẫn tải lên và cấu hình biên dịch XeLaTeX trên Overleaf không bị lỗi font tiếng Việt |
| [**`04_noi_dung_slide_presentation.md`**](04_bao_cao_va_thuyet_trinh/04_noi_dung_slide_presentation.md) | Toàn văn nội dung 18 trang slide thuyết trình bảo vệ đề tài |
