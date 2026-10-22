"""兼容命令行入口；实现位于 tiebanshenshu 包。"""
from tiebanshenshu.calendar import convert_to_bazi_info
from tiebanshenshu.data.loader import TieBanDataLoader
from tiebanshenshu.engine.calculator import TieBanCalculator
from tiebanshenshu.presentation.cli import input_datetime, main
from tiebanshenshu.tables.core import (
    LETTER_CORRECTION_MAP, NAYIN_WUXING, build_correction_map,
)

__all__ = [
    'TieBanCalculator', 'TieBanDataLoader', 'convert_to_bazi_info',
    'input_datetime', 'main', 'NAYIN_WUXING', 'LETTER_CORRECTION_MAP',
    'build_correction_map',
]

if __name__ == '__main__':
    main()
