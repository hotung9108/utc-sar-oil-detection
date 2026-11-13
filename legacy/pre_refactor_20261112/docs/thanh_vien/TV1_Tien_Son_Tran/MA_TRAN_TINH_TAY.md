# TV1 - Tiến Sơn Trần: từ ảnh xám đến mask và diện tích

## Mục tiêu và liên hệ phần việc

TV1 phụ trách tích hợp pipeline và giao diện. Bài này minh họa hợp đồng dữ liệu: ảnh xám đi vào, mask đi ra, rồi giao diện đếm diện tích và hiển thị. Đây là bài tập độc lập dùng ngưỡng cố định, chưa phải toàn bộ pipeline Otsu, hình thái và lọc tương phản của dự án. Mỗi thành viên cần tự chạy, giải thích và đổi ma trận; tài liệu chuẩn bị này không xác nhận rằng thành viên đã tự hoàn thành bài.

## Ma trận đầu vào 4 × 4

```text
A = [ 10  10 100 100
      10  10 100 100
     100 100 100 100
     100 100 100 100 ]
```

Mỗi phần tử là một mức xám uint8. Có 16 pixel; bốn pixel góc trên trái tối hơn nền. Đặt t = 50. Quy tắc: B(y,x) = 255 nếu A(y,x) ≤ t, ngược lại bằng 0. Màu trắng trong mask đánh dấu vùng tối của ảnh nguồn, không phải vùng sáng ngoài thực tế.

## Tính từng bước

Tại (0,0), 10 ≤ 50 nên B(0,0) = 255. Tại (0,2), 100 > 50 nên B(0,2) = 0. Làm tương tự cho 16 phần tử:

```text
B = [255 255   0   0
     255 255   0   0
       0   0   0   0
       0   0   0   0 ]
```

Diện tích = số phần tử khác 0 = 4 pixel. Phần trăm = 4/16 × 100 = 25%. Không dùng tổng B = 1.020 làm diện tích, vì mỗi pixel được mã hóa bằng 255. Nếu dùng tổng thì phải chia 255, nhưng đếm phần tử khác 0 dễ kiểm soát hơn.

Để minh họa hiển thị, đổi ảnh xám sang RGB bằng cách lặp ba kênh. Pixel 100 thành (100,100,100). Với pixel thuộc mask, đặt (255,0,0) để tô đỏ. Ở bài tập này tô kín vùng; ứng dụng thật tô đường biên hình thái, nên không được gọi hai hình này là một.

## Tham số và giới hạn

Nếu t = 9 thì không pixel nào được chọn. Nếu t = 10 thì vẫn chọn bốn pixel vì có dấu bằng. Nếu t = 100 thì chọn cả 16 pixel. Những kết quả này cho thấy chọn ngưỡng quyết định diện tích; không có quy tắc nào ở đây xác nhận dầu.

## Mã kiểm chứng

Tệp `vi_du_ma_tran.py` cạnh tài liệu chứa cài đặt NumPy và ma trận đầu ra kỳ vọng viết sẵn. Đã kiểm chứng bằng NumPy: mask đúng từng phần tử, diện tích 4, phần trăm 25, màu của pixel trong/ngoài mask đúng. Chạy từ gốc dự án:

```text
.venv\Scripts\python.exe -X utf8 docs/thanh_vien/TV1_Tien_Son_Tran/vi_du_ma_tran.py
```

## Câu hỏi để tự bảo vệ

1. Vì sao dấu ≤ khác dấu <? Với t = 10, dấu < sẽ bỏ toàn bộ bốn pixel tối.
2. Vì sao đếm biên không phải tính diện tích? Biên chỉ chứa đường viền; mask chứa phần vùng được chọn.
3. Vì sao ảnh trắng đen của mask không phải ảnh xám sau lọc? Nó chỉ lưu quyết định thuộc/không thuộc vùng.
4. Chuyển 25% sang mét vuông được không? Chưa được nếu không biết diện tích mặt đất mỗi pixel.
5. Bài tập đã mô phỏng toàn bộ hệ thống chưa? Chưa; nó chỉ minh họa phân ngưỡng và tích hợp đầu ra.

Nguồn đối chiếu: `src/tv1/pipeline.py`, `src/tv4/morphology.py`. Trong pipeline thực tế, ngưỡng được lựa chọn tự động, có thể dùng reference và còn các bước lọc vùng.
