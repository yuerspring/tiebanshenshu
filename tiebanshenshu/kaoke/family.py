"""家庭、婚姻及相关扩展计算。"""
from tiebanshenshu.kaoke.palaces import (
    calculate_liuqin_gongwei,
    convert_gongwei,
    convert_gua_qi,
    get_bazi_gong,
)
from tiebanshenshu.kaoke.relationships import (
    check_pokong,
    get_nayin,
    get_nayin_wuxing,
)
from tiebanshenshu.tables.kinship import (
    BA_GONG_NA_JIA,
    DI_ZHI_YIN_YUN,
    GONG_WEI_LIU_QIN,
    HUN_YIN_PEI_SHU,
    HUN_YIN_ZHUANG_KUANG,
    PEI_OU_XING_MING,
    RI_ZHU_GONG_WEI_PEI_SHU,
    SANHE_GROUPS,
    TIAN_GAN_WU_YIN,
    TIAN_GAN_YIN_YUN,
)
from tiebanshenshu.tables.numbers import (
    DI_ZHI_ORDER,
)

def calculate_mingli_guiji(bazi, marriage_status="未婚"):
    """计算命理轨迹（婚前婚后差异）"""
    liuqin_gongwei = calculate_liuqin_gongwei(bazi)
    gongwei = liuqin_gongwei.get("gongwei", {})
    
    guiji_before = []
    guiji_after = []
    
    for gw_name, gw_info in gongwei.items():
        zhi = gw_info.get("zhi", "")
        shengxiao = gw_info.get("shengxiao", "")
        
        if gw_name == "夫妻宫":
            guiji_after.append({
                "gongwei": gw_name,
                "zhi": zhi,
                "shengxiao": shengxiao,
                "change": "婚后加入配偶，影响命理轨迹"
            })
        elif gw_name == "子女宫":
            guiji_after.append({
                "gongwei": gw_name,
                "zhi": zhi,
                "shengxiao": shengxiao,
                "change": "婚后可能添子女，改变命理轨迹"
            })
        else:
            guiji_before.append({
                "gongwei": gw_name,
                "zhi": zhi,
                "shengxiao": shengxiao,
                "change": "基本不变"
            })
    
    return {
        "marriage_status": marriage_status,
        "guiji_before": guiji_before,
        "guiji_after": guiji_after,
        "reason": "婚前婚后命理轨迹差异分析"
    }

def classify_children(bazi, k_true=None):
    """区分子女类型（流产、堕胎、出嗣等）"""
    time_gan_zhi = bazi.get('time', '')
    if len(time_gan_zhi) < 2:
        return {"result": {}, "reason": "时柱信息不足"}
    
    time_zhi = time_gan_zhi[1]
    nayin_time = get_nayin(time_gan_zhi)
    wuxing_time = get_nayin_wuxing(time_gan_zhi)
    
    pokong_info = check_pokong(bazi)
    has_pokong = pokong_info.get("has_pokong", False)
    has_xing = pokong_info.get("has_xing", False)
    
    children_types = []
    
    if has_pokong:
        children_types.append({
            "type": "流产",
            "code": 2,
            "reason": f"时支{time_zhi}犯空，可能有流产之兆"
        })
    
    if has_xing:
        children_types.append({
            "type": "堕胎",
            "code": 3,
            "reason": f"时支{time_zhi}犯刑，可能有堕胎之兆"
        })
    
    for group in SANHE_GROUPS:
        if time_zhi in group:
            other_zhi = [z for z in group if z != time_zhi]
            for z in other_zhi:
                if z in [bazi.get('year', '')[1] if len(bazi.get('year', '')) > 1 else '',
                         bazi.get('month', '')[1] if len(bazi.get('month', '')) > 1 else '',
                         bazi.get('day', '')[1] if len(bazi.get('day', '')) > 1 else '']:
                    children_types.append({
                        "type": "出嗣",
                        "code": 4,
                        "reason": f"时支{time_zhi}与年/月/日支三合，可能有出嗣之子"
                    })
    
    if not children_types:
        children_types.append({
            "type": "亲生子女",
            "code": 1,
            "reason": f"时支{time_zhi}纳音{nayin_time}({wuxing_time})，主亲生子女"
        })
    
    return {
        "time_zhi": time_zhi,
        "nayin_time": nayin_time,
        "wuxing_time": wuxing_time,
        "has_pokong": has_pokong,
        "has_xing": has_xing,
        "children_types": children_types,
        "reason": "子女类型分析"
    }

