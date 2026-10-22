"""命宫、六亲宫位与卦气转换。"""
from tiebanshenshu.tables.kinship import (
    BA_GONG_NA_JIA,
    DI_ZHI_TO_SHENG_XIAO,
    E_SHEN,
    GAN_XING,
    GONG_WEI_LIU_QIN,
    JI_SHEN,
    LIU_QIN_GONG_WEI,
    WU_XING_SHEENG_KILL,
)
from tiebanshenshu.tables.numbers import (
    DI_ZHI_ORDER,
)

def calculate_ming_gong(bazi):
    """推算命宫"""
    day_gan_zhi = bazi.get('day', '')
    time_gan_zhi = bazi.get('time', '')
    
    if len(day_gan_zhi) < 2 or len(time_gan_zhi) < 2:
        return {"ming_gong": "", "reason": "数据不足"}
    
    day_zhi = day_gan_zhi[1]
    time_zhi = time_gan_zhi[1]
    
    day_order = DI_ZHI_ORDER.get(day_zhi, 1)
    time_order = DI_ZHI_ORDER.get(time_zhi, 1)
    
    ming_gong_order = (day_order + time_order - 2) % 12 + 1
    
    for zhi, order in DI_ZHI_ORDER.items():
        if order == ming_gong_order:
            ming_gong_zhi = zhi
            break
    else:
        ming_gong_zhi = "子"
    
    return {
        "ming_gong": ming_gong_zhi,
        "ming_gong_shengxiao": DI_ZHI_TO_SHENG_XIAO.get(ming_gong_zhi, ""),
        "reason": f"命宫 = (日支{day_zhi} + 时支{time_zhi}) / 2 = {ming_gong_zhi}"
    }

def get_gongwei_by_minggong(ming_gong_zhi):
    """根据命宫推算各宫位"""
    ming_gong_order = DI_ZHI_ORDER.get(ming_gong_zhi, 1)
    
    gongwei_result = {}
    for gongwei_name, offset in LIU_QIN_GONG_WEI.items():
        order = (ming_gong_order + offset - 1) % 12
        if order == 0:
            order = 12
        for zhi, zhi_order in DI_ZHI_ORDER.items():
            if zhi_order == order:
                gongwei_result[gongwei_name] = {
                    "zhi": zhi,
                    "shengxiao": DI_ZHI_TO_SHENG_XIAO.get(zhi, ""),
                    "order": order
                }
                break
    
    return gongwei_result

def check_ji_e_shen(bazi):
    """检查八字中的吉神与恶神"""
    gan_list = [bazi.get('year', '')[0] if len(bazi.get('year', '')) > 0 else '',
                bazi.get('month', '')[0] if len(bazi.get('month', '')) > 0 else '',
                bazi.get('day', '')[0] if len(bazi.get('day', '')) > 0 else '',
                bazi.get('time', '')[0] if len(bazi.get('time', '')) > 0 else '']
    
    zhi_list = [bazi.get('year', '')[1] if len(bazi.get('year', '')) > 1 else '',
                bazi.get('month', '')[1] if len(bazi.get('month', '')) > 1 else '',
                bazi.get('day', '')[1] if len(bazi.get('day', '')) > 1 else '',
                bazi.get('time', '')[1] if len(bazi.get('time', '')) > 1 else '']
    
    ji_shen_result = {}
    e_shen_result = {}
    
    for shen_name, positions in JI_SHEN.items():
        found_in_gan = []
        found_in_zhi = []
        for i, gan in enumerate(gan_list):
            if gan and i < len(positions):
                if gan == positions[i]:
                    found_in_gan.append(f"{bazi.get('year', '')[0]+bazi.get('year', '')[1] if len(bazi.get('year', ''))>1 else ''}")
        
        for zhi in zhi_list:
            if zhi in positions:
                found_in_zhi.append(zhi)
        
        if found_in_gan or found_in_zhi:
            ji_shen_result[shen_name] = {
                "gan": found_in_gan,
                "zhi": found_in_zhi
            }
    
    for shen_name, positions in E_SHEN.items():
        found_in_gan = []
        found_in_zhi = []
        for i, gan in enumerate(gan_list):
            if gan and i < len(positions):
                if gan == positions[i]:
                    found_in_gan.append(gan)
        
        for zhi in zhi_list:
            if zhi in positions:
                found_in_zhi.append(zhi)
        
        if found_in_gan or found_in_zhi:
            e_shen_result[shen_name] = {
                "gan": found_in_gan,
                "zhi": found_in_zhi
            }
    
    return {
        "ji_shen": ji_shen_result,
        "e_shen": e_shen_result,
        "has_ji_shen": len(ji_shen_result) > 0,
        "has_e_shen": len(e_shen_result) > 0
    }

