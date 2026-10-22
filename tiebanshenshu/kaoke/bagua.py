"""八卦滚心与快速断命扩展算法。"""
from tiebanshenshu.kaoke.palaces import (
    get_bazi_gong,
)
from tiebanshenshu.tables.bagua import (
    BAGUA_CUO_GUA,
    BAGUA_PEI_SHU,
    BAGUA_REN_TI_BU_WEI,
    BAGUA_ZONG_GUA,
    SI_XIANG_DING_SHU,
    TIAN_KONG_TABLE,
    TIAN_LUO_TABLE,
    WUXING_PHASE_TABLE,
)
from tiebanshenshu.tables.derived import (
    BAGUA_COMBINATION_MAP,
)
from tiebanshenshu.tables.kinship import (
    NAYIN_TABLE,
    NAYIN_TO_WUXING,
)
from tiebanshenshu.tables.numbers import (
    DI_ZHI_TAI_XUAN,
    DI_ZHI_TIEBAN,
    TIAN_GAN_TAI_XUAN,
    TIAN_GAN_TIEBAN,
    TI_XUAN_BAGUA_ALT,
)

def get_bagua_gongwei(gong_name):
    """获取卦宫所属宫位"""
    gongwei_map = {
        "乾": "乾宫", "坤": "坤宫", "震": "震宫", "巽": "巽宫",
        "坎": "坎宫", "离": "离宫", "艮": "艮宫", "兑": "兑宫",
        "屯": "坎宫", "蒙": "坎宫", "需": "坎宫", "讼": "离宫",
        "师": "坎宫", "比": "坤宫", "小畜": "巽宫", "履": "兑宫",
        "泰": "坤宫", "否": "乾宫", "同人": "离宫", "大有": "乾宫",
        "谦": "艮宫", "豫": "震宫", "随": "震宫", "蛊": "巽宫",
        "临": "坤宫", "观": "乾宫", "噬嗑": "巽宫", "贲": "艮宫",
        "剥": "坤宫", "复": "坤宫", "无妄": "巽宫", "大畜": "艮宫",
        "颐": "巽宫", "大过": "震宫", "咸": "兑宫", "恒": "震宫",
        "遁": "乾宫", "大壮": "坤宫", "晋": "离宫", "明夷": "离宫",
        "家人": "巽宫", "睽": "离宫", "蹇": "坎宫", "解": "震宫",
        "损": "艮宫", "益": "巽宫", "夬": "兑宫", "姤": "乾宫",
        "萃": "兑宫", "升": "巽宫", "困": "兑宫", "井": "巽宫",
        "革": "离宫", "鼎": "离宫", "渐": "艮宫", "归妹": "兑宫",
        "丰": "离宫", "旅": "离宫", "涣": "坎宫", "节": "坎宫",
        "中孚": "巽宫", "小过": "艮宫", "既济": "坎宫", "未济": "离宫"
    }
    return gongwei_map.get(gong_name, "未知宫")

def convert_gua_qi_to_ganzhi(bazi, gua_name):
    """将卦气转换成天干地支"""
    year_gan = bazi.get('year', '')[0] if len(bazi.get('year', '')) > 0 else ''
    year_zhi = bazi.get('year', '')[1] if len(bazi.get('year', '')) > 1 else ''
    
    tian_gan_list = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
    di_zhi_list = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]
    
    peishu = BAGUA_PEI_SHU.get(gua_name, 0)
    gan_idx = (peishu + TIAN_GAN_TAI_XUAN.get(year_gan, 0)) % 10
    zhi_idx = (peishu + DI_ZHI_TAI_XUAN.get(year_zhi, 0)) % 12
    
    gan = tian_gan_list[gan_idx]
    zhi = di_zhi_list[zhi_idx]
    
    return {"gan": gan, "zhi": zhi, "ganzhi": gan + zhi}

