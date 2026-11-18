"""Relocation lineage cannot excuse changed code or changed data."""
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from scripts import _provenance as provenance


class SourceRelocationTests(unittest.TestCase):
    def test_exact_relocation_accepted_but_modified_source_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            path=root/'scripts/group/tool.py'
            path.parent.mkdir(parents=True)
            path.write_bytes(b'original computation at new location')
            current=hashlib.sha256(path.read_bytes()).hexdigest()
            old=hashlib.sha256(b'old location imports').hexdigest()
            ledger=root/'docs/management/script_reorganization.json'
            ledger.parent.mkdir(parents=True)
            ledger.write_text(json.dumps({'source_relocations':{
                'scripts/group/tool.py':{'old_sha256':old,'new_sha256':current}}}))
            with patch.object(provenance,'ROOT',root):
                self.assertTrue(provenance.source_matches(path,old))
                self.assertTrue(provenance.source_matches(path,current))
                self.assertFalse(provenance.source_matches(path,'unrecorded hash'))
                path.write_bytes(b'changed algorithm')
                self.assertFalse(provenance.source_matches(path,old))
                self.assertFalse(provenance.source_matches(path,current))

    def test_data_without_relocation_must_match_its_real_hash(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            path=root/'model.json'; path.write_text('{}')
            ledger=root/'docs/management/script_reorganization.json'
            ledger.parent.mkdir(parents=True)
            ledger.write_text('{"source_relocations": {}}')
            with patch.object(provenance,'ROOT',root):
                self.assertFalse(provenance.source_matches(path,'old data hash'))
                self.assertFalse(provenance.committed_relocation(path))


if __name__ == '__main__':
    unittest.main()
