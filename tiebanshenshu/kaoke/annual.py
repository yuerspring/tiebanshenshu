"""流年与百岁配数扩展算法。"""
from tiebanshenshu.kaoke.palaces import (
    get_bazi_gong,
)
from tiebanshenshu.tables.derived import (
    HE_LUO_DI_ZHI,
    HE_LUO_TIAN_GAN,
)
from tiebanshenshu.tables.kinship import (
    LIU_NIAN_PEI_SHU_BIAO,
)
from tiebanshenshu.tables.numbers import (
    DI_ZHI_ORDER,
    TIAN_GAN_TAI_XUAN,
)

def calculate_liunian_zai_e(bazi, age_range=range(1, 21), fortune_map=None):
    """铁板流年灾厄直断法"""
    year_gan_zhi = bazi.get('year', '')
    if len(year_gan_zhi) < 2:
        return {"result": {}, "reason": "年柱信息不足"}
    
    gong_info = get_bazi_gong(bazi)
    gong_name = gong_info.get("gong", "")
    gong_name_simple = gong_name.replace("宫", "") if "宫" in gong_name else gong_name
    
    liunian_result = []
    
    for age in age_range:
        gan_index = (TIAN_GAN_TAI_XUAN.get(year_gan_zhi[0], 0) + age - 1) % 10
        zhi_index = (DI_ZHI_ORDER.get(year_gan_zhi[1], 1) + age - 1) % 12
        if zhi_index == 0:
            zhi_index = 12
        
        tian_gan_list = list(TIAN_GAN_TAI_XUAN.keys())
        di_zhi_list = list(DI_ZHI_ORDER.keys())
        
        cur_gan = tian_gan_list[gan_index % 10]
        cur_zhi = di_zhi_list[zhi_index - 1]
        cur_nian = cur_gan + cur_zhi
        
        peishu1 = LIU_NIAN_PEI_SHU_BIAO.get("六十四卦圆图配数", {}).get(gong_name_simple, 0)
        peishu2 = LIU_NIAN_PEI_SHU_BIAO.get("六十四卦配数秘表一", {}).get(gong_name_simple, 0)
        peishu3 = LIU_NIAN_PEI_SHU_BIAO.get("六十四卦配数秘表二", {}).get(gong_name_simple, 0)
        peishu4 = LIU_NIAN_PEI_SHU_BIAO.get("太极八卦配数秘表", {}).get(gong_name_simple, 0)
        peishu5 = LIU_NIAN_PEI_SHU_BIAO.get("六十甲子流年配数秘表", {}).get(cur_nian, 0)
        peishu6 = LIU_NIAN_PEI_SHU_BIAO.get("百流流年配数秘表", {}).get(age, 0)
        
        zong_peishu = peishu1 + peishu2 + peishu3 + peishu4 + peishu5 + peishu6
        
        duanyu = ""
        duanyu_age = ""
        if fortune_map:
            tieban_num = (zong_peishu % 12000) + 1
            if tieban_num > 12000:
                tieban_num = tieban_num % 12000 + 1
            if tieban_num < 1001:
                tieban_num = tieban_num + 1000
            
            if tieban_num in fortune_map:
                duanyu_data = fortune_map.get(tieban_num, ("", ""))
                duanyu = duanyu_data[0] if isinstance(duanyu_data, (list, tuple)) else str(duanyu_data)
                duanyu_age = duanyu_data[1] if isinstance(duanyu_data, (list, tuple)) and len(duanyu_data) > 1 else ""
            elif zong_peishu in fortune_map:
                duanyu_data = fortune_map.get(zong_peishu, ("", ""))
                duanyu = duanyu_data[0] if isinstance(duanyu_data, (list, tuple)) else str(duanyu_data)
                duanyu_age = duanyu_data[1] if isinstance(duanyu_data, (list, tuple)) and len(duanyu_data) > 1 else ""
            else:
                zai_e_index = zong_peishu % 20
                if zai_e_index == 0:
                    zai_e_index = 20
                zai_e_info = LIU_NIAN_PEI_SHU_BIAO.get("百流流年灾厄秘表", {}).get(zai_e_index, {})
                duanyu = zai_e_info.get("断语", "")
        else:
            zai_e_index = zong_peishu % 20
            if zai_e_index == 0:
                zai_e_index = 20
            zai_e_info = LIU_NIAN_PEI_SHU_BIAO.get("百流流年灾厄秘表", {}).get(zai_e_index, {})
            duanyu = zai_e_info.get("断语", "")
        
        liunian_result.append({
            "age": age,
            "nian": cur_nian,
            "pei_shu_list": [peishu1, peishu2, peishu3, peishu4, peishu5, peishu6],
            "zong_peishu": zong_peishu,
            "duanyu": duanyu,
            "duanyu_age": duanyu_age
        })
    
    return {
        "gong": gong_name,
        "year": year_gan_zhi,
        "liunian": liunian_result,
        "reason": "使用七种配数秘表推算流年灾厄"
    }

