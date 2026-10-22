"""河洛配数、音韵百切与六亲秘法。"""
from tiebanshenshu.tables.derived import (
    BAGUA_COMBINATION_MAP,
    HE_LUO_BAGUA,
    HE_LUO_DI_ZHI,
    HE_LUO_TIAN_GAN,
)

def calculate_he_luo_peishu(bazi):
    """河洛配数法：将八字天干地支转换成数字"""
    year_gan = bazi.get('year', '')[0] if len(bazi.get('year', '')) > 0 else ''
    year_zhi = bazi.get('year', '')[1] if len(bazi.get('year', '')) > 1 else ''
    month_gan = bazi.get('month', '')[0] if len(bazi.get('month', '')) > 0 else ''
    month_zhi = bazi.get('month', '')[1] if len(bazi.get('month', '')) > 1 else ''
    day_gan = bazi.get('day', '')[0] if len(bazi.get('day', '')) > 0 else ''
    day_zhi = bazi.get('day', '')[1] if len(bazi.get('day', '')) > 1 else ''
    time_gan = bazi.get('time', '')[0] if len(bazi.get('time', '')) > 0 else ''
    time_zhi = bazi.get('time', '')[1] if len(bazi.get('time', '')) > 1 else ''
    
    peishu_details = []
    peishu_nums = []
    
    for gan, zhi, pos in [(year_gan, year_zhi, '年'), (month_gan, month_zhi, '月'), 
                          (day_gan, day_zhi, '日'), (time_gan, time_zhi, '时')]:
        gan_num = HE_LUO_TIAN_GAN.get(gan, 0)
        zhi_num = HE_LUO_DI_ZHI.get(zhi, 0)
        peishu_nums.append(gan_num)
        peishu_nums.append(zhi_num)
        peishu_details.append({
            "position": pos,
            "gan": gan,
            "zhi": zhi,
            "gan_num": gan_num,
            "zhi_num": zhi_num
        })
    
    odd_nums = [n for n in peishu_nums if n > 0 and n % 2 != 0]
    even_nums = [n for n in peishu_nums if n > 0 and n % 2 == 0]
    
    odd_sum = sum(odd_nums)
    even_sum = sum(even_nums)
    
    shang_gua_num = odd_sum % 8
    if shang_gua_num == 0:
        shang_gua_num = 8
    
    xia_gua_num = even_sum % 8
    if xia_gua_num == 0:
        xia_gua_num = 8
    
    shang_gua = HE_LUO_BAGUA.get(shang_gua_num, "")
    xia_gua = HE_LUO_BAGUA.get(xia_gua_num, "")
    
    ben_gua = BAGUA_COMBINATION_MAP.get((shang_gua, xia_gua), f"{shang_gua}{xia_gua}")
    
    return {
        "bazi": bazi,
        "peishu_details": peishu_details,
        "peishu_nums": peishu_nums,
        "odd_nums": odd_nums,
        "even_nums": even_nums,
        "odd_sum": odd_sum,
        "even_sum": even_sum,
        "shang_gua": shang_gua,
        "shang_gua_num": shang_gua_num,
        "xia_gua": xia_gua,
        "xia_gua_num": xia_gua_num,
        "ben_gua": ben_gua,
        "reason": f"河洛配数法：奇数和={odd_sum}→上卦={shang_gua}({shang_gua_num})，偶数和={even_sum}→下卦={xia_gua}({xia_gua_num})，基本卦={ben_gua}"
    }

def calculate_mima_chazi(mima_num):
    """密码查字法：根据密码数查找对应的汉字"""
    mima_num = int(mima_num)
    
    shang_qian_num = mima_num // 1000
    yu_num = mima_num % 1000
    
    shang_wan_num = yu_num // 10
    yu_num_final = yu_num % 10
    
    celue_info = []
    
    celue_info.append({
        "step": "第一步",
        "operation": f"{mima_num} ÷ 1000",
        "shang": shang_qian_num,
        "yu": yu_num,
        "description": f"商为{shang_qian_num}，余数为{yu_num}"
    })
    
    celue_info.append({
        "step": "第二步",
        "operation": f"{yu_num} ÷ 10",
        "shang": shang_wan_num,
        "yu": yu_num_final,
        "description": f"商为{shang_wan_num}，余数为{yu_num_final}"
    })
    
    celue_info.append({
        "step": "第三步",
        "operation": "查表方法",
        "description": f"第一次的商为{shang_qian_num}，为找第{shang_qian_num}单元"
    })
    
    celue_info.append({
        "step": "第四步",
        "operation": "查表方法",
        "description": f"第二次的商为{shang_wan_num}，为找第{shang_wan_num}行字"
    })
    
    celue_info.append({
        "step": "第五步",
        "operation": "查表方法",
        "description": f"第二次的余数为{yu_num_final}，是第{shang_wan_num}行字中的第{yu_num_final}个字"
    })
    
    return {
        "mima_num": mima_num,
        "shang_qian_num": shang_qian_num,
        "shang_wan_num": shang_wan_num,
        "yu_num_final": yu_num_final,
        "celue_info": celue_info,
        "reason": f"密码查字法：{mima_num}→第{shang_qian_num}单元第{shang_wan_num}行第{yu_num_final}个字"
    }

