"""Commit experimental choices before physical SAR model fitting or scoring."""

import sys as _sys
from pathlib import Path as _Path
_project_root = _Path(__file__).resolve().parents[2]
_sys.path.insert(0, str(_project_root))
_sys.path.insert(0, str(_project_root / "src"))

import hashlib
import json
from pathlib import Path


from scripts._provenance import source_matches
from scripts._paths import resolve_path
from scripts.cantarell.audit_cantarell_source import ROOT


def sha(path):
    return hashlib.sha256(resolve_path(path).read_bytes()).hexdigest()


def main():
    folder = ROOT/'docs/management'
    data_path = folder/'cantarell_data_protocol_v1.json'
    filters = [{'name':'none'}, {'name':'mean','size':7}, {'name':'median','size':7},
               {'name':'lee','size':7,'looks':1}, {'name':'lee','size':7,'looks':4}]
    thresholds = [{'name':'otsu'}]+[{'name':'niblack','size':size,'k':k} for size in [31,51] for k in [.2,.5]]
    candidates = [{'id':i*len(thresholds)+j,'filter':f,'threshold':t,
                   'morphology':{'operation':'none','min_area':64}}
                  for i,f in enumerate(filters) for j,t in enumerate(thresholds)]
    models = [{'id':i,'kind':'svm','C':c} for i,c in enumerate([.1,1.,10.])]
    models += [{'id':3+i*2+j,'kind':'cart','max_depth':depth,'min_leaf':leaf}
               for i,depth in enumerate([3,5]) for j,leaf in enumerate([5,20])]
    source_files = ['src/sar_oil/core.py','src/sar_oil/reference.py','src/sar_oil/models.py',
                    'src/sar_oil/evaluation.py','scripts/qposd/qposd_fast_features.py','scripts/cantarell/prepare_cantarell_physical.py']
    protocol = {
        'version':1,'data_protocol_sha256':sha(data_path),'generator_sha256':sha(Path(__file__)),
        'existing_algorithm_source_hashes':{p:sha(ROOT/p) for p in source_files},
        'scope':'Separate binary physical-SAR supplement; SOS remains primary, QPOSD remains the generic oil/look-alike evidence.',
        'prerequisites':['Finish all 173 preparation attempts with no unresolved operational errors.',
                         'Run strict complete-array verifier; require frozen per-split scene-count and wind-coverage gates.',
                         'Write and commit exact eligible sample manifest, input hashes and execution-code hashes before first detection score or model fitting.'],
        'radiometry_branches':['sigma0','gamma0'],
        'image_pipeline':['Use the aligned common 584x784 physical crop, no resizing.',
                          'Apply candidate speckle filter in LINEAR power.',
                          'Convert to 10*log10(max(value,1e-12)); clip and scale per-image 1st/99th percentiles to [0,1]; constant range maps to zero.',
                          'Apply Otsu or local Niblack, then minimum candidate area 64 with no morphology.',
                          'Extract the same eight existing features from the filtered normalized image and candidate regions.'],
        'candidate_configs':candidates,
        'candidate_grid_rationale':'Controlled 7x7 comparison of none/mean/median/Lee L1/L4 follows existing SOS coursework evidence; two Niblack windows and two k values test local scale/offset. This is a prespecified finite grid, not an exhaustive search or a theorem that Lee is best.',
        'screening':{
            'split':'val','backends':['numpy','reference'],'with_classifier':False,
            'comparisons':50,'comparison_count_note':'25 configurations x 2 radiometry branches; both operator backends for every comparison.',
            'ranking':['pooled object F1 descending','pooled object Recall descending','candidate id ascending'],
            'undefined_metric_rank':'below all defined values',
            'retention':'For each radiometry branch, retain union of best three unrestricted configurations and best three Niblack configurations. Maximum six per branch.',
            'limitation':'Staged search may discard a candidate generator that would become better after classification.'},
        'features':['area/image_area','covariance_elongation','bbox_extent','grid_perimeter_squared/(4*pi*area)',
                    'mean','std','mean_inner_boundary_sobel_magnitude','background_ring_contrast'],
        'feature_verification':{
            'numpy':'existing grouped-coordinate NumPy helper, same eight definitions as frozen SOS core',
            'reference':'existing regionprops/ndimage reference with matching grid-perimeter convention',
            'scope':'All retained-config validation regions; additionally compare grouped NumPy with original NumPy core on first eligible validation image per source scene.',
            'measurements':['max absolute error','max relative error with denominator max(abs(reference),1e-12)','MSE','region ID/partition agreement'],
            'failure_rule':'Investigate numerical/definition mismatches before selecting a winning model; never hide changed connected components.'},
        'training':{
            'split':'train','seed':2026,'labels':'region GT foreground fraction >=0.5 positive; <=0.05 negative; intermediate regions excluded only from training',
            'max_regions_per_class':10000,'sampling':'deterministic NumPy generator, sorted sample and region order, separately per branch/config; store selected rows',
            'scaler':'mean/std fit on selected train rows only, zero std replaced with 1',
            'models':models,'numpy_and_library_each':True,
            'svm':'Same squared-hinge L2 objective and regularized constant feature as frozen SOS; NumPy max_iter=10000, max_abs_gradient tolerance=1e-6; sklearn matching objective.',
            'cart':'Same Gini criterion and depths/leaves; record tie/float-precision disagreement rather than require identical trees.',
            'ineligible_model':'Record one-class training, nonfinite scores or failed NumPy SVM convergence; do not silently select failed models or omit failed grid rows.'},
        'selection':{
            'split':'val','metric':'pooled object F1 of full NumPy detector',
            'tie_break':['pooled Recall descending','candidate id ascending','model id ascending'],
            'primary':'Best gamma0 detector constrained to Niblack, because the required final physical branch includes angle normalization and adaptive thresholding.',
            'comparators':['Best unrestricted gamma0 detector','Best unrestricted sigma0 detector','Best Niblack sigma0 detector'],
            'disclosure':'Report the unrestricted-vs-constrained validation tradeoff; do not call the constrained winner globally optimal.',
            'freeze':'Commit selected config/model hashes and validation comparison tables before evaluating detection on test.'},
        'test':{
            'split':'test','ground_truth':'all cropped semantic-foreground 8-connected components, no minimum GT area',
            'matching':'one-to-one maximum valid matches then maximum IoU, threshold IoU>=0.5, existing evaluator',
            'primary_paired_ablation':'Apply the SAME gamma0-trained Niblack winner and all its parameters to gamma0 versus sigma0 on every eligible test tile. No classifier refit or threshold adjustment in this pair.',
            'additional_pipelines':'Frozen best unrestricted gamma0, unrestricted sigma0 and Niblack sigma0 winners; deduplicate identical pipelines but retain their role labels.',
            'backend_comparison':'Both NumPy/reference image operators on every test tile, with the SAME frozen NumPy classifier, report pixel and metric disagreement.',
            'metrics':['pooled object Precision/Recall/F1','pixel IoU/Dice','FP per image','edge/interior GT Recall','per-image and per-scene counts','single-run wall time with environment/worker count'],
            'bootstrap':{'unit':'whole source scene','paired':True,'replicates':2000,'seed':2026,'interval':'2.5/97.5 percentiles of paired F1 difference; disclose few scene clusters and undefined draws'},
            'interpretation':'Paired effect applies to this fixed gamma-trained detector. Independently optimized branch winners change multiple factors and are not a pure angle-normalization ablation.'},
        'wind':{'use':'Report context and per-scene/per-image values only; no wind-based GT editing, sample filtering, threshold tuning or causal look-alike claims.'},
        'outputs':['all candidate validation rows','all model training/validation rows including failures','portable model/scaler files','frozen selection manifest',
                   'test per-image counts/masks/overlays','paired scene bootstrap replicates','executed Jupyter notebook with figures and source hashes'],
        'honesty_limits':['Oil seepage is pooled with oil spill, not relabelled as oil-like background.',
                          'Object metrics count connected components per tile, not unique physical spill events; overlapping tiles within scenes can repeat a labelled region.',
                          'Gamma conversion is a geometric-area correction; uncorrected thermal noise and approximate registration remain.',
                          'No test result is available at protocol creation; no algorithm superiority is claimed in advance.']
    }
    path = folder/'cantarell_model_protocol_v1.json'
    if path.exists():
        if json.loads(path.read_text())!=protocol:
            raise ValueError('Refusing to overwrite a changed frozen model protocol')
    else:
        path.write_text(json.dumps(protocol,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'candidate_configurations':len(candidates),'radiometry_comparisons':2*len(candidates),
                      'classifier_configs':len(models),'maximum_full_model_pairs':2*6*len(models)},indent=2))


if __name__=='__main__':
    main()
