import sys
import unittest
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from evaluate_cantarell import scene_bootstrap
from sar_oil.evaluation import counts


class PhysicalEvaluationTests(unittest.TestCase):
    def rows(self):
        truth = np.zeros((8, 8), bool)
        truth[2:5, 2:5] = True
        return [{'sample': str(i), 'scene': str(i // 2),
                 'counts': {'numpy': counts(truth, truth)}} for i in range(6)]

    def test_same_predictions_have_zero_paired_effect(self):
        output = scene_bootstrap(self.rows(), self.rows(), repeats=100)
        self.assertEqual(output['ci95'], [0., 0.])
        self.assertEqual(output['undefined_draws'], 0)
        self.assertTrue(all(len(draw) == 3 for draw in output['sampled_scenes']))
        self.assertEqual(output, scene_bootstrap(self.rows(), self.rows(), repeats=100))

    def test_unpaired_inputs_rejected(self):
        with self.assertRaises(ValueError):
            scene_bootstrap(self.rows(), self.rows()[:-1])
        changed = self.rows()
        changed[0]['scene'] = 'other'
        with self.assertRaises(ValueError):
            scene_bootstrap(self.rows(), changed)


if __name__ == '__main__':
    unittest.main()
