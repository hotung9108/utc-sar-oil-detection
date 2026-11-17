"""Synthetic integration checks, never reported as QPOSD accuracy."""
import contextlib
import io
from pathlib import Path
import sys
import unittest

import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'scripts'))
from train_qposd_classifiers import compare_models, reject_cross_split_overlap


class QposdTrainingTests(unittest.TestCase):
    def test_exact_overlap_blocks_different_splits(self):
        pair = {'first': 22, 'second': 35, 'translations': [{'entire_overlap_exact': True}]}
        with self.assertRaisesRegex(ValueError, 'crosses splits'):
            reject_cross_split_overlap(pair, {22: 'train', 35: 'test'})
        reject_cross_split_overlap(pair, {22: 'train', 35: 'train'})

    def test_no_exact_overlap_does_not_claim_scene_independence(self):
        pair = {'first': 22, 'second': 35, 'translations': []}
        self.assertIsNone(reject_cross_split_overlap(pair, {22: 'train', 35: 'test'}))

    def test_models_share_train_scaling_and_ties_use_order(self):
        X = np.zeros((8, 8))
        X[:, 0] = [-4, -3, -2, -1, 1, 2, 3, 4]
        y = (X[:, 0] > 0).astype(int)
        V = np.zeros((4, 8))
        V[:, 0] = [-100, -10, 10, 100]
        truth = (V[:, 0] > 0).astype(int)
        identities = [{'image': 99, 'object_id': i+1, 'area': 1, 'truth': int(t)}
                      for i, t in enumerate(truth)]
        configs = [{'kind': 'cart', 'params': {'max_depth': 2, 'min_leaf': 1}},
                   {'kind': 'svm', 'params': {'C': 1.}}]
        original = (X.copy(), V.copy())
        with contextlib.redirect_stdout(io.StringIO()):
            rows, models, winner = compare_models(configs, (X, y, []), (V, truth, identities))
        self.assertEqual(winner, 0)
        for row, model in zip(rows, models):
            self.assertTrue(row['numpy_converged'])
            self.assertEqual(row['numpy_validation']['macro_f1'], 1.)
            self.assertEqual(row['prediction_agreement'], 1.)
            self.assertEqual(len(row['validation_rows']), 4)
            np.testing.assert_array_equal(model.mean, X.mean(axis=0))
            self.assertAlmostEqual(model.scale[0], X[:, 0].std())
        np.testing.assert_array_equal(X, original[0])
        np.testing.assert_array_equal(V, original[1])


if __name__ == '__main__':
    unittest.main()
