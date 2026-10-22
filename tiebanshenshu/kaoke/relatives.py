"""父母、兄弟、子女与配偶生肖。"""
from tiebanshenshu.kaoke.relationships import (
    check_pokong,
    get_nayin,
    get_nayin_wuxing,
)
from tiebanshenshu.tables.kinship import (
    BA_GUA_XIAN_TIAN,
    DI_ZHI_TO_SHENG_XIAO,
    GAN_ZHI_COMBINE,
    GUA_TO_LIU_SHI_SI,
    LIUHE_PAIRS,
    LIU_QIN_TYPE_CODES,
    NAYIN_TO_WUXING,
    SANHE_GROUPS,
    TIAN_GAN_TO_GUA_XINYI,
    TIAN_GAN_XINYI,
)
from tiebanshenshu.tables.numbers import (
    DI_ZHI_TAI_XUAN,
)

def calculate_parent_shengxiao(bazi):
    """推算父母生肖"""
    year_gan_zhi = bazi.get('year', '')
    month_gan_zhi = bazi.get('month', '')
    day_gan_zhi = bazi.get('day', '')
    
    year_gan = year_gan_zhi[0] if len(year_gan_zhi) > 0 else ''
    year_zhi = year_gan_zhi[1] if len(year_gan_zhi) > 1 else ''
    month_gan = month_gan_zhi[0] if len(month_gan_zhi) > 0 else ''
    month_zhi = month_gan_zhi[1] if len(month_gan_zhi) > 1 else ''
    day_zhi = day_gan_zhi[1] if len(day_gan_zhi) > 1 else ''
    
    pokong_info = check_pokong(bazi)
    has_xing_pokong = pokong_info["has_xing"] or pokong_info["has_pokong"]
    
    father_candidates = []
    mother_candidates = []
    
    if not has_xing_pokong:
        father_candidates.append({
            "shengxiao": DI_ZHI_TO_SHENG_XIAO.get(year_zhi, ""),
            "reason": "父母之生肖必与其父之干支同支"
        })
        mother_candidates.append({
            "shengxiao": DI_ZHI_TO_SHENG_XIAO.get(month_zhi, ""),
            "reason": "父母之生肖必与其母之干支同支"
        })
    else:
        for group in SANHE_GROUPS:
            if year_zhi in group:
                for zhi in group:
                    if zhi != year_zhi:
                        father_candidates.append({
                            "shengxiao": DI_ZHI_TO_SHENG_XIAO.get(zhi, ""),
                            "reason": f"{year_zhi}三合{zhi}"
                        })
        
        he_zhi = LIUHE_PAIRS.get(year_zhi)
        if he_zhi:
            father_candidates.append({
                "shengxiao": DI_ZHI_TO_SHENG_XIAO.get(he_zhi, ""),
                "reason": f"{year_zhi}六合{he_zhi}"
            })
        
        for group in SANHE_GROUPS:
            if month_zhi in group:
                for zhi in group:
                    if zhi != month_zhi:
                        mother_candidates.append({
                            "shengxiao": DI_ZHI_TO_SHENG_XIAO.get(zhi, ""),
                            "reason": f"{month_zhi}三合{zhi}"
                        })
        
        he_zhi = LIUHE_PAIRS.get(month_zhi)
        if he_zhi:
            mother_candidates.append({
                "shengxiao": DI_ZHI_TO_SHENG_XIAO.get(he_zhi, ""),
                "reason": f"{month_zhi}六合{he_zhi}"
            })
    
    return {
        "father": father_candidates,
        "mother": mother_candidates,
        "has_xing_pokong": has_xing_pokong,
        "pokong_info": pokong_info
    }

