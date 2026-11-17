"""Verify a review ZIP against its internal file manifest without extracting it."""

import sys as _sys
from pathlib import Path as _Path
_project_root = _Path(__file__).resolve().parents[2]
_sys.path.insert(0, str(_project_root))
_sys.path.insert(0, str(_project_root / "scripts"))

import argparse
import hashlib
import json
from pathlib import PurePosixPath
import zipfile


def verify(path):
    with zipfile.ZipFile(path) as archive:
        names = archive.namelist()
        if len(names) != len(set(names)):
            raise ValueError('Duplicate ZIP paths')
        for name in names:
            p = PurePosixPath(name)
            if p.is_absolute() or '..' in p.parts or '\\' in name or ':' in name:
                raise ValueError('Unsafe ZIP path')
        manifest = json.loads(archive.read('PACKAGE_MANIFEST.json'))
        if manifest['format'] != 'sar-review-package-v1':
            raise ValueError('Unsupported manifest')
        entries = manifest['files']
        expected = [r['path'] for r in entries]
        if len(expected) != len(set(expected)) or set(names) != set(expected) | {'PACKAGE_MANIFEST.json'}:
            raise ValueError('ZIP contents differ from manifest')
        for row in entries:
            info = archive.getinfo(row['path'])
            if info.file_size != row['bytes']:
                raise ValueError(f"Size mismatch: {row['path']}")
            digest = hashlib.sha256()
            with archive.open(info) as source:
                while chunk := source.read(1024 * 1024):
                    digest.update(chunk)
            if digest.hexdigest() != row['sha256']:
                raise ValueError(f"SHA-256 mismatch: {row['path']}")
    return {'verified_files': len(entries), 'submission_ready': manifest['submission_ready'],
            'scope': 'Internal byte consistency only, not authenticity or scientific completion'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('zip_path')
    print(json.dumps(verify(parser.parse_args().zip_path)))
