"""Read-only physical-SAR UI adapter, enabled only after frozen test completion."""
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from cantarell_experiment_data import load_manifest, sha, require_committed
from cantarell_pipeline import infer, normalize_power
from sar_oil.models import RegionModel
from sar_oil.evaluation import counts, summarize
from sar_oil.core import FEATURES


def ready():
    return (ROOT / 'results/cantarell/evaluation.json').exists()


def setup():
    manifest, _ = load_manifest()
    path = ROOT / 'results/cantarell/selection.json'
    require_committed(path)
    selection = json.loads(path.read_text())
    evaluation = json.loads((ROOT / 'results/cantarell/evaluation.json').read_text())
    if not evaluation['complete'] or evaluation['binding']['selection_sha256'] != sha(path):
        raise ValueError('Physical evaluation does not verify the current selection')
    if evaluation['binding']['manifest_sha256'] != sha(ROOT / 'docs/management/cantarell_eligible_manifest.json'):
        raise ValueError('Physical evaluation input manifest differs')
    chosen = selection['winners']['primary']
    model_path = ROOT / chosen['model_file']
    require_committed(model_path)
    if sha(model_path) != chosen['model_sha256']:
        raise ValueError('Physical model hash changed')
    return manifest, chosen, model_path


def samples():
    manifest, _, _ = setup()
    return [r for r in manifest['samples'] if r['split'] == 'test']


def run_sample(sample_id):
    manifest, selected, model_path = setup()
    sample = next(r for r in manifest['samples'] if r['sample'] == sample_id and r['split'] == 'test')
    path = ROOT / sample['file']
    if sha(path) != sample['sha256']:
        raise ValueError('Prepared physical image changed')
    with np.load(path, allow_pickle=False) as arrays:
        power = arrays[selected['branch']]
        angles = arrays['incidence_degrees']
    output = infer(power, selected['config'], RegionModel.load(model_path))
    image, _ = normalize_power(power)
    rgb = np.repeat(image[..., None], 3, axis=2)
    rgb[output['prediction']] = .5*rgb[output['prediction']] + .5*np.array([1., 0., 0.])
    regions = [{'id': int(i), 'features': dict(zip(FEATURES, x.tolist())),
                'score': float(s), 'oil': bool(s > 0)}
               for i, x, s in zip(output['region_ids'], output['features'], output['scores'])]
    return {'image': image, 'filtered': output['image'], 'candidates': output['candidate_mask'],
            'mask': output['prediction'], 'overlay': rgb,
            'metadata': {'sample': sample_id, 'input_sha256': sample['sha256'],
                'branch': selected['branch'], 'config': selected['config'],
                'model_sha256': selected['model_sha256'], 'regions': regions,
                'seconds_including_preview': output['seconds_single_run'],
                'wind_speed_m_s': sample['wind_speed_m_s'],
                'incidence_degrees_min_max': [float(angles.min()), float(angles.max())],
                'ground_truth_used_for_inference': False, 'score_semantics': 'decision score, not probability'}}


def assess_sample(result):
    manifest, _, _ = setup()
    sample = next(r for r in manifest['samples'] if r['sample'] == result['metadata']['sample'])
    path = ROOT / sample['file']
    if sha(path) != sample['sha256']:
        raise ValueError('Prepared reference changed')
    with np.load(path, allow_pickle=False) as arrays:
        truth = arrays['truth']
    return {'metrics': summarize([counts(result['mask'], truth)]), 'input_sha256': sample['sha256'],
            'truth_definition': 'cropped oil spill or seepage foreground; no minimum GT area'}
