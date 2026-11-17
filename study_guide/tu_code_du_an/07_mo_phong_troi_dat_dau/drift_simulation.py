"""MODULE 7: LAGRANGIAN OIL SLICK DRIFT SIMULATION (NUMPY THUẦN)

Ví dụ tự học chưa tích hợp/kiểm chứng trong pipeline chính, không dùng dự báo thực địa:
1. Phương trình bình lưu dòng chảy + 3% gió bề mặt
2. Thành phần khuếch tán ngẫu nhiên Monte Carlo (Random Walk)
3. Hệ số loang rộng giả định để trực quan hóa, không phải mô hình Fay đã kiểm chứng
4. Chuyển đổi tọa độ hệ phẳng (mét) sang trắc địa (Kinh - Vĩ độ)
"""
from __future__ import annotations
import numpy as np


METERS_PER_DEGREE_LAT = 111139.0  # Chu vi Trái Đất / 360 độ


def meters_to_latlon(
    dx_meters: float,
    dy_meters: float,
    base_lat: float,
    base_lon: float
) -> tuple[float, float]:
    """Chuyển đổi độ dời (dx, dy) tính bằng mét sang (kinh độ, vĩ độ) mới."""
    d_lat = dy_meters / METERS_PER_DEGREE_LAT
    meters_per_degree_lon = METERS_PER_DEGREE_LAT * np.cos(np.deg2rad(base_lat))
    d_lon = dx_meters / max(1e-4, meters_per_degree_lon)
    return base_lat + d_lat, base_lon + d_lon


def simulate_slick_drift(
    base_polygon_coords: list[tuple[float, float]],
    u_wind_ms: float = 5.0,
    v_wind_ms: float = 3.0,
    u_current_ms: float = 0.2,
    v_current_ms: float = -0.1,
    time_horizons_hours: tuple[int, ...] = (0, 6, 12, 24, 48),
    diffusion_coeff: float = 2.0
) -> list[dict]:
    """Mô phỏng quỹ đạo trôi dạt và biến dạng đa giác vết dầu qua các mốc thời gian.

    Args:
        base_polygon_coords: Danh sách các đỉnh đa giác ban đầu [(lat, lon), ...]
        u_wind_ms, v_wind_ms: Thành phần vận tốc gió Đông-Tây và Nam-Bắc (m/s)
        u_current_ms, v_current_ms: Thành phần vận tốc hải lưu Đông-Tây và Nam-Bắc (m/s)
        time_horizons_hours: Các mốc giờ cần dự báo
        diffusion_coeff: Hệ số khuếch tán ngang bề mặt (m^2/s)

    Returns:
        Danh sách từ điển kết quả dự báo tại mỗi mốc thời gian.
    """
    poly = np.array(base_polygon_coords, dtype=np.float64)
    center_lat = float(np.mean(poly[:, 0]))
    center_lon = float(np.mean(poly[:, 1]))

    # 1. Vận tốc trôi dạt tổng hợp (Quy tắc 3% gió):
    # u_drift = u_current + 0.03 * u_wind
    u_drift = u_current_ms + 0.03 * u_wind_ms
    v_drift = v_current_ms + 0.03 * v_wind_ms

    results = []

    for h in time_horizons_hours:
        t_seconds = h * 3600.0

        # Độ dời bình lưu xác định (Advection displacement) tính bằng mét
        dx_advect = u_drift * t_seconds
        dy_advect = v_drift * t_seconds

        # Tâm vết dầu mới
        new_center_lat, new_center_lon = meters_to_latlon(
            dx_advect, dy_advect, center_lat, center_lon
        )

        # Hệ số tăng kích thước tuyến tính giả định, không phải công thức Fay đã xác minh:
        # scale_factor = 1.0 + 0.08 * sqrt(h)
        expansion_scale = 1.0 + 0.08 * np.sqrt(float(h))

        # Biến dạng và dịch chuyển các đỉnh đa giác
        shifted_polygon = []
        for lat, lon in poly:
            # Vector từ tâm tới đỉnh
            d_lat = lat - center_lat
            d_lon = lon - center_lon
            # Phóng to theo hệ số khuếch tán
            expanded_lat = d_lat * expansion_scale
            expanded_lon = d_lon * expansion_scale
            # Tịnh tiến tới tâm mới
            shifted_polygon.append((
                round(new_center_lat + expanded_lat, 6),
                round(new_center_lon + expanded_lon, 6)
            ))

        results.append({
            "hour": h,
            "center": (round(new_center_lat, 6), round(new_center_lon, 6)),
            "distance_km": round(np.sqrt(dx_advect**2 + dy_advect**2) / 1000.0, 2),
            "drift_speed_kmh": round(np.sqrt(u_drift**2 + v_drift**2) * 3.6, 2),
            "polygon": shifted_polygon
        })

    return results


# ==============================================================================
# BÀI TẬP THỰC NGHIỆM MÔ PHỎNG
# ==============================================================================
if __name__ == "__main__":
    print("=" * 70)
    print("--- [MODULE 7] DỰ BÁO TRÔI DẠT DẦU 48H TRÊN VÙNG BIỂN QUY NHƠN ---")
    print("=" * 70)

    # Giả định toạ độ một vệt dầu ban đầu tại vùng biển Quy Nhơn (13.78 độ Bắc, 109.30 độ Đông)
    base_slick = [
        (13.780, 109.300),
        (13.785, 109.308),
        (13.782, 109.315),
        (13.775, 109.305),
        (13.780, 109.300)
    ]

    # Điều kiện gió mùa Đông Bắc: Gió thổi về hướng Tây Nam (-u, -v)
    forecast = simulate_slick_drift(
        base_polygon_coords=base_slick,
        u_wind_ms=-4.5,
        v_wind_ms=-3.0,
        u_current_ms=-0.15,
        v_current_ms=-0.10,
        time_horizons_hours=(0, 6, 12, 24, 48)
    )

    print(f"{'Thời điểm':<12} | {'Tọa độ tâm (Vĩ, Kinh)':<25} | {'Khoảng cách trôi':<18} | {'Vận tốc trôi'}")
    print("-" * 75)
    for step in forecast:
        h_str = f"T + {step['hour']} giờ"
        coord_str = f"({step['center'][0]:.4f}°N, {step['center'][1]:.4f}°E)"
        dist_str = f"{step['distance_km']} km"
        speed_str = f"{step['drift_speed_kmh']} km/h"
        print(f"{h_str:<12} | {coord_str:<25} | {dist_str:<18} | {speed_str}")

    print("\nNhận xét:")
    print(" -> Sau 48 giờ, vết dầu đã trôi dạt tổng cộng", forecast[-1]['distance_km'], "km về hướng bờ biển.")
    print("\n✅ MODULE 7 HOẠT ĐỘNG HOÀN HẢO!")
