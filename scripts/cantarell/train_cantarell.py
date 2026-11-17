"""Train the frozen physical-SAR grid; select on validation, never access test."""

import sys as _sys
from pathlib import Path as _Path
_project_root = _Path(__file__).resolve().parents[2]
_sys.path.insert(0, str(_project_root))
_sys.path.insert(0, str(_project_root / "src"))

import json
import time
import warnings
from pathlib import Path

import numpy as np
from sklearn.exceptions import ConvergenceWarning


from scripts._provenance import source_matches
from scripts._paths import resolve_path
from scripts.cantarell.cantarell_experiment_data import ROOT, MANIFEST, load_manifest, load_input, sha, require_committed
from scripts.cantarell.cantarell_pipeline import candidates, extract
from sar_oil import core
from sar_oil.evaluation import counts, summarize
from sar_oil.models import RegionModel

DEST = ROOT / 'results/cantarell'


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(value, indent=2, allow_nan=False) + '\n'
    if path.exists():
        if json.loads(path.read_text()) != value:
            raise ValueError(f'Refusing to overwrite different evidence: {path}')
        return
    temp = path.with_suffix('.tmp')
    temp.write_text(text, encoding='utf-8')
    temp.replace(path)


def sample_training(X, purity, keys, seed=2026):
    """Intermediate-purity regions excluded only for train; deterministic rows."""
    y = np.where(purity >= .5, 1, np.where(purity <= .05, 0, -1))
    rng = np.random.default_rng(seed)
    indices = []
    for label in (0, 1):
        available = np.flatnonzero(y == label)
        indices.extend(rng.choice(available, min(10000, len(available)), replace=False).tolist())
    indices = np.array(sorted(indices), dtype=int)
    return X[indices], y[indices], [keys[i] for i in indices]


def prediction(labels, ids, scores):
    keep = np.zeros(int(labels.max()) + 1, bool)
    keep[ids] = scores > 0
    return keep[labels]


def feature_rows(sample, branch, config, folder, check_original=False):
    if sample['split'] not in ('train', 'val'):
        raise ValueError('Training feature extraction cannot use test')
    path = folder / f"{branch}_{config['id']}_{sample['sample']}.npz"
    receipt = path.with_suffix('.json')
    if receipt.exists():
        info = json.loads(receipt.read_text())
        if (not source_matches(path, info['sha256'], sha(path))) or info['input_sha256'] != sample['sha256']:
            raise ValueError('Feature cache hash mismatch')
        with np.load(path, allow_pickle=False) as saved:
            return {k: saved[k] for k in saved.files}, info
    raw, truth = load_input(sample, branch)
    output = candidates(raw, config)
    X, ids = extract(output['image'], output['labels'])
    labels = output['labels']
    areas = np.bincount(labels.ravel())
    overlap = np.bincount(labels.ravel(), weights=truth.ravel(), minlength=len(areas))
    purity = overlap[ids] / areas[ids]
    data = {'X': X, 'ids': ids, 'purity': purity}
    info = {'sample': sample['sample'], 'input_sha256': sample['sha256'], 'regions': len(ids)}
    if sample['split'] == 'val':
        other = candidates(raw, config, 'reference')
        xr, ir = extract(other['image'], other['labels'], 'reference')
        partition_match = np.array_equal(labels, other['labels']) and np.array_equal(ids, ir)
        if not partition_match:
            raise ValueError('Different candidate partitions; investigate before training selection')
        delta = np.abs(X - xr)
        info['reference'] = {'partition_match': True,
            'max_abs_error': float(delta.max(initial=0)),
            'max_relative_error': float((delta / np.maximum(np.abs(xr), 1e-12)).max(initial=0)),
            'mse': float(np.mean(delta ** 2)) if delta.size else 0.,
            'allclose': bool(np.allclose(X, xr, atol=1e-6, rtol=1e-5))}
        if not info['reference']['allclose']:
            raise ValueError('Feature verification tolerance failed')
        if check_original:
            original, oi = core.features(output['image'], labels)
            info['original_numpy_check'] = bool(np.array_equal(ids, oi) and np.allclose(X, original, atol=1e-6, rtol=1e-5))
            if not info['original_numpy_check']:
                raise ValueError('Grouped features differ from original NumPy implementation')
        data.update(labels=labels, truth=truth, reference_X=xr)
    np.savez_compressed(path, **data)
    info['sha256'] = sha(path)
    write(receipt, info)
    return data, info


