import copy
import json
from pathlib import Path
import sys
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'scripts'))
from prepare_qposd_protocol import ROOT, definition_v1, grouped_splits


class GroupSplitTests(unittest.TestCase):
    def test_real_overlap_groups_stay_together_with_minimum_changes(self):
        old = definition_v1()['splits']
        before = copy.deepcopy(old)
        shapes = json.loads((ROOT/'docs/management/qposd_shape_audit.json').read_text())
        audit = json.loads((ROOT/'docs/management/qposd_overlap_all24.json').read_text())
        result, groups, moved, feasible = grouped_splits(old, shapes, audit)
        flat = sum(result.values(), [])
        self.assertEqual(len(flat), len(set(flat)))
        self.assertEqual(set(flat), set(sum(old.values(), [])))
        self.assertEqual({k: len(v) for k, v in result.items()}, {'train': 14, 'validation': 5, 'test': 5})
        assignment = {n: k for k, ids in result.items() for n in ids}
        for group in groups:
            self.assertEqual(len({assignment[n] for n in group}), 1)
        # Crossing group must move >=1 image; fixed split sizes force >=1
        # compensating move. Reaching 2 attains that lower bound.
        self.assertEqual(moved, 2)
        self.assertGreater(feasible, 1)
        self.assertEqual(old, before)
        self.assertEqual(grouped_splits(old, shapes, audit)[0], result)


if __name__ == '__main__':
    unittest.main()
