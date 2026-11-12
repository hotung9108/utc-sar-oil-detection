BẢN BÁO CÁO V2 — XLA-BTL

BAO_CAO_BTL_XLA.pdf: bản PDF để đọc và rà soát trước khi nộp.
main.tex: nguồn LaTeX của báo cáo v2; toàn bộ hình nằm trong assets/.
front_matter.pdf: bốn trang đầu từ v1 mới, với bảng phân công trang 3 đã sửa.
front_matter.tex: nguồn có thể sửa của bốn trang đầu; cột nhiệm vụ đã được mở rộng.
main.tex chèn front_matter.pdf rồi tiếp tục phần nội dung từ trang 5.
report_content.json: nội dung có cấu trúc; bốn trang đầu tham chiếu front_matter.pdf.
evidence/: CSV, JSON và checksum của các phép đo đã dùng; không phải dữ liệu được tự tạo để minh họa.
verify_example.py và example_result.json: mã và kết quả kiểm chứng Lee/HE.
requirements.txt: phụ thuộc chạy ứng dụng từ gốc repository.

Ví dụ kiểm chứng: tại gốc repo chạy
  .venv\Scripts\python -X utf8 report_overleaf/v2/verify_example.py
Ứng dụng:
  .venv\Scripts\python -m streamlit run streamlit_app.py
Kết quả thuật toán: results/reproducible/ và results/verification/.

Nguồn LaTeX hỗ trợ pdfLaTeX (T5/Times) hoặc XeLaTeX (Times New Roman).
Từ thư mục v2, chạy xelatex main.tex hai lần để dựng báo cáo.
Nếu sửa bốn trang đầu, chạy xelatex front_matter.tex hai lần trước,
sau đó chạy xelatex main.tex. Không dùng scripts/build_report.py để dựng bản v2 này.
Để sửa trên Overleaf, mở v2/main.tex. Không thay nội dung main.tex ở gốc.
MCP olcli 0.16.2 hiện không chọn đúng tài liệu qua resource_path trong dự án này;
không coi kết quả biên dịch báo cáo gốc là kết quả kiểm tra v2.

Những điểm cần nhóm hoàn thiện:
- Xác nhận tỷ lệ đóng góp, chữ ký, ngày họp và minh chứng thực tế.
- Bốn trang đầu giữ nội dung của v1 theo yêu cầu, gồm phân công và tỷ lệ 20%;
  đây không phải số liệu đóng góp đã được kiểm chứng. Nhóm xác nhận trước khi ký.
- Danh mục ký hiệu từ v1 giữ nguyên; định nghĩa C_R trong nội dung v2 mới là
  tương phản vùng/nền. Nhóm cần thống nhất nội dung này trước khi nộp.
- Báo cáo dưới 30 trang theo yêu cầu riêng, khác mức 30–60 trang của hướng dẫn.
- Khảo sát phương pháp/tham số trên 10 ảnh; chỉ đánh giá cấu hình mặc định
  trên toàn bộ 5.538 ảnh duy nhất. Chưa có mask chuẩn và chưa có đánh giá theo cảnh độc lập.
- Chưa chứng nhận giới hạn cứng thời gian/RAM; không khẳng định vùng tối là dầu.
- Video, slide, bảng đánh giá chéo là các sản phẩm riêng cần kiểm tra trước nộp.

Các file gốc ngoài v2 được giữ nguyên. Tệp chính của dự án Overleaf không bị đổi.
