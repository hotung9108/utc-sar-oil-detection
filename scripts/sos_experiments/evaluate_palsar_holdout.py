"""Evaluate two frozen SOS pipelines on publisher PALSAR train, without fitting.

Use --prepare before --run. This is a supplementary cross-sensor patch test,
not verified scene-independent validation or a new model-selection dataset.
"""

import sys as _sys
from pathlib import Path as _Path
_project_root = _Path(__file__).resolve().parents[2]
_sys.path.insert(0, str(_project_root))
_sys.path.insert(0, str(_project_root / "src"))

from scripts._provenance import source_matches
from scripts._paths import resolve_path

import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
import hashlib
import json
import os
from pathlib import Path
import sys

for variable in ('OPENBLAS_NUM_THREADS', 'OMP_NUM_THREADS', 'MKL_NUM_THREADS'):
    os.environ.setdefault(variable, '1')
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'src'))
from sar_oil.data import records
from sar_oil.evaluation import summarize
from sar_oil.experiments import _evaluate_image
from sar_oil.provenance import ensure_run

DEST = ROOT / 'results/sos/external_palsar_train'


def digest(path):
    return hashlib.sha256(resolve_path(path).read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def write(path, value):
    temporary = path.with_suffix('.tmp')
    temporary.write_text(json.dumps(value, indent=2) + '\n', encoding='utf-8')
    temporary.replace(path)


def definition():
    audit_path = ROOT / 'docs/management/palsar_holdout_audit.json'
    audit = read(audit_path)
    assert audit['images'] == 3101
    assert not audit['cross_population_identical_grayscale_groups']
    assert source_matches(ROOT / 'data/manifest.json', audit['manifest_sha256'], digest(ROOT / 'data/manifest.json'))
    models = {}
    for name, relative in [('otsu', 'results/sos/selected.json'),
                           ('niblack', 'results/sos/adaptive/selected.json')]:
        selected_path = ROOT / relative
        selected = read(selected_path)
        model_path = selected_path.parent / selected['model_file']
        models[name] = {'selected': relative, 'selected_sha256': digest(selected_path),
                        'model': model_path.relative_to(ROOT).as_posix(),
                        'model_sha256': digest(model_path), 'config': selected['config']}
    return {'population': 'external_train', 'expected': 3101, 'backend': 'numpy',
            'mask_threshold': 128, 'object_iou_threshold': .5,
            'manifest_sha256': audit['manifest_sha256'], 'preflight_sha256': digest(audit_path),
            'script_sha256': digest(Path(__file__)), 'models': models,
            'rule': 'Evaluate every listed patch for both frozen pipelines; no fitting, filtering by outcome, threshold changes or winner selection.',
            'scope': 'Supplementary PALSAR patch-level cross-sensor evaluation. Publisher train naming does not imply use in this project fitting. Scene independence and historical manual exposure are not established.'}


def worker(row, model):
    for key in ('image', 'mask'):
        assert source_matches(ROOT / row[key], row[key + '_sha256'], digest(ROOT / row[key]))
    result = _evaluate_image((row, model['config'], str(ROOT / model['model']), 'numpy', 128))
    result.update({key: row[key] for key in ('image_sha256', 'mask_sha256')})
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--prepare', action='store_true')
    mode.add_argument('--run', action='store_true')
    parser.add_argument('--workers', type=int, default=4, choices=range(1, 9))
    args = parser.parse_args()
    ensure_run()
    expected = definition()
    DEST.mkdir(exist_ok=True)
    protocol_path = DEST / 'protocol.json'
    if args.prepare:
        if protocol_path.exists():
            assert read(protocol_path) == expected, 'Existing protocol differs; do not overwrite'
        else:
            write(protocol_path, expected)
        print('Protocol saved before inference; no model or threshold changed.')
        return
    assert read(protocol_path) == expected, 'Prepare and inspect the protocol first'
    rows = records('external_train')
    assert len(rows) == len({r['id'] for r in rows}) == expected['expected']
    by_id = {r['id']: r for r in rows}
    signature = digest(protocol_path)
    for name, model in expected['models'].items():
        path = DEST / f'{name}.json'
        completed = {}
        if path.exists():
            prior = read(path)
            assert prior['protocol_sha256'] == signature
            for result in prior['per_image']:
                row = by_id[result['id']]
                assert result['id'] not in completed
                for key in ('image', 'mask'):
                    assert result[key + '_sha256'] == row[key + '_sha256'] == digest(ROOT / row[key])
                completed[result['id']] = result

        def save():
            items = sorted(completed.values(), key=lambda r: r['id'])
            write(path, {'protocol_sha256': signature, 'expected': len(rows),
                         'completed': len(items), 'complete': len(items) == len(rows),
                         'metrics': summarize([r['counts'] for r in items]), 'per_image': items})

        with ProcessPoolExecutor(max_workers=args.workers) as pool:
            jobs = [pool.submit(worker, row, model) for row in rows if row['id'] not in completed]
            for job in as_completed(jobs):
                result = job.result()
                completed[result['id']] = result
                if len(completed) % 50 == 0:
                    save()
                    print(f'{name}: {len(completed)}/{len(rows)}', flush=True)
        assert definition() == expected
        save()
        print(name, json.dumps(read(path)['metrics']), flush=True)


if __name__ == '__main__':
    main()
