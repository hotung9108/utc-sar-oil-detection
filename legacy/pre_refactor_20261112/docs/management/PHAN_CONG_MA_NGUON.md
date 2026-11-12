# Phân công mã nguồn theo TV1–TV5

Đây là phân công trách nhiệm từ phiên bản hiện tại, không phải xác nhận tác giả lịch sử. Đề kết hợp SAR đã được người dùng xác nhận đăng ký; không bổ sung ML/DL.

| Vai trò / họ tên | GitHub từ collaborators | Nơi triển khai | Trách nhiệm |
| --- | --- | --- | --- |
| TV1 — Trưởng nhóm — Tiến Sơn Trần | `Maloque18705` | `streamlit_app.py`, `src/tv1/` | Demo Streamlit, pipeline, cấu hình, kiểm tra đầu vào và tích hợp |
| TV2 — Lương Tiến Dũng | `ltdungg` | `src/tv2/` | Ví dụ tính tay, đối chiếu thư viện, giải thích sai khác |
| TV3 — Hồ Việt Tùng | `hotung9108` | `src/tv3/` | Lọc không gian/SAR, HE, CLAHE, log và đồng hình |
| TV4 — Nguyễn Hải Hiếu | `hina-kasumi` | `src/tv4/` | Làm nét, Sobel/Prewitt/Roberts/LoG/Canny, Otsu, hình thái và liên thông |
| TV5 — Phạm Minh Tuấn | `tuanpham21105` | `src/tv5/`, các entrypoint thực nghiệm | Dữ liệu, chỉ số, thực nghiệm và thống kê |

Các module `src/filters.py`, `src/edges.py`, v.v. là lớp import tương thích; thuật toán chỉ có một bản triển khai trong thư mục phụ trách. Không phân công bằng cách sao chép thuật toán thành nhiều bản.

Mã lõi TV3/TV4 và tính chỉ số TV5 không gọi OpenCV/SciPy. NumPy FFT là phép toán số dùng trong lọc đồng hình, không phải API lọc ảnh đóng gói. TV1 dùng OpenCV để đọc/ghi, chuyển ảnh xám và resize đầu vào demo; TV2 dùng thư viện làm đối chứng.

Mỗi thành viên cần giải thích được mã mình phụ trách và chuỗi dữ liệu đi qua các phần còn lại. Họ tên đã được nhóm cung cấp; MSSV, điểm và đóng góp thực tế vẫn để trống. Xem [tài liệu cá nhân](../thanh_vien/README.md) và [dữ liệu thành viên dùng chung](thanh_vien.json).
