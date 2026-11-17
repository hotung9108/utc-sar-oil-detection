"""Measured calibration/interpolation demo on real Sentinel-1 DN, separate from SOS.

ESA L1 Detailed Algorithm Definition, equations 9-53 to 9-56: calibrated
backscatter = DN**2 / LUT**2. Gamma LUT incorporates ellipsoid incidence
geometry. This does not remove all wind/surface-angle dependence of ocean SAR.
"""
import hashlib
import json
import xml.etree.ElementTree as ET
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate import RegularGridInterpolator

ROOT = Path(__file__).resolve().parents[1]


def bilinear_numpy(y, x, values, rows, cols):
    """Bilinear interpolation on a nonuniform rectilinear grid; no extrapolation."""
    y, x, values = np.asarray(y), np.asarray(x), np.asarray(values)
    rows, cols = np.asarray(rows), np.asarray(cols)
    if values.shape != (len(y), len(x)) or np.any(np.diff(y)<=0) or np.any(np.diff(x)<=0):
        raise ValueError('Invalid interpolation grid')
    if rows.min()<y[0] or rows.max()>y[-1] or cols.min()<x[0] or cols.max()>x[-1]:
        raise ValueError('Extrapolation is not allowed')
    iy = np.clip(np.searchsorted(y,rows,side='right')-1,0,len(y)-2)
    ix = np.clip(np.searchsorted(x,cols,side='right')-1,0,len(x)-2)
    wy = ((rows-y[iy])/(y[iy+1]-y[iy]))[:,None]
    wx = ((cols-x[ix])/(x[ix+1]-x[ix]))[None,:]
    top = values[iy[:,None],ix[None,:]]*(1-wx)+values[iy[:,None],ix[None,:]+1]*wx
    bottom = values[iy[:,None]+1,ix[None,:]]*(1-wx)+values[iy[:,None]+1,ix[None,:]+1]*wx
    return top*(1-wy)+bottom*wy


def error(a,b):
    delta = a-b
    return {'max_abs':float(np.max(np.abs(delta))),'mse':float(np.mean(delta**2))}


