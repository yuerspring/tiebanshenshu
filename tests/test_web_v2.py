import contextlib
import datetime as dt
import io
import json
import unittest
from main import convert_to_bazi_info
from webui import app, init_calculator
from reference_adapter import reference_calculator


class WebParity(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with contextlib.redirect_stdout(io.StringIO()):
            cls.calc = init_calculator()
        cls.client = app.test_client()

    def check_chart(self, gender, birth, query, known=None):
        bd, bt = birth.split(' ')
        qd, qt = query.split(' ')
        payload = dict(gender=gender, birth_date=bd, birth_time=bt, query_date=qd, query_time=qt, known_shengxiao=known or {})
        response = self.client.post('/api/v1/chart', json=payload)
        self.assertEqual(response.status_code, 200, response.json)
        actual = response.json['data']
        b = dt.datetime.strptime(birth, '%Y-%m-%d %H:%M')
        if b.hour >= 23:
            b = (b + dt.timedelta(days=1)).replace(hour=0)
        ordered_known = {key: known[key] for key in actual['validation']['provided_relations']} if known else None
        direct = self.calc.calculate(dict(gender=gender, birth_info=convert_to_bazi_info(b), query_info=convert_to_bazi_info(dt.datetime.strptime(query, '%Y-%m-%d %H:%M')), **({'known_shengxiao': ordered_known} if known else {})))
        self.assertEqual(actual['result'], json.loads(json.dumps(direct, ensure_ascii=False, default=str)))
        for key in ('cong_num', 'tone_num', 'main_num', 'hex_name', 'moment_cn', 'pn_num'):
            self.assertEqual(actual['result'][key], direct[key], key)
        self.assertEqual(actual['result']['liunian'], direct['liunian'])
        self.assertEqual(len(actual['result']['liunian']), 108)
        self.assertEqual(actual['result']['keke']['xinyi_brother_count']['gua_name'], direct['keke']['xinyi_brother_count']['gua_name'])
        return actual

    def test_readme_example(self):
        actual = self.check_chart('男', '1924-06-15 16:00', '2025-04-20 10:00')
        self.assertEqual([actual['result'][k] for k in ('cong_num','tone_num','main_num','hex_name')], [11,2,344,'泰'])
        self.assertEqual([x['number'] for x in actual['destiny_articles']], [9760,1353,10606,1559])

    def test_another_normal_datetime(self):
        self.check_chart('男', '1991-03-02 08:15', '2025-04-20 10:00')

    def test_female_and_late_zi(self):
        actual = self.check_chart('女', '1990-01-01 23:35', '2025-04-20 10:00', {'母亲':'鼠'})
        self.assertEqual(actual['birth_info']['date_str'], '1990-01-02 00:35')
        self.assertIn('kao_ke_info', actual['result']['keke'])

    def test_zodiac_check_does_not_change_birth_destiny(self):
        plain = self.check_chart('男', '1991-03-02 08:15', '2025-04-20 10:00')
        checked = self.check_chart('男', '1991-03-02 08:15', '2025-04-20 10:00', {'父亲': '鼠', '兄弟': '虎'})
        self.assertEqual(plain['destiny_articles'], checked['destiny_articles'])
        self.assertEqual(set(checked['validation']['provided_relations']), {'父亲', '兄弟'})
        self.assertEqual(checked['validation']['used_relation'], checked['validation']['provided_relations'][0])
        self.assertFalse(checked['validation']['birth_destiny_affected_by_zodiac'])

    def test_validation(self):
        response=self.client.post('/api/v1/chart',json={'gender':'男','birth_date':'2030-01-01','birth_time':'12:00','query_date':'2025-01-01','query_time':'12:00'})
        self.assertEqual(response.status_code,400)
        self.assertEqual(response.json['error']['code'],'INVALID_DATETIME')
        self.assertTrue(self.client.get('/api/v1/health').json['database_loaded'])

    def test_hour_sensitivity_runs_original_calculator_for_each_quarter(self):
        sample = {'gender': '男', 'birth_date': '1991-03-02', 'birth_time': '08:30',
                  'query_date': '2025-04-20', 'query_time': '10:00'}
        response = self.client.post('/api/v1/time-sensitivity', json=sample)
        self.assertEqual(response.status_code, 200, response.json)
        comparison = response.json['data']
        self.assertEqual(comparison['minimum_time_resolution_minutes'], 15)
        self.assertEqual([c['time_range'] for c in comparison['candidates']],
                         ['08:00–08:14', '08:15–08:29', '08:30–08:44', '08:45–08:59'])
        for minute, row in zip((0, 15, 30, 45), comparison['candidates']):
            sample['birth_time'] = f'08:{minute:02d}'
            chart = self.client.post('/api/v1/chart', json=sample).json['data']
            self.assertEqual(row['main_num'], chart['result']['main_num'])
            self.assertEqual(row['brother_articles'], [a for a in chart['destiny_articles'] if '兄弟' in a['topic']])
            self.assertEqual(row['k_initial'], chart['result']['keke']['k_initial'])
        self.assertTrue(comparison['brother_articles_unchanged'])

    def test_hour_sensitivity_rejects_invalid_birth(self):
        response = self.client.post('/api/v1/time-sensitivity', json={
            'gender': '男', 'birth_date': '2030-01-01', 'birth_time': '12:30',
            'query_date': '2025-01-01', 'query_time': '12:00'})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json['error']['code'], 'INVALID_DATETIME')

    def test_os_reference_is_original_calculator_with_its_own_database(self):
        sample = {'gender': '男', 'birth_date': '1991-03-02', 'birth_time': '08:30',
                  'query_date': '2025-04-20', 'query_time': '10:00'}
        with contextlib.redirect_stdout(io.StringIO()):
            response = self.client.post('/api/v1/compare-os', json=sample)
        self.assertEqual(response.status_code, 200, response.json)
        comparison = response.json['data']
        source, calc = reference_calculator()
        raw = calc.calculate({'gender': '男',
                              'birth_info': source.convert_to_bazi_info(dt.datetime(1991, 3, 2, 8, 30)),
                              'query_info': source.convert_to_bazi_info(dt.datetime(2025, 4, 20, 10))})
        self.assertEqual(comparison['reference']['original_result'],
                         json.loads(json.dumps(raw, ensure_ascii=False, default=str)))
        self.assertEqual(comparison['reference']['final_fortune_num'],
                         raw['main_num'] + raw['ke_gan_num'] * 48)
        self.assertEqual(len(comparison['reference']['annual_fortunes']), 108)
        self.assertEqual(source.get_eight_ke_from_time(dt.datetime(1991, 3, 2, 5, 30)), '六刻')
        self.assertEqual(self.client.post('/api/v1/compare-os', json={
            **sample, 'birth_date': '2030-01-01'}).status_code, 400)


if __name__ == '__main__':
    unittest.main()
