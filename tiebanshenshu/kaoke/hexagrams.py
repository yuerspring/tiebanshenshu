"""起卦、互卦、变卦及考刻取数。"""
from .verification import select_verified_candidate

from tiebanshenshu.tables.kinship import (
    BA_GUA_BY_HOU_TIAN_NUM,
    BA_GUA_BY_XIAN_TIAN_NUM,
    BA_GUA_HOU_TIAN,
    BA_GUA_XIAN_TIAN,
    GUA_TO_LIU_SHI_SI,
)
from tiebanshenshu.tables.numbers import (
    DI_ZHI_TAI_XUAN,
    TIAN_GAN_TAI_XUAN,
)

def calculate_basic_gua(bazi, gender):
    """计算先天基本卦"""
    year_gan = bazi.get('year', '')[0] if len(bazi.get('year', '')) > 0 else ''
    year_zhi = bazi.get('year', '')[1] if len(bazi.get('year', '')) > 1 else ''
    month_gan = bazi.get('month', '')[0] if len(bazi.get('month', '')) > 0 else ''
    month_zhi = bazi.get('month', '')[1] if len(bazi.get('month', '')) > 1 else ''
    
    year_sum = TIAN_GAN_TAI_XUAN.get(year_gan, 0) + DI_ZHI_TAI_XUAN.get(year_zhi, 0)
    month_sum = TIAN_GAN_TAI_XUAN.get(month_gan, 0) + DI_ZHI_TAI_XUAN.get(month_zhi, 0)
    
    year_remainder = year_sum % 8
    month_remainder = month_sum % 8
    
    if year_remainder == 0:
        year_remainder = 8
    if month_remainder == 0:
        month_remainder = 8
    
    yang_gan = ["甲", "丙", "戊", "庚", "壬"]
    is_yang = gender == "男" and year_gan in yang_gan
    is_yin = gender == "女" and year_gan not in yang_gan
    
    if is_yang or is_yin:
        shang_gua_num = year_remainder
        xia_gua_num = month_remainder
    else:
        shang_gua_num = month_remainder
        xia_gua_num = year_remainder
    
    shang_gua = BA_GUA_BY_XIAN_TIAN_NUM.get(shang_gua_num, "")
    xia_gua = BA_GUA_BY_XIAN_TIAN_NUM.get(xia_gua_num, "")
    
    gua_name = GUA_TO_LIU_SHI_SI.get((shang_gua, xia_gua), f"{shang_gua}{xia_gua}")
    
    return {
        "year_sum": year_sum,
        "month_sum": month_sum,
        "year_remainder": year_remainder,
        "month_remainder": month_remainder,
        "shang_gua": shang_gua,
        "xia_gua": xia_gua,
        "gua_name": gua_name,
        "gender_rule": "阳男阴女" if (is_yang or is_yin) else "阴男阳女",
        "formula": f"年柱太玄和={year_sum}→{year_remainder}, 月柱太玄和={month_sum}→{month_remainder}"
    }

def get_hu_gua(shang_gua, xia_gua):
    """计算互卦：取基本卦的二三四爻为下卦，三四五爻为上卦"""
    gua_lines = {
        "乾": ["阳", "阳", "阳"], "坤": ["阴", "阴", "阴"],
        "震": ["阳", "阴", "阴"], "巽": ["阴", "阳", "阳"],
        "坎": ["阴", "阳", "阴"], "离": ["阳", "阴", "阳"],
        "艮": ["阴", "阴", "阳"], "兑": ["阳", "阳", "阴"]
    }
    
    shang_lines = gua_lines.get(shang_gua, ["阳", "阳", "阳"])
    xia_lines = gua_lines.get(xia_gua, ["阳", "阳", "阳"])
    
    all_lines = xia_lines + shang_lines
    
    hu_xia_lines = all_lines[1:4]
    hu_shang_lines = all_lines[2:5]
    
    line_to_gua = {
        ("阳", "阳", "阳"): "乾", ("阴", "阴", "阴"): "坤",
        ("阳", "阴", "阴"): "震", ("阴", "阳", "阳"): "巽",
        ("阴", "阳", "阴"): "坎", ("阳", "阴", "阳"): "离",
        ("阴", "阴", "阳"): "艮", ("阳", "阳", "阴"): "兑"
    }
    
    hu_xia_gua = line_to_gua.get(tuple(hu_xia_lines), "乾")
    hu_shang_gua = line_to_gua.get(tuple(hu_shang_lines), "乾")
    
    hu_gua_name = GUA_TO_LIU_SHI_SI.get((hu_shang_gua, hu_xia_gua), f"{hu_shang_gua}{hu_xia_gua}")
    
    return {
        "hu_shang_gua": hu_shang_gua,
        "hu_xia_gua": hu_xia_gua,
        "hu_gua_name": hu_gua_name
    }

