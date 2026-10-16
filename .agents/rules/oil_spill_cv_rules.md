# Rule: SAR Oil Spill Computer Vision Directives & Heuristics
# Scope: Project-wide guidelines for De 18 (XLA - UTC)

> [!IMPORTANT]
> ### 🚨 CHỈ THỊ BẮT BUỘC:
> 1. **CHỈ SỬ DỤNG THUẬT TOÁN COMPUTER VISION THUẦN TÚY (PURE COMPUTER VISION)**:
>    - Tuyệt đối chưa huấn luyện Model hay chạy Machine Learning / Deep Learning ở giai đoạn hiện tại.
>    - Tập trung 100% vào các kỹ thuật xử lý ảnh: Lọc nhiễu đốm Speckle (Lee, Frost, Wiener), chuẩn hóa dải động, phân ngưỡng thích nghi (Sauvola, Niblack, Otsu), hình thái học toán học (Opening, Closing, Fill holes, bwareaopen).
> 2. **HỖ TRỢ SONG SONG MATLAB VÀ PYTHON**:
>    - Hỗ trợ đầy đủ các hàm MATLAB (`.m`) chuẩn Image Processing Toolbox và Python (`cv2`, `scipy`, `numpy`, `skimage`).
> 3. **PHÁT HIỆN DỰA TRÊN ĐẶC TRƯNG HÌNH THÁI (HEURISTIC / RULE-BASED CV)**:
>    - Nhận diện đốm tối nghi vấn dầu tràn dựa trên các chỉ số hình học & tương phản: Độ thuôn dài ($Elongation \ge 2.0$), Tỉ số tương phản nền biển ($Damping \ge 1.35$), Gradient biên Sobel sắc nét ($\overline{G}_{border}$), Độ phức tạp biên ($Complexity$).
> 4. **TRỰC QUAN HÓA KẾT QUẢ**:
>    - Xuất ảnh so sánh trực quan 4 bước: [Ảnh gốc] -> [Lọc nhiễu] -> [Mặt nạ nhị phân] -> [Khoanh vùng vết dầu với Bounding box/Contours].