def calculate_yong_shen(bazi):
    """推算用神"""
    day_gan = bazi.get('day', '')[0] if len(bazi.get('day', '')) > 0 else ''
    
    if not day_gan:
        return {"yong_shen": [], "reason": "日主不明"}
    
    day_wuxing = GAN_XING.get(day_gan, {}).get("wuxing", "")
    
    wuxing_count = {"木": 0, "火": 0, "土": 0, "金": 0, "水": 0}
    
    for key in ['year', 'month', 'day', 'time']:
        gan_zhi = bazi.get(key, '')
        if len(gan_zhi) >= 2:
            gan = gan_zhi[0]
            wuxing = GAN_XING.get(gan, {}).get("wuxing", "")
            if wuxing:
                wuxing_count[wuxing] += 1
    
    max_wuxing = max(wuxing_count, key=wuxing_count.get)
    min_wuxing = min(wuxing_count, key=wuxing_count.get)
    
    yong_shen_candidates = []
    
    if WU_XING_SHEENG_KILL.get(min_wuxing, {}).get('kill') == max_wuxing:
        yong_shen_candidates.append(min_wuxing)
    
    yong_shen_candidates.append(WU_XING_SHEENG_KILL.get(max_wuxing, {}).get('kill', ''))
    
    yong_shen_candidates = [w for w in yong_shen_candidates if w]
    
    return {
        "yong_shen": yong_shen_candidates,
        "day_wuxing": day_wuxing,
        "wuxing_count": wuxing_count,
        "reason": f"日主{day_gan}属{day_wuxing}，五行分布:木{wuxing_count['木']}火{wuxing_count['火']}土{wuxing_count['土']}金{wuxing_count['金']}水{wuxing_count['水']}"
    }

def convert_gua_qi(bazi, target_liuqin):
    """卦气转换：将本人命盘转换为六亲预知命盘"""
    day_gan = bazi.get('day', '')[0] if len(bazi.get('day', '')) > 0 else ''
    
    if not day_gan:
        return {"result": {}, "reason": "日主不明"}
    
    day_wuxing = GAN_XING.get(day_gan, {}).get("wuxing", "")
    yong_shen_info = calculate_yong_shen(bazi)
    yong_shen = yong_shen_info.get("yong_shen", [])
    
    liuqin_gan_list = []
    
    if target_liuqin == "父亲":
        if day_wuxing == "木":
            liuqin_gan_list = ["戊", "己"]
        elif day_wuxing == "火":
            liuqin_gan_list = ["庚", "辛"]
        elif day_wuxing == "土":
            liuqin_gan_list = ["壬", "癸"]
        elif day_wuxing == "金":
            liuqin_gan_list = ["甲", "乙"]
        elif day_wuxing == "水":
            liuqin_gan_list = ["丙", "丁"]
    
    elif target_liuqin == "母亲":
        if day_wuxing == "木":
            liuqin_gan_list = ["壬", "癸"]
        elif day_wuxing == "火":
            liuqin_gan_list = ["甲", "乙"]
        elif day_wuxing == "土":
            liuqin_gan_list = ["丙", "丁"]
        elif day_wuxing == "金":
            liuqin_gan_list = ["戊", "己"]
        elif day_wuxing == "水":
            liuqin_gan_list = ["庚", "辛"]
    
    elif target_liuqin == "配偶":
        if GAN_XING.get(day_gan, {}).get("阳", True):
            liuqin_gan_list = ["乙", "己"]
        else:
            liuqin_gan_list = ["甲", "戊"]
    
    elif target_liuqin == "子女":
        if GAN_XING.get(day_gan, {}).get("阳", True):
            if day_wuxing == "木":
                liuqin_gan_list = ["丙", "丁"]
            elif day_wuxing == "火":
                liuqin_gan_list = ["戊", "己"]
            elif day_wuxing == "土":
                liuqin_gan_list = ["庚", "辛"]
            elif day_wuxing == "金":
                liuqin_gan_list = ["壬", "癸"]
            elif day_wuxing == "水":
                liuqin_gan_list = ["甲", "乙"]
        else:
            if day_wuxing == "木":
                liuqin_gan_list = ["丁", "丙"]
            elif day_wuxing == "火":
                liuqin_gan_list = ["己", "戊"]
            elif day_wuxing == "土":
                liuqin_gan_list = ["辛", "庚"]
            elif day_wuxing == "金":
                liuqin_gan_list = ["癸", "壬"]
            elif day_wuxing == "水":
                liuqin_gan_list = ["乙", "甲"]
    
    elif target_liuqin == "兄弟":
        if GAN_XING.get(day_gan, {}).get("阳", True):
            liuqin_gan_list = [day_gan]
        else:
            liuqin_gan_list = [day_gan]
    
    converted_bazi = {}
    for key in ['year', 'month', 'day', 'time']:
        gan_zhi = bazi.get(key, '')
        if len(gan_zhi) >= 2:
            zhi = gan_zhi[1]
            if liuqin_gan_list:
                converted_bazi[key] = liuqin_gan_list[0] + zhi
            else:
                converted_bazi[key] = gan_zhi
    
    return {
        "original_bazi": bazi,
        "converted_bazi": converted_bazi,
        "target_liuqin": target_liuqin,
        "liuqin_gan": liuqin_gan_list[0] if liuqin_gan_list else "",
        "reason": f"将{target_liuqin}年生年化转为卦气，以{liuqin_gan_list[0] if liuqin_gan_list else '未知'}为{target_liuqin}之天干"
    }

