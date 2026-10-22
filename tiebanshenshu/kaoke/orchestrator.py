"""组合各考刻模块的计算结果。"""
from tiebanshenshu.kaoke.annual import (
    calculate_liunian_zai_e,
)
from tiebanshenshu.kaoke.bagua import (
    calculate_bagua_gunxin,
    calculate_kuaisu_duanming,
)
from tiebanshenshu.kaoke.candidates import (
    get_kefen,
)
from tiebanshenshu.kaoke.family import (
    calculate_hunyin_zhuangkuang,
    calculate_mingli_guiji,
    calculate_peyou_xingming,
    classify_children,
    convert_family_fate,
    generate_48_changes,
    handle_cesarean,
)
from tiebanshenshu.kaoke.numbers import (
    calculate_liuqinjishu,
    get_day_su,
    get_hour_su,
    get_jiayun,
)
from tiebanshenshu.kaoke.palaces import (
    calculate_liuqin_gongwei,
    determine_liuqin_gongwei,
    get_bazi_gong,
)
from tiebanshenshu.kaoke.relatives import (
    calculate_brother_shengxiao,
    calculate_children_shengxiao,
    calculate_parent_shengxiao,
    calculate_spouse_shengxiao,
)

def calculate_keke(birth_info, query_info=None, fortune_map=None, db=None):
    """完整考刻定分计算"""
    bazi = birth_info.get('bazi', {})
    if not bazi:
        return None
    
    year_gan_zhi = bazi.get('year', '')
    if len(year_gan_zhi) < 2:
        return None
    
    year_gan, year_zhi = year_gan_zhi[0], year_gan_zhi[1]
    
    jiayun, xinqi1_su = get_jiayun(year_gan_zhi)
    
    hour = birth_info.get('clock_hour', birth_info.get('hour', 0))
    minute = birth_info.get('clock_minute', birth_info.get('minute', 0))
    
    k, minute_in_shichen = get_kefen(hour, minute)
    
    D = 0
    H = 0
    
    if birth_info.get('lunar_month') and birth_info.get('lunar_day'):
        day_offset = (birth_info['lunar_month'] - 1) * 30 + birth_info['lunar_day']
        day_su, D = get_day_su(xinqi1_su, day_offset)
        time_zhi = bazi.get('time', '')[1] if len(bazi.get('time', '')) > 1 else ''
        hour_su, H = get_hour_su(day_su, time_zhi)
    
    liuqinjishu = calculate_liuqinjishu(bazi, D, H)
    
    parent_result = calculate_parent_shengxiao(bazi)
    children_result = calculate_children_shengxiao(bazi)
    brother_result = calculate_brother_shengxiao(bazi)
    spouse_result = calculate_spouse_shengxiao(bazi)
    liuqin_gongwei_result = calculate_liuqin_gongwei(bazi)
    
    bazi_gong_result = get_bazi_gong(bazi)
    liuqin_position_result = determine_liuqin_gongwei(bazi)
    mingli_guiji_result = calculate_mingli_guiji(bazi)
    children_type_result = classify_children(bazi)
    cesarean_result = handle_cesarean(bazi)
    
    family_fate_results = {}
    for member in ["父亲", "母亲", "兄弟", "姊妹"]:
        family_fate_results[member] = convert_family_fate(bazi, member)
    
    changes_48_result = generate_48_changes(bazi)
    
    peyou_xingming_result = calculate_peyou_xingming(bazi, db)
    hunyin_zhuangkuang_result = calculate_hunyin_zhuangkuang(bazi, fortune_map)
    liunian_zai_e_result = calculate_liunian_zai_e(bazi, fortune_map=fortune_map)
    
    result = {
        "jiayun": jiayun,
        "xinqi1_su": xinqi1_su,
        "day_su": day_su if 'day_su' in locals() else None,
        "hour_su": hour_su if 'hour_su' in locals() else None,
        "D": D,
        "H": H,
        "k_initial": k,
        "minute_in_shichen": minute_in_shichen,
        "liuqinjishu": liuqinjishu,
        "parent_shengxiao": parent_result,
        "children_shengxiao": children_result,
        "brother_shengxiao": brother_result,
        "spouse_shengxiao": spouse_result,
        "liuqin_gongwei": liuqin_gongwei_result,
        "bazi_gong": bazi_gong_result,
        "liuqin_position": liuqin_position_result,
        "mingli_guiji": mingli_guiji_result,
        "children_type": children_type_result,
        "cesarean": cesarean_result,
        "family_fate": family_fate_results,
        "changes_48": changes_48_result,
        "peyou_xingming": peyou_xingming_result,
        "hunyin_zhuangkuang": hunyin_zhuangkuang_result,
        "liunian_zai_e": liunian_zai_e_result,
        "bagua_gunxin": calculate_bagua_gunxin(bazi, fortune_map),
        "kuaisu_duanming": calculate_kuaisu_duanming(bazi, fortune_map)
    }
    
    return result

__all__ = [
    'calculate_keke',
]
