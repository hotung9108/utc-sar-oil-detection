"""User-facing regression checks: invalid inputs and honest interpretation."""
import unittest

from streamlit.testing.v1 import AppTest

from scripts.streamlit_service import ROOT


class UserExperienceTests(unittest.TestCase):
    def test_invalid_upload_is_explained_and_cannot_run(self):
        app = AppTest.from_file(str(ROOT/'streamlit_app.py'), default_timeout=60).run()
        app.radio[0].set_value('Tải ảnh của bạn').run()
        app.file_uploader[0].upload('broken.png', b'not an image', 'image/png').run()
        self.assertFalse(app.exception)
        self.assertTrue(app.button[0].disabled)
        self.assertTrue(any('Không đọc được ảnh' in error.value for error in app.error))
        self.assertNotIn('result', app.session_state)

    def test_result_has_interpretation_and_truth_comparison(self):
        app = AppTest.from_file(str(ROOT/'streamlit_app.py'), default_timeout=60).run()
        app.button[0].click().run()
        self.assertFalse(app.exception)
        self.assertFalse(app.error)
        self.assertTrue(any('Phát hiện đúng:' in item.value for item in app.markdown))
        self.assertTrue(any('không phải đếm pixel màu' in item.value for item in app.caption))
        self.assertTrue(any('Mô hình' in item.value for item in app.info))
        self.assertFalse(app.session_state['result']['metadata']['ground_truth_used_for_inference'])


if __name__ == '__main__':
    unittest.main()