def calculate_children_shengxiao(bazi, k_true=None):
    """推算子孙生肖（使用纳音和考刻结果）"""
    time_gan_zhi = bazi.get('time', '')
    day_gan_zhi = bazi.get('day', '')
    
    time_gan = time_gan_zhi[0] if len(time_gan_zhi) > 0 else ''
    time_zhi = time_gan_zhi[1] if len(time_gan_zhi) > 1 else ''
    day_gan = day_gan_zhi[0] if len(day_gan_zhi) > 0 else ''
    day_zhi = day_gan_zhi[1] if len(day_gan_zhi) > 1 else ''
    
    nayin_time = get_nayin(time_gan_zhi)
    nayin_day = get_nayin(day_gan_zhi)
    
    children_candidates = []
    
    nayin_wuxing_time = get_nayin_wuxing(time_gan_zhi)
    nayin_wuxing_day = get_nayin_wuxing(day_gan_zhi)
    
    if nayin_wuxing_time == nayin_wuxing_day:
        for zhi in GAN_ZHI_COMBINE.get(time_gan, []):
            children_candidates.append({
                "shengxiao": DI_ZHI_TO_SHENG_XIAO.get(zhi, ""),
                "reason": f"时纳音{nayin_time}与日纳音{nayin_day}相同，取时干{nayin_wuxing_time}属性"
            })
    else:
        for zhi in GAN_ZHI_COMBINE.get(day_gan, []):
            children_candidates.append({
                "shengxiao": DI_ZHI_TO_SHENG_XIAO.get(zhi, ""),
                "reason": f"时纳音{nayin_time}与日纳音{nayin_day}不同，取日干属性"
            })
    
    if k_true and day_zhi:
        he_zhi = LIUHE_PAIRS.get(day_zhi)
        if he_zhi:
            children_candidates.append({
                "shengxiao": DI_ZHI_TO_SHENG_XIAO.get(he_zhi, ""),
                "reason": f"考刻{k_true}刻，日支{day_zhi}六合{he_zhi}"
            })
    
    return {
        "children": children_candidates,
        "nayin_time": nayin_time,
        "nayin_day": nayin_day
    }

def calculate_brother_shengxiao(bazi):
    """推算兄弟生肖"""
    month_gan_zhi = bazi.get('month', '')
    day_gan_zhi = bazi.get('day', '')
    
    month_gan = month_gan_zhi[0] if len(month_gan_zhi) > 0 else ''
    month_zhi = month_gan_zhi[1] if len(month_gan_zhi) > 1 else ''
    day_gan = day_gan_zhi[0] if len(day_gan_zhi) > 0 else ''
    day_zhi = day_gan_zhi[1] if len(day_gan_zhi) > 1 else ''
    
    brother_candidates = []
    sister_candidates = []
    
    nayin_month = get_nayin(month_gan_zhi)
    nayin_day = get_nayin(day_gan_zhi)
    
    for group in SANHE_GROUPS:
        if month_zhi in group:
            for zhi in group:
                brother_candidates.append({
                    "shengxiao": DI_ZHI_TO_SHENG_XIAO.get(zhi, ""),
                    "reason": f"月支{month_zhi}三合{zhi}"
                })
    
    he_zhi = LIUHE_PAIRS.get(month_zhi)
    if he_zhi:
        brother_candidates.append({
            "shengxiao": DI_ZHI_TO_SHENG_XIAO.get(he_zhi, ""),
            "reason": f"月支{month_zhi}六合{he_zhi}"
        })
    
    sister_candidates = [{
        "shengxiao": DI_ZHI_TO_SHENG_XIAO.get(zhi, ""),
        "reason": f"姊妹属{NAYIN_TO_WUXING.get(nayin_month, '')}生肖"
    } for zhi in GAN_ZHI_COMBINE.get(month_gan, [])[:3]]
    
    return {
        "brother": brother_candidates,
        "sister": sister_candidates,
        "nayin_month": nayin_month,
        "nayin_day": nayin_day
    }

