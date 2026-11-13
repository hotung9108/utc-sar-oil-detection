import sys
import unittest
from pathlib import Path

import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'scripts'))
from qposd_metrics import classification, detection, matches, summarize_detections


class QposdMetricTests(unittest.TestCase):
    def test_swapped_classes_are_not_true_positives(self):
        truth = np.array([[1, 1, 0, 2, 2]], dtype=np.uint8)
        result = detection(np.array([[2, 2, 0, 1, 1]]), truth)
        for row in result['classes'].values():
            self.assertEqual((row['tp'], row['fp'], row['fn']), (0, 1, 1))
        self.assertEqual(result['spatial_confusion']['true_by_predicted'], [[0, 1], [1, 0]])

    def test_merge_cannot_match_two_truth_objects(self):
        # Two 2-pixel regions merged by a 1-pixel bridge, IoU .4 each.
        result = detection(np.ones((1, 5), dtype=int), np.array([[1, 1, 0, 1, 1]]), .4)
        self.assertEqual([result['classes']['oil'][k] for k in ('tp', 'fp', 'fn')], [1, 0, 1])
        split = detection(np.array([[1, 1, 0, 1, 1]]), np.ones((1, 5), dtype=int), .4)
        self.assertEqual([split['classes']['oil'][k] for k in ('tp', 'fp', 'fn')], [1, 1, 0])

    def test_land_is_negative_and_unknown_is_ignored(self):
        truth = np.array([[3, 0, 255, 0, 1]])
        prediction = np.array([[1, 0, 1, 0, 1]])
        before = prediction.copy()
        result = detection(prediction, truth)
        self.assertEqual([result['classes']['oil'][k] for k in ('tp', 'fp', 'fn')], [1, 1, 0])
        self.assertEqual(result['classes']['oil']['below_64']['gt'], 1)
        np.testing.assert_array_equal(prediction, before)

    def test_cardinality_precedes_iou(self):
        iou = np.array([[.9, .4], [.4, 0]])
        pi, gi = matches(iou, iou >= .4)
        self.assertEqual(set(zip(pi, gi)), {(0, 1), (1, 0)})

    def test_empty_and_threshold_boundary(self):
        empty = detection(np.zeros((2, 2), int), np.zeros((2, 2), int))
        self.assertIsNone(empty['macro_f1'])
        hit = detection(np.array([[1, 0]]), np.array([[1, 1]]))
        self.assertEqual(hit['classes']['oil']['tp'], 1)

    def test_classification_rates_match_manual_counts(self):
        result = classification([0, 0, 1, 1, 1], [0, 1, 0, 1, 1])
        self.assertEqual(result['confusion_true_by_predicted'], [[1, 1], [1, 2]])
        self.assertEqual(result['look_alike_as_oil_rate'], .5)
        self.assertEqual(result['oil_as_look_alike_rate'], 1/3)
        self.assertAlmostEqual(result['macro_f1'], (.5+2/3)/2)

    def test_population_pools_counts_before_f1(self):
        good = detection(np.array([[1, 0, 2]]), np.array([[1, 0, 2]]))
        bad = detection(np.array([[0, 0, 0]]), np.array([[1, 0, 2]]))
        result = summarize_detections([good, bad])
        self.assertAlmostEqual(result['macro_f1'], 2/3)
        self.assertEqual(result['classes']['oil']['below_64']['recall'], .5)
        self.assertEqual(result['spatial_confusion']['unmatched_truth'], [1, 1])


if __name__ == '__main__':
    unittest.main()
