> **Snapshot trước đợt cập nhật:** xem [KIEM_TRA_HIEN_TAI.md](KIEM_TRA_HIEN_TAI.md) và sheet `Cap_nhat_20261111` trong Excel cho hiện trạng mới. Giữ bản này làm dấu vết kiểm tra, không thay thế kết quả nghiệm thu hiện tại.

# Đối chiếu yêu cầu BTL và kế hoạch hoàn thiện

**Ngày lập:** 11/11/2026. **Phiên bản kiểm tra:** `22f28a68b2f28b885b95834d13d96f2cd213fb2b` trên `main`.

**Kết luận: có nền tảng mã nguồn và báo cáo, nhưng chưa đủ bằng chứng đáp ứng toàn bộ yêu cầu nộp bài.** Đây là kiểm tra trong phạm vi dự án, không phải kết quả chấm điểm hay chứng nhận của giảng viên.

## 1. Phạm vi và tài liệu chuẩn

- Yêu cầu chính: [Danh sách BTL XLA và hướng dẫn](<../../docs/00_tai_lieu_goc/huong_dan_btl_docx/ds btl xla VÀ HƯỚNG DẪN.docx>).
- Theo xác nhận của người dùng: đề kết hợp tăng cường/lọc/biên trên SAR; không ML/DL. Đề 18 NASA chỉ định hướng dataset. Không mặc định phải làm toàn bộ các đề 1, 2, 5 riêng lẻ; cần giữ xác nhận phạm vi đã được giảng viên duyệt.
- Dùng TV1–TV5 tạm thời. Không gán danh tính Git, phần trăm đóng góp, chữ ký hoặc thành tích cho người chưa được xác minh.
- Có điểm cần hỏi giảng viên: quy định chung ghi thực hiện trong **3 tuần**, quy định mã nguồn yêu cầu Git trải đều **8 tuần**. Không tự bỏ một trong hai yêu cầu.
- Cũng cần xác nhận FastAPI web demo được chấp nhận thay các framework được liệt kê trong hướng dẫn.

## 2. Những phát hiện cần ưu tiên

1. **Bản báo cáo bàn giao chưa thống nhất.** [PDF cục bộ](../../report_overleaf/BTL_XLA_BaoCao.pdf) có 48 trang; 5 chương ở trang PDF 10–41, tổng 32 trang. Bản này nằm trong thư mục bị ignore. [Nguồn đang trên GitHub](../../docs/report/main.tex) mới là khung. Sổ tay 13 trang không thay thế báo cáo chính.
2. **Phân bổ chương chưa đạt:** chương 3 ở trang PDF 24–29, chương 4 ở 30–38: 15/32 = 46,875%, chưa hơn một nửa nội dung chính. Cần bổ sung nội dung thực chất, không tăng trang bằng khoảng trống.
3. **Công thức không khớp code:** báo cáo dùng `C_R = 4πA/P²` (độ tròn); code dùng `(μ_biển − μ_vùng)/μ_biển` (tương phản). Ngưỡng và pipeline trong báo cáo cũng cần cập nhật.
4. **Bảng kiểm chứng sai:** chạy `python -B -X utf8 -m src.verification` ở bước kiểm tra trước đó cho Median 99,17%, Erosion 99,30%, Gaussian MSE 0,0060. Không thể ghi mọi sai số bằng 0. Chương trình in kết luận 100% vô điều kiện không thay thế kiểm thử có tiêu chí chấp nhận.
5. **Đánh giá còn quá mức:** `CLEAN_BOUNDARY` là heuristic, không phải accuracy với mask chuẩn. Script chỉ đánh giá Class_1 và ảnh mẫu; lần so sánh trước đó vẫn báo dầu ở 4/5 ảnh biển. Đây là kết quả kiểm tra mẫu, không suy rộng thành tỷ lệ lỗi toàn dataset.
6. **Hồ sơ chưa hoàn chỉnh:** chưa tìm thấy slide/video/đánh giá chéo thực tế trong dự án; danh tính nhóm và tỷ lệ đóng góp còn chỗ trống hoặc chưa xác minh. Khai báo AI cần bổ sung các hoạt động hỗ trợ Codex đã thực hiện.
7. **Hình thức và nguồn:** báo cáo dùng 12 pt thay vì 13 pt. Có 12 mục BibTeX, 10 khóa được trích và 9 trường DOI; chưa xác minh nguồn/DOI bên ngoài dự án. Không coi số lượng này là bằng chứng mọi trích dẫn đều đúng.

