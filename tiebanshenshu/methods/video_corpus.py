"""仅加载条文供版本对照，不初始化十四表算法。"""
import csv
from functools import lru_cache
from tiebanshenshu.paths import DB_DIR

@lru_cache(maxsize=1)
def load_comparison_verses():
    with (DB_DIR / 'List.csv').open(encoding='utf-8-sig', newline='') as stream:
        return {int(row['条文数']):(row['吉凶断词'],row['年龄'])
                for row in csv.DictReader(stream)}