def calculate_baisui_liunian_peishu(bazi):
    """百岁流年配数秘法：计算每年运势变化"""
    year_gan = bazi.get('year', '')[0] if len(bazi.get('year', '')) > 0 else ''
    year_zhi = bazi.get('year', '')[1] if len(bazi.get('year', '')) > 1 else ''
    day_gan = bazi.get('day', '')[0] if len(bazi.get('day', '')) > 0 else ''
    day_zhi = bazi.get('day', '')[1] if len(bazi.get('day', '')) > 1 else ''
    
    ming_gan_num = HE_LUO_TIAN_GAN.get(day_gan, 0)
    ming_zhi_num = HE_LUO_DI_ZHI.get(day_zhi, 0)
    nian_gan_num = HE_LUO_TIAN_GAN.get(year_gan, 0)
    nian_zhi_num = HE_LUO_DI_ZHI.get(year_zhi, 0)
    
    ben_guaxu = 387
    ben_guaxu_calc = ben_guaxu * 31
    
    liunian_results = []
    
    for age in range(1, 101):
        liunian_num = ben_guaxu_calc + age * 100
        liunian_yaobian = liunian_num % 6
        if liunian_yaobian == 0:
            liunian_yaobian = 6
        
        yaobian_order = ["第六爻", "第一爻", "第二爻", "第三爻", "第四爻", "第五爻"]
        yaobian_result = yaobian_order[liunian_yaobian - 1]
        
        liunian_results.append({
            "age": age,
            "liunian_num": liunian_num,
            "yaobian": liunian_yaobian,
            "yaobian_result": yaobian_result
        })
    
    return {
        "bazi": bazi,
        "ben_guaxu": ben_guaxu,
        "ben_guaxu_calc": ben_guaxu_calc,
        "liunian_results": liunian_results,
        "reason": f"百岁流年配数秘法：基本数序={ben_guaxu}, 基本数序×31={ben_guaxu_calc}"
    }

def calculate_baisui_liunian_zai_e(bazi, age_range=range(1, 101)):
    """百岁流年灾厄秘法：计算每年灾厄"""
    year_gan = bazi.get('year', '')[0] if len(bazi.get('year', '')) > 0 else ''
    year_zhi = bazi.get('year', '')[1] if len(bazi.get('year', '')) > 1 else ''
    day_gan = bazi.get('day', '')[0] if len(bazi.get('day', '')) > 0 else ''
    day_zhi = bazi.get('day', '')[1] if len(bazi.get('day', '')) > 1 else ''
    
    ming_gan_num = HE_LUO_TIAN_GAN.get(day_gan, 0)
    ming_zhi_num = HE_LUO_DI_ZHI.get(day_zhi, 0)
    
    ben_guaxu = 387
    ben_guaxu_calc = ben_guaxu * 31
    
    zai_e_results = []
    
    for age in age_range:
        zai_e_num = ben_guaxu_calc + age * 100 + 8000
        zai_e_yaobian = zai_e_num % 6
        if zai_e_yaobian == 0:
            zai_e_yaobian = 6
        
        yaobian_order = ["第六爻", "第一爻", "第二爻", "第三爻", "第四爻", "第五爻"]
        yaobian_result = yaobian_order[zai_e_yaobian - 1]
        
        zai_e_level = ""
        if zai_e_yaobian in [1, 6]:
            zai_e_level = "大灾"
        elif zai_e_yaobian in [2, 5]:
            zai_e_level = "中灾"
        else:
            zai_e_level = "小灾"
        
        zai_e_results.append({
            "age": age,
            "zai_e_num": zai_e_num,
            "yaobian": zai_e_yaobian,
            "yaobian_result": yaobian_result,
            "zai_e_level": zai_e_level
        })
    
    return {
        "bazi": bazi,
        "ben_guaxu": ben_guaxu,
        "ben_guaxu_calc": ben_guaxu_calc,
        "zai_e_results": zai_e_results,
        "reason": f"百岁流年灾厄秘法：基本数序={ben_guaxu}, 基本数序×31={ben_guaxu_calc}"
    }

__all__ = [
    'calculate_liunian_zai_e',
    'calculate_baisui_liunian_peishu',
    'calculate_baisui_liunian_zai_e',
]