def get_bazi_gong(bazi):
    """根据八字确定所属卦宫"""
    day_gan = bazi.get('day', '')[0] if len(bazi.get('day', '')) > 0 else ''
    
    if not day_gan:
        return {"gong": "", "reason": "日主不明"}
    
    day_wuxing = GAN_XING.get(day_gan, {}).get("wuxing", "")
    
    gong_map = {
        "木": ["震宫", "巽宫"],
        "火": ["离宫"],
        "土": ["坤宫", "艮宫"],
        "金": ["乾宫", "兑宫"],
        "水": ["坎宫"]
    }
    
    gong_list = gong_map.get(day_wuxing, [])
    
    return {
        "gong": gong_list[0] if gong_list else "",
        "gong_list": gong_list,
        "day_wuxing": day_wuxing,
        "reason": f"日主{day_gan}属{day_wuxing}，对应卦宫{gong_list}"
    }

def get_na_jia_info(gong_name):
    """获取卦宫的纳甲信息"""
    if gong_name not in BA_GONG_NA_JIA:
        return {"result": {}, "reason": f"未知卦宫: {gong_name}"}
    
    return BA_GONG_NA_JIA[gong_name]

def convert_gongwei(bazi, target_gong):
    """变宫法：将本宫转换为目标宫"""
    gong_info = get_bazi_gong(bazi)
    current_gong = gong_info.get("gong", "")
    
    if not current_gong or not target_gong:
        return {"result": {}, "reason": "卦宫信息不足"}
    
    current_na_jia = get_na_jia_info(current_gong)
    target_na_jia = get_na_jia_info(target_gong)
    
    converted_bazi = {}
    for key in ['year', 'month', 'day', 'time']:
        gan_zhi = bazi.get(key, '')
        if len(gan_zhi) >= 2:
            zhi = gan_zhi[1]
            target_gan = target_na_jia.get("六亲", {}).get(zhi, "")
            if target_gan:
                converted_bazi[key] = target_gan[0] + zhi
            else:
                converted_bazi[key] = gan_zhi
    
    return {
        "original_gong": current_gong,
        "target_gong": target_gong,
        "original_bazi": bazi,
        "converted_bazi": converted_bazi,
        "reason": f"变宫法：{current_gong}→{target_gong}，纳甲转换"
    }

def determine_liuqin_gongwei(bazi):
    """判定六亲所在宫位"""
    gongwei_result = calculate_liuqin_gongwei(bazi)
    ming_gong = gongwei_result.get("ming_gong", {}).get("ming_gong", "")
    
    liuqin_position = {}
    for gongwei_name, info in gongwei_result.get("gongwei", {}).items():
        zhi = info.get("zhi", "")
        liuqin_list = GONG_WEI_LIU_QIN.get(gongwei_name, [])
        
        for liuqin in liuqin_list:
            if liuqin not in liuqin_position:
                liuqin_position[liuqin] = []
            liuqin_position[liuqin].append({
                "gongwei": gongwei_name,
                "zhi": zhi,
                "shengxiao": info.get("shengxiao", "")
            })
    
    return {
        "ming_gong": ming_gong,
        "liuqin_position": liuqin_position,
        "reason": "根据先天八字，使用变宫法判定六亲宫位"
    }

def calculate_liuqin_gongwei(bazi):
    """推算六亲宫位轨"""
    ming_gong_result = calculate_ming_gong(bazi)
    ming_gong_zhi = ming_gong_result.get("ming_gong", "")
    
    gongwei_result = get_gongwei_by_minggong(ming_gong_zhi)
    
    shen_info = check_ji_e_shen(bazi)
    
    yong_shen_info = calculate_yong_shen(bazi)
    
    liuqin_converted = {}
    for liuqin in ["父亲", "母亲", "配偶", "子女", "兄弟"]:
        converted = convert_gua_qi(bazi, liuqin)
        liuqin_converted[liuqin] = converted
    
    return {
        "ming_gong": ming_gong_result,
        "gongwei": gongwei_result,
        "shen_info": shen_info,
        "yong_shen": yong_shen_info,
        "liuqin_converted": liuqin_converted,
        "bazi": bazi
    }

__all__ = [
    'calculate_ming_gong',
    'get_gongwei_by_minggong',
    'check_ji_e_shen',
    'calculate_yong_shen',
    'convert_gua_qi',
    'get_bazi_gong',
    'get_na_jia_info',
    'convert_gongwei',
    'determine_liuqin_gongwei',
    'calculate_liuqin_gongwei',
]
