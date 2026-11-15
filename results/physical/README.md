# Kiểm chứng hiệu chuẩn trên một cửa sổ Sentinel-1 gốc

Đây là nhánh thực nghiệm riêng, không thay đổi mô hình hay kết quả SOS.
Đầu vào: một tile VV uint16 1.024 × 1.024 lấy ở tâm cảnh Sentinel-1 mà
DARTIS tham chiếu. `sentinel_window_audit.json` ghi byte range, nguồn và hash.
Tile có cả vùng biển và bờ; chưa có nhãn dầu cho tile này.

## Phép tính và đối chứng

Theo [ESA Sentinel-1 L1 Detailed Algorithm Definition, công thức 9-53–9-56](https://sentiwiki.copernicus.eu/__attachments/1673968/DI-MPC-IPFDPM%20-%20Sentinel-1%20Level%201%20Detailed%20Algorithm%20Definition%202022%20-%202.5.pdf),
cường độ hiệu chuẩn bằng `DN² / LUT²`. LUT sigma và gamma có tính đến hình
học góc tới theo ellipsoid. Nhóm nội suy song tuyến tính bằng NumPy trên lưới
không đều, đối chiếu `scipy.interpolate.RegularGridInterpolator` trên toàn tile.
Đây là đối chiếu phép nội suy và tính toán, chưa phải đối chiếu toàn bộ với SNAP.

Kết quả lưu bằng code trong `calibration.json`:

| Phép đối chiếu NumPy–SciPy | Sai số tuyệt đối lớn nhất |
|---|---:|
| Góc tới, độ | 2,13163e-14 |
| LUT sigma | 3,41061e-13 |
| Sigma0 sau hiệu chuẩn | 5,32907e-15 |
| Gamma0 sau hiệu chuẩn | 1,42109e-14 |

Góc tới tile: 38,628874°–39,245492°. Đối chiếu thêm `sigma0/cos(theta)`
với gamma từ LUT cho chênh lệch tối đa 0,003307 dB; không khẳng định hai cách
đồng nhất vì metadata góc và LUT được lấy mẫu, nội suy khác nhau.

`calibration.png` dùng cùng thang màu dB cho sigma/gamma. Các mảng số thực
được lưu ở `data/sentinel_metadata/<scene>/central_calibrated.npz`.

## Giới hạn

Chưa trừ nhiễu nhiệt; annotation ghi `thermalNoiseCorrectionPerformed=false`.
Đã ghép gió tại tâm tile như bên dưới; chưa có nhãn dầu, chưa ánh xạ tile tới patch DARTIS/SOS.
Gamma loại yếu tố diện tích chiếu hình học; không loại toàn bộ phụ thuộc
tán xạ mặt biển vào góc tới và gió. Không dùng ví dụ này để kết luận tăng F1
hay chọn gamma thay sigma cho pipeline phát hiện dầu.

## Gió tái phân tích tại tâm tile

`scripts/fetch_scene_wind.py` chọn ERA5 qua
[Open-Meteo Historical API](https://open-meteo.com/en/docs/historical-weather-api),
ô lưới gần nhất và không downscaling độ cao. Không dùng mô hình pha trộn mặc định.
Tâm tile nội suy từ annotation: 35,119401°N, 32,466506°E,
thời điểm 2019-01-05 15:49:14,737876 UTC. Ô ERA5 trả về là 35°N, 32,5°E,
cách tâm tile 13,622 km. Đây là lưới tái phân tích 0,25°, không phải đo tại pixel.

15:00 UTC: 3,83 m/s, hướng đến từ 263°; 16:00 UTC: 3,24 m/s, từ 261°.
Nội suy tuyến tính vector u/v cho thời điểm SAR: **3,345419 m/s**, từ **261,410°**.
Hướng không được nội suy như số thực thông thường vì có vòng 0°/360°.
Nguồn API làm tròn tốc độ/hướng; các chữ số sau tính toán không biểu thị độ chính xác đo.
`wind.json` lưu URL, raw hash, thời gian, tọa độ, trọng số và giới hạn.
Chưa dùng gió để chọn ngưỡng hoặc khẳng định một vùng tối là do gió yếu.

## Tái tạo

```text
python scripts/fetch_sentinel_metadata.py
python scripts/fetch_sentinel_window.py
python scripts/sentinel_calibration_demo.py
python scripts/fetch_scene_wind.py
python -m unittest discover -s tests
```
