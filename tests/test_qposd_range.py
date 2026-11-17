"""A server ignoring Range must never trigger a multi-GB archive read."""
import sys
from pathlib import Path
import unittest
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from scripts.qposd.audit_qposd import RangeReader


class RangeReaderTests(unittest.TestCase):
    def response(self, status, content_range, data):
        response = MagicMock()
        response.__enter__.return_value = response
        response.status = status
        response.headers = {'Content-Range': content_range}
        response.read.return_value = data
        return response

    def test_full_response_rejected_before_read(self):
        response = self.response(200, None, b'')
        with patch('scripts.qposd.audit_qposd.urllib.request.urlopen', return_value=response):
            with self.assertRaises(ValueError):
                RangeReader('https://example.org/data', 100).read(4)
        response.read.assert_not_called()

    def test_seek_and_exact_range(self):
        response = self.response(206, 'bytes 96-99/100', b'abcd')
        stream = RangeReader('https://example.org/data', 100)
        stream.seek(-4, 2)
        with patch('scripts.qposd.audit_qposd.urllib.request.urlopen', return_value=response):
            self.assertEqual(stream.read(), b'abcd')
        self.assertEqual(stream.tell(), 100)
        self.assertEqual(stream.transferred, 4)
        self.assertEqual(stream.read(1), b'')

    def test_budget_rejected_before_request(self):
        with patch('scripts.qposd.audit_qposd.urllib.request.urlopen') as request:
            with self.assertRaises(ValueError):
                RangeReader('https://example.org/data', 100, budget=3).read(4)
        request.assert_not_called()


if __name__ == '__main__':
    unittest.main()
