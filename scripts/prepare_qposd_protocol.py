"""Freeze source-image splits and a bounded experiment before QPOSD fitting."""
import hashlib
import json
import argparse
import itertools
import shutil
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT/'results/qposd/protocol.json'


def definition_v1():
    path = ROOT/'docs/management/qposd_shape_audit.json'
    audit = json.loads(path.read_text(encoding='utf-8'))
    eligible = [r for r in audit['pairs'] if r['spatial_shape_matches']]
    assert len(eligible) == 24
    # Stratification uses reference class presence/area, never predictions.
    oil = sorted(r['number'] for r in eligible
                 if r['class_counts']['oil'] > r['class_counts']['look_alike'])
    look = sorted(r['number'] for r in eligible if r['number'] not in oil)
    assert len(oil) == 16 and len(look) == 8
    rng = np.random.default_rng(2026)
    oil, look = rng.permutation(oil).tolist(), rng.permutation(look).tolist()
    splits = {'train': sorted(oil[:10] + look[:4]),
              'validation': sorted(oil[10:13] + look[4:6]),
              'test': sorted(oil[13:] + look[6:])}
    flattened = sum(splits.values(), [])
    assert len(flattened) == len(set(flattened)) == 24
    assert set(flattened) == {r['number'] for r in eligible}
    models = [{'kind': 'svm', 'params': {'C': c}} for c in (.01, .1, 1., 10.)]
    models += [{'kind': 'cart', 'params': {'max_depth': d, 'min_leaf': n}}
               for d in (2, 3, 5) for n in (1, 5)]
    candidates = []
    for filtering in ('none', 'lee'):
        for threshold in [{'name': 'otsu'}] + [
                {'name': 'niblack', 'size': size, 'k': k}
                for size in (31, 51) for k in (.2, .5)]:
            candidates.append({'filter': filtering, 'size': 7, 'looks': 4,
                               'threshold': threshold, 'min_area': 64,
                               'morphology': 'none'})
    return {
        'version': 1, 'record': audit['record'], 'seed': 2026,
        'shape_audit_sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
        'splits': splits, 'stratification': 'Dominant oil/look-alike pixel class per source image; 16/8 images. Three oil pixels in image32 retained.',
        'eligibility': '24 matching dimensions; full MAT finite/nine-channel/hash checks and visual review required before fitting. No resizing of 17 mismatched pairs. Stop and version protocol if a structural failure changes the population.',
        'split_scope': 'Source-image split, not verified scene-independent split. Image labels/previews inspected before split; no QPOSD model scores inspected.',
        'feature_image': {
            'channel': 'T[:,:,0] (publisher T11); not Sentinel VV or 8-bit DN',
            'filter': 'Lee, window7, looks4 on nonnegative linear T11',
            'transform': '10*log10(max(filtered,1e-12)); per-image 1st/99th percentiles, clip and scale to [0,1]; constant range gives zeros',
            'features': 'Existing eight core.features: area_fraction, elongation, extent, complexity, mean, std, boundary_gradient, background_contrast',
            'rationale': 'Frozen SOS Lee setting transferred for this supplementary experiment, not claimed optimal for QPOSD. Per-image scaling uses no labels. SVM/CART feature scaling fit on train objects only.'},
        'conditional_classification': {
            'training_objects': 'All exact-color 8-connected oil/look-alike reference regions in train, including <64 pixels; no area-based removal',
            'labels': {'oil': 1, 'look_alike': 0},
            'models': models,
            'selection': 'Highest validation macro-F1 across oil and look-alike; exact ties use model list order. NumPy backend; nonconverged fits ineligible and recorded.',
            'reference': 'Fit corresponding sklearn estimators on identical train features/scaling; save validation confusion matrices, score differences and prediction agreement for every configuration. No equality assumption for CART ties.',
            'scope': 'Classification with reference-region geometry supplied; not end-to-end detection.'},
        'detection': {
            'candidate_configs': candidates,
            'candidate_input': 'Apply configured filter to linear T11, then same log/percentile transform as above; threshold dark pixels. No ground-truth mask at inference.',
            'classifier': 'Frozen winner from conditional validation; candidate features use fixed feature_image, not reference labels.',
            'selection': 'Highest validation mean of oil object-F1 and look-alike object-F1; ties use candidate list order. Do not retrain after selecting.',
            'ground_truth': 'Keep all oil/look-alike reference components. Unknown-color pixels ignored only during evaluation. Land and sea are not silently removed from predictions; false detections count as FP.',
            'matching': 'One-to-one same-class IoU >=0.5. Report per-class TP/FP/FN, P/R/F1, mean class F1, and spatially matched cross-class confusion plus unmatched objects.',
            'min_area_scope': '64-pixel candidate filter inherited from SOS, not applied to ground truth. Also report GT counts/recall by <64 and >=64 pixels without replacing overall metrics.'},
        'test_rule': 'No test model score until both selections and model hashes are saved. Evaluate frozen winners once, report poor results without retuning. Test prediction labels withheld from selection.',
        'limits': ['Generic look-alike only, no wind/biofilm/rain causal labels.',
                   'UAVSAR L-band supplementary branch; does not replace SOS Sentinel/PALSAR results.',
                   'Five test images yield fragile estimates; object counts are not independent image or scene counts.',
                   'No physical calibration or georeferenced wind evaluation is implied.'],
    }


