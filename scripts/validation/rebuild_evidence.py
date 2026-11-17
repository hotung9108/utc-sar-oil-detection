"""Rebuild numeric reports and execute all ten notebooks from frozen results.

Requires the previously downloaded raw data. Does not download, fit, select new
models, or regenerate reviewed Word/PowerPoint/video deliverables.
"""

import sys as _sys
from pathlib import Path as _Path
_project_root = _Path(__file__).resolve().parents[2]
_sys.path.insert(0, str(_project_root))
_sys.path.insert(0, str(_project_root / "src"))

from scripts._provenance import source_matches
from scripts._paths import resolve_path

import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[2]


def sha(path):
    return hashlib.sha256(resolve_path(path).read_bytes()).hexdigest()


def main():
    primary = sorted((ROOT / 'notebooks').glob('*.ipynb'))
    extra = [ROOT / 'notebooks/external' / name for name in (
        '06_dartis_false_alarms.ipynb', '07_sentinel_calibration.ipynb',
        '08_qposd_audit.ipynb', '09_palsar_frozen_pipelines.ipynb',
        '10_qposd_classification_detection.ipynb')]
    assert len(primary) == 5 and all(p.is_file() for p in extra)
    protected = [ROOT / name for name in (
        'data/manifest.json', 'results/sos/selected.json', 'results/sos/svm_model.json',
        'results/sos/cart_model.json', 'results/sos/evaluation.json',
        'results/sos/adaptive/selected.json', 'results/sos/adaptive/cart_model.json',
        'results/sos/adaptive/svm_model.json', 'results/dartis/protocol.json',
        'results/dartis/evaluation.json', 'results/sos/external_palsar_train/protocol.json',
        'results/sos/external_palsar_train/otsu.json',
        'results/sos/external_palsar_train/niblack.json')]
    protected += sorted((ROOT/'results/qposd').rglob('*.json'))
    protected += sorted((ROOT/'results/qposd/test').glob('*.png'))
    protected += sorted((ROOT/'results/physical').glob('*.json'))
    before = {p.relative_to(ROOT).as_posix(): sha(p) for p in protected}
    commands = [['scripts/validation/verify_outputs.py'], ['scripts/sos_experiments/summarize_results.py'],
                ['scripts/dartis/report_dartis.py'], ['scripts/sos_experiments/report_palsar_holdout.py'],
                ['scripts/qposd/report_qposd.py']]
    commands += [['scripts/run_notebooks.py', '--notebook', p.relative_to(ROOT).as_posix()]
                 for p in primary + extra]
    commands += [['scripts/validation/verify_outputs.py']]
    log = {'scope': 'Rebuild reports and rerun notebook computations from frozen evidence; not full retraining or DOCX/PPTX/video production',
           'script_sha256': sha(Path(__file__)), 'protected_sha256': before,
           'expected_steps': len(commands), 'steps': [], 'passed': False}
    output = ROOT / 'docs/management/evidence_rebuild_audit.json'
    for command in commands:
        print('Running:', *command, flush=True)
        start = time.perf_counter()
        process = subprocess.run([sys.executable, *command], cwd=ROOT)
        unchanged = before == {p.relative_to(ROOT).as_posix(): sha(p) for p in protected}
        log['steps'].append({'command': command, 'exit_code': process.returncode,
                             'seconds': time.perf_counter() - start,
                             'frozen_sources_unchanged': unchanged})
        log['passed'] = process.returncode == 0 and unchanged and len(log['steps']) == len(commands)
        output.write_text(json.dumps(log, indent=2) + '\n', encoding='utf-8')
        if process.returncode or not unchanged:
            raise SystemExit(process.returncode or 'Frozen evidence changed during rebuild')
    print('All reports and ten notebooks completed; frozen models/protocols unchanged.')


if __name__ == '__main__':
    main()
