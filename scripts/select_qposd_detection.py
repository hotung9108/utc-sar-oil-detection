"""Compare frozen candidate configurations on validation, never on test."""
import json
from pathlib import Path

import numpy as np

from extract_qposd_regions import ROOT, digest, load_pair
from qposd_pipeline import infer
from qposd_metrics import detection, summarize_detections
from sar_oil.models import RegionModel
from train_qposd_classifiers import preflight, read

DEST = ROOT/'results/qposd'


def frozen_classifier():
    path = DEST/'classifier_selection.json'
    if not path.exists():
        raise ValueError('Classifier selection does not exist yet')
    selection = read(path)
    code = {'script_sha256': ROOT/'scripts/train_qposd_classifiers.py',
            'model_code_sha256': ROOT/'src/sar_oil/models.py',
            'metrics_code_sha256': ROOT/'scripts/qposd_metrics.py'}
    if any(selection[k] != digest(p) for k, p in code.items()):
        raise ValueError('Classifier code provenance changed')
    if any(digest(ROOT/name) != sha for name, sha in selection['inputs_sha256'].items()):
        raise ValueError('Classifier input provenance changed')
    winner = selection['configurations'][selection['winner_index']]
    model_path = ROOT/winner['model_path']
    if digest(model_path) != winner['model_sha256'] or not winner['numpy_converged']:
        raise ValueError('Saved classifier is changed or unconverged')
    return RegionModel.load(model_path), {
        'selection_sha256': digest(path), 'model_path': winner['model_path'],
        'model_sha256': winner['model_sha256'], 'config': winner['config']}


def main():
    output = DEST/'detection_selection.json'
    if output.exists():
        raise SystemExit('Existing detection selection found; refuse overwrite')
    try:
        protocol, _, inputs = preflight()
        model, model_record = frozen_classifier()
    except (ValueError, FileNotFoundError) as error:
        raise SystemExit(f'Stopped before validation: {error}')
    configs = protocol['detection']['candidate_configs']
    rows = [[] for _ in configs]
    for number in protocol['splits']['validation']:
        raw, truth, source = load_pair(number)
        for index, config in enumerate(configs):
            own = infer(raw, config, model, 'numpy')
            ref = infer(raw, config, model, 'reference')
            row = {'number': number, **source,
                   'numpy': detection(own['prediction'], truth),
                   'reference': detection(ref['prediction'], truth),
                   'numpy_regions': own['rows'], 'reference_regions': ref['rows'],
                   'numpy_seconds_single_run': own['seconds_single_run'],
                   'reference_seconds_single_run': ref['seconds_single_run'],
                   'candidate_disagreement_pixels': int(np.count_nonzero(own['candidate_mask'] != ref['candidate_mask'])),
                   'prediction_disagreement_pixels': int(np.count_nonzero(own['prediction'] != ref['prediction'])),
                   'feature_image_max_abs_error': float(np.max(np.abs(own['feature_image']-ref['feature_image'])))}
            rows[index].append(row)
            print(f"Validation image {number}, candidates {index}: numpy macro-F1={row['numpy']['macro_f1']}", flush=True)
    results = [{'index': i, 'config': config, 'images': group,
                'numpy_summary': summarize_detections([r['numpy'] for r in group]),
                'reference_summary': summarize_detections([r['reference'] for r in group])}
               for i, (config, group) in enumerate(zip(configs, rows))]
    eligible = [r for r in results if r['numpy_summary']['macro_f1'] is not None]
    if not eligible:
        raise ValueError('No defined validation scores; no selection')
    winner = max(eligible, key=lambda r: (r['numpy_summary']['macro_f1'], -r['index']))
    if any(digest(ROOT/name) != sha for name, sha in inputs.items()):
        raise ValueError('Input provenance changed during validation')
    _, after = frozen_classifier()
    if after != model_record:
        raise ValueError('Classifier changed during validation')
    report = {'script_sha256': digest(Path(__file__)),
              'pipeline_sha256': digest(ROOT/'scripts/qposd_pipeline.py'),
              'metrics_sha256': digest(ROOT/'scripts/qposd_metrics.py'),
              'inputs_sha256': inputs, 'classifier': model_record,
              'configurations': results, 'winner_index': winner['index'],
              'test_scored': False,
              'scope': 'Five validation images, all 10 predeclared candidate configurations. Reference image operators share the same frozen NumPy classifier to isolate operator differences. No fitting or test score used.'}
    temporary = output.with_suffix('.tmp')
    temporary.write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
    temporary.replace(output)
    print('Frozen detection selection saved:', output)


if __name__ == '__main__':
    main()
