import contextlib
import io
import unittest
from unittest.mock import patch
from webui import compute_chart, init_calculator


class HexagramProvenance(unittest.TestCase):
    def test_missing_specific_entry_does_not_borrow_legacy_fallback(self):
        sample = {'gender': '男', 'birth_date': '1924-06-15', 'birth_time': '16:00',
                  'query_date': '2025-04-20', 'query_time': '10:00'}
        with contextlib.redirect_stdout(io.StringIO()):
            calculator = init_calculator()
            self.assertIn(344, calculator.db.HEXAGRAM_MAP)
            entries = dict(calculator.db.HEXAGRAM_DETAIL_MAP)
            entries.pop(('初刻', 344))
            with patch.object(calculator.db, 'HEXAGRAM_DETAIL_MAP', entries):
                chart = compute_chart(sample)
        result = chart['result']
        self.assertFalse(result['hexagram_source']['found'])
        self.assertFalse(result['hexagram_source']['fallback_used'])
        self.assertEqual(result['data_warnings'][0]['code'], 'MISSING_HEXAGRAM_ENTRY')
        self.assertIn('344', result['data_warnings'][0]['message'])
        self.assertEqual(chart['destiny_articles'], [])


if __name__ == '__main__':
    unittest.main()
