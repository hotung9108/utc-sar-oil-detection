"""Fetch only VV TIFF blocks covering the mapped Cantarell development sample."""

import sys as _sys
from pathlib import Path as _Path
_project_root = _Path(__file__).resolve().parents[2]
_sys.path.insert(0, str(_project_root))
_sys.path.insert(0, str(_project_root / "src"))

import hashlib
import json
import math
import xml.etree.ElementTree as ET
from pathlib import Path

import numpy as np
import tifffile
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.interpolate import RegularGridInterpolator


from scripts._provenance import source_matches
from scripts._paths import resolve_path
from scripts.cantarell.audit_cantarell_source import ROOT, REVISION
from scripts.physical.fetch_sentinel_window import RangeReader
from scripts.cantarell.map_cantarell_native_grid import interpolate


def sha(path):
    return hashlib.sha256(resolve_path(path).read_bytes()).hexdigest()


def main():
    cache = ROOT / '.cache/cantarell_source' / REVISION
    mapping_audit = ROOT / 'docs/management/cantarell_mapping_audit.json'
    mapping = json.loads(mapping_audit.read_text())
    source_audit = ROOT / 'docs/management/cantarell_source_audit.json'
    if (not source_matches(source_audit, mapping['source_audit_sha256'], sha(source_audit))):
        raise ValueError('Source audit changed; rerun mapping')
    for entry in json.loads(source_audit.read_text())['receipts']:
        path = cache / entry['path']
        if entry.get('verified_against_lfs_pointer'):
            path = path.with_name(path.name + '.lfs-object')
        if (not source_matches(path, entry['sha256'], sha(path))):
            raise ValueError('Cached source asset hash mismatch')
    if (not source_matches(ROOT / mapping['mapping_file'], mapping['mapping_sha256'], sha(ROOT / mapping['mapping_file']))):
        raise ValueError('Mapping file hash mismatch')
    with np.load(ROOT / mapping['mapping_file']) as data:
        rows, cols = data['native_line'].ravel(), data['native_pixel'].ravel()
    product = json.loads((cache / 'source/productInfo.json').read_text())
    url = 'https://sentinel-s1-l1c.s3.amazonaws.com/' + product['path'] + '/measurement/iw-vv.tiff'
    target = cache / 'native_vv_dn.npy'
    receipt_path = cache / 'native_vv_download.json'
    if target.exists() and receipt_path.exists():
        receipt = json.loads(receipt_path.read_text())
        if receipt['source_url'] != url or (not source_matches(target, receipt['sha256'], sha(target))):
            raise ValueError('Cached native image provenance mismatch')
        dn = np.load(target, allow_pickle=False)
        row0, col0 = receipt['origin_line_pixel']
    else:
        reader = RangeReader(url)
        with tifffile.TiffFile(reader) as tif:
            page = tif.pages[0]
            if not page.is_tiled or page.samplesperpixel != 1:
                raise ValueError('Expected single-channel tiled TIFF')
            height, width = page.shape
            th, tw = page.tilelength, page.tilewidth
            r0, r1 = int(rows.min())//th, math.ceil(rows.max())//th
            c0, c1 = int(cols.min())//tw, math.ceil(cols.max())//tw
            row0, col0 = r0*th, c0*tw
            dn = np.zeros(((r1-r0+1)*th, (c1-c0+1)*tw), dtype=page.dtype)
            blocks = []
            for r in range(r0, r1+1):
                for c in range(c0, c1+1):
                    index = r*math.ceil(width/tw)+c
                    raw = reader._range(page.dataoffsets[index], page.databytecounts[index])
                    decoded, position, _ = page.decode(raw, index)
                    if position[2:4] != (r*th, c*tw):
                        raise ValueError('TIFF block location mismatch')
                    dn[(r-r0)*th:(r-r0+1)*th, (c-c0)*tw:(c-c0+1)*tw] = np.asarray(decoded)[0, :, :, 0]
                    blocks.append(index)
            np.save(target, dn, allow_pickle=False)
            receipt = {'source_url': url, 'scene_shape': [height, width],
                       'origin_line_pixel': [row0, col0], 'shape': list(dn.shape),
                       'dtype': str(dn.dtype), 'blocks': blocks, 'ranges': reader.requests,
                       'downloaded_bytes': reader.downloaded, 'sha256': sha(target)}
            receipt_path.write_text(json.dumps(receipt, indent=2)+'\n')
    native_rows = row0+np.arange(dn.shape[0])
    native_cols = col0+np.arange(dn.shape[1])
    yy, xx = np.meshgrid(native_rows, native_cols, indexing='ij')
    calibration = ET.parse(cache / 'source/calibration-iw-vv.xml')
    vectors = calibration.findall('.//calibrationVector')
    cy = np.array([int(v.findtext('line')) for v in vectors])
    cx = np.fromstring(vectors[0].findtext('pixel'), sep=' ')
    if not all(np.array_equal(cx, np.fromstring(v.findtext('pixel'), sep=' ')) for v in vectors):
        raise ValueError('Calibration grid is not rectangular')
    grid = np.array([np.fromstring(v.findtext('sigmaNought'), sep=' ') for v in vectors])
    if native_rows.min() < cy.min() or native_rows.max() > cy.max() or native_cols.min() < cx.min() or native_cols.max() > cx.max():
        raise ValueError('Native block extent exceeds calibration support')
    lut = interpolate(cy, cx, grid, yy.ravel(), xx.ravel())[0].reshape(dn.shape)
    if np.any(lut <= 0):
        raise ValueError('Nonpositive calibration LUT')
    sigma = dn.astype(float)**2/lut**2
    sampled = interpolate(native_rows, native_cols, sigma, rows, cols)[0]
    reference = RegularGridInterpolator((native_rows, native_cols), sigma, bounds_error=True)(np.column_stack((rows, cols)))
    if not np.allclose(sampled, reference, rtol=1e-12, atol=1e-12):
        raise ValueError('Resampling implementation mismatch')
    exported = tifffile.imread(cache / 'RASTER/IMG-TIFF/16-BIT/IMG_01_TILE_001.tiff.lfs-object')
    db = 10*np.log10(np.maximum(sampled, 1e-12)).reshape(exported.shape)
    valid = np.isfinite(exported) & np.isfinite(db)
    comparison = {'assumption': 'Exported float values compared AS IF they were VV sigma0 dB; not confirmed units.',
                  'pearson_correlation': float(np.corrcoef(exported[valid], db[valid])[0, 1]),
                  'median_db_difference_under_assumption': float(np.median(db[valid]-exported[valid])),
                  'rmse_under_assumption': float(np.sqrt(np.mean((db[valid]-exported[valid])**2)))}
    np.savez_compressed(cache / 'native_vv_sampled.npz', sigma0=sampled.reshape(exported.shape), sigma0_db=db)
    from PIL import Image
    mask = np.asarray(Image.open(cache / 'IMAGES/LABELS-1D/IMG_01_TILE_001_1D.png.lfs-object')) > 0
    fig, axes = plt.subplots(1, 3, figsize=(15, 4.5))
    for ax, values, title in zip(axes[:2], [exported, db],
                                ['Publisher export (units unconfirmed)', 'Native VV sigma0 dB, mapped approximately']):
        image = ax.imshow(values, cmap='gray', vmin=-30, vmax=-5)
        ax.contour(mask, levels=[.5], colors='red', linewidths=.6)
        ax.set_title(title, fontsize=10)
        fig.colorbar(image, ax=ax, shrink=.75)
    image = axes[2].imshow(db-exported, cmap='coolwarm', vmin=-6, vmax=6)
    axes[2].set_title('Difference under sigma0-dB assumption', fontsize=10)
    fig.colorbar(image, ax=axes[2], shrink=.75)
    for ax in axes:
        ax.set_xlabel('Map tile column')
        ax.set_ylabel('Map tile row')
    fig.suptitle('Development sample only; red = source slick label; no detection evaluation', fontsize=11)
    fig.tight_layout()
    figure = ROOT / 'docs/management/cantarell_native_comparison.png'
    fig.savefig(figure, dpi=140)
    plt.close(fig)
    output = {'mapping_audit_sha256': sha(mapping_audit), 'script_sha256': sha(Path(__file__)),
              'download': receipt, 'resampling_max_abs_error': float(np.max(np.abs(sampled-reference))),
              'comparison': comparison, 'sampled_sha256': sha(cache / 'native_vv_sampled.npz'),
              'figure': figure.relative_to(ROOT).as_posix(), 'figure_sha256': sha(figure),
              'limits': ['No thermal-noise removal; exported processing history remains unknown.',
                         'Bilinear geolocation approximation, not terrain correction.',
                         'No detection evaluation and no claim of confirmed exported units or polarization.']}
    (ROOT / 'docs/management/cantarell_native_audit.json').write_text(json.dumps(output, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({'downloaded_bytes': receipt['downloaded_bytes'], 'shape': receipt['shape'],
                      'resampling_max_abs_error': output['resampling_max_abs_error'], 'comparison': comparison}, indent=2))


if __name__ == '__main__':
    main()
