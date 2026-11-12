# TV5 - Phạm Minh Tuấn: đọc đúng chỉ số chất lượng ảnh

## Mục tiêu và liên hệ phần việc

TV5 phụ trách đánh giá. Bài này dùng hai ma trận cho trước để tự cài các phép đo bằng NumPy. B là một ảnh so sánh minh họa, không phải kết quả Lee hay CLAHE đã được khẳng định. Cần học cách đọc chỉ số mà không suy diễn thành phát hiện dầu đúng.

## Hai ma trận 4 × 4

```text
A = [0 0 2 2      B = [0 1 1 2
     0 0 2 2           0 1 1 2
     0 0 2 2           0 1 1 2
     0 0 2 2]          0 1 1 2]
```

## Trung bình, RMS contrast và AMBE

Mỗi hàng A có tổng 4, mỗi hàng B cũng có tổng 4. Cả hai trung bình đều bằng 16/16 = 1. Do đó AMBE = |mean(B)-mean(A)| = 0. Điều này chỉ nói độ sáng trung bình không đổi, không nói mọi pixel không đổi.

Ở A, mỗi hàng lệch khỏi trung bình thành [-1,-1,1,1]. Tổng bình phương sai lệch toàn ảnh là 16, phương sai = 1 và RMS contrast = sqrt(1) = 1. Ở B, mỗi hàng lệch thành [-1,0,0,1]. Tổng bình phương là 8, phương sai = 0,5 và RMS contrast = sqrt(0,5) ≈ 0,707107. Dùng phương sai tổng thể, tức chia cho 16, phù hợp mã dự án.

## MSE giữa hai ảnh

Mỗi hàng A-B là [0,-1,1,0]. Tổng bình phương mỗi hàng là 2; toàn ảnh là 8. MSE = 8/16 = 0,5. Phải chuyển sang float trước khi trừ để tránh tràn số uint8. MSE ở đây đo mức thay đổi giữa hai ảnh; A không phải ảnh sạch chuẩn, nên không được gọi đây là sai số khôi phục đối với chân lý.

## Entropy và SSI

A có hai mức với xác suất [0,5;0,5]. H(A) = -2×0,5×log2(0,5) = 1 bit. B có ba mức với xác suất [0,25;0,5;0,25]. H(B) = 0,5 + 0,5 + 0,5 = 1,5 bit. Entropy tăng trong khi RMS giảm: hai chỉ số mô tả những khía cạnh khác nhau, không thể dùng một chiều “càng lớn càng tốt” cho tất cả.

SSI = (std(B)/mean(B))/(std(A)/mean(A)) = (sqrt(0,5)/1)/(1/1) = 0,707107. Nó nói hệ số biến thiên giảm, chưa chứng minh nhiễu thật đã được loại mà chi tiết thật vẫn giữ nguyên.

## Mã kiểm chứng

`vi_du_ma_tran.py` tự tính trung bình, RMS, AMBE, MSE, entropy và SSI. Đã kiểm chứng bằng NumPy: kết quả khớp các giá trị tính tay với sai số tối đa trong ngưỡng 1e-12; các chỉ số tương ứng khớp module dự án. Chạy:

```text
.venv\Scripts\python.exe -X utf8 docs/thanh_vien/TV5_Pham_Minh_Tuan/vi_du_ma_tran.py
```

## Câu hỏi để tự bảo vệ

1. AMBE = 0 có nghĩa hai ảnh giống nhau không? Không, ví dụ này có MSE = 0,5.
2. Entropy cao hơn có chắc chất lượng tốt hơn không? Không; nhiễu cũng có thể làm histogram đa dạng hơn.
3. Vì sao dùng float trước A-B? uint8 không biểu diễn số âm đúng cho phép đo sai số.
4. Có thể dùng MSE(A,B) làm độ chính xác mask không? Không, đây là hai ảnh mức xám, không có mask chuẩn.
5. Precision/recall có đòi hỏi ML không? Không. Chúng là phép đếm đúng/sai của quyết định so với nhãn, cũng dùng được cho quy tắc cố định.

Nguồn: `src/tv5/metrics.py`. Tập bài này dùng các phép đo ảnh; đánh giá cấp ảnh của toàn tập là một thí nghiệm khác.
