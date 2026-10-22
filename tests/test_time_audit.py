import contextlib
import datetime as dt
import io
import unittest
from time_rules import calendar_birth_time, clock_coordinates, shichen_start
from webui import app

SAMPLE = {'gender': '男', 'birth_date': '1984-08-15', 'birth_time': '12:00',
          'query_date': '2025-04-20', 'query_time': '10:00'}


class TimeAudit(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_every_clock_minute_maps_to_one_of_eight_quarters(self):
        for hour in range(24):
            for minute in range(60):
                civil = dt.datetime(2000, 1, 2, hour, minute)
                coordinates = clock_coordinates(civil)
                self.assertIn(coordinates['quarter'], range(1, 9))
                self.assertEqual(int((civil-shichen_start(civil)).total_seconds()/60),
                                 coordinates['minute_in_shichen'])
        self.assertEqual(clock_coordinates(dt.datetime(2000, 1, 2, 23, 0))['quarter'], 1)
        self.assertEqual(clock_coordinates(dt.datetime(2000, 1, 3, 0, 0))['quarter'], 5)
        self.assertEqual(calendar_birth_time(dt.datetime(2000, 1, 2, 23, 5)),
                         dt.datetime(2000, 1, 3, 0, 5))

    def test_late_zi_keeps_clock_quarter_separate_from_calendar_date(self):
        with contextlib.redirect_stdout(io.StringIO()):
            late = self.client.post('/api/v1/legacy/chart', json={**SAMPLE, 'birth_time': '23:05'}).json['data']
            early = self.client.post('/api/v1/legacy/chart', json={**SAMPLE, 'birth_date': '1984-08-16', 'birth_time': '00:05'}).json['data']
        self.assertEqual(late['birth_info']['date_str'], early['birth_info']['date_str'])
        self.assertEqual(late['result']['keke']['k_initial'], 1)
        self.assertEqual(early['result']['keke']['k_initial'], 5)
        self.assertEqual(late['time_basis']['quarter'], 1)

    def test_full_shichen_spans_midnight_with_eight_distinct_clock_quarters(self):
        with contextlib.redirect_stdout(io.StringIO()):
            response = self.client.post('/api/v1/legacy/time-audit', json={**SAMPLE, 'birth_time': '00:05'})
        self.assertEqual(response.status_code, 200, response.json)
        data = response.json['data']
        self.assertEqual(data['window_start'], '1984-08-14 23:00')
        self.assertEqual(data['window_end_exclusive'], '1984-08-15 01:00')
        self.assertEqual([row['k_initial'] for row in data['samples']], list(range(1, 9)))
        self.assertEqual(len(data['samples']), 8)
        self.assertFalse(data['supports_minute_inference'])

    def test_minute_audit_measures_actual_invariance(self):
        with contextlib.redirect_stdout(io.StringIO()):
            response = self.client.post('/api/v1/legacy/time-audit', json={**SAMPLE, 'resolution_minutes': 1})
        self.assertEqual(response.status_code, 200, response.json)
        data = response.json['data']
        self.assertEqual(data['summary']['sample_count'], 120)
        self.assertEqual(data['summary']['initial_quarters'], list(range(1, 9)))
        self.assertEqual(data['summary']['unique_main_numbers'], [349])
        self.assertEqual(data['summary']['unique_destiny_article_sets'], 1)
        self.assertEqual(data['summary']['unique_annual_article_sets'], 1)

    def test_invalid_interval_and_future_samples_are_rejected(self):
        for interval in (True, '1', 0, 5, 120):
            response = self.client.post('/api/v1/legacy/time-audit', json={**SAMPLE, 'resolution_minutes': interval})
            self.assertEqual(response.status_code, 400)
            self.assertEqual(response.json['error']['code'], 'INVALID_INPUT')
        response = self.client.post('/api/v1/legacy/time-audit', json={**SAMPLE,
            'query_date': '1984-08-15', 'query_time': '12:00'})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json['error']['code'], 'INVALID_DATETIME')


if __name__ == '__main__':
    unittest.main()