def handle_cesarean(bazi):
    """剖腹产特殊处理"""
    time_gan_zhi = bazi.get('time', '')
    if len(time_gan_zhi) < 2:
        return {"result": {}, "reason": "时柱信息不足"}
    
    day_gan_zhi = bazi.get('day', '')
    if len(day_gan_zhi) < 2:
        return {"result": {}, "reason": "日柱信息不足"}
    
    day_zhi = day_gan_zhi[1]
    time_zhi = time_gan_zhi[1]
    
    natural_time_order = DI_ZHI_ORDER.get(time_zhi, 1)
    ideal_time_order = (DI_ZHI_ORDER.get(day_zhi, 1) + 1) % 12
    if ideal_time_order == 0:
        ideal_time_order = 12
    
    for zhi, order in DI_ZHI_ORDER.items():
        if order == ideal_time_order:
            ideal_time_zhi = zhi
            break
    else:
        ideal_time_zhi = "子"
    
    adjusted_bazi = bazi.copy()
    adjusted_bazi['time'] = time_gan_zhi[0] + ideal_time_zhi
    
    return {
        "original_time": time_gan_zhi,
        "natural_time_zhi": time_zhi,
        "ideal_time_zhi": ideal_time_zhi,
        "adjusted_bazi": adjusted_bazi,
        "reason": f"剖腹产修正：原时支{time_zhi}，理想时支{ideal_time_zhi}"
    }

def convert_family_fate(bazi, family_member):
    """将父母兄弟姐妹命运转化为六亲命盘"""
    converted = convert_gua_qi(bazi, family_member)
    
    converted_bazi = converted.get("converted_bazi", {})
    
    fate_conversion = {
        "original_bazi": bazi,
        "family_member": family_member,
        "converted_bazi": converted_bazi,
        "liuqin_gan": converted.get("liuqin_gan", ""),
        "reason": f"将{family_member}命运转化为六亲命盘"
    }
    
    if family_member in ["父亲", "母亲"]:
        parent_brother_converted = {}
        for sibling in ["兄弟", "姊妹"]:
            sibling_converted = convert_gua_qi(converted_bazi, sibling)
            parent_brother_converted[sibling] = sibling_converted
        
        fate_conversion["parent_siblings"] = parent_brother_converted
    
    return fate_conversion

def generate_48_changes(bazi):
    """生成四十八种命理轨迹变化（变宫六八止）"""
    gong_info = get_bazi_gong(bazi)
    current_gong = gong_info.get("gong", "")
    
    changes = []
    gong_list = list(BA_GONG_NA_JIA.keys())
    
    for target_gong in gong_list:
        if target_gong == current_gong:
            continue
        
        converted = convert_gongwei(bazi, target_gong)
        
        for gw_name in GONG_WEI_LIU_QIN.keys():
            change_info = {
                "change_type": f"{current_gong}→{target_gong}",
                "gongwei": gw_name,
                "original_gong": current_gong,
                "target_gong": target_gong,
                "description": f"变宫法：{current_gong}变为{target_gong}，{gw_name}发生变化"
            }
            changes.append(change_info)
    
    return {
        "total_changes": len(changes),
        "original_gong": current_gong,
        "changes": changes[:48],
        "reason": "变宫六八止：八宫八卦纳甲转换，产生四十八种变化"
    }

