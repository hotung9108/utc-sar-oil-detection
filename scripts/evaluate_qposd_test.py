"""Evaluate the frozen QPOSD winners on all five reserved test images once."""
import argparse
import json
from pathlib import Path

import numpy as np
from PIL import Image

from extract_qposd_regions import ROOT, digest, extract, load_pair
from qposd_metrics import classification, detection, summarize_detections
from qposd_pipeline import infer
from select_qposd_detection import frozen_classifier
from train_qposd_classifiers import preflight, read

DEST = ROOT/'results/qposd'


def frozen_detection(protocol, model_record):
    path = DEST/'detection_selection.json'
    if not path.exists():
        raise ValueError('Detection selection does not exist yet')
    selection = read(path)
    for key, source in (
            ('script_sha256', 'scripts/select_qposd_detection.py'),
            ('pipeline_sha256', 'scripts/qposd_pipeline.py'),
            ('feature_code_sha256', 'scripts/qposd_fast_features.py'),
            ('metrics_sha256', 'scripts/qposd_metrics.py')):
        if selection[key] != digest(ROOT/source):
            raise ValueError('Detection implementation changed since selection')
    if selection['classifier'] != model_record:
        raise ValueError('Classifier differs from validation selection')
    for name, sha in selection['inputs_sha256'].items():
        if digest(ROOT/name) != sha:
            raise ValueError('Detection inputs changed since validation')
    candidates = selection['configurations']
    expected = protocol['detection']['candidate_configs']
    if [r['config'] for r in candidates] != expected or len(candidates) != 10:
        raise ValueError('Candidate search differs from frozen protocol')
    for index, row in enumerate(candidates):
        if row['index'] != index or [r['number'] for r in row['images']] != protocol['splits']['validation']:
            raise ValueError('Incorrect validation population or configuration ID')
        recalculated = summarize_detections([r['numpy'] for r in row['images']])
        if recalculated != row['numpy_summary']:
            raise ValueError('Saved validation summary does not match image counts')
    eligible = [r for r in candidates if r['numpy_summary']['macro_f1'] is not None]
    winner = max(eligible, key=lambda r: (r['numpy_summary']['macro_f1'], -r['index']))
    if winner['index'] != selection['winner_index']:
        raise ValueError('Saved winner violates validation selection rule')
    return winner['config'], {'selection_sha256': digest(path),
                              'winner_index': winner['index'], 'config': winner['config']}


def write(path, value):
    path.write_text(json.dumps(value, indent=2)+'\n', encoding='utf-8')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--preflight-only', action='store_true')
    args = parser.parse_args()
    output = DEST/'evaluation.json'
    artifacts = DEST/'test'
    if output.exists() or artifacts.exists():
        raise SystemExit('Test evidence already exists; refuse overwrite or retuning')
    try:
        protocol, _, inputs = preflight()
        model, classifier_record = frozen_classifier()
        config, detector_record = frozen_detection(protocol, classifier_record)
    except (ValueError, FileNotFoundError) as error:
        raise SystemExit(f'Stopped before test: {error}')
    if args.preflight_only:
        print('Frozen selections verified; no test features or scores computed.')
        return
    artifacts.mkdir()
    rows, conditional = [], []
    for number in protocol['splits']['test']:
        raw, truth, source = load_pair(number)
        own = infer(raw, config, model, 'numpy')
        ref = infer(raw, config, model, 'reference')
        masks = {}
        for name, result in (('numpy', own), ('reference', ref)):
            path = artifacts/f'image{number}_{name}_classes.png'
            Image.fromarray(result['prediction']).save(path)
            with Image.open(path) as image:
                if not np.array_equal(np.asarray(image), result['prediction']):
                    raise ValueError('Saved class raster differs from prediction')
            masks[name] = {'path': path.relative_to(ROOT).as_posix(), 'sha256': digest(path),
                           'classes': {'0': 'background', '1': 'oil', '2': 'look_alike'}}
        # Reference geometry is read only for this explicitly conditional score.
        features = extract(number, digest(DEST/'protocol.json'))
        feature_path = artifacts/f'image{number}_reference_regions.json'
        write(feature_path, features)
        X = np.asarray([r['features'] for r in features['rows']], float).reshape(-1, 8)
        y = np.asarray([r['label'] for r in features['rows']], int)
        scores = model.scores(X)
        conditional_rows = [dict(image=number, object_id=r['object_id'], area=r['area'],
                                 truth=int(t), score=float(s), prediction=int(s > 0))
                            for r, t, s in zip(features['rows'], y, scores)]
        conditional.extend(conditional_rows)
        row = {'number': number, **source,
               'numpy': detection(own['prediction'], truth),
               'reference': detection(ref['prediction'], truth),
               'numpy_regions': own['rows'], 'reference_regions': ref['rows'],
               'numpy_seconds_single_run': own['seconds_single_run'],
               'reference_seconds_single_run': ref['seconds_single_run'],
               'candidate_disagreement_pixels': int(np.count_nonzero(own['candidate_mask'] != ref['candidate_mask'])),
               'prediction_disagreement_pixels': int(np.count_nonzero(own['prediction'] != ref['prediction'])),
               'saved_masks': masks, 'conditional_classification': classification(y, scores > 0),
               'reference_region_features': {'path': feature_path.relative_to(ROOT).as_posix(),
                                             'sha256': digest(feature_path)}}
        rows.append(row)
        write(artifacts/f'image{number}_evaluation.json', row)
        print(f"Test image {number}: object macro-F1={row['numpy']['macro_f1']}", flush=True)
    if any(digest(ROOT/name) != sha for name, sha in inputs.items()):
        raise ValueError('Input evidence changed during test evaluation')
    _, classifier_after = frozen_classifier()
    _, detector_after = frozen_detection(protocol, classifier_after)
    if classifier_after != classifier_record or detector_after != detector_record:
        raise ValueError('Frozen selections changed during evaluation')
    report = {'complete': len(rows) == len(protocol['splits']['test']),
              'script_sha256': digest(Path(__file__)),
              'pipeline_sha256': digest(ROOT/'scripts/qposd_pipeline.py'),
              'feature_code_sha256': digest(ROOT/'scripts/qposd_fast_features.py'),
              'metrics_sha256': digest(ROOT/'scripts/qposd_metrics.py'),
              'inputs_sha256': inputs, 'classifier': classifier_record,
              'detector': detector_record, 'images': rows,
              'numpy_summary': summarize_detections([r['numpy'] for r in rows]),
              'reference_summary': summarize_detections([r['reference'] for r in rows]),
              'conditional_classification': classification(
                  [r['truth'] for r in conditional], [r['prediction'] for r in conditional]),
              'conditional_rows': conditional,
              'scope': 'All five reserved source images; no fit or selection using test scores. Conditional classification uses supplied GT geometry and must not be called detection. Scene independence unverified; generic look-alike labels only. Reference operators share the frozen NumPy classifier.'}
    temporary = output.with_suffix('.tmp')
    write(temporary, report)
    temporary.replace(output)
    print('Saved frozen test evaluation:', output)


if __name__ == '__main__':
    main()