## 3. Ma trận yêu cầu

Mức “Đạt trong phạm vi kiểm tra” chỉ áp dụng cho tiêu chí của dòng đó. “Chưa tìm thấy” không có nghĩa sản phẩm không tồn tại bên ngoài dự án.

| Mã | Yêu cầu | Mức đáp ứng | Hiện trạng | Việc cần làm | Phụ trách / ưu tiên | Minh chứng |
| --- | --- | --- | --- | --- | --- | --- |
| YC01 | Đề kết hợp SAR; thuật toán xử lý ảnh, không ML/DL | Đạt trong phạm vi kiểm tra | Người dùng xác nhận đề kết hợp. README và pipeline không dùng ML/DL. Chưa đính kèm văn bản duyệt đề. | Lưu phạm vi đã thống nhất và xác nhận của giảng viên nếu có. | TV1 / P1 | [Mở minh chứng](<../../README.md>) |
| YC02 | Thuật toán cốt lõi tự cài bằng NumPy; thư viện để đối chiếu | Đạt một phần | Có nhiều thuật toán tự viết; find_connected_components ưu tiên scipy.ndimage.label, có BFS dự phòng. Tuyên bố toàn bộ Pure NumPy quá rộng. | Lập bảng phần tự cài/phần thư viện; làm rõ với giảng viên phần nào thuộc lõi. | TV4 / P0 | [Mở minh chứng](<../../src/morphology.py>) |
| YC03 | Ứng dụng demo có giao diện | Cần xác nhận | FastAPI + HTML/CSS/JS hoạt động; hướng dẫn nêu Streamlit, Gradio hoặc PyQt. Chưa có bằng chứng chấp thuận framework thay thế. | Xác nhận FastAPI web demo được chấp nhận; giữ bằng chứng kiểm thử và video. | TV1 / P1 | [Mở minh chứng](<../../app.py>) |
| YC04 | PDF 30–60 trang tổng; 25–40 trang nội dung chính; 5 chương | Đạt trong phạm vi kiểm tra | PDF cục bộ 48 trang; 5 chương từ trang PDF 10–41: 32 trang. Kiểm tra cấu trúc, chưa đánh giá mọi câu chữ. | Giữ số trang sau khi cập nhật nội dung; kiểm tra lại bản PDF cuối. | TV1 / P2 | [Mở minh chứng](<../../report_overleaf/BTL_XLA_BaoCao.pdf>) |
| YC05 | Chương 3 và 4 chiếm hơn một nửa nội dung chính | Cần bổ sung | Chương 3: trang PDF 24–29 (6); chương 4: 30–38 (9). Tổng 15/32 = 46,875%, chưa quá 50%. | Bổ sung nội dung thiết kế, kiểm chứng và phân tích thực nghiệm có giá trị; cân đối lại chương. | TV1 / P1 | [Mở minh chứng](<../../report_overleaf/BTL_XLA_BaoCao.pdf>) |
| YC06 | Báo cáo hoàn chỉnh và nguồn tương ứng có trong gói nộp | Cần bổ sung | report_overleaf chứa bản đầy đủ nhưng bị ignore. docs/report/main.tex trên GitHub chỉ là khung. Sổ tay 13 trang không thay thế báo cáo 48 trang. | Chọn nguồn báo cáo chính, đưa nguồn và PDF đã kiểm tra vào gói nộp. | TV1 / P0 | [Mở minh chứng](<../../docs/report/main.tex>) |
| YC07 | Họ tên, MSSV, file phụ trách, phần viết, tỷ lệ đóng góp và chữ ký | Cần bổ sung | Bảng còn Thành viên 2–5/MSSV trống; 20% mỗi người chưa có minh chứng; chưa có xác nhận của đủ 5 người. | Điền danh tính thực, đối chiếu sản phẩm; nhóm tự xác nhận tỷ lệ và ký. | TV1 / P0 | [Mở minh chứng](<../../report_overleaf/main.tex>) |
| YC08 | Đầu vào–đầu ra–ràng buộc; mục tiêu đo được; 3–5 công trình | Đạt một phần | Có chương tổng quan và trích dẫn; còn mục tiêu loại trừ triệt để và mô tả CR không đúng code. Chưa chốt đủ tiêu chí chấp nhận định lượng. | Chốt mục tiêu đo được, phạm vi SAR và hạn chế; đối chiếu các công trình theo ưu/nhược điểm. | TV1 / P1 | [Mở minh chứng](<../../report_overleaf/chapters/01_tong_quan.tex>) |
| YC09 | Công thức, ký hiệu, tham số thống nhất với mã nguồn | Cần sửa | Báo cáo CR = 4πA/P² (độ tròn); code CR = (μ_biển − μ_vùng)/μ_biển (tương phản). Các ngưỡng và nhánh reference mới chưa đồng bộ. | Sửa công thức và bảng ký hiệu; mô tả đúng reference_image, ngưỡng thích ứng và closing. | TV2 / P0 | [Mở minh chứng](<../../report_overleaf/chapters/02_ly_thuyet.tex>) |
| YC10 | Dẫn xuất rút gọn và ví dụ số tính tay cho thuật toán chính | Đạt một phần | Có 5 ví dụ trong verification, gồm Lee 5×5; báo cáo liệt kê NMS nhưng bộ kiểm chứng hiện có morphology và Otsu. Cần đồng bộ ví dụ và bảng tính. | Đối chiếu từng ví dụ với đúng hàm; chứng minh/dẫn xuất cần được kiểm tra riêng. | TV2 / P1 | [Mở minh chứng](<../../src/verification.py>) |
| YC11 | Sơ đồ khối, cấu trúc module, giả mã từng thuật toán, độ phức tạp | Đạt một phần | Có sơ đồ, module và độ phức tạp. Chương 3 có hai khối giả mã (CLAHE, Lee), chưa đủ mọi thuật toán tự cài đã chọn trình bày. | Cập nhật pipeline mới và bổ sung giả mã/độ phức tạp cho phần lõi còn thiếu. | TV3 / P1 | [Mở minh chứng](<../../report_overleaf/chapters/03_thiet_ke.tex>) |
| YC12 | Đối chiếu thư viện: MSE, sai số lớn nhất và giải thích sai khác | Cần sửa | Chạy verification: Median 99,17%; Erosion 99,30%; Gaussian MSE 0,0060. Bảng LaTeX ghi tất cả MSE/sai số lớn nhất bằng 0 là sai. Chưa đối chiếu CLAHE/Canny. | Sinh bảng từ lần chạy thật; bổ sung sai số lớn nhất, đối chiếu lõi còn thiếu và giải thích quy tắc biên/làm tròn. | TV2 / P0 | [Mở minh chứng](<../../src/verification.py>) |
| YC13 | Nguồn, số lượng, kích thước, cách chia/nhãn và giấy phép | Chưa xác minh đầy đủ | Có Class_0, Class_1 và 10 ảnh mẫu. Chưa xác minh đầy đủ giấy phép và nguồn gốc từng tập; nhãn lớp không phải mask phân đoạn. | Lập manifest dữ liệu, nguồn/giấy phép, cách lấy mẫu và ý nghĩa nhãn. | TV5 / P1 | [Mở minh chứng](<../../kaggle/data>) |
| YC14 | Ghi CPU/RAM, hệ điều hành và phiên bản thư viện đúng lần chạy | Đạt một phần | Báo cáo có mục môi trường nhưng chưa đối chiếu với lần chạy sau merge; tài liệu cũ nêu Python 3.10+, cấu hình hiện tại dùng 3.13. | Ghi môi trường thực tế, commit, tham số và thời điểm của lần thực nghiệm cuối. | TV5 / P1 | [Mở minh chứng](<../../report_overleaf/chapters/04_thuc_nghiem.tex>) |
| YC15 | Ít nhất 3 hướng: so sánh, khảo sát tham số, điều kiện bất lợi | Đạt một phần | Có 5 script thí nghiệm và phân tích ca lỗi; chưa có bộ kết quả cập nhật theo commit mới. Không xem số lượng script là bằng chứng chất lượng kết quả. | Chốt câu hỏi cho từng thí nghiệm; chạy lại và đưa ca nhận nhầm biển/CLAHE vào phân tích. | TV5 / P0 | [Mở minh chứng](<../../run_experiments.py>) |
| YC16 | Bảng có trung bình ± độ lệch chuẩn trên tập đánh giá | Cần bổ sung | Thí nghiệm lọc xuất trung bình các chỉ số và thời gian; chưa xuất độ lệch chuẩn tương ứng. | Lưu kết quả từng ảnh; tổng hợp mean ± std, ghi số mẫu và chỉ số tốt nhất. | TV5 / P0 | [Mở minh chứng](<../../run_experiments.py>) |
| YC17 | Phân tích có căn cứ; không thay heuristic bằng độ chính xác | Cần sửa | CLEAN_BOUNDARY không so mask chuẩn; benchmark chỉ Class_1 + mẫu. Kiểm tra trước đó: nhánh mới vẫn báo dầu ở 4/5 ảnh biển mẫu. | Đổi diễn giải kết quả; đánh giá Class_0; chỉ báo IoU/Dice nếu có mask chuẩn hợp lệ. | TV4 / P0 | [Mở minh chứng](<../../evaluate_all_edges.py>) |
| YC18 | Một lệnh tái tạo toàn bộ bảng chương 4; cố định seed nếu ngẫu nhiên | Đạt một phần | run_experiments.py chạy 5 thí nghiệm, nhưng bảng đối chứng và benchmark cần lệnh riêng. Không mặc định thêm seed nếu pipeline không dùng ngẫu nhiên. | Cung cấp một entrypoint tái tạo các bảng dùng trong báo cáo, kèm cấu hình và seed nếu sinh nhiễu/lấy mẫu. | TV5 / P1 | [Mở minh chứng](<../../run_experiments.py>) |
| YC19 | A4, Times New Roman 13 pt, lề 3/2/2,5/2,5 cm; giãn 1,3 | Đạt một phần | Nguồn report dùng 12 pt; lề và giãn dòng khớp. mathptmx không đủ bằng chứng font nhúng đúng Times New Roman. | Sửa cỡ 13 pt, kiểm tra font nhúng, lề và tràn trang trên PDF cuối. | TV1 / P1 | [Mở minh chứng](<../../report_overleaf/main.tex>) |
| YC20 | IEEE; ≥10 nguồn; ≥3 bài báo có DOI | Đạt một phần | Có 12 mục BibTeX, 10 khóa được trích, 9 mục có trường DOI. Chưa xác minh DOI/nội dung nguồn; có website kiến thức nền ngoài dữ liệu/thư viện. | Kiểm tra từng nguồn và trích dẫn; thay nguồn web nền tảng khi cần để đúng quy định. | TV2 / P1 | [Mở minh chứng](<../../report_overleaf/references.bib>) |
| YC21 | Đối chiếu từng mục tiêu, hạn chế trung thực, 2–3 hướng khả thi | Đạt một phần | Có chương kết luận nhưng các kết luận sạch hoàn toàn và chỉ tiêu cũ cần sửa theo kết quả mới. | Phân loại đạt/đạt một phần/chưa đạt theo bằng chứng; giữ hướng phát triển xử lý ảnh. | TV1 / P1 | [Mở minh chứng](<../../report_overleaf/chapters/05_ket_luan.tex>) |
| YC22 | Slide bảo vệ 15–20 slide | Chưa tìm thấy | Không tìm thấy PPT/PPTX trong phạm vi dự án; chưa kiểm tra tài khoản ngoài dự án. | Lập slide theo 12 phút trình bày; lưu bản nguồn và PDF. | TV1 / P1 | Chưa tìm thấy trong dự án |
| YC23 | Video demo 5–7 phút | Chưa tìm thấy | Không tìm thấy MP4/WEBM trong dự án. Demo trực tiếp được hướng dẫn dành 3 phút trong buổi bảo vệ. | Quay video có thao tác và ca thất bại, ghi phiên bản ứng dụng. | TV1 / P1 | Chưa tìm thấy trong dự án |
| YC24 | Bảng đánh giá chéo và xác nhận thành viên | Cần bổ sung | Có bảng phân công trong LaTeX nhưng chưa có bảng đánh giá chéo với nhận xét/minh chứng/xác nhận thực tế. | Dùng mẫu 20 lượt đánh giá chéo trong Excel; từng thành viên tự điền và xác nhận. | TV1 / P1 | [Mở minh chứng](<../../report_overleaf/main.tex>) |
| YC25 | Lịch sử commit trải đều 8 tuần từ từng thành viên | Chưa đáp ứng minh chứng | 14 commit trên main từ 17/10 đến 11/11/2026; chưa phủ 16/09–10/11. Bốn tên tác giả Git không đồng nghĩa bốn người đã xác minh. | Giữ lịch sử; bổ sung minh chứng công việc thực tế và hỏi giảng viên về mâu thuẫn 3/8 tuần. | TV1 / P0 | [Lịch sử được chụp trong Excel](PHAN_CONG_VA_MINH_CHUNG_BTL.xlsx) |
| YC26 | Nhật ký tuần có ngày, nội dung, người và tình trạng thực tế | Cần xác minh | Phụ lục đã ghi 8 tuần hoàn thành, kể cả slide. Chưa đủ bằng chứng xác nhận; workbook sẽ phân biệt ghi nhận cũ và minh chứng. | Rà soát từng dòng; ghi hồi cứu và ngày bổ sung thật; không tự xác nhận tuần chưa có bằng chứng. | TV1 / P0 | [Mở minh chứng](<../../report_overleaf/chapters/phu_luc.tex>) |
| YC27 | Khai báo công cụ AI, phạm vi sử dụng và cách kiểm tra | Cần bổ sung | Phụ lục ghi Gemini/Antigravity và Claude, chưa ghi Codex đã hỗ trợ review, merge, cấu trúc dự án và tạo hồ sơ quản lý. | Khai báo đúng phần dùng AI; nhóm kiểm tra và chịu trách nhiệm nội dung, không tự xác nhận đã kiểm tra hết. | TV2 / P0 | [Mở minh chứng](<../../report_overleaf/chapters/phu_luc.tex>) |
| YC28 | Ghi nguồn mã, hình, dữ liệu; kiểm tra trùng lặp | Chưa xác minh đầy đủ | Có tài liệu tham khảo; chưa có kết quả kiểm tra trùng lặp hoặc bảng nguồn gốc đầy đủ của từng tài sản. | Bổ sung attribution và minh chứng nguồn; thực hiện kiểm tra theo quy trình của trường. | TV5 / P1 | [Mở minh chứng](<../../docs/assets/algorithm_guide>) |
| YC29 | Đánh số theo chương; chú thích, nhãn trục, PNG và phóng to chi tiết | Đạt một phần | Nguồn LaTeX có cấu hình đánh số/chú thích và các hình PNG. Chưa kiểm tra hoàn chỉnh vị trí chú thích, thang hiển thị và ROI ở bản cuối. | Kiểm tra hình/bảng từng trang sau khi tái tạo; bổ sung ROI và nhận xét có căn cứ. | TV5 / P2 | [Mở minh chứng](<../../report_overleaf/main.tex>) |
| YC30 | PEP 8, docstring đầu vào/đầu ra/công thức; hướng dẫn chạy | Đạt một phần | Có module và nhiều docstring; chưa chạy audit PEP 8 toàn dự án. README đã cập nhật, phụ lục cài đặt còn cũ. | Đối chiếu hướng dẫn và docstring với mã; kiểm tra phong cách riêng, không đồng nhất smoke test với kiểm chứng toàn bộ. | TV3 / P2 | [Mở minh chứng](<../../README.md>) |

