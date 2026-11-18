import sys
from pathlib import Path
import unittest
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'scripts'))
from scripts.qposd.audit_qposd_overlap import exact_anchors


class QposdOverlapTests(unittest.TestCase):
    def test_finds_offset_and_verifies_entire_overlap(self):
        source = np.random.default_rng(2026).random((24, 30))
        target = source[3:, 4:]
        result = exact_anchors(source, target, stride=4, size=3)
        row = next(r for r in result['translations'] if r['target_minus_source_offset_yx'] == [-3, -4])
        self.assertTrue(row['entire_overlap_exact'])
        self.assertEqual(row['overlap_pixels'], target.size)

    def test_constant_or_radiometrically_changed_not_claimed_overlap(self):
        source = np.random.default_rng(2026).random((20, 20))
        self.assertEqual(exact_anchors(source, source*2, stride=4)['translations'], [])
        self.assertEqual(exact_anchors(np.ones((20, 20)), np.ones((20, 20)))['sampled_nonconstant_patches'], 0)


if __name__ == '__main__':
    unittest.main()