def calculate_peyou_xingming(bazi, db=None):
    """铁板直断配偶姓名法"""
    gong_info = get_bazi_gong(bazi)
    gong_name = gong_info.get("gong", "")
    wuxing = gong_info.get("day_wuxing", "")
    
    day_gan_zhi = bazi.get('day', '')
    if len(day_gan_zhi) < 2:
        return {"result": {}, "reason": "日柱信息不足"}
    
    day_gan = day_gan_zhi[0]
    day_zhi = day_gan_zhi[1]
    
    wu_yin = TIAN_GAN_WU_YIN.get(day_gan, "")
    yin_yun_gan = TIAN_GAN_YIN_YUN.get(day_gan, "")
    yin_yun_zhi = DI_ZHI_YIN_YUN.get(day_zhi, "")
    
    pei_shu = HUN_YIN_PEI_SHU.get(day_gan, {}).get("配数", 0)
    
    if db and hasattr(db, 'BAIJIA_XING'):
        xing_list = db.BAIJIA_XING.get(wuxing, [])
        ming_list = db.COMMON_NAMES.get(wuxing, [])
    else:
        xing_list = PEI_OU_XING_MING.get(wuxing, {}).get("xing", [])
        ming_list = PEI_OU_XING_MING.get(wuxing, {}).get("ming", [])
    
    xing_result = []
    for xing in xing_list[:5]:
        xing_result.append({"xing": xing, "reason": f"属{wuxing}行姓氏"})
    
    ming_result = []
    for ming in ming_list[:5]:
        ming_result.append({"ming": ming, "reason": f"属{wuxing}行名字"})
    
    return {
        "gong": gong_name,
        "wuxing": wuxing,
        "day_gan": day_gan,
        "day_zhi": day_zhi,
        "wu_yin": wu_yin,
        "yin_yun_gan": yin_yun_gan,
        "yin_yun_zhi": yin_yun_zhi,
        "yao_dong": pei_shu,
        "xing": xing_result[:10],
        "ming": ming_result[:10],
        "reason": f"命卦属{gong_name}({wuxing})，日干支{day_gan}{day_zhi}属{wu_yin}音{yin_yun_gan}{yin_yun_zhi}韵，第{pei_shu}爻动"
    }

def calculate_hunyin_zhuangkuang(bazi, fortune_map=None):
    """铁板婚姻状况直断法"""
    day_gan_zhi = bazi.get('day', '')
    if len(day_gan_zhi) < 2:
        return {"result": {}, "reason": "日柱信息不足"}
    
    day_gan = day_gan_zhi[0]
    day_zhi = day_gan_zhi[1]
    
    gan_peishu = HUN_YIN_PEI_SHU.get(day_gan, {}).get("配数", 0)
    gan_shuoming = HUN_YIN_PEI_SHU.get(day_gan, {}).get("说明", "")
    
    zhi_peishu = RI_ZHU_GONG_WEI_PEI_SHU.get(day_zhi, {}).get("配数", 0)
    zhi_gongwei = RI_ZHU_GONG_WEI_PEI_SHU.get(day_zhi, {}).get("宫位", "")
    
    zong_peishu = (gan_peishu + zhi_peishu) % 10
    if zong_peishu == 0:
        zong_peishu = 10
    
    duanyu = ""
    duanyu_age = ""
    if fortune_map:
        tieban_num = zong_peishu + 1000
        if tieban_num in fortune_map:
            duanyu_data = fortune_map.get(tieban_num, ("", ""))
            duanyu = duanyu_data[0] if isinstance(duanyu_data, (list, tuple)) else str(duanyu_data)
            duanyu_age = duanyu_data[1] if isinstance(duanyu_data, (list, tuple)) and len(duanyu_data) > 1 else ""
        elif zong_peishu in fortune_map:
            duanyu_data = fortune_map.get(zong_peishu, ("", ""))
            duanyu = duanyu_data[0] if isinstance(duanyu_data, (list, tuple)) else str(duanyu_data)
            duanyu_age = duanyu_data[1] if isinstance(duanyu_data, (list, tuple)) and len(duanyu_data) > 1 else ""
        else:
            zhuangkuang = HUN_YIN_ZHUANG_KUANG.get(zong_peishu, {})
            duanyu = zhuangkuang.get("断语", "")
            duanyu_age = ""
    else:
        zhuangkuang = HUN_YIN_ZHUANG_KUANG.get(zong_peishu, {})
        duanyu = zhuangkuang.get("断语", "")
        duanyu_age = ""
    
    return {
        "day_gan": day_gan,
        "day_zhi": day_zhi,
        "gan_peishu": gan_peishu,
        "gan_shuoming": gan_shuoming,
        "zhi_peishu": zhi_peishu,
        "zhi_gongwei": zhi_gongwei,
        "zong_peishu": zong_peishu,
        "duanyu": duanyu,
        "duanyu_age": duanyu_age,
        "reason": f"日干{day_gan}配数{gan_peishu}，日支{day_zhi}配数{zhi_peishu}，总和{zong_peishu}"
    }

__all__ = [
    'calculate_mingli_guiji',
    'classify_children',
    'handle_cesarean',
    'convert_family_fate',
    'generate_48_changes',
    'calculate_peyou_xingming',
    'calculate_hunyin_zhuangkuang',
]
