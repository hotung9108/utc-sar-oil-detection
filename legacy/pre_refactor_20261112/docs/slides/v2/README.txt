BỘ THUYẾT TRÌNH BẢO VỆ V2

Đã bổ sung ảnh minh họa vào các slide 2, 4, 5, 7–13, 16 và 17;
slide 14 có ma trận số để giải thích ví dụ Lee. Hình so sánh dùng cùng
mẫu và cùng vùng cắt để người xem theo dõi tác động của từng bước.
Các PNG nằm trong illustrations/ và đã nhúng trực tiếp vào PowerPoint.
illustrations/README.txt hướng dẫn chỉ vào hình khi trình bày;
illustrations/manifest.json ghi nguồn, cấu hình, vùng cắt và số đo.
Script build_defense_deck_v2.py gọi illustrate_defense_deck_v2.py để
lấy ảnh thật từ lần chạy pipeline. Speaker notes đầy đủ vẫn được giữ.

BAO_VE_BTL_XLA_V2.pptx: 18 slide PowerPoint có thể chỉnh sửa.
Notes của mỗi slide là một đoạn lời nói đầy đủ, liền mạch và tự nhiên,
có giải thích cho người mới, ví dụ và chuyển lời, không chia mục hướng dẫn.
loi_noi_lien_mach.json: nguồn lời nói dùng để dựng Notes trong PowerPoint.
SPEAKER_NOTES_DAY_DU.txt: bản văn bản đầy đủ trích từ Notes của 18 slide.
giai_thich_speaker_notes.json: tài liệu giải thích và câu hỏi để học thêm.
Nguồn đối chiếu và phân vai được giữ trong loi_thuyet_trinh.json.
Bản Notes đầy đủ có khoảng 6.016 từ tách bằng khoảng trắng; ước tính đọc
27–34 phút ở tốc độ 180–220 từ/phút, chưa tính dừng và demo. Cần diễn tập
để đo thời lượng thực tế. Bản này không còn là lời đọc giới hạn 12 phút.
Notes đã được phản biện với utc_sar_oil_spill_detection_presentation.md
và đối chiếu lại mã. Chi tiết lựa chọn: PHAN_BIEN_VA_LUA_CHON_NOTES.txt.
Trong PowerPoint: View > Normal, bật Notes phía dưới rồi kéo khung Notes lên
để đọc. Khi trình chiếu, bật Presenter View để xem ghi chú trên màn hình riêng.
Kịch bản demo riêng nằm trong KICH_BAN_THUYET_TRINH_V2.pdf.
Bật Presenter View để xem Notes khi nói.
BAO_VE_BTL_XLA_V2.pdf: bản slide xuất bằng Microsoft PowerPoint, 18 trang.

KICH_BAN_THUYET_TRINH_V2.pdf: kịch bản NGẮN 12 phút, 25 trang,
giữ để nhóm chọn khi cần đáp ứng thời lượng bảo vệ; không phải Notes dài mới.
KICH_BAN_THUYET_TRINH_V2.txt: cùng nội dung ở dạng văn bản dễ sửa.
loi_thuyet_trinh.json: nội dung nguồn, 18 slide, phân vai, lời đọc,
chuyển lời, nguồn số liệu, demo và 13 câu hỏi ôn tập.

Thời lượng mục tiêu: 720 giây trình bày, 180 giây demo.
Đây là phân bổ diễn tập, chưa đo thời gian bằng giọng đọc thực tế.
Kịch bản khớp số thứ tự 18 slide của BAO_VE_BTL_XLA_V2.pptx.
Không thay đổi các file PowerPoint/PDF cũ.

Dựng lại kịch bản từ thư mục gốc:
  .venv\Scripts\python -X utf8 scripts/build_defense_script_v2.py
  .venv\Scripts\python -X utf8 scripts/build_defense_deck_v2.py
  powershell -NoProfile -File scripts/export_slides_v2.ps1 -Preview

Nguồn bảng và biểu đồ: kết quả thực nghiệm hiện có trong results/reproducible/.
Bảng kiểm chứng: results/verification/per_case.csv.
Thuật toán và giới hạn: report_overleaf/v2/main.tex, src/tv1/ đến src/tv5/.
Bảng trên slide 15 trích ba phương án trong tám phương án khảo sát.
Biểu đồ trên slide 15 biểu diễn trung bình trên 10 ảnh, không có thanh độ lệch chuẩn.
Số liệu cấp ảnh trên slide 17 không phải chất lượng mask theo pixel.

Đã kiểm tra kịch bản: tổng thời gian, đủ 18 mục, nguồn số liệu confusion.json,
phân vai theo thanh_vien.json; PDF được render để rà soát font và ngắt trang.
PowerPoint đã xuất đủ 18 slide, 18 Notes khớp loi_noi_lien_mach.json; các slide được kiểm tra
qua ảnh render, không còn ô chữ tràn theo phép kiểm tra của PowerPoint.
Các phần demo/vấn đáp giữ tiêu đề cùng nội dung, không có trang chỉ chứa
một câu tiếp từ trang trước.
