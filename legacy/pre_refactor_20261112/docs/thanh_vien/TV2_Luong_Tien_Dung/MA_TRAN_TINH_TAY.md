# TV2 - Lương Tiến Dũng: Otsu và đối chiếu thư viện

## Mục tiêu và liên hệ phần việc

TV2 phụ trách lý thuyết và kiểm chứng. Bài này tự tìm ngưỡng Otsu bằng NumPy, tính tay đáp án, rồi đối chiếu mã sản xuất và OpenCV. Thuật toán Otsu trong ứng dụng thuộc module TV4; TV2 cần nắm nó để thiết kế phép kiểm chứng độc lập. Đây là tài liệu để thành viên tự luyện và giải thích, không xác nhận công việc đã được thành viên thực hiện.

## Ma trận đầu vào 4 × 4

```text
A = [50 50 200 200
     50 50 200 200
     50 50 200 200
     50 50 200 200]
```

Histogram có tám pixel mức 50 và tám pixel mức 200. Xác suất mỗi mức là 8/16 = 0,5. Trung bình toàn ảnh là (8×50 + 8×200)/16 = 125.

## Tính ngưỡng từng bước

Với t < 50, lớp tối rỗng nên không xét. Với 50 ≤ t < 200, lớp tối chứa tám số 50, lớp sáng chứa tám số 200. Vì vậy w0 = w1 = 0,5; mu0 = 50; mu1 = 200.

Phương sai giữa lớp: sigma_B² = w0 × w1 × (mu0 - mu1)² = 0,5 × 0,5 × 150² = 5.625. Với t ≥ 200, lớp sáng rỗng nên không xét. Tất cả ngưỡng nguyên từ 50 đến 199 cho cùng điểm số; mã chọn ngưỡng đầu tiên đạt cực đại, tức 50. Một cài đặt chọn 199 vẫn tạo cùng mask trên ma trận này, nên khi so sánh cần xem cả quy tắc phá hòa và ảnh đầu ra.

Phương sai toàn ảnh là [8×(50-125)² + 8×(200-125)²]/16 = 5.625. Hệ số khả tách eta = sigma_B² / sigma_total² = 1. Đây là tách hoàn hảo về mức xám của ví dụ, không phải độ chính xác phát hiện dầu 100%.

## Mask kỳ vọng

Chọn pixel ≤ 50 và hiển thị bằng 255:

```text
B = [255 255 0 0
     255 255 0 0
     255 255 0 0
     255 255 0 0]
```

## Mã kiểm chứng và thư viện

`vi_du_ma_tran.py` dùng vòng lặp xét 256 ngưỡng, tự tính trọng số, trung bình và phương sai giữa lớp. OpenCV chỉ được gọi sau đó làm đối chứng với `THRESH_BINARY_INV | THRESH_OTSU`, vì cần vùng tối thành trắng. Nếu dùng `THRESH_BINARY` thì mask bị đảo chiều, không phải Otsu tính sai.

Đã kiểm chứng bằng NumPy: ngưỡng 50, điểm số 5.625, eta của mã sản xuất bằng 1 và mask trùng OpenCV từng pixel. Chạy:

```text
.venv\Scripts\python.exe -X utf8 docs/thanh_vien/TV2_Luong_Tien_Dung/vi_du_ma_tran.py
```

## Câu hỏi để tự bảo vệ

1. Vì sao không dùng ngưỡng 125 luôn? Với ma trận này nó cho cùng mask, nhưng Otsu phải hoạt động khi histogram khác.
2. Vì sao phải bỏ ngưỡng có lớp rỗng? Trung bình lớp đó không xác định vì chia cho 0.
3. Eta = 1 có chứng minh dầu không? Không, chỉ chứng minh hai mức xám được phân tách trong ví dụ.
4. Có phải đang dùng ML không? Không; chỉ tối ưu một tiêu chí thống kê trên ảnh hiện tại, không huấn luyện mô hình.
5. Nếu hai cài đặt cho mask giống nhưng ngưỡng khác thì làm gì? Kiểm tra các ngưỡng đồng cực đại và quy tắc chọn ngưỡng trước khi kết luận lỗi.

Nguồn đối chiếu: `src/tv2/library_comparison.py`, `src/tv4/morphology.py`, kết quả `results/verification/`.