def rank(row):
    m = row['metrics']['numpy']
    return (-(m['f1'] if m['f1'] is not None else -1),
            -(m['recall'] if m['recall'] is not None else -1), row['config_id'], row['model_id'])


def main():
    manifest, protocol = load_manifest(['scripts/cantarell/train_cantarell.py'])
    screen_path = DEST / 'screen.json'
    require_committed(screen_path)
    screen = json.loads(screen_path.read_text())
    if not screen['complete'] or (not source_matches(MANIFEST, screen['binding']['manifest_sha256'], sha(MANIFEST))):
        raise ValueError('Complete matching screening required')
    binding = {'manifest_sha256': sha(MANIFEST), 'screen_sha256': sha(screen_path),
               'script_sha256': sha(Path(__file__)), 'model_protocol_sha256': manifest['model_protocol_sha256']}
    cache = ROOT / '.cache/cantarell_training' / binding['manifest_sha256'] / binding['script_sha256']
    cache.mkdir(parents=True, exist_ok=True)
    train = sorted([r for r in manifest['samples'] if r['split'] == 'train'], key=lambda r:r['sample'])
    validation = sorted([r for r in manifest['samples'] if r['split'] == 'val'], key=lambda r:r['sample'])
    comparisons, verification = [], []
    for branch in protocol['radiometry_branches']:
        for config_id in screen['retained_candidate_ids'][branch]:
            config = next(c for c in protocol['candidate_configs'] if c['id'] == config_id)
            prefix = f'{branch}_{config_id:02d}'
            all_x, all_p, keys = [], [], []
            for sample in train:
                data, _ = feature_rows(sample, branch, config, cache)
                all_x.append(data['X']); all_p.append(data['purity'])
                keys.extend([{'sample': sample['sample'], 'region_id': int(i)} for i in data['ids']])
            X, y, selected_rows = sample_training(np.concatenate(all_x), np.concatenate(all_p), keys)
            write(DEST / 'training_rows' / f'{prefix}.json', {'binding': binding, 'rows': selected_rows,
                  'labels': y.tolist(), 'features': X.tolist(), 'test_accessed': False})
            val_data, seen = [], set()
            for sample in validation:
                data, info = feature_rows(sample, branch, config, cache, sample['scene'] not in seen)
                seen.add(sample['scene'])
                val_data.append((sample, data))
                verification.append({'branch': branch, 'config_id': config_id, **info})
            for model_config in protocol['training']['models']:
                mid = model_config['id']
                checkpoint = DEST / 'validation_rows' / f'{prefix}_{mid}.json'
                if checkpoint.exists():
                    row = json.loads(checkpoint.read_text())
                    if row['binding'] != binding:
                        raise ValueError('Training checkpoint binding mismatch')
                    if row.get('model_file') and (not source_matches(ROOT / row['model_file'], row['model_sha256'], sha(ROOT / row['model_file']))):
                        raise ValueError('Saved model hash mismatch')
                    comparisons.append(row)
                    continue
                params = {k:v for k,v in model_config.items() if k not in ('id', 'kind')}
                row = {'binding': binding, 'branch': branch, 'config_id': config_id, 'config': config,
                       'model_id': mid, 'model_config': model_config, 'training_regions': len(y),
                       'class_counts': np.bincount(y, minlength=2).tolist(), 'eligible': False}
                models, diagnostics = {}, {}
                try:
                    for backend in ('numpy', 'reference'):
                        start = time.perf_counter()
                        with warnings.catch_warnings(record=True) as caught:
                            warnings.simplefilter('always', ConvergenceWarning)
                            model = RegionModel(kind=model_config['kind'], backend=backend, **params).fit(X, y)
                        converged = model.converged and not any(issubclass(w.category, ConvergenceWarning) for w in caught)
                        diagnostics[backend] = {'fit_seconds': time.perf_counter() - start, 'converged': converged,
                            'warnings': [str(w.message) for w in caught]}
                        if model_config['kind'] == 'svm':
                            design = model.transform(X)
                            weights = model.estimator.w if backend == 'numpy' else model.estimator.coef_[0]
                            margins = np.maximum(1 - (2*y-1) * (design @ weights), 0)
                            gradient = weights/len(y) - 2*params['C']*(design.T @ ((2*y-1)*margins))/len(y)
                            diagnostics[backend].update(objective=float(.5*(weights@weights)/len(y) + params['C']*(margins@margins)/len(y)),
                                gradient_max=float(np.max(np.abs(gradient))))
                        if not converged:
                            raise ValueError(f'{backend} model did not converge')
                        models[backend] = model
                    per_image, agreements, score_errors = [], [], []
                    for sample, data in val_data:
                        # Shared features isolate classifier differences; feature parity is recorded separately.
                        scores = {b:m.scores(data['X']) for b,m in models.items()}
                        if not all(np.isfinite(s).all() for s in scores.values()):
                            raise ValueError('Nonfinite model scores')
                        agreements.extend(((scores['numpy'] > 0) == (scores['reference'] > 0)).tolist())
                        score_errors.extend(np.abs(scores['numpy'] - scores['reference']).tolist())
                        per_image.append({'sample': sample['sample'], 'scene': sample['scene'],
                            'counts': {b: counts(prediction(data['labels'], data['ids'], s), data['truth']) for b,s in scores.items()}})
                    model_path = DEST / 'models' / f'{prefix}_{mid}.json'
                    model_path.parent.mkdir(parents=True, exist_ok=True)
                    models['numpy'].save(model_path)
                    row.update(eligible=True, metrics={b:summarize([r['counts'][b] for r in per_image]) for b in models},
                        per_image=per_image, classifier_agreement=float(np.mean(agreements)) if agreements else None,
                        score_max_abs_error=max(score_errors, default=0.), model_file=model_path.relative_to(ROOT).as_posix(),
                        model_sha256=sha(model_path))
                except ValueError as exc:
                    row['error'] = str(exc)
                row['diagnostics'] = diagnostics
                write(checkpoint, row)
                comparisons.append(row)
                print(f"{prefix} model {mid}: eligible={row['eligible']} F1={row.get('metrics',{}).get('numpy',{}).get('f1')}", flush=True)
    write(DEST / 'feature_verification.json', {'binding': binding, 'rows': verification})
    write(DEST / 'validation.json', {'binding': binding, 'rows': comparisons, 'test_accessed': False,
          'complete': True, 'expected_model_pairs': 7 * sum(map(len, screen['retained_candidate_ids'].values()))})
    winners = {}
    for role, branch, adaptive in [('primary', 'gamma0', True), ('gamma_unrestricted', 'gamma0', False),
                                   ('sigma_unrestricted', 'sigma0', False), ('sigma_adaptive', 'sigma0', True)]:
        eligible = [r for r in comparisons if r['eligible'] and r['branch'] == branch
                    and (not adaptive or r['config']['threshold']['name'] == 'niblack')]
        if not eligible:
            raise ValueError(f'No eligible model for {role}; report failures without inventing a selection')
        winner = sorted(eligible, key=rank)[0]
        winners[role] = {k:winner[k] for k in ['branch','config_id','config','model_id','model_config','model_file','model_sha256','metrics']}
    write(DEST / 'selection.json', {'binding': binding, 'winners': winners,
          'validation_sha256': sha(DEST / 'validation.json'), 'test_accessed': False,
          'must_commit_before_test': True})
    print(json.dumps({k:{'config':v['config_id'],'model':v['model_id'],'f1':v['metrics']['numpy']['f1']} for k,v in winners.items()}, indent=2))


if __name__ == '__main__':
    main()
