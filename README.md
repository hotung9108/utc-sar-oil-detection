# BÀI TẬP LỚN XỬ LÝ ẢNH (DIP) — KHOA CNTT, UTC

## ĐỀ TÀI: TĂNG CƯỜNG ĐỘ TƯƠNG PHẢN, KHỬ NHIỄU & XỬ LÝ BIÊN BỘC LỘ VẾT DẦU TRÀN TRÊN BIỂN TỪ ẢNH RADAR SAR SENTINEL-1

[![Pure NumPy Core](https://img.shields.io/badge/Algorithm-100%25_Pure_NumPy-blue.svg)](file:///D:/Codin/utc-code/HK4_1/XLA/BTL/src/)
[![No ML / No DL](https://img.shields.io/badge/Academic-Classical_DIP_(No_ML%2FDL)-emerald.svg)](file:///D:/Codin/utc-code/HK4_1/XLA/BTL/docs/01_TONG_QUAN_DE_TAI.md)
[![NASA Topic 18](https://img.shields.io/badge/NASA-Topic_18_SAR_Oil_Spill-orange.svg)](file:///D:/Codin/utc-code/HK4_1/XLA/BTL/docs/01_TONG_QUAN_DE_TAI.md)
[![Verification](https://img.shields.io/badge/Hand_Calculations-Zero_Error_(5%2F5)-success.svg)](file:///D:/Codin/utc-code/HK4_1/XLA/BTL/src/verification.py)
[![Full Scan](https://img.shields.io/badge/Full_Scan-1%2C853_Images_(58.8s)-purple.svg)](file:///D:/Codin/utc-code/HK4_1/XLA/BTL/results/edge_evaluation_output/)

- **Học phần**: Xử lý ảnh (Digital Image Processing - DIP)
- **Khoa**: Công nghệ Thông tin — Trường Đại học Giao thông Vận tải (UTC)
- **Giảng viên hướng dẫn**: TS. Phan Thanh Toàn, TS. Cao Thị Luyên
- **Ánh xạ đề tài**: **Nhóm A (Tăng cường & Lọc ảnh)** kết hợp **Đề 5 (Làm nét & Phát hiện biên)** và **Đề 18 NASA (Phát hiện vết dầu loang trên ảnh SAR vi ba)**.
- **Cam kết học thuật**: **100% Xử lý ảnh số kinh điển thuần túy (NO Machine Learning / NO Deep Learning)**. Toàn bộ thuật toán được tự cài đặt từ đầu bằng Pure NumPy và đối chứng kiểm chuẩn khoa học với 5 bài toán tính tay mẫu $8 \times 8$ (sai số $= 0$) và thư viện OpenCV.

---

## 📚 MỤC LỤC BỘ TÀI LIỆU TOÀN DIỆN (FULL DOCUMENTATION)

Hệ thống tài liệu đầy đủ phục vụ viết báo cáo BTL (file Word), slide thuyết trình và bảo vệ vấn đáp trước hội đồng:

| Chương / Tài liệu | Tên tài liệu & Đường dẫn | Nội dung trọng tâm |
| :---: | :--- | :--- |
| **Chương 1** | 📖 [01_TONG_QUAN_DE_TAI.md](file:///D:/Codin/utc-code/HK4_1/XLA/BTL/docs/01_TONG_QUAN_DE_TAI.md) | Thảm họa dầu tràn, cơ sở vật lý radar SAR băng C Sentinel-1, tán xạ Bragg, hiện tượng dập sóng mao dẫn và mô hình nhiễu đốm nhân Multiplicative Speckle Noise. |
| **Chương 2** | 📐 [02_CO_SO_LY_THUYET_TOAN_HOC.md](file:///D:/Codin/utc-code/HK4_1/XLA/BTL/docs/02_CO_SO_LY_THUYET_TOAN_HOC.md) | Đầy đủ công thức giải tích toán học rời rạc, ma trận nhân chập và nguyên lý của **21 thuật toán DIP**: Log, Global HE, CLAHE, Box, Gauss, Median, Bilateral, Lee MMSE, Frost, Kuan, Homomorphic, Unsharp, Laplacian, Roberts, Prewitt, Sobel, LoG, Canny 4 bước, Otsu $\eta$, Co/Giãn/Mở/Đóng, Ranh giới $\beta(A)$ và lọc NASA $C_R \ge 0.10$. |
| **Chương 3** | 🏛️ [03_KIEN_TRUC_HE_THONG_VA_CAI_DAT.md](file:///D:/Codin/utc-code/HK4_1/XLA/BTL/docs/03_KIEN_TRUC_HE_THONG_VA_CAI_DAT.md) | Kiến trúc phân tầng (Layered Architecture), module hóa Pure NumPy, quy trình xử lý Decoupled 4 bước Z-Pattern, thiết kế Web Studio FastAPI + TailwindCSS tối giản, Lightbox modal. |
| **Chương 4** | 📊 [04_KET_QUA_THUC_NGHIEM_VA_DANH_GIA.md](file:///D:/Codin/utc-code/HK4_1/XLA/BTL/docs/04_KET_QUA_THUC_NGHIEM_VA_DANH_GIA.md) | **5 bài toán tính tay $8 \times 8$ giải tích sai số $= 0$**, bảng kiểm chuẩn OpenCV ($\text{MSE} = 0.000$), kết quả 5 thử nghiệm định lượng khoa học và **báo cáo quét FULL 100% dataset (1.853 ảnh SAR)**. |
| **Chương 5** | 🚀 [05_HUONG_DAN_CAI_DAT_VA_SU_DUNG.md](file:///D:/Codin/utc-code/HK4_1/XLA/BTL/docs/05_HUONG_DAN_CAI_DAT_VA_SU_DUNG.md) | Hướng dẫn cài đặt môi trường, chạy Web Studio thời gian thực, chạy kiểm thử verification, chạy 5 thực nghiệm và chạy benchmark toàn bộ dataset. |
| **Phụ lục** | 🎓 [06_BO_CAU_HOI_PHAN_BIEN_BAO_VE_BTL.md](file:///D:/Codin/utc-code/HK4_1/XLA/BTL/docs/06_BO_CAU_HOI_PHAN_BIEN_BAO_VE_BTL.md) | **Cẩm nang 20 câu hỏi - đáp phản biện kinh điển** của các thầy cô UTC (TS. Phan Thanh Toàn, TS. Cao Thị Luyên) khi chấm bảo vệ BTL, kèm **Kịch bản thuyết trình bảo vệ trong 10 phút**. |
| **Tra cứu** | 📑 [THUAT_TOAN_SU_DUNG.md](file:///D:/Codin/utc-code/HK4_1/XLA/BTL/docs/THUAT_TOAN_SU_DUNG.md) | Bảng tra cứu đối chiếu nhanh từng hàm Python với số trang slide bài giảng UTC. |

---

## 📌 CẤU TRÚC THƯ MỤC DỰ ÁN

```
D:\Codin\utc-code\HK4_1\XLA\BTL\
├── app.py                              # Web Application Server (FastAPI REST API)
├── evaluate_all_edges.py               # Benchmark runner quét FULL 100% dataset (1.853 ảnh)
├── run_experiments.py                  # Script thực thi chuỗi 5 thử nghiệm khoa học
├── run_app.bat                         # File nhấp đúp khởi chạy server & mở trình duyệt
├── requirements.txt                    # Danh sách thư viện phụ thuộc tối thiểu
│
├── src/                                # THƯ VIỆN THUẬT TOÁN PURE NUMPY CORE (100% tự lập trình)
│   ├── filters.py                      # 9 bộ lọc đốm và không gian (Lee, Bilateral, Frost, Kuan, Box, ...)
│   ├── enhancement.py                  # Log Transform, Global HE, CLAHE cắt ngưỡng & nội suy song tuyến
│   ├── sharpening.py                   # Unsharp Masking, High-Boost, Laplacian, Sobel sharpening
│   ├── edges.py                        # Roberts, Prewitt, Sobel, LoG dò điểm qua 0, Canny 4 bước, Overlay
│   ├── morphology.py                   # Otsu, Co, Giãn, Mở, Đóng, Ranh giới beta(A), Lọc NASA Area & CR
│   ├── metrics.py                      # 6 chỉ số định lượng: ENL, SSI, RMS Contrast, Entropy, AMBE, EPI
│   ├── utils.py                        # Đọc/ghi ảnh, Difference Map, cắt lát ngang Profile Slice
│   └── verification.py                 # Bộ kiểm chuẩn 5 ví dụ số tính tay 8x8 & đối chuẩn OpenCV
│
├── static/                             # GIAO DIỆN WEB STUDIO MINIMALISM
│   ├── index.html                      # Lưới 2x2 tầm nhìn lớn, Modal Lightbox, Bảng NASA đơn sắc lớn
│   ├── css/style.css                   # Custom styles, range slider, animation
│   └── js/app.js                       # Tương tác Client: Fetch API, Chart.js, zoom modal
│
├── data/sample/                        # Bộ 10 ảnh SAR thử nghiệm chuẩn (5 Oil Slicks, 5 Sea Surface)
├── kaggle/data/Class_1/                # 1.843 ảnh SAR vết dầu thực tế Sentinel-1
│
├── results/                            # KẾT QUẢ ĐỊNH LƯỢNG KHOA HỌC
│   ├── tables/                         # Bảng dữ liệu CSV các thử nghiệm định lượng 1..5
│   ├── figures/                        # Đồ thị và biểu đồ trực quan hóa (.png)
│   └── edge_evaluation_output/         # Báo cáo quét 100% dataset: CSV & 732 ảnh chẩn đoán 4 khung hình
│
└── docs/                               # HỆ THỐNG TÀI LIỆU HỌC THUẬT TOÀN DIỆN (7 CHUYÊN ĐỀ)
```

---

## 🚀 HƯỚNG DẪN KHỞI CHẠY NHANH

### Cách 1: Khởi động tức thì bằng một cú nhấp đúp (Windows)
Nhấp đúp vào tệp:
```cmd
run_app.bat
```
Server sẽ tự động kích hoạt và mở trình duyệt tại: `http://127.0.0.1:8000`

### Cách 2: Khởi động bằng dòng lệnh Terminal
```powershell
# 1. Cài đặt thư viện
pip install -r requirements.txt

# 2. Khởi chạy server
python app.py
```

### Các lệnh kiểm thử & thực nghiệm quan trọng:
```powershell
# Kiểm tra đối chứng 5 bài toán tính tay 8x8 (Sai số = 0) & OpenCV:
python -m src.verification

# Chạy toàn bộ chuỗi 5 thử nghiệm khoa học (Xuất CSV và biểu đồ PNG):
python run_experiments.py

# Quét benchmark tự động 100% dataset (1.853 ảnh trong ~60 giây):
python evaluate_all_edges.py
```

---

## 🌟 ĐẶC TRƯNG NỔI BẬT CỦA HỆ THỐNG

1. **Chuỗi xử lý Decoupled 4 bước Z-Pattern**:
   - `1. Ảnh SAR Gốc` $\rightarrow$ `2. Sau Khử Đốm & Tăng Cường (Lee + CLAHE)` $\rightarrow$ `3. Bộc Lộ Ranh Giới Vết Dầu (beta(A) viền đỏ)` $\rightarrow$ `4. Bản Đồ Vi Sai Tác Động (|Diff| x 2)`.
   - Thuật toán phân đoạn chạy trên ảnh trước khi làm nét, triệt tiêu $100\%$ hiện tượng Undershoot thâm hụt biên ở thung lũng sóng biển.
2. **Giải pháp Ranh giới Hình thái học $\beta(A)$ vượt trội**:
   - Triệt tiêu hoàn toàn nhược điểm "vẽ viền lung tung khắp mặt biển" của Canny/Sobel, bộc lộ đường bao khép kín đúng 1 pixel ôm sát mảng dầu thật.
   - Lọc sạch vùng biển lặng giả mạo (Look-alike) bằng tiêu chuẩn NASA: $\text{Area} \ge 300\text{ px}$ và $C_R \ge 0.10$.
3. **Kiểm chuẩn học thuật tuyệt đối**:
   - 5 bài toán tính tay $8 \times 8$ giải tích khớp từng bước với slide UTC.
   - Quét thực tế trên **1.853 ảnh** đạt tỷ lệ sạch chuẩn **$60.5\%$ (1.121 ảnh)**, xuất 732 ảnh chẩn đoán 4 khung hình phục vụ tối ưu hóa thuật toán.
