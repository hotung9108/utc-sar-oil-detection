"""Select QPOSD reference-region classifiers on validation only.

Requires all structural/visual gates and all train/validation features. Never
extracts test features or selects with test scores. Does not evaluate detection.
"""

import sys as _sys
from pathlib import Path as _Path
_project_root = _Path(__file__).resolve().parents[2]
_sys.path.insert(0, str(_project_root))
_sys.path.insert(0, str(_project_root / "src"))

import argparse
import json
from pathlib import Path
import time
import warnings

import numpy as np


from scripts._provenance import source_matches
from scripts._paths import resolve_path
from scripts.qposd.extract_qposd_regions import ROOT, digest
from scripts.qposd.prepare_qposd_protocol import definition
from scripts.qposd.qposd_metrics import classification
from sar_oil.models import RegionModel

DEST = ROOT/'results/qposd'


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def reject_cross_split_overlap(pair, split_of):
    first, second = pair['first'], pair['second']
    if split_of[first] != split_of[second] and any(t['entire_overlap_exact'] for t in pair['translations']):
        raise ValueError(f'Exact overlap crosses splits: {first}/{second}; revise groups before fitting')


def preflight():
    protocol_path = DEST/'protocol.json'
    protocol = read(protocol_path)
    if protocol != definition():
        raise ValueError('Protocol differs from frozen experiment definition')
    complete = ROOT/'docs/management/qposd_matched_full_audit.json'
    visual_path = ROOT/'docs/management/qposd_pair_visual_review.json'
    if not complete.is_file():
        raise ValueError('Full 24-pair MAT audit is not complete')
    audit, visual = read(complete), read(visual_path)
    masks_path = ROOT/'docs/management/qposd_mask_audit.json'
    masks = {r['member']: r for r in read(masks_path)['masks']}
    expected = set(sum(protocol['splits'].values(), []))
    if set(audit['selection']) != expected or len(audit['pairs']) != len(expected):
        raise ValueError('Full audit population differs from protocol')
    reviewed = {r['number']: r for r in visual['pairs']}
    if not visual['visual_review_completed'] or not expected.issubset(visual['reviewed_numbers']):
        raise ValueError('Visual review does not cover all eligible pairs')
    full = {}
    for row in audit['pairs']:
        number = int(Path(row['member']).stem.replace('image', ''))
        if number in full or not row['crc32_verified'] or not row['matching_spatial_shape']:
            raise ValueError('Duplicate, CRC-unverified, or mismatched pair')
        details = row['variables']['T']
        if not details['all_finite'] or details['shape'][-1] != 9 or details['channels'][0]['min'] < 0:
            raise ValueError('Invalid full-array numeric check')
        path = ROOT/'data/lookalike_sources/qposd_features'/Path(row['member']).name
        if (not source_matches(path, row['sha256'], digest(path))) or reviewed[number]['mat_sha256'] != row['sha256']:
            raise ValueError(f'Full MAT hash/visual provenance mismatch: {number}')
        mask = masks[row['mask_member']]
        if (not source_matches(ROOT/mask['local_path'], mask['sha256'], digest(ROOT/mask['local_path']))) or reviewed[number]['mask_sha256'] != mask['sha256']:
            raise ValueError(f'Mask hash/visual provenance mismatch: {number}')
        full[number] = row
    if set(full) != expected:
        raise ValueError('Full audit IDs do not cover protocol population')
    overlap_path = ROOT/'docs/management/qposd_overlap_all24.json'
    if not overlap_path.is_file():
        raise ValueError('Full-population exact-overlap screen is incomplete')
    overlap = read(overlap_path)
    if (set(overlap['selection']) != expected
            or (not source_matches(ROOT/'scripts/qposd/audit_qposd_overlap.py', overlap['script_sha256'], digest(ROOT/'scripts/qposd/audit_qposd_overlap.py')))):
        raise ValueError('Overlap audit population/code differs')
    split_of = {n: name for name, numbers in protocol['splits'].items() for n in numbers}
    seen_pairs = set()
    for pair in overlap['pairs']:
        first, second = pair['first'], pair['second']
        key = tuple(sorted((first, second)))
        if first not in expected or second not in expected or first == second or key in seen_pairs:
            raise ValueError('Invalid or repeated overlap pair')
        seen_pairs.add(key)
        reject_cross_split_overlap(pair, split_of)
    if len(seen_pairs) != len(expected)*(len(expected)-1)//2:
        raise ValueError('Not every source pair was screened for exact overlap')
    for number in expected:
        if overlap['inputs'][str(number)]['mat_sha256'] != full[number]['sha256']:
            raise ValueError('Overlap audit source hash changed')
    census = read(ROOT/'docs/management/qposd_object_audit.json')
    census = {r['number']: r for r in census['rows']}
    inputs, groups = {}, {}
    for split in ('train', 'validation'):
        X, y, identities = [], [], []
        for number in protocol['splits'][split]:
            path = DEST/f'regions/image{number}.json'
            if not path.is_file():
                raise ValueError(f'Missing {split} features: {number}')
            record = read(path)
            required = {
                'number': number, 'protocol_sha256': digest(protocol_path),
                'mat_sha256': full[number]['sha256'],
                'mask_sha256': reviewed[number]['mask_sha256'],
                'extraction_script_sha256': digest(ROOT/'scripts/qposd/extract_qposd_regions.py'),
                'core_sha256': digest(ROOT/'src/sar_oil/core.py'),
                'reference_sha256': digest(ROOT/'src/sar_oil/reference.py')}
            if (not source_matches(ROOT/'scripts/qposd/extract_qposd_regions.py',
                                   record.get('extraction_script_sha256')) or
                    any(record.get(k) != v for k, v in required.items()
                        if k != 'extraction_script_sha256')):
                raise ValueError(f'Stale feature provenance: {number}')
            rows = record['rows']
            if [r['object_id'] for r in rows] != list(range(1, len(rows)+1)):
                raise ValueError('Missing/duplicate feature object IDs')
            for value, name in ((1, 'oil'), (0, 'look_alike')):
                objects = [r for r in rows if r['label'] == value]
                counts = census[number]['classes'][name]
                if len(objects) != counts['objects'] or sum(r['area'] for r in objects) != counts['pixels']:
                    raise ValueError('Feature population differs from full reference census')
            for row in rows:
                X.append(row['features'])
                y.append(row['label'])
                identities.append({'image': number, 'object_id': row['object_id'],
                                   'area': row['area'], 'truth': row['label']})
            inputs[path.relative_to(ROOT).as_posix()] = digest(path)
        X, y = np.asarray(X, float), np.asarray(y, int)
        if X.shape != (len(y), 8) or not np.isfinite(X).all() or set(y) != {0, 1}:
            raise ValueError(f'Invalid {split} feature matrix or class coverage')
        groups[split] = (X, y, identities)
    inputs.update({p.relative_to(ROOT).as_posix(): digest(p) for p in
                   (protocol_path, complete, visual_path, masks_path, overlap_path,
                    ROOT/'docs/management/qposd_object_audit.json')})
    return protocol, groups, inputs


