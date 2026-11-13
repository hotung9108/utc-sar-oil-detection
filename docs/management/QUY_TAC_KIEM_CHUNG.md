# Quy tắc kiểm chứng

So sánh thuật toán trên cùng split và giao thức; so bản tự cài với API thư viện tương ứng trên cùng đầu vào, dtype, padding và tham số. Báo sai số tuyệt đối lớn nhất/MSE cho đầu ra số, mức đồng thuận cho nhãn và thời gian. Ghi rõ biến thể không tương đương; đối chứng ghép công thức không phải API độc lập.

Chọn mô hình bằng validation, test chỉ dùng đánh giá cuối. Nhãn ảnh, box và mask không thay thế nhau. Nhãn semantic chuyển thành liên thông phải ghi rõ là đối tượng suy ra. PSNR/SSIM cần tham chiếu sạch hợp lệ. Mọi kết luận cải tiến phải có ablation, FP/FN và recall. Giao thức SOS đã khóa tại `../GIAO_THUC_THUC_NGHIEM.md`: IoU đối tượng >=0.5, micro PRF, sai số float atol1e-6/rtol1e-5, cùng định nghĩa padding/chu vi và objective SVM.
