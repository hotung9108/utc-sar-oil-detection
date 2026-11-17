"""Frozen input manifests and pre-score provenance gates for physical experiments."""

import sys as _sys
from pathlib import Path as _Path
_project_root = _Path(__file__).resolve().parents[2]
_sys.path.insert(0, str(_project_root))
_sys.path.insert(0, str(_project_root / "src"))

import hashlib
import json
import subprocess
from collections import Counter
from pathlib import Path

import numpy as np


from scripts._provenance import source_matches
from scripts._paths import resolve_path
from scripts.cantarell.audit_cantarell_source import ROOT

FOLDER = ROOT/'docs/management'
MANIFEST = FOLDER/'cantarell_eligible_manifest.json'
MODEL_PROTOCOL = FOLDER/'cantarell_model_protocol_v1.json'


def sha(path):
    return hashlib.sha256(resolve_path(path).read_bytes()).hexdigest()


def require_committed(path, *, allow_relocated=False):
    from scripts._provenance import committed_relocation
    path = resolve_path(path)
    if allow_relocated and committed_relocation(path):
        return
    relative = path.resolve().relative_to(ROOT.resolve()).as_posix()
    exists = subprocess.run(['git','cat-file','-e',f'HEAD:{relative}'],cwd=ROOT,capture_output=True)
    diff = subprocess.run(['git','diff','--quiet','HEAD','--',relative],cwd=ROOT,capture_output=True)
    if exists.returncode or diff.returncode:
        raise ValueError(f'Commit unchanged evidence/code before scoring: {relative}')


def freeze_manifest():
    verification_path = FOLDER/'cantarell_physical_verification.json'
    audit_path = FOLDER/'cantarell_physical_preparation_audit.json'
    if not verification_path.exists():
        raise ValueError('Run the complete physical-data verifier before freezing model inputs')
    verified,audit = json.loads(verification_path.read_text()),json.loads(audit_path.read_text())
    if not verified['data_ready_for_model_protocol'] or verified['pending'] or not audit['complete_preparation']:
        raise ValueError('Full physical-data gate has not passed')
    if (not source_matches(audit_path, verified['final_audit_sha256'], sha(audit_path))) or verified['binding']!=audit['binding']:
        raise ValueError('Verification does not bind the current completed audit')
    if (not source_matches(ROOT/'scripts/cantarell/report_cantarell_physical.py', verified['script_sha256'], sha(ROOT/'scripts/cantarell/report_cantarell_physical.py'))):
        raise ValueError('Verification script changed after the complete data check')
    for relative,expected in audit['binding']['source_hashes'].items():
        if (not source_matches(ROOT/'scripts'/relative, expected, sha(ROOT/'scripts'/relative))):
            raise ValueError('Physical preparation source changed after verification')
    if (not source_matches(FOLDER/'cantarell_physical_metadata_audit.json', audit['binding']['metadata_sha256'], sha(FOLDER/'cantarell_physical_metadata_audit.json'))):
        raise ValueError('Physical metadata evidence changed after verification')
    protocol = json.loads(MODEL_PROTOCOL.read_text())
    data_path = FOLDER/'cantarell_data_protocol_v1.json'
    if (not source_matches(data_path, protocol['data_protocol_sha256'], sha(data_path))):
        raise ValueError('Model/data protocol mismatch')
    for relative,expected in protocol['existing_algorithm_source_hashes'].items():
        if (not source_matches(ROOT/relative, expected, sha(ROOT/relative))):
            raise ValueError('Frozen algorithm source changed')
    files = ['scripts/cantarell/cantarell_experiment_data.py','scripts/cantarell/cantarell_pipeline.py','scripts/cantarell/screen_cantarell.py',
             'src/sar_oil/core.py','src/sar_oil/reference.py','src/sar_oil/evaluation.py',
             'src/sar_oil/models.py','scripts/qposd/qposd_fast_features.py']
    operator_path = FOLDER/'cantarell_operator_verification.json'
    operators = json.loads(operator_path.read_text())
    if (not source_matches(MODEL_PROTOCOL, operators['model_protocol_sha256'], sha(MODEL_PROTOCOL))) or not operators['all_real_shared_features_close']:
        raise ValueError('Operator verification does not support the current protocol')
    for relative,expected in operators['source_hashes'].items():
        if (not source_matches(ROOT/relative, expected, sha(ROOT/relative))):
            raise ValueError('Operator source changed since its verification')
    rows = []
    wind_path = FOLDER/'cantarell_wind_audit.json'
    wind = {r['sample']:r for r in json.loads(wind_path.read_text())['results']}
    for r in audit['results']:
        if r['eligible']:
            if (not source_matches(ROOT/r['file'], r['sha256'], sha(ROOT/r['file']))):
                raise ValueError('Prepared array changed after verification')
            rows.append({k:r[k] for k in ['sample','group','scene','split','file','sha256','crop']})
            rows[-1]['wind_speed_m_s'] = wind[r['sample']]['speed_m_s']
    manifest = {'model_protocol_sha256':sha(MODEL_PROTOCOL),'data_protocol_sha256':sha(data_path),
                'verification_sha256':sha(verification_path),'preparation_audit_sha256':sha(audit_path),
                'operator_verification_sha256':sha(operator_path),
                'wind_audit_sha256':sha(wind_path),'preparation_binding':audit['binding'],
                'execution_source_hashes':{p:sha(ROOT/p) for p in files},
                'samples':rows,'counts':dict(Counter(r['split'] for r in rows)),
                'excluded':verified['excluded'],'no_detection_scores_computed_when_frozen':True}
    if MANIFEST.exists():
        if json.loads(MANIFEST.read_text())!=manifest:
            raise ValueError('Refusing to overwrite a changed eligible manifest')
    else:
        MANIFEST.write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'manifest':str(MANIFEST),'counts':manifest['counts'],'must_commit_before_scoring':True},indent=2))


def load_manifest(stage_files=()):
    if not MANIFEST.exists():
        raise ValueError('Eligible manifest is not frozen; no detection scoring is allowed')
    manifest = json.loads(MANIFEST.read_text())
    require_committed(MANIFEST)
    require_committed(MODEL_PROTOCOL)
    if (not source_matches(MODEL_PROTOCOL, manifest['model_protocol_sha256'], sha(MODEL_PROTOCOL))):
        raise ValueError('Model protocol changed after input freeze')
    for relative,expected in manifest['execution_source_hashes'].items():
        path = ROOT/relative
        require_committed(path, allow_relocated=True)
        if (not source_matches(path, expected, sha(path))):
            raise ValueError(f'Execution source changed after input freeze: {relative}')
    for relative in stage_files:
        require_committed(ROOT/relative)
    return manifest,json.loads(MODEL_PROTOCOL.read_text())


def load_input(row,branch,allow_test=False):
    if branch not in ('sigma0','gamma0'):
        raise ValueError('Unknown radiometry branch')
    if row['split']=='test':
        if not allow_test:
            raise ValueError('Test data cannot enter screening or fitting')
        require_committed(ROOT/'results/cantarell/selection.json')
    path = ROOT/row['file']
    if (not source_matches(path, row['sha256'], sha(path))):
        raise ValueError('Frozen physical input hash mismatch')
    with np.load(path,allow_pickle=False) as data:
        return data[branch],data['truth']


if __name__=='__main__':
    freeze_manifest()
