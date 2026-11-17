"""Validate saved source hashes across an explicitly recorded file relocation.

Never relabel the current file hash as an old SHA-256. New outputs retain their
real hashes. Old experiment artifacts remain immutable and can be read only
when the exact migrated source matches the reviewed relocation record.
"""
import hashlib
import json
from pathlib import Path
import subprocess

from scripts._paths import ROOT, resolve_path


def relocation(path):
    path = resolve_path(path)
    try:
        relative = path.resolve().relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        return None
    ledger = ROOT/'docs/management/script_reorganization.json'
    data = json.loads(ledger.read_text(encoding='utf-8'))
    return data.get('source_relocations', {}).get(relative)


def source_matches(path, expected, actual=None):
    path = resolve_path(path)
    if actual is None:
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
    if actual == expected:
        return True
    record = relocation(path)
    return bool(record and expected == record['old_sha256']
                and actual == record.get('new_sha256'))


def committed_relocation(path):
    """Only accept a recorded relocation of a source present in Git history.

This never exempts data, selections, protocols, or model files from commit gates.
"""
    path = resolve_path(path)
    record = relocation(path)
    if not record or not source_matches(path, record['old_sha256']):
        return False
    data = json.loads((ROOT/'docs/management/script_reorganization.json').read_text())
    original = subprocess.run(['git','show', f"{data['baseline_git_commit']}:{record['old_path']}"],
                              cwd=ROOT, capture_output=True)
    return (original.returncode == 0 and
            hashlib.sha256(original.stdout).hexdigest() == record['old_sha256'])
