# Gói bàn giao để rà soát

[SAR_review_v3.zip](SAR_review_v3.zip) là bản hiện tại: 233 tệp và manifest,
39.181.421 byte, gồm báo cáo v10, slide v4, DARTIS và phép thử hai pipeline
trên 3.101 patch PALSAR. SHA-256:
`c539d5e52ebc5170dab939846b32366d2726ede348e354341f0f942a0849941e`.
Đã kiểm tra mọi thành viên và cài môi trường mới theo lock: 22 tests, kiểm
chứng SOS đã lưu, khởi động Qt và hai mô hình trên ảnh tổng hợp đều đạt.
Audit riêng: `docs/management/package_environment_audit_v3.json`. Phạm vi
không bao gồm tái huấn luyện, chạy lại dữ liệu thô hoặc hệ điều hành khác.

[SAR_review_v2.zip](SAR_review_v2.zip) là bản trước: 218 tệp nguồn và bằng
chứng, kèm `PACKAGE_MANIFEST.json`; dung lượng 38.175.632 byte. Gồm báo cáo v9,
slide v3, notebook DARTIS đã chạy và kết quả đầy đủ 2.290 ảnh. Không chứa ảnh
thô, môi trường ảo, cache, Git hoặc các bản báo cáo/slide cũ.

SHA-256: `499d8c06852bb9b3a94f4dd2a1b3df0e04e040ddce574bf5e0a9fb03e2e4cdfd`.

Đã kiểm tra CRC và SHA-256 mọi thành viên, giải nén riêng, cài môi trường mới
bằng `uv sync --frozen --extra demo`: 22 tests và kiểm chứng kết quả SOS đã lưu
đạt; Qt khởi động và hai mô hình chạy được trên ảnh hằng tổng hợp. Không coi
kiểm tra khởi động là độ chính xác SAR hoặc tái huấn luyện toàn bộ. Chưa thử
trên hệ điều hành khác. Bằng chứng sau đóng gói nằm ngoài ZIP tại
`docs/management/package_environment_audit_v2.json`, gắn với hash gói.

```powershell
python scripts/verify_review_package.py deliverables/packages/SAR_review_v2.zip
python scripts/verify_package_environment.py --project <thu-muc-giai-nen> --package deliverables/packages/SAR_review_v2.zip --output <tep-audit-moi.json>
```

Lệnh thứ hai chạy sau khi cài môi trường trong bản giải nén còn nguyên tệp.
Lệnh kiểm chứng có thể cập nhật nhật ký trong thư mục giải nén, không sửa ZIP.
Gói là ảnh chụp tại thời điểm đóng; audit và README bổ sung sau đó không tự
xuất hiện bên trong. Bản v1 được giữ để truy vết.

Đây chưa phải bộ nộp hoàn chỉnh: còn thông tin nhóm và hồ sơ đóng góp thật,
nhãn để đánh giá hiệu chuẩn/gió và phân biệt nguyên nhân look-alike, cùng test
độc lập mới cho nhánh Niblack. Xem `deliverables/README.md` và completion audit.
