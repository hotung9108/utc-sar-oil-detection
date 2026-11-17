import sys
import unittest
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from scripts.cantarell.train_cantarell import sample_training, prediction, feature_rows


class PhysicalTrainingTests(unittest.TestCase):
    def test_purity_boundaries_and_determinism(self):
        X = np.arange(48).reshape(6, 8)
        purity = np.array([0, .05, .051, .499, .5, 1])
        x, y, keys = sample_training(X, purity, list(range(6)))
        self.assertEqual(keys, [0, 1, 4, 5])
        np.testing.assert_array_equal(y, [0, 0, 1, 1])
        np.testing.assert_array_equal(x, X[keys])

    def test_class_cap_and_sample_identity(self):
        X = np.arange(24000*8).reshape(24000, 8)
        p = np.repeat([0., 1.], 12000)
        first = sample_training(X, p, list(range(len(X))))
        second = sample_training(X, p, list(range(len(X))))
        self.assertEqual(first[2], second[2])
        np.testing.assert_array_equal(np.bincount(first[1]), [10000, 10000])
        np.testing.assert_array_equal(first[0], X[first[2]])

    def test_test_input_rejected_before_read(self):
        with self.assertRaisesRegex(ValueError, 'cannot use test'):
            feature_rows({'split': 'test'}, 'gamma0', {}, Path('missing'))

    def test_score_zero_is_negative_and_background_never_selected(self):
        labels = np.array([[0, 1, 1], [2, 2, 3]])
        actual = prediction(labels, np.array([1, 2, 3]), np.array([1., 0., -1.]))
        np.testing.assert_array_equal(actual, [[False, True, True], [False, False, False]])


if __name__ == '__main__':
    unittest.main()
