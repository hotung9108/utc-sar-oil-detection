"""Ensure the test runner rejects a winner inconsistent with validation."""
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'scripts'))
import evaluate_qposd_test as runner
from qposd_metrics import detection, summarize_detections


class QposdTestGateTests(unittest.TestCase):
    def fixture(self, directory):
        configs = [{'synthetic_config': i} for i in range(10)]
        protocol = {'splits': {'validation': [1, 2, 3, 4, 5]},
                    'detection': {'candidate_configs': configs}}
        truth = np.array([[1, 0, 2]])
        rows = []
        for i, config in enumerate(configs):
            metric = detection(truth if i == 0 else np.zeros_like(truth), truth)
            images = [{'number': n, 'numpy': metric} for n in range(1, 6)]
            rows.append({'index': i, 'config': config, 'images': images,
                         'numpy_summary': summarize_detections([metric]*5)})
        model = {'synthetic_model': 'fixed'}
        selection = {'classifier': model, 'inputs_sha256': {},
                     'configurations': rows, 'winner_index': 0}
        for key, source in (
                ('script_sha256', 'scripts/select_qposd_detection.py'),
                ('pipeline_sha256', 'scripts/qposd_pipeline.py'),
                ('metrics_sha256', 'scripts/qposd_metrics.py')):
            selection[key] = runner.digest(runner.ROOT/source)
        path = directory/'detection_selection.json'
        path.write_text(json.dumps(selection), encoding='utf-8')
        return path, protocol, model, selection

    def test_accepts_only_the_predeclared_validation_winner(self):
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            path, protocol, model, selection = self.fixture(directory)
            with patch.object(runner, 'DEST', directory):
                config, _ = runner.frozen_detection(protocol, model)
                self.assertEqual(config, {'synthetic_config': 0})
                selection['winner_index'] = 2
                path.write_text(json.dumps(selection), encoding='utf-8')
                with self.assertRaisesRegex(ValueError, 'winner violates'):
                    runner.frozen_detection(protocol, model)

    def test_rejects_missing_validation_image_and_altered_summary(self):
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            path, protocol, model, selection = self.fixture(directory)
            selection['configurations'][0]['numpy_summary']['macro_f1'] = .5
            path.write_text(json.dumps(selection), encoding='utf-8')
            with patch.object(runner, 'DEST', directory):
                with self.assertRaisesRegex(ValueError, 'summary'):
                    runner.frozen_detection(protocol, model)
            path, protocol, model, selection = self.fixture(directory)
            selection['configurations'][0]['images'].pop()
            path.write_text(json.dumps(selection), encoding='utf-8')
            with patch.object(runner, 'DEST', directory):
                with self.assertRaisesRegex(ValueError, 'population'):
                    runner.frozen_detection(protocol, model)


if __name__ == '__main__':
    unittest.main()
