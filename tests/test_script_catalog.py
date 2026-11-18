"""Moving tools must not invalidate research provenance or command discovery."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]


class ScriptOrganizationTests(unittest.TestCase):
    def test_relocation_sources_and_paths_match_record(self):
        record = json.loads((ROOT/'docs/management/script_reorganization.json').read_text())
        for relative, row in record['source_relocations'].items():
            with self.subTest(path=relative):
                self.assertEqual(hashlib.sha256((ROOT/relative).read_bytes()).hexdigest(), row['new_sha256'])
        for old, new in record['moves'].items():
            self.assertFalse((ROOT/old).exists())
            self.assertTrue((ROOT/new).is_file())

    def test_catalog_covers_tools_and_unique_names(self):
        rows = json.loads((ROOT/'scripts/catalog.json').read_text())
        self.assertEqual(len(rows), len({r['task'] for r in rows}))
        actual = {p.relative_to(ROOT).as_posix() for p in (ROOT/'scripts').rglob('*')
                  if p.suffix in {'.py','.mjs','.ps1'} and '__pycache__' not in p.parts
                  and 'nasa_crawler' not in p.parts and p.name != 'tasks.py' and not p.name.startswith('_')}
        self.assertEqual({r['path'] for r in rows}, actual)

    def test_launcher_forwards_help_from_another_directory(self):
        result = subprocess.run([sys.executable, str(ROOT/'scripts/tasks.py'), 'run',
                                 'sos/sos', '--', '--help'], cwd=ROOT/'tests',
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('--selection', result.stdout)


if __name__ == '__main__':
    unittest.main()
