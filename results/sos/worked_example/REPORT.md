# Ví dụ số kiểm chứng Lee trên ma trận 5×5

Tái tạo: `python scripts/worked_example.py`. Đây là ma trận tổng hợp phục vụ giải thích, không phải ảnh SAR hoặc chứng cứ về độ chính xác phát hiện dầu.

Ma trận có giá trị 0,2 ở mọi ô, riêng ô giữa là 0,9. Cửa sổ 3×3 ở tâm gồm tám giá trị 0,2 và một giá trị 0,9. Dùng phương sai tổng thể, L=4:

- m = (8×0,2 + 0,9)/9 = 5/18.
- v = (8×0,2² + 0,9²)/9 − m² = 98/2025.
- noise = m²/4 = 25/1296.
- w = max(v−noise,0)/v = 943/1568.
- y = m + w(0,9−m) = 1643/2520 ≈ 0.651984126984.

Code kiểm tra giá trị tâm bằng `Fraction` (số hữu tỉ chính xác), đối chiếu NumPy với công thức này, rồi đối chiếu cả ma trận với bản dùng thống kê SciPy. Sai số tuyệt đối lớn nhất: 1.943e-16; MSE: 6.933e-33. Giá trị các ô còn lại và toàn bộ ma trận đầu ra nằm trong `example.json`.

## Ý nghĩa và giới hạn của công thức

Xét mô hình cục bộ đơn giản Y=X+N, N có trung bình 0 và không tương quan với X. Với ước lượng tuyến tính X̂=m+a(Y−m), sai số bình phương kỳ vọng là (a−1)² Var(X)+a² Var(N). Đạo hàm theo a bằng 0 cho a=Var(X)/(Var(X)+Var(N))=1−Var(N)/Var(Y). Thay các phương sai bằng ước lượng cục bộ và chặn phần âm cho dạng trọng số đang dùng.

Đây là giải thích theo mô hình đơn giản. Nhiễu speckle SAR thường được mô hình hóa dạng nhân; cách thay Var(N) bằng m²/L trong code là một xấp xỉ cục bộ. Dữ liệu PNG không xác minh thang cường độ tuyến tính hoặc số looks vật lý. Vì vậy suy luận trên KHÔNG chứng minh L=4 tối ưu, KHÔNG chứng minh F1 tăng, và KHÔNG chứng minh giữ đúng biên dầu. Các kết luận về SOS phải dựa vào thực nghiệm validation đã lưu.

Ở vùng gần hằng, v≤noise nên w=0: đầu ra là m. Khi v lớn so với noise, w gần 1: đầu ra gần giá trị quan sát. Điểm sáng bất thường cũng có thể làm v tăng; do đó cơ chế này có thể giữ lại cả nhiễu hoặc cấu trúc không phải dầu.

## Liên hệ cài đặt

`core.mean_filter` tính mean và mean bình phương bằng summed-area table; `core.filter_image` tính v=max(E[Y²]−m²,0), noise, w rồi đầu ra. Chuyển sang float trước khi bình phương để tránh tràn uint8; dùng mẫu số max(v,1e−12) để tránh chia 0. Padding reflect không lặp pixel biên. Bản SciPy dùng mode mirror tương ứng; đây là cùng công thức với công cụ tính thống kê khác, không phải một API Lee độc lập.

Với ảnh H×W và cửa sổ k, cách tích phân có thời gian/bộ nhớ O((H+k)(W+k)); khi k nhỏ so với ảnh là O(HW). Cách trượt cửa sổ trực tiếp tính từng trung bình tốn O(HWk²). Khác biệt tối ưu hóa này không làm thay đổi định nghĩa công thức.
