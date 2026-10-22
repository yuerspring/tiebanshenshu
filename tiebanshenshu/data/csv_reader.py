"""CSV编码兼容读取与单元格清洗。"""
import os
from pathlib import Path
import pandas as pd
from tiebanshenshu.paths import DB_DIR


class CsvTableReader:
    def __init__(self, db_folder=None):
        self.db_folder = str(Path(db_folder) if db_folder is not None else DB_DIR)

    def _read_csv_robust(self, filename, header_option=0):
        """健壮的读取函数，自动尝试多种编码"""
        path = os.path.join(self.db_folder, filename)
        if not os.path.exists(path): return None

        encodings = ['utf-8-sig', 'gbk', 'gb18030', 'utf-16']
        for enc in encodings:
            try:
                return pd.read_csv(path, header=header_option, encoding=enc)
            except Exception as e:
                continue
        return None

    def _read_csv_as_dicts(self, filename):
        """读取为字典列表 (带表头)"""
        df = self._read_csv_robust(filename, header_option=0)
        if df is not None:
            return df.to_dict('records')
        return []

    def _clean_key(self, val):
        if pd.isna(val) or val is None: return ""
        return str(val).strip().replace('\ufeff', '')

    def _is_numeric(self, value):
        """判断值是否可以转换为数字"""
        if pd.isna(value):
            return False
        try:
            float(value)
            return True
        except (ValueError, TypeError):
            return False
