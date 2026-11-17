"""Verify operators on the two train development tiles, without reading GT.

This is not candidate ranking or a detection score. All frozen configurations run.
"""

import sys as _sys
from pathlib import Path as _Path
_project_root = _Path(__file__).resolve().parents[2]
_sys.path.insert(0, str(_project_root))
_sys.path.insert(0, str(_project_root / "src"))

import hashlib
import json
from pathlib import Path

import numpy as np


from scripts._provenance import source_matches
from scripts._paths import resolve_path
from scripts.cantarell.audit_cantarell_source import ROOT, REVISION
from scripts.cantarell.cantarell_pipeline import candidates, extract
from sar_oil import core, reference


def sha(path):
    return hashlib.sha256(resolve_path(path).read_bytes()).hexdigest()


def error(a,b):
    delta = np.asarray(a)-np.asarray(b)
    return {'max_abs':float(np.max(np.abs(delta),initial=0)),
            'max_relative':float(np.max(np.abs(delta)/np.maximum(np.abs(b),1e-12),initial=0)),
            'mse':float(np.mean(delta**2)) if delta.size else 0.,
            'allclose_atol_1e6_rtol_1e5':bool(np.allclose(a,b,atol=1e-6,rtol=1e-5))}


def partition_equal(a,b):
    if not np.array_equal(a>0,b>0):
        return False
    pairs = np.unique(a.astype(np.int64)*(int(b.max())+1)+b)
    return len(pairs)==int(a.max())+1==int(b.max())+1


def compare(raw,config,features=True):
    ours = candidates(raw,config,'numpy')
    theirs = candidates(raw,config,'reference')
    shared_reference_labels = reference.label(ours['candidate_mask'])
    partition = partition_equal(ours['labels'],shared_reference_labels)
    if not partition:
        raise ValueError('Connected components disagree on the SAME candidate mask')
    row = {'config_id':config['id'],'filtered_linear_error':error(ours['filtered_linear'],theirs['filtered_linear']),
           'normalized_error':error(ours['image'],theirs['image']),
           'candidate_mask_disagreement':int(np.count_nonzero(ours['candidate_mask']!=theirs['candidate_mask'])),
           'numpy_regions':int(ours['labels'].max()),'reference_regions':int(theirs['labels'].max()),
           'same_mask_partition_equal':partition}
    if features:
        X,ids = extract(ours['image'],ours['labels'],'numpy')
        ref,ref_ids = extract(ours['image'],ours['labels'],'reference')
        if ids!=ref_ids:
            raise ValueError('Feature IDs disagree on shared labels')
        row['shared_image_and_labels_feature_error'] = error(X,ref)
        row['shared_feature_rows'] = len(ids)
    return row


def main():
    folder = ROOT/'docs/management'
    protocol_path = folder/'cantarell_model_protocol_v1.json'
    protocol = json.loads(protocol_path.read_text())
    for path,expected in protocol['existing_algorithm_source_hashes'].items():
        if (not source_matches(ROOT/path, expected, sha(ROOT/path))):
            raise ValueError('Frozen source algorithm changed')
    progress = json.loads((folder/'cantarell_physical_progress.json').read_text())
    for path,expected in progress['binding']['source_hashes'].items():
        if (not source_matches(ROOT/'scripts'/path, expected, sha(ROOT/'scripts'/path))):
            raise ValueError('Prepared development source binding is stale')
    directory = ROOT/'.cache/cantarell_source'/REVISION/'physical_prepared'/progress['run_key']
    rows,input_receipts = [],[]
    for sample in ['IMG_01_TILE_001','IMG_01_TILE_002']:
        receipt = json.loads((directory/f'{sample}.json').read_text())
        if not receipt['eligible'] or receipt['split']!='train' or receipt['binding']!=progress['binding']:
            raise ValueError('Development sample is not an eligible frozen train input')
        path = ROOT/receipt['file']
        if (not source_matches(path, receipt['sha256'], sha(path))):
            raise ValueError('Prepared development array hash mismatch')
        input_receipts.append({'sample':sample,'file':receipt['file'],'sha256':receipt['sha256']})
        with np.load(path,allow_pickle=False) as data:
            for branch in ['sigma0','gamma0']:
                raw = data[branch]
                for config in protocol['candidate_configs']:
                    rows.append({'sample':sample,'branch':branch,**compare(raw,config)})
                print(f'Verified {sample}/{branch}: all 25 configurations',flush=True)
    rng = np.random.default_rng(2026)
    synthetic = {'zero':np.zeros((16,17)), 'constant':np.ones((16,17))*.0123,
                 'small_dynamic_range':10**rng.uniform(-8,3,size=(17,19))}
    synthetic_rows = []
    for name,raw in synthetic.items():
        for config in protocol['candidate_configs']:
            row = compare(raw,config,features=False)
            if name in ['zero','constant'] and (row['numpy_regions'] or row['reference_regions']):
                raise ValueError('Constant image unexpectedly creates dark candidates')
            synthetic_rows.append({'case':name,**row})
    invalid = [np.array([[0.,-1.],[1.,2.]]),np.array([[0.,np.nan],[1.,2.]]),np.zeros(4)]
    for raw in invalid:
        try:
            candidates(raw,protocol['candidate_configs'][0])
        except ValueError:
            pass
        else:
            raise ValueError('Invalid physical input was accepted')
    source_names = ['scripts/cantarell/cantarell_pipeline.py','scripts/cantarell/verify_cantarell_operators.py',
                    'src/sar_oil/core.py','src/sar_oil/reference.py','scripts/qposd/qposd_fast_features.py']
    result = {'model_protocol_sha256':sha(protocol_path),'source_hashes':{p:sha(ROOT/p) for p in source_names},
              'input_receipts':input_receipts,'real_comparisons':len(rows),'rows':rows,
              'synthetic_comparisons':len(synthetic_rows),'synthetic_rows':synthetic_rows,
              'invalid_input_checks_passed':len(invalid),'ground_truth_read':False,'model_fitted':False,
              'detection_metrics_computed':False,'configurations_ranked':False,
              'all_real_shared_features_close':all(r['shared_image_and_labels_feature_error']['allclose_atol_1e6_rtol_1e5'] for r in rows),
              'total_real_candidate_disagreement_pixels':sum(r['candidate_mask_disagreement'] for r in rows),
              'limits':['Two train development tiles from one scene, not all eligible inputs.',
                        'Feature comparison uses the same NumPy image and labels to isolate feature formulas; separate operator masks may differ.',
                        'No ground-truth detection accuracy or algorithm superiority follows from numerical agreement.']}
    (folder/'cantarell_operator_verification.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:result[k] for k in ['real_comparisons','synthetic_comparisons','all_real_shared_features_close','total_real_candidate_disagreement_pixels','ground_truth_read']},indent=2))


if __name__=='__main__':
    main()
