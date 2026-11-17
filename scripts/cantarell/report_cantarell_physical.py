"""Verify completed physical inputs, or report explicitly partial live receipts."""

import sys as _sys
from pathlib import Path as _Path
_project_root = _Path(__file__).resolve().parents[2]
_sys.path.insert(0, str(_project_root))
_sys.path.insert(0, str(_project_root / "src"))

import argparse
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
import scipy
import skimage
import tifffile
from PIL import Image


from scripts._provenance import source_matches
from scripts._paths import resolve_path
from scripts.cantarell.audit_cantarell_source import ROOT, REVISION


def sha(path):
    return hashlib.sha256(resolve_path(path).read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--progress',action='store_true',help='Read live receipts; never claim the full data gate is passed.')
    args = parser.parse_args()
    folder = ROOT/'docs/management'
    protocol_path,metadata_path = folder/'cantarell_data_protocol_v1.json',folder/'cantarell_physical_metadata_audit.json'
    protocol = json.loads(protocol_path.read_text())
    source_names = ['prepare_cantarell_physical.py','map_cantarell_native_grid.py','check_cantarell_registration.py','fetch_sentinel_window.py']
    binding = {'protocol_sha256':sha(protocol_path),'metadata_sha256':sha(metadata_path),
               'source_hashes':{name:sha(ROOT/'scripts'/name) for name in source_names},
               'versions':{'numpy':np.__version__,'scipy':scipy.__version__,'skimage':skimage.__version__,'tifffile':tifffile.__version__}}
    run_key = hashlib.sha256(json.dumps(binding,sort_keys=True).encode()).hexdigest()
    cache = ROOT/'.cache/cantarell_source'/REVISION
    directory = cache/'physical_prepared'/run_key
    expected = {r['sample']:r for r in protocol['samples']}
    if args.progress:
        rows = [json.loads(p.read_text()) for p in sorted(directory.glob('*.json'))]
        complete = False
        final_audit_sha = None
    else:
        audit_path = folder/'cantarell_physical_preparation_audit.json'
        audit = json.loads(audit_path.read_text())
        if audit['binding']!=binding or audit['run_key']!=run_key:
            raise ValueError('Final audit is stale or from a different preparation run')
        if not audit['complete_preparation'] or audit['group_errors']:
            raise ValueError('Preparation is incomplete; use --progress for an explicitly partial report')
        rows = audit['results']
        complete = True
        final_audit_sha = sha(audit_path)
    seen = [r['sample'] for r in rows]
    if len(set(seen))!=len(seen) or set(seen)-set(expected):
        raise ValueError('Unexpected/duplicate sample receipt')
    if complete and set(seen)!=set(expected):
        raise ValueError('Full audit missing samples')
    criteria = protocol['eligibility_checks_frozen_before_full_native_reconstruction']
    verified_files = 0
    counts,excluded,pending = Counter(),[],sorted(set(expected)-set(seen))
    scenes = defaultdict(set)
    numeric_max = defaultdict(float)
    paired_relative_difference = []
    crop_totals = Counter()
    wind = json.loads((folder/'cantarell_wind_audit.json').read_text())
    if (not source_matches(protocol_path, wind['protocol_sha256'], sha(protocol_path))) or (not source_matches(metadata_path, wind['metadata_sha256'], sha(metadata_path))):
        raise ValueError('Wind audit belongs to another source protocol')
    winds = {r['sample']:r for r in wind['results']}
    for row in rows:
        if row['binding']!=binding:
            raise ValueError('Receipt source binding mismatch')
        original = expected[row['sample']]
        if any(row[k]!=original[k] for k in ['split','scene','group']):
            raise ValueError('Sample split/source differs from frozen protocol')
        if 'quality' in row:
            reg = row['registration']
            delta = np.array(reg['global']['skimage_subpixel_shift'])
            calculated = {
                'shift_magnitude':bool(np.max(np.abs(delta))<=criteria['max_abs_global_shift_pixels']),
                'local_consistency':bool(reg['max_local_difference']<=criteria['max_abs_local_minus_global_shift_pixels']),
                'pearson':bool(reg['actual_linear_power_shift_statistics']['pearson_correlation']>=criteria['minimum_registered_pearson_on_8pixel_interior']),
                'finite':row['quality']['finite']}
            if calculated!=row['quality'] or all(calculated.values())!=row['eligible']:
                raise ValueError('Stored eligibility is inconsistent with frozen numeric criteria')
        elif row['eligible']:
            raise ValueError('Eligible sample lacks quality evidence')
        for name,error in row.get('numpy_scipy_max_abs_errors',{}).items():
            numeric_max[name] = max(numeric_max[name],error)
        if row['eligible']:
            counts[row['split']] += 1
            scenes[row['split']].add(row['scene'])
            for key,value in row['crop'].items():
                if key not in ['pixels_each_edge','shape']:
                    crop_totals[key] += value
        else:
            excluded.append({'sample':row['sample'],'split':row['split'],'checks':row.get('failed_checks',[]),
                             'detail':row.get('quality_failure_detail',row.get('error'))})
        if complete and row.get('file'):
            path = ROOT/row['file']
            if (not source_matches(path, row['sha256'], sha(path))):
                raise ValueError('Prepared array hash mismatch')
            mask_path = cache/f"IMAGES/LABELS-1D/{row['sample']}_1D.png.lfs-object"
            if (not source_matches(mask_path, original['mask_sha256'], sha(mask_path))):
                raise ValueError('Source mask hash mismatch')
            source_mask = np.asarray(Image.open(mask_path))[8:-8,8:-8]
            with np.load(path,allow_pickle=False) as data:
                required = {'sigma0','gamma0','incidence_degrees','truth','semantic_mask'}
                if set(data.files)!=required or any(data[k].shape!=(584,784) for k in required):
                    raise ValueError('Unexpected prepared fields or crop dimensions')
                if not np.array_equal(data['semantic_mask'],source_mask) or not np.array_equal(data['truth'],source_mask>0):
                    raise ValueError('Prepared GT differs from frozen source crop')
                finite = all(np.all(np.isfinite(data[k])) for k in ['sigma0','gamma0','incidence_degrees'])
                if finite!=row['quality']['finite']:
                    raise ValueError('Stored finiteness claim differs from actual arrays')
                if row['eligible']:
                    if np.any(data['sigma0']<0) or np.any(data['gamma0']<0):
                        raise ValueError('Negative calibrated power')
                    if np.any((data['incidence_degrees']<=0)|(data['incidence_degrees']>=90)):
                        raise ValueError('Invalid incidence range')
                    valid = data['sigma0']>0
                    approximate = data['sigma0'][valid]/np.cos(np.deg2rad(data['incidence_degrees'][valid]))
                    paired_relative_difference.append(float(np.max(np.abs(data['gamma0'][valid]-approximate)/np.maximum(approximate,1e-12))))
            verified_files += 1
    minimum = criteria['minimum_eligible_scenes_per_split']
    scene_counts = {split:len(scenes[split]) for split in ['train','val','test']}
    gate = complete and all(n>=minimum for n in scene_counts.values())
    wind_missing = [r['sample'] for r in rows if r['eligible'] and r['sample'] not in winds]
    report = {'scope':'partial live receipts; array files not verified' if args.progress else 'complete prepared-array verification',
              'script_sha256':sha(Path(__file__)),
              'run_key':run_key,'binding':binding,'final_audit_sha256':final_audit_sha,
              'processed':len(rows),'expected':len(expected),'pending':pending,'eligible_counts':dict(counts),
              'eligible_scene_counts':scene_counts,'excluded':excluded,'verified_array_files':verified_files,
              'scene_count_gate_passed':gate,'eligible_samples_missing_wind':wind_missing,
              'numeric_max_abs_errors':dict(numeric_max),'eligible_crop_object_counts':dict(crop_totals),
              'max_relative_gamma_vs_postresampling_formula':max(paired_relative_difference,default=None),
              'gamma_formula_note':'Native gamma is computed before spatial resampling; dividing already-resampled sigma by cos(resampled angle) need not be identical.',
              'data_ready_for_model_protocol':gate and not wind_missing,
              'model_protocol_must_be_frozen_separately_before_fitting':True,
              'no_detection_scores_computed':True}
    name = 'cantarell_physical_progress.json' if args.progress else 'cantarell_physical_verification.json'
    (folder/name).write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:report[k] for k in ['scope','processed','expected','eligible_counts','eligible_scene_counts','verified_array_files','scene_count_gate_passed','eligible_samples_missing_wind']},indent=2))


if __name__=='__main__':
    main()