def main():
    audit = json.loads((ROOT/'docs/management/sentinel_window_audit.json').read_text())
    metadata = json.loads((ROOT/'docs/management/sentinel_metadata_audit.json').read_text())
    tile_path = ROOT/audit['file']
    assert hashlib.sha256(tile_path.read_bytes()).hexdigest()==audit['sha256']
    for item in metadata['files']:
        if 'file' in item:
            assert hashlib.sha256((ROOT/item['file']).read_bytes()).hexdigest()==item['sha256']
    directory = tile_path.parent
    dn = np.load(tile_path,allow_pickle=False).astype(np.float64)
    row0,col0 = audit['window_origin_line_pixel']
    rows,cols = row0+np.arange(dn.shape[0]), col0+np.arange(dn.shape[1])
    yy,xx = np.meshgrid(rows,cols,indexing='ij')
    query = np.stack([yy,xx],axis=-1)
    annotation = ET.parse(directory/'annotation/iw-vv.xml')
    points = annotation.findall('.//geolocationGridPoint')
    gy = sorted({int(p.findtext('line')) for p in points})
    gx = sorted({int(p.findtext('pixel')) for p in points})
    mapping = {(int(p.findtext('line')),int(p.findtext('pixel'))):float(p.findtext('incidenceAngle')) for p in points}
    assert len(mapping)==len(gy)*len(gx)
    angles = np.array([[mapping[(y,x)] for x in gx] for y in gy])
    angle = bilinear_numpy(gy,gx,angles,rows,cols)
    angle_ref = RegularGridInterpolator((gy,gx),angles,bounds_error=True)(query)
    checks = {'incidence_interpolation':error(angle,angle_ref)}
    calibration = ET.parse(directory/'annotation/calibration/calibration-iw-vv.xml')
    vectors = calibration.findall('.//calibrationVector')
    cy = np.array([int(v.findtext('line')) for v in vectors])
    cx = np.fromstring(vectors[0].findtext('pixel'),sep=' ')
    assert all(np.array_equal(np.fromstring(v.findtext('pixel'),sep=' '),cx) for v in vectors)
    calibrated = {}
    for name in ('sigmaNought','gamma'):
        values = np.array([np.fromstring(v.findtext(name),sep=' ') for v in vectors])
        lut = bilinear_numpy(cy,cx,values,rows,cols)
        ref = RegularGridInterpolator((cy,cx),values,bounds_error=True)(query)
        assert np.all(lut>0)
        checks[name+'_lut_interpolation'] = error(lut,ref)
        calibrated[name] = dn**2/lut**2
        checks[name+'_calibrated'] = error(calibrated[name],dn**2/ref**2)
        if not np.allclose(lut,ref,rtol=1e-12,atol=1e-12):
            raise AssertionError('NumPy/SciPy interpolation mismatch')
    assert np.allclose(angle,angle_ref,rtol=1e-12,atol=1e-12)
    derived_gamma = calibrated['sigmaNought']/np.cos(np.deg2rad(angle))
    delta_db = 10*np.log10(derived_gamma/calibrated['gamma'])
    output = ROOT/'results/physical'
    output.mkdir(parents=True,exist_ok=True)
    result = {'scope':'One unlabelled native Sentinel-1 tile; no detection accuracy or algorithm superiority claim',
        'scene':audit['scene'],'tile_sha256':audit['sha256'],
        'metadata_files':metadata['files'],'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'shape':list(dn.shape),'angle_min':float(angle.min()),'angle_max':float(angle.max()),
        'formula':'backscatter = DN^2 / interpolated_LUT^2',
        'reference':'SciPy RegularGridInterpolator, linear, same grid and boundaries; not SNAP end-to-end equivalence',
        'checks':checks,'allclose_tolerance':{'rtol':1e-12,'atol':1e-12},'allclose_passed':True,
        'sigma_over_cos_vs_gamma_lut_max_abs_db':float(np.max(np.abs(delta_db))),
        'thermal_noise_correction_performed_in_source':annotation.findtext('.//thermalNoiseCorrectionPerformed'),
        'thermal_noise_correction_applied_here':False,
        'limits':['No oil ground truth','No wind joined','Gamma normalization removes geometric area factor, not complete ocean scattering dependence',
                  'No map from this tile to SOS or a labelled DARTIS patch','Interpolation reference is not an independent SAR processor']}
    (output/'calibration.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    np.savez_compressed(directory/'central_calibrated.npz',incidence_degrees=angle,
                        sigma0=calibrated['sigmaNought'],gamma0=calibrated['gamma'])
    fig,axes = plt.subplots(1,3,figsize=(14,4.5))
    db_min = min(float(10*np.log10(v.min())) for v in calibrated.values())
    db_max = max(float(10*np.log10(v.max())) for v in calibrated.values())
    for ax,values,title in zip(axes,[angle,10*np.log10(calibrated['sigmaNought']),10*np.log10(calibrated['gamma'])],
                              ['Ellipsoid incidence (degrees)','Sigma0 (dB), no thermal correction','Gamma0 (dB), no thermal correction']):
        limits = {} if title.startswith('Ellipsoid') else {'vmin':db_min,'vmax':db_max}
        image=ax.imshow(values,cmap='viridis',**limits); ax.set_title(title,fontsize=10)
        ax.set(xlabel='Tile column',ylabel='Tile row'); fig.colorbar(image,ax=ax,shrink=0.8)
    fig.tight_layout(); fig.savefig(output/'calibration.png',dpi=160); plt.close(fig)
    print(json.dumps({'checks':checks,'angle_range':[result['angle_min'],result['angle_max']],
                      'gamma_relation_max_abs_db':result['sigma_over_cos_vs_gamma_lut_max_abs_db']},indent=2))


if __name__=='__main__': main()