def gua_to_number(shang_gua, xia_gua, hu_shang_gua, hu_xia_gua, use_xian_tian=True):
    """将卦转换为取数：上卦千位，下卦百位，互上卦十位，互下卦个位"""
    if use_xian_tian:
        shang_num = BA_GUA_XIAN_TIAN.get(shang_gua, 1)
        xia_num = BA_GUA_XIAN_TIAN.get(xia_gua, 1)
        hu_shang_num = BA_GUA_XIAN_TIAN.get(hu_shang_gua, 1)
        hu_xia_num = BA_GUA_XIAN_TIAN.get(hu_xia_gua, 1)
    else:
        shang_num = BA_GUA_HOU_TIAN.get(shang_gua, 1)
        xia_num = BA_GUA_HOU_TIAN.get(xia_gua, 1)
        hu_shang_num = BA_GUA_HOU_TIAN.get(hu_shang_gua, 1)
        hu_xia_num = BA_GUA_HOU_TIAN.get(hu_xia_gua, 1)
    
    number = shang_num * 1000 + xia_num * 100 + hu_shang_num * 10 + hu_xia_num
    
    return {
        "number": number,
        "breakdown": f"{shang_num}×1000 + {xia_num}×100 + {hu_shang_num}×10 + {hu_xia_num} = {number}",
        "shang_num": shang_num,
        "xia_num": xia_num,
        "hu_shang_num": hu_shang_num,
        "hu_xia_num": hu_xia_num
    }

def get_bian_gua(shang_gua, xia_gua, yao_pos):
    """动爻变卦：根据动爻位置变卦"""
    gua_lines = {
        "乾": ["阳", "阳", "阳"], "坤": ["阴", "阴", "阴"],
        "震": ["阳", "阴", "阴"], "巽": ["阴", "阳", "阳"],
        "坎": ["阴", "阳", "阴"], "离": ["阳", "阴", "阳"],
        "艮": ["阴", "阴", "阳"], "兑": ["阳", "阳", "阴"]
    }
    
    shang_lines = list(gua_lines.get(shang_gua, ["阳", "阳", "阳"]))
    xia_lines = list(gua_lines.get(xia_gua, ["阳", "阳", "阳"]))
    
    all_lines = xia_lines + shang_lines
    
    if 1 <= yao_pos <= 6:
        idx = yao_pos - 1
        all_lines[idx] = "阴" if all_lines[idx] == "阳" else "阳"
    
    new_xia_lines = all_lines[:3]
    new_shang_lines = all_lines[3:]
    
    line_to_gua = {
        ("阳", "阳", "阳"): "乾", ("阴", "阴", "阴"): "坤",
        ("阳", "阴", "阴"): "震", ("阴", "阳", "阳"): "巽",
        ("阴", "阳", "阴"): "坎", ("阳", "阴", "阳"): "离",
        ("阴", "阴", "阳"): "艮", ("阳", "阳", "阴"): "兑"
    }
    
    new_xia_gua = line_to_gua.get(tuple(new_xia_lines), xia_gua)
    new_shang_gua = line_to_gua.get(tuple(new_shang_lines), shang_gua)
    
    bian_gua_name = GUA_TO_LIU_SHI_SI.get((new_shang_gua, new_xia_gua), f"{new_shang_gua}{new_xia_gua}")
    
    return {
        "bian_shang_gua": new_shang_gua,
        "bian_xia_gua": new_xia_gua,
        "bian_gua_name": bian_gua_name,
        "yao_pos": yao_pos
    }

