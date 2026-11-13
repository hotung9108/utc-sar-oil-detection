# Thực nghiệm bổ sung: ràng buộc ngưỡng thích nghi

Tái tạo: `python scripts/adaptive_experiment.py --workers 6`. Không đọc tập test hoặc thay kết quả/mô hình cũ. Đây là phân tích bổ sung sau lựa chọn, tái sử dụng validation; không phải kiểm chứng độc lập mới.

Từ 99 cấu hình Niblack đã khảo sát, lấy 3 cấu hình có F1 ứng viên cao nhất (hòa thì Recall rồi ID). Mỗi cấu hình dùng no morphology/min_area64, 8 đặc trưng và 9 cấu hình classifier: tổng 27 lần fit. Các lựa chọn cố định kế thừa thực nghiệm trước, không chứng minh tối ưu toàn cục. Chọn bằng F1 nghiêm ngặt; không dùng thời gian để phá hòa.

| Classifier NumPy | Tham số | F1 validation | Recall | Agreement với thư viện | Hội tụ |
|---|---|---:|---:|---:|---|
| cart | {'max_depth': 3, 'min_leaf': 5} | 0.144656 | 0.245255 | 1.000000 | True |
| svm | {'C': 10} | 0.137952 | 0.245620 | 1.000000 | True |

Cấu hình bổ sung chọn trên validation: `{'filter': {'name': 'lee', 'size': 7, 'looks': 1}, 'threshold': {'name': 'niblack', 'size': 51, 'k': 0.2}, 'morphology': {'operation': 'none', 'min_area': 64}}`, `cart {'max_depth': 3, 'min_leaf': 5}`.
Toàn bộ pipeline NumPy chạy lại trên 671 ảnh validation: F1=0.144656, Precision=0.102580, Recall=0.245255. Số đếm từng ảnh lưu trong `validation_full_numpy.json`.

Nhánh này đáp ứng thao tác ngưỡng thích nghi, chưa khắc phục thiếu góc tới/gió/nhãn look-alike. Chưa công bố test mới cho nhánh này; muốn kết luận tổng quát hóa phải có tập độc lập chưa sử dụng. Không gán kết quả test của nhánh Otsu cho nhánh Niblack.
