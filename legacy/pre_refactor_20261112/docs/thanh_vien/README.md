# Tài liệu học và bảo vệ theo thành viên

Danh sách do nhóm cung cấp ngày 11/11/2026. Tài khoản lấy từ API collaborators của chính repo `hotung9108/utc-sar-oil-detection`. GitHub xác nhận tài khoản có quyền truy cập; họ tên ứng với tài khoản do nhóm xác nhận, không suy ra từ hồ sơ công khai.

| Thành viên | Họ tên | GitHub đã xác minh | Sổ tay đầy đủ | Slide / thời gian |
| --- | --- | --- | --- | --- |
| TV1 — Trưởng nhóm | Tiến Sơn Trần | [Maloque18705](https://github.com/Maloque18705) | [Markdown](TV1_Tien_Son_Tran/TV1_Tien_Son_Tran_TAI_LIEU_HOC_VA_BAO_VE.md) · [PDF](TV1_Tien_Son_Tran/TV1_Tien_Son_Tran_TAI_LIEU_HOC_VA_BAO_VE.pdf) | 1, 2, 3, 6, 18 / 130 giây |
| TV2 | Lương Tiến Dũng | [ltdungg](https://github.com/ltdungg) | [Markdown](TV2_Luong_Tien_Dung/TV2_Luong_Tien_Dung_TAI_LIEU_HOC_VA_BAO_VE.md) · [PDF](TV2_Luong_Tien_Dung/TV2_Luong_Tien_Dung_TAI_LIEU_HOC_VA_BAO_VE.pdf) | 5, 14 / 120 giây |
| TV3 | Hồ Việt Tùng | [hotung9108](https://github.com/hotung9108) | [Markdown](TV3_Ho_Viet_Tung/TV3_Ho_Viet_Tung_TAI_LIEU_HOC_VA_BAO_VE.md) · [PDF](TV3_Ho_Viet_Tung/TV3_Ho_Viet_Tung_TAI_LIEU_HOC_VA_BAO_VE.pdf) | 7, 8, 16 / 140 giây |
| TV4 | Nguyễn Hải Hiếu | [hina-kasumi](https://github.com/hina-kasumi) | [Markdown](TV4_Nguyen_Hai_Hieu/TV4_Nguyen_Hai_Hieu_TAI_LIEU_HOC_VA_BAO_VE.md) · [PDF](TV4_Nguyen_Hai_Hieu/TV4_Nguyen_Hai_Hieu_TAI_LIEU_HOC_VA_BAO_VE.pdf) | 9–13 / 160 giây |
| TV5 | Phạm Minh Tuấn | [tuanpham21105](https://github.com/tuanpham21105) | [Markdown](TV5_Pham_Minh_Tuan/TV5_Pham_Minh_Tuan_TAI_LIEU_HOC_VA_BAO_VE.md) · [PDF](TV5_Pham_Minh_Tuan/TV5_Pham_Minh_Tuan_TAI_LIEU_HOC_VA_BAO_VE.pdf) | 4, 15, 17 / 170 giây |

Mỗi folder có **một Markdown đầy đủ và một PDF cùng nội dung**, thay cho ba đề cương ngắn trước đây. Đây là trách nhiệm học và trình bày hiện tại, không chứng nhận ai đã viết mã trong quá khứ. Tên tài khoản TV1/TV2/TV4 được sửa từ `maloque`/`itdungg`/`hinakasumi` theo danh sách collaborators; MSSV chưa được cung cấp.

Mỗi sổ tay có **10 chương**, bắt đầu từ pixel, kiểu dữ liệu, kernel, padding và histogram; sau đó giải thích phần cá nhân: **nó là gì, để làm gì, vì sao cần, tính như thế nào, khi nào có thể sai**. Có ví dụ số từng bước, phản ví dụ, bài thực hành, kịch bản trình bày và **20–25 câu hỏi ôn tập có gợi ý trả lời**, ngoài các câu hỏi nằm trong bài học. TV1 học kiến trúc và tích hợp; TV2 học kiểm chứng; TV3 học lọc và tăng cường; TV4 học biên và phân đoạn; TV5 học dữ liệu, chỉ số và thực nghiệm.

PDF có chữ tiếng Việt được nhúng font, bảng biểu, số trang, mục lục bấm được và 10 dấu trang theo chương. Markdown cùng tên là nguồn duy nhất cho nội dung PDF. Trình dựng kiểm nội dung được xuất và lưu hash nguồn/PDF trong `pdf_audit.json`. Tạo lại năm PDF bằng lệnh sau từ gốc repo:

```powershell
uv run --extra docs python scripts/build_member_pdfs.py
```

**Kết quả thuật toán:** xem [hướng dẫn đầu ra](../../results/README.md) hoặc chương 8 của bất kỳ sổ tay nào. Batch hiện có CSV cho 5.538 ảnh; PNG tự động chỉ gồm các ca minh họa, chưa có 5.538 bộ mask/trung gian.

## Tất cả thành viên phải nắm

1. Hướng dẫn BTL là mục tiêu chính; đề tài 18 cung cấp hướng dữ liệu. Đọc báo cáo chính ở `docs/report/`, không học thuộc các bản lịch sử `docs/01_...06_...` thay cho bản hiện tại.
2. Luồng ảnh: đọc xám → Lee → CLAHE → Otsu → hình thái → liên thông → lọc diện tích/tương phản. Làm nét chỉ phục vụ quan sát, không đổi mask ứng viên.
3. Đây là xử lý ảnh truyền thống: không huấn luyện, không trọng số học từ nhãn, không neural network. NumPy có thể dùng để viết ML, nên phải giải thích bằng các phép toán thực tế của dự án, không chỉ nói “dùng NumPy”.
4. Một đường biên/vùng tối không chứng minh có dầu. CLAHE khuếch đại chênh lệch nhỏ; Lee không xóa mọi nhiễu. Cần phân biệt ảnh gốc, ảnh tăng cường, biên và mask.
5. 5.538 ảnh trong repo: 3.695 Class_0, 1.843 Class_1; ít hơn bộ CSIRO công bố 92 ảnh. 10 ảnh demo là tập con, không phải kiểm thử độc lập. Không có mask chuẩn để tính IoU/Dice.
6. Kết quả toàn tập cấp ảnh: TN 810, FP 2.885, FN 204, TP 1.639; precision 36,23%, recall 88,93%. Không được gọi đây là hệ thống xác định dầu đáng tin cậy.
7. 594 ca đối chiếu gồm 558 PASS, 36 DESCRIPTIVE, 0 FAIL. DESCRIPTIVE không có nghĩa là đạt; phép ghép thư viện không phải đối chứng thuật toán độc lập hoàn toàn.

## Cách học có sản phẩm kiểm tra

| Buổi | Việc phải làm | Bằng chứng tự kiểm tra |
| --- | --- | --- |
| 1 | Cài Python 3.13, đọc README và chạy demo | Tự mở được ứng dụng; chỉ ra file nhận đầu vào và hàm xử lý |
| 2 | Đọc module cá nhân, tự làm ví dụ nhỏ | Ghi phép tính 3×3/5×5 và kiểm lại bằng hàm thật |
| 3 | Đổi đúng một tham số, giữ ảnh cố định | Lưu PNG/JSON trước–sau; giải thích tác động thay vì đoán |
| 4 | Hai người đổi phần để hỏi chéo | Mỗi người trả lời ít nhất hai câu về phần khác |
| 5 | Tập 12 phút nói + 3 phút demo + 5 phút vấn đáp | Người bấm giờ ghi thời lượng thật và câu chưa trả lời được |

Các buổi này là kế hoạch từ hiện tại, chưa được đánh dấu hoàn thành và không có ngày quá khứ giả.

## Điều phối bảo vệ

Trình chiếu theo thứ tự 1→18. Tổng thời gian phân bổ trong JSON thành viên là đúng 720 giây. TV1 mở đầu, giới thiệu từng người và quay lại slide 6/18; các thành viên tiếp lời theo slide được giao. Speaker notes trong PowerPoint và `docs/slides/KICH_BAN_BAO_VE.md` có tên và thời lượng từng slide.

Demo 180 giây: TV1 90 giây để mở ứng dụng/chọn dữ liệu/tải kết quả; TV3 30 giây giải thích Lee–CLAHE; TV4 30 giây đổi biên/hình thái; TV5 30 giây đọc chỉ số và nhắc FP. TV2 đối chiếu cấu hình đã tải với bảng kiểm chứng, sẵn sàng giải thích khi giảng viên hỏi. Mỗi người phải tự thao tác được toàn bộ demo nếu bị chỉ định.

Lệnh chung chạy từ gốc repo:

```powershell
uv sync --locked --all-extras
uv run streamlit run streamlit_app.py
uv run --extra dev python -m pytest tests -q
uv run python reproduce.py --workers 4
```

Đọc thêm [kiểm tra ML/DL](../management/KIEM_TRA_ML_DL.md), [toàn bộ dataset](../management/CHAY_TOAN_BO_DATASET.md) và [khung hồi cứu trung thực](../management/HOI_CUU_TU_10_08.md).
