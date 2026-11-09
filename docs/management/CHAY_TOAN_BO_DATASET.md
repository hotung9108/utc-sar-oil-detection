# Xử lý toàn bộ dataset Kaggle trong repo

Ngày 11/11/2026 đã chạy lại `reproduce.py --workers 4` thành công trên **5.538/5.538 ảnh**, gồm 3.695 Class_0 và 1.843 Class_1. Không có hàng ảnh thiếu hoặc đường dẫn trùng. Đây là toàn bộ ảnh trong bản repo, không phải đủ 5.630 ảnh mà metadata CSIRO công bố; còn chênh 92 ảnh chưa biết nguyên nhân.

Kiểm kê đệ quy còn thấy 10 file trong `kaggle/data/sample/`, đều trùng SHA-256 với 10 ảnh đã có trong hai lớp chính. Vì vậy có **5.548 đường dẫn file nhưng 5.538 ảnh khác nhau**; các bản sao dùng cùng kết quả và không được tính lặp vào thống kê. `reproducible_data_inventory.json` lưu ánh xạ từng bản sao về ảnh đã đánh giá.

## Xem bất kỳ ảnh nào trong demo

```powershell
uv run streamlit run streamlit_app.py
```

Chọn **Nguồn ảnh có sẵn → Dataset Kaggle → Class_0 hoặc Class_1**. Gõ tên trong ô `Chọn ảnh Kaggle`, ví dụ `class_1_00013.jpg`. Ứng dụng xử lý ảnh vừa chọn, cho phép đổi từng tham số và tải PNG/JSON. Khi tải file riêng, ảnh upload được ưu tiên; xóa upload để quay lại ảnh có sẵn.

## Chạy hàng loạt để đánh giá

```powershell
uv run python reproduce.py --workers 4
```

Lệnh chạy ví dụ số, đối chiếu thư viện, khảo sát mẫu rồi toàn dataset. Không cần nhãn mask hoặc mô hình. Nhãn thư mục chỉ được dùng để đối chiếu sau khi xử lý ảnh. Nếu chỉ cần phần đánh giá toàn tập, entrypoint tương thích `uv run python evaluate_all_edges.py` dùng mặc định 4 worker; tên file cũ không có nghĩa chạy mọi toán tử biên trên mọi ảnh. Entry này chỉ cập nhật bảng dataset, không thay thế manifest full của `reproduce.py`.

| Đầu ra trong `results/reproducible/` | Ý nghĩa |
| --- | --- |
| `dataset_per_image.csv` | Một hàng/ảnh: đường dẫn, nhãn, có ứng viên hay không, số vùng, diện tích, tương phản và thời gian |
| `dataset_summary.csv` | Thống kê gộp theo lớp; không phải số liệu mask chuẩn |
| `confusion.json` | TP/FP/FN/TN và các chỉ số cấp ảnh |
| `manifest.json` | Phạm vi full/samples, phiên bản môi trường, cấu hình, hash nguồn, thời điểm chạy |

Pipeline toàn tập cố định: Lee 5×5, L=4 → CLAHE clip=2, lưới 8×8 → Otsu/hình thái, min_area=300, min_contrast=0,10, closing_radius=4. Khảo sát nhiều bộ lọc/tham số/nhiễu chỉ thực hiện trên 10 ảnh mẫu; **không tuyên bố mọi ảnh đã chạy mọi tổ hợp thuật toán**.

| Kết quả | Giá trị |
| --- | ---: |
| TN / FP / FN / TP | 810 / 2.885 / 204 / 1.639 |
| Precision | 36,23% |
| Recall | 88,93% |
| F1 | 51,48% |
| Specificity | 21,92% |
| Accuracy | 44,22% |

Kết quả cho thấy báo nhầm cao, không chứng nhận nhận diện dầu đáng tin cậy. Không có ground truth pixel nên chưa tính IoU/Dice hoặc độ chính xác biên. Không có quá trình train/test học mô hình; chọn tham số sau khi xem dữ liệu vẫn có thể gây thiên lệch.

`results/` được bỏ qua bởi Git vì tái tạo được. Bản CSV/JSON dùng cho báo cáo nằm trong `docs/report/evidence/` có checksum. Lượt batch lưu số liệu từng ảnh, không tự xuất 5.538 bộ PNG trung gian; muốn xem/tải ảnh cụ thể dùng demo. Không lấy một lượt `--samples-only` để xác nhận toàn bộ dataset.