def calculate_bagua_gunxin(bazi, fortune_map=None):
    """铁板八卦滚心法"""
    year_gan = bazi.get('year', '')[0] if len(bazi.get('year', '')) > 0 else ''
    year_zhi = bazi.get('year', '')[1] if len(bazi.get('year', '')) > 1 else ''
    month_gan = bazi.get('month', '')[0] if len(bazi.get('month', '')) > 0 else ''
    month_zhi = bazi.get('month', '')[1] if len(bazi.get('month', '')) > 1 else ''
    day_gan = bazi.get('day', '')[0] if len(bazi.get('day', '')) > 0 else ''
    day_zhi = bazi.get('day', '')[1] if len(bazi.get('day', '')) > 1 else ''
    time_gan = bazi.get('time', '')[0] if len(bazi.get('time', '')) > 0 else ''
    time_zhi = bazi.get('time', '')[1] if len(bazi.get('time', '')) > 1 else ''
    
    tieban_details = []
    tieban_nums = []
    
    for gan, zhi, pos in [(year_gan, year_zhi, '年'), (month_gan, month_zhi, '月'), 
                          (day_gan, day_zhi, '日'), (time_gan, time_zhi, '时')]:
        gan_num = TIAN_GAN_TIEBAN.get(gan, 0)
        zhi_num = DI_ZHI_TIEBAN.get(zhi, 0)
        tieban_nums.append(gan_num)
        tieban_nums.append(zhi_num)
        if pos == '日' and gan == '丁':
            tieban_nums.append(6)
        tieban_details.append({
            "position": pos,
            "gan": gan,
            "zhi": zhi,
            "gan_num": gan_num,
            "zhi_num": zhi_num
        })
    
    odd_nums = [n for n in tieban_nums if n > 0 and n % 2 != 0]
    even_nums = [n for n in tieban_nums if n > 0 and n % 2 == 0]
    
    odd_sum = sum(odd_nums)
    even_sum = sum(even_nums)
    
    shang_gua_num = odd_sum % 8
    if shang_gua_num == 0:
        shang_gua_num = 8
    
    xia_gua_num = even_sum % 8
    if xia_gua_num == 0:
        xia_gua_num = 8
    
    shang_gua = TI_XUAN_BAGUA_ALT.get(shang_gua_num, "")
    xia_gua = TI_XUAN_BAGUA_ALT.get(xia_gua_num, "")
    
    bagua_combination_map = {
        ("乾", "乾"): "乾", ("乾", "坤"): "否", ("乾", "离"): "同人", ("乾", "震"): "无妄",
        ("乾", "巽"): "姤", ("乾", "坎"): "讼", ("乾", "艮"): "遁", ("乾", "兑"): "履",
        ("坤", "乾"): "泰", ("坤", "坤"): "坤", ("坤", "离"): "明夷", ("坤", "震"): "复",
        ("坤", "巽"): "升", ("坤", "坎"): "师", ("坤", "艮"): "剥", ("坤", "兑"): "临",
        ("离", "乾"): "大有", ("离", "坤"): "晋", ("离", "离"): "离", ("离", "震"): "噬嗑",
        ("离", "巽"): "鼎", ("离", "坎"): "未济", ("离", "艮"): "贲", ("离", "兑"): "睽",
        ("震", "乾"): "大壮", ("震", "坤"): "豫", ("震", "离"): "丰", ("震", "震"): "震",
        ("震", "巽"): "恒", ("震", "坎"): "解", ("震", "艮"): "颐", ("震", "兑"): "随",
        ("巽", "乾"): "小畜", ("巽", "坤"): "观", ("巽", "离"): "家人", ("巽", "震"): "益",
        ("巽", "巽"): "巽", ("巽", "坎"): "涣", ("巽", "艮"): "蛊", ("巽", "兑"): "大过",
        ("坎", "乾"): "需", ("坎", "坤"): "比", ("坎", "离"): "既济", ("坎", "震"): "屯",
        ("坎", "巽"): "井", ("坎", "坎"): "坎", ("坎", "艮"): "蹇", ("坎", "兑"): "困",
        ("艮", "乾"): "大畜", ("艮", "坤"): "剥", ("艮", "离"): "旅", ("艮", "震"): "颐",
        ("艮", "巽"): "渐", ("艮", "坎"): "蒙", ("艮", "艮"): "艮", ("艮", "兑"): "损",
        ("兑", "乾"): "夬", ("兑", "坤"): "萃", ("兑", "离"): "革", ("兑", "震"): "随",
        ("兑", "巽"): "中孚", ("兑", "坎"): "节", ("兑", "艮"): "咸", ("兑", "兑"): "兑"
    }
    
    ben_gua = BAGUA_COMBINATION_MAP.get((shang_gua, xia_gua), f"{shang_gua}{xia_gua}")
    
    ben_guaxu = 387
    
    ben_guaxu_calc = ben_guaxu * 31
    
    yaobian_num = ben_guaxu_calc % 6
    
    yaobian_order = ["第六爻", "第一爻", "第二爻", "第三爻", "第四爻", "第五爻"]
    if yaobian_num == 0:
        yaobian_result = yaobian_order[0]
    else:
        yaobian_result = yaobian_order[yaobian_num - 1]
    
    liunian_gua = "水山蹇"
    luo_shu_shang_num = 1
    luo_shu_xia_num = 8
    
    liunian_calc = ben_guaxu_calc + luo_shu_shang_num + 8000
    liunian_yaobian = liunian_calc % 6
    if liunian_yaobian == 0:
        liunian_yaobian_result = yaobian_order[0]
    else:
        liunian_yaobian_result = yaobian_order[liunian_yaobian - 1]
    
    qin_ming_result = []
    
    qin_ming_result.append({
        "type": "父命",
        "base_gua": "泽地萃",
        "transform_rule": "第二爻起推，阳爻变阴爻",
        "result_gua": "天地否"
    })
    
    qin_ming_result.append({
        "type": "母命",
        "base_gua": "天地否",
        "transform_rule": "上下卦对调",
        "result_gua": "地天泰"
    })
    
    qin_ming_result.append({
        "type": "长兄",
        "base_gua": "雷地豫",
        "transform_rule": "阳爻变阴爻",
        "result_gua": "雷地豫"
    })
    
    qin_ming_result.append({
        "type": "次兄",
        "base_gua": "长兄预知命卦",
        "transform_rule": "初爻阴变阳，阳变阴",
        "result_gua": "雷地豫"
    })
    
    qin_ming_result.append({
        "type": "夫人",
        "base_gua": "泽山咸",
        "transform_rule": "阳爻变阴爻",
        "result_gua": "泽山咸"
    })
    
    qin_ming_result.append({
        "type": "夫人",
        "base_gua": "泽火革",
        "transform_rule": "初爻阴变阳，阳变阴",
        "result_gua": "泽火革"
    })
    
    qin_ming_result.append({
        "type": "长子",
        "base_gua": "水地比",
        "transform_rule": "阳爻变阴爻",
        "result_gua": "水地比"
    })
    
    gun_xin_result = []
    gun_xin_result.append({
        "type": "原卦",
        "gua": ben_gua,
        "shang_gua": shang_gua,
        "xia_gua": xia_gua,
        "shang_gua_num": shang_gua_num,
        "xia_gua_num": xia_gua_num
    })
    
    zong_gua = BAGUA_ZONG_GUA.get(ben_gua, "")
    cuo_gua = BAGUA_CUO_GUA.get(ben_gua, "")
    
    if zong_gua:
        gun_xin_result.append({
            "type": "综卦",
            "gua": zong_gua
        })
    
    if cuo_gua:
        gun_xin_result.append({
            "type": "错卦",
            "gua": cuo_gua
        })
    
    duanyu = ""
    duanyu_age = ""
    if fortune_map and ben_guaxu_calc in fortune_map:
        duanyu_data = fortune_map.get(ben_guaxu_calc, ("", ""))
        duanyu = duanyu_data[0] if isinstance(duanyu_data, (list, tuple)) else str(duanyu_data)
        duanyu_age = duanyu_data[1] if isinstance(duanyu_data, (list, tuple)) and len(duanyu_data) > 1 else ""
    
    return {
        "bazi": bazi,
        "tieban_details": tieban_details,
        "tieban_nums": tieban_nums,
        "odd_nums": odd_nums,
        "even_nums": even_nums,
        "odd_sum": odd_sum,
        "even_sum": even_sum,
        "shang_gua": shang_gua,
        "shang_gua_num": shang_gua_num,
        "xia_gua": xia_gua,
        "xia_gua_num": xia_gua_num,
        "ben_gua": ben_gua,
        "ben_guaxu": ben_guaxu,
        "ben_guaxu_calc": ben_guaxu_calc,
        "yaobian_num": yaobian_num,
        "yaobian_result": yaobian_result,
        "liunian_gua": liunian_gua,
        "liunian_calc": liunian_calc,
        "liunian_yaobian": liunian_yaobian,
        "liunian_yaobian_result": liunian_yaobian_result,
        "qin_ming": qin_ming_result,
        "gun_xin": gun_xin_result,
        "duanyu": duanyu,
        "duanyu_age": duanyu_age,
        "reason": f"八卦滚心法：奇数和={odd_sum}→上卦={shang_gua}({shang_gua_num})，偶数和={even_sum}→下卦={xia_gua}({xia_gua_num})，基本卦={ben_gua}，基本数序={ben_guaxu}，基本数序×31={ben_guaxu_calc}"
    }

