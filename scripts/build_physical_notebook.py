"""Build a notebook exposing the measured, separate physical calibration demo."""
from pathlib import Path
import nbformat as nbf

ROOT = Path(__file__).resolve().parents[1]
nb=nbf.v4.new_notebook(cells=[
 nbf.v4.new_markdown_cell('''# 07 — Metadata góc tới và hiệu chuẩn Sentinel-1 thật

Nhánh bổ sung, không thay đổi mô hình SOS. Tile 1.024×1.024 có DN uint16,
góc tới và LUT hiệu chuẩn từ cùng cảnh gốc. Chưa có nhãn dầu cho tile này.
Không dùng kết quả này thay Precision/Recall/F1 trên dữ liệu có nhãn.

Chuẩn bị từ thư mục gốc:
```text
python scripts/fetch_sentinel_metadata.py
python scripts/fetch_sentinel_window.py
python scripts/fetch_scene_wind.py
```
Chỉ đọc cửa sổ nhỏ qua HTTP Range, không tải toàn cảnh 626 MB.
Nguồn và hash: `docs/management/sentinel_window_audit.json`.
'''),
 nbf.v4.new_code_cell('''from pathlib import Path
import sys, json, inspect
from IPython.display import display, Code, Image, Markdown
ROOT=next(p for p in [Path.cwd(), *Path.cwd().parents] if (p/'src/sar_oil').is_dir())
sys.path.insert(0,str(ROOT/'scripts'))
from sentinel_calibration_demo import bilinear_numpy, main
display(Code(inspect.getsource(bilinear_numpy),language='python'))'''),
 nbf.v4.new_markdown_cell('''## Công thức và phép đối chứng

`backscatter = DN² / LUT²`, theo ESA L1 Detailed Algorithm Definition,
công thức 9-53–9-56. Nội suy song tuyến tính NumPy được đối chiếu với
SciPy RegularGridInterpolator trên toàn bộ tile, cùng lưới và cùng biên.
LUT gamma chứa yếu tố hình học góc tới ellipsoid; không đồng nghĩa đã loại
hết ảnh hưởng góc/gió lên tán xạ mặt biển. Xem nguồn đầy đủ trong
`results/physical/README.md`.

Ô dưới thực sự chạy lại hiệu chuẩn và lưu JSON/mảng/biểu đồ; không chỉ đọc số có sẵn.'''),
 nbf.v4.new_code_cell('''main()
result=json.loads((ROOT/'results/physical/calibration.json').read_text())
assert result['allclose_passed']
display(Image(filename=str(ROOT/'results/physical/calibration.png')))'''),
 nbf.v4.new_markdown_cell('''## Giới hạn phải ghi trong báo cáo

- Cả source và demo chưa trừ nhiễu nhiệt.
- Gió ERA5 ghép tại tâm tile là dữ liệu ô lưới thô; chưa có nhãn dầu trên tile.
- Chưa xác nhận ánh xạ tile tới patch JPEG DARTIS hoặc SOS.
- Sai số NumPy–SciPy nhỏ kiểm chứng tính toán, chưa chứng minh gamma tăng F1.
- Chưa đối chiếu toàn bộ với bộ xử lý SAR độc lập như SNAP.
'''),
 nbf.v4.new_markdown_cell('''## Gió ERA5 tại tâm tile

Chọn rõ ERA5, ô lưới gần nhất và tắt downscaling theo độ cao. Nội suy hai
vector u/v tại hai giờ kề thời điểm chụp, không lấy trung bình góc hướng gió.
Đây là gió tái phân tích, không phải đo hiện trường hoặc gió từng pixel SAR.
Nguồn: [Open-Meteo Historical API](https://open-meteo.com/en/docs/historical-weather-api).
'''),
 nbf.v4.new_code_cell('''import hashlib
import matplotlib.pyplot as plt
from datetime import datetime
wind=json.loads((ROOT/'results/physical/wind.json').read_text())
raw_path=ROOT/wind['raw_file']
assert hashlib.sha256(raw_path.read_bytes()).hexdigest()==wind['raw_sha256']
assert wind['scene']==result['scene']
assert wind['annotation_sha256']==next(r['sha256'] for r in result['metadata_files'] if r.get('file','').endswith('/annotation/iw-vv.xml'))
raw=json.loads(raw_path.read_text())
print('SAR time UTC:', wind['sar_center_utc'])
print('ERA5 nearest grid:', wind['returned_grid_lat_lon'], 'distance km:', round(wind['grid_center_distance_km'],3))
print('Interpolated wind m/s:', round(wind['speed_m_s'],4), 'FROM degrees:', round(wind['from_degrees'],3))
fig,ax=plt.subplots(figsize=(9,3))
hours=[datetime.fromisoformat(t).hour for t in raw['hourly']['time']]
ax.plot(hours,raw['hourly']['wind_speed_10m'],marker='.',label='ERA5 hourly')
moment=datetime.fromisoformat(wind['sar_center_utc'])
hour=moment.hour+moment.minute/60+moment.second/3600
ax.scatter([hour],[wind['speed_m_s']],color='red',label='Vector interpolation at SAR time',zorder=3)
ax.set(xlabel='UTC hour, 2019-01-05',ylabel='10 m wind (m/s)',title='Nearest ERA5 grid cell; not pixel-scale observation')
ax.legend(); fig.tight_layout()
plot_path=ROOT/'results/physical/wind.png'
fig.savefig(plot_path,dpi=160); plt.close(fig)
display(Image(filename=str(plot_path)))'''),
])
nb.metadata.kernelspec={'name':'python3','display_name':'Python 3','language':'python'}
p=ROOT/'notebooks/external/07_sentinel_calibration.ipynb'
p.parent.mkdir(parents=True,exist_ok=True)
nbf.validate(nb); nbf.write(nb,p)
print(p.relative_to(ROOT))
