import sys
import unittest
from pathlib import Path
import numpy as np

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from scripts.cantarell.analyze_cantarell_failures import object_size_recall


class SizeDiagnosticTests(unittest.TestCase):
    def test_small_contained_gt_cannot_match_min_area_64(self):
        pred = np.zeros((12,12),bool); pred[2:10,2:10]=True
        gt = np.zeros_like(pred); gt[3:6,3:6]=True
        result = object_size_recall(pred,gt)
        self.assertEqual(result['below_32'],{'gt':1,'matched':0})

    def test_full_overlap_and_empty_cases(self):
        gt = np.zeros((20,20),bool); gt[1:9,1:9]=True; gt[15,15]=True
        result = object_size_recall(gt,gt)
        self.assertEqual(result['at_least_64'],{'gt':1,'matched':1})
        self.assertEqual(result['below_32'],{'gt':1,'matched':1})
        empty = object_size_recall(np.zeros_like(gt),np.zeros_like(gt))
        self.assertEqual(sum(v['gt'] for v in empty.values()),0)


if __name__=='__main__':
    unittest.main()
