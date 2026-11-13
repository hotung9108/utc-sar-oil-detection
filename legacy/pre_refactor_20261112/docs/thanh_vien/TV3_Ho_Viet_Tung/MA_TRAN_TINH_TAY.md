# TV3 - Hồ Việt Tùng: lọc Lee và cân bằng histogram

## Mục tiêu và liên hệ phần việc

TV3 phụ trách khử nhiễu và tăng tương phản. Hai ví dụ này tách rõ hai nhiệm vụ: Lee làm thay đổi thống kê lân cận, HE thay đổi ánh xạ mức xám. HE là nền tảng để hiểu histogram và CDF, không thay thế phần giải thích CLAHE của dự án. Thành viên cần tự chạy, đổi ma trận và trình bày lại cách tính.

## Ví dụ 1: Lee trên ma trận 5 × 5

```text
A = [100 100 100 100 100
     100 100 100 100 100
     100 100 200 100 100
     100 100 100 100 100
     100 100 100 100 100]
```

Xét cửa sổ 3 × 3 ở tâm. Có tám số 100 và một số 200. Tổng = 1.000, nên mu = 1.000/9 = 111,111... Tổng bình phương = 8×10.000 + 40.000 = 120.000. Phương sai v = 120.000/9 - (1.000/9)² = 80.000/81 = 987,654...

Chọn L = 4. Phương sai nhiễu ước lượng sigma_n² = mu²/L = 250.000/81 = 3.086,420... Trọng số chưa chặn là 1 - sigma_n²/v = 1 - 3,125 = -2,125. Chặn trong [0,1] được K = 0. Đầu ra J = mu + K×(I-mu) = 111,111..., làm tròn thành 111.

Tại một cửa sổ không chứa tâm 200, tất cả phần tử bằng 100: mu = 100, v = 0. Mẫu số dùng max(v,1e-8), K được chặn về 0, nên J = 100. Với đệm reflect, toàn bộ đầu ra là:

```text
J = [100 100 100 100 100
     100 111 111 111 100
     100 111 111 111 100
     100 111 111 111 100
     100 100 100 100 100]
```

Điểm 200 bị làm mờ và ảnh hưởng lan sang hàng xóm. Bài này minh họa cơ chế làm mịn, không chứng minh pixel 200 là nhiễu thật. Cửa sổ 3 × 3 dùng cho tính tay; mặc định ứng dụng là 5 × 5.

## Ví dụ 2: HE trên ma trận 4 × 4

```text
B = [0 1 2 3
     0 1 2 3
     0 1 2 3
     0 1 2 3]
```

Histogram bốn mức là [4,4,4,4]. CDF dạng số đếm là [4,8,12,16]. Dự án dùng CDF-min: lấy CDF đầu tiên khác 0 là 4, rồi LUT(k) = round((CDF(k)-4)/(16-4) × 255).

Tính từng mức: 0 thành 0; 1 thành (8-4)/12×255 = 85; 2 thành 170; 3 thành 255. Đầu ra:

```text
E = [0 85 170 255
     0 85 170 255
     0 85 170 255
     0 85 170 255]
```

Dải mức xám đã trải rộng, nhưng không có quan sát mới về đối tượng. CLAHE còn chia ô, cắt histogram, phân phối phần dư và nội suy giữa các ô; không được gọi phép HE 4 × 4 này là toàn bộ CLAHE.

## Mã kiểm chứng

`vi_du_ma_tran.py` tự cài Lee bằng vòng lặp cửa sổ và HE bằng histogram/CDF. Đã kiểm chứng bằng NumPy: hai đầu ra đúng toàn bộ ma trận kỳ vọng, khớp hàm dự án; HE còn khớp OpenCV. Chạy:

```text
.venv\Scripts\python.exe -X utf8 docs/thanh_vien/TV3_Ho_Viet_Tung/vi_du_ma_tran.py
```

## Câu hỏi để tự bảo vệ

1. K âm có nghĩa gì? Nhiễu ước lượng vượt phương sai quan sát; cài đặt chặn K về 0.
2. Tăng L khi mu, v giữ nguyên tác động gì? Giảm phương sai nhiễu ước lượng, thường tăng K và giữ nhiều giá trị gốc hơn.
3. Vì sao phải đổi sang float trước bình phương? uint8 không đủ miền giá trị để tính 200².
4. Vì sao có CDF-min? Đó là quy ước ánh xạ đang dùng để đưa mức thấp nhất về 0 trong ảnh không hằng; phải đồng bộ khi so với thư viện.
5. HE/CLAHE có luôn giúp mask đúng hơn không? Không; có thể làm rõ cả nhiễu và chi tiết nền.

Nguồn: `src/tv3/filters.py`, `src/tv3/enhancement.py`, `src/tv2/verification.py`.