def calculate_kaoke_qushu(bazi, gender, db=None, verify_condition=None):
    """先天六亲考刻候选；须由外部已知事实核验后选定"""
    basic_result = calculate_basic_gua(bazi, gender)
    shang_gua = basic_result['shang_gua']
    xia_gua = basic_result['xia_gua']
    
    hu_result = get_hu_gua(shang_gua, xia_gua)
    hu_shang_gua = hu_result['hu_shang_gua']
    hu_xia_gua = hu_result['hu_xia_gua']
    
    qs_result = gua_to_number(shang_gua, xia_gua, hu_shang_gua, hu_xia_gua, use_xian_tian=True)
    basic_number = qs_result['number']
    
    candidates = []
    
    candidates.append({
        "yao_pos": 0,
        "desc": "基本卦",
        "shang_gua": shang_gua,
        "xia_gua": xia_gua,
        "gua_name": basic_result['gua_name'],
        "hu_shang_gua": hu_shang_gua,
        "hu_xia_gua": hu_xia_gua,
        "hu_gua_name": hu_result['hu_gua_name'],
        "number": basic_number,
        "match": False
    })
    
    for yao_pos in range(1, 7):
        bian_result = get_bian_gua(shang_gua, xia_gua, yao_pos)
        bian_shang = bian_result['bian_shang_gua']
        bian_xia = bian_result['bian_xia_gua']
        
        bian_hu_result = get_hu_gua(bian_shang, bian_xia)
        bian_hu_shang = bian_hu_result['hu_shang_gua']
        bian_hu_xia = bian_hu_result['hu_xia_gua']
        
        bian_qs_result = gua_to_number(bian_shang, bian_xia, bian_hu_shang, bian_hu_xia, use_xian_tian=True)
        
        duanyu = ""
        if db and hasattr(db, 'FORTUNE_DUANYU_MAP') and bian_qs_result['number'] in db.FORTUNE_DUANYU_MAP:
            duanyu, _ = db.FORTUNE_DUANYU_MAP[bian_qs_result['number']]
        
        match = False
        
        candidates.append({
            "yao_pos": yao_pos,
            "desc": f"{yao_pos}爻动",
            "shang_gua": bian_shang,
            "xia_gua": bian_xia,
            "gua_name": bian_result['bian_gua_name'],
            "hu_shang_gua": bian_hu_shang,
            "hu_xia_gua": bian_hu_xia,
            "hu_gua_name": bian_hu_result['hu_gua_name'],
            "number": bian_qs_result['number'],
            "duanyu": duanyu,
            "match": match
        })
    
    selection = select_verified_candidate(candidates, db, verify_condition)
    best_candidate = selection['candidate']
    best_num = best_candidate['number'] if best_candidate is not None else None
    jiajian_results = []
    if best_num is not None:
        for multiplier in [2, 4, 8, 16]:
            add_val = best_num + 48 * multiplier
            sub_val = best_num - 48 * multiplier
            jiajian_results.append({
                "multiplier": multiplier,
                "add": add_val,
                "sub": sub_val,
                "formula": f"{best_num}±48×{multiplier} → {add_val}, {sub_val}"
            })

    return {
        "basic_gua": basic_result,
        "hu_gua": hu_result,
        "basic_number": basic_number,
        "candidates": candidates,
        "candidate_selection_status": selection["status"],
        "matched_candidate_indices": selection["matched_indices"],
        "verification_basis": "caller_supplied_condition",
        "best_number": best_num,
        "best_candidate": best_candidate,
        "jiajian_results": jiajian_results,
        "method": "先天考刻取数法"
    }

