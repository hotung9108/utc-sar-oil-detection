"""Invert the Sentinel geolocation grid for one labelled map tile.

Numerical agreement is not independent geolocation accuracy or SNAP equivalence.
No classifier is trained and no detection metrics are selected here.
"""

import sys as _sys
from pathlib import Path as _Path
_project_root = _Path(__file__).resolve().parents[2]
_sys.path.insert(0, str(_project_root))
_sys.path.insert(0, str(_project_root / "src"))

import hashlib
import json
import xml.etree.ElementTree as ET
from pathlib import Path

import numpy as np
from scipy.interpolate import RegularGridInterpolator
from scipy.optimize import least_squares

from scripts.cantarell.audit_cantarell_source import REVISION, ROOT


def interpolate(y, x, values, rows, cols):
    """Paired coordinates, bilinear value and analytic derivatives, NumPy only."""
    iy = np.clip(np.searchsorted(y, rows, side='right') - 1, 0, len(y) - 2)
    ix = np.clip(np.searchsorted(x, cols, side='right') - 1, 0, len(x) - 2)
    dy, dx = y[iy+1] - y[iy], x[ix+1] - x[ix]
    a, b = (rows-y[iy])/dy, (cols-x[ix])/dx
    v00, v01 = values[iy, ix], values[iy, ix+1]
    v10, v11 = values[iy+1, ix], values[iy+1, ix+1]
    value = (1-a)*((1-b)*v00+b*v01) + a*((1-b)*v10+b*v11)
    dr = ((1-b)*(v10-v00)+b*(v11-v01))/dy
    dc = ((1-a)*(v01-v00)+a*(v11-v10))/dx
    return value, dr, dc


def main():
    cache = ROOT / '.cache/cantarell_source' / REVISION
    audit_path = ROOT / 'docs/management/cantarell_source_audit.json'
    audit = json.loads(audit_path.read_text(encoding='utf-8'))
    for receipt in audit['receipts']:
        path = cache / receipt['path']
        if receipt.get('verified_against_lfs_pointer'):
            path = path.with_name(path.name + '.lfs-object')
        if hashlib.sha256(path.read_bytes()).hexdigest() != receipt['sha256']:
            raise ValueError(f'Source hash mismatch: {path}')
    xml = ET.parse(cache / 'source/iw-vv.xml')
    points = xml.findall('.//geolocationGridPoint')
    y = np.array(sorted({int(p.findtext('line')) for p in points}))
    x = np.array(sorted({int(p.findtext('pixel')) for p in points}))
    fields = {}
    for name in ('latitude', 'longitude', 'incidenceAngle'):
        mapping = {(int(p.findtext('line')), int(p.findtext('pixel'))): float(p.findtext(name)) for p in points}
        if len(mapping) != len(y)*len(x):
            raise ValueError('Nonrectangular source grid')
        fields[name] = np.array([[mapping[(r, c)] for c in x] for r in y])
    import tifffile
    with tifffile.TiffFile(cache / 'RASTER/IMG-TIFF/16-BIT/IMG_01_TILE_001.tiff.lfs-object') as tif:
        page = tif.pages[0]
        shape = page.shape
        scale, tie = page.tags['ModelPixelScaleTag'].value, page.tags['ModelTiepointTag'].value
    rr, cc = np.indices(shape)
    target_lon = (tie[3]+(cc+.5-tie[0])*scale[0]).ravel()
    target_lat = (tie[4]-(rr+.5-tie[1])*scale[1]).ravel()
    rows = np.full(target_lat.shape, float(np.median(y)))
    cols = np.full(target_lat.shape, float(np.median(x)))
    for iteration in range(20):
        lat, a, b = interpolate(y, x, fields['latitude'], rows, cols)
        lon, c, d = interpolate(y, x, fields['longitude'], rows, cols)
        det = a*d-b*c
        if np.any(np.abs(det) < 1e-16):
            raise ValueError('Singular geolocation Jacobian')
        e, f = lat-target_lat, lon-target_lon
        dr, dc = (d*e-b*f)/det, (a*f-c*e)/det
        rows -= dr
        cols -= dc
        if max(np.max(np.abs(dr)), np.max(np.abs(dc))) < 1e-7:
            break
    else:
        raise ValueError('Inverse geolocation did not converge')
    if rows.min() < y[0] or rows.max() > y[-1] or cols.min() < x[0] or cols.max() > x[-1]:
        raise ValueError('Tile outside geolocation interpolation support')
    query = np.column_stack((rows, cols))
    reference = {name: RegularGridInterpolator((y, x), value, bounds_error=True)
                 for name, value in fields.items()}
    errors = {}
    for name in fields:
        ours = interpolate(y, x, fields[name], rows, cols)[0]
        theirs = reference[name](query)
        errors[name] = float(np.max(np.abs(ours-theirs)))
        if not np.allclose(ours, theirs, rtol=1e-12, atol=1e-12):
            raise ValueError('NumPy and SciPy interpolation differ')
    inverse_checks = []
    for row in (0, shape[0]//2, shape[0]-1):
        for col in (0, shape[1]//2, shape[1]-1):
            index = row*shape[1]+col
            target = np.array([target_lat[index], target_lon[index]])
            def residual(pos):
                return np.array([reference['latitude']([pos])[0], reference['longitude']([pos])[0]])-target
            solved = least_squares(residual, [np.median(y), np.median(x)],
                                   bounds=([y[0], x[0]], [y[-1], x[-1]]),
                                   xtol=1e-13, ftol=1e-13, gtol=1e-13)
            difference = float(np.max(np.abs(solved.x-query[index])))
            if not solved.success or difference > 1e-4:
                raise ValueError('Independent inverse solver mismatch')
            inverse_checks.append({'tile_row_col': [row, col], 'max_abs_native_pixel_error': difference})
    lat_back = reference['latitude'](query)
    lon_back = reference['longitude'](query)
    angle = interpolate(y, x, fields['incidenceAngle'], rows, cols)[0].reshape(shape)
    output = cache / 'native_mapping.npz'
    np.savez_compressed(output, native_line=rows.reshape(shape), native_pixel=cols.reshape(shape), incidence_degrees=angle)
    result = {
        'source_audit_sha256': hashlib.sha256(audit_path.read_bytes()).hexdigest(),
        'script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'sample': 'IMG_01_TILE_001', 'shape': list(shape), 'iterations': iteration+1,
        'native_line_range': [float(rows.min()), float(rows.max())],
        'native_pixel_range': [float(cols.min()), float(cols.max())],
        'incidence_range': [float(angle.min()), float(angle.max())],
        'numpy_scipy_forward_max_abs_errors': errors,
        'scipy_inverse_checks': inverse_checks,
        'roundtrip_max_abs_degrees': {'latitude': float(np.max(np.abs(lat_back-target_lat))),
                                      'longitude': float(np.max(np.abs(lon_back-target_lon)))},
        'mapping_file': output.relative_to(ROOT).as_posix(),
        'mapping_sha256': hashlib.sha256(output.read_bytes()).hexdigest(),
        'limits': ['Bilinear geolocation approximation, not range-Doppler terrain correction.',
                   'Solver agreement measures numerical consistency, not independent geolocation accuracy.',
                   'No native imagery fetched or intensity/polarization match established by this script.',
                   'No detection metrics or claim of calibration benefit.']}
    (ROOT / 'docs/management/cantarell_mapping_audit.json').write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
