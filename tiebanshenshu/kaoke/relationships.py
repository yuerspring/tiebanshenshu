"""纳音、刑、合、空等共用判断。"""
from tiebanshenshu.tables.kinship import (
    LIUHE_PAIRS,
    NAYIN_TABLE,
    NAYIN_TO_WUXING,
    PO_KONG_ZHI,
    SANHE_GROUPS,
    SI_ZHI_XING,
)

def get_nayin(gan_zhi):
    """获取干支的纳音"""
    return NAYIN_TABLE.get(gan_zhi, "")

def get_nayin_wuxing(gan_zhi):
    """获取干支纳音的五行"""
    nayin = get_nayin(gan_zhi)
    return NAYIN_TO_WUXING.get(nayin, "")

def check_xing(zhi1, zhi2):
    """检查两地支是否相刑"""
    return zhi2 in SI_ZHI_XING.get(zhi1, [])

def check_pokong(bazi):
    """检查八字是否犯四直刑破空"""
    year_gan_zhi = bazi.get('year', '')
    month_gan_zhi = bazi.get('month', '')
    day_gan_zhi = bazi.get('day', '')
    time_gan_zhi = bazi.get('time', '')
    
    year_zhi = year_gan_zhi[1] if len(year_gan_zhi) > 1 else ''
    month_zhi = month_gan_zhi[1] if len(month_gan_zhi) > 1 else ''
    day_zhi = day_gan_zhi[1] if len(day_gan_zhi) > 1 else ''
    time_zhi = time_gan_zhi[1] if len(time_gan_zhi) > 1 else ''
    
    pokong_info = {
        "has_xing": False,
        "xing_details": [],
        "has_pokong": False,
        "pokong_details": []
    }
    
    zhi_list = [year_zhi, month_zhi, day_zhi, time_zhi]
    for i, z1 in enumerate(zhi_list):
        for j, z2 in enumerate(zhi_list):
            if i != j and z1 and z2:
                if check_xing(z1, z2):
                    pokong_info["has_xing"] = True
                    pokong_info["xing_details"].append(f"{z1}刑{z2}")
    
    for yuan, kong_zhi_list in PO_KONG_ZHI.items():
        for zhi in zhi_list:
            if zhi and zhi in kong_zhi_list:
                pokong_info["has_pokong"] = True
                pokong_info["pokong_details"].append(f"{yuan}旬空{zhi}")
    
    return pokong_info

def check_sanhe(zhi1, zhi2):
    """检查两地支是否三合"""
    for group in SANHE_GROUPS:
        if zhi1 in group and zhi2 in group:
            return True, group
    return False, None

def check_liuhe(zhi1, zhi2):
    """检查两地支是否六合"""
    return LIUHE_PAIRS.get(zhi1) == zhi2

__all__ = [
    'get_nayin',
    'get_nayin_wuxing',
    'check_xing',
    'check_pokong',
    'check_sanhe',
    'check_liuhe',
]