def calculate_xinyi_brother_count(bazi, db=None):
    """心易派铁板神数兄弟姐妹数计算"""
    year_gan = bazi.get('year', '')[0] if len(bazi.get('year', '')) > 0 else ''
    month_gan = bazi.get('month', '')[0] if len(bazi.get('month', '')) > 0 else ''
    day_gan = bazi.get('day', '')[0] if len(bazi.get('day', '')) > 0 else ''
    time_gan = bazi.get('time', '')[0] if len(bazi.get('time', '')) > 0 else ''
    
    year_zhi = bazi.get('year', '')[1] if len(bazi.get('year', '')) > 1 else ''
    month_zhi = bazi.get('month', '')[1] if len(bazi.get('month', '')) > 1 else ''
    day_zhi = bazi.get('day', '')[1] if len(bazi.get('day', '')) > 1 else ''
    time_zhi = bazi.get('time', '')[1] if len(bazi.get('time', '')) > 1 else ''
    
    year_num = TIAN_GAN_XINYI.get(year_gan, 0)
    month_num = TIAN_GAN_XINYI.get(month_gan, 0)
    day_num = TIAN_GAN_XINYI.get(day_gan, 0)
    time_num = TIAN_GAN_XINYI.get(time_gan, 0)
    
    tian_gan_num = f"{year_num}{month_num}{day_num}{time_num}"
    
    shang_sum = year_num + month_num
    xia_sum = day_num + time_num
    
    shang_gua = TIAN_GAN_TO_GUA_XINYI.get(shang_sum % 8 if shang_sum % 8 != 0 else 8, "坤")
    xia_gua = TIAN_GAN_TO_GUA_XINYI.get(xia_sum % 8 if xia_sum % 8 != 0 else 8, "坤")
    
    gua_name = GUA_TO_LIU_SHI_SI.get((shang_gua, xia_gua), f"{shang_gua}{xia_gua}")
    
    gua_yao_info = {
        "火地晋": {
            "yao": [
                {"position": "上爻", "role": "官鬼", "gan": "己", "zhi": "巳"},
                {"position": "五爻", "role": "父母", "gan": "己", "zhi": "未"},
                {"position": "四爻", "role": "兄弟", "gan": "己", "zhi": "酉", "shi": True},
                {"position": "三爻", "role": "妻财", "gan": "乙", "zhi": "卯"},
                {"position": "二爻", "role": "官鬼", "gan": "乙", "zhi": "巳"},
                {"position": "初爻", "role": "父母", "gan": "乙", "zhi": "未", "ying": True}
            ]
        }
    }
    
    yao_info = gua_yao_info.get(gua_name, {})
    
    fu_mu_yong_shen = None
    fu_mu_yong_shen_value = 0
    ying_yao_value = 0
    
    if yao_info:
        for yao in yao_info.get("yao", []):
            if yao.get("role") == "父母":
                gan_val = TIAN_GAN_XINYI.get(yao["gan"], 0)
                zhi_val = DI_ZHI_TAI_XUAN.get(yao["zhi"], 0)
                if yao.get("shi"):
                    fu_mu_yong_shen = yao
                    fu_mu_yong_shen_value = (gan_val - zhi_val) * 10
                elif yao.get("ying"):
                    ying_yao_value = gan_val + zhi_val
    
    father_results = []
    mother_results = []
    
    fuqin_bian_gua = {"shang": "兑", "xia": "巽"}
    fuqin_gua_num = BA_GUA_XIAN_TIAN.get(fuqin_bian_gua["shang"], 2) * 100 + BA_GUA_XIAN_TIAN.get(fuqin_bian_gua["xia"], 5)
    
    father_base = LIU_QIN_TYPE_CODES.get("父亲", 1000)
    father_tiaowen1 = father_base + fuqin_gua_num + fu_mu_yong_shen_value
    
    duanyu1 = ""
    if db and hasattr(db, 'FORTUNE_DUANYU_MAP') and father_tiaowen1 in db.FORTUNE_DUANYU_MAP:
        duanyu1, _ = db.FORTUNE_DUANYU_MAP[father_tiaowen1]
    
    father_tiaowen2 = father_tiaowen1 + ying_yao_value
    
    duanyu2 = ""
    if db and hasattr(db, 'FORTUNE_DUANYU_MAP') and father_tiaowen2 in db.FORTUNE_DUANYU_MAP:
        duanyu2, _ = db.FORTUNE_DUANYU_MAP[father_tiaowen2]
    
    father_results.append({
        "desc": "父亲兄弟数",
        "bian_gua": f"{fuqin_bian_gua['shang']}{fuqin_bian_gua['xia']}",
        "gua_num": fuqin_gua_num,
        "yong_shen_value": fu_mu_yong_shen_value,
        "tiaowen_num": father_tiaowen1,
        "duanyu": duanyu1,
        "formula": f"{father_base}+{fuqin_gua_num}+{fu_mu_yong_shen_value}={father_tiaowen1}"
    })
    
    father_results.append({
        "desc": "父亲排行",
        "tiaowen_num": father_tiaowen2,
        "duanyu": duanyu2,
        "formula": f"{father_tiaowen1}+{ying_yao_value}={father_tiaowen2}"
    })
    
    muqin_bian_gua1 = {"shang": "离", "xia": "巽"}
    muqin_gua_num1 = BA_GUA_XIAN_TIAN.get(muqin_bian_gua1["shang"], 3) * 100 + BA_GUA_XIAN_TIAN.get(muqin_bian_gua1["xia"], 5)
    
    mother_base = LIU_QIN_TYPE_CODES.get("母亲", 2000)
    mother_tiaowen1 = mother_base + muqin_gua_num1 + ying_yao_value
    
    duanyu3 = ""
    if db and hasattr(db, 'FORTUNE_DUANYU_MAP') and mother_tiaowen1 in db.FORTUNE_DUANYU_MAP:
        duanyu3, _ = db.FORTUNE_DUANYU_MAP[mother_tiaowen1]
    
    muqin_bian_gua2 = {"shang": "震", "xia": "巽"}
    muqin_gua_num2 = BA_GUA_XIAN_TIAN.get(muqin_bian_gua2["shang"], 4) * 100 + BA_GUA_XIAN_TIAN.get(muqin_bian_gua2["xia"], 5)
    
    mother_tiaowen2 = mother_base + muqin_gua_num2 + ying_yao_value - 30
    
    duanyu4 = ""
    if db and hasattr(db, 'FORTUNE_DUANYU_MAP') and mother_tiaowen2 in db.FORTUNE_DUANYU_MAP:
        duanyu4, _ = db.FORTUNE_DUANYU_MAP[mother_tiaowen2]
    
    mother_results.append({
        "desc": "母亲姐妹数",
        "bian_gua": f"{muqin_bian_gua1['shang']}{muqin_bian_gua1['xia']}",
        "gua_num": muqin_gua_num1,
        "tiaowen_num": mother_tiaowen1,
        "duanyu": duanyu3,
        "formula": f"{mother_base}+{muqin_gua_num1}+{ying_yao_value}={mother_tiaowen1}"
    })
    
    mother_results.append({
        "desc": "母亲排行",
        "bian_gua": f"{muqin_bian_gua2['shang']}{muqin_bian_gua2['xia']}",
        "gua_num": muqin_gua_num2,
        "tiaowen_num": mother_tiaowen2,
        "duanyu": duanyu4,
        "formula": f"{mother_base}+{muqin_gua_num2}+{ying_yao_value}-30={mother_tiaowen2}"
    })
    
    return {
        "tian_gan_num": tian_gan_num,
        "shang_sum": shang_sum,
        "xia_sum": xia_sum,
        "shang_gua": shang_gua,
        "xia_gua": xia_gua,
        "gua_name": gua_name,
        "fu_mu_yong_shen": fu_mu_yong_shen,
        "fu_mu_yong_shen_value": fu_mu_yong_shen_value,
        "ying_yao_value": ying_yao_value,
        "father_results": father_results,
        "mother_results": mother_results,
        "method": "心易派铁板神数兄弟姐妹数计算"
    }

