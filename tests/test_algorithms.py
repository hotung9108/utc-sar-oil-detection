import sys
import unittest
import tempfile
from unittest.mock import patch
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import numpy as np

from sar_oil.evaluation import counts, region_counts, region_geometry
from sar_oil.reference import label
from sar_oil.verification import verify


class AlgorithmTests(unittest.TestCase):
    def test_reference_equivalence_and_edge_cases(self):
        # Verification writes a result file; tests must not alter frozen evidence.
        with tempfile.TemporaryDirectory() as directory:
            with patch('sar_oil.verification.OUT', Path(directory)):
                result = verify()
        self.assertTrue(result["passed"], [c for c in result["checks"] if not c["passed"]])

    def test_cached_region_metrics_equal_pixel_matching(self):
        rng = np.random.default_rng(14)
        for _ in range(12):
            labels = label(rng.random((40, 40)) > 0.85)
            truth = rng.random((40, 40)) > 0.8
            keep = rng.random(int(labels.max())) > 0.5
            prediction = np.r_[False, keep][labels]
            self.assertEqual(
                counts(prediction, truth), region_counts(region_geometry(labels, truth), keep)
            )
