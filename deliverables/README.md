# Bàn giao bản review dự án SAR

Đây là bộ tài liệu và mã nguồn để nhóm chạy, rà soát và hoàn thiện. **Chưa phải bản nộp đầy đủ Đề 18**; tình trạng từng yêu cầu nằm trong `docs/management/completion_audit.json`.

Gói v4: `packages/SAR_review_v4.zip`, gồm báo cáo v11, slide v5, 10 notebook
và các kết quả SOS, DARTIS/PALSAR, QPOSD. Trạng thái kiểm tra và hash của từng gói nằm trong
tệp JSON cùng tên bên cạnh ZIP; không chuyển xác nhận từ gói cũ sang gói mới.

## Các sản phẩm

| Sản phẩm | Điểm mở |
|---|---|
| Báo cáo 41 trang, 29 trang nội dung chính, có kết quả QPOSD | `report/Bao_cao_SAR_SOS_review_v11.docx` hoặc `.pdf` |
| Slide 24 trang, có kết quả và ca thất bại QPOSD | `presentation/SAR_SOS_review_v5.pptx` |
| Video tự động 6 phút có phụ đề, không âm thanh | `video/SAR_demo_v1.mp4` |
| Giao diện PyQt | `scripts/demo_qt.py` từ thư mục gốc |
| Năm notebook SOS theo nhiệm vụ | `notebooks/01_...` đến `05_...` |
| Nhánh Sentinel-1 gốc và gió ERA5 | `notebooks/external/07_sentinel_calibration.ipynb` |
| DARTIS: 2.290 ảnh đã đánh giá, báo nhầm 63,2751% | `results/dartis/REPORT.md` |
| QPOSD: đối chiếu NumPy/thư viện, 5 ảnh test và nhầm lẫn dầu/tương tự dầu | `results/qposd/REPORT.md`; `notebooks/external/10_qposd_classification_detection.ipynb` |

## Chạy sau khi giải nén

Các lệnh sau chạy ở thư mục có `pyproject.toml`, không chạy trong `deliverables/`.

```powershell
uv sync --frozen --extra demo
uv run --frozen --extra demo python run_experiments.py --verify-only
```

Lệnh `--verify-only` đối chiếu bằng chứng đã lưu và chạy tests; không huấn luyện lại, không chứng minh mọi yêu cầu đã hoàn thành. Gói có manifest chia dữ liệu để kiểm tra provenance. Muốn suy luận, chạy notebook có đọc ảnh hoặc tái lập toàn bộ thí nghiệm, tải SOS v1 theo `data/README.md` và đặt đúng cây thư mục trước:

```powershell
uv run --frozen --extra demo python scripts/demo_qt.py
uv run --frozen --extra demo python run_experiments.py --workers 6
```

Notebook 07 cần dữ liệu SAR/metadata/gió đã tải bởi các script ở `results/physical/README.md`. Notebook 06 đã thực thi bốn ô mã trên kết quả đủ 2.290 ảnh, gồm ba hình đã kiểm tra trực quan; bộ kiểm tra vẫn từ chối nếu DARTIS thiếu ảnh hoặc sai hash. Kết quả DARTIS đã có trong báo cáo v9 và slide v3; ZIP v1 vẫn là bản trước cập nhật này. Để dựng lại DOCX/PPTX, xem `docs/report/README.md` và `deliverables/presentation/README.md`; công cụ Word/Artifact Tool là phụ thuộc bổ sung, không thuộc lệnh tái lập SOS.

## Kiểm tra gói

`scripts/build_review_package.py` tạo ZIP mới, giữ hash của bản báo cáo/slide/video đã duyệt, kiểm tra CRC và SHA-256 tất cả thành viên. `PACKAGE_MANIFEST.json` trong ZIP liệt kê từng tệp và hash. Gói không chứa dữ liệu ảnh thô, `.venv`, cache, `.git` hoặc kho `legacy`; lịch sử đầy đủ vẫn ở repository. Vì thiếu `legacy`, không dùng gói này để chạy phép kiểm tra bảo toàn kho lịch sử.

```powershell
python scripts/build_review_package.py --output deliverables/packages/SAR_review_v1.zip
python scripts/verify_review_package.py deliverables/packages/SAR_review_v1.zip
```

Script không ghi đè gói đã có; khi cập nhật cần chọn tên phiên bản mới. Hash xác nhận byte của tệp, không xác nhận độ đúng của nhãn hoặc đóng góp cá nhân.

### Kiểm tra cài đặt mới đã thực hiện

Đã tạo `.venv` mới trong thư mục giải nén gói v1, cài `uv sync --frozen --extra demo` với Python 3.13.5 và `include-system-site-packages=false`. Kiểm chứng số liệu/output notebook và 22 tests đạt. Qt khởi động được; cả hai mô hình đã lưu chạy được trên ảnh hằng tổng hợp 32×32. Đây là kiểm tra nạp và ghép nối chương trình, không phải số đo độ chính xác SAR. Bằng chứng ngoài ZIP tại `docs/management/package_environment_audit.json`, gắn với hash gói v1. Gói ZIP đã phát hành không bị sửa.

Để kiểm tra lại từ repository sau khi giải nén và cài môi trường riêng:

```powershell
python scripts/verify_package_environment.py --project <thu-muc-giai-nen>
```

Đã thử trên cùng máy Windows với môi trường ảo mới; chưa thử trên hệ điều hành khác. Script kiểm tra môi trường được bổ sung sau khi đóng gói v1 nên lấy từ repository hiện tại.

## Phần còn thiếu

- Nhãn và căn chỉnh hợp lệ để đánh giá tác động hiệu chuẩn/gió lên phát hiện dầu.
- Nhãn theo từng nguyên nhân vật lý của look-alike; QPOSD đã đánh giá lớp chung trên 24 cặp hợp lệ, chưa chứng minh độc lập cảnh.
- Test Sentinel độc lập mới cho nhánh Niblack; đã có phép thử PALSAR bổ sung, không dùng kết quả Otsu thay thế.
- Thông tin bìa, mã sinh viên, xác nhận đóng góp, chữ ký và biên bản họp thật.

Các ô chưa xác nhận được giữ trống. Video và kết quả tự động không thay thế thuyết trình, buổi họp hay công việc thực tế của từng thành viên.
