"""Integration checks: real frozen model, uploads, stale state and export."""
import io
import json
import unittest
import zipfile

import numpy as np
from PIL import Image
from streamlit.testing.v1 import AppTest

from scripts.desktop.demo_engine import SELECTIONS, infer
from scripts.web.streamlit_service import ROOT, assess_bytes, download_zip, examples, infer_bytes


class StreamlitTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sample = examples()[0]
        cls.data = (ROOT / cls.sample['image']).read_bytes()
        cls.truth = (ROOT / cls.sample['mask']).read_bytes()
        cls.selection = next(iter(SELECTIONS.values()))

    def test_adapter_matches_engine_and_zip(self):
        result = infer_bytes(self.data, self.selection)
        original = infer(ROOT / self.sample['image'], self.selection)
        np.testing.assert_array_equal(result['mask'], original['mask'])
        self.assertEqual(result['metadata']['regions'], original['metadata']['regions'])
        mask_before = result['mask'].copy()
        evaluation = assess_bytes(result, self.truth)
        np.testing.assert_array_equal(result['mask'], mask_before)
        with zipfile.ZipFile(io.BytesIO(download_zip(result, evaluation))) as archive:
            self.assertEqual(set(archive.namelist()), {
                'image.png', 'filtered.png', 'candidates.png', 'mask.png', 'overlay.png', 'regions.json'})
            metadata = json.loads(archive.read('regions.json'))
            self.assertFalse(metadata['ground_truth_used_for_inference'])
            self.assertEqual(metadata['post_inference_evaluation'], evaluation)
            np.testing.assert_array_equal(np.asarray(Image.open(io.BytesIO(archive.read('mask.png')))) > 0,
                                          result['mask'])

    def test_invalid_input_and_mismatched_truth(self):
        with self.assertRaises((ValueError, OSError)):
            infer_bytes(b'invalid image', self.selection)
        result = infer_bytes(self.data, self.selection)
        stream = io.BytesIO()
        Image.fromarray(np.zeros((3, 4), dtype='uint8')).save(stream, format='PNG')
        with self.assertRaises(ValueError):
            assess_bytes(result, stream.getvalue())

    def test_ui_sample_and_selection_invalidation(self):
        app = AppTest.from_file(str(ROOT / 'streamlit_app.py'), default_timeout=60).run()
        self.assertFalse(app.exception)
        app.button[0].click().run()
        self.assertFalse(app.exception)
        self.assertFalse(app.error)
        self.assertEqual(len(app.metric), 6)
        self.assertIn('result', app.session_state)
        app.selectbox[0].select(list(SELECTIONS)[1]).run()
        self.assertNotIn('result', app.session_state)
        app.button[0].click().run()
        self.assertFalse(app.exception)
        self.assertFalse(app.error)

    def test_ui_upload_and_navigation(self):
        app = AppTest.from_file(str(ROOT / 'streamlit_app.py'), default_timeout=60).run()
        app.radio[0].set_value('Tải ảnh của bạn').run()
        app.file_uploader[0].upload('sample.png', self.data, 'image/png').run()
        app.file_uploader[1].upload('truth.png', self.truth, 'image/png').run()
        app.button[0].click().run()
        self.assertFalse(app.exception)
        self.assertFalse(app.error)
        self.assertEqual(len(app.metric), 6)
        app.file_uploader[0].clear().run()
        self.assertNotIn('result', app.session_state)
        for page in ['Bằng chứng thực nghiệm', 'Phạm vi và hướng dẫn']:
            app.sidebar.radio[0].set_value(page).run()
            self.assertFalse(app.exception)


if __name__ == '__main__':
    unittest.main()
