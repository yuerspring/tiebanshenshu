import csv
import json
import tempfile
import unittest
from pathlib import Path
from scripts.audit_data import ROOT, MANIFEST, audit, check_corpus, check_hexagram_table


class DataIntegrity(unittest.TestCase):
    def test_repository_corpus_is_complete_and_matches_reviewed_snapshot(self):
        result = audit()
        self.assertTrue(result['ok'], result['errors'])
        self.assertEqual(result['corpus']['rows'], 12000)
        self.assertEqual(result['corpus']['unique_numbers'], 12000)

    def test_existing_missing_and_duplicate_quarter_keys_are_visible(self):
        report = audit()
        self.assertFalse(report['table_quality_ok'])
        self.assertEqual(report['table_14_9_findings']['missing'], [['正刻', 700]])
        duplicate = report['table_14_9_findings']['duplicates'][0]
        self.assertEqual(duplicate['key'], ['正刻', 670])
        self.assertEqual(duplicate['lines'], [1240, 1270])

    def test_conflicting_table_rows_are_not_silently_overwritten(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / '14-9.csv'
            path.write_text('初刻,181,大壮\n初刻,181,乾\n', encoding='utf-8')
            report = check_hexagram_table(path)
            self.assertTrue(report['duplicates'][0]['conflicting'])

    def test_modified_hash_fails_audit(self):
        snapshot = json.loads(MANIFEST.read_text())
        snapshot['files']['DB/List.csv']['sha256'] = '0' * 64
        with tempfile.TemporaryDirectory() as temp:
            manifest = Path(temp) / 'manifest.json'
            manifest.write_text(json.dumps(snapshot))
            self.assertFalse(audit(ROOT, manifest)['ok'])

    def test_duplicate_number_and_empty_text_are_not_hidden(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / 'List.csv'
            with path.open('w', encoding='utf-8', newline='') as handle:
                writer = csv.writer(handle)
                writer.writerow(['集', '条文数', '年龄', '吉凶断词'])
                writer.writerow(['子集', 1001, '', 'example'])
                writer.writerow(['子集', 1001, '', ''])
            errors, _ = check_corpus(path)
            self.assertTrue(any('duplicate' in error for error in errors))
            self.assertTrue(any('empty verse' in error for error in errors))


if __name__ == '__main__':
    unittest.main()
