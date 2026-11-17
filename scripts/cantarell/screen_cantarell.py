"""Run all frozen candidate comparisons on validation only, with resumable rows."""

import sys as _sys
from pathlib import Path as _Path
_project_root = _Path(__file__).resolve().parents[2]
_sys.path.insert(0, str(_project_root))
_sys.path.insert(0, str(_project_root / "src"))

import json
import time
from pathlib import Path

import numpy as np

from scripts.cantarell.cantarell_experiment_data import ROOT, MANIFEST, load_manifest, load_input, sha
from scripts.cantarell.cantarell_pipeline import candidates
from sar_oil.evaluation import counts, summarize


def rank(row):
    m = row['summary']['numpy']
    return (-(m['f1'] if m['f1'] is not None else -1),
            -(m['recall'] if m['recall'] is not None else -1),row['config_id'])


def main():
    manifest,protocol = load_manifest(['scripts/cantarell/screen_cantarell.py'])
    validation = [r for r in manifest['samples'] if r['split']=='val']
    if not validation:
        raise ValueError('No frozen validation images')
    binding = {'manifest_sha256':sha(MANIFEST),'script_sha256':sha(Path(__file__)),
               'model_protocol_sha256':manifest['model_protocol_sha256'],
               'operator_sha256':sha(ROOT/'scripts/cantarell/cantarell_pipeline.py')}
    checkpoint = ROOT/'.cache/cantarell_screen'/binding['manifest_sha256']/binding['script_sha256']
    checkpoint.mkdir(parents=True,exist_ok=True)
    aggregates = []
    for branch in protocol['radiometry_branches']:
        for config in protocol['candidate_configs']:
            rows = []
            for sample in validation:
                path = checkpoint/f"{branch}_{config['id']:02d}_{sample['sample']}.json"
                if path.exists():
                    row = json.loads(path.read_text())
                    if row['binding']!=binding or row['input_sha256']!=sample['sha256']:
                        raise ValueError('Candidate checkpoint binding mismatch')
                else:
                    raw,truth = load_input(sample,branch)
                    started = time.perf_counter()
                    outputs = {backend:candidates(raw,config,backend) for backend in ['numpy','reference']}
                    row = {'binding':binding,'sample':sample['sample'],'scene':sample['scene'],
                           'input_sha256':sample['sha256'],'branch':branch,'config_id':config['id'],
                           'counts':{backend:counts(result['candidate_mask'],truth) for backend,result in outputs.items()},
                           'mask_disagreement_pixels':int(np.count_nonzero(outputs['numpy']['candidate_mask']!=outputs['reference']['candidate_mask'])),
                           'normalized_image_max_abs_error':float(np.max(np.abs(outputs['numpy']['image']-outputs['reference']['image']))),
                           'seconds_single_run':{backend:result['seconds_single_run'] for backend,result in outputs.items()},
                           'seconds_including_evaluation':time.perf_counter()-started}
                    temp = path.with_suffix('.json.tmp')
                    temp.write_text(json.dumps(row,indent=2)+'\n',encoding='utf-8')
                    temp.replace(path)
                rows.append(row)
            summary = {backend:summarize([r['counts'][backend] for r in rows]) for backend in ['numpy','reference']}
            aggregates.append({'branch':branch,'config_id':config['id'],'config':config,'summary':summary,'rows':rows,
                               'mask_disagreement_pixels':sum(r['mask_disagreement_pixels'] for r in rows)})
            print(f"{branch} config {config['id']:02d}: val F1={summary['numpy']['f1']}, reference={summary['reference']['f1']}",flush=True)
    retained = {}
    for branch in protocol['radiometry_branches']:
        ordered = sorted([r for r in aggregates if r['branch']==branch],key=rank)
        adaptive = [r for r in ordered if r['config']['threshold']['name']=='niblack']
        retained[branch] = sorted({r['config_id'] for r in ordered[:3]+adaptive[:3]})
    result = {'binding':binding,'validation_samples':len(validation),'comparisons':aggregates,
              'retained_candidate_ids':retained,'ranking':'NumPy pooled F1, Recall, stable ID; no timing tie-break',
              'complete':len(aggregates)==50,'test_accessed':False,'classifiers_fitted':False,
              'limits':['Candidate-only scores, not final classified detection.',
                        'Two operator backends on every validation input; a staged search, not exhaustive full-model optimization.']}
    output = ROOT/'results/cantarell'
    output.mkdir(parents=True,exist_ok=True)
    destination = output/'screen.json'
    if destination.exists():
        if json.loads(destination.read_text())!=result:
            raise ValueError('Refusing to overwrite changed screening evidence')
    else:
        destination.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'complete':result['complete'],'retained':retained},indent=2))


if __name__=='__main__':
    main()
