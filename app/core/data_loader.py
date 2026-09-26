"""Reuse the repository's CSV parser with a shared startup instance."""
from pathlib import Path
from main import TieBanDataLoader

ROOT = Path(__file__).resolve().parents[2]
DATABASE = ROOT / "数据库"
REQUIRED_FILES = [f"14-{n}.csv" for n in range(1, 11)] + [
    "14-11-1.csv", "14-11-2.csv", "14-12.csv", "14-13.csv", "14-14.csv",
    "铁板神数-条文断词.csv",
]


def load_database():
    missing = [name for name in REQUIRED_FILES if not (DATABASE / name).is_file()]
    if missing:
        raise RuntimeError("数据库文件缺失：" + "、".join(missing))
    loader = TieBanDataLoader(DATABASE)
    if not loader.DATA_BY_LETTER or not loader.FORTUNE_DUANYU_MAP or not loader.DESTINY_DATA:
        raise RuntimeError("数据库加载失败：本命、流年条文或断语为空")
    return loader
