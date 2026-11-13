import sys
from pathlib import Path
import unittest
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'scripts'))
from qposd_pipeline import infer


class FixedClassifier:
    def scores(self, features):
        # Deterministic synthetic stub, not a trained QPOSD model.
        return np.ones(len(features))


class QposdPipelineTests(unittest.TestCase):
    def config(self, name='otsu'):
        return {'filter': 'lee', 'size': 7, 'looks': 4, 'min_area': 64,
                'morphology': 'none', 'threshold': {'name': name, 'size': 31, 'k': .2}}

    def test_constant_image_has_no_spurious_regions(self):
        for backend in ('numpy', 'reference'):
            result = infer(np.ones((64, 64)), self.config(), FixedClassifier(), backend)
            self.assertFalse(result['prediction'].any())
            self.assertEqual(result['rows'], [])

    def test_dark_region_and_library_agreement(self):
        y, x = np.mgrid[:96, :96]
        raw = 1 + .01*np.sin(x)*np.cos(y)
        raw[30:65, 20:75] *= .1
        original = raw.copy()
        for threshold in ('otsu', 'niblack'):
            own = infer(raw, self.config(threshold), FixedClassifier())
            ref = infer(raw, self.config(threshold), FixedClassifier(), 'reference')
            self.assertGreater(len(own['rows']), 0)
            self.assertTrue(all(r['area'] >= 64 for r in own['rows']))
            np.testing.assert_array_equal(own['candidate_mask'], ref['candidate_mask'])
            np.testing.assert_array_equal(own['prediction'], ref['prediction'])
        np.testing.assert_array_equal(raw, original)

    def test_invalid_physical_input_rejected(self):
        for raw in (np.array([[0, -1], [1, 1]]), np.full((3, 3), np.nan)):
            with self.assertRaises(ValueError):
                infer(raw, self.config(), FixedClassifier())


if __name__ == '__main__':
    unittest.main()
