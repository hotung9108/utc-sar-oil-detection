import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts import streamlit_physical as physical


class PhysicalWebGateTests(unittest.TestCase):
    def test_evaluation_alone_does_not_enable_physical_mode(self):
        with tempfile.TemporaryDirectory() as directory, patch.object(physical, 'ROOT', Path(directory)):
            path = Path(directory)/'results/cantarell/evaluation.json'
            path.parent.mkdir(parents=True)
            path.write_text(json.dumps({'complete':True}))
            self.assertFalse(physical.ready())
            with self.assertRaisesRegex(ValueError, 'independent result verification'):
                physical.setup()

    def test_failed_verification_is_rejected_before_loading_models(self):
        with tempfile.TemporaryDirectory() as directory, patch.object(physical, 'ROOT', Path(directory)):
            root = Path(directory)
            path = root/'results/cantarell/evaluation.json'
            path.parent.mkdir(parents=True)
            path.write_text('{}')
            audit = root/'docs/management/cantarell_results_verification.json'
            audit.parent.mkdir(parents=True)
            audit.write_text(json.dumps({'passed':False}))
            with self.assertRaisesRegex(ValueError, 'missing or stale'):
                physical.setup()


if __name__ == '__main__':
    unittest.main()