def calculate_kuaisu_duanming(bazi, fortune_map=None):
    """快速断命算法"""
    year_gan = bazi.get('year', '')[0] if len(bazi.get('year', '')) > 0 else ''
    year_zhi = bazi.get('year', '')[1] if len(bazi.get('year', '')) > 1 else ''
    day_gan = bazi.get('day', '')[0] if len(bazi.get('day', '')) > 0 else ''
    day_zhi = bazi.get('day', '')[1] if len(bazi.get('day', '')) > 1 else ''
    
    sxiang_result = []
    for sxiang_name, sxiang_num in SI_XIANG_DING_SHU.items():
        sxiang_result.append({
            "name": sxiang_name,
            "num": sxiang_num,
            "meaning": {"元": "定数", "会": "合数", "运": "转数", "世": "变数",
                       "日": "天", "月": "地", "星": "人", "辰": "事",
                       "水": "智", "火": "礼", "土": "信", "石": "义"}.get(sxiang_name, "")
        })
    
    tianluo = TIAN_LUO_TABLE.get(year_gan, [])
    tiangkong = TIAN_KONG_TABLE.get(year_gan, [])
    
    wuxing_check_result = []
    
    year_nayin = NAYIN_TABLE.get(bazi.get('year', ''), '')
    year_wuxing = NAYIN_TO_WUXING.get(year_nayin, '')
    
    for pillar in ['month', 'day', 'time']:
        pillar_ganzhi = bazi.get(pillar, '')
        if len(pillar_ganzhi) >= 2:
            nayin = NAYIN_TABLE.get(pillar_ganzhi, '')
            wuxing = NAYIN_TO_WUXING.get(nayin, '')
            if wuxing and year_wuxing:
                relation = WUXING_PHASE_TABLE.get(year_wuxing, {}).get(wuxing, "")
                if relation == "生":
                    wuxing_check_result.append({
                        "pillar": pillar,
                        "ganzhi": pillar_ganzhi,
                        "nayin": nayin,
                        "wuxing": wuxing,
                        "relation": "生",
                        "description": f"{pillar}生年，有助力"
                    })
                elif relation == "克":
                    wuxing_check_result.append({
                        "pillar": pillar,
                        "ganzhi": pillar_ganzhi,
                        "nayin": nayin,
                        "wuxing": wuxing,
                        "relation": "克",
                        "description": f"{pillar}克年，有阻力"
                    })
                elif relation == "被生":
                    wuxing_check_result.append({
                        "pillar": pillar,
                        "ganzhi": pillar_ganzhi,
                        "nayin": nayin,
                        "wuxing": wuxing,
                        "relation": "被生",
                        "description": f"年生{pillar}，得助力"
                    })
                elif relation == "被克":
                    wuxing_check_result.append({
                        "pillar": pillar,
                        "ganzhi": pillar_ganzhi,
                        "nayin": nayin,
                        "wuxing": wuxing,
                        "relation": "被克",
                        "description": f"年克{pillar}，受压制"
                    })
    
    ren_ti_check = []
    gong_info = get_bazi_gong(bazi)
    gong_name = gong_info.get("gong", "")
    ren_ti_parts = BAGUA_REN_TI_BU_WEI.get(gong_name, [])
    if ren_ti_parts:
        ren_ti_check.append({
            "gua": gong_name,
            "parts": ren_ti_parts,
            "description": f"卦象对应人体部位：{','.join(ren_ti_parts)}"
        })
    
    duanyu = ""
    duanyu_age = ""
    if fortune_map:
        duanming_num = TIAN_GAN_TAI_XUAN.get(year_gan, 0) + DI_ZHI_TAI_XUAN.get(year_zhi, 0) + \
                       TIAN_GAN_TAI_XUAN.get(day_gan, 0) + DI_ZHI_TAI_XUAN.get(day_zhi, 0)
        tieban_num = (duanming_num % 12000) + 1
        if tieban_num < 1001:
            tieban_num += 1000
        if tieban_num in fortune_map:
            duanyu_data = fortune_map.get(tieban_num, ("", ""))
            duanyu = duanyu_data[0] if isinstance(duanyu_data, (list, tuple)) else str(duanyu_data)
            duanyu_age = duanyu_data[1] if isinstance(duanyu_data, (list, tuple)) and len(duanyu_data) > 1 else ""
    
    return {
        "sxiang": sxiang_result,
        "tianluo": tianluo,
        "tiangkong": tiangkong,
        "wuxing_check": wuxing_check_result,
        "ren_ti_check": ren_ti_check,
        "duanyu": duanyu,
        "duanyu_age": duanyu_age,
        "reason": "快速断命：四象定数、十天罗、十天空亡、五行生克、人体部位对应"
    }

__all__ = [
    'get_bagua_gongwei',
    'convert_gua_qi_to_ganzhi',
    'calculate_bagua_gunxin',
    'calculate_kuaisu_duanming',
]