def calculate_yinyun_baiqie(bazi):
    """音韵百切法：用于查找姓名用字"""
    year_gan = bazi.get('year', '')[0] if len(bazi.get('year', '')) > 0 else ''
    year_zhi = bazi.get('year', '')[1] if len(bazi.get('year', '')) > 1 else ''
    day_gan = bazi.get('day', '')[0] if len(bazi.get('day', '')) > 0 else ''
    day_zhi = bazi.get('day', '')[1] if len(bazi.get('day', '')) > 1 else ''
    
    ming_gan_num = HE_LUO_TIAN_GAN.get(day_gan, 0)
    ming_zhi_num = HE_LUO_DI_ZHI.get(day_zhi, 0)
    nian_gan_num = HE_LUO_TIAN_GAN.get(year_gan, 0)
    nian_zhi_num = HE_LUO_DI_ZHI.get(year_zhi, 0)
    
    first_char_num = ming_gan_num * 1000 + ming_zhi_num * 100 + nian_gan_num * 10 + nian_zhi_num
    second_char_num = nian_gan_num * 1000 + nian_zhi_num * 100 + ming_gan_num * 10 + ming_zhi_num
    
    first_char_info = calculate_mima_chazi(first_char_num)
    second_char_info = calculate_mima_chazi(second_char_num)
    
    return {
        "bazi": bazi,
        "ming_gan": day_gan,
        "ming_zhi": day_zhi,
        "nian_gan": year_gan,
        "nian_zhi": year_zhi,
        "ming_gan_num": ming_gan_num,
        "ming_zhi_num": ming_zhi_num,
        "nian_gan_num": nian_gan_num,
        "nian_zhi_num": nian_zhi_num,
        "first_char_num": first_char_num,
        "second_char_num": second_char_num,
        "first_char_info": first_char_info,
        "second_char_info": second_char_info,
        "reason": f"音韵百切法：名干={day_gan}({ming_gan_num}), 名支={day_zhi}({ming_zhi_num}), 年干={year_gan}({nian_gan_num}), 年支={year_zhi}({nian_zhi_num})"
    }

def calculate_liuqin_shengxiao_mifa(bazi):
    """六亲生肖配数秘法"""
    year_gan = bazi.get('year', '')[0] if len(bazi.get('year', '')) > 0 else ''
    year_zhi = bazi.get('year', '')[1] if len(bazi.get('year', '')) > 1 else ''
    month_gan = bazi.get('month', '')[0] if len(bazi.get('month', '')) > 0 else ''
    month_zhi = bazi.get('month', '')[1] if len(bazi.get('month', '')) > 1 else ''
    day_gan = bazi.get('day', '')[0] if len(bazi.get('day', '')) > 0 else ''
    day_zhi = bazi.get('day', '')[1] if len(bazi.get('day', '')) > 1 else ''
    time_gan = bazi.get('time', '')[0] if len(bazi.get('time', '')) > 0 else ''
    time_zhi = bazi.get('time', '')[1] if len(bazi.get('time', '')) > 1 else ''
    
    D = HE_LUO_TIAN_GAN.get(day_gan, 0) + HE_LUO_DI_ZHI.get(day_zhi, 0)
    H = HE_LUO_TIAN_GAN.get(time_gan, 0) + HE_LUO_DI_ZHI.get(time_zhi, 0)
    
    liuqin_results = []
    
    liuqin_results.append({
        "type": "父亲",
        "base": HE_LUO_TIAN_GAN.get(year_gan, 0),
        "formula": f"D + 年干河洛数 = {D} + {HE_LUO_TIAN_GAN.get(year_gan, 0)}",
        "result": D + HE_LUO_TIAN_GAN.get(year_gan, 0)
    })
    
    liuqin_results.append({
        "type": "母亲",
        "base": HE_LUO_TIAN_GAN.get(month_gan, 0),
        "formula": f"D + 月干河洛数 = {D} + {HE_LUO_TIAN_GAN.get(month_gan, 0)}",
        "result": D + HE_LUO_TIAN_GAN.get(month_gan, 0)
    })
    
    liuqin_results.append({
        "type": "兄弟",
        "base": HE_LUO_DI_ZHI.get(month_zhi, 0),
        "formula": f"D + 月支河洛数 = {D} + {HE_LUO_DI_ZHI.get(month_zhi, 0)}",
        "result": D + HE_LUO_DI_ZHI.get(month_zhi, 0)
    })
    
    liuqin_results.append({
        "type": "配偶",
        "base": HE_LUO_DI_ZHI.get(day_zhi, 0),
        "formula": f"H + 日支河洛数 = {H} + {HE_LUO_DI_ZHI.get(day_zhi, 0)}",
        "result": H + HE_LUO_DI_ZHI.get(day_zhi, 0)
    })
    
    liuqin_results.append({
        "type": "子女",
        "base": HE_LUO_TIAN_GAN.get(time_gan, 0),
        "formula": f"H + 时干河洛数 = {H} + {HE_LUO_TIAN_GAN.get(time_gan, 0)}",
        "result": H + HE_LUO_TIAN_GAN.get(time_gan, 0)
    })
    
    return {
        "bazi": bazi,
        "D": D,
        "H": H,
        "liuqin_results": liuqin_results,
        "reason": f"六亲生肖配数秘法：D={D}(日干+日支), H={H}(时干+时支)"
    }

__all__ = [
    'calculate_he_luo_peishu',
    'calculate_mima_chazi',
    'calculate_yinyun_baiqie',
    'calculate_liuqin_shengxiao_mifa',
]
