"""Check denominators and prevent incomplete external results being published."""
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import dartis_results
from evaluate_dartis import aggregate


class DartisReportingTests(unittest.TestCase):
    def test_pixel_fraction_is_weighted_by_pixels_not_images(self):
        rows = [
            {'false_alarm': True, 'retained_regions': 2, 'predicted_oil_pixels': 10, 'pixels': 10},
            {'false_alarm': False, 'retained_regions': 0, 'predicted_oil_pixels': 0, 'pixels': 90},
        ]
        result = aggregate(rows)
        self.assertEqual(result['false_alarm_rate'], 0.5)
        self.assertEqual(result['retained_regions_per_image'], 1.0)
        self.assertEqual(result['predicted_oil_pixel_fraction'], 0.1)
        self.assertNotIn('recall', result)
        self.assertNotIn('f1', result)

    def test_empty_population_is_undefined_not_zero_false_alarms(self):
        result = aggregate([])
        self.assertIsNone(result['false_alarm_rate'])
        self.assertIsNone(result['predicted_oil_pixel_fraction'])

    def test_incomplete_checkpoint_cannot_be_reported_as_complete(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            def write(name, data):
                path = root / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(json.dumps(data), encoding='utf-8')
            provenance = {key:'fixture' for key in (
                'protocol_sha256','manifest_sha256','script_sha256','selected_sha256','model_sha256')}
            write('results/dartis/evaluation.json', {
                'provenance':provenance, 'complete':False, 'expected':2290,
                'completed':1, 'per_image':[]})
            write('results/dartis/protocol.json', provenance)
            write('results/sos/selected.json', {'model_file':'model.json'})
            write('data/dartis/catalog_manifest.json', [])
            # Isolate the population guard; no inference or actual data are fabricated.
            with patch.object(dartis_results, 'ROOT', root), \
                    patch.object(dartis_results, 'ensure_run'), \
                    patch.object(dartis_results, 'digest', return_value='fixture'):
                with self.assertRaisesRegex(ValueError, 'Incomplete or duplicate population'):
                    dartis_results.verified_results()


if __name__ == '__main__':
    unittest.main()
