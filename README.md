# Bài tập lớn Xử lý ảnh — UTC

Khử nhiễu, tăng cường tương phản và xử lý biên vùng tối ứng viên trên ảnh SAR bằng **xử lý ảnh truyền thống**, không có machine learning/deep learning. Mục tiêu chính là [hướng dẫn BTL XLA](<docs/00_tai_lieu_goc/huong_dan_btl_docx/ds btl xla VÀ HƯỚNG DẪN.docx>); đề tài 18 trong tài liệu NASA chỉ định hướng dataset. Đề kết hợp đã được nhóm xác nhận đăng ký.

## Chạy demo

Python **3.13**; chạy tại thư mục gốc dự án:

~~~powershell
uv sync --locked --all-extras
uv run streamlit run streamlit_app.py
~~~

Mở http://localhost:8501. Windows có thể chạy `run_app.bat` sau khi cài môi trường. Nếu dùng pip:

~~~powershell
py -3.13 -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
.venv\Scripts\python -m streamlit run streamlit_app.py
~~~

Demo có ảnh mẫu và tải ảnh, thay phương pháp/tham số, sáu ảnh kết quả, histogram/lát cắt, bảng đối chiếu, tải PNG/JSON. Ảnh được đổi kích thước thành 400×400. `app.py` và `static/` là demo FastAPI cũ; **Streamlit là demo chính để nộp**.

## Mã nguồn và phân công

| Vai trò | Họ tên / GitHub đã xác minh | Vị trí triển khai | Trách nhiệm |
| --- | --- | --- | --- |
| TV1 — Trưởng nhóm | Tiến Sơn Trần / `Maloque18705` | `src/tv1/`, `streamlit_app.py` | Pipeline, validation, I/O, giao diện |
| TV2 | Lương Tiến Dũng / `ltdungg` | `src/tv2/` | Ví dụ số, đối chiếu thư viện và minh chứng |
| TV3 | Hồ Việt Tùng / `hotung9108` | `src/tv3/` | Lọc và tăng cường tương phản |
| TV4 | Nguyễn Hải Hiếu / `hina-kasumi` | `src/tv4/` | Làm nét, biên, Otsu, hình thái và liên thông |
| TV5 | Phạm Minh Tuấn / `tuanpham21105` | `src/tv5/`, `reproduce.py` | Chỉ số, thí nghiệm, tham số, ca lỗi và dữ liệu |

[Tài liệu học và trình bày riêng cho từng thành viên](docs/thanh_vien/README.md) có **một Markdown đầy đủ và một PDF cho mỗi người**: 10 chương giải thích từ nền tảng, ví dụ tính tay, giới hạn thuật toán, bài thực hành, slide/thời lượng và 20–25 câu hỏi có gợi ý trả lời. Chương 8 và [hướng dẫn đầu ra](results/README.md) chỉ rõ nơi lưu kết quả chạy. Họ tên do nhóm cung cấp; tài khoản được đối chiếu với API collaborators của repo.

Lõi xử lý dùng NumPy/Python. OpenCV phục vụ đọc/ghi/resize/hiển thị; OpenCV/SciPy được gọi trong module đối chiếu. Gán nhãn liên thông tự cài bằng run-length union-find. NumPy FFT là phép toán số cho bộ lọc đồng hình; không tuyên bố tự cài FFT.

Các file trực tiếp dưới `src/` chuyển tiếp import để giữ tương thích. Xem [phân công mã nguồn](docs/management/PHAN_CONG_MA_NGUON.md). Đây là trách nhiệm hiện tại, không gán lại tác giả commit trong quá khứ.

~~~text
BTL/
├── streamlit_app.py             # Demo chính
├── reproduce.py                 # Một lệnh tái tạo mọi bảng thực nghiệm
├── src/tv1/ ... src/tv5/         # Triển khai theo vai trò
├── tests/                       # Hồi quy thuật toán và Streamlit
├── data/sample/                 # 10 ảnh demo
├── kaggle/data/Class_0,Class_1/  # 5.538 ảnh có nhãn thư mục
├── docs/report/                 # PDF, DOCX, LaTeX, hình và evidence
├── docs/slides/                 # PPTX, PDF và kịch bản bảo vệ
├── docs/management/             # Phân công, Excel, đối chiếu yêu cầu
├── docs/thanh_vien/             # 5 folder học, trình bày và vấn đáp cá nhân
├── docs/00_tai_lieu_goc/         # Hướng dẫn học phần và giáo trình
├── scripts/                    # Dựng báo cáo/slide, xuất PDF
├── results/                    # Đầu ra tái tạo, được Git bỏ qua
└── pyproject.toml, uv.lock      # Python và phụ thuộc đã khóa
~~~

## Kiểm chứng và tái tạo

~~~powershell
uv run python reproduce.py
uv run --extra dev python -m pytest tests -q
uv run --extra dev ruff check --config pyproject.toml src tests streamlit_app.py reproduce.py
~~~

`reproduce.py` chạy 5 ví dụ số, 33 thuật toán/chỉ số × 18 ca đối chiếu, khảo sát 10 ảnh mẫu và đánh giá **cả hai lớp** dữ liệu. Seed 2026; lưu từng ảnh và trung bình/độ lệch chuẩn. Manifest lưu phạm vi, môi trường, cấu hình và SHA-256 nguồn. `--samples-only` là lượt chạy thiếu phần toàn dataset; trình dựng báo cáo từ chối dùng nó để xác nhận kết quả toàn tập.

Kết quả hiện tại: **558 PASS, 36 DESCRIPTIVE, 0 FAIL** trong 594 đối chiếu. Bilateral/Canny là so sánh biến thể; DESCRIPTIVE không phải PASS. Phép ghép thư viện cho Lee/Frost/Kuan/đồng hình kiểm tra công thức đã chọn, không phải API tương đương độc lập cho từng phương pháp.

