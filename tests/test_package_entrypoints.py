"""Deployment regressions introduced by moving files into a package."""
import contextlib
import importlib
import io
import os
from pathlib import Path
import pkgutil
import subprocess
import sys
import tempfile
import unittest

import keke_module
import main
import tiebanshenshu
from tiebanshenshu.data.loader import TieBanDataLoader
from tiebanshenshu.engine.calculator import TieBanCalculator
from tiebanshenshu.kaoke.candidates import kao_ke

ROOT = Path(__file__).resolve().parents[1]


class PackageEntrypoints(unittest.TestCase):
    def test_legacy_imports_share_the_real_implementations(self):
        self.assertIs(main.TieBanCalculator, TieBanCalculator)
        self.assertIs(main.TieBanDataLoader, TieBanDataLoader)
        self.assertIs(keke_module.kao_ke, kao_ke)

    def test_every_algorithm_module_can_be_imported(self):
        for info in pkgutil.walk_packages(tiebanshenshu.__path__, 'tiebanshenshu.'):
            with self.subTest(module=info.name):
                importlib.import_module(info.name)

    def test_data_paths_do_not_depend_on_working_directory(self):
        command = '''import contextlib,io
from tiebanshenshu.data.loader import TieBanDataLoader
with contextlib.redirect_stdout(io.StringIO()):
    db=TieBanDataLoader()
assert len(db.FORTUNE_DUANYU_MAP)==12000
assert db.LETTER_TABLE['初刻','奇数','四','石']=='福'
'''
        with tempfile.TemporaryDirectory() as folder:
            proc = subprocess.run([sys.executable, '-c', command], cwd=folder,
                                  env={**os.environ, 'PYTHONPATH': str(ROOT)},
                                  text=True, capture_output=True, timeout=30)
        self.assertEqual(proc.returncode, 0, proc.stderr)

    def test_module_cli_writes_report_outside_repository(self):
        with tempfile.TemporaryDirectory() as folder:
            proc = subprocess.run([sys.executable, '-m', 'tiebanshenshu'],
                                  input='1\n1924-06-15 16:00\n2025-04-20 10:00\n',
                                  cwd=folder, env={**os.environ, 'PYTHONPATH': str(ROOT)},
                                  text=True, capture_output=True, timeout=30)
            reports = list((Path(folder) / 'output').glob('*.md'))
            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertEqual(len(reports), 1, proc.stdout)
            report = reports[0].read_text()
            self.assertIn('本命数', report)
            self.assertIn('344', report)
            self.assertIn('9760', report)


if __name__ == '__main__':
    unittest.main()
