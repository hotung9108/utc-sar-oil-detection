"""Freeze source-group split and image-only physical-data eligibility before fitting."""

import sys as _sys
from pathlib import Path as _Path
_project_root = _Path(__file__).resolve().parents[2]
_sys.path.insert(0, str(_project_root))
_sys.path.insert(0, str(_project_root / "src"))

import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path


from scripts._provenance import source_matches
from scripts._paths import resolve_path
from scripts.cantarell.audit_cantarell_source import ROOT, REVISION


def sha(path):
    return hashlib.sha256(resolve_path(path).read_bytes()).hexdigest()


def main():
    folder = ROOT / 'docs/management'
    inventory_path = folder / 'cantarell_full_inventory.json'
    scene_path = folder / 'cantarell_scenes_audit.json'
    inventory, scenes = (json.loads(p.read_text()) for p in (inventory_path, scene_path))
    if not inventory['complete_inventory'] or not scenes['complete']:
        raise ValueError('Complete source inventory is required')
    samples = inventory['samples']
    group_to_scene = {r['group']: r for r in scenes['results']}
    parent = {g: g for g in group_to_scene}

    def find(g):
        while parent[g] != g:
            parent[g] = parent[parent[g]]
            g = parent[g]
        return g

    def union(a, b):
        a, b = find(a), find(b)
        if a != b:
            parent[max(a, b)] = min(a, b)

    id_groups = defaultdict(set)
    for sample in samples:
        for prop in sample['vector_properties']:
            id_groups[prop['ID_POLY']].add(sample['group'])
    for groups in id_groups.values():
        ordered = sorted(groups)
        for g in ordered[1:]:
            union(ordered[0], g)
    components = defaultdict(list)
    for g in parent:
        components[find(g)].append(g)
    # Preserve held-out membership: a linked train group moves to test, never vice versa.
    priority = {'train': 0, 'val': 1, 'test': 2}
    assignments = {}
    for groups in components.values():
        split = max((group_to_scene[g]['split'] for g in groups), key=priority.get)
        assignments.update({g: split for g in groups})
    rows = [{'sample': s['sample'], 'group': s['group'], 'scene': group_to_scene[s['group']]['scene'],
             'publisher_split': s['split'], 'split': assignments[s['group']],
             'exported_image_sha256': s['image_sha256'], 'mask_sha256': s['mask_sha256']}
            for s in samples]
    for groups in id_groups.values():
        if len({assignments[g] for g in groups}) != 1:
            raise ValueError('Polygon identifier still crosses splits')
    protocol = {
        'version': 1, 'scope': 'Physical SAR supplement; SOS and its frozen evidence remain primary and unchanged.',
        'revision': REVISION, 'inventory_sha256': sha(inventory_path), 'scenes_audit_sha256': sha(scene_path),
        'generator_sha256': sha(Path(__file__)),
        'split_rule': 'Union all source groups sharing a polygon ID; assign each component to highest publisher held-out level: test > val > train. No random resplitting.',
        'reason': 'OS03029GXS1 appears in IMG_17/test and IMG_18/train; differing acquisition dates/locations do not establish whether it is an ID collision or linked event.',
        'linked_groups': [sorted(g) for g in components.values() if len(g)>1],
        'sample_counts': dict(Counter(r['split'] for r in rows)),
        'scene_counts': dict(Counter(assignments.values())),
        'changed_groups': [{'group': g, 'from': group_to_scene[g]['split'], 'to': assignments[g]}
                           for g in sorted(assignments) if assignments[g] != group_to_scene[g]['split']],
        'samples': rows,
        'physical_inputs': {
            'polarization': 'VV', 'native_units': 'uint16 amplitude DN from original GRD TIFF',
            'calibration': 'sigma0 = DN^2 / sigmaNought_LUT^2, LUT interpolated on native line/pixel grid',
            'angle_branch': 'gamma0_derived = sigma0 / cos(ellipsoid_incidence_angle)',
            'thermal_noise_subtraction': False,
            'noise_limit': 'Both paired branches share uncorrected thermal noise; no claim of noise-corrected SNAP equivalence.',
            'geolocation': 'NumPy inverse bilinear geolocation, checked against SciPy; then sample linear power into publisher map grid.',
            'labels': 'Publisher mask > 0 (oil spill and natural seepage pooled); no oil-like negative cause labels.',
            'ground_truth_size_filter': None
        },
        'registration': {
            'method': 'Same mean-subtracted Hann-window phase correlation as the two development tiles; upsample_factor=100; image only.',
            'reference': 'Publisher float TIFF used as an image alignment anchor, not as calibrated SAR input.',
            'transformation': 'Apply estimated row/column translation to all native physical channels consistently; never shift GT to maximize detection scores.',
            'local_diagnostic_grid': [3, 3],
            'masks_used': False,
            'no_test_performance_tuning': True
        },
        'eligibility_checks_frozen_before_full_native_reconstruction': {
            'source_hashes_and_shapes_match': True,
            'all_queries_inside_metadata_support': True,
            'max_abs_global_shift_pixels': 3.0,
            'max_abs_local_minus_global_shift_pixels': 0.5,
            'minimum_registered_pearson_on_8pixel_interior': 0.70,
            'all_finite': True,
            'numpy_scipy_interpolation_rtol': 1e-12,
            'numpy_scipy_interpolation_atol': 1e-12,
            'minimum_eligible_scenes_per_split': 3,
            'rationale': 'Engineering eligibility tolerances, not theoretical guarantees; 0.70 is looser than the observed 0.88-0.89 development correlations. Publish all exclusions and do not retune thresholds on test.',
            'failure_behavior': 'Retain all failed-sample receipts and reasons; no silent fallback to PNG or other polarization. If scene-count gate fails, stop before model fitting.'
        },
        'boundary_handling': 'Restrict physical metrics and labels to a common interior crop of 8 map pixels on all sides for every paired branch; report crop and GT objects touching new boundary. No GT small-object removal.',
        'exposure': 'All masks inspected by automated geometry audit; two IMG_01 train images inspected visually and used for registration development. Test is not claimed completely unseen.',
        'model_protocol_status': 'Not yet frozen. Only source preparation and split are frozen here; model/grid selection must be specified and committed before fitting or scoring detection.',
        'limits': ['Scene-group separation is not proof of independent spill events or meteorology.',
                   'Gamma conversion corrects a geometric area factor, not all ocean incidence-angle dependence.',
                   'Registration uses processed images; absolute geolocation and exporter processing history remain uncertain.',
                   'No model has been fitted or detection test score computed on this supplement.']
    }
    target = folder / 'cantarell_data_protocol_v1.json'
    if target.exists():
        existing = json.loads(target.read_text())
        if existing != protocol:
            raise ValueError('Refusing to overwrite a frozen protocol with changed content')
    else:
        target.write_text(json.dumps(protocol, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({k: protocol[k] for k in ('linked_groups', 'sample_counts', 'scene_counts', 'changed_groups')}, indent=2))


if __name__ == '__main__':
    main()