Đánh giá cấp ảnh: TN=810, FP=2.885, FN=204, TP=1.639. Precision ≈36,23%, recall ≈88,93%; đây **không phải đánh giá mask pixel**. [Metadata CSIRO trong repo](kaggle/metadata/dataset_metadata.xml) xác định nhãn 0=không dầu, 1=có dầu, DOI 10.25919/4v55-dn16; [giấy phép đi kèm](kaggle/metadata/license.html) ghi CC BY-SA 4.0. Bản repo ít hơn số công bố 92 ảnh; chưa có mask chuẩn hoặc checksum bộ gốc.

## Báo cáo, slide và hồ sơ nhóm

- [Báo cáo PDF](docs/report/BAO_CAO_BTL_XLA.pdf), [Word chỉnh sửa được](docs/report/BAO_CAO_BTL_XLA.docx), [nguồn LaTeX](docs/report/main.tex).
- [Slide PowerPoint](docs/slides/BAO_VE_BTL_XLA.pptx), [slide PDF](docs/slides/BAO_VE_BTL_XLA.pdf), [kịch bản 12 phút + demo 3 phút](docs/slides/KICH_BAN_BAO_VE.md).
- [Excel phân công, khung 8 tuần và đánh giá chéo](docs/management/PHAN_CONG_VA_MINH_CHUNG_BTL.xlsx). Tên/GitHub đã cập nhật; MSSV, điểm, đóng góp và chữ ký để nhóm tự điền. Có thêm khung hồi cứu 10/08–11/11/2026, không thay lịch sử Git.
- [Excel kế hoạch chi tiết 10/08–11/11/2026](docs/management/KE_HOACH_PHAN_CONG_1008_1111_2026.xlsx): 70 nhiệm vụ, 14 khoảng tuần, 5 sheet thành viên, sản phẩm/tiêu chí/người kiểm tra và bảng tiến độ. Cập nhật ô vàng trong `Ke_hoach`; các mốc quá khứ là phân bổ hồi cứu, trạng thái thực tế cần nhóm xác nhận. Giữ bản sao trước khi dựng lại bằng `scripts/build_project_plan.py --overwrite`, vì thao tác này thay các cập nhật thủ công.
- [Đối chiếu yêu cầu hiện tại](docs/management/KIEM_TRA_HIEN_TAI.md). `DOI_CHIEU_YEU_CAU_BTL.md` là snapshot trước đợt sửa.

Dựng lại từ số liệu vừa chạy:

~~~powershell
uv run --extra docs python scripts/build_report.py
uv run --extra docs python scripts/build_defense_slides.py
powershell -NoProfile -File scripts/export_slides.ps1
~~~

PDF báo cáo nhúng Times New Roman của Windows, dùng công thức vector từ LaTeX; DOCX/LaTeX chứa cùng nội dung, phân trang có thể thay đổi theo phần mềm. Xuất PDF slide cần Microsoft PowerPoint; PPTX tạo được bằng python-pptx. Canva MCP đã được kiểm tra nhưng bị quản trị viên vô hiệu hóa.

`docs/report/evidence/` giữ CSV/JSON và checksum đã dùng trong báo cáo. Không cần commit ảnh trung gian trong `results/`; không chỉnh tay CSV để làm đẹp số liệu. Các tài liệu `docs/01_...06_...` và sổ tay PDF chỉ để tham khảo lịch sử; báo cáo chính nằm trong `docs/report/`.

## Vì sao CLAHE làm xuất hiện đốm tối?

Lee giảm đốm theo thống kê cục bộ, không xóa mọi nhiễu/kết cấu nền. CLAHE ánh xạ lại mức xám theo từng vùng nên chênh lệch nhỏ vốn khó nhìn trở nên rõ. Toán tử biên phát hiện thay đổi cường độ, không biết đó có phải dầu hay không. Đồng nhất mọi đường biên hoặc vùng tối với dầu gây **báo động giả**.

Pipeline giữ ảnh sau lọc trước CLAHE làm tham chiếu, lọc diện tích/tương phản, tách làm nét khỏi phân đoạn. Ảnh class_1_00013 hiện giữ một vùng ứng viên khoảng 2,08% ảnh; vẫn có báo nhầm trên ảnh biển. Báo cáo không tuyên bố đã loại hết lỗi.

## Xem và chạy tất cả ảnh Kaggle

Trong sidebar chọn **Nguồn ảnh có sẵn → Dataset Kaggle → Class_0/Class_1**, rồi gõ tên ảnh trong ô chọn. Demo đọc cả 5.538 ảnh cục bộ và xử lý ảnh được chọn theo tham số hiện tại; không tự chạy cả dataset mỗi lần bấm widget.

`kaggle/data/sample/` còn có 10 file trùng byte với các ảnh trong hai lớp chính: 5.548 đường dẫn tương ứng 5.538 ảnh khác nhau. Thống kê không đếm lặp các bản sao.

`uv run python reproduce.py --workers 4` xử lý toàn tập bằng pipeline mặc định, lưu CSV mỗi ảnh và confusion JSON trong `results/reproducible/`. [Hướng dẫn và phạm vi kết quả](docs/management/CHAY_TOAN_BO_DATASET.md); [bằng chứng không dùng ML/DL](docs/management/KIEM_TRA_ML_DL.md).

Video 5–7 phút chưa làm theo yêu cầu hiện tại. Trước khi nộp, nhóm cần điền và ký hồ sơ, xác nhận nguồn dữ liệu/trích dẫn, diễn tập và giải trình lịch sử Git chưa đủ 8 tuần. Không sửa ngày/tác giả để tạo minh chứng giả.
