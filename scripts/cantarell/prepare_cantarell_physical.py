"""Reconstruct paired physical SAR inputs under the frozen data protocol.

No model fitting or detection scoring. Every sample gets a receipt, including failures.
"""

import sys as _sys
from pathlib import Path as _Path
_project_root = _Path(__file__).resolve().parents[2]
_sys.path.insert(0, str(_project_root))
_sys.path.insert(0, str(_project_root / "src"))

import argparse
import hashlib
import json
import math
import time
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import numpy as np
import scipy
import skimage
import tifffile
from PIL import Image
from scipy.interpolate import RegularGridInterpolator
from scipy.ndimage import label as label_reference, shift as shift_reference


from scripts._provenance import source_matches
from scripts._paths import resolve_path
from scripts.cantarell.audit_cantarell_source import ROOT, REVISION
from scripts.cantarell.check_cantarell_registration import register, stats
from scripts.physical.fetch_sentinel_window import RangeReader
from scripts.cantarell.map_cantarell_native_grid import interpolate

CACHE = ROOT / '.cache/cantarell_source' / REVISION
FOLDER = ROOT / 'docs/management'


def sha(path):
    return hashlib.sha256(resolve_path(path).read_bytes()).hexdigest()


def write_json(path, value):
    temp = path.with_suffix(path.suffix+'.tmp')
    temp.write_text(json.dumps(value, indent=2)+'\n', encoding='utf-8')
    temp.replace(path)


class DiskRangeReader(RangeReader):
    def __init__(self, url, directory):
        self.directory = directory
        directory.mkdir(parents=True, exist_ok=True)
        super().__init__(url)

    def _range(self, offset, size):
        if (offset, size) in self.cache:
            return self.cache[offset, size]
        path = self.directory / f'{offset}_{size}.bin'
        receipt_path = path.with_suffix('.json')
        if path.exists() and receipt_path.exists():
            receipt = json.loads(receipt_path.read_text())
            raw = path.read_bytes()
            if receipt['url'] != self.url or len(raw) != size or (not source_matches(path, receipt['sha256'], sha(path))):
                raise ValueError('Persisted byte-range provenance mismatch')
            if self.total is not None and self.total != receipt['remote_bytes']:
                raise ValueError('Remote size receipt mismatch')
            self.total = receipt['remote_bytes']
            self.cache[offset, size] = raw
            self.requests.append({'offset': offset, 'bytes': size, 'sha256': receipt['sha256']})
            return raw
        for attempt in range(3):
            try:
                raw = super()._range(offset, size)
                break
            except (OSError, TimeoutError):
                if attempt == 2:
                    raise
                time.sleep(2*(attempt+1))
        path.write_bytes(raw)
        write_json(receipt_path, {'url': self.url, 'offset': offset, 'bytes': size,
                                 'remote_bytes': self.total, 'sha256': sha(path)})
        return raw


def load_grids(meta):
    for f in meta['files']:
        if (not source_matches(ROOT / f['file'], f['sha256'], sha(ROOT / f['file']))):
            raise ValueError('Physical metadata hash mismatch')
    annotation = ET.parse(ROOT / meta['files'][0]['file'])
    points = annotation.findall('.//geolocationGridPoint')
    y = np.array(sorted({int(p.findtext('line')) for p in points}))
    x = np.array(sorted({int(p.findtext('pixel')) for p in points}))
    fields = {}
    for name in ('latitude', 'longitude', 'incidenceAngle'):
        lookup = {(int(p.findtext('line')), int(p.findtext('pixel'))): float(p.findtext(name)) for p in points}
        fields[name] = np.array([[lookup[(r,c)] for c in x] for r in y])
    vectors = ET.parse(ROOT / meta['files'][1]['file']).findall('.//calibrationVector')
    cy = np.array([int(v.findtext('line')) for v in vectors])
    cx = np.fromstring(vectors[0].findtext('pixel'), sep=' ')
    lut = np.array([np.fromstring(v.findtext('sigmaNought'), sep=' ') for v in vectors])
    return y, x, fields, cy, cx, lut