def calculate_spouse_shengxiao(bazi, k_true=None):
    """推算配偶生肖"""
    day_gan_zhi = bazi.get('day', '')
    time_gan_zhi = bazi.get('time', '')
    
    day_gan = day_gan_zhi[0] if len(day_gan_zhi) > 0 else ''
    day_zhi = day_gan_zhi[1] if len(day_gan_zhi) > 1 else ''
    time_zhi = time_gan_zhi[1] if len(time_gan_zhi) > 1 else ''
    
    spouse_candidates = []
    
    he_zhi = LIUHE_PAIRS.get(day_zhi)
    if he_zhi:
        spouse_candidates.append({
            "shengxiao": DI_ZHI_TO_SHENG_XIAO.get(he_zhi, ""),
            "reason": f"日支{day_zhi}六合{he_zhi}"
        })
    
    for group in SANHE_GROUPS:
        if day_zhi in group:
            for zhi in group:
                if zhi != day_zhi:
                    spouse_candidates.append({
                        "shengxiao": DI_ZHI_TO_SHENG_XIAO.get(zhi, ""),
                        "reason": f"日支{day_zhi}三合{zhi}"
                    })
    
    nayin_day = get_nayin(day_gan_zhi)
    wuxing_day = get_nayin_wuxing(day_gan_zhi)
    
    spouse_candidates.append({
        "shengxiao": "综合推算",
        "reason": f"日纳音{nayin_day}({wuxing_day})，配偶属相与日干{day_gan}相配合"
    })
    
    return {
        "spouse": spouse_candidates,
        "nayin_day": nayin_day
    }

__all__ = [
    'calculate_parent_shengxiao',
    'calculate_children_shengxiao',
    'calculate_brother_shengxiao',
    'calculate_xinyi_brother_count',
    'calculate_spouse_shengxiao',
]
