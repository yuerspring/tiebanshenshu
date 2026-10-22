import unittest
from types import SimpleNamespace
from keke_module import kao_ke


class KaokeCandidates(unittest.TestCase):
    def test_zero_matches_never_becomes_first_quarter(self):
        selected, rows, info = kao_ke({'父亲': 10}, {'父亲': '鸡'})
        self.assertIsNone(selected)
        self.assertEqual(info['status'], 'no_match')
        self.assertEqual(info['match_count'], 0)
        self.assertFalse(any(row['match'] for row in rows))

    def test_all_relations_must_agree_not_just_first(self):
        bases = {'父亲': 10, '母亲': 11}
        selected, _, info = kao_ke(bases, {'父亲': '鼠', '母亲': '牛'})
        self.assertEqual(selected, 1)
        self.assertEqual(info['used_relations'], ['父亲', '母亲'])
        self.assertEqual(info['source_status'], 'unverified')
        conflict = {'父亲': '鼠', '母亲': '虎'}
        selected, rows, info = kao_ke(bases, conflict)
        self.assertIsNone(selected)
        self.assertEqual(info['status'], 'no_match')
        self.assertEqual(rows[0]['conflicting_conditions'], 1)
        self.assertEqual(kao_ke(bases, dict(reversed(list(conflict.items())))),
                         kao_ke(bases, conflict))

    def test_dog_and_pig_are_explicitly_unsupported(self):
        for zodiac in ('狗', '猪'):
            with self.subTest(zodiac=zodiac):
                selected, rows, info = kao_ke({'父亲': 10}, {'父亲': zodiac})
                self.assertIsNone(selected)
                self.assertEqual(info['status'], 'unsupported')
                self.assertEqual(info['unsupported_relations'], ['父亲'])
                self.assertTrue(all(row['conditions'][0]['match'] is None for row in rows))

    def test_supported_conflict_takes_precedence_over_unsupported_relation(self):
        selected, _, info = kao_ke(
            {'父亲': 10, '母亲': 10, '子女': 10},
            {'父亲': '鼠', '母亲': '牛', '子女': '狗'},
        )
        self.assertIsNone(selected)
        self.assertEqual(info['status'], 'no_match')
        self.assertEqual(info['supported_candidate_ks'], [])
        self.assertEqual(info['unsupported_relations'], ['子女'])

    def test_existence_of_verse_does_not_claim_text_verification(self):
        database = SimpleNamespace(FORTUNE_DUANYU_MAP={})
        _, rows, _ = kao_ke({'父亲': 10}, {'父亲': '鼠'}, database)
        code = rows[0]['conditions'][0]['code']
        database.FORTUNE_DUANYU_MAP[code] = ('完全不涉及父亲生肖的条文', '')
        _, rows, _ = kao_ke({'父亲': 10}, {'父亲': '鼠'}, database)
        self.assertFalse(rows[0]['conditions'][0]['text_verified'])
        self.assertEqual(rows[0]['conditions'][0]['duanyu'], '完全不涉及父亲生肖的条文')

    def test_empty_evidence_does_not_select_a_quarter(self):
        self.assertEqual(kao_ke({'父亲': 10}, {}), (None, None, None))


if __name__ == '__main__':
    unittest.main()