## 4. Cách sử dụng Excel

[Mở PHAN_CONG_VA_MINH_CHUNG_BTL.xlsx](PHAN_CONG_VA_MINH_CHUNG_BTL.xlsx). Sáu sheet:

| Sheet | Nội dung |
| --- | --- |
| `Yeu_cau_BTL` | 30 yêu cầu/tiêu chí, hiện trạng, minh chứng, người phụ trách và ưu tiên. |
| `Thanh_vien` | 5 vai trò đề xuất; tên, MSSV, Git, đóng góp thực tế và xác nhận để trống. |
| `Khung_8_tuan` | 40 dòng (8 tuần × 5 vai trò), nhiệm vụ đề xuất và ghi nhận cũ tách khỏi minh chứng. |
| `Lich_su_Git` | 14 commit nguyên trạng trên main, SHA và thời gian tác giả/committer có múi giờ. |
| `Viec_can_hoan_thien` | 15 việc, phụ thuộc, tiêu chí nghiệm thu; ngày bắt đầu/hạn để trống, chờ chốt hạn nộp. |
| `Danh_gia_cheo` | 20 lượt đánh giá giữa các thành viên; điểm, nhận xét và chữ ký để trống. |

Bảng có bộ lọc, cố định tiêu đề và danh sách trạng thái. Thang đánh giá chéo 0–10 là **đề xuất**, không phải rubric chính thức. Nhóm cần xác nhận trước khi dùng. Các ngày là ô ngày Excel; các timestamp Git giữ nguyên chuỗi ISO để không mất múi giờ.

