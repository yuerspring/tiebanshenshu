"""Fixtures transcribed from the supplied PDF; dates are not calendar fixtures.

The PDF gives lunar dates and a query sexagenary hour without a Gregorian query
 date. Supply those declared pillars directly so calendar conversion is not
 silently substituted for the source example.
"""
import contextlib
import datetime as dt
import io
import unittest
from unittest.mock import patch
from main import convert_to_bazi_info
from webui import app, init_calculator


class SuppliedBookExamples(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with contextlib.redirect_stdout(io.StringIO()):
            cls.calc = init_calculator()

    def example_two(self):
        birth = convert_to_bazi_info(dt.datetime(1924, 6, 16, 16))
        query = convert_to_bazi_info(dt.datetime(2025, 4, 20, 10))
        birth.update(lunar_month=5, lunar_day=15, is_leap=False,
                     bazi={'year':'甲子','month':'庚午','day':'乙丑','time':'甲申'})
        query['bazi']['time'] = '己巳'
        return {'gender':'男', 'birth_info':birth, 'query_info':query}

    def test_pdf_pages_60_61_basic_table_matrices(self):
        tables = self.calc.db.tables
        self.assertEqual(tables['14-1'], {str(n):n for n in range(1,13)})
        self.assertEqual(tables['14-2'], dict(zip('子丑寅卯辰巳午未申酉戌亥', range(1,13))))
        self.assertEqual(tables['14-4'], dict(zip('宫商角徵羽', [5,4,3,2,1])))
        self.assertEqual(tables['14-6'], dict(zip('水火木金土', range(1,6))))
        tones = ['羽徵宫角商','徵宫角商羽','角商羽徵宫',
                 '宫角商羽徵','商羽徵宫角','徵宫角商羽']
        groups = ['甲己','乙庚','丙辛','丁壬','戊癸']
        for number in range(1,13):
            for group, tone in zip(groups, tones[(number-1)//2]):
                self.assertEqual(tables['14-3'][number][group], tone)
        for element, expected in zip('水火木金土',
                                     [[1,2,3,4,5],[2,3,4,5,1],[3,4,5,1,2],
                                      [4,5,1,2,3],[5,1,2,3,4]]):
            for group, value in zip(groups, expected):
                for stem in group:
                    self.assertEqual(tables['14-5'][element][stem], value)

    def test_pdf_pages_30_32_full_example_two_destiny(self):
        result = self.calc.calculate(self.example_two())
        self.assertEqual([result[k] for k in ('cong_num','tone_num','moment_cn','main_num','hex_name','pn_num')],
                         [11, 2, '初刻', 345, '泰', 4])
        table = result['tbl_data']
        numbers = [table['base'] + table['seq'] + n
                   for offsets in table['offsets'].values() for n in offsets]
        self.assertEqual(numbers, [9760, 1353, 10606, 1559])

    def test_pdf_pages_37_39_first_sixteen_original_annual_numbers(self):
        annual = self.calc.calculate(self.example_two())['liunian']
        self.assertEqual([r['original_fortune'] for r in annual[:16]],
                         list(map(str, [2408,8151,3188,8992,2919,5625,6226,8874,
                                        8952,7754,1082,5641,2239,4116,1614,7012])))
        self.assertEqual(annual[2]['letter'], '福')
        self.assertFalse(annual[2]['correction_applied'])
        self.assertEqual(annual[2]['correction_status'], 'unverified_candidate')

    def test_pdf_pages_15_16_formula_and_both_moment_lookups(self):
        payload = self.example_two()
        payload['birth_info'].update(lunar_day=9)
        # 火日遇庚：3；土时：5。甲年男命为初刻；同例女命为正刻。
        payload['birth_info']['bazi']['day'] = '甲戌'
        payload['query_info']['bazi']['time'] = '庚午'
        for gender, moment, hexagram in [('男','初刻','坤'), ('女','正刻','乾')]:
            payload['gender'] = gender
            result = self.calc.calculate(payload)
            self.assertEqual(result['main_num'], 369)
            self.assertEqual(result['moment_cn'], moment)
            self.assertEqual(result['hex_name'], hexagram)

    def test_missing_required_tone_table_is_not_replaced_with_gong(self):
        tables = dict(self.calc.db.tables)
        tables['14-3'] = {}
        with patch.object(self.calc.db, 'tables', tables):
            with self.assertRaises(KeyError):
                self.calc.calculate(self.example_two())

    def test_api_explains_two_moments_without_claiming_minute_precision(self):
        response = app.test_client().post('/api/v1/legacy/chart', json={
            'gender':'男','birth_date':'1984-08-15','birth_time':'12:01',
            'query_date':'2025-04-20','query_time':'10:00'})
        self.assertEqual(response.status_code, 200)
        basis = response.json['data']['method_basis']
        self.assertFalse(basis['birth_minute_used_in_main_formula'])
        self.assertFalse(basis['kin_candidates_applied_to_main_formula'])
        self.assertEqual(basis['verification_scope'], 'selected_rules_and_examples')


if __name__ == '__main__':
    unittest.main()
