import sys
from pathlib import Path
import unittest
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from scripts.qposd.qposd_labels import decode_mask


class QposdLabelTests(unittest.TestCase):
    def test_publisher_colors_and_observed_unknowns(self):
        rgb = np.array([[(0, 0, 255), (255, 0, 0), (0, 255, 0), (0, 0, 0),
                         (12, 255, 14), (198, 118, 255)]], dtype=np.uint8)
        np.testing.assert_array_equal(decode_mask(rgb), [[0, 1, 2, 3, 255, 255]])

    def test_scaled_or_grayscale_masks_rejected(self):
        for image in (np.zeros((2, 2), dtype=np.uint8), np.zeros((2, 2, 3))):
            with self.assertRaises(ValueError):
                decode_mask(image)


if __name__ == '__main__':
    unittest.main()
