import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from download_dartis import cooldown_seconds


class DownloadBackoffTests(unittest.TestCase):
    def test_retry_after_seconds_and_http_date(self):
        self.assertEqual(cooldown_seconds('120',0),120)
        self.assertEqual(cooldown_seconds('Thu, 01 Jan 1970 00:02:00 GMT',0),120)
        self.assertEqual(cooldown_seconds('0',0),60)

    def test_missing_or_malformed_header_has_conservative_default(self):
        self.assertEqual(cooldown_seconds(None,0),900)
        self.assertEqual(cooldown_seconds('not a date',0),900)


if __name__=='__main__': unittest.main()
