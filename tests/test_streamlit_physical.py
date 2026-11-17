"""Real-data physical UI integration, enabled after independent test verification."""
import io
import json
import unittest
import zipfile
from unittest.mock import patch

import numpy as np
from PIL import Image
from streamlit.testing.v1 import AppTest

from scripts import streamlit_physical as physical
from scripts.streamlit_service import download_zip


class PhysicalWebTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not physical.ready():
            raise unittest.SkipTest('Physical evaluation and independent verification not complete yet')
        cls.sample = physical.samples()[0]
        cls.read_fields = []
        original = np.load

        class ObservedArchive:
            def __init__(self, *args, **kwargs):
                self.archive = original(*args, **kwargs)

            def __enter__(self):
                return self

            def __exit__(self, *args):
                self.archive.close()

            def __getitem__(self, key):
                cls.read_fields.append(key)
                return self.archive[key]

        with patch.object(physical.np, 'load', ObservedArchive):
            cls.result = physical.run_sample(cls.sample['sample'])

    def test_real_inference_does_not_read_truth(self):
        self.assertEqual(set(self.read_fields), {'gamma0', 'incidence_degrees'})
        self.assertEqual(self.result['metadata']['role'], 'filtered_adaptive')
        self.assertNotEqual(self.result['metadata']['config']['filter']['name'], 'none')
        self.assertEqual(self.result['metadata']['config']['threshold']['name'], 'niblack')

    def test_evaluation_and_export_match_frozen_outputs(self):
        actual = physical.assess_sample(self.result)
        evaluation = json.loads((physical.ROOT/'results/cantarell/evaluation.json').read_text())
        row = next(r for r in evaluation['roles']['filtered_adaptive']['per_image'] if r['sample']==self.sample['sample'])
        from sar_oil.evaluation import summarize
        self.assertEqual(actual['metrics'], summarize([row['counts']['numpy']]))
        with zipfile.ZipFile(io.BytesIO(download_zip(self.result, actual))) as archive:
            prediction = np.asarray(Image.open(io.BytesIO(archive.read('mask.png'))))>0
            np.testing.assert_array_equal(prediction, self.result['mask'])
            metadata = json.loads(archive.read('regions.json'))
            self.assertEqual(metadata['post_inference_evaluation'], actual)

    def test_ui_physical_result_and_sample_invalidation(self):
        app = AppTest.from_file(str(physical.ROOT/'streamlit_app.py'), default_timeout=60).run()
        app.sidebar.radio[0].set_value('Sentinel-1 vật lý').run()
        self.assertFalse(app.exception)
        with patch.object(physical, 'run_sample', return_value=self.result):
            app.button[0].click().run()
        self.assertFalse(app.exception)
        self.assertFalse(app.error)
        self.assertEqual(len(app.metric),3)
        self.assertIn('physical_result',app.session_state)
        app.selectbox[0].select(physical.samples()[1]).run()
        self.assertNotIn('physical_result',app.session_state)


if __name__=='__main__':
    unittest.main()
