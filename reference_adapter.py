"""Independent, unmodified calculation using Nanphy/TiebanshenshuOS.

The archived source and its own CSV tables live under reference_os/. This
adapter supplies absolute paths and disables the archived localhost debug
reporter; it does not change that project's calculation rules.
"""
import datetime as dt
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent / 'reference_os'
_module = None
_calculator = None


def reference_calculator():
    global _module, _calculator
    if _calculator is None:
        spec = importlib.util.spec_from_file_location('archived_tiebanshenshu_os', ROOT / 'main.py')
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        # The archived code attempts to POST debug events to localhost. Disable
        # the transport; public chart inputs never need to leave this process.
        module.report_log = lambda *args, **kwargs: None
        calc = module.TieBanCalculator.__new__(module.TieBanCalculator)
        calc.loader = module.TieBanDataLoader(db_folder=str(ROOT / 'DB'))
        calc.db = calc.loader
        calc.tiangan = module.TIAN_GAN
        calc.dizhi = module.DI_ZHI
        _module, _calculator = module, calc
    return _module, _calculator


def compare_with_os(data, current):
    module, calc = reference_calculator()
    birth = dt.datetime.strptime(f"{data['birth_date']} {data['birth_time']}", '%Y-%m-%d %H:%M')
    query = dt.datetime.strptime(f"{data['query_date']} {data['query_time']}", '%Y-%m-%d %H:%M')
    if birth.hour == 23:
        birth = (birth + dt.timedelta(days=1)).replace(hour=0)
    birth_info, query_info = module.convert_to_bazi_info(birth), module.convert_to_bazi_info(query)
    if not birth_info or not query_info:
        raise ValueError('参考版农历或八字转换失败')
    result = calc.calculate({'gender': data['gender'], 'birth_info': birth_info,
                             'query_info': query_info})
    table = result.get('tbl_data') or {}
    brother = []
    for offset in table.get('offsets', {}).get('兄弟个数', []):
        number = table['base'] + table['seq'] + offset
        sentence, age = calc.get_fortune_duanyu(number)
        brother.append({'number': number, 'sentence': sentence, 'age': age})
    current_annual = current['result'].get('liunian') or []
    reference_annual = result.get('liunian') or []
    annual_differences = sum(
        old.get('corrected_fortune') != new.get('corrected_fortune')
        for old, new in zip(reference_annual, current_annual)
    )
    return json.loads(json.dumps({
        'source': 'Nanphy/TiebanshenshuOS@785dc871d523e1c4d7772946955fd30fc8ebb4bf',
        'reference': {
            'eight_ke': result.get('moment_cn'),
            'ke_gan_number': result.get('ke_gan_num'),
            'main_num': result.get('main_num'),
            'final_fortune_num': result.get('final_fortune_num'),
            'hex_name': result.get('hex_name'),
            'brother_articles': brother,
            'annual_fortunes': reference_annual,
            'bagua_jiaze': result.get('bagua_jiaze'),
            'san_yuan': result.get('san_yuan'),
            'wu_shu_ji_gong': result.get('wu_shu_ji_gong'),
            'original_result': result,
        },
        'current': {
            'moment_cn': current['result'].get('moment_cn'),
            'k_initial': current['result'].get('keke', {}).get('k_initial'),
            'main_num': current['result'].get('main_num'),
            'hex_name': current['result'].get('hex_name'),
            'brother_articles': [a for a in current['destiny_articles'] if '兄弟' in a['topic']],
        },
        'annual_corrected_fortune_differences': annual_differences,
        'notes': [
            '参考版按原代码计算；其中 get_eight_ke_from_time 对普通奇数小时额外加 60 分钟，可能把卯时 05:30 归入第七刻，不能据此确认出生分钟。',
            '参考版的六亲验证执行段被注释，输入兄弟人数或生肖不会重算其本命兄弟条文。',
            '两版 14-10.csv、List.csv 一致；14-11-1、14-11-2 和 14-13 的若干内容不同，流年差异不能仅归因于算法。',
        ],
    }, ensure_ascii=False, default=str))
