# Báo cáo kỹ thuật SOS

Chưa phải bộ nộp hoàn chỉnh. Bản dựng hiện nằm trong `.cache/report/`; chỉ chuyển
sang thư mục bàn giao sau khi kiểm tra toàn bộ trang, số trang mục lục và nội dung.
Thông tin lớp, giảng viên, nhóm, mã sinh viên, chữ ký, điểm đóng góp và biên bản họp
phải được xác nhận thực tế. Không dùng nhật ký tự động thay cho đóng góp cá nhân.

## Nguồn nội dung

- `narrative.json`: nội dung chương và kết luận, gắn với vị trí trong mẫu gốc.
- `bibliography.json`: 13 tài liệu tham khảo được trích trong nội dung, gồm nguồn hiệu chuẩn Sentinel-1, ERA5 và QPOSD bổ sung.
- `template_contract.md`: quy tắc dùng mẫu, phạm vi thay đổi và các bước kiểm tra.
- Các bảng lấy trực tiếp từ `results/sos/*.json`; hình từ `report_figures/` và
  `diagnostics/`. Không gõ lại bảng kết quả bằng tay.

## Dựng và cập nhật trường

Các script dựng cần Python có `python-docx` và `lxml`. Khi thực hiện bằng Codex,
dùng Python của documents runtime theo skill. Biến `$DocPython` dưới đây là đường
dẫn tới interpreter phù hợp trên máy chạy; không phải tên executable cố định.

```powershell
& $DocPython scripts/inspect_report_template.py
& $DocPython scripts/build_report.py
powershell -NoProfile -File scripts/update_report_fields.ps1
& $DocPython scripts/import_report_fields.py
```

Lệnh cập nhật trường cần Microsoft Word trên Windows, chạy ẩn trên bản sao và đóng
Word sau khi xong. Script nhập kết quả kiểm tra hash của cả bản dựng lẫn bản Word,
giữ nguyên các style có sẵn và các phần khác của gói. Chỉ thêm style mục lục còn thiếu.
Nếu sửa nội dung phải dựng và cập nhật trường lại, không dùng mục lục cũ.

Sau đó dùng `render_docx.py` của documents skill để render
`.cache/report/Bao_cao_SAR_SOS_fields.docx`, kiểm tra **mọi trang** và đối chiếu
mục lục với trang thực tế. Các audit trong cache chỉ chứng minh phạm vi được ghi;
`layout_verified=false` không được coi là bản đã duyệt.

## Các kiểm tra còn lại

- Bố cục toàn bộ bản render mới nhất, đặc biệt bảng nhiều trang và hình thất bại.
- Số thứ tự công thức sát lề phải và dẫn chiếu đủ từng hình/bảng.
- Độ dài sau mỗi lần sửa phải được kiểm tra lại trong `render_audit.json`: nội dung
  chính cần nằm trong giao của hai hướng dẫn, tức 25–35 trang.
- Thông tin bìa và xác nhận của thành viên. Phần cứng đã ghi trong `environment.json`
  tại lúc chuẩn bị báo cáo; đây không phải nhật ký tải máy khi benchmark.
- DOCX/PDF cuối, slides và video demo trong bộ bàn giao.

`render_progress.json` lưu những trang đã xem và các lỗi phát hiện, gắn với hash
DOCX/PDF của đúng vòng render. Không chuyển trạng thái duyệt từ bản cũ sang bản mới
chỉ vì mục lục khớp. Bản v7 đã kiểm tra đủ 36 trang. Bản cập nhật tiếp theo bổ sung
hiệu chuẩn, gió, GUI/video và thẩm định QPOSD; phải kiểm tra lại các trang thay đổi.
