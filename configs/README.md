# Cấu hình

Grid thực nghiệm SOS có một nguồn định nghĩa trong `src/sar_oil/experiments.py` (`FILTERS`, `THRESHOLDS`, `MODELS`, `GROUPS`). Giao thức tại `docs/GIAO_THUC_THUC_NGHIEM.md`.

Split/seed/mask threshold lưu trong `data/manifest.json`. Cấu hình được chọn và checksum manifest lưu trong `results/sos/selected.json`; model NumPy JSON bên cạnh. Không sửa cấu hình sau khi xem test để báo lại kết quả đó như test độc lập.
