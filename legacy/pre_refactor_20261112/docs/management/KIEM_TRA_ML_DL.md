# Dự án hiện tại có dùng ML/DL không?

**Không dùng ML hoặc deep learning trong pipeline hiện tại.** Kết luận dựa trên mã được kiểm tra trong repo, dependency và đường xử lý thực tế, không chỉ dựa vào tuyên bố README. Đây không phải bảo đảm cho mọi thay đổi trong tương lai.

## Bằng chứng từ mã

| Phần | Phép toán thực tế | Vì sao không phải học mô hình |
| --- | --- | --- |
| `src/tv3/filters.py` | Box/Gaussian/median/bilateral, Lee/Kuan/Frost | Kernel hoặc trọng số tính theo công thức và thống kê ảnh; không tối ưu từ nhãn |
| `src/tv3/enhancement.py` | Log, HE, CLAHE, đồng hình FFT | Ánh xạ mức xám/histogram/tần số; không mạng neuron |
| `src/tv4/edges.py`, `sharpening.py` | Đạo hàm, làm nét, NMS, ngưỡng kép/hysteresis | Kernel cố định và quy tắc nối biên; convolution không đồng nghĩa CNN |
| `src/tv4/morphology.py` | Otsu, erosion/dilation, liên thông, lọc diện tích/tương phản | Quy tắc quyết định đặt trước, ngưỡng tính từ histogram của ảnh hiện tại |
| `src/tv1/pipeline.py` | Gọi các phép toán với `PipelineConfig` | Không nhận nhãn lớp; không fit, loss, optimizer hoặc cập nhật trọng số |
| `src/tv5/experiments.py` | So có/không vùng ứng viên với nhãn thư mục | Nhãn dùng sau xử lý để đánh giá TP/FP/FN/TN, không huấn luyện |

Không thấy import hoặc gọi PyTorch/TensorFlow/Keras/scikit-learn/XGBoost/ONNX trong code thực thi, không thấy file trọng số mô hình trong nội dung dự án được Git quản lý. `scripts/audit_no_ml.py` lưu danh sách import và dấu hiệu cần xem lại; kiểm tra tĩnh bổ trợ việc đọc code, không phải chứng minh hình thức tuyệt đối. `tests/test_numpy_boundary.py` chặn import thư viện đối chứng/ML trong module lõi.

OpenCV dùng I/O/resize và đối chứng; SciPy/skimage phục vụ đối chiếu, không có bước học. NumPy tự nó có thể dùng để viết ML, nhưng code ở đây cài công thức xử lý ảnh. Thống kê mean/variance thích nghi, Otsu tự chọn ngưỡng, khảo sát CLAHE và chỉ số precision/recall **không tự biến bài toán thành ML**.

## Các tên dễ gây hiểu nhầm

- Metadata CSIRO có cụm “for machine learning (Deep Learning)”: đó là tên/mục đích có thể dùng của dataset. Việc dùng ảnh của dataset không bắt buộc dùng phương pháp học.
- Biến `prediction` là kết quả quy tắc `số vùng > 0`; không phải đầu ra một mô hình đã train.
- Hàm kế thừa tên `detect_oil_slick_morphological` trả vùng tối ứng viên. Tên hàm không chứng minh đó là dầu.
- Codex hỗ trợ viết/kiểm tra mã là việc sử dụng công cụ AI trong quá trình phát triển, đã khai báo trong phụ lục C. Thuật toán xử lý ảnh chạy lúc demo không gọi mô hình AI hoặc API AI.

## Tự kiểm tra

```powershell
uv run python scripts/audit_no_ml.py
uv run --extra dev python -m pytest tests/test_numpy_boundary.py -q
```

Giữ phạm vi này khi cải tiến: lọc, histogram, ngưỡng, hình thái, ROI, đo lường và kiểm chứng. Nếu thêm mô hình học hoặc trọng số pretrained sau này phải đổi kết luận và kiểm tra lại yêu cầu BTL.
