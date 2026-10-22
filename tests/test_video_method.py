import contextlib
import io
import unittest
from tiebanshenshu.methods.video import VideoMethodCalculator
from webui import app, init_calculator

EXAMPLE = dict(year='乙巳',month='辛巳',day='甲申',time='丙子')


class VideoMethodTests(unittest.TestCase):
    def setUp(self):
        self.calc=VideoMethodCalculator()

    def test_video_04_50_and_09_40_example(self):
        r=self.calc.calculate(EXAMPLE)['preliminary']
        self.assertEqual((r['sum'],r['hour_divisor'],r['remainder'],r['initial_ke_candidate']), (55,1,0,1))
        self.assertEqual(r['base_number'],9467)
        self.assertIsNone(r['true_ke'])
        self.assertEqual([c['multiplier'] for c in r['secret_candidates']],[0,1,2,4,6,8,10,12,14])
        self.assertFalse(r['secret_candidates'][-1]['in_corpus'])

    def test_plus_six_is_constant_not_mutual_upper(self):
        b=dict(EXAMPLE,year='甲子',month='甲子')
        self.assertEqual(self.calc.calculate(b)['preliminary']['base_number']//1000,8)

    def test_20_55_22_20_and_23_20_source_examples(self):
        rows=self.calc.calculate(EXAMPLE)['pillar_articles']
        self.assertEqual([r['jiaze']['number'] for r in rows[:2]],[2381,4381])
        self.assertEqual([r['stem_branch_sum_number'] for r in rows[:2]],[3345,3945])
        self.assertEqual(rows[0]['jiaze']['line_values_top_down'],[30,60,90,30,120,60])
        self.assertEqual(len(rows),4)

    def test_four_stem_encoding_and_branch_fallback(self):
        self.assertEqual(self.calc.encode_stems('辛甲丙乙'),9126)
        self.assertEqual(self.calc.encode_stems('辛月月戊'),9003)
        self.assertEqual(self.calc.encode_stems('辛乙壬壬'),9655)
        r=self.calc.number_method(EXAMPLE,5003)
        self.assertEqual((r['status'],r['number']),('four_stem_fallback',9126))

    def test_25_50_number_to_gua_and_no_default(self):
        r=self.calc.number_method(EXAMPLE,9003)
        self.assertEqual((r['upper'],r['lower']),('坎','震'))
        self.assertEqual(r['number'],1387) # 依公开加则规则派生，不冒充口述假设的3456。
        missing=self.calc.calculate(EXAMPLE)
        self.assertEqual(missing['number_method']['status'],'requires_confirmed_number')
        self.assertEqual(missing['before_after']['before']['articles'],[])
        self.assertEqual(missing['before_after']['after']['status'],'requires_houtian_conversion_rule')

    def test_before_series_uses_linear_96_and_separate_benming_input(self):
        r=self.calc.calculate(EXAMPLE,benming_gua_number=2000)['before_after']['before']
        self.assertEqual(r['combination'],3467)
        self.assertEqual([a['number'] for a in r['articles']],[5563,5659,5755,5851])

    def test_after_gua_series_decreases_instead_of_reusing_before_gua(self):
        r=self.calc.series_for_gua('乾','乾',2000,use_xian_tian=False)
        self.assertEqual(r['combination'],6666)
        self.assertEqual([a['number'] for a in r['articles']],[8570,8474,8378,8282])

    def test_31_10_untransformed_annual_example(self):
        r=self.calc.annual_example(EXAMPLE,'壬午')
        self.assertEqual((r['base'],r['stem_add'],r['branch_add'],r['number']), (6464,3,[2,7],6476))
        self.assertEqual(r['status'],'untransformed_branch_only')

    def test_invalid_inputs_and_unresolved_pair_boundary(self):
        for b in [None,{},dict(EXAMPLE,year='甲'),dict(EXAMPLE,time=['丙','子'])]:
            with self.assertRaises(ValueError):self.calc.calculate(b)
        for n in [True,0,9003.0,'9003',13000]:
            with self.assertRaises(ValueError):self.calc.number_method(EXAMPLE,n)
        self.assertEqual(self.calc.number_method(EXAMPLE,9901)['status'],'unresolved_pair_boundary')
        self.assertTrue(self.calc.article(13000)['in_corpus'])
        self.assertFalse(self.calc.article(1000)['in_corpus'])


class VideoApiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with contextlib.redirect_stdout(io.StringIO()):init_calculator()
        cls.client=app.test_client()

    def test_video_case_and_corpus_conflict_are_visible(self):
        response=self.client.post('/api/v1/video-chart',json={'bazi':EXAMPLE,'fortune_pillar':'壬午'})
        self.assertEqual(response.status_code,200)
        r=response.json['data']
        self.assertEqual(r['preliminary']['base_number'],9467)
        self.assertEqual(r['edition_conflicts'][0]['corpus_sentence'],'己酉之年，宴饮鹰扬。')
        self.assertEqual(r['annual']['number'],6476)
        self.assertEqual(len(r['pillar_articles']),4)

    def test_number_requires_explicit_fact_confirmation(self):
        p={'bazi':EXAMPLE,'confirmed_number':9003}
        self.assertEqual(self.client.post('/api/v1/video-chart',json=p).status_code,400)
        self.assertEqual(self.client.post('/api/v1/video-chart',json={**p,'number_confirmed':True}).status_code,200)

    def test_both_routes_render_and_dates_convert_without_claiming_video_calendar(self):
        self.assertIn('视频演算'.encode(),self.client.get('/').data)
        self.assertIn('V2'.encode(),self.client.get('/legacy').data)
        r=self.client.post('/api/v1/video-chart',json={'birth_date':'1991-03-02','birth_time':'08:15'})
        self.assertEqual(r.status_code,200)
        self.assertEqual(r.json['data']['input_basis'],'legacy_calendar_conversion_not_video_verified')

    def test_bad_optional_fields_return_json_errors(self):
        for field,value in [('fortune_pillar',[]),('benming_gua_number',True),('confirmed_number',{}),('bazi',[] )]:
            p={'bazi':EXAMPLE,field:value,'number_confirmed':True}
            r=self.client.post('/api/v1/video-chart',json=p)
            self.assertEqual(r.status_code,400,r.json)
            self.assertEqual(r.json['error']['code'],'INVALID_INPUT')


if __name__=='__main__':unittest.main()