Đường dẫn minh chứng trong workbook tính tương đối từ `docs/management/`. Giữ cấu trúc thư mục khi chia sẻ. Các link `report_overleaf/` chỉ mở được khi người nhận có thư mục báo cáo cục bộ; bản clone GitHub hiện tại chưa có các file này.

## 5. Lịch sử 8 tuần và minh chứng hồi cứu

- Khung 8 tuần: **16/09–10/11/2026** (56 ngày). Ngày lập hồ sơ: **11/11/2026**. Commit ngày 11/11 vẫn được giữ trong sheet Git và đánh dấu ngoài khung; không loại để làm đẹp số liệu.
- 14 commit hiện có từ **17/10–11/11/2026**. Có 4 tên tác giả Git; không suy ra 4 người hoặc tự ánh xạ sang 5 thành viên.
- Phụ lục cũ ghi cả 8 tuần “Hoàn thành”, kể cả slide. Workbook chỉ chép lại nội dung đó với nhãn **chưa xác minh**; không dùng nó làm xác nhận đã hoàn thành.
- Có commit trong tuần chỉ chứng minh có commit; chưa chứng minh TV cụ thể thực hiện nhiệm vụ đề xuất trong tuần. Không có commit cũng không tự chứng minh nhóm không làm việc ngoài Git.
- Nếu có tài liệu cũ, lịch sử chỉnh sửa hoặc biên bản họp, bổ sung link, ngày bổ sung và người xác nhận. Không lấy ngày tạo/copy file hiện tại để khẳng định ngày hoàn thành trước đó.
- Không sửa ngày/tác giả, không tạo commit giả, không force-push lịch sử. Nhóm cần giải trình thiếu lịch sử Git và xin cách chấp nhận minh chứng bổ sung từ giảng viên.

