"""金泉本 PDF 68–69 页所述先验基本卦、再验变卦的流程回归。"""
import unittest
from types import SimpleNamespace
from tiebanshenshu.kaoke.hexagrams import calculate_kaoke_qushu, calculate_houtian_yuncheng


class BookCandidateVerificationTests(unittest.TestCase):
    def methods(self):
        bazi = dict(year='甲子', month='庚午', day='乙丑', time='甲申')
        return (
            lambda **kw: calculate_kaoke_qushu(bazi, '男', **kw),
            lambda **kw: calculate_houtian_yuncheng(bazi, **kw),
        )

    def test_unverified_and_unmatched_do_not_generate_predictions(self):
        for method in self.methods():
            for kw, status in [({}, 'not_provided'), ({'verify_condition': lambda n, d: False}, 'no_match')]:
                result = method(**kw)
                self.assertEqual(result['candidate_selection_status'], status)
                self.assertIsNone(result['best_number'])
                self.assertIsNone(result['best_candidate'])
                self.assertEqual(result['jiajian_results'], [])
                self.assertEqual(len(result['candidates']), 7)

    def test_basic_verse_is_checked_once_and_can_be_selected(self):
        for method in self.methods():
            number = method()['basic_number']
            seen = []
            def verify(n, text):
                seen.append((n, text))
                return n == number and text == '已知事实测试'
            result = method(db=SimpleNamespace(FORTUNE_DUANYU_MAP={number: ('已知事实测试', '')}), verify_condition=verify)
            self.assertEqual(len(seen), 7)
            self.assertEqual(seen[0], (number, '已知事实测试'))
            self.assertEqual(result['candidate_selection_status'], 'unique_candidate')
            self.assertEqual(result['best_candidate']['yao_pos'], 0)
            self.assertEqual(result['jiajian_results'][0]['add'], number + 96)
            self.assertEqual(result['jiajian_results'][0]['sub'], number - 96)

    def test_multiple_matches_remain_ambiguous(self):
        for method in self.methods():
            result = method(verify_condition=lambda n, d: True)
            self.assertEqual(result['candidate_selection_status'], 'ambiguous')
            self.assertEqual(result['matched_candidate_indices'], list(range(7)))
            self.assertIsNone(result['best_number'])
            self.assertEqual(result['jiajian_results'], [])

    def test_unique_changed_line_is_selected(self):
        for method in self.methods():
            number = method()['candidates'][2]['number']
            result = method(verify_condition=lambda n, d: n == number)
            self.assertEqual(result['candidate_selection_status'], 'unique_candidate')
            self.assertEqual(result['best_candidate']['yao_pos'], 2)

class BookTableAndVerseTests(unittest.TestCase):
    def test_jin_pdf_68_taixuan_table_and_derived_example(self):
        from tiebanshenshu.tables.numbers import TIAN_GAN_TAI_XUAN, DI_ZHI_TAI_XUAN
        from tiebanshenshu.kaoke.hexagrams import calculate_basic_gua, get_hu_gua, gua_to_number
        for chars, expected in [('甲己子午', 9), ('乙庚丑未', 8), ('丙辛寅申', 7), ('丁壬卯酉', 6), ('戊癸辰戌', 5), ('巳亥', 4)]:
            for char in chars:
                self.assertEqual((TIAN_GAN_TAI_XUAN | DI_ZHI_TAI_XUAN)[char], expected)
        # 人工构造输入按书中规则手算：18%8=2兑；12%8=4震；互上巽5、互下艮7。
        gua = calculate_basic_gua({'year':'甲子', 'month':'丁卯'}, '男')
        self.assertEqual((gua['shang_gua'], gua['xia_gua']), ('兑', '震'))
        hu = get_hu_gua('兑', '震')
        self.assertEqual(gua_to_number('兑','震',hu['hu_shang_gua'],hu['hu_xia_gua'])['number'], 2457)

    def test_xu_pdf_40_four_explicit_parent_examples(self):
        import contextlib
        import io
        from tiebanshenshu.data.loader import TieBanDataLoader
        with contextlib.redirect_stdout(io.StringIO()):
            db = TieBanDataLoader()
        for number, subject, animal in [(9253,'父命','蛇'), (9553,'父命','亥'), (9855,'母命','蛇'), (10155,'母命','猪')]:
            text = db.FORTUNE_DUANYU_MAP[number][0]
            self.assertIn(subject, text)
            self.assertIn(animal, text)


if __name__ == '__main__':
    unittest.main()
