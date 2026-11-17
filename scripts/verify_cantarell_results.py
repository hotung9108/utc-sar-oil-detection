"""Independently reconstruct grids, winner selection and test counts from artifacts."""
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image

from cantarell_experiment_data import ROOT, MANIFEST, load_manifest, sha
sys.path.insert(0,str(ROOT/'src'))
from sar_oil.evaluation import counts, summarize
from evaluate_cantarell import scene_bootstrap
from select_cantarell_required_filter import choose, PROTOCOL as FILTER_PROTOCOL

BASE = ROOT / 'results/cantarell'


def read(name):
    return json.loads((BASE / name).read_text())


def require(condition, message):
    if not condition:
        raise ValueError(message)


def main():
    manifest, protocol = load_manifest()
    screen, training, selection, evaluation = [read(n) for n in
        ('screen.json', 'validation.json', 'selection.json', 'evaluation.json')]
    population = {split:{r['sample']:r for r in manifest['samples'] if r['split']==split}
                  for split in ('train','val','test')}
    expected_grid = {(b,c['id']) for b in protocol['radiometry_branches'] for c in protocol['candidate_configs']}
    require(len(screen['comparisons']) == len(expected_grid) and
            {(r['branch'],r['config_id']) for r in screen['comparisons']} == expected_grid, 'Incomplete candidate grid')
    for row in screen['comparisons']:
        require(len(row['rows']) == len(population['val']) and
                {r['sample'] for r in row['rows']} == set(population['val']), 'Candidate validation population changed')
        for backend in ('numpy','reference'):
            require(summarize([r['counts'][backend] for r in row['rows']]) == row['summary'][backend], 'Candidate summary mismatch')
    retained = {}
    def candidate_rank(r):
        m = r['summary']['numpy']
        return (-(m['f1'] if m['f1'] is not None else -1), -(m['recall'] if m['recall'] is not None else -1), r['config_id'])
    for branch in protocol['radiometry_branches']:
        ordered = sorted([r for r in screen['comparisons'] if r['branch']==branch], key=candidate_rank)
        adaptive = [r for r in ordered if r['config']['threshold']['name']=='niblack']
        retained[branch] = sorted({r['config_id'] for r in ordered[:3]+adaptive[:3]})
    require(retained == screen['retained_candidate_ids'], 'Retained candidates violate screening rule')
    expected_models = {(b,c,m['id']) for b,ids in retained.items() for c in ids for m in protocol['training']['models']}
    actual_models = {(r['branch'],r['config_id'],r['model_id']) for r in training['rows']}
    require(len(training['rows']) == len(expected_models) and actual_models == expected_models, 'Incomplete model grid')
    require(training['binding']['manifest_sha256']==sha(MANIFEST) and
            training['binding']['script_sha256']==sha(ROOT/'scripts/train_cantarell.py') and
            training['binding']['screen_sha256']==sha(BASE/'screen.json'), 'Training binding changed')
    for row in training['rows']:
        require(row['binding'] == training['binding'], 'Model row binding mismatch')
        if not row['eligible']:
            require(bool(row.get('error')), 'Excluded model lacks a reason')
            continue
        require(len(row['per_image']) == len(population['val']) and
                {r['sample'] for r in row['per_image']} == set(population['val']), 'Model validation population changed')
        for backend in ('numpy','reference'):
            require(row['diagnostics'][backend]['converged'], 'Selected-grid eligible model unconverged')
            require(summarize([r['counts'][backend] for r in row['per_image']]) == row['metrics'][backend], 'Model summary mismatch')
        require(sha(ROOT/row['model_file']) == row['model_sha256'], 'Model file changed')
        saved = json.loads((ROOT/row['model_file']).read_text())
        samples = read(f"training_rows/{row['branch']}_{row['config_id']:02d}.json")
        require(all(r['sample'] in population['train'] for r in samples['rows']), 'Non-train sample used in fitting')
        X, y = np.asarray(samples['features']), np.asarray(samples['labels'])
        require(len(X) == len(y) == len(samples['rows']) == row['training_regions'], 'Training rows incomplete')
        require(np.bincount(y,minlength=2).tolist() == row['class_counts'], 'Training class counts mismatch')
        # Match RegionModel's selected-column array layout/reduction order exactly.
        selected_X = X[:,saved['columns']]
        mean, scale = selected_X.mean(axis=0), selected_X.std(axis=0)
        scale[scale<1e-12] = 1
        require(np.array_equal(mean, saved['mean']) and np.array_equal(scale, saved['scale']), 'Scaler differs from train-only statistics')
    require(selection['validation_sha256']==sha(BASE/'validation.json'), 'Selection validation hash changed')
    def model_rank(r):
        m = r['metrics']['numpy']
        return (-(m['f1'] if m['f1'] is not None else -1), -(m['recall'] if m['recall'] is not None else -1), r['config_id'], r['model_id'])
    roles = [('primary','gamma0',True),('gamma_unrestricted','gamma0',False),
             ('sigma_unrestricted','sigma0',False),('sigma_adaptive','sigma0',True)]
    for role,branch,adaptive in roles:
        candidates = [r for r in training['rows'] if r['eligible'] and r['branch']==branch
                      and (not adaptive or r['config']['threshold']['name']=='niblack')]
        winner = min(candidates,key=model_rank)
        require(all(winner[k]==v for k,v in selection['winners'][role].items()), 'Winner violates frozen rule')
    require(evaluation['binding']['selection_sha256']==sha(BASE/'selection.json') and
            evaluation['binding']['script_sha256']==sha(ROOT/'scripts/evaluate_cantarell.py'), 'Evaluation binding changed')
    supplement = read('requirements_selection.json')
    expected_filter = choose(training['rows'])
    require(supplement['protocol_sha256']==sha(FILTER_PROTOCOL) and
            all(expected_filter[k]==v for k,v in supplement['selected'].items()), 'Required-filter winner mismatch')
    require(evaluation['binding']['required_filter_selection_sha256']==sha(BASE/'requirements_selection.json'), 'Required-filter test binding changed')
    require(set(evaluation['roles']) == {r[0] for r in roles} | {'paired_sigma_same_model','filtered_adaptive','paired_sigma_filtered_model'}, 'Missing test role')
    verified_masks = 0
    for role, group in evaluation['roles'].items():
        if role=='paired_sigma_same_model':
            selected = dict(selection['winners']['primary'],branch='sigma0')
        elif role=='filtered_adaptive':
            selected = supplement['selected']
        elif role=='paired_sigma_filtered_model':
            selected = dict(supplement['selected'],branch='sigma0')
        else:
            selected = selection['winners'][role]
        require(group['selection']==selected, 'Test did not use the frozen model/configuration')
        require(len(group['per_image'])==len(population['test']) and
                {r['sample'] for r in group['per_image']} == set(population['test']), 'Test population changed')
        for row in group['per_image']:
            sample = population['test'][row['sample']]
            require(row['scene']==sample['scene'] and row['input_sha256']==sample['sha256'], 'Test source changed')
            folder = BASE/'test_outputs'/role/row['sample']
            for name,expected in row['artifact_sha256'].items():
                require(sha(folder/name)==expected, 'Output artifact changed')
            with Image.open(folder/'mask.png') as im:
                prediction = np.asarray(im)>0
            with Image.open(folder/'truth.png') as im:
                truth = np.asarray(im)>0
            require(sha(ROOT/sample['file'])==sample['sha256'], 'Physical NPZ changed')
            with np.load(ROOT/sample['file'],allow_pickle=False) as arrays:
                require(np.array_equal(truth,arrays['truth']), 'Exported GT differs from frozen input')
            require(counts(prediction,truth)==row['counts']['numpy'], 'Saved mask does not reproduce object counts')
            verified_masks += 1
        for backend in ('numpy','reference'):
            require(summarize([r['counts'][backend] for r in group['per_image']])==group['metrics'][backend], 'Test summary mismatch')
    bootstrap = read('angle_bootstrap.json')
    rebuilt = scene_bootstrap(evaluation['roles']['primary']['per_image'],evaluation['roles']['paired_sigma_same_model']['per_image'])
    require(all(bootstrap[k]==v for k,v in rebuilt.items()), 'Paired bootstrap differs')
    filtered_bootstrap = read('angle_bootstrap_filtered.json')
    rebuilt_filtered = scene_bootstrap(evaluation['roles']['filtered_adaptive']['per_image'], evaluation['roles']['paired_sigma_filtered_model']['per_image'])
    require(all(filtered_bootstrap[k]==v for k,v in rebuilt_filtered.items()), 'Filtered paired bootstrap differs')
    output = {'passed':True,'candidate_comparisons':len(expected_grid),'model_pairs':len(expected_models),
              'verified_test_masks':verified_masks,'script_sha256':sha(Path(__file__)),
              'input_sha256':{n:sha(BASE/n) for n in ('screen.json','validation.json','selection.json','requirements_selection.json',
                                                    'evaluation.json','angle_bootstrap.json','angle_bootstrap_filtered.json')},
              'scope':'Reconstructed grids, train-only scalers, winner rules, saved-mask object counts and paired bootstrap; not a new model fit'}
    path = ROOT/'docs/management/cantarell_results_verification.json'
    path.write_text(json.dumps(output,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(output,indent=2))


if __name__=='__main__':
    main()
