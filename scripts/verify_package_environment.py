"""Verify an extracted package using its own freshly installed virtual environment.

Install first with `uv sync --frozen --extra demo` in the extracted directory.
No raw SAR images or training are involved in the startup smoke check.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project', type=Path, required=True)
    parser.add_argument('--output', type=Path, default=ROOT / 'docs/management/package_environment_audit.json')
    parser.add_argument('--package', type=Path, help='Original ZIP to bind the extracted files to the audit')
    args = parser.parse_args()
    project = args.project.resolve()
    interpreter = project / ('.venv/Scripts/python.exe' if os.name == 'nt' else '.venv/bin/python')
    config = (project / '.venv/pyvenv.cfg').read_text()
    assert 'include-system-site-packages = false' in config
    assert interpreter.is_file()
    manifest = json.loads((project / 'PACKAGE_MANIFEST.json').read_text(encoding='utf-8'))
    package_sha256 = None
    if args.package:
        import zipfile
        from verify_review_package import verify
        verify(args.package)
        package_sha256 = hashlib.sha256(args.package.read_bytes()).hexdigest()
        with zipfile.ZipFile(args.package) as archive:
            assert archive.read('PACKAGE_MANIFEST.json') == (project / 'PACKAGE_MANIFEST.json').read_bytes()
        for row in manifest['files']:
            assert hashlib.sha256((project / row['path']).read_bytes()).hexdigest() == row['sha256'], row['path']
    for name in ['uv.lock', 'pyproject.toml']:
        expected = next(r['sha256'] for r in manifest['files'] if r['path'] == name)
        assert hashlib.sha256((project / name).read_bytes()).hexdigest() == expected
    env = dict(os.environ, PYTHONIOENCODING='utf-8', QT_QPA_PLATFORM='offscreen')
    env.pop('PYTHONPATH', None)
    env.pop('VIRTUAL_ENV', None)
    log_dir = project / '.cache/environment-check'
    log_dir.mkdir(parents=True, exist_ok=True)

    def run(name, command):
        process = subprocess.run([str(interpreter), *command], cwd=project, env=env,
                                 capture_output=True, text=True, encoding='utf-8')
        (log_dir / f'{name}.log').write_text(process.stdout + process.stderr, encoding='utf-8')
        if process.returncode:
            raise RuntimeError(f'{name} failed; inspect {log_dir / (name + ".log")}')
        print(f'{name}: passed', flush=True)
        return process.stdout

    run('saved_evidence_and_tests', ['run_experiments.py', '--verify-only'])
    info = json.loads(run('environment', ['-c',
        'import sys,json,importlib.metadata as m; print(json.dumps({"python":sys.version,"prefix":sys.prefix,"base_prefix":sys.base_prefix,"executable":sys.executable,"packages":{d.metadata["Name"]:d.version for d in m.distributions()}}))']))
    assert Path(info['prefix']).resolve() == (project / '.venv').resolve()
    smoke = run('qt_and_models', ['-c', '''
import sys,json
from pathlib import Path
import numpy as np
from PIL import Image
root=Path.cwd();sys.path.insert(0,str(root/'scripts'))
import demo_engine as engine
from demo_qt import QApplication,Window,configure_app
assert Path(engine.__file__).resolve().is_relative_to(root)
app=QApplication([]);configure_app(app);window=Window();window.show();app.processEvents()
assert window.isVisible() and window.choice.count()==2
sample=root/'.cache/environment-check/constant.png'
Image.fromarray(np.full((32,32),128,dtype=np.uint8)).save(sample)
checks=[]
for selection in engine.SELECTIONS.values():
    result=engine.infer(sample,selection)
    assert result['mask'].shape==(32,32) and not result['mask'].any()
    assert result['metadata']['ground_truth_used_for_inference'] is False
    checks.append(str(selection.relative_to(root)))
window.close();app.processEvents();assert not window.isVisible()
print(json.dumps({'qt_startup':True,'models_loaded':checks,'input':'Constant synthetic 32x32; startup smoke only, not detection accuracy'}))
'''])
    runner = json.loads((project / 'results/sos/runner_verify.json').read_text())
    assert runner['passed']
    audit = {'project': str(project), 'package_sha256': package_sha256,
             'all_extracted_files_verified_before_execution': bool(args.package),
             'environment': info, 'runner': runner,
             'qt_and_models': json.loads(smoke), 'fresh_venv_verified': True,
             'lock_and_project_match_package': True, 'system_site_packages': False,
             'logs': str(log_dir), 'submission_ready': False,
             'scope': 'New venv on the same Windows host, installed from the frozen lock. No claim of another OS, full retraining, or real-image GUI validation in this environment.'}
    args.output.write_text(
        json.dumps(audit, indent=2) + '\n', encoding='utf-8')


if __name__ == '__main__':
    main()