def paired_checked(y, x, values, rows, cols, checks, name):
    if rows.min()<y[0] or rows.max()>y[-1] or cols.min()<x[0] or cols.max()>x[-1]:
        raise ValueError(f'Outside metadata/interpolation support: {name}')
    ours = interpolate(y, x, values, rows, cols)[0]
    reference = RegularGridInterpolator((y,x), values, bounds_error=True)(np.column_stack((rows,cols)))
    checks[name] = float(np.max(np.abs(ours-reference)))
    if not np.allclose(ours, reference, rtol=1e-12, atol=1e-12):
        raise ValueError(f'NumPy/SciPy mismatch: {name}')
    return ours


def shift_numpy(image, delta, checks, name):
    rr, cc = np.indices(image.shape, dtype=float)
    rr, cc = rr.ravel()-delta[0], cc.ravel()-delta[1]
    inside = (rr>=0)&(rr<=image.shape[0]-1)&(cc>=0)&(cc<=image.shape[1]-1)
    result = np.full(rr.shape, np.nan)
    result[inside] = interpolate(np.arange(image.shape[0]), np.arange(image.shape[1]), image, rr[inside], cc[inside])[0]
    result = result.reshape(image.shape)
    ref = shift_reference(image, delta, order=1, mode='constant', cval=np.nan, prefilter=False)
    checks[name] = float(np.max(np.abs(result[np.isfinite(ref)]-ref[np.isfinite(ref)])))
    if not np.allclose(result, ref, rtol=1e-12, atol=1e-12, equal_nan=True):
        raise ValueError('NumPy/SciPy translation mismatch')
    return result


