import sys
from pathlib import Path
import unittest
import numpy as np
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'src'))
sys.path.insert(0, str(ROOT/'scripts'))
from sar_oil.core import features as original
from scripts.qposd.qposd_fast_features import features


class GroupedFeatureTests(unittest.TestCase):
    def test_empty_single_pixel_border_and_noncontiguous_ids(self):
        a = np.random.default_rng(2026).random((32, 40))
        empty = np.zeros(a.shape, int)
        full = np.full(a.shape, 9)
        mixed = empty.copy()
        mixed[0, 0] = 7
        mixed[1:10, 30:40] = 3
        mixed[20:30, 2:12] = 17
        mixed[22:25, 5:8] = 0
        mixed[30, 39] = 7
        for labels in (empty, full, mixed):
            before = labels.copy()
            expected, ids = original(a, labels)
            actual, actual_ids = features(a, labels)
            self.assertEqual(ids, actual_ids)
            np.testing.assert_array_equal(actual, expected)
            np.testing.assert_array_equal(labels, before)


if __name__ == '__main__':
    unittest.main()
