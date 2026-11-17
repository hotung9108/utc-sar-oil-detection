# Mục tiêu dự án Đề 18

Chốt ngày 12/11/2026 theo yêu cầu của nhóm. Tài liệu này thay định hướng cũ “không ML/DL”.

**Cập nhật 17/11/2026:** đã hoàn thiện luồng phần mềm với Streamlit, 12 notebook và
thực nghiệm bổ sung Cantarell/QPOSD. **Chưa đủ căn cứ xác nhận đạt 100% Đề 18**;
xem [đối chiếu hiện tại](DANH_GIA_DU_AN_VA_DOI_CHIEU_DE_18.md). Các mốc kế hoạch
12–15/11 dưới đây là lịch sử, không phải xác nhận đã đủ mọi yêu cầu.
Theo yêu cầu mới, không làm thêm video, slide hoặc báo cáo Word/PDF.

## Bài toán

Phát hiện vết dầu tràn trên biển từ ảnh SAR — Đề 18, liên hệ NASA #6 trong tài liệu môn học. Bối cảnh ứng dụng là phát hiện sớm ngoài khơi để hỗ trợ giảm ảnh hưởng tới du lịch và ngư nghiệp miền Trung Việt Nam. Dữ liệu và bằng chứng phải quyết định phương pháp được sử dụng.

## Yêu cầu bắt buộc

1. Lọc speckle, chuẩn hóa theo góc tới và phân ngưỡng thích nghi để tìm vùng tối ứng viên.
2. Trích đặc trưng từng vùng: độ thuôn dài, độ phức tạp biên, gradient biên và tương phản với nền.
3. Phân lớp dầu và tương tự dầu bằng CART/SVM. Cả CART và SVM phải có bản tự cài bằng NumPy để khảo sát; thư viện dùng làm đối chứng.

## Trình tự nghiên cứu

- Tìm dữ liệu có nhãn và kiểm chứng nguồn trước: giấy phép, loại nhãn, chất lượng gán nhãn, ảnh–nhãn khớp nhau, mã cảnh, góc tới, thời gian và gió nếu có.
- Lưu manifest và chia train/validation/test độc lập theo cảnh hoặc sự kiện khi metadata cho phép. Công bố giới hạn nếu không chứng minh được độc lập.
- Thực nghiệm các phương án trên cùng dữ liệu và giao thức. Chọn thuật toán/tham số trên validation; không chọn theo test.
- Hai lớp so sánh bắt buộc: giữa các thuật toán và giữa bản tự cài với hàm thư viện tương ứng. Ghi công thức/biến thể, tham số, sai số, thời gian và giải thích khác biệt. Không coi đối chứng ghép lại cùng công thức là thư viện độc lập.
- Chỉ dùng số liệu thực sự chạy được, có seed, cấu hình, phiên bản mã và checksum dữ liệu. Các bảng phải tái tạo bằng một lệnh sau khi pipeline được triển khai.

## Đánh giá và cải tiến

Precision, Recall, F1 mức đối tượng trên test; tỷ lệ nhầm dầu/look-alike và phân tích FP/FN. Giao thức ghép đối tượng và ngưỡng IoU phải được chốt trước khi đánh giá. Nhãn cấp ảnh không thay thế mask/nhãn đối tượng; bounding box không đại diện diện tích dầu thực.

Cải tiến nhóm tập trung giảm báo nhầm bằng nền cục bộ và đặc trưng vùng; có thể bổ sung gió khi metadata hợp lệ. Cần ablation trên cùng split, báo cả thay đổi recall và thời gian. Chưa tuyên bố cải tiến có hiệu quả trước khi có kết quả.

Phân biệt ảnh sigma0 tuyến tính, dB và ảnh hiển thị. Không suy góc tới từ JPEG. Không dùng PSNR/SSIM của SAR thực khi chưa có ảnh sạch tham chiếu hợp lệ.

## NASA và giới hạn phạm vi

Tìm hiểu mục đích nghiên cứu/ứng phó dầu tràn của NASA bằng nguồn chính thức, phân biệt ảnh NASA và nhãn do nhóm khác tạo. Các yêu cầu cụ thể của Đề 18 lấy từ tài liệu môn học, không tự gán thành nguyên văn yêu cầu NASA. Xem [danh mục nguồn](NGUON_DU_LIEU_SAR_DAU_TRAN.md).

AIS truy nguồn tàu và mô phỏng trôi dầu là hướng phát triển sau. Ngày 13/11/2026 nhóm chọn **Refined Deep-SAR Oil Spill — SOS** làm dữ liệu chính cho thực nghiệm xử lý ảnh. Đã kiểm kê 8070 cặp ảnh/mask; Sentinel là tập chính, PALSAR đánh giá ngoài miền. Xem `management/KIEM_TRA_REFINED_SOS.md`.

## Phạm vi triển khai đã chốt

Thực hiện pipeline NumPy và bản thư viện, CLI và 5 notebook Jupyter theo thành viên; chạy số liệu thật trước khi quyết định thuật toán. So sánh 110 cấu hình lọc/ngưỡng, rồi 729 cấu hình hình thái/đặc trưng/classifier trên validation. Chọn bản NumPy đã kiểm chứng và hội tụ; giữ nguyên test cuối. Chi tiết tại [giao thức](GIAO_THUC_THUC_NGHIEM.md) và [phân công](management/KE_HOACH_SOS_NOTEBOOK.md).

SOS thiếu metadata góc tới, gió và nhãn look-alike; riêng nhánh SOS chỉ đo dầu/nền trên PNG. Đã bổ sung Cantarell cho dữ liệu vật lý/góc tới/gió và QPOSD cho dầu/look-alike chung, nhưng chưa kiểm chứng tất cả trên một pipeline Sentinel-1. **Chưa hoàn tất toàn bộ minh chứng của Đề 18**. Không suy góc tới từ PNG, không giả lập gió và không gọi nền là từng loại gió yếu/màng sinh học/mưa.

Đầu ra cuối gồm mask, overlay, đặc trưng/điểm từng vùng, Precision/Recall/F1 đối tượng, pixel IoU/Dice, FP/ảnh, ablation và phân tích lỗi. Mục tiêu cải tiến là giảm báo nhầm bằng vùng nền cục bộ và phân lớp vùng; chỉ kết luận có cải thiện khi số liệu test xác nhận, kể cả khi kết quả kém. Hạn bàn giao: 23:59 ngày 15/11/2026, Asia/Saigon.
