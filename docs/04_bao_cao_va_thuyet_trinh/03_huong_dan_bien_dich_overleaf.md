# HƯỚNG DẪN BIÊN DỊCH BÁO CÁO LATEX KHÔNG LỖI FONT CHỮ
**Học phần:** Xử lý ảnh (TS. Phan Thanh Toàn — ĐH Giao thông Vận tải)  
**Đề tài 18:** Phát hiện vết dầu tràn trên biển từ ảnh SAR Sentinel-1

---

## 1. NGUYÊN NHÂN GÂY LỖI FONT TIẾNG VIỆT TRONG LATEX VÀ CÁCH ĐÃ KHẮC PHỤC

Trước đây, khi biên dịch tiếng Việt trong LaTeX thường gặp các lỗi:
1. **Thiếu gói mã hóa phông chữ `\usepackage[T5]{fontenc}`**:
   - Trình biên dịch **pdfLaTeX** mặc định dùng bảng mã `OT1` (chỉ có 128 ký tự tiếng Anh cơ bản). Khi gặp các nguyên âm tiếng Việt có dấu (`ạ, ả, ã, ơ, ư, ề, ổ, đ...`), pdfLaTeX báo lỗi:
     `Font OT1/cmr/m/n/12 does not contain glyph...` hoặc `Missing character: There is no ... in font cmr12!`. Kết quả là các chữ tiếng Việt bị mất dấu, rỗng chữ hoặc biến thành ô vuông.
   - **Đã khắc phục**: Bổ sung `\usepackage[T5]{fontenc}` và `\usepackage{mathptmx}` (Times New Roman chuẩn quy định Luận văn tốt nghiệp UTC).
2. **Xung đột giữa các trình biên dịch (pdfLaTeX vs XeLaTeX/LuaLaTeX)**:
   - Nếu đổi trình biên dịch sang XeLaTeX trên Overleaf, gói `inputenc` và `T5 fontenc` sẽ xung đột vì XeLaTeX dùng bộ phông Unicode `fontspec`.
   - **Đã khắc phục**: Sử dụng khối điều kiện `\usepackage{iftex}` trong `main.tex`. Dự án giờ đây **tự động thích ứng 100%** cho dù bạn chọn biên dịch bằng **pdfLaTeX**, **XeLaTeX** hay **LuaLaTeX**!
3. **Các ký tự Unicode dấu câu đặc biệt (gạch ngang dài `—`, ngoặc kép `“ ”`, dấu ba chấm `…`)**:
   - Khi copy-paste từ Word vào LaTeX, các dấu này làm `inputenc` báo lỗi:
     `! Package inputenc Error: Unicode character ... not set up for use with LaTeX`.
   - **Đã khắc phục**: Tích hợp gói `newunicodechar` tự động ánh xạ mọi ký tự đặc biệt sang lệnh chuẩn LaTeX.
4. **Tiêu đề tiếng Việt trong khối mã nguồn `listings`**:
   - Đã cấu hình `inputencoding=utf8`, `extendedchars=true` và bọc tiêu đề an toàn bằng dấu ngoặc kép đôi `caption={{...}}`.

---

## 2. HƯỚNG DẪN BIÊN DỊCH TRÊN OVERLEAF (KHUYÊN DÙNG)

1. Nén toàn bộ thư mục `report_latex/` thành tệp `report_latex.zip`.
2. Truy cập [Overleaf](https://www.overleaf.com), bấm **New Project** -> **Upload Project** -> Tải tệp `report_latex.zip` lên.
3. Kiểm tra cài đặt trình biên dịch (**Menu** ở góc trên cùng bên trái):
   - **Compiler**: Chọn **pdfLaTeX** (mặc định) HOẶC **XeLaTeX** (cả 2 đều chạy mượt 100%).
   - **TeX Live version**: Chọn **2023** hoặc **2024** (mới nhất).
   - **Main document**: Chọn `main.tex`.
4. Bấm **Recompile** (Ctrl + Enter) -> PDF sẽ xuất ra hoàn hảo, sắc nét, đúng chuẩn phông chữ Times New Roman và không còn bất kỳ lỗi font tiếng Việt nào!

---

## 3. HƯỚNG DẪN BIÊN DỊCH TRÊN MÁY TÍNH CÁ NHÂN (OFFLINE)

Nếu máy tính của bạn đã cài đặt TeX Live hoặc MiKTeX:

### Cách 1: Sử dụng giao diện TeXStudio / VS Code
- Mở tệp `report_latex/main.tex`.
- Bấm nút **Build & View** (phím tắt `F5` trên TeXStudio).

### Cách 2: Sử dụng dòng lệnh Terminal
```bash
cd report_latex

# Biên dịch bằng pdfLaTeX (chạy 2 lần để cập nhật mục lục và số trang):
pdflatex -interaction=nonstopmode main.tex
bibtex main
pdflatex -interaction=nonstopmode main.tex
pdflatex -interaction=nonstopmode main.tex

# HOẶC biên dịch bằng xelatex:
xelatex -interaction=nonstopmode main.tex
bibtex main
xelatex -interaction=nonstopmode main.tex
```

File kết quả sẽ là `main.pdf` với đầy đủ 5 chương, bìa luận văn UTC, bảng mục lục tự động, danh mục hình vẽ/bảng biểu và danh mục tài liệu tham khảo chuẩn IEEE.
