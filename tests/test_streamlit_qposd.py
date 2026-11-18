import io
import json
import unittest
import zipfile
from unittest.mock import patch

import numpy as np
from PIL import Image
from streamlit.testing.v1 import AppTest

from scripts.web import streamlit_qposd as qposd


class QposdWebTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.number = qposd.samples()[0]
        cls.result = qposd.run_sample(cls.number)

    def test_real_inference_matches_frozen_test_and_export(self):
        evaluation = qposd.assess_sample(self.result)
        saved = json.loads((qposd.ROOT / 'results/qposd/evaluation.json').read_text())
        row = next(r for r in saved['images'] if r['number'] == self.number)
        self.assertEqual(evaluation['metrics'], row['numpy'])
        self.assertFalse(self.result['metadata']['ground_truth_used_for_inference'])
        with zipfile.ZipFile(io.BytesIO(qposd.export_zip(self.result, evaluation))) as archive:
            classes = np.asarray(Image.open(io.BytesIO(archive.read('classes.png'))))
            np.testing.assert_array_equal(classes, self.result['prediction'])
            self.assertTrue(set(np.unique(classes)).issubset({0, 1, 2}))

    def test_page_renders_result_and_clears_on_sample_change(self):
        app = AppTest.from_file(str(qposd.ROOT / 'streamlit_app.py'), default_timeout=60).run()
        app.sidebar.radio[0].set_value('Dầu và look-alike').run()
        self.assertFalse(app.exception)
        with patch.object(qposd, 'run_sample', return_value=self.result):
            app.button[0].click().run()
        self.assertFalse(app.exception)
        self.assertFalse(app.error)
        self.assertIn('qposd_result', app.session_state)
        app.selectbox[0].select(qposd.samples()[1]).run()
        self.assertNotIn('qposd_result', app.session_state)


if __name__ == '__main__':
    unittest.main()
