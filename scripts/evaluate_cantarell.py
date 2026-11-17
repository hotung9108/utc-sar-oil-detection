"""Frozen test evaluation and paired scene bootstrap; no fitting or selection."""
import json
import os
import platform
import sys
from importlib.metadata import version
from pathlib import Path

import numpy as np
from PIL import Image
from threadpoolctl import threadpool_info

from cantarell_experiment_data import ROOT, MANIFEST, load_manifest, load_input, sha, require_committed
from cantarell_pipeline import infer, normalize_power
from sar_oil.evaluation import counts, summarize
from sar_oil.models import RegionModel
from train_cantarell import write
from select_cantarell_required_filter import PROTOCOL as FILTER_PROTOCOL, OUTPUT as FILTER_SELECTION, choose

DEST = ROOT / 'results/cantarell'


def scene_bootstrap(primary, counterfactual, repeats=2000, seed=2026):
    """Resample whole scenes, retaining the same sampled scenes in both arms."""
    first = {r['sample']: r for r in primary}
    second = {r['sample']: r for r in counterfactual}
    if set(first) != set(second) or any(first[k]['scene'] != second[k]['scene'] for k in first):
        raise ValueError('Paired bootstrap requires identical samples and scene IDs')
    scenes = sorted({r['scene'] for r in primary})
    if not scenes:
        raise ValueError('No scenes for bootstrap')
    rng = np.random.default_rng(seed)
    differences, draws = [], []
    for _ in range(repeats):
        selected = rng.choice(scenes, len(scenes), replace=True).tolist()
        metrics = []
        for rows in (primary, counterfactual):
            metrics.append(summarize([r['counts']['numpy'] for scene in selected for r in rows if r['scene'] == scene])['f1'])
        differences.append(None if any(v is None for v in metrics) else metrics[0] - metrics[1])
        draws.append(selected)
    valid = [v for v in differences if v is not None]
    return {'unit': 'source scene', 'seed': seed, 'replicates': repeats, 'scenes': scenes,
            'sampled_scenes': draws, 'gamma_minus_sigma_f1': differences,
            'undefined_draws': repeats - len(valid),
            'ci95': np.percentile(valid, [2.5, 97.5]).tolist() if valid else None,
            'scope': 'Same gamma-trained adaptive detector; few scene clusters; not a universal normalization effect'}


