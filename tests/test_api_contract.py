"""Regression coverage for untrusted requests at the web boundary."""
import io
import json
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from webui import app


ENDPOINTS = ('/api/v1/legacy/chart', '/api/legacy/calculate',
             '/api/v1/legacy/time-sensitivity', '/api/v1/legacy/compare-os', '/api/v1/legacy/time-audit')
SAMPLE = {'gender': '男', 'birth_date': '1991-03-02', 'birth_time': '08:30',
          'query_date': '2025-04-20', 'query_time': '10:00'}


class ApiContract(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def assert_error(self, response, status, code):
        self.assertEqual(response.status_code, status, response.data)
        self.assertTrue(response.is_json)
        self.assertFalse(response.json['success'])
        self.assertEqual(response.json['error']['code'], code)
        self.assertEqual(response.headers['Cache-Control'], 'no-store')

    def test_zodiac_types_are_rejected_without_server_errors(self):
        invalid = (None, [], False, 0, '', {'父亲': []}, {'父亲': {}},
                   {'父亲': None}, {'父亲': 1}, {'父亲': '猫'}, {'未知': '鼠'})
        with patch('webui.init_calculator') as engine:
            for path in ENDPOINTS:
                for known in invalid:
                    with self.subTest(path=path, known=known):
                        self.assert_error(self.client.post(
                            path, json={**SAMPLE, 'known_shengxiao': known}),
                            400, 'INVALID_INPUT')
            engine.assert_not_called()

    def test_non_object_and_malformed_json_are_rejected(self):
        for path in ENDPOINTS:
            for body in ('null', '[]', 'true', '1', '{', '"hello"'):
                with self.subTest(path=path, body=body):
                    self.assert_error(self.client.post(
                        path, data=body, content_type='application/json'),
                        400, 'INVALID_INPUT')
            self.assert_error(self.client.post(path, data='gender=男'),
                              400, 'INVALID_INPUT')

    def test_datetime_validation_precedes_calculation(self):
        changes = ({'birth_time': '8:30'}, {'birth_time': '24:00'},
                   {'birth_date': '2025-02-30'}, {'birth_date': '1991-3-02'},
                   {'query_time': None}, {'birth_date': '2030-01-01'},
                   {'birth_time': '08:50', 'query_date': '1991-03-02',
                    'query_time': '08:40'})
        with patch('webui.init_calculator') as engine:
            for path in ENDPOINTS:
                for change in changes:
                    with self.subTest(path=path, change=change):
                        self.assert_error(self.client.post(path, json={**SAMPLE, **change}),
                                          400, 'INVALID_DATETIME')
                missing = dict(SAMPLE)
                del missing['birth_date']
                self.assert_error(self.client.post(path, json=missing),
                                  400, 'INVALID_DATETIME')
            engine.assert_not_called()

    def test_request_limit_with_and_without_content_length(self):
        body = json.dumps({**SAMPLE, 'padding': 'x' * 4096}).encode()
        for path in ENDPOINTS:
            with self.subTest(path=path):
                self.assert_error(self.client.post(path, data=body,
                                  content_type='application/json'), 413, 'INVALID_INPUT')
                # Simulate a server-terminated/chunked stream with no Content-Length.
                response = self.client.open(path, method='POST', environ_overrides={
                    'wsgi.input': io.BytesIO(body), 'wsgi.input_terminated': True,
                    'CONTENT_LENGTH': '', 'CONTENT_TYPE': 'application/json',
                })
                # Werkzeug may return a bounded, truncated body to the JSON
                # parser when Content-Length is absent. Both outcomes reject it.
                self.assertIn(response.status_code, (400, 413))
                self.assert_error(response, response.status_code, 'INVALID_INPUT')

    def test_health_is_unavailable_when_database_is_empty(self):
        with patch('tiebanshenshu.methods.video_corpus.load_comparison_verses', return_value={}):
            response = self.client.get('/api/v1/health')
        self.assertEqual(response.status_code, 503)
        self.assertFalse(response.json['success'])
        self.assertFalse(response.json['database_loaded'])

    def test_health_hides_initialization_errors(self):
        with patch('tiebanshenshu.methods.video_corpus.load_comparison_verses', side_effect=RuntimeError('internal details')):
            with self.assertLogs('webui', level='ERROR'):
                response = self.client.get('/api/v1/health')
        self.assertEqual(response.status_code, 503)
        self.assertNotIn('internal details', response.get_data(as_text=True))

    def test_successful_chart_response_is_not_cached(self):
        with patch('webui.compute_chart', return_value={'result': 'example'}):
            response = self.client.post('/api/v1/legacy/chart', json=SAMPLE)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json['success'])
        self.assertEqual(response.headers['Cache-Control'], 'no-store')
        self.assertEqual(response.headers['X-Content-Type-Options'], 'nosniff')


if __name__ == '__main__':
    unittest.main()
