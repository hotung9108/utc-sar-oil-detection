"""Reproduce feature equivalence on a fixed validation candidate population."""

import sys as _sys
from pathlib import Path as _Path
_project_root = _Path(__file__).resolve().parents[2]
_sys.path.insert(0, str(_project_root))
_sys.path.insert(0, str(_project_root / "src"))

import argparse
import json
from pathlib import Path
import time
import numpy as np
from scripts.qposd.extract_qposd_regions import ROOT, digest, load_pair, display_normalize
from sar_oil import core
from scripts.qposd.qposd_fast_features import features


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise SystemExit('Refuse to overwrite an existing measurement')
    protocol_path = ROOT/'results/qposd/protocol.json'
    protocol = json.loads(protocol_path.read_text(encoding='utf-8'))
    if 13 not in protocol['splits']['validation']:
        raise ValueError('Benchmark image must belong to validation')
    raw, _, source = load_pair(13)
    config = protocol['detection']['candidate_configs'][1]
    feature_image, _ = display_normalize(core.filter_image(raw, 'lee', size=7, looks=4))
    candidate_image, _ = display_normalize(core.filter_image(
        raw, config['filter'], size=config['size'], looks=config['looks']))
    labels = core.label(core.postprocess(core.threshold(candidate_image, **config['threshold']),
                                        operation='none', min_area=config['min_area']))
    start = time.perf_counter()
    expected, ids = core.features(feature_image, labels)
    original_seconds = time.perf_counter()-start
    start = time.perf_counter()
    actual, actual_ids = features(feature_image, labels)
    grouped_seconds = time.perf_counter()-start
    assert ids == actual_ids
    np.testing.assert_array_equal(actual, expected)
    report = {'image': 13, 'candidate_configuration_index': 1, **source,
              'objects': len(ids), 'ids_equal': True, 'features_exactly_equal': True,
              'max_abs_error_by_column': np.max(np.abs(actual-expected), axis=0).tolist(),
              'original_seconds_single_run': original_seconds,
              'grouped_seconds_single_run': grouped_seconds,
              'core_sha256': digest(ROOT/'src/sar_oil/core.py'),
              'grouped_code_sha256': digest(ROOT/'scripts/qposd/qposd_fast_features.py'),
              'benchmark_script_sha256': digest(Path(__file__)),
              'protocol_sha256': digest(protocol_path),
              'scope': 'One fixed validation candidate population; single-run timing, not a universal speed claim. No model fitting or configuration selection.'}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
