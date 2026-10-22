import unittest
from unittest.mock import patch
from tiebanshenshu.methods.video import VideoMethodCalculator
from webui import app

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
        self.assertEqual(missing['number_method']['status'],'requires_basis_number')
        self.assertEqual(missing['before_after']['before']['articles'],[])
        self.assertEqual(missing['before_after']['after']['status'],'requires_benming_gua_number')

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

    def test_video_case_runs_without_matching_corpus_or_fact_confirmation(self):
        result=self.calc.calculate(EXAMPLE,basis_number=9003,fortune_pillar='壬午')
        self.assertEqual(result['number_method']['pair_sums'],[9,3])
        self.assertEqual(result['number_method']['number'],1387)
        self.assertFalse(result['number_method']['input_fact_verified'])
        self.assertEqual(result['life_sequence']['articles'][1]['number'],1483)
        before=result['before_after']['before'];after=result['before_after']['after']
        self.assertEqual((before['combination'],before['base']),(3467,4854))
        self.assertEqual([a['number'] for a in before['articles']],[4950,5046,5142,5238])
        self.assertEqual((after['upper'],after['lower'],after['combination'],after['base']),('艮','艮',8831,10218))
        self.assertEqual([a['number'] for a in after['articles']],[10122,10026,9930,9834])
        self.assertEqual(result['annual']['number'],6476)
        self.assertTrue(all(not a['found'] for a in before['articles']))

    def test_explicit_benming_override_and_middle_five_are_local(self):
        result=self.calc.calculate(EXAMPLE,basis_number=9003,benming_gua_number=2000)
        self.assertEqual(result['before_after']['before']['base'],5467)
        b=dict(EXAMPLE,time='丁亥') # 6+4=10 ->2; day丁巳=10 ->2; test center separately
        b['time']='甲辰' #9+5=14 mod8=6
        b['day']='甲子' #18 mod8=2
        # 己亥=9+4=13 ->5 is the actual unresolved center, other branch still proceeds.
        b['time']='己亥'
        r=self.calc.calculate(b,basis_number=9003)['before_after']
        self.assertEqual(r['after']['status'],'requires_middle_five_rule')
        self.assertEqual(r['before']['status'],'calculated')

    def test_ke_carry_and_sequence_edges_preserve_raw_arithmetic(self):
        b=dict(year='甲子',month='乙丑',day='丙寅',time='丁亥')
        r=self.calc.preliminary(b)
        self.assertEqual((r['sum'],r['remainder'],r['shichen_shift'],r['initial_ke_candidate']),(58,10,1,2))
        r=self.calc.sequence_article(13096)
        self.assertEqual((r['arithmetic_number'],r['number'],r['range_adjustment']),(13096,1096,-12000))
        self.assertEqual(self.calc.sequence_article(904)['number'],12904)
        with self.assertRaises(ValueError):self.calc.calculate(EXAMPLE,confirmed_number=9003,basis_number=9655)

    def test_one_verified_video_caption_does_not_verify_whole_corpus(self):
        calc=VideoMethodCalculator({4381:('黄莺出谷，载迁乔木。','39'),9467:('己酉之年，宴饮鹰扬。','')})
        self.assertTrue(calc.article(4381)['video_text_verified'])
        self.assertFalse(calc.article(4381)['video_edition_verified'])
        self.assertFalse(calc.article(4381)['fact_verified'])
        self.assertFalse(calc.article(9467)['video_text_verified'])
        self.assertFalse(VideoMethodCalculator({4381:('错误条文','')}).article(4381)['video_text_verified'])

    def test_inserted_tables_are_exposed_and_caption_conflict_is_explicit(self):
        result=self.calc.calculate(EXAMPLE)
        tables={t['title']:t for t in result['reference_tables']}
        self.assertEqual(len(tables),8)
        rows={r['key']:r['value'] for r in tables['化神五行数']['rows']}
        self.assertEqual(rows['甲己'],('土',5))
        self.assertEqual(rows['丁壬'],('木',3))
        conflict=result['source_conflicts'][0]
        self.assertEqual(conflict['overlay_order'],'年月日时')
        self.assertEqual(conflict['worked_example_order'],'月日時年')

    def test_parent_tables_video_examples_and_five_digit_encoding(self):
        rows=self.calc.parent_candidates({'父亲':'鼠','母亲':'牛'})
        self.assertEqual([r['base_number'] for r in rows],[9003,9655])
        self.assertEqual([a['number'] for a in rows[0]['year_candidates']],[9003,9013,9023,9033,9043])
        self.assertEqual(self.calc.parent_candidates({'母亲':'猴'})[0]['base_number'],10005)
        self.assertEqual(self.calc.encode_stems('甲月月月壬'),10005)
        self.assertEqual(self.calc.encode_stems('辛支月戊'),9003)
        self.assertFalse(rows[0]['base_article']['fact_verified'])
        for bad in ([],{'父亲':'猫'},{'母亲':[]},{'兄弟':'牛'}):
            with self.assertRaises(ValueError):self.calc.parent_candidates(bad)

    def test_life_sequence_video_26_20_and_wrap(self):
        seq=self.calc.life_sequence(3456)
        numbers=[a['number'] for a in seq['articles']]
        self.assertEqual(numbers[:3],[3456,3552,3648])
        self.assertEqual(len(numbers),125)
        self.assertEqual(len(numbers),len(set(numbers)))
        self.assertEqual(self.calc.life_sequence(12960)['articles'][1]['number'],1056)
        self.assertTrue(all(1001<=n<=13000 for n in numbers))