def grouped_splits(original, shapes, overlap):
    ids = sorted(sum(original.values(), []))
    parent = {n: n for n in ids}
    def root(n):
        while parent[n] != n:
            n = parent[n]
        return n
    for pair in overlap['pairs']:
        if any(t['entire_overlap_exact'] for t in pair['translations']):
            a, b = root(pair['first']), root(pair['second'])
            parent[max(a, b)] = min(a, b)
    groups = {}
    for n in ids:
        groups.setdefault(root(n), []).append(n)
    oil = {r['number'] for r in shapes['pairs'] if r['number'] in ids
           and r['class_counts']['oil'] > r['class_counts']['look_alike']}
    oil_groups, look_groups = [], []
    for group in groups.values():
        if set(group).issubset(oil):
            oil_groups.append(group)
        elif set(group).isdisjoint(oil):
            look_groups.append(group)
        else:
            raise ValueError('Mixed-class overlap group requires a new stratification design')
    old_split = {n: k for k, numbers in original.items() for n in numbers}
    if any(len({old_split[n] for n in g}) != 1 for g in look_groups):
        raise ValueError('Look-alike overlap requires extending the grouped assignment search')
    # Enumerate every oil-group assignment preserving 10/3/3 images. Keep
    # look-alike assignment fixed (no cross-split overlap in that stratum).
    subsets = []
    for size in range(1, len(oil_groups)+1):
        for indices in itertools.combinations(range(len(oil_groups)), size):
            selected = frozenset(n for i in indices for n in oil_groups[i])
            if len(selected) == 3:
                subsets.append(selected)
    choices = []
    for validation in subsets:
        for test in subsets:
            if validation & test:
                continue
            assigned = {'train': oil-set(validation)-set(test),
                        'validation': set(validation), 'test': set(test)}
            result = {k: sorted(assigned[k] | (set(original[k])-oil)) for k in original}
            moved = sum(old_split[n] != k for k, numbers in result.items() for n in numbers)
            tie = hashlib.sha256(('2026:'+json.dumps(result, sort_keys=True)).encode()).hexdigest()
            choices.append((moved, tie, result))
    if not choices:
        raise ValueError('No group-preserving split meets the fixed stratum counts')
    moved, _, result = min(choices, key=lambda x: (x[0], x[1]))
    return result, list(groups.values()), moved, len(choices)


def definition():
    result = definition_v1()
    overlap_path = ROOT/'docs/management/qposd_overlap_all24.json'
    overlap = json.loads(overlap_path.read_text(encoding='utf-8'))
    shapes = json.loads((ROOT/'docs/management/qposd_shape_audit.json').read_text(encoding='utf-8'))
    original = result['splits']
    revised, groups, moved, count = grouped_splits(original, shapes, overlap)
    archived = ROOT/'results/qposd/archive/protocol_v1/protocol.json'
    result.update(version=2, splits=revised)
    result['revision'] = {
        'reason': 'Exact translated overlap crosses train/test in v1 (21/22); repair before fitting.',
        'original_protocol_sha256': hashlib.sha256(archived.read_bytes()).hexdigest(),
        'overlap_audit_sha256': hashlib.sha256(overlap_path.read_bytes()).hexdigest(),
        'groups': groups, 'images_moved': moved, 'feasible_group_assignments': count,
        'selection_rule': 'Preserve 14/5/5 total and 10/3/3 dominant-oil counts; enumerate all eligible oil-group assignments, minimize changed image membership, tie-break SHA256 of seed2026 plus canonical split JSON. No model scores read.',
        'prior_exposure': 'All images/masks visually audited. V1 train/validation features extracted before grouping; no classifier fitted and no model scores. Revised test is not claimed visually blind.',
    }
    result['split_scope'] = 'Connected exact-overlap groups kept intact. Sampled overlap screening does not establish scene independence or exclude radiometrically changed/rotated overlap.'
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--migrate-overlap-groups', action='store_true')
    args = parser.parse_args()
    if args.migrate_overlap_groups:
        if json.loads(OUTPUT.read_text(encoding='utf-8')) != definition_v1():
            raise SystemExit('Migration requires the unchanged v1 protocol')
        for name in ('classifier_selection.json', 'detection_selection.json', 'evaluation.json', 'models', 'test'):
            if (OUTPUT.parent/name).exists():
                raise SystemExit('Model/test evidence already exists; cannot migrate as a pre-fit change')
        archive = (OUTPUT.parent/'archive/protocol_v1').resolve()
        regions = (OUTPUT.parent/'regions').resolve()
        root_path = ROOT.resolve()
        if not archive.is_relative_to(root_path) or not regions.is_relative_to(root_path) or archive.exists():
            raise SystemExit('Unsafe or existing archive destination')
        # Validate feasibility before moving any evidence.
        grouped_splits(definition_v1()['splits'],
                       json.loads((ROOT/'docs/management/qposd_shape_audit.json').read_text()),
                       json.loads((ROOT/'docs/management/qposd_overlap_all24.json').read_text()))
        archive.mkdir(parents=True)
        (archive/'protocol.json').write_bytes(OUTPUT.read_bytes())
        shutil.move(str(regions), str(archive/'regions'))
        OUTPUT.write_text(json.dumps(definition(), indent=2)+'\n', encoding='utf-8')
    result = definition()
    if OUTPUT.exists():
        if json.loads(OUTPUT.read_text(encoding='utf-8')) != result:
            raise SystemExit('Existing protocol differs; refuse silent overwrite')
        print('Existing protocol matches; no changes.')
    else:
        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
        print('Frozen protocol:', OUTPUT)
    print(json.dumps(result['splits']))


if __name__ == '__main__':
    main()
