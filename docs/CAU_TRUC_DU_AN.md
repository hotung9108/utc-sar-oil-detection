# Bản đồ dự án

**Dọn bản xuất cũ (18/11/2026):** đã bỏ báo cáo/slide/video và ZIP bàn giao trong `deliverables/`, nguồn báo cáo `latex/`, `latex_btl/`, `docs/report/`, các bản tương ứng trong `legacy/`, preview/cache xuất bản và bản PDF/slide trong `XLA/`. Giữ ảnh minh họa trong `XLA/`, đề bài/giáo trình và `results/`. Lịch sử file đã bỏ và hash của 81 file lưu trữ nằm tại `management/removed_old_deliverables.json`; manifest của `legacy/` nay chỉ kiểm tra các file được giữ, không còn là bản lưu nguyên vẹn 5.938 file trước đây.

**Cập nhật dọn file dùng một lần (18/11/2026):** đã xóa 12 script trong `scripts/notebook_tools/` và 21 script Python tạm tại cấp gốc `.cache/`. Notebook hiện có là nguồn chỉnh sửa trực tiếp; chạy bằng `scripts/run_notebooks.py`. Dữ liệu, mô hình, kết quả và log kiểm chứng được giữ nguyên. Danh mục lệnh và trình chạy thí nghiệm đã bỏ bước sinh notebook. Lịch sử các công cụ đã xóa được lưu riêng trong `removed_one_time_tools` của bản ghi chuyển cấu trúc.

## Bắt đầu từ đâu?

| Bạn muốn làm gì? | Mở / chạy |
|---|---|
| Dùng giao diện | `uv run --frozen --extra web streamlit run streamlit_app.py` |
| Đọc quy trình chính | `notebooks/01_data_and_ground_truth.ipynb` đến `05_final_pipeline.ipynb` |
| Đọc mã thuật toán | `src/sar_oil/` |
| Tìm một lệnh thực nghiệm | `python scripts/tasks.py list` hoặc [danh mục scripts](../scripts/README.md) |
| Xem số liệu thật | `results/sos/`, `results/cantarell/`, `results/qposd/` |
| Biết còn thiếu gì so với đề | [Đối chiếu Đề 18](DANH_GIA_DU_AN_VA_DOI_CHIEU_DE_18.md) |

## Các nhóm thư mục

- **Chạy và phát triển:** `src/`, `scripts/`, `tests/`, `.streamlit/` và `streamlit_app.py`.
- **Dữ liệu và chứng cứ:** `data/` chứa ảnh/nhãn/metadata; `results/` chứa mô hình, lựa chọn và số đo. Không xem `results/` là cache để xóa.
- **Học và giải thích:** `notebooks/` hiện có 15 notebook (8 ở cấp gốc, 7 trong `external/`); `study_guide/` là ví dụ tự học, không thay thế pipeline đã kiểm chứng.
- **Tài liệu dự án:** `docs/00_tai_lieu_goc/` giữ đề gốc; `docs/management/` giữ giao thức, kiểm kê, phân công và nhật ký kiểm tra; các file MD ở `docs/` là hướng dẫn hiện hành.
- **Lịch sử:** `legacy/` giữ bản trước refactor, không tham gia suy luận hiện tại.
- **Công cụ cục bộ:** `.venv/`, `.agents/`, `.pytest_cache/`, `.ruff_cache/`; `.git/` là lịch sử Git. `.cache/` còn chứa worktree Git và cache thí nghiệm, không xóa toàn bộ mà chưa kiểm tra.
- **`configs/`:** hiện là trang chỉ dẫn nơi cấu hình thực sự được lưu; grid ở `src/sar_oil/experiments.py`, lựa chọn đã khóa ở `results/`.

## Quy tắc sắp xếp mới

Toàn bộ script đã được chia nhóm vật lý: `sos_experiments/`, `cantarell/`, `qposd/`, `dartis/`, `physical/`, `validation/`, `desktop/`, `web/`, `publishing/`, `packaging/`. Có 98 file được chuyển; cấp gốc chỉ giữ ba lệnh chính, hai module hỗ trợ nội bộ và danh mục/hướng dẫn.

Lệnh thường dùng vẫn giữ nguyên: `scripts/sos.py`, `scripts/run_notebooks.py`; tái tạo bằng chứng dùng `scripts/validation/rebuild_evidence.py`. Các lệnh công cụ được chuyển có bản đồ đường dẫn cũ → mới tại `docs/management/script_reorganization.json`. Tài liệu và manifest lịch sử không được viết lại thành một lần chạy mới.

### Bảo toàn nguồn bằng chứng

Di chuyển đã làm thay đổi import, cách tìm thư mục gốc và các cổng kiểm tra nguồn, nên SHA-256 mã nguồn mới khác bản gốc. Bản ghi migration lưu commit gốc, đường dẫn và cả hai hash; không sửa các hash trong số liệu thí nghiệm cũ. Khi đọc chứng cứ cũ, chỉ nguồn có hash mới khớp chính xác bản migration mới được chấp nhận thay cho nguồn cũ. Các file dữ liệu/mô hình không có ngoại lệ này. Khi sinh kết quả mới, hàm digest vẫn trả hash thật của file mới.

Migration là bản ghi thay đổi cấu trúc đã kiểm tra, không phải định lý chứng minh hai chương trình tương đương. Kiểm thử thuật toán, kiểm tra các mask đã lưu và chạy lại notebook cung cấp bằng chứng hồi quy bổ sung. Không cập nhật migration để hợp thức hóa thay đổi thuật toán mà chưa có thực nghiệm mới.

Việc sắp xếp không đồng nghĩa dự án đã đạt 100% đề; giới hạn dữ liệu và đánh giá trong tài liệu đối chiếu vẫn còn hiệu lực.

## Kiểm tra sau sắp xếp — 18/11/2026

- `python -m unittest discover -s tests`: **69 kiểm thử đạt**.
- `python scripts/run_notebooks.py --all`: **15/15 notebook chạy thành công**. Kiểm tra riêng import/bootstrap từ thư mục của từng notebook cũng đạt cho cả 15 notebook.
- `python scripts/validation/verify_outputs.py`: 8 notebook cấp gốc có output, không có lỗi cell; số liệu tổng hợp SOS và pipeline NumPy khớp.
- `python scripts/cantarell/verify_cantarell_results.py`: kiểm tra lại **50 so sánh ứng viên, 84 cặp mô hình, 175 mask kiểm tra**.
- `python scripts/packaging/verify_archive.py`: **5.938 file lưu trữ khớp checksum gốc**.
- `src/` và số liệu/mô hình trong `results/` được giữ nguyên. Notebook được cập nhật import/đường dẫn và chạy lại. Công cụ xuất bản được kiểm tra cú pháp/đường dẫn; không dựng lại Word/PDF/slide/video.