def main():
    manifest, protocol = load_manifest(['scripts/evaluate_cantarell.py', 'scripts/train_cantarell.py',
                                       'scripts/select_cantarell_required_filter.py'])
    selection_path = DEST / 'selection.json'
    require_committed(selection_path)
    selection = json.loads(selection_path.read_text())
    if selection['binding']['manifest_sha256'] != sha(MANIFEST):
        raise ValueError('Selected model input manifest mismatch')
    if sha(DEST / 'validation.json') != selection['validation_sha256']:
        raise ValueError('Validation evidence changed after selection')
    require_committed(FILTER_PROTOCOL)
    require_committed(FILTER_SELECTION)
    filtered = json.loads(FILTER_SELECTION.read_text())
    if (filtered['protocol_sha256']!=sha(FILTER_PROTOCOL) or
            filtered['script_sha256']!=sha(ROOT/'scripts/select_cantarell_required_filter.py') or
            filtered['validation_sha256']!=sha(DEST/'validation.json') or
            filtered['original_selection_sha256']!=sha(selection_path)):
        raise ValueError('Required-filter selection provenance mismatch')
    expected = choose(json.loads((DEST/'validation.json').read_text())['rows'])
    if not all(expected[k]==v for k,v in filtered['selected'].items()):
        raise ValueError('Required-filter selection violates validation rule')
    test = sorted([r for r in manifest['samples'] if r['split'] == 'test'], key=lambda r:r['sample'])
    binding = {'manifest_sha256': sha(MANIFEST), 'selection_sha256': sha(selection_path),
               'script_sha256': sha(Path(__file__)), 'helper_sha256': sha(ROOT / 'scripts/train_cantarell.py'),
               'required_filter_selection_sha256':sha(FILTER_SELECTION), 'required_filter_protocol_sha256':sha(FILTER_PROTOCOL)}
    runs = dict(selection['winners'])
    runs['paired_sigma_same_model'] = {**selection['winners']['primary'], 'branch': 'sigma0'}
    runs['filtered_adaptive'] = filtered['selected']
    runs['paired_sigma_filtered_model'] = {**filtered['selected'], 'branch':'sigma0'}
    summaries = {}
    for role, selected in runs.items():
        model_path = ROOT / selected['model_file']
        require_committed(model_path)
        if sha(model_path) != selected['model_sha256']:
            raise ValueError('Model hash changed after selection')
        model = RegionModel.load(model_path)
        rows = []
        for sample in test:
            folder = DEST / 'test_outputs' / role / sample['sample']
            row_path = folder / 'counts.json'
            if row_path.exists():
                row = json.loads(row_path.read_text())
                if row['binding'] != binding or row['input_sha256'] != sample['sha256']:
                    raise ValueError('Test checkpoint binding mismatch')
                for name, expected in row['artifact_sha256'].items():
                    if sha(folder / name) != expected:
                        raise ValueError('Test output changed')
                rows.append(row)
                continue
            raw, truth = load_input(sample, selected['branch'], allow_test=True)
            outputs = {b:infer(raw, selected['config'], model, b) for b in ('numpy', 'reference')}
            folder.mkdir(parents=True, exist_ok=True)
            image, _ = normalize_power(raw)
            rgb = np.repeat(image[..., None], 3, axis=2)
            rgb[outputs['numpy']['prediction']] = .5*rgb[outputs['numpy']['prediction']] + .5*np.array([1.,0.,0.])
            images = {'input.png': image, 'mask.png': outputs['numpy']['prediction'],
                      'truth.png': truth, 'overlay.png': rgb,
                      'candidate.png': outputs['numpy']['candidate_mask']}
            for name, array in images.items():
                Image.fromarray(np.clip(array * 255, 0, 255).astype('uint8')).save(folder / name)
            np.savez_compressed(folder / 'regions.npz', features=outputs['numpy']['features'],
                                ids=outputs['numpy']['region_ids'], scores=outputs['numpy']['scores'])
            files = list(images) + ['regions.npz']
            row = {'binding': binding, 'sample': sample['sample'], 'scene': sample['scene'],
                   'input_sha256': sample['sha256'], 'role': role, 'branch': selected['branch'],
                   'model_sha256': selected['model_sha256'],
                   'counts': {b:counts(o['prediction'], truth) for b,o in outputs.items()},
                   'mask_disagreement_pixels': int(np.count_nonzero(outputs['numpy']['prediction'] != outputs['reference']['prediction'])),
                   'seconds_single_run': {b:o['seconds_single_run'] for b,o in outputs.items()},
                   'wind_speed_m_s': sample['wind_speed_m_s'],
                   'artifact_sha256': {name:sha(folder / name) for name in files}}
            write(row_path, row)
            rows.append(row)
        summaries[role] = {'selection': selected, 'per_image': rows,
            'metrics': {b:summarize([r['counts'][b] for r in rows]) for b in ('numpy', 'reference')},
            'per_scene': {scene:summarize([r['counts']['numpy'] for r in rows if r['scene'] == scene])
                          for scene in sorted({r['scene'] for r in rows})},
            'mask_disagreement_pixels': sum(r['mask_disagreement_pixels'] for r in rows)}
        print(f"{role}: {summaries[role]['metrics']['numpy']}", flush=True)
    paired = scene_bootstrap(summaries['primary']['per_image'], summaries['paired_sigma_same_model']['per_image'],
                             protocol['test']['bootstrap']['replicates'], protocol['test']['bootstrap']['seed'])
    write(DEST / 'angle_bootstrap.json', {'binding': binding, **paired})
    filtered_pair = scene_bootstrap(summaries['filtered_adaptive']['per_image'], summaries['paired_sigma_filtered_model']['per_image'],
                                   protocol['test']['bootstrap']['replicates'], protocol['test']['bootstrap']['seed'])
    write(DEST/'angle_bootstrap_filtered.json', {'binding':binding, **filtered_pair})
    write(DEST / 'evaluation.json', {'binding': binding, 'test_samples': len(test), 'roles': summaries,
          'complete': all(len(v['per_image']) == len(test) for v in summaries.values()),
          'angle_bootstrap_sha256': sha(DEST / 'angle_bootstrap.json'),
          'angle_bootstrap_filtered_sha256':sha(DEST/'angle_bootstrap_filtered.json'),
          'environment': {'python': sys.version, 'platform': platform.platform(),
              'logical_cpus': os.cpu_count(), 'image_workers': 1,
              'packages': {p:version(p) for p in ('numpy','scipy','scikit-image','scikit-learn','Pillow')},
              'threadpools': threadpool_info(),
              'timing_scope': 'Single-run wall time, no isolated-machine or repeated performance benchmark claim'},
          'limits': protocol['honesty_limits'], 'models_fitted_on_test': False})


if __name__ == '__main__':
    main()