## 6. Phạm vi đã thực hiện và giới hạn

- Đã tạo hồ sơ đối chiếu và workbook; chưa thực hiện 15 việc hoàn thiện trong backlog. “Chưa bắt đầu” là trạng thái của các việc đề xuất mới, không phủ nhận công việc đã có trước đó.
- Chưa sửa thuật toán, báo cáo gốc, lịch sử Git hoặc dữ liệu. Không chạy lại toàn bộ benchmark/thí nghiệm hay tái biên dịch PDF trong bước tạo hồ sơ.
- Không truy cập nguồn ngoài dự án để xác minh DOI, giấy phép hoặc danh tính tác giả. Các mục đó được đánh dấu cần kiểm tra.
- Công cụ hỗ trợ: Codex đọc tài liệu/code/Git, tổng hợp thiếu sót và tạo workbook/bản đối chiếu. Nhóm cần đọc lại, xác nhận dữ liệu và bổ sung khai báo AI phù hợp; tài liệu này không tự chứng nhận nhóm đã kiểm tra mọi dòng mã.
- Các kiểm tra sau khi sinh file: mở lại XLSX, kiểm tra 6 sheet, 40 dòng tuần, 20 cặp đánh giá, 14 commit khớp Git, các ô chưa xác nhận còn trống, các đường dẫn hiện có mở đúng và Git HEAD không đổi.
