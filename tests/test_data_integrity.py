import csv
import json
import tempfile
import unittest
from pathlib import Path
from scripts.audit_data import ROOT, MANIFEST, audit, check_corpus


class DataIntegrity(unittest.TestCase):
    def test_repository_corpus_is_complete_and_matches_reviewed_snapshot(self):
        result = audit()
        self.assertTrue(result['ok'], result['errors'])
        self.assertEqual(result['corpus']['rows'], 12000)
        self.assertEqual(result['corpus']['unique_numbers'], 12000)

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