def prepare(sample, scene, meta, grids, protocol, run_dir, binding, retry_errors=False):
    name = sample['sample']
    receipt_path = run_dir / f'{name}.json'
    if receipt_path.exists():
        previous = json.loads(receipt_path.read_text())
        if previous['binding'] != binding:
            raise ValueError('Prepared sample binding mismatch')
        if previous.get('file') and (not source_matches(ROOT / previous['file'], previous['sha256'], sha(ROOT / previous['file']))):
            raise ValueError('Prepared sample hash mismatch')
        if not (retry_errors and 'error' in previous):
            return previous
    result = {'sample': name, 'group': sample['group'], 'scene': sample['scene'],
              'split': sample['split'], 'binding': binding, 'eligible': False}
    try:
        exported_path = CACHE / f'RASTER/IMG-TIFF/16-BIT/{name}.tiff.lfs-object'
        mask_path = CACHE / f'IMAGES/LABELS-1D/{name}_1D.png.lfs-object'
        if (not source_matches(exported_path, sample['exported_image_sha256'], sha(exported_path))) or (not source_matches(mask_path, sample['mask_sha256'], sha(mask_path))):
            raise ValueError('Publisher image or mask hash mismatch')
        with tifffile.TiffFile(exported_path) as tif:
            p = tif.pages[0]
            exported = p.asarray().astype(float)
            scale, tie = p.tags['ModelPixelScaleTag'].value, p.tags['ModelTiepointTag'].value
        if exported.shape != (600,800) or not np.all(np.isfinite(exported)):
            raise ValueError('Invalid publisher image')
        rr, cc = np.indices(exported.shape)
        target_lat = (tie[4]-(rr+.5-tie[1])*scale[1]).ravel()
        target_lon = (tie[3]+(cc+.5-tie[0])*scale[0]).ravel()
        y,x,fields,cy,cx,lut_grid = grids
        rows = np.full(target_lat.shape, float(np.median(y)))
        cols = np.full(target_lat.shape, float(np.median(x)))
        for iteration in range(20):
            lat,a,b = interpolate(y,x,fields['latitude'],rows,cols)
            lon,c,d = interpolate(y,x,fields['longitude'],rows,cols)
            det = a*d-b*c
            if np.any(np.abs(det)<1e-16):
                raise ValueError('Singular inverse geolocation')
            e,f = lat-target_lat,lon-target_lon
            dr,dc = (d*e-b*f)/det,(a*f-c*e)/det
            rows -= dr
            cols -= dc
            if max(np.max(np.abs(dr)),np.max(np.abs(dc)))<1e-7:
                break
        else:
            raise ValueError('Inverse geolocation did not converge')
        checks = {}
        back_lat = paired_checked(y,x,fields['latitude'],rows,cols,checks,'latitude')
        back_lon = paired_checked(y,x,fields['longitude'],rows,cols,checks,'longitude')
        roundtrip = max(float(np.max(np.abs(back_lat-target_lat))),float(np.max(np.abs(back_lon-target_lon))))
        if roundtrip>1e-9:
            raise ValueError('Geolocation roundtrip mismatch')
        r0,r1 = int(np.floor(rows.min())),int(np.ceil(rows.max()))+1
        c0,c1 = int(np.floor(cols.min())),int(np.ceil(cols.max()))+1
        nr,nc = np.arange(r0,r1),np.arange(c0,c1)
        ny,nx = np.meshgrid(nr,nc,indexing='ij')
        native_lut = paired_checked(cy,cx,lut_grid,ny.ravel(),nx.ravel(),checks,'sigma_lut').reshape(ny.shape)
        native_angle = paired_checked(y,x,fields['incidenceAngle'],ny.ravel(),nx.ravel(),checks,'native_angle').reshape(ny.shape)
        if np.any(native_lut<=0):
            raise ValueError('Nonpositive calibration LUT')
        url = scene['base_url']+'measurement/iw-vv.tiff'
        reader = DiskRangeReader(url, CACHE/'native_ranges'/sample['scene'])
        with tifffile.TiffFile(reader) as tif:
            p = tif.pages[0]
            if list(p.shape)!=meta['shape'] or not p.is_tiled or p.samplesperpixel!=1 or p.dtype != np.dtype('uint16'):
                raise ValueError('Native TIFF does not match metadata')
            th,tw = p.tilelength,p.tilewidth
            dn = np.zeros(ny.shape,dtype=p.dtype)
            for tr in range(r0//th,(r1-1)//th+1):
                for tc in range(c0//tw,(c1-1)//tw+1):
                    index = tr*math.ceil(p.shape[1]/tw)+tc
                    raw = reader._range(p.dataoffsets[index],p.databytecounts[index])
                    decoded,position,_ = p.decode(raw,index)
                    if position[2:4]!=(tr*th,tc*tw):
                        raise ValueError('Native TIFF block origin mismatch')
                    tile = np.asarray(decoded)[0,:,:,0]
                    ar,br = max(r0,tr*th),min(r1,(tr+1)*th)
                    ac,bc = max(c0,tc*tw),min(c1,(tc+1)*tw)
                    dn[ar-r0:br-r0,ac-c0:bc-c0] = tile[ar-tr*th:br-tr*th,ac-tc*tw:bc-tc*tw]
        result['native_source'] = {'url':url,'ranges':reader.requests,'downloaded_now_bytes':reader.downloaded,
                                   'roi_origin':[r0,c0],'roi_shape':list(dn.shape)}
        sigma_native = dn.astype(float)**2/native_lut**2
        gamma_native = sigma_native/np.cos(np.deg2rad(native_angle))
        channels = {}
        for key,values in [('sigma0',sigma_native),('gamma0',gamma_native),('incidence_degrees',native_angle)]:
            channels[key] = paired_checked(nr,nc,values,rows,cols,checks,'sample_'+key).reshape(exported.shape)
        moving = 10*np.log10(np.maximum(channels['sigma0'],1e-12))
        global_registration = register(exported,moving)
        delta = np.array(global_registration['skimage_subpixel_shift'])
        local = []
        ye,xe = np.linspace(0,600,4,dtype=int),np.linspace(0,800,4,dtype=int)
        for r in range(3):
            for c in range(3):
                part = (slice(ye[r],ye[r+1]),slice(xe[c],xe[c+1]))
                diagnostic = register(exported[part],moving[part])
                local.append({'block':[r,c],'shift':diagnostic['skimage_subpixel_shift']})
        max_local = float(np.max(np.abs(np.array([v['shift'] for v in local])-delta)))
        crop = (slice(8,-8),slice(8,-8))
        aligned = {key:shift_numpy(value,delta,checks,'translate_'+key)[crop] for key,value in channels.items()}
        finite = all(np.all(np.isfinite(v)) for v in aligned.values())
        registration_stats = stats(exported[crop],10*np.log10(np.maximum(aligned['sigma0'],1e-12)))
        criteria = protocol['eligibility_checks_frozen_before_full_native_reconstruction']
        quality = {'shift_magnitude':bool(np.max(np.abs(delta))<=criteria['max_abs_global_shift_pixels']),
                   'local_consistency':bool(max_local<=criteria['max_abs_local_minus_global_shift_pixels']),
                   'pearson':bool(registration_stats['pearson_correlation']>=criteria['minimum_registered_pearson_on_8pixel_interior']),
                   'finite':bool(finite)}
        # Labels are only decoded after image-only registration and eligibility calculations.
        mask = np.asarray(Image.open(mask_path))
        if mask.shape != exported.shape or not set(np.unique(mask)).issubset({0,1,2}):
            raise ValueError('Invalid mask dimensions/encoding')
        truth = (mask>0)[crop]
        full_labels,full_count = label_reference(mask>0,np.ones((3,3),dtype=int))
        crop_labels,crop_count = label_reference(truth,np.ones((3,3),dtype=int))
        touching = np.unique(np.concatenate((crop_labels[0],crop_labels[-1],crop_labels[:,0],crop_labels[:,-1])))
        present_full_ids = set(np.unique(full_labels[crop]))-{0}
        output = run_dir/f'{name}.npz'
        np.savez_compressed(output,**aligned,truth=truth,semantic_mask=mask[crop])
        result.update({'eligible':all(quality.values()),'quality':quality,'failed_checks':[k for k,v in quality.items() if not v],
                       'registration':{'global':global_registration,'local':local,'max_local_difference':max_local,
                                       'actual_linear_power_shift_statistics':registration_stats},
                       'numpy_scipy_max_abs_errors':checks,'roundtrip_max_abs_degrees':roundtrip,
                       'incidence_range':[float(np.nanmin(aligned['incidence_degrees'])),float(np.nanmax(aligned['incidence_degrees']))],
                       'crop':{'pixels_each_edge':8,'shape':list(truth.shape),'full_gt_components':int(full_count),
                               'cropped_gt_components':int(crop_count),'full_gt_components_completely_outside_crop':int(full_count-len(present_full_ids)),
                               'cropped_gt_components_touching_edge':int(np.count_nonzero(touching))},
                       'file':output.relative_to(ROOT).as_posix(),'sha256':sha(output)})
    except Exception as exc:
        if isinstance(exc,ValueError) and (str(exc).startswith('Outside metadata/interpolation support:') or
                                          str(exc)=='Inverse geolocation did not converge'):
            result['failed_checks'] = ['metadata_support_or_geolocation']
            result['quality_failure_detail'] = str(exc)
        else:
            result['error'] = f'{type(exc).__name__}: {exc}'
    if receipt_path.exists():
        prior = json.loads(receipt_path.read_text())
        if 'error' in prior:
            result['prior_error_attempts'] = prior.get('prior_error_attempts',[])+[prior['error']]
    write_json(receipt_path,result)
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--groups',nargs='*',help='Prepare selected groups for implementation checks; default all.')
    parser.add_argument('--workers',type=int,default=2)
    parser.add_argument('--retry-errors',action='store_true',help='Retry operational errors only; preserve prior error messages.')
    args = parser.parse_args()
    if not 1<=args.workers<=2:
        raise ValueError('Use one or two workers to bound native-array memory')
    protocol_path = FOLDER/'cantarell_data_protocol_v1.json'
    protocol = json.loads(protocol_path.read_text())
    meta_path,scenes_path = FOLDER/'cantarell_physical_metadata_audit.json',FOLDER/'cantarell_scenes_audit.json'
    metadata,scenes = json.loads(meta_path.read_text()),json.loads(scenes_path.read_text())
    if (not source_matches(protocol_path, metadata['protocol_sha256'], sha(protocol_path))) or not metadata['complete'] or (not source_matches(scenes_path, protocol['scenes_audit_sha256'], sha(scenes_path))):
        raise ValueError('Frozen source metadata binding failed')
    sources = {name:sha(ROOT/'scripts'/name) for name in ['prepare_cantarell_physical.py','map_cantarell_native_grid.py',
                                                        'check_cantarell_registration.py','fetch_sentinel_window.py']}
    binding = {'protocol_sha256':sha(protocol_path),'metadata_sha256':sha(meta_path),'source_hashes':sources,
               'versions':{'numpy':np.__version__,'scipy':scipy.__version__,'skimage':skimage.__version__,'tifffile':tifffile.__version__}}
    run_key = hashlib.sha256(json.dumps(binding,sort_keys=True).encode()).hexdigest()
    run_dir = CACHE/'physical_prepared'/run_key
    run_dir.mkdir(parents=True,exist_ok=True)
    by_group = defaultdict(list)
    for sample in protocol['samples']:
        if not args.groups or sample['group'] in args.groups:
            by_group[sample['group']].append(sample)
    if args.groups and set(args.groups)-set(by_group):
        raise ValueError('Unknown requested group')
    scene_by = {r['group']:r for r in scenes['results']}
    meta_by = {r['group']:r for r in metadata['results']}

    def run_group(group,entries):
        grids = load_grids(meta_by[group])
        outputs = []
        for entry in entries:
            result = prepare(entry,scene_by[group],meta_by[group],grids,protocol,run_dir,binding,args.retry_errors)
            outputs.append(result)
            print(f"{entry['sample']} eligible={result['eligible']} {result.get('error',result.get('failed_checks',[]))}",flush=True)
        return outputs

    results,group_errors = [],[]
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        pending = {pool.submit(run_group,g,entries):g for g,entries in by_group.items()}
        for future in as_completed(pending):
            try:
                results.extend(future.result())
            except Exception as exc:
                group_errors.append({'group':pending[future],'error':f'{type(exc).__name__}: {exc}'})
            print(f'Completed {len(results)}/{sum(map(len,by_group.values()))} selected samples',flush=True)
    results.sort(key=lambda r:r['sample'])
    eligible_scenes = {split:sorted({r['scene'] for r in results if r['eligible'] and r['split']==split}) for split in ['train','val','test']}
    counts = Counter(r['split'] for r in results if r['eligible'])
    complete = len(results)==len(protocol['samples']) and not group_errors and not any('error' in r for r in results)
    audit = {'binding':binding,'run_key':run_key,'expected_samples':len(protocol['samples']),
             'processed_samples':len(results),'complete_preparation':complete,'group_errors':group_errors,
             'eligible_counts':dict(counts),'eligible_scenes':eligible_scenes,
             'scene_count_gate_passed':complete and all(len(v)>=3 for v in eligible_scenes.values()),
             'results':results,'limits':protocol['limits'],
             'no_models_fitted':True,'no_detection_scores_computed':True}
    write_json(FOLDER/'cantarell_physical_preparation_audit.json',audit)
    print(json.dumps({k:audit[k] for k in ['run_key','processed_samples','complete_preparation','eligible_counts','scene_count_gate_passed','group_errors']},indent=2))


if __name__=='__main__':
    main()
