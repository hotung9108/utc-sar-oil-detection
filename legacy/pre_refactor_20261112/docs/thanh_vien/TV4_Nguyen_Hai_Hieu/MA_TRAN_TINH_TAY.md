# TV4 - Nguyễn Hải Hiếu: Sobel và biên hình thái

## Mục tiêu và liên hệ phần việc

TV4 cần phân biệt biên từ biến thiên mức xám với biên trích từ mask. Hai ví dụ dùng ma trận 5 × 5, có đầu ra tính tay để kiểm tra mã NumPy. Đây là bài tập chuẩn bị để thành viên tự thực hiện và giải thích.

## Ví dụ 1: Sobel trên một bước sáng tối

```text
A = [0 0 100 100 100
     0 0 100 100 100
     0 0 100 100 100
     0 0 100 100 100
     0 0 100 100 100]

Kx = [-1 0 1     Ky = [-1 -2 -1
      -2 0 2            0  0  0
      -1 0 1]           1  2  1]
```

Tại tâm (2,2), cửa sổ 3 × 3 có mỗi hàng [0,100,100]. Gx = (-1×0 + 1×100) + (-2×0 + 2×100) + (-1×0 + 1×100) = 400. Gy bằng tổng hàng dưới có trọng số trừ hàng trên có trọng số, nên bằng 0 vì các hàng giống nhau. Độ lớn gradient = sqrt(400² + 0²) = 400.

Chỉ xét chín vị trí bên trong để không lẫn quy ước đệm biên. Đầu ra tính tay:

```text
Gx = [400 400 0     Gy = [0 0 0
      400 400 0           0 0 0
      400 400 0]          0 0 0]
```

Vì độ lớn có thể lớn hơn 255, phải giữ float khi tính. Hàm Sobel dự án trả cả Gx/Gy float và ảnh độ lớn đã chặn 0–255 để hiển thị. Không đem ảnh đã chặn đó thay cho gradient float trong các bước cần độ lớn thực như Canny.

## Ví dụ 2: biên hình thái từ mask

Ký hiệu 1 tương ứng 255 trong mã:

```text
B = [0 0 0 0 0
     0 1 1 1 0
     0 1 1 1 0
     0 1 1 1 0
     0 0 0 0 0]
```

Co bằng kernel vuông 3 × 3. Một pixel chỉ được giữ nếu toàn bộ cửa sổ của nó thuộc vùng trắng. Chỉ pixel giữa (2,2) có đủ chín pixel trắng xung quanh. Vậy erosion có một pixel trắng. Biên B trừ erosion là:

```text
Erosion = [0 0 0 0 0    Boundary = [0 0 0 0 0
           0 0 0 0 0                0 1 1 1 0
           0 0 1 0 0                0 1 0 1 0
           0 0 0 0 0                0 1 1 1 0
           0 0 0 0 0]               0 0 0 0 0]
```

Mask có diện tích 9 pixel; biên có 8 pixel. Đây là ví dụ cụ thể vì sao đếm pixel biên không phải diện tích vùng. Biên hình thái phụ thuộc mask đã tạo trước, còn Sobel phản ứng trực tiếp với mức xám.

## Mã kiểm chứng

`vi_du_ma_tran.py` tự cài tương quan Sobel ở miền trong và phép co nhị phân. Đã kiểm chứng bằng NumPy: Gx/Gy, erosion và boundary khớp đáp án tính tay, đồng thời khớp hàm dự án trên phạm vi tương ứng. Chạy:

```text
.venv\Scripts\python.exe -X utf8 docs/thanh_vien/TV4_Nguyen_Hai_Hieu/vi_du_ma_tran.py
```

## Câu hỏi để tự bảo vệ

1. Vì sao Gy = 0? Không có thay đổi theo chiều hàng trong ví dụ.
2. Gx = 400 có phải cường độ pixel đầu vào không? Không, đó là đáp ứng toán tử đạo hàm.
3. Vì sao chỉ so miền trong 3 × 3? Để tách phép tính kernel khỏi lựa chọn đệm ảnh; muốn kiểm chứng toàn ảnh phải kiểm tra cả đệm.
4. Mask có lỗ thì phép B trừ erosion có thể vẽ quanh lỗ không? Có.
5. Biên có chứng minh dầu không? Không; nó chỉ chỉ ra biến thiên mức xám hoặc ranh giới của một mask.

Nguồn: `src/tv4/edges.py`, `src/tv4/morphology.py`.
