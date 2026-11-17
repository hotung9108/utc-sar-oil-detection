"""Run the frozen SOS NumPy model on every DARTIS no-oil patch.

Protocol must exist before execution. Results are external negative-set diagnostics,
not a replacement for SOS test metrics or physical look-alike subtype evaluation.
"""

import sys as _sys
from pathlib import Path as _Path
_project_root = _Path(__file__).resolve().parents[2]
_sys.path.insert(0, str(_project_root))
_sys.path.insert(0, str(_project_root / "src"))

from scripts._provenance import source_matches
from scripts._paths import resolve_path

import argparse
import hashlib
import json
import os
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

os.environ.setdefault('OPENBLAS_NUM_THREADS', '1')
os.environ.setdefault('OMP_NUM_THREADS', '1')
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'src'))
from sar_oil.models import RegionModel
from sar_oil.pipeline import predict
from sar_oil.provenance import ensure_run

DEST = ROOT / 'results/dartis'


def digest(path):
    return hashlib.sha256(resolve_path(path).read_bytes()).hexdigest()


def worker(row, expected_hash):
    start = time.perf_counter()
    path = ROOT / 'data/dartis' / row['filename']
    assert source_matches(path, expected_hash, digest(path)), 'Image changed since download audit'
    with Image.open(path) as source:
        image = np.asarray(source.convert('L'), dtype=np.float64) / 255.0
    assert image.shape == (row['height'], row['width'])
    selected = json.loads((ROOT / 'results/sos/selected.json').read_text())
    model = RegionModel.load(ROOT / 'results/sos' / selected['model_file'])
    mask, regions = predict(image, selected['config'], model, backend='numpy')
    positive = sum(r['oil'] for r in regions)
    assert bool(mask.any()) == (positive > 0)
    return {'filename': row['filename'], 'subset': row['subset'],
            'cluster': row['filename'].split('-')[2], 'scene_ids': row['scene_ids'],
            'image_sha256': expected_hash, 'candidate_regions': len(regions),
            'retained_regions': positive, 'false_alarm': positive > 0,
            'predicted_oil_pixels': int(mask.sum()), 'pixels': mask.size,
            'seconds': time.perf_counter() - start}


def aggregate(rows):
    n = len(rows)
    return {'images': n, 'false_alarm_images': sum(r['false_alarm'] for r in rows),
            'false_alarm_rate': sum(r['false_alarm'] for r in rows) / n if n else None,
            'retained_regions': sum(r['retained_regions'] for r in rows),
            'retained_regions_per_image': sum(r['retained_regions'] for r in rows) / n if n else None,
            'predicted_oil_pixel_fraction': sum(r['predicted_oil_pixels'] for r in rows) /
                sum(r['pixels'] for r in rows) if n else None}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workers', type=int, default=4, choices=range(1, 9))
    args = parser.parse_args()
    ensure_run()
    protocol_path = DEST / 'protocol.json'
    protocol = json.loads(protocol_path.read_text())
    selected_path = ROOT / 'results/sos/selected.json'
    selected = json.loads(selected_path.read_text())
    model_path = selected_path.parent / selected['model_file']
    assert source_matches(selected_path, protocol['selected_sha256'], digest(selected_path))
    assert source_matches(model_path, protocol['model_sha256'], digest(model_path))
    download = json.loads((DEST / 'download_audit.json').read_text())
    assert download['complete'] and download['errors'] == 0, 'Finish all downloads first'
    manifest_path = ROOT / 'data/dartis/catalog_manifest.json'
    assert source_matches(manifest_path, download['manifest_sha256'], digest(manifest_path))
    rows = [r for r in json.loads(manifest_path.read_text()) if r['subset'] in {'nc', 'nw'}]
    assert len(rows) == 2290
    hashes = {r['filename']: r['sha256'] for r in download['files']}
    provenance = {'protocol_sha256': digest(protocol_path), 'manifest_sha256': digest(manifest_path),
                  'script_sha256': digest(Path(__file__)), 'selected_sha256': digest(selected_path),
                  'model_sha256': digest(model_path)}
    output = DEST / 'evaluation.json'
    completed = {}
    if output.exists():
        old = json.loads(output.read_text())
        assert old['provenance'] == provenance, 'Checkpoint differs from frozen run'
        completed = {r['filename']: r for r in old['per_image']}
        for name, result in completed.items():
            assert result['image_sha256'] == hashes[name]
            assert source_matches(ROOT / 'data/dartis' / name, hashes[name], digest(ROOT / 'data/dartis' / name))

    def save():
        results = sorted(completed.values(), key=lambda r: r['filename'])
        grouped = {subset: aggregate([r for r in results if r['subset'] == subset])
                   for subset in ['nc', 'nw']}
        clusters = {key: aggregate([r for r in results if r['subset'] + '-' + r['cluster'] == key])
                    for key in sorted({r['subset'] + '-' + r['cluster'] for r in results})}
        report = {'provenance': provenance, 'expected': len(rows), 'completed': len(results),
                  'complete': len(results) == len(rows), 'overall': aggregate(results),
                  'by_subset': grouped, 'by_cluster': clusters, 'per_image': results,
                  'scope': 'Frozen-model no-oil external diagnostics; no oil recall/F1 or physical subtype claims'}
        temp = output.with_suffix('.tmp')
        temp.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
        temp.replace(output)

    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        jobs = [pool.submit(worker, row, hashes[row['filename']]) for row in rows
                if row['filename'] not in completed]
        for job in as_completed(jobs):
            result = job.result()  # Fail visibly; never silently drop an image.
            completed[result['filename']] = result
            if len(completed) % 25 == 0:
                save()
                print(f'{len(completed)}/{len(rows)} evaluated', flush=True)
    assert source_matches(model_path, protocol['model_sha256'], digest(model_path))
    assert source_matches(selected_path, protocol['selected_sha256'], digest(selected_path))
    save()
    print(json.dumps(aggregate(list(completed.values())), indent=2))


if __name__ == '__main__':
    main()