def calculate_houtian_yuncheng(bazi, db=None, verify_condition=None):
    """计算后天运程卦"""
    day_gan = bazi.get('day', '')[0] if len(bazi.get('day', '')) > 0 else ''
    day_zhi = bazi.get('day', '')[1] if len(bazi.get('day', '')) > 1 else ''
    time_gan = bazi.get('time', '')[0] if len(bazi.get('time', '')) > 0 else ''
    time_zhi = bazi.get('time', '')[1] if len(bazi.get('time', '')) > 1 else ''
    
    day_sum = TIAN_GAN_TAI_XUAN.get(day_gan, 0) + DI_ZHI_TAI_XUAN.get(day_zhi, 0)
    time_sum = TIAN_GAN_TAI_XUAN.get(time_gan, 0) + DI_ZHI_TAI_XUAN.get(time_zhi, 0)
    
    shang_num = day_sum - 10
    xia_num = time_sum - 10
    
    if shang_num <= 0:
        shang_num += 9
    if xia_num <= 0:
        xia_num += 9
    
    shang_gua = BA_GUA_BY_HOU_TIAN_NUM.get(shang_num, "")
    xia_gua = BA_GUA_BY_HOU_TIAN_NUM.get(xia_num, "")
    
    if shang_gua == "中":
        shang_gua = "坤"
    if xia_gua == "中":
        xia_gua = "坤"
    
    gua_name = GUA_TO_LIU_SHI_SI.get((shang_gua, xia_gua), f"{shang_gua}{xia_gua}")
    
    hu_result = get_hu_gua(shang_gua, xia_gua)
    hu_shang_gua = hu_result['hu_shang_gua']
    hu_xia_gua = hu_result['hu_xia_gua']
    
    qs_result = gua_to_number(shang_gua, xia_gua, hu_shang_gua, hu_xia_gua, use_xian_tian=False)
    basic_number = qs_result['number']
    
    candidates = []
    
    candidates.append({
        "yao_pos": 0,
        "desc": "基本卦",
        "shang_gua": shang_gua,
        "xia_gua": xia_gua,
        "gua_name": gua_name,
        "hu_shang_gua": hu_shang_gua,
        "hu_xia_gua": hu_xia_gua,
        "hu_gua_name": hu_result['hu_gua_name'],
        "number": basic_number,
        "match": False
    })
    
    for yao_pos in range(1, 7):
        bian_result = get_bian_gua(shang_gua, xia_gua, yao_pos)
        bian_shang = bian_result['bian_shang_gua']
        bian_xia = bian_result['bian_xia_gua']
        
        bian_hu_result = get_hu_gua(bian_shang, bian_xia)
        bian_hu_shang = bian_hu_result['hu_shang_gua']
        bian_hu_xia = bian_hu_result['hu_xia_gua']
        
        bian_qs_result = gua_to_number(bian_shang, bian_xia, bian_hu_shang, bian_hu_xia, use_xian_tian=False)
        
        duanyu = ""
        if db and hasattr(db, 'FORTUNE_DUANYU_MAP') and bian_qs_result['number'] in db.FORTUNE_DUANYU_MAP:
            duanyu, _ = db.FORTUNE_DUANYU_MAP[bian_qs_result['number']]
        
        match = False
        
        candidates.append({
            "yao_pos": yao_pos,
            "desc": f"{yao_pos}爻动",
            "shang_gua": bian_shang,
            "xia_gua": bian_xia,
            "gua_name": bian_result['bian_gua_name'],
            "hu_shang_gua": bian_hu_shang,
            "hu_xia_gua": bian_hu_xia,
            "hu_gua_name": bian_hu_result['hu_gua_name'],
            "number": bian_qs_result['number'],
            "duanyu": duanyu,
            "match": match
        })
    
    selection = select_verified_candidate(candidates, db, verify_condition)
    best_candidate = selection['candidate']
    best_num = best_candidate['number'] if best_candidate is not None else None
    jiajian_results = []
    if best_num is not None:
        for multiplier in [2, 4, 8, 16]:
            add_val = best_num + 48 * multiplier
            sub_val = best_num - 48 * multiplier
            jiajian_results.append({
                "multiplier": multiplier,
                "add": add_val,
                "sub": sub_val,
                "formula": f"{best_num}±48×{multiplier} → {add_val}, {sub_val}"
            })

    return {
        "day_sum": day_sum,
        "time_sum": time_sum,
        "shang_num": shang_num,
        "xia_num": xia_num,
        "basic_gua": gua_name,
        "hu_gua": hu_result,
        "basic_number": basic_number,
        "candidates": candidates,
        "candidate_selection_status": selection["status"],
        "matched_candidate_indices": selection["matched_indices"],
        "verification_basis": "caller_supplied_condition",
        "best_number": best_num,
        "best_candidate": best_candidate,
        "jiajian_results": jiajian_results,
        "method": "后天运程取数法"
    }

__all__ = [
    'calculate_basic_gua',
    'get_hu_gua',
    'gua_to_number',
    'get_bian_gua',
    'calculate_kaoke_qushu',
    'calculate_houtian_yuncheng',
]
