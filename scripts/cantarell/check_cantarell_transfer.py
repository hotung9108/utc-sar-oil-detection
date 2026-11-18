"""Execute the committed second-tile registration protocol without using labels."""

import sys as _sys
from pathlib import Path as _Path
_project_root = _Path(__file__).resolve().parents[2]
_sys.path.insert(0, str(_project_root))
_sys.path.insert(0, str(_project_root / "src"))

import json
import math
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.request import urlopen

import numpy as np
import tifffile
from scipy.interpolate import RegularGridInterpolator
from scipy.ndimage import shift as shift_image


from scripts._provenance import source_matches
from scripts._paths import resolve_path
from scripts.cantarell.audit_cantarell_source import ROOT, REVISION, BASE
from scripts.cantarell.check_cantarell_registration import register, stats, sha
from scripts.physical.fetch_sentinel_window import RangeReader
from scripts.cantarell.map_cantarell_native_grid import interpolate


def main():
    protocol_path = ROOT / 'docs/management/cantarell_registration_protocol.json'
    protocol = json.loads(protocol_path.read_text())
    if protocol['repository_revision'] != REVISION:
        raise ValueError('Protocol revision mismatch')
    cache = ROOT / '.cache/cantarell_source' / REVISION
    work = cache / protocol['check_sample']
    work.mkdir(exist_ok=True)
    source_path = ROOT / 'docs/management/cantarell_source_audit.json'
    source = json.loads(source_path.read_text())
    # Verify all reused assets, including native metadata and development TIFF.
    for item in source['receipts']:
        path = cache / item['path']
        if item.get('verified_against_lfs_pointer'):
            path = path.with_name(path.name + '.lfs-object')
        if (not source_matches(path, item['sha256'], sha(path))):
            raise ValueError(f'Cached source changed: {path}')
    asset_path = f"RASTER/IMG-TIFF/16-BIT/{protocol['check_sample']}.tiff"
    pointer = work / 'exported.lfs'
    if not pointer.exists():
        with urlopen(BASE + asset_path, timeout=45) as response:
            raw = response.read(1025)
        if not raw.startswith(b'version https://git-lfs.github.com/spec/v1') or len(raw) > 1024:
            raise ValueError('Expected bounded LFS pointer')
        pointer.write_bytes(raw)
    fields = dict(line.split(' ', 1) for line in pointer.read_text().splitlines())
    expected, size = fields['oid'].removeprefix('sha256:'), int(fields['size'])
    if size > 20_000_000:
        raise ValueError('Exported TIFF exceeds budget')
    exported_path = work / 'exported.tiff'
    url = f'https://media.githubusercontent.com/media/Garcia-INPE/oilspill-detection-dataset/{REVISION}/{asset_path}'
    if not exported_path.exists():
        with urlopen(url, timeout=45) as response:
            raw = response.read(size+1)
        exported_path.write_bytes(raw)
    if exported_path.stat().st_size != size or (not source_matches(exported_path, expected, sha(exported_path))):
        raise ValueError('LFS payload hash/size mismatch')

    def read_tiff(path):
        with tifffile.TiffFile(path) as tif:
            p = tif.pages[0]
            pixels = p.asarray().astype(float)
            scale, tie = p.tags['ModelPixelScaleTag'].value, p.tags['ModelTiepointTag'].value
            if p.tags['GeoAsciiParamsTag'].value != 'WGS 84|':
                raise ValueError('Unexpected map CRS')
        h, w = pixels.shape
        bounds = [tie[3]-tie[0]*scale[0], tie[4]-(h-tie[1])*scale[1],
                  tie[3]+(w-tie[0])*scale[0], tie[4]+tie[1]*scale[1]]
        rr, cc = np.indices(pixels.shape)
        lon = (tie[3]+(cc+.5-tie[0])*scale[0]).ravel()
        lat = (tie[4]-(rr+.5-tie[1])*scale[1]).ravel()
        return pixels, bounds, lat, lon

    exported, bounds, target_lat, target_lon = read_tiff(exported_path)
    _, dev_bounds, _, _ = read_tiff(cache / f"RASTER/IMG-TIFF/16-BIT/{protocol['development_sample']}.tiff.lfs-object")
    overlap = max(0, min(bounds[2], dev_bounds[2])-max(bounds[0], dev_bounds[0])) * max(0, min(bounds[3], dev_bounds[3])-max(bounds[1], dev_bounds[1]))
    overlap_fraction = overlap/((bounds[2]-bounds[0])*(bounds[3]-bounds[1]))
    points = ET.parse(cache / 'source/iw-vv.xml').findall('.//geolocationGridPoint')
    y = np.array(sorted({int(p.findtext('line')) for p in points}))
    x = np.array(sorted({int(p.findtext('pixel')) for p in points}))
    grids = {}
    for name in ('latitude', 'longitude'):
        lookup = {(int(p.findtext('line')), int(p.findtext('pixel'))): float(p.findtext(name)) for p in points}
        grids[name] = np.array([[lookup[(r, c)] for c in x] for r in y])
    rows, cols = np.full(target_lat.shape, float(np.median(y))), np.full(target_lat.shape, float(np.median(x)))
    for iteration in range(20):
        lat, a, b = interpolate(y, x, grids['latitude'], rows, cols)
        lon, c, d = interpolate(y, x, grids['longitude'], rows, cols)
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
        raise ValueError('Inverse geolocation failed')
    if rows.min() < y[0] or rows.max() > y[-1] or cols.min() < x[0] or cols.max() > x[-1]:
        raise ValueError('Outside native geolocation grid')
    query = np.column_stack((rows, cols))
    roundtrip = {name: float(np.max(np.abs(RegularGridInterpolator((y, x), grids[name])(query)-target)))
                 for name, target in [('latitude', target_lat), ('longitude', target_lon)]}
    if max(roundtrip.values()) > 1e-9:
        raise ValueError('Roundtrip geolocation residual exceeds tolerance')
    product = json.loads((cache / 'source/productInfo.json').read_text())
    native_url = 'https://sentinel-s1-l1c.s3.amazonaws.com/' + product['path'] + '/measurement/iw-vv.tiff'
    dn_path, receipt_path = work / 'native_dn.npy', work / 'download.json'
    if dn_path.exists() and receipt_path.exists():
        receipt = json.loads(receipt_path.read_text())
        if (not source_matches(dn_path, receipt['sha256'], sha(dn_path))) or receipt['url'] != native_url:
            raise ValueError('Cached native image changed')
        dn = np.load(dn_path, allow_pickle=False)
        row0, col0 = receipt['origin_line_pixel']
    else:
        reader = RangeReader(native_url)
        with tifffile.TiffFile(reader) as tif:
            p = tif.pages[0]
            if not p.is_tiled or p.samplesperpixel != 1:
                raise ValueError('Unexpected native TIFF layout')
            th, tw = p.tilelength, p.tilewidth
            r0, r1 = int(rows.min())//th, math.ceil(rows.max())//th
            c0, c1 = int(cols.min())//tw, math.ceil(cols.max())//tw
            row0, col0 = r0*th, c0*tw
            dn = np.zeros(((r1-r0+1)*th, (c1-c0+1)*tw), dtype=p.dtype)
            for r in range(r0, r1+1):
                for c in range(c0, c1+1):
                    index = r*math.ceil(p.shape[1]/tw)+c
                    raw = reader._range(p.dataoffsets[index], p.databytecounts[index])
                    decoded, position, _ = p.decode(raw, index)
                    if position[2:4] != (r*th, c*tw):
                        raise ValueError('Native TIFF block position mismatch')
                    dn[(r-r0)*th:(r-r0+1)*th, (c-c0)*tw:(c-c0+1)*tw] = np.asarray(decoded)[0, :, :, 0]
            np.save(dn_path, dn, allow_pickle=False)
            receipt = {'url': native_url, 'origin_line_pixel': [row0, col0], 'shape': list(dn.shape),
                       'ranges': reader.requests, 'downloaded_bytes': reader.downloaded, 'sha256': sha(dn_path)}
            receipt_path.write_text(json.dumps(receipt, indent=2)+'\n')
    native_rows, native_cols = row0+np.arange(dn.shape[0]), col0+np.arange(dn.shape[1])
    yy, xx = np.meshgrid(native_rows, native_cols, indexing='ij')
    vectors = ET.parse(cache / 'source/calibration-iw-vv.xml').findall('.//calibrationVector')
    cy = np.array([int(v.findtext('line')) for v in vectors])
    cx = np.fromstring(vectors[0].findtext('pixel'), sep=' ')
    if not all(np.array_equal(cx, np.fromstring(v.findtext('pixel'), sep=' ')) for v in vectors):
        raise ValueError('Nonrectangular calibration grid')
    if native_rows.min() < cy.min() or native_rows.max() > cy.max() or native_cols.min() < cx.min() or native_cols.max() > cx.max():
        raise ValueError('Outside calibration support')
    grid = np.array([np.fromstring(v.findtext('sigmaNought'), sep=' ') for v in vectors])
    lut = interpolate(cy, cx, grid, yy.ravel(), xx.ravel())[0].reshape(dn.shape)
    if np.any(lut <= 0):
        raise ValueError('Nonpositive LUT')
    sigma = dn.astype(float)**2/lut**2
    sampled = interpolate(native_rows, native_cols, sigma, rows, cols)[0]
    ref = RegularGridInterpolator((native_rows, native_cols), sigma)(query)
    if not np.allclose(sampled, ref, rtol=1e-12, atol=1e-12):
        raise ValueError('Native resampling reference mismatch')
    moving = 10*np.log10(np.maximum(sampled, 1e-12)).reshape(exported.shape)
    fixed = np.array(protocol['fixed_shift_row_col'])
    moved = shift_image(moving, fixed, order=1, mode='constant', cval=np.nan, prefilter=False)
    interior = (slice(8, -8), slice(8, -8))
    before, after = stats(exported[interior], moving[interior]), stats(exported[interior], moved[interior])
    diagnostic = register(exported, moving)
    difference = float(np.max(np.abs(np.array(diagnostic['skimage_subpixel_shift'])-fixed)))
    checks = {'shift_transfer': difference <= protocol['engineering_checks_not_statistical_theorems']['max_abs_shift_difference_pixels'],
              'correlation_increased': after['pearson_correlation'] > before['pearson_correlation'],
              'coverage_unchanged': before['pixels'] == after['pixels']}
    np.savez_compressed(work / 'sampled.npz', sigma0=sampled.reshape(exported.shape), native_line=rows.reshape(exported.shape), native_pixel=cols.reshape(exported.shape))
    result = {'protocol_sha256': sha(protocol_path), 'source_audit_sha256': sha(source_path),
              'script_sha256': sha(Path(__file__)), 'sample': protocol['check_sample'], 'mask_read': False,
              'exported_tiff': {'url': url, 'sha256': expected, 'bytes': size, 'pointer_sha256': sha(pointer)},
              'development_bounds_wsen': dev_bounds, 'check_bounds_wsen': bounds, 'check_overlap_fraction': overlap_fraction,
              'native_download': receipt, 'roundtrip_max_abs_degrees': roundtrip,
              'numpy_scipy_resampling_max_abs_error': float(np.max(np.abs(sampled-ref))),
              'fixed_shift': fixed.tolist(), 'before': before, 'after_fixed_shift': after,
              'independent_shift_diagnostic': diagnostic, 'shift_difference_max_abs': difference,
              'checks': checks, 'passed': all(checks.values()), 'sampled_sha256': sha(work / 'sampled.npz'),
              'limitations': protocol['limitations']}
    (ROOT / 'docs/management/cantarell_transfer_audit.json').write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({k: result[k] for k in ('sample', 'check_overlap_fraction', 'fixed_shift', 'before', 'after_fixed_shift', 'shift_difference_max_abs', 'checks', 'passed')}, indent=2))


if __name__ == '__main__':
    main()