def compare_models(models, train, validation):
    X, y, _ = train
    V, truth, identities = validation
    results, fitted = [], []
    for index, config in enumerate(models):
        own = RegionModel(config['kind'], backend='numpy', **config['params'])
        reference = RegionModel(config['kind'], backend='reference', **config['params'])
        start = time.perf_counter()
        own.fit(X, y)
        numpy_seconds = time.perf_counter()-start
        start = time.perf_counter()
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter('always')
            reference.fit(X, y)
        reference_seconds = time.perf_counter()-start
        scores, ref_scores = own.scores(V), reference.scores(V)
        if not np.isfinite(scores).all() or not np.isfinite(ref_scores).all():
            raise ValueError('Nonfinite validation scores')
        metrics = classification(truth, scores > 0)
        results.append({
            'index': index, 'config': config, 'numpy_converged': bool(own.converged),
            'numpy_validation': metrics,
            'reference_validation': classification(truth, ref_scores > 0),
            'reference_warnings': [str(w.message) for w in caught],
            'score_max_abs_difference': float(np.max(np.abs(scores-ref_scores))),
            'prediction_agreement': float(np.mean((scores > 0) == (ref_scores > 0))),
            'numpy_fit_seconds_single_run': numpy_seconds,
            'reference_fit_seconds_single_run': reference_seconds,
            'numpy_iterations': getattr(own.estimator, 'iterations', None),
            'numpy_gradient_max': getattr(own.estimator, 'gradient_max', None),
            'numpy_objective': getattr(own.estimator, 'objective', None),
            'validation_rows': [dict(row, numpy_score=float(s), reference_score=float(r))
                                for row, s, r in zip(identities, scores, ref_scores)]})
        fitted.append(own)
        print(f"Model {index}: converged={own.converged}, validation macro-F1={metrics['macro_f1']}", flush=True)
    eligible = [r for r in results if r['numpy_converged'] and r['numpy_validation']['macro_f1'] is not None]
    if not eligible:
        raise ValueError('No converged eligible classifier; no selection made')
    winner = max(eligible, key=lambda r: (r['numpy_validation']['macro_f1'], -r['index']))
    return results, fitted, winner['index']


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--preflight-only', action='store_true')
    args = parser.parse_args()
    try:
        protocol, groups, inputs = preflight()
    except (ValueError, FileNotFoundError) as error:
        raise SystemExit(f'Preflight stopped before fitting: {error}')
    if args.preflight_only:
        print('All gates passed; no fitting performed.')
        return
    output = DEST/'classifier_selection.json'
    if output.exists() or (DEST/'models').exists():
        raise SystemExit('Existing model evidence found; refuse overwrite')
    results, models, winner = compare_models(protocol['conditional_classification']['models'],
                                             groups['train'], groups['validation'])
    # Bind saved output to unchanged inputs after fitting as well.
    if any((not source_matches(ROOT/name, sha, digest(ROOT/name))) for name, sha in inputs.items()):
        raise SystemExit('Input evidence changed during fitting')
    (DEST/'models').mkdir()
    for index, model in enumerate(models):
        target = DEST/f'models/model{index}.json'
        model.save(target)
        restored = RegionModel.load(target)
        if not np.array_equal(model.scores(groups['validation'][0]), restored.scores(groups['validation'][0])):
            raise ValueError('Model serialization changed predictions')
        results[index]['model_path'] = target.relative_to(ROOT).as_posix()
        results[index]['model_sha256'] = digest(target)
    report = {'script_sha256': digest(Path(__file__)),
              'model_code_sha256': digest(ROOT/'src/sar_oil/models.py'),
              'metrics_code_sha256': digest(ROOT/'scripts/qposd/qposd_metrics.py'),
              'inputs_sha256': inputs, 'winner_index': winner, 'configurations': results,
              'train_objects': len(groups['train'][1]), 'validation_objects': len(groups['validation'][1]),
              'test_scored': False,
              'scope': 'Conditional classification with reference geometry, not end-to-end detection. Reference estimators use identical NumPy feature inputs to isolate model implementation differences.'}
    output.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print('Saved classifier selection:', output)


if __name__ == '__main__':
    main()
