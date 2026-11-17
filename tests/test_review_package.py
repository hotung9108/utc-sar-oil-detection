import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
import zipfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from scripts.packaging.verify_review_package import verify


class PackageTests(unittest.TestCase):
    def make_zip(self, path, payload=b'abcd', extra=None):
        manifest = {'format': 'sar-review-package-v1', 'submission_ready': False,
                    'files': [{'path': 'README.md', 'bytes': 4,
                               'sha256': hashlib.sha256(b'abcd').hexdigest()}]}
        with zipfile.ZipFile(path, 'w') as archive:
            archive.writestr('PACKAGE_MANIFEST.json', json.dumps(manifest))
            archive.writestr('README.md', payload)
            if extra:
                archive.writestr(extra, b'x')

    def test_valid_package_is_not_marked_submission_ready(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'p.zip'; self.make_zip(path)
            result = verify(path)
            self.assertEqual(result['verified_files'], 1)
            self.assertFalse(result['submission_ready'])

    def test_equal_size_corruption_is_detected(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'p.zip'; self.make_zip(path, b'abce')
            with self.assertRaisesRegex(ValueError, 'SHA-256'):
                verify(path)

    def test_unlisted_and_unsafe_files_are_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            for extra in ['extra.txt', '../escape.txt']:
                path = Path(folder) / 'p.zip'; self.make_zip(path, extra=extra)
                with self.assertRaises(ValueError):
                    verify(path)


if __name__ == '__main__':
    unittest.main()
